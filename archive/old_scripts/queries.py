from typing import List
import requests
import logging
import time
import random
from utils import *
from config import BASE_URL, USERNAME, PASSWORD, DEFAULT_DATE, PLACE_PAIRS

logger = logging.getLogger("auto-queries")
datestr = time.strftime("%Y-%m-%d", time.localtime())


class Query:
    """
    train-ticket query class
    """

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
        from utils import generate_new_cookies
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

        # 按照atomic_queries.py的数据格式构造
        data = '{"username":"' + username + '","password":"' + password + '"}'

        try:
            # 直接发送登录请求，不获取验证码
            logger.info(f"正在登录: {url}, 用户名: {username}")
            logger.debug(f"请求数据: {data}")
            logger.debug(f"使用cookies: {cookies}")
            
            r = self.session.post(url=url, headers=headers,
                                  cookies=cookies, data=data, verify=False)

            if r.status_code != 200:
                logger.error(f"登录请求失败，状态码: {r.status_code}")
                logger.error(f"错误内容: {r.text}")
                return False
                
            # 检查返回的JSON内容
            response_json = r.json()
            logger.debug(f"登录响应: {response_json}")
            
            if not response_json:
                logger.error("登录响应不是有效的JSON格式")
                return False
                
            # 检查响应结构
            if "data" not in response_json or response_json["data"] is None:
                logger.error("登录响应中没有data字段或data为空")
                logger.error(f"完整响应: {response_json}")
                return False
                
            data = response_json.get("data")
            user_id = data.get("userId")
            token = data.get("token")
            
            if not user_id or not token:
                logger.error(f"未找到用户ID或令牌: userId={user_id}, token={token}")
                return False
                
            self.uid = user_id
            self.token = token
            self.session.headers.update(
                {"Authorization": f"Bearer {self.token}"}
            )
            logger.info(f"登录成功, 用户ID: {self.uid}")
            return True
        except requests.exceptions.ConnectionError as e:
            logger.error(f"连接服务器失败: {e}")
            return False
        except requests.exceptions.Timeout as e:
            logger.error(f"请求超时: {e}")
            return False
        except Exception as e:
            logger.error(f"登录时发生未知错误: {e}")
            return False

    def admin_login(self):
        return self.login

    def query_high_speed_ticket(self, place_pair: tuple = None, time: str = None, headers: dict = {}) -> List[str]:
        """
        查询高铁票
        
        Args:
            place_pair: 使用的开始结束组对，如果为None则随机从配置中选择
            time: 出发日期，如果为None则使用配置中的日期
            headers: 请求头
            
        Returns:
            TripId列表
        """
        url = f"{self.address}/api/v1/travelservice/trips/left"
        
        # 使用配置中的地点对，如未提供
        if place_pair is None:
            place_pair = random_from_list(PLACE_PAIRS['high_speed'])
            
        # 使用配置中的日期，如未提供
        if time is None:
            time = DEFAULT_DATE

        payload = {
            "departureTime": time,
            "startingPlace": place_pair[0],
            "endPlace": place_pair[1],
        }

        response = self.session.post(url=url, headers=headers, json=payload)

        if response.status_code != 200 or response.json().get("data") is None:
            logger.warning(
                f"请求 {url} 失败。响应数据: {response.text}")
            return None

        data = response.json().get("data")  # type: dict

        trip_ids = []
        for d in data:
            trip_id = d.get("tripId").get("type") + \
                d.get("tripId").get("number")
            trip_ids.append(trip_id)
        return trip_ids

    def query_normal_ticket(self, place_pair: tuple = None, time: str = None, headers: dict = {}) -> List[str]:
        """
        查询普通列车票
        
        Args:
            place_pair: 使用的开始结束组对，如果为None则随机从配置中选择
            time: 出发日期，如果为None则使用配置中的日期
            headers: 请求头
            
        Returns:
            TripId列表
        """
        url = f"{self.address}/api/v1/travel2service/trips/left"
        
        # 使用配置中的地点对，如未提供
        if place_pair is None:
            place_pair = random_from_list(PLACE_PAIRS['normal'])
            
        # 使用配置中的日期，如未提供
        if time is None:
            time = DEFAULT_DATE

        payload = {
            "departureTime": time,
            "startingPlace": place_pair[0],
            "endPlace": place_pair[1],
        }

        response = self.session.post(url=url, headers=headers, json=payload)

        if response.status_code != 200 or response.json().get("data") is None:
            logger.warning(
                f"请求 {url} 失败。响应数据: {response.text}")
            return None

        data = response.json().get("data")  # type: dict

        trip_ids = []
        for d in data:
            trip_id = d.get("tripId").get("type") + \
                d.get("tripId").get("number")
            trip_ids.append(trip_id)
        return trip_ids

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

    def query_orders(self, types: tuple = tuple([0, 1]), query_other: bool = False, headers: dict = {}) -> List[tuple]:
        """
        返回(orderId, tripId) triple list for inside_pay_service
        :param headers:
        :return:
        """
        url = ""

        if query_other:
            url = f"{self.address}/api/v1/orderOtherService/orderOther/refresh"
        else:
            url = f"{self.address}/api/v1/orderservice/order/refresh"

        payload = {
            "loginId": self.uid,
        }

        response = self.session.post(url=url, headers=headers, json=payload)
        if response.status_code != 200 or response.json().get("data") is None:
            logger.warning(
                f"query orders failed, response data is {response.text}")
            return None

        data = response.json().get("data")
        pairs = []
        for d in data:
            # status = 0: not paid
            # status=1 paid not collect
            # status=2 collected
            if d.get("status") in types:
                order_id = d.get("id")
                trip_id = d.get("trainNumber")
                pairs.append((order_id, trip_id))

        logger.info(f"queried {len(pairs)} orders")

        return pairs

    def query_other_orders(self, types: tuple = tuple([0, 1]), headers: dict = {}) -> List[tuple]:
        return self.query_orders(types, True, headers)

    def query_orders_all_info(self, query_other: bool = False, headers: dict = {}) -> List[dict]:
        """
        返回(orderId, tripId) triple list for consign service
        :param headers:
        :return:
        """

        if query_other:
            url = f"{self.address}/api/v1/orderOtherService/orderOther/refresh"
        else:
            url = f"{self.address}/api/v1/orderservice/order/refresh"

        payload = {
            "loginId": self.uid,
        }

        response = self.session.post(url=url, headers=headers, json=payload)
        if response.status_code != 200 or response.json().get("data") is None:
            logger.warning(
                f"query orders failed, response data is {response.text}")
            return None

        data = response.json().get("data")
        list = []
        for d in data:
            result = {}
            result["accountId"] = d.get("accountId")
            result["targetDate"] = time.strftime(
                '%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            result["orderId"] = d.get("id")
            result["from"] = d.get("from")
            result["to"] = d.get("to")
            list.append(result)

        logger.info(f"queried {len(list)} orders")

        return list

    def put_consign(self, result, headers: dict = {}) -> str:
        url = f"{self.address}/api/v1/consignservice/consigns"
        consignload = {
            "accountId": result["accountId"],
            "handleDate": time.strftime('%Y-%m-%d', time.localtime(time.time())),
            "targetDate": result["targetDate"],
            "from": result["from"],
            "to": result["to"],
            "orderId": result["orderId"],
            "consignee": "32",
            "phone": "12345677654",
            "weight": "32",
            "id": "",
            "isWithin": False
        }
        res = self.session.put(url=url, headers=headers,
                               json=consignload)

        order_id = result["orderId"]
        if res.status_code == 200 or res.status_code == 201:
            logger.info(f"order {order_id} put consign success")
        else:
            logger.warning(
                f"order {order_id} failed, code: {res.status_code}, text: {res.text}")
            return None

        return order_id

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

    def pay_order(self, order_id: str, trip_id: str, headers: dict = {}) -> str:
        url = f"{self.address}/api/v1/inside_pay_service/inside_payment"
        payload = {
            "orderId": order_id,
            "tripId": trip_id
        }

        res = self.session.post(url=url, headers=headers, json=payload)

        if res.status_code == 200:
            logger.info(f"order {order_id} pay success")
        else:
            logger.warning(
                f"pay order {order_id} failed, code: {res.status_code}, text: {res.text}")
            return None

        return order_id

    def cancel_order(self, order_id, headers: dict = {}):
        url = f"{self.address}/api/v1/cancelservice/cancel/{order_id}/{self.uid}"

        res = self.session.get(url=url, headers=headers)

        if res.status_code == 200:
            logger.info(f"order {order_id} cancel success")
        else:
            logger.warning(
                f"order {order_id} cancel failed, code: {res.status_code}, text: {res.text}")

        return order_id

    def collect_order(self, order_id, headers: dict = {}):
        url = f"{self.address}/api/v1/executeservice/execute/collected/{order_id}"
        res = self.session.get(url=url, headers=headers)
        if res.status_code == 200:
            logger.info(f"order {order_id} collect success")
        else:
            logger.warning(
                f"order {order_id} collect failed, code: {res.status_code}, text: {res.text}")

        return order_id

    def enter_station(self, order_id, headers: dict = {}):
        url = f"{self.address}/api/v1/executeservice/execute/execute/{order_id}"
        res = self.session.get(url=url,
                               headers=headers)
        if res.status_code == 200:
            logger.info(f"order {order_id} enter station success")
        else:
            logger.warning(
                f"order {order_id} enter station failed, code: {res.status_code}, text: {res.text}")

        return order_id

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
