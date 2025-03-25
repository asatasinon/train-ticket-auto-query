"""
场景执行器模块，负责批量执行场景
"""
import time
import random
import logging
from typing import List, Callable, Any, Dict, Tuple, Optional

# 导入核心模块
from ..core.queries import Query

logger = logging.getLogger("scenario-runner")


class ScenarioRunner:
    """场景执行器类，用于批量执行场景"""
    
    def __init__(self, query: Query):
        """
        初始化场景执行器
        
        Args:
            query: Query对象，用于执行API请求
        """
        self.query = query
        self.scenarios = []
        self.scenario_weights = {}  # 场景权重字典
    
    def add_scenario(self, scenario: Callable, weight: int = 1):
        """
        添加场景
        
        Args:
            scenario: 场景函数
            weight: 场景权重，权重越高被随机选中的概率越大
        """
        self.scenarios.append(scenario)
        self.scenario_weights[scenario.__name__] = weight
        logger.debug(f"添加场景: {scenario.__name__}，权重: {weight}")
        
    def add_scenarios(self, scenarios: List[Callable], weight: int = 1):
        """
        批量添加场景
        
        Args:
            scenarios: 场景函数列表
            weight: 所有场景的权重，权重越高被随机选中的概率越大
        """
        for scenario in scenarios:
            self.add_scenario(scenario, weight)
    
    def _select_random_scenario(self) -> Optional[Callable]:
        """
        根据权重随机选择场景
        
        Returns:
            随机选择的场景函数
        """
        if not self.scenarios:
            logger.warning("没有可执行的场景")
            return None
            
        # 如果没有设置权重，则使用平均权重
        if not self.scenario_weights:
            return random.choice(self.scenarios)
            
        # 根据权重选择场景
        total_weight = sum(self.scenario_weights.values())
        r = random.uniform(0, total_weight)
        current_weight = 0
        
        for scenario in self.scenarios:
            current_weight += self.scenario_weights.get(scenario.__name__, 1)
            if r <= current_weight:
                return scenario
                
        # 如果没有选中任何场景（浮点数误差可能导致），则返回最后一个场景
        return self.scenarios[-1]
    
    def run_random(self, count: int = 100, interval: float = 1.0) -> Tuple[int, int]:
        """
        随机执行场景
        
        Args:
            count: 执行次数
            interval: 执行间隔（秒）
            
        Returns:
            (成功次数, 失败次数)的元组
        """
        if not self.scenarios:
            logger.warning("没有可执行的场景")
            return (0, 0)
            
        start_time = time.time()
        success_count = 0
        fail_count = 0
        
        logger.info(f"开始执行随机场景，计划执行{count}次")
        
        for i in range(count):
            # 随机选择场景
            scenario = self._select_random_scenario()
            if not scenario:
                logger.error("无法选择场景，停止执行")
                break
                
            scenario_name = scenario.__name__
            
            logger.info(f"执行场景 [{i+1}/{count}]: {scenario_name}")
            
            try:
                # 执行场景
                scenario(self.query)
                success_count += 1
                logger.info(f"场景 {scenario_name} 执行成功")
            except Exception as e:
                fail_count += 1
                logger.error(f"场景 {scenario_name} 执行失败: {str(e)}")
            
            # 使用配置的执行间隔
            if i < count - 1:  # 最后一次不需要等待
                time.sleep(interval)
        
        # 统计结果
        elapsed_time = time.time() - start_time
        logger.info("=" * 50)
        logger.info(
            f"执行完毕！总计: {count}个场景, "
            f"成功: {success_count}, 失败: {fail_count}"
        )
        logger.info(
            f"总耗时: {elapsed_time:.2f}秒, "
            f"平均每个场景: {elapsed_time/count:.2f}秒"
        )
        
        return (success_count, fail_count)
    
    def run_specific(self, scenario: Callable) -> bool:
        """
        执行特定场景
        
        Args:
            scenario: 要执行的场景函数
            
        Returns:
            执行是否成功
        """
        scenario_name = scenario.__name__
        logger.info(f"执行特定场景: {scenario_name}")
        
        try:
            scenario(self.query)
            logger.info(f"场景 {scenario_name} 执行成功")
            return True
        except Exception as e:
            logger.error(f"场景 {scenario_name} 执行失败: {str(e)}")
            return False
    
    def run_all(self, interval: float = 1.0) -> Dict[str, bool]:
        """
        执行所有场景
        
        Args:
            interval: 场景间隔（秒）
            
        Returns:
            场景名到执行结果的映射字典
        """
        if not self.scenarios:
            logger.warning("没有可执行的场景")
            return {}
            
        results = {}
        total = len(self.scenarios)
        
        logger.info(f"开始执行所有场景，共{total}个")
        
        for i, scenario in enumerate(self.scenarios):
            scenario_name = scenario.__name__
            logger.info(f"执行场景 [{i+1}/{total}]: {scenario_name}")
            
            try:
                scenario(self.query)
                results[scenario_name] = True
                logger.info(f"场景 {scenario_name} 执行成功")
            except Exception as e:
                results[scenario_name] = False
                logger.error(f"场景 {scenario_name} 执行失败: {str(e)}")
            
            # 使用配置的执行间隔
            if i < total - 1:  # 最后一次不需要等待
                time.sleep(interval)
        
        # 统计结果
        success_count = sum(1 for result in results.values() if result)
        fail_count = sum(1 for result in results.values() if not result)
        
        logger.info("=" * 50)
        logger.info(
            f"所有场景执行完毕！总计: {total}个场景, "
            f"成功: {success_count}, 失败: {fail_count}"
        )
        
        return results


class ScenarioSet:
    """场景集合类，用于组织和管理相关场景"""
    
    def __init__(self, name: str):
        """
        初始化场景集合
        
        Args:
            name: 场景集合名称
        """
        self.name = name
        self.scenarios = []
        self.description = ""
    
    def set_description(self, description: str):
        """
        设置场景集合描述
        
        Args:
            description: 描述文本
        """
        self.description = description
    
    def add_scenario(self, scenario: Callable):
        """
        添加场景到集合
        
        Args:
            scenario: 场景函数
        """
        self.scenarios.append(scenario)
    
    def add_scenarios(self, scenarios: List[Callable]):
        """
        批量添加场景到集合
        
        Args:
            scenarios: 场景函数列表
        """
        self.scenarios.extend(scenarios)
    
    def get_scenarios(self) -> List[Callable]:
        """
        获取场景列表
        
        Returns:
            场景函数列表
        """
        return self.scenarios 