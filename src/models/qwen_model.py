"""
千问VL-Max模型实现

基于现有codespace/qwenMaxApi.py的实现，适配BaseModel接口
"""

import base64
import json
import math
from typing import List, Dict, Any, Optional
import requests

from core.data_types import GISData
from .batch_config import BatchConfig, BatchConfigPresets

from .base_model import BaseModel, ModelPricing


class QwenModel(BaseModel):
    """阿里云千问VL-Max模型实现 - 基于现有codespace/qwenMaxApi.py"""
    
    def __init__(self, api_key: str, model_name: str = "qwen-vl-max-2025-04-08", batch_config: Optional[BatchConfig] = None, **kwargs):
        """
        初始化千问模型
        
        Args:
            api_key: 百炼API Key
            model_name: 模型名称，默认使用最新版本
            batch_config: 分批处理配置，如果为None则使用默认配置
            **kwargs: 其他配置参数
        """
        super().__init__(api_key, model_name, **kwargs)
        
        # 千问API配置
        self.base_url = kwargs.get('base_url', "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation")
        self.provider = "阿里云百炼"
        
        # 分批处理配置
        if batch_config is None:
            # 如果没有提供配置，尝试从kwargs创建或使用默认配置
            if any(key in kwargs for key in ['enable_auto_batch', 'max_input_length', 'batch_overlap']):
                # 从kwargs创建配置（向后兼容）
                self.batch_config = BatchConfig(
                    enable_auto_batch=kwargs.get('enable_auto_batch', True),
                    max_input_length=kwargs.get('max_input_length', 15000),
                    batch_overlap=kwargs.get('batch_overlap', 500),
                    max_devices_per_batch=kwargs.get('max_devices_per_batch', None),
                    safety_margin=kwargs.get('safety_margin', 0.8),
                    retry_failed_batches=kwargs.get('retry_failed_batches', True),
                    max_batch_retries=kwargs.get('max_batch_retries', 2)
                )
            else:
                # 根据输入数据大小智能选择配置
                device_count = len(kwargs.get('initial_gis_data', {}).get('devices', []))
                if device_count > 0:
                    self.batch_config = BatchConfigPresets.recommend_for_data_size(device_count)
                    self.logger.info(f"根据设备数量({device_count})自动选择批处理配置")
                else:
                    # 使用更保守的默认配置，避免输出超过token限制
                    self.batch_config = BatchConfigPresets.conservative()
                    self.logger.info("使用保守的默认批处理配置")
        else:
            self.batch_config = batch_config
        
        # 验证配置
        try:
            self.batch_config.validate()
        except ValueError as e:
            self.logger.error(f"分批配置验证失败: {e}")
            self.logger.info("使用默认配置")
            self.batch_config = BatchConfigPresets.balanced()
        
        # 为了向后兼容，保留原有属性
        self.enable_auto_batch = self.batch_config.enable_auto_batch
        self.max_input_length = self.batch_config.max_input_length
        self.batch_overlap = self.batch_config.batch_overlap
        
        self.logger.info(f"千问模型初始化成功: {self.model_name}")
        if self.enable_auto_batch:
            self.logger.info(f"已启用自动分批处理，最大输入长度: {self.max_input_length}")
            self.logger.debug(f"分批配置: {self.batch_config}")
    
    def _estimate_input_length(self, messages: List[dict]) -> int:
        """估算输入消息的字符长度"""
        total_length = 0
        for message in messages:
            content = message.get('content', '')
            if isinstance(content, str):
                total_length += len(content)
            elif isinstance(content, list):
                for item in content:
                    if isinstance(item, dict) and item.get('type') == 'text':
                        total_length += len(item.get('text', ''))
        return total_length
    
    def _split_gis_data(self, gis_data: dict, max_devices_per_batch: int = None) -> List[dict]:
        """将GIS数据按设备数量分割成多个批次，考虑输出token限制"""
        devices = gis_data.get('devices', [])
        
        # 使用配置中的设备数限制
        if max_devices_per_batch is None:
            max_devices_per_batch = self.batch_config.max_devices_per_batch
        
        # 如果没有设置设备数限制，使用默认值
        if max_devices_per_batch is None:
            max_devices_per_batch = 50  # 默认值
        
        # 根据设备总数动态调整批次大小，避免输出超过token限制
        total_devices = len(devices)
        if total_devices > 100:
            # 对于大数据集，进一步减小批次大小
            max_devices_per_batch = min(max_devices_per_batch, 10)
            self.logger.info(f"检测到大数据集({total_devices}个设备)，调整批次大小为{max_devices_per_batch}")
        elif total_devices > 50:
            # 对于中等数据集，适度减小批次大小
            max_devices_per_batch = min(max_devices_per_batch, 15)
            self.logger.info(f"检测到中等数据集({total_devices}个设备)，调整批次大小为{max_devices_per_batch}")
        
        if len(devices) <= max_devices_per_batch:
            return [gis_data]
        
        batches = []
        for i in range(0, len(devices), max_devices_per_batch):
            batch_devices = devices[i:i + max_devices_per_batch]
            batch_data = {
                **gis_data,
                'devices': batch_devices,
                'metadata': {
                    **gis_data.get('metadata', {}),
                    'batch_info': {
                        'batch_index': len(batches),
                        'total_devices': len(devices),
                        'batch_devices': len(batch_devices),
                        'device_range': [i, i + len(batch_devices)]
                    }
                }
            }
            batches.append(batch_data)
        
        self.logger.info(f"将{len(devices)}个设备分割为{len(batches)}个批次处理")
        self.logger.debug(f"每批次最大设备数: {max_devices_per_batch}")
        return batches
    
    def _merge_treatment_results(self, batch_results: List[GISData]) -> GISData:
        """合并多个批次的治理结果"""
        if not batch_results:
            return GISData(devices=[], buildings=[], roads=[], rivers=[], boundaries={}, metadata={})
        
        if len(batch_results) == 1:
            return batch_results[0]
        
        # 合并所有设备
        all_devices = []
        for result in batch_results:
            all_devices.extend(result.devices)
        
        # 使用第一个结果的其他数据作为基础
        base_result = batch_results[0]
        merged_result = GISData(
            devices=all_devices,
            buildings=base_result.buildings,
            roads=base_result.roads,
            rivers=base_result.rivers,
            boundaries=base_result.boundaries,
            metadata={
                **base_result.metadata,
                'merged_from_batches': len(batch_results),
                'total_devices': len(all_devices)
            }
        )
        
        self.logger.info(f"成功合并{len(batch_results)}个批次的结果，总设备数: {len(all_devices)}")
        return merged_result
    
    def beautify(self, gis_data: dict, prompt: str, image_path: Optional[str] = None):
        """重写beautify方法以支持自动分批处理"""
        from .base_model import TreatmentResponse
        from core.data_types import GISData
        
        device_count = len(gis_data.get('devices', []))
        self.logger.info(f"开始治理处理，输入设备数量: {device_count}")
        
        # 根据实际数据大小动态调整批处理配置
        if device_count > 50:
            # 对于大数据集，使用更保守的配置
            original_config = self.batch_config
            self.batch_config = BatchConfigPresets.recommend_for_data_size(device_count)
            self.logger.info(f"根据设备数量({device_count})动态调整批处理配置: max_devices_per_batch={self.batch_config.max_devices_per_batch}")
        
        try:
            if self.enable_auto_batch:
                # 使用自动分批处理
                batch_result = self._process_with_auto_batch(gis_data, prompt, image_path)
                # _process_with_auto_batch返回字典，需要提取TreatmentResponse
                if batch_result['success']:
                    return batch_result['data']  # 直接返回TreatmentResponse对象
                else:
                    # 分批处理失败，返回失败的TreatmentResponse
                    return TreatmentResponse(
                        treated_gis_data=GISData(devices=[], buildings=[], roads=[], rivers=[], boundaries={}, metadata={}),
                        input_tokens=0,
                        output_tokens=0,
                        processing_time=0.0,
                        raw_response=batch_result['message'],
                        confidence_score=0.0
                    )
            else:
                # 使用原始处理方式
                messages = self._build_beautify_messages(gis_data, prompt)
                if image_path:
                    messages = self._add_image_to_messages(messages, image_path)
                
                api_response = self._make_api_call(messages)
                result = self._parse_treatment_response(api_response['response'])
                
                # 返回TreatmentResponse对象
                return TreatmentResponse(
                    treated_gis_data=result,
                    input_tokens=api_response['usage']['input_tokens'],
                    output_tokens=api_response['usage']['output_tokens'],
                    processing_time=0.0,
                    raw_response=api_response['response'],
                    confidence_score=self._extract_confidence(api_response['response'])
                )
            
        except Exception as e:
            self.logger.error(f"治理处理失败: {e}")
            # 异常时也返回TreatmentResponse对象
            empty_gis_data = GISData(
                devices=[],
                buildings=gis_data.get('buildings', []),
                roads=gis_data.get('roads', []),
                rivers=gis_data.get('rivers', []),
                boundaries=gis_data.get('boundaries', {}),
                metadata=gis_data.get('metadata', {})
            )
            
            return TreatmentResponse(
                treated_gis_data=empty_gis_data,
                input_tokens=0,
                output_tokens=0,
                processing_time=0.0,
                raw_response=f'治理失败: {str(e)}',
                confidence_score=0.0
            )
    
    def _build_beautify_messages(self, gis_data: dict, prompt: str) -> List[dict]:
        """构建治理请求的消息（从BaseModel复制）"""
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
            {"role": "system", "content": "你是一个专业的GIS数据处理和电网台区美化专家。"},
            {"role": "user", "content": user_message}
        ]
    
    def _process_with_auto_batch(self, gis_data: dict, prompt: str, image_path: Optional[str] = None) -> dict:
        """自动分批处理大输入数据"""
        from .base_model import TreatmentResponse
        
        try:
            # 估算输入长度
            test_messages = self._build_beautify_messages(gis_data, prompt)
            if image_path:
                test_messages = self._add_image_to_messages(test_messages, image_path)
            
            input_length = self._estimate_input_length(test_messages)
            
            if input_length <= self.max_input_length:
                # 输入长度在限制内，直接处理
                self.logger.info(f"输入长度{input_length}在限制内，直接处理")
                response = self._make_api_call(test_messages)
                result = self._parse_treatment_response(response['response'])
                
                # 创建TreatmentResponse对象
                treatment_response = TreatmentResponse(
                    treated_gis_data=result,
                    input_tokens=response['usage']['input_tokens'],
                    output_tokens=response['usage']['output_tokens'],
                    processing_time=0.0,
                    raw_response=response['response'],
                    confidence_score=self._extract_confidence(response['response'])
                )
                
                return {
                    'success': True,
                    'data': treatment_response,
                    'message': '治理成功完成',
                    'metadata': {
                        'input_tokens': response['usage']['input_tokens'],
                        'output_tokens': response['usage']['output_tokens'],
                        'processing_time': 0.0
                    }
                }
            
            # 需要分批处理
            self.logger.info(f"输入长度{input_length}超过限制{self.max_input_length}，启用分批处理")
            
            # 估算每批次最大设备数
            device_count = len(gis_data.get('devices', []))
            if device_count == 0:
                # 如果没有设备，可能是其他数据过大，直接尝试处理
                response = self._make_api_call(test_messages)
                result = self._parse_treatment_response(response['response'])
                
                # 创建TreatmentResponse对象
                treatment_response = TreatmentResponse(
                    treated_gis_data=result,
                    input_tokens=response['usage']['input_tokens'],
                    output_tokens=response['usage']['output_tokens'],
                    processing_time=0.0,
                    raw_response=response['response'],
                    confidence_score=self._extract_confidence(response['response'])
                )
                
                return {
                    'success': True,
                    'data': treatment_response,
                    'message': '治理成功完成',
                    'metadata': {
                        'input_tokens': response['usage']['input_tokens'],
                        'output_tokens': response['usage']['output_tokens'],
                        'processing_time': 0.0
                    }
                }
        
            # 根据输入长度比例估算每批次设备数
            ratio = self.max_input_length / input_length
            max_devices_per_batch = max(1, int(device_count * ratio * 0.8))  # 留20%余量
            
            self.logger.info(f"每批次最大设备数: {max_devices_per_batch}")
            
            # 分割数据
            batches = self._split_gis_data(gis_data, max_devices_per_batch)
            
            # 处理每个批次
            batch_results = []
            failed_batches = []
        
            for i, batch_data in enumerate(batches):
                self.logger.info(f"处理批次 {i+1}/{len(batches)}")
                
                success = False
                retry_count = 0
                
                while not success and retry_count <= self.batch_config.max_batch_retries:
                    try:
                        if retry_count > 0:
                            self.logger.info(f"批次 {i+1} 重试第 {retry_count} 次")
                        
                        # 构建消息
                        messages = self._build_beautify_messages(batch_data, prompt)
                        if image_path:
                            messages = self._add_image_to_messages(messages, image_path)
                        
                        # 调用API
                        response = self._make_api_call(messages)
                        result = self._parse_treatment_response(response['response'])
                        batch_results.append(result)
                        
                        self.logger.info(f"批次 {i+1} 处理完成，设备数: {len(result.devices)}")
                        success = True
                        
                    except Exception as e:
                        retry_count += 1
                        self.logger.error(f"批次 {i+1} 处理失败 (尝试 {retry_count}): {e}")
                        
                        if retry_count > self.batch_config.max_batch_retries:
                            if self.batch_config.retry_failed_batches:
                                self.logger.warning(f"批次 {i+1} 达到最大重试次数，记录为失败批次")
                                failed_batches.append((i+1, batch_data, str(e)))
                                # 创建空结果以保持批次完整性
                                empty_result = GISData(
                                    devices=[],
                                    buildings=[],
                                    roads=[],
                                    rivers=[],
                                    boundaries={},
                                    metadata={'error': str(e), 'batch_index': i}
                                )
                                batch_results.append(empty_result)
                            else:
                                self.logger.error(f"批次 {i+1} 处理失败，停止处理")
                                raise
        
            # 报告失败的批次
            if failed_batches:
                self.logger.warning(f"共有 {len(failed_batches)} 个批次处理失败")
                for batch_num, _, error in failed_batches:
                    self.logger.warning(f"  - 批次 {batch_num}: {error}")
            
            # 合并结果
            merged_result = self._merge_treatment_results(batch_results)
            
            # 创建TreatmentResponse对象
            treatment_response = TreatmentResponse(
                treated_gis_data=merged_result,
                input_tokens=0,  # 分批处理时暂时设为0
                output_tokens=0,  # 分批处理时暂时设为0
                processing_time=0.0,
                raw_response="分批处理完成",
                confidence_score=0.9
            )
            
            return {
                'success': True,
                'data': treatment_response,
                'message': f'分批治理成功完成，共处理{len(batches)}个批次',
                'metadata': {
                    'input_tokens': 0,
                    'output_tokens': 0,
                    'processing_time': 0.0,
                    'batch_count': len(batches),
                    'failed_batches': len(failed_batches)
                }
            }
            
        except Exception as e:
            self.logger.error(f"分批处理失败: {e}")
            return {
                'success': False,
                'data': None,
                'message': f'分批处理失败: {str(e)}',
                'metadata': {
                    'input_tokens': 0,
                    'output_tokens': 0,
                    'processing_time': 0.0
                }
            }
    
    def _make_api_call(self, messages: List[dict], **kwargs) -> Dict[str, Any]:
        """
        千问API调用实现 - 使用requests直接调用
        
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
                "input": {
                    "messages": messages
                },
                "parameters": {
                    "max_tokens": kwargs.get('max_tokens', 8000),
                    "temperature": kwargs.get('temperature', 0.3),
                    "top_p": kwargs.get('top_p', 0.8)
                }
            }
            
            self.logger.debug(f"调用千问API，模型: {self.model_name}")
            
            # 调用API
            response = requests.post(
                self.base_url,
                headers=headers,
                json=data,
                timeout=self.timeout
            )
            response.raise_for_status()
            result = response.json()
            
            if result.get("code"):
                raise Exception(f"千问API错误: {result.get('message', 'Unknown error')}")
            
            # 提取响应信息
            output = result["output"]
            content = output["choices"][0]["message"]["content"]
            
            usage_data = result.get("usage", {})
            usage = {
                "input_tokens": usage_data.get("input_tokens", 0),
                "output_tokens": usage_data.get("output_tokens", 0),
                "total_tokens": usage_data.get("total_tokens", 0)
            }
            
            self.logger.info(f"千问API调用成功，输入tokens: {usage['input_tokens']}, 输出tokens: {usage['output_tokens']}")
            
            return {
                "response": content,
                "usage": usage,
                "raw_response": result
            }
            
        except Exception as e:
            self.logger.error(f"千问API调用失败: {e}")
            raise
    
    def _add_image_to_messages(self, messages: List[dict], image_path: str) -> List[dict]:
        """
        千问的图片添加方式
        
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
            
            # 千问使用OpenAI兼容格式
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
        千问VL-Max定价信息
        
        Returns:
            ModelPricing: 定价信息
        """
        # 基于2025年1月的千问VL-Max定价（按美元计算）
        return ModelPricing(
            input_price_per_1m_tokens=0.4,   # 约合美元价格
            output_price_per_1m_tokens=1.2,  # 约合美元价格
            currency="USD",
            model_name=self.model_name
        )
    
    def _parse_treatment_response(self, response: str) -> GISData:
        """
        解析千问的治理响应
        
        千问的响应通常包含JSON数组或包含devices字段的对象；也可能被```json 包裹，或末尾缺少收尾括号。
        """
        try:
            import re
            self.logger.debug("开始解析千问治理响应")

            def _to_text(resp) -> str:
                if isinstance(resp, str):
                    return resp
                # 常见：[{"text": "```json...```"}]
                try:
                    if isinstance(resp, list):
                        parts = []
                        for item in resp:
                            if isinstance(item, dict) and 'text' in item and isinstance(item['text'], str):
                                parts.append(item['text'])
                        if parts:
                            return "".join(parts)
                except Exception:
                    pass
                return str(resp)

            raw_text = _to_text(response)

            def _json_fix_and_load(s: str):
                # 去除结尾多余逗号
                s2 = re.sub(r",\s*([}\]])", r"\1", s)
                
                # 尝试直接解析
                try:
                    return json.loads(s2)
                except json.JSONDecodeError as e:
                    # 尝试修复常见的JSON语法错误
                    s3 = s2
                    
                    # 首先处理模型输出截断的情况（移除"..."标记和相关的不完整结构）
                    s3 = re.sub(r'\s*\.\.\..*$', '', s3, flags=re.DOTALL)
                    s3 = re.sub(r',\s*$', '', s3)  # 移除末尾的逗号
                    
                    # 然后尝试通用的逗号修复：在数值后添加逗号（如果后面跟着换行和其他内容）
                    s3 = re.sub(r'(\d+\.?\d*)(\s*\n\s*[\[\{"\d])', r'\1,\2', s3)
                    
                    # 修复对象属性之间缺少逗号的问题
                    s3 = re.sub(r'("[^"]*"\s*:\s*[^,}\]]*)(\s*"[^"]*"\s*:)', r'\1,\2', s3)
                    
                    # 修复数组元素之间缺少逗号的问题
                    s3 = re.sub(r'(})(\s*{)', r'\1,\2', s3)
                    s3 = re.sub(r'(])(\s*\[)', r'\1,\2', s3)
                    
                    # 修复数字/字符串后缺少逗号的问题
                    s3 = re.sub(r'("[^"]*")(\s*"[^"]*")', r'\1,\2', s3)
                    s3 = re.sub(r'(\d+)(\s*"[^"]*")', r'\1,\2', s3)
                    
                    # 修复数组中数值后缺少逗号的问题（特别处理浮点数）
                    s3 = re.sub(r'(\d+\.\d+)(\s*\])', r'\1\2', s3)  # 数组末尾的浮点数
                    s3 = re.sub(r'(\d+\.\d+)(\s*\n\s*\])', r'\1\2', s3)  # 换行后的数组结束
                    s3 = re.sub(r'(\d+\.\d+)(\s*\n\s*\[)', r'\1,\2', s3)  # 数组间的浮点数
                    s3 = re.sub(r'(\d+\.\d+)(\s*\n\s*{)', r'\1,\2', s3)  # 对象前的浮点数
                    
                    # 修复数组结束后缺少逗号的问题
                    s3 = re.sub(r'(\])(\s*"[^"]*"\s*:)', r'\1,\2', s3)
                    
                    # 修复对象结束后缺少逗号的问题
                    s3 = re.sub(r'(})(\s*"[^"]*"\s*:)', r'\1,\2', s3)
                    
                    # 修复数值后缺少逗号的问题（更精确的模式）
                    s3 = re.sub(r'(\d+\.?\d*)(\s*\])', r'\1\2', s3)  # 数组内数值
                    s3 = re.sub(r'(\d+\.?\d*)(\s*})', r'\1\2', s3)   # 对象内数值
                    
                    # 修复嵌套数组中缺少逗号的问题
                    s3 = re.sub(r'(\])(\s*\[)', r'\1,\2', s3)
                    
                    # 修复对象属性值后缺少逗号的问题
                    s3 = re.sub(r'("[^"]*")(\s*"[^"]*"\s*:)', r'\1,\2', s3)
                    
                    # 修复数组中对象间缺少逗号的问题
                    s3 = re.sub(r'(})(\s*{)', r'\1,\2', s3)
                    
                    # 修复多层嵌套结构中的逗号问题
                    s3 = re.sub(r'(\d+\.?\d*)(\s*\]\s*,?\s*\[)', r'\1\2', s3)
                    
                    # 修复数组中连续数值缺少逗号的问题
                    s3 = re.sub(r'(\d+\.\d+)(\s*\n\s*\d+\.\d+)', r'\1,\2', s3)
                    s3 = re.sub(r'(\d+)(\s*\n\s*\d+)', r'\1,\2', s3)
                    
                    # 修复数组中数值和数组结束符之间的问题
                    s3 = re.sub(r'(\d+\.\d+)(\s*\n\s*\]\s*\n\s*\])', r'\1\2', s3)
                    
                    try:
                        return json.loads(s3)
                    except json.JSONDecodeError as e:
                        # 处理"Extra data"错误，截取到第一个完整的JSON对象
                        if "Extra data" in str(e):
                            try:
                                # 尝试找到第一个完整的JSON对象的结束位置
                                decoder = json.JSONDecoder()
                                obj, idx = decoder.raw_decode(s3)
                                return obj
                            except (json.JSONDecodeError, ValueError):
                                pass
                        # 追加缺失的收尾括号
                        need_brace = s3.count('{') - s3.count('}')
                        need_bracket = s3.count('[') - s3.count(']')
                        if need_brace > 0 or need_bracket > 0:
                            s4 = s3 + ('}' * max(0, need_brace)) + (']' * max(0, need_bracket))
                            try:
                                return json.loads(s4)
                            except json.JSONDecodeError:
                                pass
                        
                        # 如果所有修复尝试都失败，抛出原始错误
                        raise e

            def _extract_any_json(text: str):
                t = text.replace('\u200b', '').replace('\ufeff', '')
                # 去掉代码围栏标记，但保留内容
                t = t.replace('```json', '```').replace('```JSON', '```')
                # 优先对象，再尝试数组
                i_obj, j_obj = t.find('{'), t.rfind('}')
                if i_obj != -1 and j_obj != -1 and j_obj > i_obj:
                    candidate = t[i_obj:j_obj+1]
                    try:
                        return _json_fix_and_load(candidate)
                    except Exception:
                        pass
                i_arr, j_arr = t.find('['), t.rfind(']')
                if i_arr != -1 and j_arr != -1 and j_arr > i_arr:
                    candidate = t[i_arr:j_arr+1]
                    return _json_fix_and_load(candidate)
                # 代码块内再试一次
                m = re.search(r"```+\s*(?:json|JSON)?\s*(.*?)```", t, flags=re.S)
                if m:
                    inner = m.group(1)
                    # 去除可能的前缀/后缀说明
                    inner = inner.strip()
                    # 再递归一次
                    return _extract_any_json(inner)
                return None

            parsed = _extract_any_json(raw_text)
            if parsed is None:
                raise ValueError("响应中未找到有效的JSON片段")

            # 统一为设备列表
            if isinstance(parsed, dict):
                devices_list = parsed.get('devices') or parsed.get('annotations') or []
            elif isinstance(parsed, list):
                devices_list = parsed
            else:
                devices_list = []

            # 转换为标准的GIS数据格式
            processed_devices = []
            for device in devices_list:
                if isinstance(device, dict) and 'points' in device:
                    # 计算设备中心点作为x, y坐标
                    points = device.get('points') or []
                    if points:
                        x_coords = [p[0] for p in points if isinstance(p, (list, tuple)) and len(p) >= 2]
                        y_coords = [p[1] for p in points if isinstance(p, (list, tuple)) and len(p) >= 2]
                        if x_coords and y_coords:
                            center_x = sum(x_coords) / len(x_coords)
                            center_y = sum(y_coords) / len(y_coords)
                            processed_devices.append({
                                'id': device.get('id') or f"dev_{len(processed_devices)}",
                                'x': center_x,
                                'y': center_y,
                                'type': device.get('label', 'unknown'),
                                'points': points,
                                'original_data': device
                            })

            self.logger.info(f"成功解析 {len(processed_devices)} 个设备")

            return GISData(
                devices=processed_devices,
                buildings=[],
                roads=[],
                rivers=[],
                boundaries={},
                metadata={
                    'source': 'qwen_treatment',
                    'model': self.model_name,
                    'device_count': len(processed_devices)
                }
            )

        except Exception as e:
            # 安全打印原始响应摘要
            try:
                raw_preview = _to_text(response)[:500]
            except Exception:
                raw_preview = str(response)[:500]
            self.logger.error(f"解析千问治理响应失败: {e}")
            self.logger.error(f"原始响应: {raw_preview}...")
            
            # 保存失败的响应到文件以便调试
            import os
            debug_dir = "debug_responses"
            os.makedirs(debug_dir, exist_ok=True)
            with open(os.path.join(debug_dir, "failed_response.json"), "w", encoding="utf-8") as f:
                f.write(raw_text)
            
            # 同时保存经过修复处理后的文本
            try:
                # 尝试应用修复逻辑看看结果
                test_text = raw_text
                test_text = re.sub(r'\s*\.\.\..*$', '', test_text, flags=re.DOTALL)
                test_text = re.sub(r',\s*$', '', test_text)
                with open(os.path.join(debug_dir, "processed_response.json"), "w", encoding="utf-8") as f:
                    f.write(test_text)
                self.logger.error(f"处理后的响应已保存到: {os.path.join(debug_dir, 'processed_response.json')}")
            except Exception as debug_e:
                self.logger.error(f"保存处理后响应失败: {debug_e}")
            
            self.logger.error(f"完整响应已保存到: {os.path.join(debug_dir, 'failed_response.json')}")
            
            raise ValueError(f"无法解析千问治理结果: {str(e)}")
    
    def _parse_evaluation_response(self, response: str) -> Dict[str, Any]:
        """
        解析千问的评分响应
        
        Args:
            response: 千问模型的原始响应
            
        Returns:
            Dict[str, Any]: 解析后的评分数据
        """
        try:
            self.logger.debug("开始解析千问评分响应")
            
            # 尝试提取JSON部分
            if not isinstance(response, str):
                data = json.loads(response[0]['text'][7:-3])
            else:
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
            self.logger.error(f"解析千问评分响应失败: {e}")
            self.logger.error(f"原始响应: {response[:500]}...")
            raise ValueError(f"无法解析千问评分结果: {str(e)}")
    
    def _extract_confidence(self, response: str) -> float:
        """
        从千问响应中提取置信度
        
        Args:
            response: 原始响应文本
            
        Returns:
            float: 置信度分数 (0-1)
        """
        # 千问通常不直接提供置信度，这里基于响应质量估算
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
        self.logger.info(f"模拟调用千问VL-Max API...")
        self.logger.info(f"输入数据: {len(gis_data.get('devices', []))}个设备")
        
        import time
        time.sleep(0.1)  # 模拟网络延迟
        
        # 模拟治理后的数据
        treated_devices = []
        for device in gis_data.get('devices', []):
            optimized_device = device.copy()
            optimized_device['x'] += 10  # 模拟位置调整
            optimized_device['y'] += 5
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
        self.logger.info("模拟调用千问进行美观性评分...")
        
        import time
        time.sleep(0.1)
        
        return {
            "beauty_score": 85.5,
            "dimension_scores": {
                "layout": 88,      # 布局合理性
                "spacing": 85,     # 设备间距
                "harmony": 87,     # 视觉和谐性
                "accessibility": 82 # 可达性
            },
            "improvement_analysis": {
                "devices_moved": 3,
                "spacing_improved": True,
                "layout_optimized": True
            },
            "reasoning": "治理后设备布局更加整齐，间距更加合理，整体美观性得到显著提升。"
        }