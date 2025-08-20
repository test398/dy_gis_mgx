#!/usr/bin/env python3
import json
import csv
import os
import re
from collections import defaultdict

# 定义文件路径
json_file_path = '/Users/bonckus/代码/dy_gis_mgx/charts/all_extracted_scores.json'
csv_file_path = '/Users/bonckus/代码/dy_gis_mgx/charts/all_台区打分详情.csv'
output_json_path = '/Users/bonckus/代码/dy_gis_mgx/charts/modified_extracted_scores.json'

# 读取CSV文件，提取file_name前缀及其变体
csv_prefixes = set()
csv_prefix_to_file = defaultdict(list)

with open(csv_file_path, 'r', encoding='utf-8') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for row in csv_reader:
        file_name = row['file_name']
        # 提取前缀（去掉_评分详情.json）
        prefix = file_name.split('_评分详情.json')[0]
        csv_prefixes.add(prefix)
        csv_prefix_to_file[prefix].append(file_name)

        # 添加可能的变体
        # 1. 去掉所有非字母数字字符
        clean_prefix = re.sub(r'[^a-zA-Z0-9]', '', prefix)
        csv_prefixes.add(clean_prefix)
        csv_prefix_to_file[clean_prefix].append(file_name)

        # 2. 小写形式
        lower_prefix = prefix.lower()
        csv_prefixes.add(lower_prefix)
        csv_prefix_to_file[lower_prefix].append(file_name)

        # 3. 去掉连字符
        no_hyphen_prefix = prefix.replace('-', '')
        csv_prefixes.add(no_hyphen_prefix)
        csv_prefix_to_file[no_hyphen_prefix].append(file_name)

# 读取JSON文件
with open(json_file_path, 'r', encoding='utf-8') as json_file:
    data = json.load(json_file)

# 分析tq_id格式
print("=== JSON tq_id 格式分析 ===")
print(f"总共有 {len(data)} 个项目")

# 分类统计不同格式的tq_id
format_counts = defaultdict(int)
for item in data:
    if 'tq_id' in item:
        tq_id = item['tq_id']
        if '-' in tq_id:
            parts = tq_id.split('-')
            format_counts[f'{len(parts)}段-分隔'] += 1
        elif re.match(r'^\d+$', tq_id):
            format_counts['纯数字'] += 1
        elif re.match(r'^[a-f0-9]+$', tq_id.lower()):
            format_counts['十六进制字符串'] += 1
        else:
            format_counts['其他格式'] += 1

print("tq_id格式分布:")
for fmt, count in format_counts.items():
    print(f'  {fmt}: {count}')

# 分析CSV前缀格式
print("\n=== CSV file_name 前缀格式分析 ===")
print(f"总共有 {len(csv_prefixes)} 个唯一前缀")

csv_format_counts = defaultdict(int)
for prefix in csv_prefixes:
    if '-' in prefix:
        parts = prefix.split('-')
        csv_format_counts[f'{len(parts)}段-分隔'] += 1
    elif re.match(r'^\d+$', prefix):
        csv_format_counts['纯数字'] += 1
    elif re.match(r'^[a-f0-9]+$', prefix.lower()):
        csv_format_counts['十六进制字符串'] += 1
    elif len(prefix) <= 10:
        csv_format_counts['短字符串(<10)'] += 1
    else:
        csv_format_counts['其他格式'] += 1

print("前缀格式分布:")
for fmt, count in csv_format_counts.items():
    print(f'  {fmt}: {count}')

# 尝试匹配tq_id和前缀
print("\n=== 匹配尝试 ===")
matched_count = 0
partial_matched_count = 0
not_matched = []

# 定义匹配策略
strategies = [
    ('完整匹配', lambda x: x in csv_prefixes),
    ('去掉连字符匹配', lambda x: x.replace('-', '') in csv_prefixes),
    ('小写匹配', lambda x: x.lower() in csv_prefixes),
    ('清理特殊字符匹配', lambda x: re.sub(r'[^a-zA-Z0-9]', '', x) in csv_prefixes),
    ('部分匹配(前缀在tq_id中)', lambda x: any(prefix in x for prefix in csv_prefixes if len(prefix) > 5)),
    ('部分匹配(tq_id在前缀中)', lambda x: any(x in prefix for prefix in csv_prefixes if len(x) > 5))
]

# 保存最佳匹配结果
best_matches = []

for item in data:
    if 'tq_id' in item:
        original_tq_id = item['tq_id']
        # 去掉第一个-和之前的字符
        parts = original_tq_id.split('-', 1)
        if len(parts) > 1:
            new_tq_id = parts[1]
        else:
            new_tq_id = original_tq_id

        # 尝试所有匹配策略
        matched = False
        best_match = None
        best_strategy = None

        for strategy_name, strategy_func in strategies:
            if strategy_func(new_tq_id):
                matched = True
                best_match = new_tq_id
                best_strategy = strategy_name
                matched_count += 1
                break

        # 如果没有完全匹配，尝试部分匹配
        if not matched:
            for strategy_name, strategy_func in strategies[4:]:  # 只尝试部分匹配策略
                if strategy_name.startswith('部分匹配') and strategy_func(new_tq_id):
                    partial_matched_count += 1
                    # 找到匹配的前缀
                    if strategy_name == '部分匹配(前缀在tq_id中)':
                        matching_prefixes = [p for p in csv_prefixes if p in new_tq_id and len(p) > 5]
                    else:
                        matching_prefixes = [p for p in csv_prefixes if new_tq_id in p and len(new_tq_id) > 5]
                    best_match = matching_prefixes[0] if matching_prefixes else None
                    best_strategy = strategy_name
                    break

        # 记录结果
        if best_match:
            best_matches.append({
                'original_tq_id': original_tq_id,
                'new_tq_id': new_tq_id,
                'matched_prefix': best_match,
                'strategy': best_strategy
            })
            # 更新tq_id
            item['tq_id'] = best_match
        else:
            not_matched.append({
                'original': original_tq_id,
                'modified': new_tq_id
            })

# 保存修改后的JSON
with open(output_json_path, 'w', encoding='utf-8') as output_file:
    json.dump(data, output_file, ensure_ascii=False, indent=2)

# 输出结果
print(f'完全匹配: {matched_count} 个')
print(f'部分匹配: {partial_matched_count} 个')
print(f'未匹配: {len(not_matched)} 个')

# 显示一些匹配成功的例子
if best_matches:
    print("\n=== 匹配成功的示例 ===")
    for i, match in enumerate(best_matches[:5]):
        print(f'  示例 {i+1}:')
        print(f'    原始tq_id: {match["original_tq_id"]}')
        print(f'    修改后tq_id: {match["new_tq_id"]}')
        print(f'    匹配的前缀: {match["matched_prefix"]}')
        print(f'    使用策略: {match["strategy"]}')
        print(f'    对应的CSV文件名: {csv_prefix_to_file[match["matched_prefix"]][0]}')

# 显示一些未匹配的例子
if not_matched:
    print("\n=== 未匹配的示例 ===")
    for i, item in enumerate(not_matched[:5]):
        print(f'  {i+1}. 原始: {item["original"]} -> 修改后: {item["modified"]}')

print(f'\n修改后的文件已保存到: {output_json_path}')

# 删除脚本自身
script_path = os.path.abspath(__file__)
os.remove(script_path)
print(f'脚本 {script_path} 已自动删除')