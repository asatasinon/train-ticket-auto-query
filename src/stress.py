#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Train-Ticket 压测工具

这是一个用于压测Train-Ticket系统的工具，可以并发执行指定场景。
使用方法：
    python -m src.stress  # 使用默认配置执行压测
    python -m src.stress --scenario high_speed  # 指定场景进行压测
    python -m src.stress --concurrent 20  # 指定并发数为20
    python -m src.stress --count 200  # 指定总请求数为200
    python -m src.stress --help  # 显示帮助信息

注意: 直接运行此文件时，需要确保项目根目录在Python路径中，
否则应该使用"python -m src.stress"方式运行。
"""

import argparse
import logging
import sys
import time
import threading
import queue
import statistics
from typing import Dict, Any, Callable
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径，以便于直接运行此文件
if __name__ == "__main__":
    # 获取当前文件所在目录的父目录（即项目根目录）
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))

# 导入项目内部模块
from src.utils.config import (
    setup_logging, check_config, 
    STRESS_CONCURRENT, STRESS_COUNT, STRESS_SCENARIO,
    STRESS_TIMEOUT, STRESS_INTERVAL, STRESS_ERROR_RATE_THRESHOLD
)
from src.core.queries import Query
from src.scenarios.scenarios import (
    query_high_speed_ticket_scenario,
    query_normal_ticket_scenario,
    query_food_scenario,
    query_ticket_parallel_scenario,
    query_and_pay_ticket,
    query_and_cancel_ticket,
    query_and_consign,
    query_and_book_ticket_scenario,
    query_and_rebook_ticket_scenario
)

# 场景映射字典，用于命令行参数
SCENARIO_MAP = {
    "high_speed": query_high_speed_ticket_scenario,
    "normal": query_normal_ticket_scenario,
    "food": query_food_scenario,
    "parallel": query_ticket_parallel_scenario,
    "pay": query_and_pay_ticket,
    "cancel": query_and_cancel_ticket,
    "consign": query_and_consign,
    "book": query_and_book_ticket_scenario,
    "rebook": query_and_rebook_ticket_scenario
}


class StressTestResult:
    """压测结果类，用于记录和分析压测结果"""
    
    def __init__(self):
        """初始化压测结果"""
        self.success_count = 0  # 成功请求数
        self.fail_count = 0     # 失败请求数
        self.response_times = []  # 响应时间列表(毫秒)
        self.start_time = time.time()  # 压测开始时间
        self.end_time = None    # 压测结束时间
        self.errors = []        # 错误信息列表
        self.lock = threading.Lock()  # 线程锁，用于并发更新结果
    
    def add_success(self, response_time: float):
        """
        添加成功请求记录
        
        Args:
            response_time: 响应时间(秒)
        """
        with self.lock:
            self.success_count += 1
            # 转换为毫秒
            self.response_times.append(response_time * 1000)
    
    def add_failure(self, error: str):
        """
        添加失败请求记录
        
        Args:
            error: 错误信息
        """
        with self.lock:
            self.fail_count += 1
            self.errors.append(error)
    
    def complete(self):
        """标记压测完成，记录结束时间"""
        self.end_time = time.time()
    
    def total_time(self) -> float:
        """
        获取压测总时间(秒)
        
        Returns:
            压测总时间(秒)
        """
        if self.end_time is None:
            return time.time() - self.start_time
        return self.end_time - self.start_time
    
    def total_count(self) -> int:
        """
        获取总请求数
        
        Returns:
            总请求数
        """
        return self.success_count + self.fail_count
    
    def error_rate(self) -> float:
        """
        获取错误率
        
        Returns:
            错误率(0-1)
        """
        total = self.total_count()
        if total == 0:
            return 0
        return self.fail_count / total
    
    def qps(self) -> float:
        """
        获取每秒请求数(QPS)
        
        Returns:
            每秒请求数
        """
        total_time = self.total_time()
        if total_time == 0:
            return 0
        return self.total_count() / total_time
    
    def avg_response_time(self) -> float:
        """
        获取平均响应时间(毫秒)
        
        Returns:
            平均响应时间(毫秒)
        """
        if not self.response_times:
            return 0
        return sum(self.response_times) / len(self.response_times)
    
    def min_response_time(self) -> float:
        """
        获取最小响应时间(毫秒)
        
        Returns:
            最小响应时间(毫秒)
        """
        if not self.response_times:
            return 0
        return min(self.response_times)
    
    def max_response_time(self) -> float:
        """
        获取最大响应时间(毫秒)
        
        Returns:
            最大响应时间(毫秒)
        """
        if not self.response_times:
            return 0
        return max(self.response_times)
    
    def p90_response_time(self) -> float:
        """
        获取90%的响应时间(毫秒)
        
        Returns:
            90%的响应时间(毫秒)
        """
        if not self.response_times:
            return 0
        sorted_times = sorted(self.response_times)
        index = int(len(sorted_times) * 0.9)
        return sorted_times[index]
    
    def p95_response_time(self) -> float:
        """
        获取95%的响应时间(毫秒)
        
        Returns:
            95%的响应时间(毫秒)
        """
        if not self.response_times:
            return 0
        sorted_times = sorted(self.response_times)
        index = int(len(sorted_times) * 0.95)
        return sorted_times[index]
    
    def p99_response_time(self) -> float:
        """
        获取99%的响应时间(毫秒)
        
        Returns:
            99%的响应时间(毫秒)
        """
        if not self.response_times:
            return 0
        sorted_times = sorted(self.response_times)
        index = int(len(sorted_times) * 0.99)
        return sorted_times[index]
    
    def std_dev_response_time(self) -> float:
        """
        获取响应时间标准差(毫秒)
        
        Returns:
            响应时间标准差(毫秒)
        """
        if len(self.response_times) <= 1:
            return 0
        return statistics.stdev(self.response_times)
    
    def summary(self) -> Dict[str, Any]:
        """
        获取压测结果摘要
        
        Returns:
            包含压测结果摘要的字典
        """
        return {
            "total_requests": self.total_count(),
            "success_count": self.success_count,
            "fail_count": self.fail_count,
            "error_rate": self.error_rate(),
            "total_time": self.total_time(),
            "qps": self.qps(),
            "avg_response_time": self.avg_response_time(),
            "min_response_time": self.min_response_time(),
            "max_response_time": self.max_response_time(),
            "p90_response_time": self.p90_response_time(),
            "p95_response_time": self.p95_response_time(),
            "p99_response_time": self.p99_response_time(),
            "std_dev_response_time": self.std_dev_response_time(),
            "errors": self.errors[:10]  # 只返回前10个错误
        }
    
    def print_summary(self):
        """输出压测结果摘要"""
        summary = self.summary()
        
        print("\n" + "=" * 60)
        print(f"压测结果摘要 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        print(f"总请求数: {summary['total_requests']}")
        print(f"成功请求数: {summary['success_count']}")
        print(f"失败请求数: {summary['fail_count']}")
        print(f"错误率: {summary['error_rate']:.2%}")
        print(f"总耗时: {summary['total_time']:.2f}秒")
        print(f"QPS: {summary['qps']:.2f}请求/秒")
        print(f"平均响应时间: {summary['avg_response_time']:.2f}毫秒")
        print(f"最小响应时间: {summary['min_response_time']:.2f}毫秒")
        print(f"最大响应时间: {summary['max_response_time']:.2f}毫秒")
        print(f"90%响应时间: {summary['p90_response_time']:.2f}毫秒")
        print(f"95%响应时间: {summary['p95_response_time']:.2f}毫秒")
        print(f"99%响应时间: {summary['p99_response_time']:.2f}毫秒")
        print(f"响应时间标准差: {summary['std_dev_response_time']:.2f}毫秒")
        
        if summary['errors']:
            print("\n前10个错误:")
            for i, error in enumerate(summary['errors'], 1):
                print(f"{i}. {error}")
        
        print("=" * 60)


def worker(scenario_func: Callable, query: Query, result: StressTestResult):
    """
    工作线程函数，执行指定场景并记录结果
    
    Args:
        scenario_func: 要执行的场景函数
        query: Query对象，用于执行API请求
        result: StressTestResult对象，用于记录结果
    """
    start_time = time.time()
    
    try:
        # 执行场景
        scenario_func(query)
        # 记录成功
        response_time = time.time() - start_time
        result.add_success(response_time)
    except Exception as e:
        # 记录失败
        error = f"{type(e).__name__}: {str(e)}"
        result.add_failure(error)


def run_stress_test(
    scenario: str, 
    concurrent_num: int, 
    count: int,
    interval: float = 0.1,
    timeout: int = 30
) -> StressTestResult:
    """
    运行压测
    
    Args:
        scenario: 要执行的场景名称
        concurrent_num: 并发数
        count: 总请求数
        interval: 请求启动间隔(秒)
        timeout: 请求超时时间(秒)
        
    Returns:
        StressTestResult对象，包含压测结果
    """
    logger = logging.getLogger("stress-test")
    
    # 获取场景函数
    scenario_func = SCENARIO_MAP.get(scenario)
    if not scenario_func:
        logger.error(f"未知场景: {scenario}")
        sys.exit(1)
    
    logger.info(
        f"开始压测 - 场景: {scenario}, 并发数: {concurrent_num}, "
        f"总请求数: {count}"
    )
    
    # 创建压测结果对象
    result = StressTestResult()
    
    # 创建Query对象并登录
    query = Query()
    logger.info("登录中...")
    if not query.login():
        logger.error("登录失败！")
        sys.exit(1)
    
    logger.info(f"登录成功，用户ID: {query.uid}")
    logger.info("正在准备压测环境...")
    
    # 创建任务队列
    task_queue = queue.Queue()
    for i in range(count):
        task_queue.put(i)
    
    # 创建并启动工作线程
    threads = []
    stop_event = threading.Event()
    
    def thread_worker():
        while not stop_event.is_set():
            try:
                # 非阻塞方式获取任务，超时后检查是否应该停止
                _ = task_queue.get(block=True, timeout=0.1)
                worker(scenario_func, query, result)
                task_queue.task_done()
                
                # 记录进度
                completed = result.total_count()
                if completed % 10 == 0 or completed == count:
                    progress = completed / count * 100
                    logger.info(
                        f"进度: {progress:.1f}% - 完成: {completed}/{count}"
                    )
                
            except queue.Empty:
                # 队列为空，检查是否应该停止
                continue
            except Exception as e:
                logger.error(f"工作线程遇到错误: {e}")
                result.add_failure(f"Thread error: {str(e)}")
                task_queue.task_done()
    
    # 启动工作线程
    logger.info(f"正在启动{concurrent_num}个工作线程...")
    for i in range(concurrent_num):
        thread = threading.Thread(target=thread_worker)
        thread.daemon = True
        thread.start()
        threads.append(thread)
        # 按照间隔时间启动线程，避免瞬间启动所有线程
        if i < concurrent_num - 1:  # 最后一个线程不需要等待
            time.sleep(interval)
    
    try:
        # 等待所有任务完成或超时
        logger.info("所有工作线程已启动，等待任务完成...")
        task_queue.join()
        logger.info("所有任务已完成")
    except KeyboardInterrupt:
        logger.warning("收到中断信号，正在停止...")
    finally:
        # 通知所有线程停止
        stop_event.set()
        
        # 等待所有线程结束
        for thread in threads:
            thread.join(timeout=1.0)
        
        # 标记压测完成
        result.complete()
    
    return result


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="Train-Ticket 压测工具")
    
    parser.add_argument(
        "--scenario", 
        type=str, 
        choices=list(SCENARIO_MAP.keys()),
        default=STRESS_SCENARIO,
        help=f"要执行的场景，默认为{STRESS_SCENARIO}"
    )
    
    parser.add_argument(
        "--concurrent", 
        type=int, 
        default=STRESS_CONCURRENT,
        help=f"并发数，默认为{STRESS_CONCURRENT}"
    )
    
    parser.add_argument(
        "--count", 
        type=int, 
        default=STRESS_COUNT,
        help=f"总请求数，默认为{STRESS_COUNT}"
    )
    
    parser.add_argument(
        "--interval", 
        type=float, 
        default=STRESS_INTERVAL,
        help=f"请求启动间隔(秒)，默认为{STRESS_INTERVAL}"
    )
    
    parser.add_argument(
        "--timeout", 
        type=int, 
        default=STRESS_TIMEOUT,
        help=f"请求超时时间(秒)，默认为{STRESS_TIMEOUT}"
    )
    
    parser.add_argument(
        "--error-threshold", 
        type=float, 
        default=STRESS_ERROR_RATE_THRESHOLD,
        help=f"可接受的错误率阈值，默认为{STRESS_ERROR_RATE_THRESHOLD}"
    )
    
    return parser.parse_args()


def main():
    """主函数"""
    # 设置日志
    setup_logging()
    logger = logging.getLogger("stress")
    
    logger.info("=" * 50)
    logger.info("Train-Ticket 压测工具")
    logger.info("=" * 50)
    
    # 解析命令行参数
    args = parse_args()
    
    # 检查配置
    logger.info("检查配置...")
    if not check_config():
        logger.error("配置检查失败！")
        return 1
    
    # 运行压测
    try:
        result = run_stress_test(
            scenario=args.scenario,
            concurrent_num=args.concurrent,
            count=args.count,
            interval=args.interval,
            timeout=args.timeout
        )
        
        # 输出压测结果
        result.print_summary()
        
        # 检查错误率是否超过阈值
        if result.error_rate() > args.error_threshold:
            logger.error(
                f"压测失败！错误率{result.error_rate():.2%}"
                f"超过阈值{args.error_threshold:.2%}"
            )
            return 1
        
        logger.info(f"压测成功完成！QPS: {result.qps():.2f}请求/秒")
        return 0
        
    except KeyboardInterrupt:
        logger.warning("压测被用户中断")
        return 130
    except Exception as e:
        logger.error(f"压测过程中发生错误: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 