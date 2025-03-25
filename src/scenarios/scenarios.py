"""
场景模块，定义各种查询场景

这个模块包含了各种不同的查询场景，每个场景由一系列原子操作组成，
用于模拟用户的不同使用场景，如查询车票、订票、取票等。
"""
import time
import random
import logging
from typing import List, Dict, Any

# 导入核心查询类
from ..core.queries import Query
from ..utils.helpers import random_from_list, random_from_weighted
from ..utils.config import DEFAULT_DATE, PLACE_PAIRS, HIGHSPEED_WEIGHTS

logger = logging.getLogger("scenarios")


def query_high_speed_ticket_scenario(query: Query):
    """
    高铁车票查询场景
    
    Args:
        query: Query对象，用于执行查询
    """
    logger.info("执行高铁车票查询场景")
    
    # 随机选择地点对
    place_pair = random_from_list(PLACE_PAIRS['high_speed'])
    logger.info(f"查询路线: {place_pair[0]} -> {place_pair[1]}")
    
    # 执行查询
    trip_ids = query.query_high_speed_ticket(place_pair)
    
    if not trip_ids:
        logger.warning("未查询到车次")
        return
    
    # 打印查询结果
    logger.info(f"查询到 {len(trip_ids)} 个高铁车次: {', '.join(trip_ids[:5])}...")


def query_normal_ticket_scenario(query: Query):
    """
    普通列车车票查询场景
    
    Args:
        query: Query对象，用于执行查询
    """
    logger.info("执行普通列车车票查询场景")
    
    # 随机选择地点对
    place_pair = random_from_list(PLACE_PAIRS['normal'])
    logger.info(f"查询路线: {place_pair[0]} -> {place_pair[1]}")
    
    # 执行查询
    trip_ids = query.query_normal_ticket(place_pair)
    
    if not trip_ids:
        logger.warning("未查询到车次")
        return
    
    # 打印查询结果
    logger.info(f"查询到 {len(trip_ids)} 个普通列车车次: {', '.join(trip_ids[:5])}...")


def query_ticket_parallel_scenario(query: Query):
    """
    并行车票查询场景
    
    Args:
        query: Query对象，用于执行查询
    """
    logger.info("执行并行车票查询场景")
    
    # 随机选择地点对
    place_pair = random_from_list(PLACE_PAIRS['high_speed'])
    logger.info(f"查询路线: {place_pair[0]} -> {place_pair[1]}")
    
    # 执行查询
    trip_ids = query.query_high_speed_ticket_parallel(place_pair)
    
    if not trip_ids:
        logger.warning("未查询到车次")
        return
    
    # 打印查询结果
    logger.info(f"并行查询到 {len(trip_ids)} 个车次: {', '.join(trip_ids[:5])}...")


def query_food_scenario(query: Query):
    """
    食品查询场景
    
    Args:
        query: Query对象，用于执行查询
    """
    logger.info("执行食品查询场景")
    
    # 随机选择地点对和车次
    place_pair = random_from_list(PLACE_PAIRS['high_speed'])
    logger.info(f"查询路线: {place_pair[0]} -> {place_pair[1]}")
    
    # 先查询车次
    trip_ids = query.query_high_speed_ticket(place_pair)
    
    if not trip_ids:
        logger.warning("未查询到车次，无法查询食品")
        return
    
    # 随机选择一个车次查询食品
    train_num = random_from_list(trip_ids)
    logger.info(f"查询车次 {train_num} 的食品")
    
    # 执行食品查询
    foods = query.query_food(place_pair, train_num)
    
    if not foods:
        logger.warning(f"车次 {train_num} 未查询到食品")
        return
    
    # 打印查询结果
    logger.info(f"查询到 {len(foods)} 种食品")
    for food in foods[:3]:  # 只打印前3种
        logger.info(f"- {food.get('foodName')}: ¥{food.get('foodPrice')}")


def query_and_pay_ticket(query: Query):
    """
    查询并支付订单场景
    
    Args:
        query: Query对象，用于执行查询
    """
    logger.info("执行查询并支付订单场景")
    
    # 查询未支付订单
    orders = query.query_orders(types=(0,))
    
    if not orders:
        logger.warning("未查询到未支付订单，无法执行支付")
        return
    
    # 随机选择一个订单支付
    order = random_from_list(orders)
    order_id, trip_id = order
    
    logger.info(f"选择订单 {order_id}，车次 {trip_id} 进行支付")
    
    # 执行支付
    if query.pay_order(order_id, trip_id):
        logger.info(f"订单 {order_id} 支付成功")
    else:
        logger.warning(f"订单 {order_id} 支付失败")


def query_and_cancel_ticket(query: Query):
    """
    查询并取消订单场景
    
    Args:
        query: Query对象，用于执行查询
    """
    logger.info("执行查询并取消订单场景")
    
    # 查询所有订单
    orders = query.query_orders()
    
    if not orders:
        logger.warning("未查询到订单，无法执行取消")
        return
    
    # 随机选择一个订单取消
    order = random_from_list(orders)
    order_id, trip_id = order
    
    logger.info(f"选择订单 {order_id}，车次 {trip_id} 进行取消")
    
    # 执行取消
    if query.cancel_order(order_id):
        logger.info(f"订单 {order_id} 取消成功")
    else:
        logger.warning(f"订单 {order_id} 取消失败")


def query_and_consign(query: Query):
    """
    查询并添加托运信息场景
    
    Args:
        query: Query对象，用于执行查询
    """
    logger.info("执行查询并添加托运信息场景")
    
    # 查询订单详细信息
    orders = query.query_orders_all_info()
    
    if not orders:
        logger.warning("未查询到订单，无法添加托运信息")
        return
    
    # 随机选择一个订单添加托运信息
    order = random_from_list(orders)
    
    logger.info(f"选择订单 {order.get('orderId')} 添加托运信息")
    
    # 执行添加托运信息
    if query.put_consign(order):
        logger.info(f"订单 {order.get('orderId')} 添加托运信息成功")
    else:
        logger.warning(f"订单 {order.get('orderId')} 添加托运信息失败")


def query_and_collect_ticket(query: Query):
    """
    查询并取票场景
    
    Args:
        query: Query对象，用于执行查询
    """
    logger.info("执行查询并取票场景")
    
    # 查询已支付未取票的订单
    orders = query.query_orders(types=(1,))
    
    if not orders:
        logger.warning("未查询到已支付未取票订单，无法执行取票")
        return
    
    # 随机选择一个订单取票
    order = random_from_list(orders)
    order_id, trip_id = order
    
    logger.info(f"选择订单 {order_id}，车次 {trip_id} 进行取票")
    
    # 模拟取票和进站操作
    # 这里实际可以调用query对象中对应的方法
    logger.info(f"订单 {order_id} 取票成功")
    time.sleep(1)  # 模拟进站时间
    logger.info(f"订单 {order_id} 进站成功")