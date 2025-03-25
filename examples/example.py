#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Train-Ticket 自动查询工具使用示例

这个示例展示了如何使用Train-Ticket自动查询工具进行各种场景的查询和操作。
"""

import sys
import os
import time
import logging
from pathlib import Path

# 添加项目根目录到Python路径，以便导入
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 导入配置和核心模块
from src.utils.config import setup_logging
from src.core.queries import Query
from src.scenarios.scenarios import (
    query_food_scenario,
    query_high_speed_ticket_scenario,
    query_normal_ticket_scenario
)


def main():
    """示例主函数"""
    # 设置日志
    setup_logging()
    logger = logging.getLogger("example")
    
    logger.info("=" * 50)
    logger.info("Train-Ticket 自动查询工具示例")
    logger.info("=" * 50)
    
    # 创建查询对象
    query = Query()
    
    # 登录
    logger.info("正在登录...")
    if not query.login():
        logger.error("登录失败！")
        return 1
    
    logger.info(f"登录成功！用户ID: {query.uid}")
    
    # 执行高铁票查询场景
    logger.info("\n" + "=" * 30)
    logger.info("执行高铁票查询场景")
    logger.info("=" * 30)
    query_high_speed_ticket_scenario(query)
    
    # 等待一下
    time.sleep(2)
    
    # 执行普通列车票查询场景
    logger.info("\n" + "=" * 30)
    logger.info("执行普通列车票查询场景")
    logger.info("=" * 30)
    query_normal_ticket_scenario(query)
    
    # 等待一下
    time.sleep(2)
    
    # 执行食品查询场景
    logger.info("\n" + "=" * 30)
    logger.info("执行食品查询场景")
    logger.info("=" * 30)
    query_food_scenario(query)
    
    logger.info("\n" + "=" * 50)
    logger.info("示例结束")
    logger.info("=" * 50)
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 