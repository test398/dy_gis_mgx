import base64
import os
from zai import ZhipuAiClient
from prompt import system_prompt, user_prompt


def beautification_pipeline_glm4v(image_path, image_data):
    """ 图像美化处理管道 """
    # 这里调用具体的美化处理逻辑
    with open(image_path, "rb") as f:
        img_base = base64.b64encode(f.read()).decode("utf-8")
    client = ZhipuAiClient(api_key=os.environ.get("ZHIPU_API_KEY"))  # 填写您自己的APIKey
    content1 = open(image_path[:-5] + '_zlq.json', 'r', encoding='utf-8').read()
    content2 = open(image_path[:-5] + '_zlh.json', 'r', encoding='utf-8').read()
    response = client.chat.completions.create(
        model="glm-4v-plus-0111",  # 填写需要调用的模型名称
        messages=[{"role": "system", "content": system_prompt}, 
            {"role": "user", "content": user_prompt.replace("&content&", content1).replace("&content2&", content2)},
        ]
    )
    print(response.choices[0].message.content)


    # 返回处理后的结果
    return {
        'output_data': image_data,  # 假设处理后数据与输入相同
        'input_tokens': 100,
        'output_tokens': 100
    }


img_path = r"D:\work\dy_gis_mgx\标注数据目录\治理前标注图片\images\0a6db9ae-22b9d507-d2ed-4527-9306-f6385b1264e9.png"

