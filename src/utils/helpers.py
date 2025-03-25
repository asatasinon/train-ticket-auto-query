"""
辅助函数模块，提供各种通用工具函数
"""
import random
import string
import logging
import requests
from typing import List, Dict, Any, Optional

# 导入配置
from .config import HIGHSPEED_WEIGHTS

logger = logging.getLogger("helpers")


def random_boolean() -> bool:
    """
    返回一个随机布尔值
    
    Returns:
        随机的True或False值
    """
    return random.choice([True, False])


def random_from_list(items: List) -> Any:
    """
    从列表中随机选择一个元素
    
    Args:
        items: 输入列表
        
    Returns:
        列表中的随机元素，如果列表为空则返回None
    """
    if not items:
        logger.warning("从空列表中随机选择，返回None")
        return None
    return random.choice(items)


def random_from_weighted(d: dict = None) -> Any:
    """
    根据权重随机选择
    
    Args:
        d: 带相对权重的字典，eg. {'a': 100, 'b': 50}，如果不提供则使用配置中高铁/普通列车的权重
        
    Returns:
        根据权重随机选择的key
    """
    if d is None:
        d = HIGHSPEED_WEIGHTS
        
    total = sum(d.values())    # 权重求和
    ra = random.uniform(0, total)   # 在0与权重和之前获取一个随机数
    curr_sum = 0
    ret = None

    keys = d.keys()
    for k in keys:
        curr_sum += d[k]             # 在遍历中，累加当前权重值
        if ra <= curr_sum:          # 当随机数<=当前权重和时，返回权重key
            ret = k
            break

    return ret


def random_int(min_val: int = 0, max_val: int = 100) -> int:
    """
    生成指定范围内的随机整数
    
    Args:
        min_val: 最小值（包含）
        max_val: 最大值（包含）
        
    Returns:
        指定范围内的随机整数
    """
    return random.randint(min_val, max_val)


def random_float(min_val: float = 0.0, max_val: float = 1.0) -> float:
    """
    生成指定范围内的随机浮点数
    
    Args:
        min_val: 最小值（包含）
        max_val: 最大值（包含）
        
    Returns:
        指定范围内的随机浮点数
    """
    return random.uniform(min_val, max_val)


def random_string(length: int = 8) -> str:
    """
    生成指定长度的随机字符串
    
    Args:
        length: 字符串长度
        
    Returns:
        随机字符串
    """
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def random_phone() -> str:
    """
    生成随机电话号码
    
    Returns:
        随机电话号码字符串
    """
    return ''.join(random.choices(string.digits, k=random.randint(8, 15)))


def generate_new_cookies(base_url: str) -> Optional[Dict[str, str]]:
    """
    生成新的cookies
    
    Args:
        base_url: 服务器基础URL
        
    Returns:
        新生成的cookies字典，如果失败则返回None
    """
    try:
        # 访问验证码生成接口来获取新的cookies
        verify_url = f"{base_url}/api/v1/verifycode/generate"
        logger.info(f"获取新cookies: {verify_url}")
        
        response = requests.get(verify_url)
        if response.status_code != 200:
            logger.warning(f"获取cookies失败: {response.status_code}")
            return None
            
        # 从响应中提取cookies
        cookies = response.cookies.get_dict()
        logger.info(f"获取到新cookies: {cookies}")
        return cookies
    except Exception as e:
        logger.error(f"生成cookies时出错: {e}")
        return None
