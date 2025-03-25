import random
from typing import List, Any
import string
import logging
import requests

# 导入配置
from config import HIGHSPEED_WEIGHTS

logger = logging.getLogger("utils")


def random_boolean() -> bool:
    """
    返回一个随机布尔值
    """
    return random.choice([True, False])


def random_from_list(items: List) -> Any:
    """
    从列表中随机选择一个元素
    
    Args:
        items: 输入列表
        
    Returns:
        列表中的随机元素
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
        返回随机选择的key
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


def random_str() -> str:
    """
    生成随机字符串
    
    Returns:
        随机字符串
    """
    return ''.join(random.choices(
        string.ascii_letters, 
        k=random.randint(4, 10)
    ))


def random_phone() -> str:
    """
    生成随机电话号码
    
    Returns:
        随机电话号码字符串
    """
    return ''.join(random.choices(string.digits, k=random.randint(8, 15)))


def generate_new_cookies(base_url):
    """
    生成新的cookies
    
    Args:
        base_url: 服务器基础URL
        
    Returns:
        新生成的cookies字典
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
