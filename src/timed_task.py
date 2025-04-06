#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Train-Ticket 定时任务工具

这是一个用于按顺序循环执行所有场景的定时任务工具。
每隔一分钟执行一个场景，执行完所有场景后退出登录并重新开始循环。

使用方法：
    python -m src.timed_task  # 使用默认间隔（1分钟）执行
    python -m src.timed_task --interval 30  # 使用自定义间隔（30秒）执行
    python -m src.timed_task --log-level DEBUG  # 使用指定日志级别执行
    python -m src.timed_task --server http://example.com --username user --password pass  # 指定连接参数
    python -m src.timed_task --health-file /path/to/health  # 指定健康检查文件路径
    python -m src.timed_task --help  # 显示帮助信息
"""

import argparse
import logging
import sys
import time
import schedule
import datetime
import os
from pathlib import Path

# 设置时区为中国上海时间（东八区）
os.environ["TZ"] = "Asia/Shanghai"
try:
    time.tzset()  # 在Unix系统上应用时区设置
    print(f"时区已设置为: {os.environ['TZ']}")
except AttributeError:
    # Windows系统不支持tzset()
    print("在当前操作系统上无法设置时区，时间可能不准确")

# 添加项目根目录到Python路径，以便于直接运行此文件
if __name__ == "__main__":
    # 获取当前文件所在目录的父目录（即项目根目录）
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))

# 导入项目内部模块
from src.utils.config import setup_logging, check_config
from src.core.queries import Query
from src.scenarios.scenarios import (
    query_high_speed_ticket_scenario,
    query_normal_ticket_scenario,
    query_ticket_parallel_scenario,  # 导入但不使用
    query_food_scenario,
    query_and_book_ticket_scenario,
    query_and_pay_ticket,
    query_and_consign,
    query_and_collect_ticket,
    query_and_rebook_ticket_scenario,
    query_and_cancel_ticket,
)

# 注意：并行查询场景(query_ticket_parallel_scenario)已从定时任务中移除
# 原因：该场景使用的API端点在某些服务器环境中存在兼容性问题
# 具体表现为HTTP 405错误(Method Not Allowed)或返回无内容的响应

# 场景列表，按实际使用场景的先后顺序排序
SCENARIOS = [
    ("查询高铁票", query_high_speed_ticket_scenario),
    ("查询普通列车票", query_normal_ticket_scenario),
    # 已移除：("并行查询车票", query_ticket_parallel_scenario)
    ("查询食品", query_food_scenario),
    ("预订车票", query_and_book_ticket_scenario),
    ("支付订单", query_and_pay_ticket),
    ("添加托运信息", query_and_consign),
    ("取票", query_and_collect_ticket),
    ("改签车票", query_and_rebook_ticket_scenario),
    ("取消订单", query_and_cancel_ticket),
]


class TimedTaskRunner:
    """定时任务执行器类"""

    def __init__(
        self, 
        interval_seconds=60, 
        server_url=None,
        username=None,
        password=None,
        health_file="/tmp/timed_task_health"
    ):
        """
        初始化定时任务执行器

        Args:
            interval_seconds: 任务执行间隔（秒）
            server_url: 服务器地址，如果提供则覆盖环境变量
            username: 用户名，如果提供则覆盖环境变量
            password: 密码，如果提供则覆盖环境变量
            health_file: 健康检查文件路径
        """
        self.logger = logging.getLogger("timed-task")
        self.interval = interval_seconds
        self.server_url = server_url
        self.username = username
        self.password = password
        self.health_file = health_file
        self.query = None
        self.current_scenario_index = 0
        self.total_scenarios = len(SCENARIOS)
        self.running = False
        self.last_login_time = None

    def setup(self):
        """设置环境，创建Query对象并登录"""
        self.logger.info("正在设置定时任务环境...")
        
        # 如果提供了服务器地址、用户名和密码，则设置环境变量
        if self.server_url:
            os.environ["TS_BASE_URL"] = self.server_url
            self.logger.info(f"使用命令行参数设置服务器地址: {self.server_url}")
            
        if self.username:
            os.environ["TS_USERNAME"] = self.username
            self.logger.info(f"使用命令行参数设置用户名: {self.username}")
            
        if self.password:
            os.environ["TS_PASSWORD"] = self.password
            self.logger.info("使用命令行参数设置密码")
        
        # 检查配置
        if not check_config():
            self.logger.error("配置检查失败，无法连接到服务器")
            return False

        # 登录（如果需要）
        if not self.login():
            return False

        return True
        
    def login(self):
        """执行登录操作"""
        # 创建新的Query对象
        self.query = Query()
        
        # 登录
        self.logger.info("正在登录...")
        if not self.query.login():
            self.logger.error("登录失败！")
            return False

        self.last_login_time = time.time()
        self.logger.info(f"登录成功！用户ID: {self.query.uid}")
        return True
        
    def logout(self):
        """执行退出登录操作"""
        if self.query and self.query.uid:
            self.logger.info(f"正在退出登录，用户ID: {self.query.uid}")
            # 清理身份验证信息
            self.query.token = ""
            self.query.uid = ""
            # 移除会话中的认证头
            if "Authorization" in self.query.session.headers:
                del self.query.session.headers["Authorization"]
            self.logger.info("退出登录成功")
            # 设置query为None，以便下次运行时创建新的Query对象
            self.query = None
            return True
        return False

    def run_next_scenario(self):
        """执行下一个场景"""
        # 如果没有登录或者Query对象不存在，重新登录
        if not self.query:
            if not self.login():
                self.logger.error("登录失败，无法继续执行场景")
                return

        # 获取当前要执行的场景
        scenario_name, scenario_func = SCENARIOS[self.current_scenario_index]

        # 执行场景
        self.logger.info(
            f"[{self.current_scenario_index + 1}/{self.total_scenarios}] "
            f"开始执行场景: {scenario_name}"
        )
        try:
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.logger.info(f"执行时间: {current_time}")
            scenario_func(self.query)
            self.logger.info(f"场景 {scenario_name} 执行完成")

            # 更新健康检查文件，用于Docker容器健康检查
            try:
                with open(self.health_file, "w") as f:
                    f.write(f"Last execution: {current_time}\n")
                    f.write(f"Last scenario: {scenario_name}\n")
                    f.write(f"Last login: {datetime.datetime.fromtimestamp(self.last_login_time).strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Timezone: {os.environ.get('TZ', 'not set')}\n")
                self.logger.debug(f"已更新健康检查文件: {self.health_file}")
            except Exception as e:
                self.logger.warning(f"无法更新健康检查文件: {e}")
        except Exception as e:
            self.logger.error(f"场景 {scenario_name} 执行出错: {e}")

        # 更新索引，进入下一个场景
        self.current_scenario_index = (
            self.current_scenario_index + 1
        ) % self.total_scenarios
        
        # 如果已完成所有场景（即索引回到0），则退出登录，以便下次循环时重新登录
        if self.current_scenario_index == 0:
            self.logger.info("已完成所有场景，退出登录以便下次循环时重新登录")
            self.logout()

    def start(self):
        """启动定时任务"""
        if not self.setup():
            self.logger.error("环境设置失败，无法启动定时任务")
            return

        self.running = True
        self.logger.info(f"定时任务已启动，将每 {self.interval} 秒执行一个场景")
        self.logger.info("每完成一轮所有场景后，将退出登录并在下次循环开始时重新登录")

        # 立即执行一次第一个场景
        self.run_next_scenario()

        # 设置定时任务
        schedule.every(self.interval).seconds.do(self.run_next_scenario)

        # 主循环
        try:
            while self.running:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("用户中断，定时任务已停止")
        except Exception as e:
            self.logger.error(f"执行过程中出现错误: {e}")
        finally:
            self.running = False
            # 确保退出时进行登出
            if self.query:
                self.logout()
            self.logger.info("定时任务已结束")

    def stop(self):
        """停止定时任务"""
        self.running = False
        self.logger.info("正在停止定时任务...")


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="Train-Ticket 定时任务工具")

    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="任务执行间隔（秒），默认为60秒（1分钟）",
    )

    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="日志级别，默认为INFO",
    )
    
    parser.add_argument(
        "--server",
        type=str,
        help="Train-Ticket服务器地址",
    )
    
    parser.add_argument(
        "--username",
        type=str,
        help="登录用户名",
    )
    
    parser.add_argument(
        "--password",
        type=str,
        help="登录密码",
    )
    
    parser.add_argument(
        "--health-file",
        type=str,
        default="/tmp/timed_task_health",
        help="健康检查文件路径，默认为/tmp/timed_task_health",
    )

    return parser.parse_args()


def main():
    """主函数"""
    # 解析命令行参数
    args = parse_args()

    # 设置日志
    setup_logging(level=args.log_level)
    logger = logging.getLogger("timed-task")

    logger.info("=" * 50)
    logger.info("Train-Ticket 定时任务工具")
    logger.info("=" * 50)

    # 创建并启动定时任务执行器
    runner = TimedTaskRunner(
        interval_seconds=args.interval, 
        server_url=args.server,
        username=args.username,
        password=args.password,
        health_file=args.health_file
    )
    runner.start()

    return 0


if __name__ == "__main__":
    sys.exit(main())
