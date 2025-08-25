import json
import pandas as pd
import re
import os

def load_json_data(file_path):
    """加载JSON数据"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"成功加载JSON文件: {file_path}")
        print(f"数据类型: {type(data)}")
        if isinstance(data, list):
            print(f"数组长度: {len(data)}")
        elif isinstance(data, dict):
            print(f"字典键数量: {len(data.keys())}")
        return data
    except Exception as e:
        print(f"加载JSON文件失败: {e}")
        return None

def process_tq_id(tq_id):
    """处理台区ID，提取数字部分"""
    if pd.isna(tq_id) or tq_id == '':
        return None
    
    # 转换为字符串
    tq_str = str(tq_id)
    
    # 提取数字部分
    numbers = re.findall(r'\d+', tq_str)
    if numbers:
        # 取最长的数字序列
        longest_number = max(numbers, key=len)
        return longest_number
    
    return tq_str

def extract_scores_from_item(item, parent_name=""):
    """从单个项目中提取评分信息"""
    scores = {}
    
    # 获取当前项目名称
    current_name = item.get('name', '')
    full_name = f"{parent_name}_{current_name}" if parent_name else current_name
    
    # 如果有评分，记录下来
    if 'score' in item:
        try:
            score_value = float(item['score'])
            scores[full_name] = score_value
        except (ValueError, TypeError):
            pass
    
    # 递归处理子项
    if 'children' in item and isinstance(item['children'], list):
        for child in item['children']:
            child_scores = extract_scores_from_item(child, full_name)
            scores.update(child_scores)
    
    return scores

def extract_all_scores(data):
    """提取所有评分数据"""
    all_scores = []
    
    if isinstance(data, list):
        for i, item in enumerate(data):
            print(f"处理第 {i+1} 个项目...")
            
            # 提取台区ID
            tq_id = item.get('tq_id', f'unknown_{i}')
            processed_tq_id = process_tq_id(tq_id)
            
            # 提取评分
            scores = extract_scores_from_item(item)
            
            if scores:
                score_record = {
                    'tq_id': tq_id,
                    'processed_tq_id': processed_tq_id,
                    **scores
                }
                all_scores.append(score_record)
                
                if i < 3:  # 打印前3个样本的详细信息
                    print(f"  台区ID: {tq_id} -> {processed_tq_id}")
                    print(f"  评分项目数: {len(scores)}")
                    print(f"  评分项目: {list(scores.keys())[:5]}...")  # 只显示前5个
    
    elif isinstance(data, dict):
        # 如果是单个对象
        tq_id = data.get('tq_id', 'unknown')
        processed_tq_id = process_tq_id(tq_id)
        scores = extract_scores_from_item(data)
        
        if scores:
            score_record = {
                'tq_id': tq_id,
                'processed_tq_id': processed_tq_id,
                **scores
            }
            all_scores.append(score_record)
    
    return all_scores

def merge_score_columns(df):
    """合并相似的评分列"""
    # 获取所有评分列（除了ID列）
    score_columns = [col for col in df.columns if col not in ['tq_id', 'processed_tq_id']]
    
    # 创建列映射字典
    column_mapping = {}
    processed_columns = set()
    
    for col in score_columns:
        if col in processed_columns:
            continue
            
        # 查找相似的列
        similar_cols = [col]
        for other_col in score_columns:
            if other_col != col and other_col not in processed_columns:
                # 简单的相似性检查（可以根据需要调整）
                if col.lower().replace('_', '').replace(' ', '') == other_col.lower().replace('_', '').replace(' ', ''):
                    similar_cols.append(other_col)
        
        if len(similar_cols) > 1:
            # 合并相似列
            main_col = similar_cols[0]
            column_mapping[main_col] = similar_cols
            processed_columns.update(similar_cols)
        else:
            column_mapping[col] = [col]
            processed_columns.add(col)
    
    # 创建新的DataFrame
    new_data = []
    for _, row in df.iterrows():
        new_row = {
            'tq_id': row['tq_id'],
            'processed_tq_id': row['processed_tq_id']
        }
        
        for main_col, cols in column_mapping.items():
            # 合并列的值（取非空值，如果有多个非空值则取平均）
            values = []
            for col in cols:
                if col in row and pd.notna(row[col]):
                    values.append(row[col])
            
            if values:
                new_row[main_col] = sum(values) / len(values)
            else:
                new_row[main_col] = None
        
        new_data.append(new_row)
    
    return pd.DataFrame(new_data)

def adjust_score_proportions(df, target_scale=10):
    """调整评分比例到目标范围"""
    # 获取所有评分列
    score_columns = [col for col in df.columns if col not in ['tq_id', 'processed_tq_id']]
    
    for col in score_columns:
        # 获取非空值
        valid_scores = df[col].dropna()
        
        if len(valid_scores) > 0:
            min_score = valid_scores.min()
            max_score = valid_scores.max()
            
            if max_score > min_score:
                # 线性缩放到0-target_scale范围
                df[col] = df[col].apply(
                    lambda x: ((x - min_score) / (max_score - min_score)) * target_scale if pd.notna(x) else x
                )
            
            print(f"列 '{col}': 原始范围 [{min_score:.2f}, {max_score:.2f}] -> 调整后范围 [0, {target_scale}]")
    
    return df

def generate_detailed_scores_csv(json_file_path, output_csv_path):
    """生成详细评分CSV文件"""
    print(f"开始处理文件: {json_file_path}")
    
    # 1. 加载JSON数据
    data = load_json_data(json_file_path)
    if data is None:
        print("无法加载数据，程序退出")
        return False
    
    # 2. 提取评分数据
    print("\n提取评分数据...")
    all_scores = extract_all_scores(data)
    
    if not all_scores:
        print("未找到评分数据")
        return False
    
    print(f"成功提取 {len(all_scores)} 条评分记录")
    
    # 3. 转换为DataFrame
    df = pd.DataFrame(all_scores)
    print(f"\nDataFrame形状: {df.shape}")
    print(f"列名: {list(df.columns)[:10]}...")  # 只显示前10个列名
    
    # 4. 合并相似的评分列
    print("\n合并相似的评分列...")
    df = merge_score_columns(df)
    print(f"合并后DataFrame形状: {df.shape}")
    
    # 5. 调整评分比例
    print("\n调整评分比例...")
    df = adjust_score_proportions(df, target_scale=10)
    
    # 6. 保存到CSV
    try:
        df.to_csv(output_csv_path, index=False, encoding='utf-8-sig')
        print(f"\n详细评分CSV文件已保存: {output_csv_path}")
        
        # 显示统计信息
        print("\n=== 统计信息 ===")
        print(f"总记录数: {len(df)}")
        print(f"总列数: {len(df.columns)}")
        print(f"评分列数: {len(df.columns) - 2}")
        
        # 显示前几行
        print("\n=== 前5行数据预览 ===")
        print(df.head())
        
        return True
        
    except Exception as e:
        print(f"保存CSV文件失败: {e}")
        return False

def main():
    # 配置文件路径
    json_file_path = "../data/人工打分结果.json"  # 输入的JSON文件路径
    output_csv_path = "../data/人工打分结果_详细分项.csv"  # 输出的CSV文件路径
    
    # 检查输入文件是否存在
    if not os.path.exists(json_file_path):
        print(f"输入文件不存在: {json_file_path}")
        print("请检查文件路径是否正确")
        return
    
    # 确保输出目录存在
    output_dir = os.path.dirname(output_csv_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        print(f"创建输出目录: {output_dir}")
    
    # 生成详细评分CSV
    success = generate_detailed_scores_csv(json_file_path, output_csv_path)
    
    if success:
        print("\n程序执行完成！")
    else:
        print("\n程序执行失败！")

if __name__ == "__main__":
    main()