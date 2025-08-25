#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终分析：总分与分项得分不一致的问题
"""

import json
import csv
from typing import Dict, List, Any

def analyze_all_areas():
    """
    分析所有台区的总分与分项得分的一致性
    """
    input_file = "人工打分结果_只保留selected.json"
    
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    inconsistent_areas = []
    consistent_areas = []
    
    for record in data['mgx_rating_result']:
        tq_id = record['tq_id']
        total_score = record.get('total_score', 0)
        
        # 收集所有有分数的项目
        calculated_total = 0
        
        def collect_scores(item):
            nonlocal calculated_total
            
            # 如果当前项有分数，记录它
            if item.get('is_score', False) and 'score' in item:
                try:
                    score_value = float(item['score'])
                    calculated_total += score_value
                except ValueError:
                    pass
            
            # 递归处理子项
            if 'children' in item:
                for child in item['children']:
                    collect_scores(child)
        
        for item in record['result_content']:
            collect_scores(item)
        
        difference = total_score - calculated_total
        
        if abs(difference) > 0.01:  # 允许小的浮点数误差
            inconsistent_areas.append({
                'tq_id': tq_id,
                'total_score': total_score,
                'calculated_total': calculated_total,
                'difference': difference
            })
        else:
            consistent_areas.append({
                'tq_id': tq_id,
                'total_score': total_score,
                'calculated_total': calculated_total
            })
    
    print(f"总台区数: {len(data['mgx_rating_result'])}")
    print(f"一致的台区数: {len(consistent_areas)}")
    print(f"不一致的台区数: {len(inconsistent_areas)}")
    
    if inconsistent_areas:
        print("\n不一致的台区示例:")
        for i, area in enumerate(inconsistent_areas[:5]):
            print(f"  {i+1}. 台区ID: {area['tq_id']}")
            print(f"     总分: {area['total_score']}")
            print(f"     计算总分: {area['calculated_total']:.2f}")
            print(f"     差异: {area['difference']:.2f}")
    
    # 保存详细结果到CSV
    output_file = "分析结果_总分一致性.csv"
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['台区ID', '总分', '计算总分', '差异', '是否一致']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for area in consistent_areas:
            writer.writerow({
                '台区ID': area['tq_id'],
                '总分': area['total_score'],
                '计算总分': area['calculated_total'],
                '差异': 0,
                '是否一致': '是'
            })
        
        for area in inconsistent_areas:
            writer.writerow({
                '台区ID': area['tq_id'],
                '总分': area['total_score'],
                '计算总分': area['calculated_total'],
                '差异': area['difference'],
                '是否一致': '否'
            })
    
    print(f"\n详细分析结果已保存到: {output_file}")
    return consistent_areas, inconsistent_areas

def main():
    try:
        consistent, inconsistent = analyze_all_areas()
        
        if inconsistent:
            print("\n发现总分与分项得分不一致的问题，需要进一步调查。")
        else:
            print("\n所有台区的总分与分项得分都一致。")
            
    except FileNotFoundError:
        print("错误：找不到输入文件 '人工打分结果_只保留selected.json'")
    except Exception as e:
        print(f"分析过程中发生错误: {str(e)}")

if __name__ == "__main__":
    main()