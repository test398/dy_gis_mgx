import base64
import os
from zai import ZhipuAiClient

APIKEY = os.environ.get("ZHIPU_API_KEY")

img_path = r"D:\work\dy_gis_mgx\标注数据目录\治理前标注图片\images\0a6db9ae-22b9d507-d2ed-4527-9306-f6385b1264e9.png"
with open(img_path, "rb") as f:
    img_base = base64.b64encode(f.read()).decode("utf-8")
client = ZhipuAiClient(api_key=APIKEY)  # 填写您自己的APIKey
response = client.chat.completions.create(
    model="glm-4v-plus-0111",  # 填写需要调用的模型名称
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": img_base
                    }
                },
                {
                    "type": "text",
                    "text": "图中有什么"
                }
            ]
        },
        {
            "role": "assistant",
            "content": [
                {
                    "type": "text",
                    "text": (
                        "这是一幅描绘自然风景的画，展现了一片宁静的湖泊，湖水呈现出深浅不一的蓝绿色调。"
                        "湖边长着一棵盛开的樱花树，粉白色的花朵在阳光下显得格外鲜艳。树下有一位身穿蓝色衣服的人坐在船上，"
                        "似乎正在享受这美好的时光。\n\n"
                        "背景是连绵起伏的山脉，山体被绿色的植被覆盖，山顶则被云雾缭绕，增添了几分神秘感。"
                        "远处还可以看到一座小亭子，它坐落在湖边的岩石上，与周围的自然环境和谐相融。\n\n"
                        "整个画面给人一种宁静、和谐的感觉，仿佛置身于一个世外桃源之中。"
                    )
                }
            ]
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "https://cdn.bigmodel.cn/xxxxxxx.jpeg"
                    }
                },
                {
                    "type": "text",
                    "text": "这个图与上面图有什么不一样"
                }
            ]
        },
        {
            "role": "assistant",
            "content": [
                {
                    "type": "text",
                    "text": (
                        "第一张图和第二张图在画面内容、构图、色彩等方面都有很大的不同，形成鲜明的对比。\n\n"
                        "1.第一张图是风景画，主要描绘了自然风景，如樱花树、湖泊、山脉等，色彩丰富，充满春天的气息，"
                        "而第二张图是描绘长城在冬季的风景照片，长城在白雪覆盖的山脉中蜿蜒盘旋，整体色调偏冷，"
                        "给人一种寒冷、宁静的感觉。\n\n"
                        "2.构图上，第一张图采用对称式构图，以樱花树为中心，两侧的景物相互呼应，形成平衡和谐的画面效果，"
                        "第二张图则采用对角线构图，长城作为视觉引导线，引导观众的视线穿越整个画面，增加画面的深度和动态感。\n\n"
                        "整体来看，这两张图在画面内容、色彩、构图和氛围上都呈现出明显的对比，一张是充满生机和色彩的春日风景画，"
                        "另一张是宁静而神秘的冬日长城风景照。"
                    )
                }
            ]
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "https://cdn.bigmodel.cn/xxxxxxx.jpeg"
                    }
                },
                {
                    "type": "text",
                    "text": "这个图与上一张图有什么区别"
                }
            ]
        }
    ]
)
print(response.choices[0].message.content)