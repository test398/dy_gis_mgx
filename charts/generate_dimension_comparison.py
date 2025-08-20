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

def generate_dimension_comparison(score_file, output_image='dimension_comparison.png'):
    """生成各维度评分对比图（使用换算后的数据）"""
    # 读取评分数据
    score_data = read_json_file(score_file)
    if not score_data:
        print("无法读取评分数据文件")
        return False

    # 提取各维度评分数据
    # 假设数据格式为: {"dimensions": [{"name": "架空线", "score": 0.82}, ...]}
    dimensions = []
    scores = []

    # 尝试不同的数据格式
    if isinstance(score_data, dict):
        # 格式1: 直接包含dimensions字段
        if 'dimensions' in score_data and isinstance(score_data['dimensions'], list):
            for item in score_data['dimensions']:
                if 'name' in item and 'score' in item:
                    dimensions.append(item['name'])
                    # 换算为0-10分 (原始是0-2分)
                    scores.append(item['score'] * 5)
        # 格式2: 直接包含各维度字段
        elif all(key in score_data for key in ['架空线', '电缆线路', '分支箱', '接入点', '计量箱']):
            dimensions = ['架空线', '电缆线路', '分支箱', '接入点', '计量箱']
            for dim in dimensions:
                # 换算为0-10分 (原始是0-2分)
                scores.append(score_data[dim] * 5)
    # 如果没有找到合适的数据格式，使用Markdown文件中提到的数据
    if not dimensions:
        print("未找到合适的各维度评分数据格式，使用示例数据")
        # 从Markdown文件中提取的示例数据
        dimensions = ['架空线', '电缆线路', '分支箱', '接入点', '计量箱']
        original_scores = [0.82, 1.24, 0.31, 0.45, 0.79]  # 原始0-2分
        # 换算为0-10分
        scores = [score * 5 for score in original_scores]

    # 创建对比图
    plt.figure(figsize=(12, 7))

    # 绘制柱状图
    bars = plt.bar(dimensions, scores, color='skyblue', edgecolor='black')

    # 添加每个柱子的数值标签
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{height:.2f}', ha='center', va='bottom')

    # 设置图表标题和坐标轴标签
    plt.title('各维度评分对比图 (0-10分)')
    plt.xlabel('评分维度')
    plt.ylabel('分数 (0-10)')
    plt.ylim(0, 10)  # 设置y轴范围为0-10
    plt.grid(True, linestyle='--', alpha=0.7, axis='y')

    # 保存图表
    plt.tight_layout()
    plt.savefig(output_image, dpi=300, bbox_inches='tight')
    print(f"各维度评分对比图已保存至: {output_image}")
    plt.close()

    return True

if __name__ == "__main__":
    # 输入文件路径（尝试从汇总报告中读取，如果不存在则使用示例数据）
    input_file =("/Users/bonckus/代码/dy_gis_mgx/GisData/resGIS_qwen/评分分析汇总报告.json")
    # 输出图像文件路径
    output_image = "/Users/bonckus/代码/dy_gis_mgx/charts/dimension_comparison.png"

    # 生成各维度评分对比图
    success = generate_dimension_comparison(input_file, output_image)
    if success:
        print("各维度评分对比图生成成功")
    else:
        print("各维度评分对比图生成失败")