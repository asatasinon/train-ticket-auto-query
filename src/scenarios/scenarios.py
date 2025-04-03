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
from ..utils.helpers import random_from_list, random_from_weighted, random_string, random_phone
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


def query_and_book_ticket_scenario(query: Query):
    """
    查询并预订车票场景
    
    Args:
        query: Query对象，用于执行查询
    """
    logger.info("执行查询并预订车票场景")
    
    # 随机决定是预订高铁还是普通列车
    high_speed = random_from_weighted(HIGHSPEED_WEIGHTS)
    start = ""
    end = ""
    trip_ids = []
    
    # 根据车票类型查询可用车次
    if high_speed:
        # 高铁路线
        place_pair = random_from_list(PLACE_PAIRS['high_speed'])
        start, end = place_pair
        logger.info(f"查询高铁路线: {start} -> {end}")
        trip_ids = query.query_high_speed_ticket(place_pair=place_pair)
    else:
        # 普通列车路线
        place_pair = random_from_list(PLACE_PAIRS['normal'])
        start, end = place_pair
        logger.info(f"查询普通列车路线: {start} -> {end}")
        trip_ids = query.query_normal_ticket(place_pair=place_pair)
    
    # 如果没有查询到车次，退出场景
    if not trip_ids:
        logger.warning("未查询到可用车次，无法预订车票")
        return
    
    logger.info(f"查询到 {len(trip_ids)} 个车次，准备预订车票")
    
    # 查询保险选项
    query.query_assurances()
    
    # 执行预订操作
    query.preserve(start, end, trip_ids, high_speed)
    
    logger.info("预订车票场景执行完成")


def query_and_rebook_ticket_scenario(query: Query):
    """
    查询并改签车票场景
    
    Args:
        query: Query对象，用于执行查询
    """
    logger.info("执行查询并改签车票场景")
    
    # 查询可改签的订单（状态为0-未支付或1-已支付）
    orders = []
    # 随机决定是查询高铁还是普通列车订单
    if random_from_weighted(HIGHSPEED_WEIGHTS):
        logger.info("查询高铁订单进行改签")
        orders = query.query_orders(types=(0, 1))
    else:
        logger.info("查询普通列车订单进行改签")
        orders = query.query_orders(types=(0, 1), query_other=True)
    
    # 如果没有查询到订单，退出场景
    if not orders:
        logger.warning("未查询到可改签的订单，无法执行改签")
        return
    
    # 随机选择一个订单进行改签
    order = random_from_list(orders)
    order_id, trip_id = order
    
    logger.info(f"选择订单 {order_id}，车次 {trip_id} 进行改签")
    
    # 获取当前日期作为新日期
    new_date = DEFAULT_DATE
    # 随机选择新的座位类型 (2-一等座，3-二等座)
    new_seat_type = random_from_list(["2", "3"])
    
    # 执行改签操作（改为同一车次的不同座位类型）
    # 注意：在实际场景中，可能需要先查询可用的车次，然后选择不同的车次进行改签
    logger.info(f"改签为同一车次的座位类型 {new_seat_type}")
    query.rebook_ticket(order_id, trip_id, trip_id, new_date, new_seat_type)
    
    logger.info(f"订单 {order_id} 改签场景执行完成")