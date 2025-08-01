import os
from openai import OpenAI
""" 
图片中是一个电网低压台区GIS图,我们将图中电网设备做了标注,并且标注结果将在下面提供出来.
请按照以下规则帮我重新排布电网设备,只要电网设备的坐标,建筑,道路和河流的坐标信息只作为参考,不做规划.
电网设备的标注坐标信息如下: {content}
请将电网设备的坐标信息按照以下规则进行排布:
1. 沿路排布原则： 设备只排布在道路两侧一米的范围
2. 电缆头摆放原则： 设备应水平整齐摆放在站房的正下方, 设备距离站房不宜过远, 并且摆放在附近的建筑物旁边
3. 分支箱摆放原则： 设备应摆放在楼栋附近的空地处
4. 接入点摆放原则： 设备从同一个电缆头出来的接入点应合并在同一个像素点，并且这个位置应该在建筑物上
5. 表箱摆放原则： 设备应与接入点方向水平或者成正交折线
6. 线形优化： 共线段需合并，线段应沿道路排布(横平竖直)；若无明显道路，则顺着建筑物的边缘沿布
7. 正交最短布线： 连线拐点最少、总长最短，避免穿越建筑物、站房设备，涉水等。
请按照以下格式输出坐标信息:
['id': 'TFvUrGF_P1', 'points': [[x, y], [x, y], [x, y], [x, y]], ...]
不要修改标注的id, 只需要修改坐标信息即可.严格按照上面数据格式输出坐标信息.不要有其他内容.
"""
# 读取标注json的内容
content = open('zlq.json', 'r', encoding='utf-8').read()
content2 = open('zlh.json', 'r', encoding='utf-8').read()


client = OpenAI(
    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
    api_key='sk-12ddc17853354879ba2a18830f3a41d7',
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)
completion = client.chat.completions.create(
    model="qwen-vl-max-2025-04-08",  # 此处以qwen-vl-plus为例，可按需更换模型名称。模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
    extra_body={
            "parameters": {
                "vl_high_resolution_images": True  # 启用高分辨率模式
            }
        },
    messages=[{"role": "user","content": [
            {"type": "image_url",
             "image_url": {"url": "https://dashscope-file-datacenter-prod-01.oss-cn-beijing.aliyuncs.com/1920596245375804/12139647/5c708a3b589a458d8fadea2e3497149b.1753674342953.png?Expires=1753952360&OSSAccessKeyId=LTAI5tFEd57BcgTFgxpSL5j1&Signature=5%2FNGt8lygFBYGckYV3APNdiyFEQ%3D"}},
            {"type": "text", "text": f""" """}
            ]}]
    )
print(completion.model_dump_json())

