#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Train-Ticket 定时任务工具

这是一个用于按顺序循环执行所有场景的定时任务工具。
每隔一分钟执行一个场景，执行完所有场景后重新开始循环。

使用方法：
    python -m src.timed_task  # 使用默认间隔（1分钟）执行
    python -m src.timed_task --interval 30  # 使用自定义间隔（30秒）执行
    python -m src.timed_task --log-level DEBUG  # 使用指定日志级别执行
    python -m src.timed_task --token-refresh 1800  # 自定义token刷新间隔（秒）
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
    query_ticket_parallel_scenario,
    query_food_scenario,
    query_and_book_ticket_scenario,
    query_and_pay_ticket,
    query_and_consign,
    query_and_collect_ticket,
    query_and_rebook_ticket_scenario,
    query_and_cancel_ticket,
)

# 场景列表，按实际使用场景的先后顺序排序
SCENARIOS = [
    ("查询高铁票", query_high_speed_ticket_scenario),
    ("查询普通列车票", query_normal_ticket_scenario),
    ("并行查询车票", query_ticket_parallel_scenario),
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
        token_refresh_interval=1800,
        server_url=None,
        username=None,
        password=None,
        health_file="/tmp/timed_task_health"
    ):
        """
        初始化定时任务执行器

        Args:
            interval_seconds: 任务执行间隔（秒）
            token_refresh_interval: token刷新间隔（秒），默认30分钟
            server_url: 服务器地址，如果提供则覆盖环境变量
            username: 用户名，如果提供则覆盖环境变量
            password: 密码，如果提供则覆盖环境变量
            health_file: 健康检查文件路径
        """
        self.logger = logging.getLogger("timed-task")
        self.interval = interval_seconds
        self.token_refresh_interval = token_refresh_interval
        self.server_url = server_url
        self.username = username
        self.password = password
        self.health_file = health_file
        self.query = None
        self.current_scenario_index = 0
        self.total_scenarios = len(SCENARIOS)
        self.running = False
        self.last_token_refresh = time.time()

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

        # 创建Query对象
        self.query = Query()

        # 登录
        self.logger.info("正在登录...")
        if not self.query.login():
            self.logger.error("登录失败！")
            return False

        # 记录当前token刷新时间
        self.last_token_refresh = time.time()
        self.logger.info(f"登录成功！用户ID: {self.query.uid}")
        return True

    def refresh_token_if_needed(self):
        """检查并刷新token（如果需要）"""
        current_time = time.time()
        # 如果距离上次刷新token的时间超过了设定的间隔，则刷新token
        if current_time - self.last_token_refresh >= self.token_refresh_interval:
            self.logger.info(
                f"距离上次刷新token已经过去了"
                f"{int((current_time - self.last_token_refresh) / 60)}分钟，"
                f"开始刷新token"
            )
            if self.query.refresh_token():
                self.last_token_refresh = current_time
                self.logger.info("Token刷新成功")
            else:
                self.logger.error("Token刷新失败")

    def token_refresh_scheduler(self):
        """定期刷新token的调度方法"""
        self.refresh_token_if_needed()

    def run_next_scenario(self):
        """执行下一个场景"""
        if not self.query:
            self.logger.error("Query对象未初始化，请先调用setup方法")
            return

        # 刷新token（如果需要）
        self.refresh_token_if_needed()

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
                    f.write(
                        f"Last token refresh: {datetime.datetime.fromtimestamp(
                            self.last_token_refresh).strftime('%Y-%m-%d %H:%M:%S')}\n"
                    )
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

    def start(self):
        """启动定时任务"""
        if not self.setup():
            self.logger.error("环境设置失败，无法启动定时任务")
            return

        self.running = True
        self.logger.info(f"定时任务已启动，将每 {self.interval} 秒执行一个场景")
        self.logger.info(f"Token将每 {self.token_refresh_interval} 秒刷新一次")

        # 立即执行一次第一个场景
        self.run_next_scenario()

        # 设置定时任务
        schedule.every(self.interval).seconds.do(self.run_next_scenario)

        # 设置token刷新任务
        # 每5分钟检查一次token是否需要刷新
        token_check_interval = min(300, self.token_refresh_interval / 2)
        schedule.every(token_check_interval).seconds.do(self.token_refresh_scheduler)

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
        "--token-refresh",
        type=int,
        default=1800,
        help="token刷新间隔（秒），默认为1800秒（30分钟）",
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
        token_refresh_interval=args.token_refresh,
        server_url=args.server,
        username=args.username,
        password=args.password,
        health_file=args.health_file
    )
    runner.start()

    return 0


if __name__ == "__main__":
    sys.exit(main())
