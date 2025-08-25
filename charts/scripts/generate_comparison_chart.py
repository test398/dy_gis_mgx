import json
import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import pearsonr
import jsonlines
import wandb

# 设置中文字体，使用更通用的配置
plt.rcParams["font.family"] = ["Arial Unicode MS", "sans-serif"]
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 初始化WandB
def init_wandb():
    try:
        wandb.init(
            project="gis-beautification",
            name="chart-generation",
            config={
                "version": "1.0",
                "description": "电网台区美化治理与打分系统图表生成"
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
                    content = f.read(10000)  # 读取前10000个字符
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

def extract_scores_from_data(data):
    """从数据中提取评分信息"""
    scores = {}
    
    def extract_recursive(item, prefix=""):
        if isinstance(item, dict):
            # 检查是否有评分信息
            if 'score' in item:
                name = item.get('name', prefix)
                try:
                    score_value = float(item['score'])
                    scores[name] = score_value
                except (ValueError, TypeError):
                    pass
            
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

def calculate_total_score(scores):
    """计算总分"""
    return sum(scores.values()) if scores else 0

def generate_comparison_data(machine_score_file, human_score_file):
    """生成对比数据"""
    print("读取机器评分数据...")
    machine_data = extract_sample_data(machine_score_file, 50)  # 限制样本数量
    
    print("读取人工评分数据...")
    human_data = extract_sample_data(human_score_file, 50)
    
    if not machine_data or not human_data:
        print("无法读取评分数据")
        return None
    
    print(f"机器评分样本数: {len(machine_data)}")
    print(f"人工评分样本数: {len(human_data)}")
    
    comparison_data = []
    
    # 处理机器评分数据
    for i, data in enumerate(machine_data[:min(len(machine_data), 20)]):
        scores = extract_scores_from_data(data)
        total_score = calculate_total_score(scores)
        
        comparison_data.append({
            'id': f'sample_{i+1}',
            'machine_score': total_score,
            'machine_details': scores,
            'human_score': None,
            'human_details': {}
        })
    
    # 处理人工评分数据并尝试匹配
    for i, data in enumerate(human_data[:min(len(human_data), len(comparison_data))]):
        scores = extract_scores_from_data(data)
        total_score = calculate_total_score(scores)
        
        if i < len(comparison_data):
            comparison_data[i]['human_score'] = total_score
            comparison_data[i]['human_details'] = scores
    
    # 过滤掉没有对应人工评分的数据
    comparison_data = [item for item in comparison_data if item['human_score'] is not None]
    
    print(f"成功匹配的样本数: {len(comparison_data)}")
    return comparison_data

def generate_charts(comparison_data, output_dir='../charts'):
    """生成对比图表"""
    if not comparison_data:
        print("没有对比数据，无法生成图表")
        return
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 提取数据
    machine_scores = [item['machine_score'] for item in comparison_data]
    human_scores = [item['human_score'] for item in comparison_data]
    sample_ids = [item['id'] for item in comparison_data]
    
    # 1. 散点图对比
    plt.figure(figsize=(10, 8))
    plt.scatter(machine_scores, human_scores, alpha=0.6, s=50)
    
    # 添加对角线（理想情况下机器分数=人工分数）
    min_score = min(min(machine_scores), min(human_scores))
    max_score = max(max(machine_scores), max(human_scores))
    plt.plot([min_score, max_score], [min_score, max_score], 'r--', alpha=0.8, label='理想对角线')
    
    # 计算相关系数
    if len(machine_scores) > 1:
        correlation, p_value = pearsonr(machine_scores, human_scores)
        plt.title(f'机器评分 vs 人工评分\n相关系数: {correlation:.3f} (p={p_value:.3f})')
    else:
        plt.title('机器评分 vs 人工评分')
    
    plt.xlabel('机器评分')
    plt.ylabel('人工评分')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    scatter_path = os.path.join(output_dir, 'scatter_comparison.png')
    plt.savefig(scatter_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"散点图已保存: {scatter_path}")
    
    # 2. 柱状图对比
    plt.figure(figsize=(12, 6))
    x = np.arange(len(sample_ids))
    width = 0.35
    
    plt.bar(x - width/2, machine_scores, width, label='机器评分', alpha=0.8)
    plt.bar(x + width/2, human_scores, width, label='人工评分', alpha=0.8)
    
    plt.xlabel('样本')
    plt.ylabel('评分')
    plt.title('机器评分与人工评分对比')
    plt.xticks(x, [f'S{i+1}' for i in range(len(sample_ids))], rotation=45)
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    bar_path = os.path.join(output_dir, 'score_comparison.png')
    plt.savefig(bar_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"柱状图已保存: {bar_path}")
    
    # 3. 分布对比
    plt.figure(figsize=(10, 6))
    plt.hist(machine_scores, bins=10, alpha=0.7, label='机器评分', density=True)
    plt.hist(human_scores, bins=10, alpha=0.7, label='人工评分', density=True)
    
    plt.xlabel('评分')
    plt.ylabel('密度')
    plt.title('评分分布对比')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    dist_path = os.path.join(output_dir, 'score_distribution.png')
    plt.savefig(dist_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"分布图已保存: {dist_path}")
    
    # 4. 差异分析
    differences = [h - m for h, m in zip(human_scores, machine_scores)]
    
    plt.figure(figsize=(10, 6))
    plt.bar(range(len(differences)), differences, alpha=0.7)
    plt.axhline(y=0, color='r', linestyle='--', alpha=0.8)
    
    plt.xlabel('样本')
    plt.ylabel('评分差异 (人工 - 机器)')
    plt.title('评分差异分析')
    plt.xticks(range(len(sample_ids)), [f'S{i+1}' for i in range(len(sample_ids))], rotation=45)
    plt.grid(True, alpha=0.3)
    
    diff_path = os.path.join(output_dir, 'score_difference.png')
    plt.savefig(diff_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"差异图已保存: {diff_path}")
    
    return {
        'scatter_plot': scatter_path,
        'bar_chart': bar_path,
        'distribution': dist_path,
        'difference': diff_path
    }

def generate_analysis_report(comparison_data, output_dir):
    """生成分析报告"""
    if not comparison_data:
        return
    
    machine_scores = [item['machine_score'] for item in comparison_data]
    human_scores = [item['human_score'] for item in comparison_data]
    
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
# 评分对比分析报告

## 基本统计

### 样本数量
- 总样本数: {len(comparison_data)}

### 机器评分统计
- 平均分: {machine_mean:.2f}
- 标准差: {machine_std:.2f}
- 最高分: {max(machine_scores):.2f}
- 最低分: {min(machine_scores):.2f}

### 人工评分统计
- 平均分: {human_mean:.2f}
- 标准差: {human_std:.2f}
- 最高分: {max(human_scores):.2f}
- 最低分: {min(human_scores):.2f}

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

## 结论

{'机器评分与人工评分具有较强的一致性' if abs(correlation) > 0.7 else '机器评分与人工评分存在一定差异，需要进一步优化'}

"""
    
    report_path = os.path.join(output_dir, 'analysis_report.md')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"分析报告已保存: {report_path}")
    return report_path

def main():
    # 配置文件路径
    config = {
        'machine_score_file': '/Users/bonckus/代码/dy_gis_mgx/GisData/resGIS_qwen',  # 机器评分目录或文件
        'human_score_file': '/Users/bonckus/代码/dy_gis_mgx/charts/all_extracted_scores.json',  # 人工评分文件
        'output_dir': '../charts'
    }
    
    # 初始化WandB（可选）
    wandb_enabled = init_wandb()
    
    try:
        # 生成对比数据
        print("开始生成对比数据...")
        comparison_data = generate_comparison_data(
            config['machine_score_file'],
            config['human_score_file']
        )
        
        if not comparison_data:
            print("无法生成对比数据，程序退出")
            return
        
        # 生成图表
        print("\n开始生成图表...")
        chart_paths = generate_charts(comparison_data, config['output_dir'])
        
        # 生成分析报告
        print("\n生成分析报告...")
        report_path = generate_analysis_report(comparison_data, config['output_dir'])
        
        # 上传到WandB（如果启用）
        if wandb_enabled:
            try:
                for chart_name, chart_path in chart_paths.items():
                    wandb.log({chart_name: wandb.Image(chart_path)})
                
                # 记录统计数据
                machine_scores = [item['machine_score'] for item in comparison_data]
                human_scores = [item['human_score'] for item in comparison_data]
                correlation, _ = pearsonr(machine_scores, human_scores) if len(machine_scores) > 1 else (0, 1)
                
                wandb.log({
                    'correlation': correlation,
                    'machine_mean': np.mean(machine_scores),
                    'human_mean': np.mean(human_scores),
                    'sample_count': len(comparison_data)
                })
                
                print("数据已上传到WandB")
            except Exception as e:
                print(f"WandB上传失败: {str(e)}")
        
        print("\n图表生成完成！")
        
    except Exception as e:
        print(f"程序执行出错: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        if wandb_enabled:
            wandb.finish()

if __name__ == '__main__':
    main()