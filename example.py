#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
示例脚本，演示如何使用配置系统和随机执行不同场景
"""

import time
import random
import logging
import sys
from queries import Query
from config import (
    setup_logging, BATCH_COUNT, BATCH_INTERVAL, get_config, check_config
)
import scenarios


def main():
    """主函数，演示配置使用和场景执行"""
    # 设置日志
    setup_logging()
    logger = logging.getLogger("example")
    
    # 显示加载的配置信息
    config = get_config()
    logger.info(f"加载配置: 服务器地址={config['base_url']}")
    logger.info(f"用户名={config['username']}")
    logger.info(f"批量执行次数={config['batch_count']}")
    
    # 检查配置是否有效
    if not check_config():
        logger.error("配置检查失败，请修正配置后重试")
        return False
    
    # 初始化查询类（不传入地址则会使用配置中的地址）
    q = Query()
    
    # 登录（不传入用户名密码则会使用配置中的凭据）
    if not q.login():
        logger.error("登录失败，退出程序")
        return False
    
    logger.info("登录成功，开始执行场景")
    
    # 可用场景列表
    available_scenarios = [
        scenarios.query_and_preserve,
        scenarios.query_and_cancel,
        scenarios.query_and_pay,
        scenarios.query_and_rebook,
        scenarios.query_and_collect,
        scenarios.query_and_execute,
        scenarios.query_and_consign
    ]
    
    # 批量执行场景
    start_time = time.time()
    success_count = 0
    fail_count = 0
    
    # 使用配置的批量执行次数
    for i in range(BATCH_COUNT):
        # 随机选择场景
        scenario = random.choice(available_scenarios)
        scenario_name = scenario.__name__
        
        logger.info(f"执行场景 [{i+1}/{BATCH_COUNT}]: {scenario_name}")
        
        try:
            # 执行场景
            scenario(q)
            success_count += 1
            logger.info(f"场景 {scenario_name} 执行成功")
        except Exception as e:
            fail_count += 1
            logger.error(f"场景 {scenario_name} 执行失败: {str(e)}")
        
        # 使用配置的执行间隔
        time.sleep(BATCH_INTERVAL)
    
    # 统计结果
    elapsed_time = time.time() - start_time
    logger.info("=" * 50)
    logger.info(
        f"执行完毕！总计: {BATCH_COUNT}个场景, "
        f"成功: {success_count}, 失败: {fail_count}"
    )
    logger.info(
        f"总耗时: {elapsed_time:.2f}秒, "
        f"平均每个场景: {elapsed_time/BATCH_COUNT:.2f}秒"
    )
    
    return True


if __name__ == "__main__":
    result = main()
    sys.exit(0 if result else 1) 