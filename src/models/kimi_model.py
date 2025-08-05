"""
Kimi K2模型实现

基于Kimi K2 API，适配BaseModel接口
"""

import base64
import json
from typing import List, Dict, Any
import requests

from core.data_types import GISData

from .base_model import BaseModel, ModelPricing


class KimiModel(BaseModel):
    """Kimi K2模型实现"""
    
    def __init__(self, api_key: str, model_name: str = "kimi-k2", **kwargs):
        """
        初始化Kimi K2模型
        
        Args:
            api_key: Kimi API Key
            model_name: 模型名称，默认使用Kimi K2
            **kwargs: 其他配置参数
        """
        super().__init__(api_key, model_name, **kwargs)
        
        # Kimi API配置
        self.base_url = kwargs.get('base_url', "https://kimi.moonshot.cn/api/chat")
        self.provider = "Moonshot AI"
        
        self.logger.info(f"Kimi K2模型初始化成功: {self.model_name}")
    
    def _make_api_call(self, messages: List[dict], **kwargs) -> Dict[str, Any]:
        """
        Kimi K2 API调用实现
        
        Args:
            messages: 消息列表
            **kwargs: API调用参数
            
        Returns:
            Dict[str, Any]: {"response": str, "usage": dict, "raw_response": dict}
        """
        try:
            # 准备请求头
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # 准备请求数据
            data = {
                "model": self.model_name,
                "messages": messages,
                "max_tokens": kwargs.get('max_tokens', 4000),
                "temperature": kwargs.get('temperature', 0.3),
                "top_p": kwargs.get('top_p', 0.8),
                "stream": False
            }
            
            self.logger.debug(f"调用Kimi K2 API，模型: {self.model_name}")
            
            # 调用API
            response = requests.post(
                self.base_url,
                headers=headers,
                json=data,
                timeout=self.timeout
            )
            response.raise_for_status()
            result = response.json()
            
            if result.get("error"):
                raise Exception(f"Kimi K2 API错误: {result.get('error', {}).get('message', 'Unknown error')}")
            
            # 提取响应信息
            choices = result.get("choices", [])
            if not choices:
                raise Exception("API响应中没有choices字段")
            
            content = choices[0].get("message", {}).get("content", "")
            
            usage_data = result.get("usage", {})
            usage = {
                "input_tokens": usage_data.get("prompt_tokens", 0),
                "output_tokens": usage_data.get("completion_tokens", 0),
                "total_tokens": usage_data.get("total_tokens", 0)
            }
            
            self.logger.info(f"Kimi K2 API调用成功，输入tokens: {usage['input_tokens']}, 输出tokens: {usage['output_tokens']}")
            
            return {
                "response": content,
                "usage": usage,
                "raw_response": result
            }
            
        except Exception as e:
            self.logger.error(f"Kimi K2 API调用失败: {e}")
            raise
    
    def _add_image_to_messages(self, messages: List[dict], image_path: str) -> List[dict]:
        """
        Kimi K2的图片添加方式
        
        Args:
            messages: 原始消息列表
            image_path: 图片文件路径
            
        Returns:
            List[dict]: 包含图片的消息列表
        """
        try:
            # 读取并编码图片
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Kimi K2使用OpenAI兼容格式
            if messages and messages[-1]["role"] == "user":
                # 将文本内容转换为多模态格式
                text_content = messages[-1]["content"]
                messages[-1]["content"] = [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    },
                    {
                        "type": "text",
                        "text": text_content
                    }
                ]
            
            self.logger.debug(f"成功添加图片到消息: {image_path}")
            return messages
            
        except Exception as e:
            self.logger.error(f"添加图片失败: {e}")
            # 如果图片添加失败，返回原始消息
            return messages
    
    def get_pricing(self) -> ModelPricing:
        """
        Kimi K2定价信息
        
        Returns:
            ModelPricing: 定价信息
        """
        # 基于2025年1月的Kimi K2定价（按美元计算）
        return ModelPricing(
            input_price_per_1m_tokens=0.25,  # 约合美元价格
            output_price_per_1m_tokens=0.75, # 约合美元价格
            currency="USD",
            model_name=self.model_name
        )
    
    def _parse_treatment_response(self, response: str) -> dict:
        """
        解析Kimi K2的治理响应
        
        Args:
            response: Kimi K2模型的原始响应
            
        Returns:
            dict: 解析后的GIS数据
        """
        try:
            self.logger.debug("开始解析Kimi K2治理响应")
            
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
            processed_devices = data.get('devices', [])
            for device in processed_devices:
                if isinstance(device, dict) and 'points' in device:
                    # 计算设备中心点
                    points = device['points']
                    if points and len(points) > 0:
                        x_coords = [p[0] for p in points if len(p) >= 2]
                        y_coords = [p[1] for p in points if len(p) >= 2]
                        
                        if x_coords and y_coords:
                            device['x'] = sum(x_coords) / len(x_coords)
                            device['y'] = sum(y_coords) / len(y_coords)
            
            self.logger.info(f"成功解析 {len(processed_devices)} 个设备")
            
            # 创建GIS数据对象
            return GISData(
                devices=processed_devices,
                buildings=data.get('buildings', []),
                roads=data.get('roads', []),
                rivers=data.get('rivers', []),
                boundaries=data.get('boundaries', {}),
                metadata={
                    'source': 'kimi_treatment',
                    'model': self.model_name,
                    'device_count': len(processed_devices)
                }
            )
            
        except Exception as e:
            self.logger.error(f"解析Kimi K2治理响应失败: {e}")
            self.logger.error(f"原始响应: {response[:500]}...")
            raise ValueError(f"无法解析Kimi K2治理结果: {str(e)}")
    
    def _parse_evaluation_response(self, response: str) -> Dict[str, Any]:
        """
        解析Kimi K2的评分响应
        
        Args:
            response: Kimi K2模型的原始响应
            
        Returns:
            Dict[str, Any]: 解析后的评分数据
        """
        try:
            self.logger.debug("开始解析Kimi K2评分响应")
            
            # 尝试提取JSON部分
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start != -1 and json_end != -1:
                json_str = response[json_start:json_end]
                data = json.loads(json_str)
            else:
                # 如果没有JSON格式，尝试从文本中提取分数
                import re
                score_match = re.search(r'(\d+(?:\.\d+)?)', response)
                if score_match:
                    score = float(score_match.group(1))
                    data = {
                        "beauty_score": score,
                        "dimension_scores": {},
                        "improvement_analysis": {},
                        "reasoning": response
                    }
                else:
                    raise ValueError("无法从响应中提取评分信息")
            
            # 确保必要字段存在
            if 'beauty_score' not in data:
                raise ValueError("响应中缺少beauty_score字段")
            
            # 提供默认值
            data.setdefault('dimension_scores', {})
            data.setdefault('improvement_analysis', {})
            data.setdefault('reasoning', response)
            
            self.logger.info(f"成功解析评分: {data['beauty_score']}")
            
            return data
            
        except Exception as e:
            self.logger.error(f"解析Kimi K2评分响应失败: {e}")
            self.logger.error(f"原始响应: {response[:500]}...")
            raise ValueError(f"无法解析Kimi K2评分结果: {str(e)}")
    
    def _extract_confidence(self, response: str) -> float:
        """
        从Kimi K2响应中提取置信度
        
        Args:
            response: 原始响应文本
            
        Returns:
            float: 置信度分数 (0-1)
        """
        # Kimi K2通常不直接提供置信度，这里基于响应质量估算
        try:
            # 如果响应包含有效的JSON格式，置信度较高
            if '[' in response and ']' in response:
                return 0.9
            elif '{' in response and '}' in response:
                return 0.8
            else:
                return 0.6
        except:
            return 0.5
    
    def simulate_beautification(self, gis_data: dict) -> Dict[str, Any]:
        """
        模拟美化治理过程（用于演示）
        """
        self.logger.info(f"模拟调用Kimi K2 API...")
        self.logger.info(f"输入数据: {len(gis_data.get('devices', []))}个设备")
        
        import time
        time.sleep(0.1)  # 模拟网络延迟
        
        # 模拟治理后的数据
        treated_devices = []
        for device in gis_data.get('devices', []):
            optimized_device = device.copy()
            optimized_device['x'] += 12  # 模拟位置调整
            optimized_device['y'] += 7
            treated_devices.append(optimized_device)
        
        return {
            "devices": treated_devices,
            "buildings": gis_data.get('buildings', []),
            "roads": gis_data.get('roads', []),
            "rivers": gis_data.get('rivers', []),
            "boundaries": gis_data.get('boundaries', {}),
            "metadata": {**gis_data.get('metadata', {}), "treated": True}
        }
    
    def simulate_evaluation(self, original_gis_data: dict, treated_gis_data: dict) -> Dict[str, Any]:
        """
        模拟美观性评分（用于演示）
        """
        self.logger.info("模拟调用Kimi K2进行美观性评分...")
        
        import time
        time.sleep(0.1)
        
        return {
            "beauty_score": 89.8,
            "dimension_scores": {
                "layout": 91,      # 布局合理性
                "spacing": 88,     # 设备间距
                "harmony": 90,     # 视觉和谐性
                "accessibility": 89 # 可达性
            },
            "improvement_analysis": {
                "devices_moved": 5,
                "spacing_improved": True,
                "layout_optimized": True
            },
            "reasoning": "Kimi K2治理后设备布局更加优化，间距更加合理，整体美观性得到显著提升。"
        } 