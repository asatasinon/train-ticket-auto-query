"""
Train-Ticket 查询核心模块，提供与系统交互的API封装
"""
from typing import List, Dict, Tuple, Any, Optional
import requests
import logging
import time
import random

# 导入项目内模块
from ..utils.helpers import random_from_list, generate_new_cookies
from ..utils.config import BASE_URL, USERNAME, PASSWORD, DEFAULT_DATE, PLACE_PAIRS

logger = logging.getLogger("auto-queries")
datestr = time.strftime("%Y-%m-%d", time.localtime())


class Query:
    """Train-Ticket 查询类，负责与API交互"""

    def __init__(self, ts_address: str = None) -> None:
        """
        初始化查询类
        
        Args:
            ts_address: Train-Ticket系统地址，如果为None则使用配置文件中的地址
        """
        # 如果未提供地址，使用配置中的基础URL
        self.address = ts_address if ts_address else BASE_URL
        self.uid = ""
        self.token = ""
        self.session = requests.Session()
        self.session.headers.update({
            'Proxy-Connection': 'keep-alive',
            'Accept': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
            'Content-Type': 'application/json',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
        })

    def login(self, username=None, password=None) -> bool:
        """
        登陆并建立session，返回登陆结果
        
        Args:
            username: 用户名，如果为None则使用配置文件中的用户名
            password: 密码，如果为None则使用配置文件中的密码
            
        Returns:
            登录是否成功
        """
        # 使用配置中的用户名密码，如未提供
        username = username if username else USERNAME
        password = password if password else PASSWORD
        
        url = f"{self.address}/api/v1/users/login"
        
        # 首先尝试获取新的cookies
        cookies = generate_new_cookies(self.address)
        
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
            'Referer': f"{self.address}/client_login.html",
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'close'
        }

        # 构建登录数据
        data = '{"username":"' + username + '","password":"' + password + '"}'

        try:
            r = requests.post(url=url, headers=headers,
                              cookies=cookies, data=data, verify=False)

            if r.status_code == 200 and r.json().get("data"):
                data = r.json().get("data")
                self.uid = data.get("userId")
                self.token = data.get("token")
                
                # 更新会话中的认证信息
                self.session.headers.update({
                    "Authorization": f"Bearer {self.token}",
                    "Cookie": f"JSESSIONID={cookies.get('JSESSIONID', '')}; YsbCaptcha={cookies.get('YsbCaptcha', '')}"
                })
                
                logger.info(f"登录成功，用户ID: {self.uid}")
                return True
            else:
                logger.error(f"登录失败: {r.status_code} - {r.text}")
                return False
                
        except Exception as e:
            logger.error(f"登录过程中出现异常: {e}")
            return False

    def query_high_speed_ticket(self, place_pair: tuple = None, 
                                date: str = None) -> List[str]:
        """
        查询高铁票
        
        Args:
            place_pair: 出发地和目的地元组，如果为None则随机选择
            date: 日期，格式为YYYY-MM-DD，如果为None则使用配置中的日期
            
        Returns:
            高铁车次列表
        """
        # 使用配置中的默认值，如果未提供
        if place_pair is None:
            place_pair = random_from_list(PLACE_PAIRS['high_speed'])
        
        date = date if date else DEFAULT_DATE
        
        url = f"{self.address}/api/v1/travelservice/trips/left"
        
        payload = {
            "departureTime": date,
            "startingPlace": place_pair[0],
            "endPlace": place_pair[1],
        }
        
        try:
            response = self.session.post(url=url, json=payload)
            
            if response.status_code != 200 or not response.json().get("data"):
                logger.warning(f"查询高铁票失败: {response.status_code} - {response.text}")
                return []
            
            data = response.json().get("data")
            
            trip_ids = []
            for d in data:
                trip_id = d.get("tripId").get("type") + d.get("tripId").get("number")
                trip_ids.append(trip_id)
                
            logger.info(f"查询到 {len(trip_ids)} 个高铁车次")
            return trip_ids
            
        except Exception as e:
            logger.error(f"查询高铁票过程中出现异常: {e}")
            return []

    def query_normal_ticket(self, place_pair: tuple = None, 
                            date: str = None) -> List[str]:
        """
        查询普通列车票
        
        Args:
            place_pair: 出发地和目的地元组，如果为None则随机选择
            date: 日期，格式为YYYY-MM-DD，如果为None则使用配置中的日期
            
        Returns:
            普通列车车次列表
        """
        # 使用配置中的默认值，如果未提供
        if place_pair is None:
            place_pair = random_from_list(PLACE_PAIRS['normal'])
        
        date = date if date else DEFAULT_DATE
        
        url = f"{self.address}/api/v1/travel2service/trips/left"
        
        payload = {
            "departureTime": date,
            "startingPlace": place_pair[0],
            "endPlace": place_pair[1],
        }
        
        try:
            response = self.session.post(url=url, json=payload)
            
            if response.status_code != 200 or not response.json().get("data"):
                logger.warning(f"查询普通列车票失败: {response.status_code} - {response.text}")
                return []
            
            data = response.json().get("data")
            
            trip_ids = []
            for d in data:
                trip_id = d.get("tripId").get("type") + d.get("tripId").get("number")
                trip_ids.append(trip_id)
                
            logger.info(f"查询到 {len(trip_ids)} 个普通列车车次")
            return trip_ids
            
        except Exception as e:
            logger.error(f"查询普通列车票过程中出现异常: {e}")
            return []

    def query_orders(self, types: tuple = (0, 1), 
                     query_other: bool = False) -> List[tuple]:
        """
        查询订单
        
        Args:
            types: 订单类型，0=未支付，1=已支付
            query_other: 是否查询其他类型订单
            
        Returns:
            订单信息列表，每项为(orderId, tripId)元组
        """
        if query_other:
            url = f"{self.address}/api/v1/orderOtherService/orderOther/refresh"
        else:
            url = f"{self.address}/api/v1/orderservice/order/refresh"
        
        payload = {
            "loginId": self.uid,
        }
        
        try:
            response = self.session.post(url=url, json=payload)
            
            if response.status_code != 200 or not response.json().get("data"):
                logger.warning(f"查询订单失败: {response.status_code} - {response.text}")
                return []
            
            data = response.json().get("data")
            pairs = []
            
            for d in data:
                order_status = d.get("status")
                
                # 按类型过滤
                if order_status in types:
                    pairs.append((d.get("id"), d.get("trainNumber")))
            
            logger.info(f"查询到 {len(pairs)} 个订单")
            return pairs
            
        except Exception as e:
            logger.error(f"查询订单过程中出现异常: {e}")
            return []

    def query_food(self, place_pair: tuple = None, 
                   train_num: str = None, 
                   date: str = None) -> List[Dict]:
        """
        查询食品
        
        Args:
            place_pair: 出发地和目的地元组，如果为None则随机选择
            train_num: 车次号，如果为None则使用"D1345"
            date: 日期，格式为YYYY-MM-DD，如果为None则使用配置中的日期
            
        Returns:
            食品信息列表
        """
        # 使用默认值，如果未提供
        if place_pair is None:
            place_pair = random_from_list(PLACE_PAIRS['high_speed'])
        
        train_num = train_num if train_num else "D1345"
        date = date if date else DEFAULT_DATE
        
        url = f"{self.address}/api/v1/foodservice/foods/{date}/{place_pair[0]}/{place_pair[1]}/{train_num}"
        
        try:
            response = self.session.get(url=url)
            
            if response.status_code != 200 or not response.json().get("data"):
                logger.warning(f"查询食品失败: {response.status_code} - {response.text}")
                return []
            
            data = response.json().get("data")
            logger.info(f"查询到 {len(data)} 种食品")
            return data
            
        except Exception as e:
            logger.error(f"查询食品过程中出现异常: {e}")
            return []
    
    def cancel_order(self, order_id: str) -> bool:
        """
        取消订单
        
        Args:
            order_id: 订单ID
            
        Returns:
            是否成功取消订单
        """
        url = f"{self.address}/api/v1/cancelservice/cancel/{order_id}/{self.uid}"
        
        try:
            response = self.session.get(url=url)
            
            if response.status_code != 200 or not response.json().get("data"):
                logger.warning(f"取消订单失败: {response.status_code} - {response.text}")
                return False
            
            data = response.json().get("data")
            logger.info(f"成功取消订单 {order_id}")
            return True
            
        except Exception as e:
            logger.error(f"取消订单过程中出现异常: {e}")
            return False
    
    def pay_order(self, order_id: str, trip_id: str) -> bool:
        """
        支付订单
        
        Args:
            order_id: 订单ID
            trip_id: 车次ID
            
        Returns:
            是否支付成功
        """
        url = f"{self.address}/api/v1/inside_pay_service/inside_payment"
        
        payload = {
            "orderId": order_id,
            "tripId": trip_id
        }
        
        try:
            response = self.session.post(url=url, json=payload)
            
            if response.status_code != 200 or not response.json().get("data"):
                logger.warning(f"支付订单失败: {response.status_code} - {response.text}")
                return False
            
            logger.info(f"成功支付订单 {order_id}")
            return True
            
        except Exception as e:
            logger.error(f"支付订单过程中出现异常: {e}")
            return False
    
    def put_consign(self, order_info: Dict) -> bool:
        """
        添加托运信息
        
        Args:
            order_info: 订单信息，包含accountId, targetDate, orderId, from, to字段
            
        Returns:
            是否添加成功
        """
        url = f"{self.address}/api/v1/consignservice/consigns"
        
        # 生成随机重量和名称
        weight = round(random.uniform(1.0, 10.0), 1)
        consign_name = f"Consign-{int(time.time())}"
        
        payload = {
            "accountId": order_info.get("accountId"),
            "handleDate": order_info.get("targetDate"),
            "targetDate": order_info.get("targetDate"),
            "from": order_info.get("from"),
            "to": order_info.get("to"),
            "orderId": order_info.get("orderId"),
            "consignee": self.uid,
            "phone": "12345678900",
            "weight": weight,
            "id": "",
            "isWithin": False,
            "name": consign_name
        }
        
        try:
            response = self.session.post(url=url, json=payload)
            
            if response.status_code != 200 or not response.json().get("data"):
                logger.warning(f"添加托运信息失败: {response.status_code} - {response.text}")
                return False
            
            logger.info(f"成功添加托运信息 {consign_name} 到订单 {order_info.get('orderId')}")
            return True
            
        except Exception as e:
            logger.error(f"添加托运信息过程中出现异常: {e}")
            return False
            
    def query_orders_all_info(self, query_other: bool = False) -> List[Dict]:
        """
        查询订单的详细信息（用于托运服务）
        
        Args:
            query_other: 是否查询其他类型订单
            
        Returns:
            订单详细信息列表
        """
        if query_other:
            url = f"{self.address}/api/v1/orderOtherService/orderOther/refresh"
        else:
            url = f"{self.address}/api/v1/orderservice/order/refresh"
        
        payload = {
            "loginId": self.uid,
        }
        
        try:
            response = self.session.post(url=url, json=payload)
            
            if response.status_code != 200 or not response.json().get("data"):
                logger.warning(f"查询订单详细信息失败: {response.status_code} - {response.text}")
                return []
            
            data = response.json().get("data")
            results = []
            
            for d in data:
                result = {}
                result["accountId"] = d.get("accountId")
                result["targetDate"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                result["orderId"] = d.get("id")
                result["from"] = d.get("from")
                result["to"] = d.get("to")
                results.append(result)
            
            logger.info(f"查询到 {len(results)} 个详细订单信息")
            return results
            
        except Exception as e:
            logger.error(f"查询订单详细信息过程中出现异常: {e}")
            return []

    def query_high_speed_ticket_parallel(self, place_pair: tuple = (), time: str = "", headers: dict = {}) -> List[str]:
        """
        返回TripId 列表
        :param place_pair: 使用的开始结束组对
        :param headers: 请求头
        :return: TripId 列表
        """

        url = f"{self.address}/api/v1/travelservice/trips/left_parallel"
        place_pairs = [("Shang Hai", "Su Zhou"),
                       ("Su Zhou", "Shang Hai"),
                       ("Nan Jing", "Shang Hai")]

        if place_pair == ():
            place_pair = random.choice(place_pairs)

        if time == "":
            time = datestr

        payload = {
            "departureTime": time,
            "startingPlace": place_pair[0],
            "endPlace": place_pair[1],
        }

        response = self.session.post(url=url, headers=headers, json=payload)

        if response.status_code != 200 or response.json().get("data") is None:
            logger.warning(
                f"request for {url} failed. response data is {response.text}")
            return None

        data = response.json().get("data")  # type: dict

        trip_ids = []
        for d in data:
            trip_id = d.get("tripId").get("type") + \
                d.get("tripId").get("number")
            trip_ids.append(trip_id)
        return trip_ids

    def query_advanced_ticket(self, place_pair: tuple = (), type: str = "cheapest", date: str = "", headers: dict = {}) -> List[str]:
        """
        高级查询
        :param type [cheapet, quickest, minStation]
        """

        url = f"{self.address}/api/v1/travelplanservice/travelPlan/{type}"
        place_pairs = [("Shang Hai", "Su Zhou"),
                       ("Su Zhou", "Shang Hai"),
                       ("Nan Jing", "Shang Hai")]

        if place_pair == ():
            place_pair = random.choice(place_pairs)

        if date == "":
            date = datestr

        payload = {
            "departureTime": date,
            "startingPlace": place_pair[0],
            "endPlace": place_pair[1],
        }

        response = self.session.post(url=url, headers=headers, json=payload)

        if response.status_code != 200 or response.json().get("data") is None:
            logger.warning(
                f"request for {url} failed. response data is {response.text}")
            return None

        data = response.json().get("data")

        trip_ids = []
        for d in data:
            trip_id = d.get("tripId")
            trip_ids.append(trip_id)
        return trip_ids

    def query_assurances(self, headers: dict = {}):
        url = f"{self.address}/api/v1/assuranceservice/assurances/types"

        response = self.session.get(url=url, headers=headers)
        if response.status_code != 200 or response.json().get("data") is None:
            logger.warning(
                f"query assurance failed, response data is {response.text}")
            return None
        _ = response.json().get("data")
        # assurance只有一种

        return [{"assurance": "1"}]

    def query_food(self, place_pair: tuple = ("Shang Hai", "Su Zhou"), train_num: str = "D1345", headers: dict = {}):
        url = f"{self.address}/api/v1/foodservice/foods/2021-07-14/{place_pair[0]}/{place_pair[1]}/{train_num}"

        response = self.session.get(url=url, headers=headers)
        if response.status_code != 200 or response.json().get("data") is None:
            logger.warning(
                f"query food failed, response data is {response.text}")
            return None
        _ = response.json().get("data")

        # food 是什么不会对后续调用链有影响，因此查询后返回一个固定数值
        return [{
            "foodName": "Soup",
            "foodPrice": 3.7,
            "foodType": 2,
            "stationName": "Su Zhou",
            "storeName": "Roman Holiday"
        }]

    def query_contacts(self, headers: dict = {}) -> List[str]:
        """
        返回座位id列表
        :param headers:
        :return: id list
        """
        url = f"{self.address}/api/v1/contactservice/contacts/account/{self.uid}"

        response = self.session.get(url=url, headers=headers)
        if response.status_code != 200 or response.json().get("data") is None:
            logger.warning(
                f"query contacts failed, response data is {response.text}")
            return None

        data = response.json().get("data")
        # print("contacts")
        # pprint(data)

        ids = [d.get("id") for d in data if d.get("id") != None]
        # pprint(ids)
        return ids

    def query_other_orders(self, types: tuple = tuple([0, 1]), headers: dict = {}) -> List[tuple]:
        return self.query_orders(types, True, headers)

    def query_route(self, routeId: str = '', headers: dict = {}):
        if routeId == '':
            url = f"{self.address}/api/v1/routeservice/routes"
        else:
            url = f"{self.address}/api/v1/routeservice/routes/{routeId}"

        res = self.session.get(url=url, headers=headers)

        if res.status_code == 200:
            logger.info(f"query routeId success")
        else:
            logger.warning(
                f"query routeId: {routeId} fail, code: {res.status_code}, text: {res.text}")

        return

    def query_cheapest(self, date="", headers: dict = {}):
        self.query_advanced_ticket(type="cheapest", date=date)

    def query_min_station(self, date="", headers: dict = {}):
        self.query_advanced_ticket(type="minStation", date=date)

    def query_quickest(self, date="", headers: dict = {}):
        self.query_advanced_ticket(type="quickest", date=date)

    def query_admin_basic_price(self, headers: dict = {}):
        url = f"{self.address}/api/v1/adminbasicservice/adminbasic/prices"
        response = self.session.get(url=url, headers=headers)

        if response.status_code == 200:
            logger.info(f"query price success")
            return response
        else:
            logger.warning(f"query price failed")
            return None

    def query_admin_basic_config(self, headers: dict = {}):
        url = f"{self.address}/api/v1/adminbasicservice/adminbasic/configs"
        response = self.session.get(url=url, headers=headers)
        if response.status_code == 200:
            logger.info(f"config success")
            return response
        else:
            logger.warning(f"config failed")
            return None

    def rebook_ticket(self, old_order_id, old_trip_id, new_trip_id, new_date="", new_seat_type="", headers: dict = {}):
        url = f"{self.address}/api/v1/rebookservice/rebook"

        if new_date == "":
            new_date = datestr

        if new_seat_type == "":
            new_seat_type = random_from_list(["2", "3"])

        payload = {
            "oldTripId": old_trip_id,
            "orderId": old_order_id,
            "tripId": new_trip_id,
            "date": new_date,
            "seatType": new_seat_type
        }
        # print(payload)
        r = self.session.post(url=url, json=payload, headers=headers)
        if r.status_code == 200:
            logger.info(r.text)
        else:
            logger.warning(
                f"Request Failed: status code: {r.status_code}, {r.text}")

        return

    def query_admin_travel(self, headers: dict = {}):
        url = f"{self.address}/api/v1/admintravelservice/admintravel"

        r = self.session.get(url=url, headers=headers)
        if r.status_code == 200 and r.json()["status"] == 1:
            logger.info("success to query admin travel")
        else:
            logger.warning(
                f"faild to query admin travel with status_code: {r.status_code}")
        return

    def preserve(self, start: str, end: str, trip_ids: List = [], is_high_speed: bool = True, date: str = "", headers: dict = {}):
        if date == "":
            date = datestr

        if is_high_speed:
            PRESERVE_URL = f"{self.address}/api/v1/preserveservice/preserve"
        else:
            PRESERVE_URL = f"{self.address}/api/v1/preserveotherservice/preserveOther"

        base_preserve_payload = {
            "accountId": self.uid,
            "assurance": "0",
            "contactsId": "",
            "date": date,
            "from": start,
            "to": end,
            "tripId": ""
        }

        trip_id = random_from_list(trip_ids)
        base_preserve_payload["tripId"] = trip_id

        need_food = random_boolean()
        if need_food:
            logger.info("need food")
            food_result = self.query_food()
            food_dict = random_from_list(food_result)
            base_preserve_payload.update(food_dict)
        else:
            logger.info("not need food")
            base_preserve_payload["foodType"] = "0"

        need_assurance = random_boolean()
        if need_assurance:
            base_preserve_payload["assurance"] = 1

        contacts_result = self.query_contacts()
        contacts_id = random_from_list(contacts_result)
        base_preserve_payload["contactsId"] = contacts_id

        # 高铁 2-3
        seat_type = random_from_list(["2", "3"])
        base_preserve_payload["seatType"] = seat_type

        need_consign = random_boolean()
        if need_consign:
            consign = {
                "consigneeName": random_str(),
                "consigneePhone": random_phone(),
                "consigneeWeight": random.randint(1, 10),
                "handleDate": date
            }
            base_preserve_payload.update(consign)

        logger.info(
            f"choices: preserve_high: {is_high_speed} need_food:{need_food}  need_consign: {need_consign}  need_assurance:{need_assurance}")

        res = self.session.post(url=PRESERVE_URL,
                                headers=headers,
                                json=base_preserve_payload)

        if res.status_code == 200 and res.json()["data"] == "Success":
            logger.info(f"preserve trip {trip_id} success")
        else:
            logger.error(
                f"preserve failed, code: {res.status_code}, {res.text}")
        return
