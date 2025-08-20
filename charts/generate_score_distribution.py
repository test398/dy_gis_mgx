import json
import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# 设置中文字体，确保中文正常显示
plt.rcParams["font.family"] = ["Arial Unicode MS", "sans-serif"]
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

def read_json_file(file_path):
    """读取JSON文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"读取文件错误: {file_path}, 错误信息: {str(e)}")
        return None

def generate_score_distribution(score_file, output_image='score_distribution.png'):
    """生成分数分布直方图"""
    # 读取分数数据
    score_data = read_json_file(score_file)
    if not score_data:
        print("无法读取分数数据文件")
        return False

    # 提取converted_score数据
    converted_scores = []
    for item in score_data:
        if 'converted_score' in item:
            converted_scores.append(item['converted_score'])

    if not converted_scores:
        print("未找到converted_score数据")
        return False

    # 计算统计信息
    scores_mean = np.mean(converted_scores)
    scores_median = np.median(converted_scores)
    scores_min = np.min(converted_scores)
    scores_max = np.max(converted_scores)

    print(f"分数统计信息:")
    print(f"均值: {scores_mean:.2f}")
    print(f"中位数: {scores_median:.2f}")
    print(f"最小值: {scores_min:.2f}")
    print(f"最大值: {scores_max:.2f}")

    # 创建直方图
    plt.figure(figsize=(10, 6))
    n, bins, patches = plt.hist(converted_scores, bins=20, range=(0, 10), 
                               density=False, alpha=0.7, color='skyblue', edgecolor='black')

    # 添加统计信息文本
    stats_text = f"均值: {scores_mean:.2f}\n中位数: {scores_median:.2f}\n最小值: {scores_min:.2f}\n最大值: {scores_max:.2f}"
    plt.text(0.05, 0.95, stats_text, transform=plt.gca().transAxes, 
             verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    # 设置图表标题和坐标轴标签
    plt.title('分数分布直方图')
    plt.xlabel('分数 (0-10)')
    plt.ylabel('样本数量')
    plt.grid(True, linestyle='--', alpha=0.7)

    # 保存图表
    plt.tight_layout()
    plt.savefig(output_image, dpi=300, bbox_inches='tight')
    print(f"直方图已保存至: {output_image}")
    plt.close()

    return True

if __name__ == "__main__":
    # 输入文件路径
    input_file = "/Users/bonckus/代码/dy_gis_mgx/charts/converted_scores_10point_v2.json"
    # 输出图像文件路径
    output_image = "/Users/bonckus/代码/dy_gis_mgx/charts/score_distribution.png"

    # 生成直方图
    success = generate_score_distribution(input_file, output_image)
    if success:
        print("分数分布直方图生成成功")
    else:
        print("分数分布直方图生成失败")