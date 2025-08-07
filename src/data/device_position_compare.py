import json
import matplotlib.pyplot as plt
import os

def compare_device_positions(file1, file2, out_img_path='设备位置对比_auto.png'):
    """
    对比两个json文件中的设备位置，并生成对比图片。
    Args:
        file1: 原始标注json路径
        file2: 治理后json路径
        out_img_path: 输出图片路径
    """
    def load_points(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        points = []
        for ann in data.get('annotations', []):
            pts = ann.get('points', [])
            if pts:
                if len(pts) == 1:
                    points.append(pts[0])
                else:
                    x = sum(p[0] for p in pts) / len(pts)
                    y = sum(p[1] for p in pts) / len(pts)
                    points.append([x, y])
        return points

    points1 = load_points(file1)
    points2 = load_points(file2)

    plt.figure(figsize=(8, 8))
    if points1:
        x1, y1 = zip(*points1)
        plt.scatter(x1, y1, c='red', label='原始标注', marker='o')
    if points2:
        x2, y2 = zip(*points2)
        plt.scatter(x2, y2, c='blue', label='治理后', marker='x')

    plt.legend()
    plt.title('设备位置对比')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.gca().set_aspect('equal')
    plt.tight_layout()
    plt.savefig(out_img_path, dpi=200, bbox_inches='tight')
    plt.close()
    print(f"对比图片已保存为 {out_img_path}") 