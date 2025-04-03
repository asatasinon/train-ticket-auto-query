#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Train-Ticket 自动查询工具

这是项目的主入口点，用于执行各种场景。
使用方法：
    python -m src.main  # 默认执行所有场景
    python -m src.main --scenario all  # 执行所有场景
    python -m src.main --scenario high_speed  # 只执行高铁票查询场景
    python -m src.main --scenario normal  # 只执行普通列车票查询场景
    python -m src.main --scenario food  # 只执行食品查询场景
    python -m src.main --random 10  # 随机执行10次场景
    python -m src.main --test-connection  # 测试连接
    python -m src.main --help  # 显示帮助信息
    
注意: 直接运行此文件时，需要确保项目根目录在Python路径中，
否则应该使用"python -m src.main"方式运行。
"""

import argparse
import logging
import sys
import os
from typing import Optional, Tuple
from pathlib import Path

# 添加项目根目录到Python路径，以便于直接运行此文件
# 当作为模块运行时（python -m src.main）不需要此段代码
if __name__ == "__main__":
    # 获取当前文件所在目录的父目录（即项目根目录）
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))

# 导入项目内部模块 - 使用绝对导入
from src.utils.config import (
    setup_logging, check_config, BASE_URL,
    BATCH_COUNT, BATCH_INTERVAL
)
from src.core.queries import Query
from src.scenarios.runners import ScenarioRunner
from src.scenarios.scenarios import (
    query_high_speed_ticket_scenario,
    query_normal_ticket_scenario,
    query_food_scenario,
    query_ticket_parallel_scenario,
    query_and_pay_ticket,
    query_and_cancel_ticket,
    query_and_consign,
    query_and_book_ticket_scenario,
    query_and_rebook_ticket_scenario
)

# 场景映射字典，用于命令行参数
SCENARIO_MAP = {
    "high_speed": query_high_speed_ticket_scenario,
    "normal": query_normal_ticket_scenario,
    "food": query_food_scenario,
    "parallel": query_ticket_parallel_scenario,
    "pay": query_and_pay_ticket,
    "cancel": query_and_cancel_ticket,
    "consign": query_and_consign,
    "book": query_and_book_ticket_scenario,
    "rebook": query_and_rebook_ticket_scenario
}

# 所有场景列表
ALL_SCENARIOS = [
    query_high_speed_ticket_scenario,
    query_normal_ticket_scenario,
    query_food_scenario,
    query_ticket_parallel_scenario,
    query_and_pay_ticket,
    query_and_cancel_ticket,
    query_and_consign,
    query_and_book_ticket_scenario,
    query_and_rebook_ticket_scenario
]

# 场景权重配置
SCENARIO_WEIGHTS = {
    "query_high_speed_ticket_scenario": 25,  # 高铁票查询场景权重
    "query_normal_ticket_scenario": 25,      # 普通列车票查询场景权重
    "query_food_scenario": 10,               # 食品查询场景权重
    "query_ticket_parallel_scenario": 10,    # 并行查询场景权重
    "query_and_pay_ticket": 5,               # 支付订单场景权重
    "query_and_cancel_ticket": 5,            # 取消订单场景权重
    "query_and_consign": 5,                  # 托运场景权重
    "query_and_book_ticket_scenario": 10,    # 预订车票场景权重
    "query_and_rebook_ticket_scenario": 5    # 重新订票场景权重
}


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="Train-Ticket 自动查询工具")
    
    # 场景选择参数组
    scenario_group = parser.add_mutually_exclusive_group()
    scenario_group.add_argument(
        "--scenario", 
        type=str, 
        choices=list(SCENARIO_MAP.keys()) + ["all"],
        help="要执行的场景，'all'表示执行所有场景"
    )
    scenario_group.add_argument(
        "--random", 
        type=int, 
        metavar="COUNT",
        help=f"随机执行场景指定次数，默认为{BATCH_COUNT}次"
    )
    
    # 其他参数
    parser.add_argument(
        "--interval", 
        type=float, 
        default=BATCH_INTERVAL,
        help="场景执行间隔（秒），默认为配置文件中的值"
    )
    parser.add_argument(
        "--test-connection", 
        action="store_true",
        help="测试与服务器的连接"
    )
    parser.add_argument(
        "--config", 
        action="store_true",
        help="显示当前配置"
    )
    
    return parser.parse_args()


def test_connection():
    """测试与服务器的连接"""
    logger = logging.getLogger("main")
    logger.info(f"测试与服务器 {BASE_URL} 的连接...")
    if check_config():
        logger.info("连接测试成功！")
        return True
    else:
        logger.error("连接测试失败！")
        return False


def show_config():
    """显示当前配置"""
    from src.utils.config import get_config
    
    logger = logging.getLogger("main")
    config = get_config()
    
    logger.info("当前配置:")
    for key, value in config.items():
        if key == "password":  # 不显示密码
            value = "******"
        logger.info(f"  {key}: {value}")


def setup_runner() -> Tuple[Optional[Query], Optional[ScenarioRunner]]:
    """
    设置场景执行器
    
    Returns:
        (Query对象, ScenarioRunner对象)的元组，如果登录失败则返回(None, None)
    """
    logger = logging.getLogger("main")
    
    # 创建查询对象
    query = Query()
    
    # 登录
    logger.info("正在登录...")
    if not query.login():
        logger.error("登录失败！")
        return None, None
    
    logger.info(f"登录成功！用户ID: {query.uid}")
    
    # 创建场景执行器
    runner = ScenarioRunner(query)
    
    # 添加所有场景，设置权重
    for scenario in ALL_SCENARIOS:
        weight = SCENARIO_WEIGHTS.get(scenario.__name__, 10)  # 默认权重10
        runner.add_scenario(scenario, weight)
        logger.debug(f"添加场景 {scenario.__name__}，权重: {weight}")
    
    return query, runner


def main():
    """主函数"""
    # 设置日志
    setup_logging()
    logger = logging.getLogger("main")
    
    logger.info("=" * 50)
    logger.info("Train-Ticket 自动查询工具")
    logger.info("=" * 50)
    
    # 解析命令行参数
    args = parse_args()
    
    # 处理测试连接
    if args.test_connection:
        if test_connection():
            return 0
        else:
            return 1
    
    # 显示配置
    if args.config:
        show_config()
        return 0
    
    # 设置场景执行器
    query, runner = setup_runner()
    if not query:
        return 1
    
    # 执行场景
    if args.scenario:
        if args.scenario == "all":
            logger.info("执行所有场景")
            results = runner.run_all(interval=args.interval)
            
            # 统计结果
            success_count = sum(1 for result in results.values() if result)
            fail_count = sum(1 for result in results.values() if not result)
            
            logger.info("=" * 50)
            logger.info(f"所有场景执行完毕！总计: {len(results)}个场景")
            logger.info(f"成功: {success_count}, 失败: {fail_count}")
            logger.info("场景执行情况:")
            for name, success in results.items():
                logger.info(f"  {name}: {'成功' if success else '失败'}")
        else:
            # 执行特定场景
            scenario = SCENARIO_MAP.get(args.scenario)
            if not scenario:
                logger.error(f"未知场景: {args.scenario}")
                return 1
                
            logger.info(f"执行场景: {scenario.__name__}")
            success = runner.run_specific(scenario)
            logger.info(f"场景执行{'成功' if success else '失败'}")
    
    elif args.random is not None:
        # 随机执行场景
        count = args.random if args.random > 0 else BATCH_COUNT
        logger.info(f"随机执行{count}次场景")
        success_count, fail_count = runner.run_random(
            count=count, 
            interval=args.interval
        )
        
        logger.info("=" * 50)
        logger.info(f"随机场景执行完毕！总计: {count}次")
        logger.info(f"成功: {success_count}, 失败: {fail_count}")
    
    else:
        # 如果没有指定任何操作，默认执行所有场景
        logger.info("未指定任何操作，默认执行所有场景")
        results = runner.run_all(interval=args.interval)
        
        # 统计结果
        success_count = sum(1 for result in results.values() if result)
        fail_count = sum(1 for result in results.values() if not result)
        
        logger.info("=" * 50)
        logger.info(f"所有场景执行完毕！总计: {len(results)}个场景")
        logger.info(f"成功: {success_count}, 失败: {fail_count}")
        logger.info("场景执行情况:")
        for name, success in results.items():
            logger.info(f"  {name}: {'成功' if success else '失败'}")
    
    logger.info("=" * 50)
    return 0


if __name__ == "__main__":
    sys.exit(main()) 