from json_to_png import get_label_image
import re
import json
import requests
import json
import base64

api = 'Bearer sk-OyJ2Hpcbb8H8ce1XowlpgTt3yr6iJGDufkgOZZX8MFRrqTHz'

prompt_jiliangxiang = '''我将给你三张图片，这三张图片都是带有计量箱和接入点的分布图，其中蓝色圆点为计量箱，红色圆点为接入点。请帮我根据前面两张图片的评分与下面的参考评分规则，对第三张图片计量箱的布置进行打分。

## 输出要求
- 回答必须以以下固定格式开头：  
  **评分：X/15** （其中 X 为具体分数）。  
- 在分数后，请说明具体理由。  

## 评分范围
打分范围为 **0–15**。  
- 第一张图片的参考分数为 **15**  
- 第二张图片的参考分数为 **5**  
整体上，如果布置合理，应该优先给出更高的分数。  

## 参考评分规则（以宽松、整体印象为主）
- **11–15分：**  
  完全符合要求，计量箱位于建筑物上，紧邻接入点，整齐排列，无任何空间冲突。  

- **6–10分：**  
  基本符合，但存在少量问题，计量箱之间间距偏大，部分未在建筑上，计量箱与接入点轻微重叠。  

- **0–5分：**  
  明显不合理，计量箱不在建筑上，远离接入点，分布杂乱，与设备存在冲突或遮挡。  

## 注意事项
请客观地给分，只要整体合理，就应靠近高分。'''

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def get_gen_str(base64_image, base64_image1, base64_image2):
    """获取模型生成的字符串，运行多次"""
    num_runs = 1
    outputs = []
   
    for _ in range(num_runs):
        try:

            url = "https://api.chatanywhere.tech/v1/chat/completions"
            payload = json.dumps({
            "model": "gpt-5",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        { 
                            "type": "text", 
                            "text": prompt_jiliangxiang
                        },
                        {
                            "type": "image_url",
                            "image_url":{ 
                                "url":f"data:image/png;base64,{base64_image}"
                            }
                        },
                        {
                            "type": "image_url",
                            "image_url":{ 
                                "url":f"data:image/png;base64,{base64_image1}"
                            }
                        },
                        {
                            "type": "image_url",
                            "image_url":{ 
                                "url":f"data:image/png;base64,{base64_image2}"
                            }
                        },
                    ],
                }
            ]
            })
            headers = {
            'Authorization': api,
            'Content-Type': 'application/json'
            }

            response = requests.request("POST", url, headers=headers, data=payload)
            response = response.json()
            gen_str = response["choices"][0]["message"]["content"]
            print(f"Generated string: {gen_str}")
            outputs.append(gen_str)
        except Exception as e:
            outputs.append(f"Error: {str(e)}")
            print(f"Error: {str(e)}")
    
    return outputs

def get_scores(example_15_path, example_5_path, to_score_path):
    # 关于15分的例子的分布图
    base64_image = encode_image(example_15_path)

    # 关于5分例子的分布图
    base64_image1 = encode_image(example_5_path)

    # 目前处理的分布图
    base64_image2 = encode_image(to_score_path)

    responses = get_gen_str(base64_image, base64_image1, base64_image2)

    def parser(responses):
        scores = []
        for response in responses:
            match = re.search(r"评分：(\d+)/15", response)
            if match:
                scores.append(int(match.group(1)))
            else:
                print("自动评分出错，未找到评分信息")
                scores.append(None)
        return scores
    
    return parser(responses)


if __name__ == "__main__":
    example_15_path = "15_distribution.png"
    example_5_path = "5_distribution.png"
    to_score_path = "102320e324ff80808166f86cba016710228b8a7c75_distribution.png"

    print("计量箱最终分数:", get_scores(example_15_path, example_5_path, to_score_path))
    