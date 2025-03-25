#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试登录功能，使用atomic_queries.py中的方法
"""

import sys
import logging
import requests
import json
from config import setup_logging, BASE_URL, USERNAME, PASSWORD
from utils import generate_new_cookies

# 设置日志
setup_logging()
logger = logging.getLogger("login-test")

def test_atomic_login():
    """
    使用atomic_queries.py中的方法测试登录
    """
    url = f"{BASE_URL}/api/v1/users/login"
    
    # 尝试获取新的cookies
    cookies = generate_new_cookies(BASE_URL)
    
    # 如果获取cookies失败，使用默认的cookies
    if not cookies:
        logger.warning("获取新cookies失败，使用默认cookies")
        cookies = {
            'JSESSIONID': '9ED5635A2A892A4BA31E7E98533A279D',
            'YsbCaptcha': '025080CF8BA94594B09E283F17815444',
        }
    
    headers = {
        'Proxy-Connection': 'keep-alive',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
        'Content-Type': 'application/json',
        'Origin': url,
        'Referer': f"{BASE_URL}/client_login.html",
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Connection': 'close'
    }
    
    # 使用配置的用户名和密码
    data = f'{{"username":"{USERNAME}","password":"{PASSWORD}"}}'
    
    logger.info(f"正在测试登录: {url}")
    logger.info(f"使用用户名: {USERNAME}")
    logger.info(f"请求数据: {data}")
    
    try:
        # 输出请求详情
        logger.info("发送请求...")
        logger.info(f"Headers: {json.dumps(headers, indent=2)}")
        logger.info(f"Cookies: {json.dumps(cookies, indent=2)}")
        
        # 发送登录请求
        r = requests.post(url=url, headers=headers, cookies=cookies, data=data, verify=False)
        
        # 输出响应详情
        logger.info(f"状态码: {r.status_code}")
        logger.info(f"响应头: {json.dumps(dict(r.headers), indent=2)}")
        logger.info(f"响应体: {r.text}")
        
        if r.status_code != 200:
            logger.error(f"登录请求失败，状态码: {r.status_code}")
            return False
        
        # 解析响应
        try:
            response_json = r.json()
            logger.info(f"JSON响应: {json.dumps(response_json, indent=2)}")
            
            if "data" not in response_json or response_json["data"] is None:
                logger.error("响应中没有data字段或data为空")
                return False
            
            data = response_json.get("data")
            user_id = data.get("userId")
            token = data.get("token")
            
            if not user_id or not token:
                logger.error(f"未找到用户ID或令牌: userId={user_id}, token存在: {bool(token)}")
                return False
            
            logger.info("=" * 50)
            logger.info("登录成功!")
            logger.info(f"用户ID: {user_id}")
            logger.info(f"Token前10位: {token[:10]}...")
            logger.info("=" * 50)
            
            return True
        except ValueError:
            logger.error(f"响应不是有效的JSON格式: {r.text}")
            return False
    except requests.exceptions.ConnectionError as e:
        logger.error(f"连接服务器失败: {e}")
        return False
    except Exception as e:
        logger.error(f"测试登录时发生错误: {e}")
        return False

def main():
    """主函数"""
    logger.info("开始测试原子登录...")
    result = test_atomic_login()
    
    if result:
        logger.info("登录测试成功!")
        return True
    else:
        logger.error("登录测试失败!")
        return False

if __name__ == "__main__":
    # 禁用SSL警告
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    result = main()
    sys.exit(0 if result else 1) 