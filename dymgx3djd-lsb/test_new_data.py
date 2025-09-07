#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试新数据集 - 使用训练好的工程ML模型
对比机器评分_筛选结果2的结果
"""

import os
import csv
import json
import pandas as pd
import numpy as np
from engineering_ml_cable_scoring import EngineeringMLCableScoring
import warnings
warnings.filterwarnings('ignore')


def load_machine_scores(csv_file):
    """加载机器评分结果"""
    machine_scores = {}
    try:
        with open(csv_file, "r", encoding="utf-8-sig") as file:
            reader = csv.reader(file)
            header = next(reader)  # 跳过标题行
            print(f"CSV标题: {header}")
            
            for row in reader:
                if len(row) >= 2:
                    taiwan_id = row[0].strip()
                    score = int(row[1])  # 假设第二列是电缆段评分
                    machine_scores[taiwan_id] = score
                    
        print(f"成功加载 {len(machine_scores)} 个机器评分结果")
        return machine_scores
        
    except Exception as e:
        print(f"加载机器评分结果失败: {e}")
        return {}


def test_new_data_with_trained_model():
    """使用训练好的模型测试新数据集"""
    
    print("=" * 80)
    print("测试新数据集 - 工程ML模型 vs 机器评分_筛选结果2")
    print("=" * 80)
    
    # 1. 创建模型实例并加载训练好的模型
    model_file = "engineering_ml_model.pkl"
    ml_scorer = EngineeringMLCableScoring(model_file)
    
    if not os.path.exists(model_file):
        print(f"模型文件 {model_file} 不存在，开始训练...")
        success = ml_scorer.train()
        if not success:
            print("模型训练失败！")
            return
    else:
        if not ml_scorer.load_model():
            print("加载模型失败，重新训练...")
            success = ml_scorer.train()
            if not success:
                print("模型训练失败！")
                return
    
    print("✓ 工程ML模型加载完成")
    
    # 2. 加载机器评分结果2
    machine_scores = load_machine_scores("机器评分_筛选结果2.csv")
    if not machine_scores:
        print("无法加载机器评分结果，退出测试")
        return
    
    # 3. 测试新图片文件夹中的数据
    new_data_dir = "新的图片"
    if not os.path.exists(new_data_dir):
        print(f"新数据目录 {new_data_dir} 不存在")
        return
    
    print(f"✓ 开始测试 {new_data_dir} 中的数据")
    
    results = []
    ml_predictions = {}
    successful_tests = 0
    failed_tests = 0
    
    # 4. 遍历新数据集并进行预测
    for taiwan_id in machine_scores.keys():
        json_file = os.path.join(new_data_dir, f"{taiwan_id}_zlh.json")
        
        if not os.path.exists(json_file):
            print(f"⚠ 找不到文件: {json_file}")
            failed_tests += 1
            continue
        
        try:
            # 读取JSON数据
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            all_annotations = data.get("annotations", [])
            cable_segments = [ann for ann in all_annotations if ann.get("label") == "电缆段"]
            
            if not cable_segments:
                print(f"⚠ {taiwan_id}: 未找到电缆段标注")
                ml_score = 8  # 默认分数
            else:
                # 使用工程ML模型预测
                ml_score = ml_scorer.predict(cable_segments, all_annotations)
            
            ml_predictions[taiwan_id] = ml_score
            machine_score = machine_scores[taiwan_id]
            
            # 计算差异
            score_diff = abs(ml_score - machine_score)
            
            results.append({
                '台区ID': taiwan_id,
                '机器评分2': machine_score,
                '工程ML评分': ml_score,
                '评分差异': score_diff,
                '电缆段数量': len(cable_segments),
                '总标注数量': len(all_annotations)
            })
            
            # 评估准确度
            accuracy_level = "完美" if score_diff == 0 else "准确" if score_diff <= 1 else "可接受" if score_diff <= 2 else "偏差大"
            print(f"{taiwan_id}: 机器={machine_score}, ML={ml_score}, 差异={score_diff} ({accuracy_level})")
            
            successful_tests += 1
            
        except Exception as e:
            print(f"✗ {taiwan_id} 测试失败: {e}")
            failed_tests += 1
            continue
    
    # 5. 统计分析
    if results:
        print("\n" + "=" * 80)
        print("测试统计结果")
        print("=" * 80)
        
        df = pd.DataFrame(results)
        
        # 基本统计
        total_tests = len(results)
        avg_diff = df['评分差异'].mean()
        std_diff = df['评分差异'].std()
        
        # 准确度统计
        perfect_count = len(df[df['评分差异'] == 0])
        accurate_count = len(df[df['评分差异'] <= 1])
        acceptable_count = len(df[df['评分差异'] <= 2])
        
        print(f"测试样本数: {total_tests}")
        print(f"成功测试: {successful_tests}")
        print(f"失败测试: {failed_tests}")
        print(f"平均绝对误差: {avg_diff:.2f} ± {std_diff:.2f}")
        print()
        print(f"完美匹配 (差异=0): {perfect_count} ({perfect_count/total_tests*100:.1f}%)")
        print(f"准确匹配 (差异≤1): {accurate_count} ({accurate_count/total_tests*100:.1f}%)")
        print(f"可接受匹配 (差异≤2): {acceptable_count} ({acceptable_count/total_tests*100:.1f}%)")
        
        # 分数分布对比
        print(f"\n分数分布对比:")
        print(f"机器评分2分布: {dict(df['机器评分2'].value_counts().sort_index())}")
        print(f"工程ML评分分布: {dict(df['工程ML评分'].value_counts().sort_index())}")
        
        # 相关性分析
        correlation = df['机器评分2'].corr(df['工程ML评分'])
        print(f"\n相关系数: {correlation:.3f}")
        
        # 6. 保存详细结果
        output_file = "新数据集测试结果对比.csv"
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"\n详细结果已保存到: {output_file}")
        
        # 7. 保存摘要报告
        summary_file = "新数据集测试摘要.txt"
        with open(summary_file, "w", encoding="utf-8") as f:
            f.write("新数据集测试摘要报告\n")
            f.write("="*50 + "\n\n")
            f.write(f"测试时间: 使用训练好的工程ML模型\n")
            f.write(f"对比基准: 机器评分_筛选结果2.csv\n")
            f.write(f"测试数据: {new_data_dir} 文件夹\n\n")
            f.write(f"测试样本数: {total_tests}\n")
            f.write(f"平均绝对误差: {avg_diff:.2f} ± {std_diff:.2f}\n")
            f.write(f"完美匹配率: {perfect_count/total_tests*100:.1f}%\n")
            f.write(f"准确匹配率: {accurate_count/total_tests*100:.1f}%\n")
            f.write(f"可接受匹配率: {acceptable_count/total_tests*100:.1f}%\n")
            f.write(f"相关系数: {correlation:.3f}\n\n")
            f.write("结论:\n")
            if correlation > 0.7:
                f.write("- 工程ML模型与机器评分2具有强相关性\n")
            elif correlation > 0.5:
                f.write("- 工程ML模型与机器评分2具有中等相关性\n")
            else:
                f.write("- 工程ML模型与机器评分2相关性较低\n")
            
            if accurate_count/total_tests > 0.8:
                f.write("- 模型准确率较高，表现良好\n")
            elif accurate_count/total_tests > 0.6:
                f.write("- 模型准确率中等，有改进空间\n")
            else:
                f.write("- 模型准确率较低，需要进一步优化\n")
        
        print(f"摘要报告已保存到: {summary_file}")
        
    else:
        print("没有成功测试的样本！")


if __name__ == "__main__":
    test_new_data_with_trained_model()