import json
import cv2
import random
import numpy as np

def get_label_image(input_json_path, input_image_path, output_image_path):
    # 读取 JSON
    with open(input_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 读取原图
    img = cv2.imread(input_image_path)  # <-- 换成你的原图路径

    # 给每个 label 随机一个颜色
    colors = {}
    for ann in data["annotations"]:
        label = ann["label"]
        if label not in colors:
            colors[label] = [random.randint(0, 255) for _ in range(3)]

    # 绘制标注
    for ann in data["annotations"]:
        
        label = ann["label"]
        if label == "计量箱":
            colors[label] = (255, 0, 0)  # 红色
        elif label == "接入点":
            colors[label] = (0, 0, 255)  # 蓝色
        else:
            continue
        pts = ann["points"]
        color = colors[label]

        x, y = map(int, pts[0])
        if label == "计量箱":
            cv2.circle(img, (x, y-8), 8, color, -1)
        elif label == "接入点":
            cv2.circle(img, (x, y-8), 6, color, -1)

    # 保存结果
    cv2.imwrite(output_image_path, img)
