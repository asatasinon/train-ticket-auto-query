from queries import Query
from utils import random_from_weighted, random_from_list
from config import HIGHSPEED_WEIGHTS, PLACE_SHANG_HAI, PLACE_SU_ZHOU, PLACE_NAN_JING, DEFAULT_DATE
import logging

logger = logging.getLogger("autoquery-scenario")


def query_and_cancel(q: Query):
    """
    查询订单并取消
    
    Args:
        q: 查询对象
    """
    if random_from_weighted(HIGHSPEED_WEIGHTS):
        pairs = q.query_orders(types=tuple([0, 1]))
    else:
        pairs = q.query_orders(types=tuple([0, 1]), query_other=True)

    if not pairs:
        return

    # (orderId, tripId)
    pair = random_from_list(pairs)

    order_id = q.cancel_order(order_id=pair[0])
    if not order_id:
        return

    logger.info(f"{order_id} 已查询并取消")


def query_and_collect(q: Query):
    """
    查询订单并取票
    
    Args:
        q: 查询对象
    """
    if random_from_weighted(HIGHSPEED_WEIGHTS):
        pairs = q.query_orders(types=tuple([1]))
    else:
        pairs = q.query_orders(types=tuple([1]), query_other=True)

    if not pairs:
        return

    # (orderId, tripId)
    pair = random_from_list(pairs)

    order_id = q.collect_order(order_id=pair[0])
    if not order_id:
        return

    logger.info(f"{order_id} 已查询并取票")


def query_and_execute(q: Query):
    """
    查询订单并进站
    
    Args:
        q: 查询对象
    """
    if random_from_weighted(HIGHSPEED_WEIGHTS):
        pairs = q.query_orders(types=tuple([1]))
    else:
        pairs = q.query_orders(types=tuple([1]), query_other=True)

    if not pairs:
        return

    # (orderId, tripId)
    pair = random_from_list(pairs)

    order_id = q.enter_station(order_id=pair[0])
    if not order_id:
        return

    logger.info(f"{order_id} 已查询并进站")


def query_and_preserve(q: Query):
    """
    查询并预订车票
    
    Args:
        q: 查询对象
    """
    start = ""
    end = ""
    trip_ids = []

    high_speed = random_from_weighted(HIGHSPEED_WEIGHTS)
    if high_speed:
        start = PLACE_SHANG_HAI
        end = PLACE_SU_ZHOU
        high_speed_place_pair = (start, end)
        trip_ids = q.query_high_speed_ticket(place_pair=high_speed_place_pair, time=DEFAULT_DATE)
    else:
        start = PLACE_SHANG_HAI
        end = PLACE_NAN_JING
        other_place_pair = (start, end)
        trip_ids = q.query_normal_ticket(place_pair=other_place_pair, time=DEFAULT_DATE)

    _ = q.query_assurances()

    q.preserve(start, end, trip_ids, high_speed)


def query_and_consign(q: Query):
    """
    查询订单并托运
    
    Args:
        q: 查询对象
    """
    if random_from_weighted(HIGHSPEED_WEIGHTS):
        list = q.query_orders_all_info()
    else:
        list = q.query_orders_all_info(query_other=True)

    if not list:
        return

    # (orderId, tripId)
    res = random_from_list(list)
    order_id = q.put_consign(res)

    if not order_id:
        return

    logger.info(f"{order_id} 已查询并托运")


def query_and_pay(q: Query):
    """
    查询订单并支付
    
    Args:
        q: 查询对象
    """
    if random_from_weighted(HIGHSPEED_WEIGHTS):
        pairs = q.query_orders(types=tuple([0, 1]))
    else:
        pairs = q.query_orders(types=tuple([0, 1]), query_other=True)

    if not pairs:
        return

    # (orderId, tripId)
    pair = random_from_list(pairs)
    order_id = q.pay_order(pair[0], pair[1])

    if not order_id:
        return

    logger.info(f"{order_id} 已查询并支付")


def query_and_rebook(q: Query):
    """
    查询订单并改签
    
    Args:
        q: 查询对象
    """
    if random_from_weighted(HIGHSPEED_WEIGHTS):
        pairs = q.query_orders(types=tuple([0, 1]))
    else:
        pairs = q.query_orders(types=tuple([0, 1]), query_other=True)

    if not pairs:
        return

    # (orderId, tripId)
    pair = random_from_list(pairs)

    order_id = q.cancel_order(order_id=pair[0])
    if not order_id:
        return

    q.rebook_ticket(pair[0], pair[1], pair[1])
    logger.info(f"{order_id} 已查询并改签")