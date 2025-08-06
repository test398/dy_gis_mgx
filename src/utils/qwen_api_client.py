import os
import json
import base64
import time
from typing import Dict, Any
from openai import OpenAI

class QwenAPIClient:
    def __init__(self, api_key: str, base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    @staticmethod
    def encode_image(image_path: str) -> str:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def call_beautification_api(self, image1_path: str, image2_path: str, gis_data1: Dict, gis_data2: Dict) -> Dict:
        """
        image1_path: 治理前图片路径
        image2_path: 治理后图片路径
        gis_data1: 治理前gis数据
        gis_data2: 治理后gis数据
        """
        base64_image1 = self.encode_image(image1_path)
        base64_image2 = self.encode_image(image2_path)
        system_prompt = self._get_system_prompt()
        user_prompt = self._format_prompt_for_evaluation(gis_data1, gis_data2)
        start_time = time.perf_counter()
        try:
            completion = self.client.chat.completions.create(
                model="qwen-vl-max-2025-04-08",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": [
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image1}"}},
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image2}"}},
                        ],
                    },
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=6144,
            )
            response_content = completion.choices[0].message.content
            parsed = self._parse_evaluation_response(response_content)
            valid = self._validate_scoring_output(parsed)
            end_time = time.perf_counter()
            return {
                "raw_response": response_content,
                "parsed": parsed,
                "valid": valid,
                "run_time": end_time - start_time
            }
        except Exception as e:
            end_time = time.perf_counter()
            return {"error": str(e), "run_time": end_time - start_time}

    def _format_prompt_for_evaluation(self, original_data: Dict, treated_data: Dict) -> str:
        return f"""
【输入数据1 - 电网设备的标注坐标信息】：\n{json.dumps(original_data, ensure_ascii=False)}\n\n【输入数据2 - 电网设备删除或者新增的设备信息】：\n{json.dumps(treated_data, ensure_ascii=False)}\n\n说明: 输入数据1和输入数据2中的设备是有对应关系的, 设备的id相同表示对应。输入数据1上的坐标对应第一张图片，输入数据2上的坐标对应第二张图片。请按照系统提示中的规则重新排布电网设备，输出优化后的设备坐标信息。"""

    def _parse_evaluation_response(self, raw_response: str) -> Any:
        # 尝试提取JSON部分
        if '[' in raw_response:
            start_idx = raw_response.find('[')
            if ']' in raw_response:
                end_idx = raw_response.rfind(']') + 1
                json_str = raw_response[start_idx:end_idx]
            else:
                json_str = raw_response[start_idx:]
                last_comma = json_str.rfind(',')
                if last_comma > 0:
                    json_str = json_str[:last_comma] + '\n]'
                else:
                    json_str += ']'
            try:
                return json.loads(json_str)
            except Exception as e:
                return {"error": f"JSON解析失败: {e}", "raw": raw_response}
        return {"error": "未找到JSON格式输出", "raw": raw_response}

    def _validate_scoring_output(self, parsed_data: Any) -> bool:
        # 检查是否包含5大评价维度的关键字段
        if isinstance(parsed_data, list):
            # 简单检查每个设备是否有id和points
            for item in parsed_data:
                if not isinstance(item, dict):
                    return False
                if 'id' not in item or 'points' not in item:
                    return False
            return True
        return False

    def _get_system_prompt(self) -> str:
        # 可根据实际需求调整，或从文件读取
        return """
你是一名电网GIS专家，正在处理低压台区的设备排布优化任务。你将获得电网设备的标注数据。请根据设备标注数据，按照规则重新排布电网设备，仅输出设备的坐标信息。\n(详细规则略，可参考原prompt)\n【输出格式示例】\n[{'id': 'TFvUrGF_P1', 'points': [[100, 200], ...]}, ...]\n"""