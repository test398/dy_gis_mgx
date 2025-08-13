"""
大模型基类

定义所有大模型的统一接口和通用实现
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
import time
import logging
import json
from dataclasses import dataclass
from models.prompt import system_prompt, user_prompt
from core.data_types import EvaluationResponse, GISData, TreatmentResponse


@dataclass
class ModelPricing:
    """模型定价信息"""
    input_price_per_1m_tokens: float    # 输入价格 (美元/1M tokens)
    output_price_per_1m_tokens: float   # 输出价格 (美元/1M tokens)
    currency: str = "USD"
    model_name: str = ""

    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """计算调用成本"""
        input_cost = input_tokens * self.input_price_per_1m_tokens / 1_000_000
        output_cost = output_tokens * self.output_price_per_1m_tokens / 1_000_000
        return input_cost + output_cost


class BaseModel(ABC):
    """所有大模型的基类"""
    
    def __init__(self, api_key: str, model_name: str, **kwargs):
        """
        初始化基础模型
        
        Args:
            api_key: API密钥
            model_name: 模型名称
            **kwargs: 其他配置参数
        """
        self.api_key = api_key
        self.model_name = model_name
        self.max_retries = kwargs.get('max_retries', 3)
        self.timeout = kwargs.get('timeout', 300)
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
        
        # 子类可重写的配置
        self.base_url = kwargs.get('base_url', None)
        self.extra_headers = kwargs.get('extra_headers', {})
        
        # 设置日志格式
        # if not self.logger.handlers:
        #     handler = logging.StreamHandler()
        #     formatter = logging.Formatter(
        #         '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        #     )
        #     handler.setFormatter(formatter)
        #     self.logger.addHandler(handler)
        #     self.logger.setLevel(logging.INFO)
    
    @abstractmethod
    def _make_api_call(self, messages: List[dict], **kwargs) -> Dict[str, Any]:
        """
        实际的API调用实现 (子类必须实现)
        
        Args:
            messages: 消息列表
            **kwargs: API调用参数
            
        Returns:
            dict: {"response": str, "usage": dict, "raw_response": dict}
        """
        pass
    
    @abstractmethod
    def get_pricing(self) -> ModelPricing:
        """获取模型定价信息 (子类必须实现)"""
        pass
    
    @abstractmethod
    def _add_image_to_messages(self, messages: List[dict], image_path: str) -> List[dict]:
        """添加图片到消息 (不同模型实现不同)"""
        pass
    
    def beautify(self, gis_data: dict, prompt: str, image_path: Optional[str] = None) -> TreatmentResponse:
        """
        美化治理接口 (通用实现)
        
        Args:
            gis_data: GIS结构化数据
            prompt: 治理提示词
            image_path: 可选的图片路径
            
        Returns:
            dict: 治理结果
        """
        self.logger.info(f"开始治理处理，输入设备数量: {len(gis_data.get('devices', []))}")
        
        # 构建消息
        messages = self._build_beautify_messages(gis_data, prompt)
        
        # 添加图片（如果有）
        if image_path:
            messages = self._add_image_to_messages(messages, image_path)
        
        # 调用API
        start_time = time.perf_counter()
        try:
            api_result = self._make_api_call_with_retry(messages)
            processing_time = time.perf_counter() - start_time
            
            # 解析治理结果
            treated_gis_data = self._parse_treatment_response(api_result["response"])
            
            self.logger.info(f"治理完成，处理时间: {processing_time:.2f}s")
            
            return TreatmentResponse(
                treated_gis_data=treated_gis_data,
                input_tokens=api_result.get("usage", {}).get("input_tokens", 0),
                output_tokens=api_result.get("usage", {}).get("output_tokens", 0),
                processing_time=processing_time,
                raw_response=api_result["response"],
                confidence_score=self._extract_confidence(api_result["response"])
            )
            
        except Exception as e:
            self.logger.error(f"治理处理失败: {e}")
            raise
    
    def evaluate(self, original_gis_data: dict, treated_gis_data: dict) -> EvaluationResponse:
        """
        美观性评分接口 - 使用单项评分流程
        
        Args:
            original_gis_data: 原始GIS数据
            treated_gis_data: 治理后的GIS数据
            
        Returns:
            EvaluationResponse: 评分结果
        """
        self.logger.info("开始美观性评分 - 使用单项评分流程")
        
        try:
            # 导入单项评分流程
            from core.evaluation import evaluation_pipeline
            
            # 对治理后的数据进行单项评分
            evaluation_result = evaluation_pipeline({'gis_data': treated_gis_data})
            
            # 提取评分结果
            beauty_score = evaluation_result.get('total_score', 0.0)
            
            # 构建维度评分
            dimension_scores = {
                'overhead_lines': evaluation_result.get('overhead', {}).get('total_score', 0.0),
                'cable_lines': evaluation_result.get('cable_lines', {}).get('total_score', 0.0),
                'branch_boxes': evaluation_result.get('branch_boxes', {}).get('total_score', 0.0),
                'access_points': evaluation_result.get('access_points', {}).get('total_score', 0.0),
                'meter_boxes': evaluation_result.get('meter_boxes', {}).get('total_score', 0.0)
            }
            
            # 构建改善分析
            improvement_analysis = {
                'evaluation_level': evaluation_result.get('level', ''),
                'veto_applied': evaluation_result.get('veto', False),
                'veto_reasons': evaluation_result.get('veto_reasons', []),
                'details': evaluation_result.get('details', {})
            }
            
            # 构建评分理由
            reasoning_parts = evaluation_result.get('basis', [])
            reasoning = '\n'.join(reasoning_parts) if reasoning_parts else f"单项评分完成，总分: {beauty_score}分，等级: {evaluation_result.get('level', '')}。"
            
            self.logger.info(f"单项评分完成，总分: {beauty_score}分，等级: {evaluation_result.get('level', '')}")
            
            return EvaluationResponse(
                beauty_score=beauty_score,
                dimension_scores=dimension_scores,
                improvement_analysis=improvement_analysis,
                reasoning=reasoning,
                input_tokens=0,  # 单项评分不消耗API tokens
                output_tokens=0
            )
            
        except Exception as e:
            self.logger.error(f"单项评分处理失败: {e}")
            raise
    
    def _make_api_call_with_retry(self, messages: List[dict]) -> Dict[str, Any]:
        """带重试的API调用"""
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                self.logger.debug(f"API调用尝试 {attempt + 1}/{self.max_retries}")
                return self._make_api_call(messages)
                
            except Exception as e:
                last_exception = e
                self.logger.warning(f"API调用失败 (尝试 {attempt + 1}/{self.max_retries}): {e}")
                
                if attempt < self.max_retries - 1:
                    # 指数退避
                    wait_time = 2 ** attempt
                    self.logger.info(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
        
        self.logger.error(f"API调用最终失败，已尝试 {self.max_retries} 次")
        raise last_exception
    
    def _build_beautify_messages(self, gis_data: dict, prompt: str) -> List[dict]:
        """构建治理请求的消息"""
        # 将GIS数据序列化为JSON字符串
        gis_json = json.dumps(gis_data, ensure_ascii=False, indent=2)
        
        user_message = f"""
            {prompt}

            ## 当前台区GIS数据:
            ```json
            {gis_json}
            ```

            请基于以上数据进行美观性治理，返回JSON格式的优化后数据, 不要包含任何其他内容和代码内容。
            返回格式应包含: devices, buildings, roads, rivers, boundaries, metadata 字段。
            """
        
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
    
    def _build_evaluate_messages(self, original_gis_data: dict, treated_gis_data: dict) -> List[dict]:
        """构建评分请求的消息"""
        original_json = json.dumps(original_gis_data, ensure_ascii=False, indent=2)
        treated_json = json.dumps(treated_gis_data, ensure_ascii=False, indent=2)
        
        user_message = f"""
            请对台区治理效果进行美观性评分 (0-100分)。

            ## 治理前数据:
            ```json
            {original_json}
            ```

            ## 治理后数据:
            ```json
            {treated_json}
            ```

            请从以下维度评分并返回JSON格式:
            1. layout (布局合理性) - 设备排列是否整齐有序
            2. spacing (设备间距) - 设备间距是否合适
            3. harmony (视觉和谐性) - 整体视觉效果是否和谐
            4. accessibility (可达性) - 设备是否易于维护访问

            返回格式示例:
            {{
                "beauty_score": 85.5,
                "dimension_scores": {{
                    "layout": 88,
                    "spacing": 85,
                    "harmony": 87,
                    "accessibility": 82
                }},
                "improvement_analysis": {{
                    "devices_moved": 3,
                    "spacing_improved": true,
                    "layout_optimized": true
                }},
                "reasoning": "治理后设备布局更加整齐，间距更加合理..."
            }}
            """
        
        return [
            {"role": "system", "content": "你是台区美观性评价专家，能客观评估设备布局的美观性和合理性。"},
            {"role": "user", "content": user_message}
        ]
    
    def _parse_treatment_response(self, response: str) -> GISData:
        """解析治理响应为GIS数据"""
        try:
            # 尝试提取JSON部分
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start != -1 and json_end != -1:
                json_str = response[json_start:json_end]
                data = json.loads(json_str)
            else:
                # 如果没有找到JSON，尝试直接解析整个响应
                data = json.loads(response)
            
            # 确保包含必要字段
            return GISData(
                devices=data.get('devices', []),
                buildings=data.get('buildings', []),
                roads=data.get('roads', []),
                rivers=data.get('rivers', []),
                boundaries=data.get('boundaries', {}),
                metadata=data.get('metadata', {})
            )
            
        except Exception as e:
            self.logger.error(f"解析治理响应失败: {e}")
            self.logger.error(f"原始响应: {response[:500]}...")
            raise ValueError(f"无法解析治理结果: {str(e)}")
    
    def _parse_evaluation_response(self, response: str) -> Dict[str, Any]:
        """解析评分响应"""
        try:
            # 尝试提取JSON部分
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start != -1 and json_end != -1:
                json_str = response[json_start:json_end]
                data = json.loads(json_str)
            else:
                # 如果没有找到JSON，尝试直接解析整个响应
                data = json.loads(response)
            
            # 确保必要字段存在
            if 'beauty_score' not in data:
                raise ValueError("响应中缺少beauty_score字段")
            
            # 提供默认值
            data.setdefault('dimension_scores', {})
            data.setdefault('improvement_analysis', {})
            data.setdefault('reasoning', '')
            
            return data
            
        except Exception as e:
            self.logger.error(f"解析评分响应失败: {e}")
            self.logger.error(f"原始响应: {response[:500]}...")
            raise ValueError(f"无法解析评分结果: {str(e)}")
    
    def _extract_confidence(self, response: str) -> float:
        """提取置信度"""
        # 默认置信度，子类可以根据响应内容实现更复杂的置信度提取
        return 0.8
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        return {
            "model_type": self.__class__.__name__.lower().replace('model', ''),
            "model_name": self.model_name,
            "provider": getattr(self, 'provider', None)
        }
    
    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """计算调用成本"""
        pricing = self.get_pricing()
        return pricing.calculate_cost(input_tokens, output_tokens)