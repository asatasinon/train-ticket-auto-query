#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试连接和登录功能
"""

import sys
import logging
from config import setup_logging, check_config, get_config
from queries import Query


def main():
    """测试连接和登录"""
    # 设置日志级别为DEBUG
    setup_logging()
    logger = logging.getLogger("connection-test")
    
    # 显示配置信息
    config = get_config()
    logger.info("=" * 50)
    logger.info("配置信息:")
    logger.info(f"服务器地址: {config['base_url']}")
    logger.info(f"用户名: {config['username']}")
    logger.info("=" * 50)
    
    # 测试服务器连接
    logger.info("开始测试服务器连接...")
    if not check_config():
        logger.error("服务器连接测试失败")
        return False
    
    logger.info("服务器连接测试成功")
    
    # 测试登录
    logger.info("开始测试登录...")
    q = Query()
    if not q.login():
        logger.error("登录测试失败")
        return False
    
    logger.info("登录测试成功")
    logger.info(f"用户ID: {q.uid}")
    logger.info(f"令牌: {q.token[:10]}...（已截断）")
    
    return True


if __name__ == "__main__":
    result = main()
    sys.exit(0 if result else 1) 