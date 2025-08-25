import json
import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import pearsonr
import jsonlines
import wandb
from collections import defaultdict

# 设置中文字体，使用更通用的配置
plt.rcParams["font.family"] = ["Arial Unicode MS", "sans-serif"]
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 初始化WandB
def init_wandb():
    try:
        wandb.init(
            project="gis-beautification-normalized",
            name="normalized-chart-generation",
            config={
                "version": "2.0",
                "description": "电网台区美化治理标准化评分图表生成"
            }
        )
        print("WandB初始化成功")
        return True
    except Exception as e:
        print(f"WandB初始化失败: {str(e)}")
        return False

def read_json_file(file_path):
    """读取JSON文件，支持大文件和复杂结构"""
    try:
        # 尝试常规JSON解析
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        # 尝试使用jsonlines解析每行一个JSON的格式
        try:
            data = []
            with jsonlines.open(file_path) as reader:
                for line in reader:
                    data.append(line)
            return data
        except Exception as e:
            print(f"无法解析文件: {file_path}, 错误信息: {str(e)}")
            # 尝试读取文件的一部分进行解析
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read(50000)  # 读取前50000个字符
                    # 尝试找到完整的JSON对象
                    if content.strip().startswith('['):
                        # 数组格式，尝试找到第一个完整对象
                        bracket_count = 0
                        for i, char in enumerate(content):
                            if char == '{':
                                bracket_count += 1
                            elif char == '}':
                                bracket_count -= 1
                                if bracket_count == 0:
                                    # 找到第一个完整对象
                                    sample_json = content[1:i+1]  # 去掉开头的[
                                    return [json.loads(sample_json)]
                    return json.loads(content)
            except Exception as inner_e:
                print(f"部分解析也失败: {str(inner_e)}")
                return None
    except Exception as e:
        print(f"读取文件错误: {file_path}, 错误信息: {str(e)}")
        return None

def find_sample_files(directory, pattern='*.json'):
    """查找目录中匹配模式的文件"""
    import glob
    return glob.glob(os.path.join(directory, pattern))

def extract_sample_data(score_file, sample_count=None):
    """从评分文件或目录中提取样本数据"""
    if os.path.isdir(score_file):
        # 如果是目录，查找JSON文件
        json_files = find_sample_files(score_file)
        samples = []
        end_idx = sample_count if sample_count is not None else len(json_files)
        for file in json_files[:end_idx]:
            data = read_json_file(file)
            if data:
                if isinstance(data, dict):
                    data['file_name'] = os.path.basename(file)
                samples.append(data)
        return samples
    else:
        # 如果是文件，直接读取
        data = read_json_file(score_file)
        if data:
            if isinstance(data, list):
                # 如果是数组，取前sample_count个
                end_idx = sample_count if sample_count is not None else len(data)
                return data[:end_idx]
            else:
                # 如果是单个对象，返回包含它的数组
                return [data]
        return []

def normalize_score(score, original_range=(0, 2), target_range=(0, 10)):
    """标准化评分到目标范围"""
    if score is None:
        return None
    
    try:
        score_val = float(score)
        # 线性映射到目标范围
        original_min, original_max = original_range
        target_min, target_max = target_range
        
        if original_max == original_min:
            return target_min
        
        normalized = ((score_val - original_min) / (original_max - original_min)) * (target_max - target_min) + target_min
        return max(target_min, min(target_max, normalized))  # 确保在目标范围内
    except (ValueError, TypeError):
        return None

def extract_normalized_scores_from_data(data):
    """从数据中提取并标准化评分信息"""
    scores = {}
    
    def extract_recursive(item, prefix=""):
        if isinstance(item, dict):
            # 检查是否有评分信息
            if 'score' in item:
                name = item.get('name', prefix)
                original_score = item['score']
                normalized_score = normalize_score(original_score, (0, 2), (0, 10))
                if normalized_score is not None:
                    scores[name] = {
                        'original': original_score,
                        'normalized': normalized_score
                    }
            
            # 递归处理子项
            if 'children' in item and isinstance(item['children'], list):
                for child in item['children']:
                    child_prefix = f"{prefix}-{item.get('name', '')}" if prefix else item.get('name', '')
                    extract_recursive(child, child_prefix)
            
            # 处理其他可能的嵌套结构
            for key, value in item.items():
                if key not in ['score', 'name', 'children'] and isinstance(value, (dict, list)):
                    extract_recursive(value, f"{prefix}-{key}" if prefix else key)
        
        elif isinstance(item, list):
            for i, sub_item in enumerate(item):
                extract_recursive(sub_item, f"{prefix}[{i}]" if prefix else f"item[{i}]")
    
    extract_recursive(data)
    return scores

def calculate_normalized_total_score(scores):
    """计算标准化总分"""
    normalized_scores = [score_info['normalized'] for score_info in scores.values() if score_info['normalized'] is not None]
    return sum(normalized_scores) if normalized_scores else 0

def generate_normalized_comparison_data(machine_score_file, human_score_file):
    """生成标准化对比数据"""
    print("读取机器评分数据...")
    machine_data = extract_sample_data(machine_score_file, 100)  # 增加样本数量
    
    print("读取人工评分数据...")
    human_data = extract_sample_data(human_score_file, 100)
    
    if not machine_data or not human_data:
        print("无法读取评分数据")
        return None
    
    print(f"机器评分样本数: {len(machine_data)}")
    print(f"人工评分样本数: {len(human_data)}")
    
    comparison_data = []
    
    # 处理机器评分数据
    for i, data in enumerate(machine_data[:min(len(machine_data), 50)]):
        scores = extract_normalized_scores_from_data(data)
        total_score = calculate_normalized_total_score(scores)
        
        comparison_data.append({
            'id': f'sample_{i+1}',
            'machine_score_normalized': total_score,
            'machine_details_normalized': {k: v['normalized'] for k, v in scores.items()},
            'machine_details_original': {k: v['original'] for k, v in scores.items()},
            'human_score_normalized': None,
            'human_details_normalized': {},
            'human_details_original': {}
        })
    
    # 处理人工评分数据并尝试匹配
    for i, data in enumerate(human_data[:min(len(human_data), len(comparison_data))]):
        scores = extract_normalized_scores_from_data(data)
        total_score = calculate_normalized_total_score(scores)
        
        if i < len(comparison_data):
            comparison_data[i]['human_score_normalized'] = total_score
            comparison_data[i]['human_details_normalized'] = {k: v['normalized'] for k, v in scores.items()}
            comparison_data[i]['human_details_original'] = {k: v['original'] for k, v in scores.items()}
    
    # 过滤掉没有对应人工评分的数据
    comparison_data = [item for item in comparison_data if item['human_score_normalized'] is not None]
    
    print(f"成功匹配的样本数: {len(comparison_data)}")
    return comparison_data

def generate_normalized_charts(comparison_data, output_dir='../images'):
    """生成标准化对比图表"""
    if not comparison_data:
        print("没有对比数据，无法生成图表")
        return
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 提取标准化数据
    machine_scores = [item['machine_score_normalized'] for item in comparison_data]
    human_scores = [item['human_score_normalized'] for item in comparison_data]
    sample_ids = [item['id'] for item in comparison_data]
    
    # 1. 标准化散点图对比
    plt.figure(figsize=(12, 8))
    plt.scatter(machine_scores, human_scores, alpha=0.6, s=60, c='blue', edgecolors='black', linewidth=0.5)
    
    # 添加对角线（理想情况下机器分数=人工分数）
    min_score = 0
    max_score = 10
    plt.plot([min_score, max_score], [min_score, max_score], 'r--', alpha=0.8, linewidth=2, label='理想对角线')
    
    # 计算相关系数
    if len(machine_scores) > 1:
        correlation, p_value = pearsonr(machine_scores, human_scores)
        plt.title(f'标准化评分对比 (0-10分)\n相关系数: {correlation:.3f} (p={p_value:.3f})', fontsize=14, fontweight='bold')
    else:
        plt.title('标准化评分对比 (0-10分)', fontsize=14, fontweight='bold')
    
    plt.xlabel('机器评分 (标准化)', fontsize=12)
    plt.ylabel('人工评分 (标准化)', fontsize=12)
    plt.xlim(0, 10)
    plt.ylim(0, 10)
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    scatter_path = os.path.join(output_dir, 'normalized_scatter_comparison.png')
    plt.savefig(scatter_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"标准化散点图已保存: {scatter_path}")
    
    # 2. 标准化柱状图对比
    plt.figure(figsize=(14, 8))
    x = np.arange(len(sample_ids))
    width = 0.35
    
    bars1 = plt.bar(x - width/2, machine_scores, width, label='机器评分', alpha=0.8, color='skyblue')
    bars2 = plt.bar(x + width/2, human_scores, width, label='人工评分', alpha=0.8, color='lightcoral')
    
    plt.xlabel('样本', fontsize=12)
    plt.ylabel('标准化评分 (0-10分)', fontsize=12)
    plt.title('标准化评分对比', fontsize=14, fontweight='bold')
    plt.xticks(x, [f'S{i+1}' for i in range(len(sample_ids))], rotation=45)
    plt.ylim(0, 10)
    plt.legend()
    plt.grid(True, alpha=0.3, axis='y')
    
    # 在柱子上显示数值
    for bar in bars1:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{height:.1f}', ha='center', va='bottom', fontsize=8)
    
    for bar in bars2:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{height:.1f}', ha='center', va='bottom', fontsize=8)
    
    bar_path = os.path.join(output_dir, 'normalized_score_comparison.png')
    plt.savefig(bar_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"标准化柱状图已保存: {bar_path}")
    
    # 3. 标准化分布对比
    plt.figure(figsize=(12, 8))
    
    # 创建子图
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # 左图：直方图
    ax1.hist(machine_scores, bins=15, alpha=0.7, label='机器评分', density=True, color='skyblue', edgecolor='black')
    ax1.hist(human_scores, bins=15, alpha=0.7, label='人工评分', density=True, color='lightcoral', edgecolor='black')
    ax1.set_xlabel('标准化评分 (0-10分)', fontsize=12)
    ax1.set_ylabel('密度', fontsize=12)
    ax1.set_title('评分分布对比', fontsize=14, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim(0, 10)
    
    # 右图：箱线图
    box_data = [machine_scores, human_scores]
    box_plot = ax2.boxplot(box_data, labels=['机器评分', '人工评分'], patch_artist=True)
    box_plot['boxes'][0].set_facecolor('skyblue')
    box_plot['boxes'][1].set_facecolor('lightcoral')
    ax2.set_ylabel('标准化评分 (0-10分)', fontsize=12)
    ax2.set_title('评分分布箱线图', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim(0, 10)
    
    plt.tight_layout()
    dist_path = os.path.join(output_dir, 'normalized_score_distribution.png')
    plt.savefig(dist_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"标准化分布图已保存: {dist_path}")
    
    # 4. 评分改进分析
    differences = [h - m for h, m in zip(human_scores, machine_scores)]
    
    plt.figure(figsize=(12, 8))
    colors = ['green' if d > 0 else 'red' if d < 0 else 'gray' for d in differences]
    bars = plt.bar(range(len(differences)), differences, alpha=0.7, color=colors)
    plt.axhline(y=0, color='black', linestyle='-', alpha=0.8, linewidth=1)
    
    plt.xlabel('样本', fontsize=12)
    plt.ylabel('评分差异 (人工 - 机器)', fontsize=12)
    plt.title('标准化评分差异分析', fontsize=14, fontweight='bold')
    plt.xticks(range(len(sample_ids)), [f'S{i+1}' for i in range(len(sample_ids))], rotation=45)
    plt.grid(True, alpha=0.3)
    
    # 添加统计信息
    mean_diff = np.mean(differences)
    std_diff = np.std(differences)
    plt.text(0.02, 0.98, f'平均差异: {mean_diff:.2f}\n标准差: {std_diff:.2f}', 
             transform=plt.gca().transAxes, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    diff_path = os.path.join(output_dir, 'normalized_score_difference.png')
    plt.savefig(diff_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"标准化差异图已保存: {diff_path}")
    
    return {
        'normalized_scatter_plot': scatter_path,
        'normalized_bar_chart': bar_path,
        'normalized_distribution': dist_path,
        'normalized_difference': diff_path
    }

def generate_detailed_dimension_analysis(comparison_data, output_dir):
    """生成详细的维度分析"""
    if not comparison_data:
        return
    
    # 收集所有维度的评分
    all_dimensions = set()
    for item in comparison_data:
        all_dimensions.update(item['machine_details_normalized'].keys())
        all_dimensions.update(item['human_details_normalized'].keys())
    
    all_dimensions = sorted(list(all_dimensions))
    
    if len(all_dimensions) > 20:  # 如果维度太多，只选择前20个
        all_dimensions = all_dimensions[:20]
    
    # 为每个维度收集数据
    dimension_data = defaultdict(lambda: {'machine': [], 'human': []})
    
    for item in comparison_data:
        for dim in all_dimensions:
            machine_score = item['machine_details_normalized'].get(dim, 0)
            human_score = item['human_details_normalized'].get(dim, 0)
            
            dimension_data[dim]['machine'].append(machine_score)
            dimension_data[dim]['human'].append(human_score)
    
    # 生成维度对比热力图
    plt.figure(figsize=(16, 10))
    
    # 准备热力图数据
    machine_matrix = []
    human_matrix = []
    
    for dim in all_dimensions:
        machine_matrix.append(dimension_data[dim]['machine'])
        human_matrix.append(dimension_data[dim]['human'])
    
    # 创建子图
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12))
    
    # 机器评分热力图
    im1 = ax1.imshow(machine_matrix, cmap='RdYlBu_r', aspect='auto', vmin=0, vmax=10)
    ax1.set_title('机器评分各维度热力图 (标准化)', fontsize=14, fontweight='bold')
    ax1.set_ylabel('评分维度', fontsize=12)
    ax1.set_yticks(range(len(all_dimensions)))
    ax1.set_yticklabels([dim.split('-')[-1] if '-' in dim else dim for dim in all_dimensions])
    
    # 人工评分热力图
    im2 = ax2.imshow(human_matrix, cmap='RdYlBu_r', aspect='auto', vmin=0, vmax=10)
    ax2.set_title('人工评分各维度热力图 (标准化)', fontsize=14, fontweight='bold')
    ax2.set_xlabel('样本编号', fontsize=12)
    ax2.set_ylabel('评分维度', fontsize=12)
    ax2.set_yticks(range(len(all_dimensions)))
    ax2.set_yticklabels([dim.split('-')[-1] if '-' in dim else dim for dim in all_dimensions])
    
    # 添加颜色条
    plt.colorbar(im1, ax=ax1, label='评分 (0-10分)')
    plt.colorbar(im2, ax=ax2, label='评分 (0-10分)')
    
    plt.tight_layout()
    heatmap_path = os.path.join(output_dir, 'normalized_dimension_heatmap.png')
    plt.savefig(heatmap_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"维度热力图已保存: {heatmap_path}")
    
    return heatmap_path

def generate_normalized_analysis_report(comparison_data, output_dir):
    """生成标准化分析报告"""
    if not comparison_data:
        return
    
    machine_scores = [item['machine_score_normalized'] for item in comparison_data]
    human_scores = [item['human_score_normalized'] for item in comparison_data]
    
    # 计算统计指标
    machine_mean = np.mean(machine_scores)
    human_mean = np.mean(human_scores)
    machine_std = np.std(machine_scores)
    human_std = np.std(human_scores)
    
    differences = [h - m for h, m in zip(human_scores, machine_scores)]
    mean_diff = np.mean(differences)
    std_diff = np.std(differences)
    
    correlation, p_value = pearsonr(machine_scores, human_scores) if len(machine_scores) > 1 else (0, 1)
    
    # 生成报告
    report = f"""
# 标准化评分对比分析报告

## 数据标准化说明
- 原始评分范围：0-2分
- 标准化范围：0-10分
- 标准化方法：线性映射

## 基本统计

### 样本数量
- 总样本数: {len(comparison_data)}

### 机器评分统计 (标准化)
- 平均分: {machine_mean:.2f}/10
- 标准差: {machine_std:.2f}
- 最高分: {max(machine_scores):.2f}/10
- 最低分: {min(machine_scores):.2f}/10

### 人工评分统计 (标准化)
- 平均分: {human_mean:.2f}/10
- 标准差: {human_std:.2f}
- 最高分: {max(human_scores):.2f}/10
- 最低分: {min(human_scores):.2f}/10

## 对比分析

### 相关性分析
- 皮尔逊相关系数: {correlation:.3f}
- p值: {p_value:.3f}
- 相关性强度: {'强' if abs(correlation) > 0.7 else '中等' if abs(correlation) > 0.4 else '弱'}

### 差异分析
- 平均差异 (人工-机器): {mean_diff:.2f}
- 差异标准差: {std_diff:.2f}
- 最大正差异: {max(differences):.2f}
- 最大负差异: {min(differences):.2f}

### 评分分布
- 机器评分集中度: {machine_std:.2f} (标准差越小越集中)
- 人工评分集中度: {human_std:.2f}
- 评分一致性: {'高' if abs(mean_diff) < 1 else '中等' if abs(mean_diff) < 2 else '低'}

## 结论与建议

### 主要发现
1. **相关性**: {'机器评分与人工评分具有较强的一致性' if abs(correlation) > 0.7 else '机器评分与人工评分存在一定差异'}
2. **评分水平**: {'人工评分整体高于机器评分' if mean_diff > 0.5 else '人工评分整体低于机器评分' if mean_diff < -0.5 else '人工评分与机器评分水平相当'}
3. **评分稳定性**: {'机器评分更稳定' if machine_std < human_std else '人工评分更稳定'}

### 改进建议
{'1. 机器评分算法需要进一步优化以提高与人工评分的一致性' if abs(correlation) < 0.7 else '1. 机器评分算法表现良好，可考虑在实际应用中使用'}
2. 建议对差异较大的样本进行详细分析
3. 可考虑引入更多评分维度以提高评分准确性

---
*生成时间：2025年1月*
*标准化评分范围：0-10分*
*数据处理脚本：generate_normalized_charts.py*
"""
    
    report_path = os.path.join(output_dir.replace('images', 'reports'), 'normalized_analysis_report.md')
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"标准化分析报告已保存: {report_path}")
    return report_path

def main():
    # 配置文件路径
    config = {
        'machine_score_file': '../data/机器打分详情.csv',  # 机器评分文件
        'human_score_file': '../data/人工打分结果.json',  # 人工评分文件
        'output_dir': '../images'
    }
    
    # 初始化WandB（可选）
    wandb_enabled = init_wandb()
    
    try:
        # 生成标准化对比数据
        print("开始生成标准化对比数据...")
        comparison_data = generate_normalized_comparison_data(
            config['machine_score_file'],
            config['human_score_file']
        )
        
        if not comparison_data:
            print("无法生成对比数据，程序退出")
            return
        
        # 生成标准化图表
        print("\n开始生成标准化图表...")
        chart_paths = generate_normalized_charts(comparison_data, config['output_dir'])
        
        # 生成详细维度分析
        print("\n生成详细维度分析...")
        heatmap_path = generate_detailed_dimension_analysis(comparison_data, config['output_dir'])
        
        # 生成标准化分析报告
        print("\n生成标准化分析报告...")
        report_path = generate_normalized_analysis_report(comparison_data, config['output_dir'])
        
        # 上传到WandB（如果启用）
        if wandb_enabled:
            try:
                for chart_name, chart_path in chart_paths.items():
                    wandb.log({chart_name: wandb.Image(chart_path)})
                
                if heatmap_path:
                    wandb.log({'dimension_heatmap': wandb.Image(heatmap_path)})
                
                # 记录统计数据
                machine_scores = [item['machine_score_normalized'] for item in comparison_data]
                human_scores = [item['human_score_normalized'] for item in comparison_data]
                correlation, _ = pearsonr(machine_scores, human_scores) if len(machine_scores) > 1 else (0, 1)
                
                wandb.log({
                    'normalized_correlation': correlation,
                    'normalized_machine_mean': np.mean(machine_scores),
                    'normalized_human_mean': np.mean(human_scores),
                    'sample_count': len(comparison_data),
                    'score_range': '0-10 (normalized)'
                })
                
                print("数据已上传到WandB")
            except Exception as e:
                print(f"WandB上传失败: {str(e)}")
        
        print("\n标准化图表生成完成！")
        print(f"图表保存在: {config['output_dir']}")
        print(f"报告保存在: {report_path}")
        
    except Exception as e:
        print(f"程序执行出错: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        if wandb_enabled:
            wandb.finish()

if __name__ == '__main__':
    main()