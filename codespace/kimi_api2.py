# -*- coding: utf-8 -*-
"""
@Time ： 2025/8/4 17:09
@Auth ： bonck
@File ：kimi_api2.py
@IDE ：PyCharm
@Motto：(Always Be Coding)
"""

# -*- coding: utf-8 -*-
"""
@Time ： 2025/8/4 15:33
@Auth ： bonck
@File ：kimi_api.py
@IDE ：PyCharm
@Motto：(Always Be Coding)
"""
import os
import json
import matplotlib.pyplot as plt
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv
import time
import base64

# Load environment variables from .env file
load_dotenv()
APIKEY = "sk-CwIjxXK6TAcsMofUKMovBdPVfyS088aKVCPUKYmfYfK8YkiI"

# 读取标注json的内容
with open(os.path.abspath('zlq.json'), 'r', encoding='utf-8') as f:
    content = f.read()
with open(os.path.abspath('zlh.json'), 'r', encoding='utf-8') as f:
    content2 = f.read()


# System prompt保持不变（您原有的详细提示）

def encode_image_to_base64(image_path):
    """优化图片编码函数，添加错误处理"""
    try:
        with open(image_path, "rb") as f:
            image_data = f.read()
        return f"data:image/{os.path.splitext(image_path)[1][1:]};base64,{base64.b64encode(image_data).decode('utf-8')}"
    except Exception as e:
        print(f"图片编码错误: {e}")
        return None


# 处理两张图片
image_path1 = "4ecd11d6-ea922643e18a06deef5a716682015aea8fd2862bb8.png"
image_path2 = "186808be-ea922643e18a06deef5a716682015aea8fd2862bb8.png"

image_url1 = encode_image_to_base64(image_path1)
image_url2 = encode_image_to_base64(image_path2)

# 检查图片是否加载成功
if not all([image_url1, image_url2]):
    raise ValueError("图片加载失败，请检查路径")

client = OpenAI(
    api_key=APIKEY,
    base_url="https://api.moonshot.cn/v1",
)


def call_api_with_retry():
    """带重试机制的API调用函数"""
    max_retries = 3
    retry_delay = 60  # 初始延迟60秒

    for attempt in range(max_retries):
        try:
            # 记录开始时间
            start_time = time.perf_counter()

            completion = client.chat.completions.create(
                model="moonshot-v1-8k-vision-preview",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": [
                            {"type": "image_url", "image_url": {"url": image_url1}},
                            {"type": "image_url", "image_url": {"url": image_url2}},
                            {"type": "text", "text": user_prompt}
                        ],
                    }
                ],
                max_tokens=4096  # 适当降低token限制
            )

            response_content = completion.choices[0].message.content
            print("API调用成功！")
            return response_content

        except Exception as api_error:
            if "rate_limit" in str(api_error):
                wait_time = retry_delay * (attempt + 1)
                print(f"达到速率限制，第 {attempt + 1} 次重试，等待 {wait_time} 秒...")
                time.sleep(wait_time)
            else:
                print(f"API错误: {api_error}")
                raise

    raise Exception(f"API调用失败，已达最大重试次数 {max_retries}")


try:
    # 调用带重试的函数
    response_content = call_api_with_retry()

    # 处理响应（保持您原有的处理逻辑）
    try:
        if '[' in response_content:
            start_idx = response_content.find('[')
            end_idx = response_content.rfind(']') + 1 if ']' in response_content else len(response_content)
            json_str = response_content[start_idx:end_idx]

            # 尝试修复可能的JSON格式问题
            if not json_str.strip().endswith(']'):
                json_str = json_str[:json_str.rfind(',')] + ']'

            output_devices = json.loads(json_str)
            print("成功解析响应数据！")

    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}")
        # 保存原始响应
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        with open(f'response_{timestamp}.json', 'w', encoding='utf-8') as f:
            f.write(response_content)
        print(f"原始响应已保存为 response_{timestamp}.json")

except Exception as final_error:
    print(f"最终错误: {final_error}")

# 记录运行时间
end_time = time.perf_counter()
print(f"\n总运行时间: {(end_time - start_time):.2f} 秒")