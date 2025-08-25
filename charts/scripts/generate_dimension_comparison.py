import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
from collections import defaultdict

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def load_json_data(file_path):
    """加载JSON数据"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"成功加载JSON文件: {file_path}")
        return data
    except Exception as e:
        print(f"加载JSON文件失败: {e}")
        return None

def extract_dimension_scores(item, dimension_scores=None, parent_path=""):
    """递归提取各维度评分"""
    if dimension_scores is None:
        dimension_scores = defaultdict(list)
    
    # 获取当前项目信息
    name = item.get('name', '')
    score = item.get('score')
    
    # 构建完整路径
    current_path = f"{parent_path}/{name}" if parent_path else name
    
    # 如果有评分，记录到对应维度
    if score is not None:
        try:
            score_value = float(score)
            # 将0-2分的评分转换为0-10分
            normalized_score = (score_value / 2.0) * 10.0
            dimension_scores[current_path].append(normalized_score)
        except (ValueError, TypeError):
            pass
    
    # 递归处理子项
    if 'children' in item and isinstance(item['children'], list):
        for child in item['children']:
            extract_dimension_scores(child, dimension_scores, current_path)
    
    return dimension_scores

def process_all_data(data):
    """处理所有数据，提取维度评分"""
    all_dimension_scores = defaultdict(list)
    
    if isinstance(data, list):
        for i, item in enumerate(data):
            if i % 10 == 0:  # 每处理10个项目打印一次进度
                print(f"处理进度: {i+1}/{len(data)}")
            
            dimension_scores = extract_dimension_scores(item)
            
            # 合并到总的维度评分中
            for dimension, scores in dimension_scores.items():
                all_dimension_scores[dimension].extend(scores)
    
    elif isinstance(data, dict):
        dimension_scores = extract_dimension_scores(data)
        all_dimension_scores.update(dimension_scores)
    
    return all_dimension_scores

def filter_main_dimensions(dimension_scores, min_samples=5):
    """筛选主要维度（有足够样本的维度）"""
    filtered_dimensions = {}
    
    for dimension, scores in dimension_scores.items():
        if len(scores) >= min_samples:
            filtered_dimensions[dimension] = scores
    
    # 按维度名称排序
    sorted_dimensions = dict(sorted(filtered_dimensions.items()))
    
    print(f"\n筛选结果:")
    print(f"原始维度数: {len(dimension_scores)}")
    print(f"筛选后维度数: {len(sorted_dimensions)}")
    
    return sorted_dimensions

def generate_dimension_comparison_chart(dimension_scores, output_path, chart_type='box'):
    """生成维度对比图表"""
    if not dimension_scores:
        print("没有维度数据，无法生成图表")
        return False
    
    # 准备数据
    dimensions = list(dimension_scores.keys())
    scores_data = list(dimension_scores.values())
    
    # 计算统计信息
    stats = []
    for dim, scores in dimension_scores.items():
        stats.append({
            'dimension': dim,
            'mean': np.mean(scores),
            'std': np.std(scores),
            'min': np.min(scores),
            'max': np.max(scores),
            'count': len(scores)
        })
    
    if chart_type == 'box':
        # 箱线图
        plt.figure(figsize=(15, 8))
        
        box_plot = plt.boxplot(scores_data, labels=dimensions, patch_artist=True)
        
        # 设置颜色
        colors = plt.cm.Set3(np.linspace(0, 1, len(dimensions)))
        for patch, color in zip(box_plot['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        
        plt.title('各维度评分分布对比（箱线图）', fontsize=16, fontweight='bold')
        plt.xlabel('评分维度', fontsize=12)
        plt.ylabel('评分 (0-10分)', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.grid(True, alpha=0.3)
        
    elif chart_type == 'violin':
        # 小提琴图
        plt.figure(figsize=(15, 8))
        
        violin_plot = plt.violinplot(scores_data, positions=range(1, len(dimensions)+1))
        
        # 设置颜色
        colors = plt.cm.Set3(np.linspace(0, 1, len(dimensions)))
        for pc, color in zip(violin_plot['bodies'], colors):
            pc.set_facecolor(color)
            pc.set_alpha(0.7)
        
        plt.title('各维度评分分布对比（小提琴图）', fontsize=16, fontweight='bold')
        plt.xlabel('评分维度', fontsize=12)
        plt.ylabel('评分 (0-10分)', fontsize=12)
        plt.xticks(range(1, len(dimensions)+1), dimensions, rotation=45, ha='right')
        plt.grid(True, alpha=0.3)
        
    elif chart_type == 'bar':
        # 柱状图（显示平均分）
        plt.figure(figsize=(15, 8))
        
        means = [np.mean(scores) for scores in scores_data]
        stds = [np.std(scores) for scores in scores_data]
        
        bars = plt.bar(range(len(dimensions)), means, yerr=stds, 
                      capsize=5, alpha=0.7, color=plt.cm.Set3(np.linspace(0, 1, len(dimensions))))
        
        plt.title('各维度平均评分对比', fontsize=16, fontweight='bold')
        plt.xlabel('评分维度', fontsize=12)
        plt.ylabel('平均评分 (0-10分)', fontsize=12)
        plt.xticks(range(len(dimensions)), dimensions, rotation=45, ha='right')
        plt.grid(True, alpha=0.3, axis='y')
        
        # 在柱子上显示数值
        for i, (bar, mean, std) in enumerate(zip(bars, means, stds)):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + std + 0.1,
                    f'{mean:.1f}', ha='center', va='bottom', fontsize=10)
    
    plt.tight_layout()
    
    # 保存图表
    try:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"图表已保存: {output_path}")
        return True
    except Exception as e:
        print(f"保存图表失败: {e}")
        plt.close()
        return False

def generate_statistics_report(dimension_scores, output_path):
    """生成统计报告"""
    try:
        # 计算统计信息
        stats_data = []
        for dimension, scores in dimension_scores.items():
            stats_data.append({
                '维度': dimension,
                '样本数': len(scores),
                '平均分': round(np.mean(scores), 2),
                '标准差': round(np.std(scores), 2),
                '最小值': round(np.min(scores), 2),
                '最大值': round(np.max(scores), 2),
                '中位数': round(np.median(scores), 2)
            })
        
        # 创建DataFrame并保存
        df = pd.DataFrame(stats_data)
        df = df.sort_values('平均分', ascending=False)
        
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"统计报告已保存: {output_path}")
        
        # 打印前10个维度的统计信息
        print("\n=== 评分最高的10个维度 ===")
        print(df.head(10).to_string(index=False))
        
        return True
        
    except Exception as e:
        print(f"生成统计报告失败: {e}")
        return False

def generate_heatmap(dimension_scores, output_path, max_dimensions=20):
    """生成热力图"""
    try:
        # 选择评分最高的维度
        sorted_dims = sorted(dimension_scores.items(), 
                           key=lambda x: np.mean(x[1]), reverse=True)
        
        selected_dims = dict(sorted_dims[:max_dimensions])
        
        # 准备数据矩阵
        dimensions = list(selected_dims.keys())
        max_samples = max(len(scores) for scores in selected_dims.values())
        
        # 创建数据矩阵（维度 x 样本）
        data_matrix = np.full((len(dimensions), max_samples), np.nan)
        
        for i, (dim, scores) in enumerate(selected_dims.items()):
            data_matrix[i, :len(scores)] = scores
        
        # 生成热力图
        plt.figure(figsize=(16, 10))
        
        # 只显示有数据的部分
        valid_samples = min(50, max_samples)  # 最多显示50个样本
        plot_data = data_matrix[:, :valid_samples]
        
        im = plt.imshow(plot_data, cmap='RdYlBu_r', aspect='auto', vmin=0, vmax=10)
        
        plt.colorbar(im, label='评分 (0-10分)')
        plt.title(f'各维度评分热力图（前{max_dimensions}个维度）', fontsize=16, fontweight='bold')
        plt.xlabel('样本编号', fontsize=12)
        plt.ylabel('评分维度', fontsize=12)
        
        # 设置y轴标签
        plt.yticks(range(len(dimensions)), 
                  [dim.split('/')[-1] if '/' in dim else dim for dim in dimensions])
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"热力图已保存: {output_path}")
        return True
        
    except Exception as e:
        print(f"生成热力图失败: {e}")
        plt.close()
        return False

def main():
    # 配置文件路径
    json_file_path = "../data/人工打分结果.json"
    output_dir = "../images"
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 检查输入文件
    if not os.path.exists(json_file_path):
        print(f"输入文件不存在: {json_file_path}")
        return
    
    print("开始处理维度对比分析...")
    
    # 1. 加载数据
    data = load_json_data(json_file_path)
    if data is None:
        return
    
    # 2. 提取维度评分
    print("\n提取维度评分...")
    dimension_scores = process_all_data(data)
    
    # 3. 筛选主要维度
    print("\n筛选主要维度...")
    filtered_dimensions = filter_main_dimensions(dimension_scores, min_samples=5)
    
    if not filtered_dimensions:
        print("没有找到足够的维度数据")
        return
    
    # 4. 生成不同类型的图表
    print("\n生成图表...")
    
    # 箱线图
    box_chart_path = os.path.join(output_dir, "dimension_comparison_boxplot.png")
    generate_dimension_comparison_chart(filtered_dimensions, box_chart_path, 'box')
    
    # 柱状图
    bar_chart_path = os.path.join(output_dir, "dimension_comparison_barplot.png")
    generate_dimension_comparison_chart(filtered_dimensions, bar_chart_path, 'bar')
    
    # 小提琴图（如果维度不太多）
    if len(filtered_dimensions) <= 15:
        violin_chart_path = os.path.join(output_dir, "dimension_comparison_violin.png")
        generate_dimension_comparison_chart(filtered_dimensions, violin_chart_path, 'violin')
    
    # 热力图
    heatmap_path = os.path.join(output_dir, "dimension_heatmap.png")
    generate_heatmap(filtered_dimensions, heatmap_path)
    
    # 5. 生成统计报告
    print("\n生成统计报告...")
    stats_report_path = os.path.join(output_dir.replace('images', 'data'), "dimension_statistics.csv")
    os.makedirs(os.path.dirname(stats_report_path), exist_ok=True)
    generate_statistics_report(filtered_dimensions, stats_report_path)
    
    print("\n维度对比分析完成！")
    print(f"共处理 {len(filtered_dimensions)} 个维度")
    print(f"图表保存在: {output_dir}")

if __name__ == "__main__":
    main()