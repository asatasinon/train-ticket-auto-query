#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试登录功能
"""

import sys
import os
import logging
import time
from pathlib import Path

# 添加项目根目录到Python路径，以便导入
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.config import setup_logging, get_config
from src.core.queries import Query


def test_normal_login():
    """测试正常登录"""
    logger = logging.getLogger("login-test")
    
    # 获取配置
    config = get_config()
    username = config['username']
    password = config['password']
    
    logger.info(f"使用配置的用户名密码登录: {username}")
    
    # 创建查询对象并登录
    query = Query()
    start_time = time.time()
    success = query.login()
    elapsed_time = time.time() - start_time
    
    if success:
        logger.info(f"登录成功，用户ID: {query.uid}")
        logger.info(f"登录耗时: {elapsed_time:.3f} 秒")
        return True
    else:
        logger.error("登录失败")
        return False


def test_wrong_password():
    """测试错误密码登录"""
    logger = logging.getLogger("login-test")
    
    # 获取配置
    config = get_config()
    username = config['username']
    wrong_password = "wrong_password"
    
    logger.info(f"使用错误密码登录: {username}")
    
    # 创建查询对象并登录
    query = Query()
    success = query.login(username=username, password=wrong_password)
    
    if not success:
        logger.info("使用错误密码登录失败，符合预期")
        return True
    else:
        logger.error("使用错误密码登录成功，不符合预期")
        return False


def main():
    """运行所有登录测试"""
    # 设置日志
    setup_logging()
    logger = logging.getLogger("login-test")
    
    logger.info("=" * 50)
    logger.info("登录测试开始")
    logger.info("=" * 50)
    
    # 测试正常登录
    logger.info("\n" + "-" * 30)
    logger.info("测试1: 正常登录")
    normal_result = test_normal_login()
    
    # 测试错误密码登录
    logger.info("\n" + "-" * 30)
    logger.info("测试2: 错误密码登录")
    wrong_pwd_result = test_wrong_password()
    
    # 汇总结果
    logger.info("\n" + "=" * 50)
    logger.info("测试结果汇总:")
    logger.info(f"正常登录测试: {'通过' if normal_result else '失败'}")
    logger.info(f"错误密码登录测试: {'通过' if wrong_pwd_result else '失败'}")
    logger.info("=" * 50)
    
    # 所有测试都通过才算成功
    return normal_result and wrong_pwd_result


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 