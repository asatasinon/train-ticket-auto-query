"""
Flask Web 应用主文件，提供压测可视化的 Web 界面和 WebSocket 通信
"""

from flask import Flask, render_template, jsonify
from flask_sock import Sock
import json
import logging
import time
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
import asyncio

# 导入场景相关模块
from ..scenarios.scenarios import (
    query_high_speed_ticket_scenario,
    query_normal_ticket_scenario,
    query_ticket_parallel_scenario,
    query_food_scenario,
    query_and_pay_ticket,
    query_and_cancel_ticket,
    query_and_consign,
    query_and_collect_ticket,
)
from ..scenarios.runners import ScenarioRunner
from ..core.queries import Query

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
sock = Sock(app)

# 存储所有可用的场景
AVAILABLE_SCENARIOS = {
    "高铁车票查询": query_high_speed_ticket_scenario,
    "普通列车查询": query_normal_ticket_scenario,
    "并行车票查询": query_ticket_parallel_scenario,
    "食品查询": query_food_scenario,
    "查询并支付订单": query_and_pay_ticket,
    "查询并取消订单": query_and_cancel_ticket,
    "查询并添加托运": query_and_consign,
    "查询并取票": query_and_collect_ticket,
}

# 创建线程安全的计数器
class ThreadSafeCounter:
    def __init__(self):
        self._value = 0
        self._lock = threading.Lock()

    def increment(self):
        with self._lock:
            self._value += 1
            return self._value

    def get(self):
        with self._lock:
            return self._value


# 存储压测结果
test_results = {
    "execution": {
        "total": 0,          # 总执行次数
        "success": 0,        # 场景执行成功次数
        "failure": 0,        # 场景执行失败次数
        "total_time": 0,     # 总执行时间
    },
    "api_response": {
        "total": 0,          # 总请求次数
        "success": 0,        # HTTP 200成功次数
        "failure": 0,        # 非HTTP 200次数
        "response_times": [], # 所有响应时间
        "min_time": 0,       # 最小响应时间
        "max_time": 0,       # 最大响应时间
        "avg_time": 0,       # 平均响应时间
        "sum_time": 0,       # 总响应时间
        "p90_time": 0,       # P90响应时间
        "p95_time": 0,       # P95响应时间
        "p99_time": 0,       # P99响应时间
        "error_details": {    # 错误详情
            "500": 0,
            "502": 0,
            "504": 0,
            "connection_refused": 0,
            "other": 0
        }
    },
    "start_time": None,
    "end_time": None,
    "qps": 0
}

# 全局消息队列
message_queue = Queue()

@app.route("/")
def index():
    """渲染主页"""
    return render_template("index.html", scenarios=AVAILABLE_SCENARIOS.keys())


@app.route("/api/scenarios")
def get_scenarios():
    """获取所有可用场景"""
    return jsonify(list(AVAILABLE_SCENARIOS.keys()))


def safe_send(ws, message_type, data):
    """
    安全发送消息的辅助函数
    Args:
        ws: WebSocket连接
        message_type: 消息类型
        data: 消息数据
    """
    try:
        if not ws.connected:
            logger.info("WebSocket 连接已关闭")
            return False
        
        # 打印原始输入数据
        logger.debug(f"准备发送消息 - 类型: {message_type}, 数据: {data}")
        
        message = {
            "type": message_type,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        }
        
        if isinstance(data, str):
            message["message"] = data
        else:
            message.update(data)
            
        # 验证消息是否可以被正确序列化
        try:
            # 先尝试序列化，检查是否有问题
            message_str = json.dumps(message, ensure_ascii=False)
            # 验证序列化后的消息是否可以被正确解析
            json.loads(message_str)  # 验证JSON格式
            
            # 打印最终发送的消息
            logger.info(f"发送WebSocket消息: {message_str}")
            
            # 将消息放入队列
            message_queue.put((ws, message_str))
            return True
            
        except json.JSONDecodeError as e:
            logger.error(f"消息序列化/验证失败: {str(e)}")
            logger.error(f"问题消息内容: {message}")
            # 发送错误消息
            error_message = {
                "type": "error",
                "message": f"服务器内部错误：消息格式异常 - {str(e)}",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            }
            error_str = json.dumps(error_message, ensure_ascii=False)
            message_queue.put((ws, error_str))
            return False
            
    except Exception as e:
        logger.error(f"发送消息失败: {str(e)}")
        logger.error(f"消息类型: {message_type}, 数据: {data}")
        return False


def message_sender():
    """消息发送线程"""
    while True:
        try:
            ws, message = message_queue.get()
            if ws and ws.connected:
                try:
                    ws.send(message)
                    time.sleep(0.05)  # 每条消息之间增加50ms延迟
                except Exception as e:
                    logger.error(f"发送消息失败: {str(e)}")
            message_queue.task_done()
        except Exception as e:
            logger.error(f"消息发送线程错误: {str(e)}")
            time.sleep(0.1)


# 启动消息发送线程
sender_thread = threading.Thread(target=message_sender, daemon=True)
sender_thread.start()

def execute_scenario(scenario, query, ws, counter, total_count):
    """执行单个场景"""
    try:
        # 获取场景名称（去掉 _scenario 后缀）
        scenario_name = scenario.__name__.replace('_scenario', '')
        
        # 发送场景开始执行的消息
        if not safe_send(ws, "stage", f"开始执行场景: {scenario_name}"):
            return

        start_time = time.time()
        try:
            # 执行场景
            result = scenario(query)
            response_time = time.time() - start_time
            
            # 检查是否有错误响应
            error_response = None
            if hasattr(result, 'error_response'):
                error_response = result.error_response
            
            # 获取状态码
            if error_response and '502' in error_response:
                status_code = 502
            elif error_response and '500' in error_response:
                status_code = 500
            elif error_response and '504' in error_response:
                status_code = 504
            else:
                status_code = getattr(result, 'status_code', 200)  # 默认200
            
            # 更新API响应统计
            test_results["api_response"]["total"] += 1
            test_results["api_response"]["response_times"].append(response_time)
            
            if status_code == 200:
                test_results["api_response"]["success"] += 1
                test_results["execution"]["success"] += 1
                # 发送成功消息
                safe_send(ws, "log", {
                    "message": f"场景 {scenario_name} 执行成功",
                    "response_time": f"{response_time:.3f}秒",
                    "status_code": status_code
                })
            else:
                test_results["api_response"]["failure"] += 1
                test_results["execution"]["failure"] += 1
                # 更新错误统计
                error_type = str(status_code)
                if error_type in ["500", "502", "504"]:
                    test_results["api_response"]["error_details"][error_type] += 1
                else:
                    test_results["api_response"]["error_details"]["other"] += 1
                # 发送API错误消息
                safe_send(ws, "api_error", {
                    "message": f"接口返回错误状态码: {status_code}",
                    "response_time": f"{response_time:.3f}秒",
                    "scenario": scenario_name,
                    "error": error_response if error_response else "未知错误"
                })
                
        except Exception as e:
            # 场景执行失败
            test_results["execution"]["failure"] += 1
            error_message = str(e)
            response_time = time.time() - start_time
            
            # 更新API响应统计
            test_results["api_response"]["total"] += 1
            test_results["api_response"]["failure"] += 1
            test_results["api_response"]["response_times"].append(response_time)
            
            # 判断错误类型
            if "Connection refused" in error_message:
                test_results["api_response"]["error_details"]["connection_refused"] += 1
            elif "502" in error_message:
                test_results["api_response"]["error_details"]["502"] += 1
            elif "500" in error_message:
                test_results["api_response"]["error_details"]["500"] += 1
            elif "504" in error_message:
                test_results["api_response"]["error_details"]["504"] += 1
            else:
                test_results["api_response"]["error_details"]["other"] += 1
            
            # 发送错误消息
            safe_send(ws, "error", {
                "message": f"场景执行失败: {error_message}",
                "response_time": f"{response_time:.3f}秒",
                "scenario": scenario_name
            })

        # 更新执行计数
        test_results["execution"]["total"] += 1

        # 更新进度
        current_count = counter.increment()
        progress = min((current_count / total_count) * 100, 100)
        safe_send(ws, "progress", {
            "progress": progress,
            "current": min(current_count, total_count),
            "total": total_count,
            "execution": test_results["execution"],
            "api_response": {
                "total": test_results["api_response"]["total"],
                "success": test_results["api_response"]["success"],
                "failure": test_results["api_response"]["failure"],
                "error_details": test_results["api_response"]["error_details"]
            }
        })

    except Exception as e:
        logger.error(f"执行场景时发生异常: {str(e)}")
        safe_send(ws, "error", f"执行场景时发生异常: {str(e)}")


@sock.route("/ws")
def ws(ws):
    """WebSocket 连接处理"""
    def safe_receive(timeout=None):
        """安全接收消息"""
        try:
            message = ws.receive(timeout=timeout)
            if not message:
                logger.warning("收到空消息")
                return None
            return json.loads(message)
        except json.JSONDecodeError as e:
            logger.error(f"JSON 解析错误: {str(e)}")
            return None
        except Exception as e:
            if "not connected" in str(e).lower():
                logger.info("WebSocket 连接已关闭")
            else:
                logger.error(f"接收消息失败: {str(e)}")
            return None

    try:
        # 发送初始化阶段信息
        if not safe_send(ws, "stage", "正在进行压测，等待任务初始化..."):
            return

        # 接收初始配置
        config = safe_receive()
        if not config:
            logger.error("无法解析配置信息")
            return
        logger.info(f"收到压测配置: {config}")

        # 初始化场景执行器
        query = Query()
        runner = ScenarioRunner(query)

        # 添加选中的场景
        selected_scenarios = config.get("scenarios", [])
        safe_send(ws, "stage", "正在初始化测试场景...")

        for scenario_name in selected_scenarios:
            if scenario_name in AVAILABLE_SCENARIOS:
                runner.add_scenario(AVAILABLE_SCENARIOS[scenario_name])
                safe_send(ws, "stage", f"场景 {scenario_name} 已加载")

        # 重置测试结果
        test_results.update(
            {
                "execution": {
                    "total": 0,
                    "success": 0,
                    "failure": 0,
                    "total_time": 0,
                },
                "api_response": {
                    "total": 0,
                    "success": 0,
                    "failure": 0,
                    "response_times": [],
                    "min_time": 0,
                    "max_time": 0,
                    "avg_time": 0,
                    "sum_time": 0,
                    "p90_time": 0,
                    "p95_time": 0,
                    "p99_time": 0,
                    "error_details": {
                        "500": 0,
                        "502": 0,
                        "504": 0,
                        "connection_refused": 0,
                        "other": 0
                    }
                },
                "start_time": datetime.now(),
                "end_time": None,
                "qps": 0
            }
        )

        # 获取配置参数
        total_count = config.get("total_count", 100)  # 默认改为100次
        interval = config.get("interval", 0.1)
        concurrency = config.get("concurrency", 100)  # 默认改为100并发

        safe_send(ws, "stage", f"开始执行压测，并发数: {concurrency}，总请求数: {total_count}")

        # 创建线程安全的计数器
        counter = ThreadSafeCounter()

        # 创建线程池，设置最大并发数为100
        with ThreadPoolExecutor(max_workers=min(concurrency, 100)) as executor:
            # 提交所有任务
            futures = []
            for _ in range(total_count):
                scenario = runner._select_random_scenario()
                if scenario:
                    future = executor.submit(
                        execute_scenario,
                        scenario,
                        query,
                        ws,
                        counter,
                        total_count,
                    )
                    futures.append(future)
                    time.sleep(interval / concurrency)  # 根据并发数调整间隔

            # 等待所有任务完成
            safe_send(ws, "stage", "等待所有任务完成...")

            for future in futures:
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"任务执行失败: {str(e)}")

        safe_send(ws, "stage", "所有任务执行完成，正在计算统计结果...")

        # 计算最终统计结果
        test_results["end_time"] = datetime.now()
        total_time = (test_results["end_time"] - test_results["start_time"]).total_seconds()
        test_results["execution"]["total_time"] = total_time
        
        # 计算API响应时间统计
        response_times = test_results["api_response"]["response_times"]
        if response_times:
            response_times.sort()
            test_results["api_response"].update({
                "min_time": min(response_times),
                "max_time": max(response_times),
                "avg_time": sum(response_times) / len(response_times),
                "sum_time": sum(response_times),
                "p90_time": response_times[int(len(response_times) * 0.9)],
                "p95_time": response_times[int(len(response_times) * 0.95)],
                "p99_time": response_times[int(len(response_times) * 0.99)]
            })
        
        test_results["qps"] = test_results["api_response"]["total"] / total_time if total_time > 0 else 0

        # 发送完成消息和最终结果
        final_results = {
            "results": {
                "execution": test_results["execution"],
                "api_response": {
                    k: v for k, v in test_results["api_response"].items()
                    if k != "response_times"  # 不发送原始响应时间数组
                },
                "qps": test_results["qps"]
            }
        }
        
        # 打印最终结果
        logger.info("准备发送最终结果:")
        logger.info(json.dumps(final_results, ensure_ascii=False, indent=2))
        
        safe_send(ws, "complete", final_results)

        # 等待前端确认接收完成
        try:
            confirmation = safe_receive(timeout=5.0)
            if confirmation and confirmation.get("type") == "complete_confirmed":
                logger.info("前端确认接收完成")
            else:
                logger.warning("收到无效的确认消息")
        except Exception as e:
            logger.warning(f"等待前端确认超时: {str(e)}")

    except Exception as e:
        logger.error(f"WebSocket 处理发生错误: {str(e)}")
        try:
            safe_send(ws, "error", f"压测执行失败: {str(e)}")
        except Exception:
            pass  # 忽略发送错误消息时的异常


if __name__ == "__main__":
    # 使用 Flask 开发服务器
    app.run(host="0.0.0.0", port=5001, debug=True)
