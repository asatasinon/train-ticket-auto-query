"""
配置管理模块，负责从.env文件加载配置并提供访问接口
"""
import os
import time
import logging
from typing import Dict, Any
import requests


# 尝试导入dotenv库，如果没有安装则给出提示
try:
    from dotenv import load_dotenv
except ImportError:
    print("请先安装python-dotenv库: pip install python-dotenv")
    raise

# 加载.env文件中的环境变量
load_dotenv()

# 日志配置
LOG_LEVEL = os.getenv('TS_LOG_LEVEL', 'INFO')
LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

# 系统配置
BASE_URL = os.getenv('TS_BASE_URL', 'http://139.196.152.44:31000')
USERNAME = os.getenv('TS_USERNAME', 'fdse_microservice')
PASSWORD = os.getenv('TS_PASSWORD', '111111')

# 当前日期，如果没有设置则使用当前日期
DEFAULT_DATE = os.getenv('TS_DEFAULT_DATE', '')
if not DEFAULT_DATE:
    DEFAULT_DATE = time.strftime("%Y-%m-%d", time.localtime())

# 地点配置
PLACE_SHANG_HAI = os.getenv('TS_PLACE_SHANG_HAI', 'Shang Hai')
PLACE_SU_ZHOU = os.getenv('TS_PLACE_SU_ZHOU', 'Su Zhou')
PLACE_NAN_JING = os.getenv('TS_PLACE_NAN_JING', 'Nan Jing')

# 权重配置
HIGHSPEED_WEIGHT = int(os.getenv('TS_HIGHSPEED_WEIGHT', 60))
NORMAL_WEIGHT = int(os.getenv('TS_NORMAL_WEIGHT', 40))
HIGHSPEED_WEIGHTS = {True: HIGHSPEED_WEIGHT, False: NORMAL_WEIGHT}

# 批量执行配置
BATCH_COUNT = int(os.getenv('TS_BATCH_COUNT', 100))
BATCH_INTERVAL = float(os.getenv('TS_BATCH_INTERVAL', 1))

# 场景相关配置
PLACE_PAIRS = {
    'high_speed': [
        (PLACE_SHANG_HAI, PLACE_SU_ZHOU),
        (PLACE_SU_ZHOU, PLACE_SHANG_HAI),
        (PLACE_NAN_JING, PLACE_SHANG_HAI)
    ],
    'normal': [
        (PLACE_SHANG_HAI, PLACE_NAN_JING),
        (PLACE_NAN_JING, PLACE_SHANG_HAI)
    ]
}


def get_config() -> Dict[str, Any]:
    """
    获取所有配置项
    
    Returns:
        包含所有配置的字典
    """
    return {
        'base_url': BASE_URL,
        'username': USERNAME,
        'password': PASSWORD,
        'default_date': DEFAULT_DATE,
        'place_pairs': PLACE_PAIRS,
        'highspeed_weights': HIGHSPEED_WEIGHTS,
        'batch_count': BATCH_COUNT,
        'batch_interval': BATCH_INTERVAL,
        'log_level': LOG_LEVEL
    }


def setup_logging():
    """配置日志系统"""
    log_level = LOG_LEVELS.get(LOG_LEVEL, logging.INFO)
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def check_config() -> bool:
    """
    检查配置是否有效
    
    Returns:
        配置是否有效
    """
    logger = logging.getLogger("config-check")
    
    # 检查BASE_URL是否有效
    if not BASE_URL:
        logger.error("BASE_URL未设置，请在.env文件中配置TS_BASE_URL")
        return False
    
    # 尝试连接服务器
    try:
        logger.info(f"正在检查服务器连接: {BASE_URL}")
        r = requests.get(f"{BASE_URL}/client_login.html", timeout=5)
        if r.status_code != 200:
            logger.error(f"服务器连接失败，状态码: {r.status_code}")
            return False
        logger.info("服务器连接成功")
        return True
    except requests.exceptions.ConnectionError:
        logger.error(f"无法连接到服务器: {BASE_URL}")
        logger.error("请检查服务器地址和网络连接")
        return False
    except requests.exceptions.Timeout:
        logger.error(f"连接服务器超时: {BASE_URL}")
        logger.error("服务器响应时间过长，请检查网络连接")
        return False
    except Exception as e:
        logger.error(f"检查配置时发生错误: {e}")
        return False 