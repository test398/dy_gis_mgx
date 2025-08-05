import os
import json
import matplotlib.pyplot as plt
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv
import time

# Load environment variables from .env file
load_dotenv()

# 读取标注json的内容
with open('../标注数据目录/有对应关系的标注结果数据/zlq.json', 'r', encoding='utf-8') as f:
    content = f.read()
with open('../标注数据目录/有对应关系的标注结果数据/zlh.json', 'r', encoding='utf-8') as f:
    content2 = f.read()

# System prompt with background and rules
system_prompt = """
【背景说明】
你是一名电网GIS专家，正在处理低压台区的设备排布优化任务。你将获得电网设备的标注数据。

【术语解释】
- 台区：指低压配电网的供电区域。
- GIS：地理信息系统，包含空间地物信息。
- 站房：配电变压器等设备的集中安置建筑。
- points：二维坐标点数组，表示设备空间位置。

【设备类型说明】
- 档距段/连接线：连接各设备的线路，需沿道路排布。
- 电缆头：电缆起始/终止点，通常靠近站房或建筑物。
- 分支箱：分配电能的设备，需靠近楼栋长边空地。
- 接入点：电缆头与表箱的连接点，合并于建筑物中心。
- 表箱：用户用电计量箱，需与接入点方向水平或正交。

【输入数据字段说明】
- id：设备唯一标识，字符串类型。
- label：设备类型，取值如"表箱"、"电缆头"等。
- points：二维数组，每个元素为[x, y]坐标。
- flag：设备增删标时,取值为"new_pos"或"old_pos"。

【目标与输出要求】
请根据设备标注数据，按照以下规则重新排布电网设备，仅输出设备的坐标信息。

            【详细规则与约束】
            1. 沿路排布原则：档距段和连接线设备只排布在道路两侧一米的范围内。
            2. 电缆头摆放原则：起始电缆头设备应水平整齐摆放在站房的正下方，距离站房大概2米的位置，如果周围有建筑物,需要靠近建筑物一侧。
            3. 分支箱摆放原则：分支箱设备应摆放在楼栋长边附近的空地处,距离建筑物大概1米的位置。
            4. 接入点摆放原则：同一电缆头的接入点合并在同一像素点上，且应在建筑物中心位置处。
            5. 表箱摆放原则：表箱设备应与接入点方向水平或成正交折线。
            6. 线形优化：共线段需合并，线段应沿道路排布（横平竖直）；若无明显道路，则顺着建筑物边缘布线。
            7. 正交最短布线：连线拐点最少、总长最短，避免穿越建筑物、站房设备、河流。

            【输出格式示例】
            [
            {{'id': 'TFvUrGF_P1', 'points': [[100, 200], [120, 200], [120, 220], [100, 220], ...]}},
            {{'id': 'TFvUrGF_P2', 'points': [[300, 400], [320, 400], [320, 420], [300, 420], ...]}},
            ...
            ]

            【治理前后样例】
            1. 表箱治理前后
            治理前：{{"id": "TFvUrGF_P1", "points": [[40.723, 80.641], [40.69, 82.253], [46.601, 82.041], [46.534, 80.598]], "label": "表箱"}}
            治理后：{{"id": "TFvUrGF_P1", "points": [[20.845, 75.243], [21.974, 75.221], [21.903, 73.899], [20.845, 73.854]], "label": "表箱"}}
            2. 电缆头治理前后
            治理前: {{"id": "tf1Xp2mJdo", "points": [[60.527, 67.531], [60.494, 68.506], [61.461, 67.894], [60.799, 67.636]], "label": "电缆终端头起点"}}
            治理后: {{"id": "tf1Xp2mJdo", "points": [[63.341, 72.187], [63.331, 70.733], [64.296, 71.442]], "label": "电缆终端头起点"}}
            3. 分支箱治理前后
            治理前: {{"id": "g3Ar-fnV4Y", "points": [[49.772, 28.189], [49.735, 29.916], [51.315, 30.009], [51.388, 28.236]], "label": "分支箱"}}
            治理后: {{"id": "g3Ar-fnV4Y", "points": [[52.576, 32.23], [52.57, 33.11], [53.552, 33.086], [53.54, 32.254]], "label": "分支箱"}}
            4. 档距段/连接线治理前后
            治理前: {{"id": "IquNkEaXSU", "points": [[53.758, 13.148], [55.609, 13.148], [55.574, 13.627], [53.843, 13.583]], "label": "连接线"}}
            治理后: {{"id": "IquNkEaXSU", "points": [[77.655, 10.976], [78.279, 11.087], [78.301, 10.684], [77.721, 10.6]], "label": "连接线"}}
            5. 接入点治理前后
            治理前: {{"id": "CdRCzZLbxZ", "points": [[52.837, 13.062], [52.936, 13.313], [53.658, 13.817], [53.8, 13.547], [53.729, 13.062], [53.559, 12.864], [53.233, 12.882], [53.078, 12.9]], "label": "接入点"}}
            治理后: {{"id": "CdRCzZLbxZ", "points": [[59.12, 20.172], [59.361, 20.156], [59.503, 20.07], [59.639, 19.882], [59.67, 19.638], [59.67, 19.387], [59.54, 19.199], [59.429, 19.112], [59.281, 19.018], [59.169, 19.042], [59.04, 19.089], [58.916, 19.23], [58.823, 19.426], [58.805, 19.583], [58.817, 19.803], [58.873, 19.984], [58.972, 20.093]], "label": "接入点"}}

            【排布算法与流程说明】
            数据预处理：解析输入数据，校验字段完整性。
            设备分类：按type分组，分别处理。
            规则判断：依次应用排布规则，调整points坐标。
            冲突检测：检测设备重叠、越界等问题，自动修正。
            输出生成：按格式输出所有设备的id和points。

            【常见问题与处理建议】
            道路缺失：优先参考建筑物边缘布线。
            建筑物密集：设备优先靠近空地，避免重叠。
            河流阻隔：线路需绕行，避免穿越河流

【注意事项】
- 不要修改设备的id，只需调整points坐标。
- 严格按照上述格式输出，不要输出多余内容。
- 如遇特殊情况（如无道路），请优先参考建筑物边缘进行排布。
"""

# User prompt with actual data
user_prompt = f"""
【输入数据1 - 电网设备的标注坐标信息】：
{content}

【输入数据2 - 电网设备删除或者新增的设备信息】：
{content2}

说明: 输入数据1和输入数据2中的设备是有对应关系的, 设备的id相同表示对应。

请按照系统提示中的规则重新排布电网设备，输出优化后的设备坐标信息。
"""
# 记录开始时间
start_time = time.perf_counter()

client = OpenAI(
    # API key loaded from .env file
    api_key=os.environ.get("OPENAI_API_KEY"),
)
try:
    completion = client.chat.completions.create(
        model="o3",  # Using OpenAI's o3 model
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        max_completion_tokens=65536
    )
    
    # 获取响应
    response_content = completion.choices[0].message.content
    print(response_content)
    
    # 尝试解析JSON响应并进行可视化
    try:
        # 假设响应是JSON格式的设备列表
        if '[' in response_content:
            # 提取JSON部分，处理可能不完整的响应
            start_idx = response_content.find('[')
            
            # 如果有完整的结束括号
            if ']' in response_content:
                end_idx = response_content.rfind(']') + 1
                json_str = response_content[start_idx:end_idx]
            else:
                # 如果没有结束括号，尝试修复JSON
                json_str = response_content[start_idx:]
                # 移除最后一个不完整的条目
                last_comma = json_str.rfind(',')
                if last_comma > 0:
                    json_str = json_str[:last_comma] + '\n]'
                else:
                    json_str += ']'
            
            output_devices = json.loads(json_str)
            
    except Exception as viz_error:
        print(f"可视化过程中出现错误: {viz_error}")
        print("尝试保存原始响应到文件...")
        
        # 保存响应到文件以便分析
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        with open(f'response_{timestamp}.txt', 'w', encoding='utf-8') as f:
            f.write(response_content)
        print(f"原始响应已保存到: response_{timestamp}.txt")
        
except Exception as api_error:
    print(f"API调用错误: {api_error}")

# 记录结束时间并计算运行时间
end_time = time.perf_counter()
run_time = end_time - start_time
print(f"\n=== 脚本运行完成 ===")
print(f"总运行时间: {run_time:.2f} 秒")

