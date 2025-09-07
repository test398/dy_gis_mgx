#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试档距段新数据集 - 使用训练好的档距段ML模型
对比人工评分_筛选结果2的结果
"""

import os
import csv
import json
import pandas as pd
import numpy as np
from pole_span_ml_scoring import PoleSpanMLScoring
import warnings

warnings.filterwarnings("ignore")


def load_manual_pole_span_scores(csv_file):
    """加载人工档距段评分结果"""
    manual_scores = {}
    try:
        with open(csv_file, "r", encoding="utf-8-sig") as file:
            reader = csv.reader(file)
            header = next(reader)  # 跳过标题行
            print(f"CSV标题: {header}")

            for row in reader:
                if len(row) >= 3:
                    taiwan_id = row[0].strip()
                    pole_span_score = int(row[2])  # 第三列是档距段评分
                    manual_scores[taiwan_id] = pole_span_score

        print(f"成功加载 {len(manual_scores)} 个人工档距段评分结果")
        return manual_scores

    except Exception as e:
        print(f"加载人工档距段评分结果失败: {e}")
        return {}


def test_pole_span_new_data():
    """使用训练好的档距段模型测试新数据集"""

    print("=" * 80)
    print("测试档距段新数据集 - 档距段ML模型 vs 人工评分_筛选结果2")
    print("=" * 80)

    # 1. 创建档距段模型实例并加载训练好的模型
    model_file = "pole_span_ml_model.pkl"
    ml_scorer = PoleSpanMLScoring(model_file)

    if not os.path.exists(model_file):
        print(f"模型文件 {model_file} 不存在，开始训练...")
        success = ml_scorer.train()
        if not success:
            print("档距段模型训练失败！")
            return
    else:
        if not ml_scorer.load_model():
            print("加载档距段模型失败，重新训练...")
            success = ml_scorer.train()
            if not success:
                print("档距段模型训练失败！")
                return

    print("✓ 档距段ML模型加载完成")

    # 2. 加载人工评分结果2
    manual_scores = load_manual_pole_span_scores("人工评分_筛选结果2.csv")
    if not manual_scores:
        print("无法加载人工档距段评分结果，退出测试")
        return

    # 3. 测试新图片文件夹中的数据
    new_data_dir = "新的图片"
    if not os.path.exists(new_data_dir):
        print(f"新数据目录 {new_data_dir} 不存在")
        return

    print(f"✓ 开始测试 {new_data_dir} 中的档距段数据")

    results = []
    ml_predictions = {}
    successful_tests = 0
    failed_tests = 0

    # 4. 遍历新数据集并进行档距段预测
    for taiwan_id in manual_scores.keys():
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
            # 寻找档距段标注，如果没有则使用电缆段作为代替
            pole_spans = [
                ann
                for ann in all_annotations
                if ann.get("label") in ["档距段", "电缆段"]
            ]

            if not pole_spans:
                print(f"⚠ {taiwan_id}: 未找到档距段或电缆段标注，给予满分")
                ml_score = 6  # 台区无档距段，记为满分
            else:
                # 使用档距段ML模型预测
                ml_score = ml_scorer.predict(pole_spans, all_annotations)

            ml_predictions[taiwan_id] = ml_score
            manual_score = manual_scores[taiwan_id]

            # 计算差异
            score_diff = abs(ml_score - manual_score)

            # 统计档距段和电缆段数量
            pole_span_count = len(
                [ann for ann in pole_spans if ann.get("label") == "档距段"]
            )
            cable_segment_count = len(
                [ann for ann in pole_spans if ann.get("label") == "电缆段"]
            )

            results.append(
                {
                    "台区ID": taiwan_id,
                    "人工档距段评分": manual_score,
                    "档距段ML评分": ml_score,
                    "评分差异": score_diff,
                    "档距段数量": pole_span_count,
                    "电缆段数量": cable_segment_count,
                    "总标注数量": len(all_annotations),
                }
            )

            # 评估准确度
            accuracy_level = (
                "完美"
                if score_diff == 0
                else "准确"
                if score_diff <= 1
                else "可接受"
                if score_diff <= 2
                else "偏差大"
            )
            print(
                f"{taiwan_id}: 人工={manual_score}, ML={ml_score}, 差异={score_diff} ({accuracy_level})"
            )

            successful_tests += 1

        except Exception as e:
            print(f"✗ {taiwan_id} 测试失败: {e}")
            failed_tests += 1
            continue

    # 5. 统计分析
    if results:
        print("\n" + "=" * 80)
        print("档距段测试统计结果")
        print("=" * 80)

        df = pd.DataFrame(results)

        # 基本统计
        total_tests = len(results)
        avg_diff = df["评分差异"].mean()
        std_diff = df["评分差异"].std()

        # 准确度统计
        perfect_count = len(df[df["评分差异"] == 0])
        accurate_count = len(df[df["评分差异"] <= 1])
        acceptable_count = len(df[df["评分差异"] <= 2])

        print(f"测试样本数: {total_tests}")
        print(f"成功测试: {successful_tests}")
        print(f"失败测试: {failed_tests}")
        print(f"平均绝对误差: {avg_diff:.2f} ± {std_diff:.2f}")
        print()
        print(
            f"完美匹配 (差异=0): {perfect_count} ({perfect_count / total_tests * 100:.1f}%)"
        )
        print(
            f"准确匹配 (差异≤1): {accurate_count} ({accurate_count / total_tests * 100:.1f}%)"
        )
        print(
            f"可接受匹配 (差异≤2): {acceptable_count} ({acceptable_count / total_tests * 100:.1f}%)"
        )

        # 分数分布对比
        print(f"\n档距段分数分布对比:")
        manual_dist = dict(df["人工档距段评分"].value_counts().sort_index())
        ml_dist = dict(df["档距段ML评分"].value_counts().sort_index())
        print(f"人工评分分布: {manual_dist}")
        print(f"档距段ML评分分布: {ml_dist}")

        # 相关性分析
        correlation = df["人工档距段评分"].corr(df["档距段ML评分"])
        print(f"\n相关系数: {correlation:.3f}")

        # 档距段数量统计
        has_pole_spans = len(df[df["档距段数量"] > 0])
        only_cable_segments = len(df[(df["档距段数量"] == 0) & (df["电缆段数量"] > 0)])
        no_segments = len(df[(df["档距段数量"] == 0) & (df["电缆段数量"] == 0)])

        print(f"\n数据分布:")
        print(
            f"有档距段标注: {has_pole_spans} ({has_pole_spans / total_tests * 100:.1f}%)"
        )
        print(
            f"仅有电缆段标注: {only_cable_segments} ({only_cable_segments / total_tests * 100:.1f}%)"
        )
        print(f"无相关标注: {no_segments} ({no_segments / total_tests * 100:.1f}%)")

        # 6. 保存详细结果
        output_file = "档距段新数据集测试结果对比.csv"
        df.to_csv(output_file, index=False, encoding="utf-8-sig")
        print(f"\n详细结果已保存到: {output_file}")

        # 7. 保存摘要报告
        summary_file = "档距段新数据集测试摘要.txt"
        with open(summary_file, "w", encoding="utf-8") as f:
            f.write("档距段新数据集测试摘要报告\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"测试时间: 使用训练好的档距段ML模型\n")
            f.write(f"对比基准: 人工评分_筛选结果2.csv (档距段评分)\n")
            f.write(f"测试数据: {new_data_dir} 文件夹\n")
            f.write(f"评分范围: 0-6分\n\n")
            f.write(f"测试样本数: {total_tests}\n")
            f.write(f"平均绝对误差: {avg_diff:.2f} ± {std_diff:.2f}\n")
            f.write(f"完美匹配率: {perfect_count / total_tests * 100:.1f}%\n")
            f.write(f"准确匹配率: {accurate_count / total_tests * 100:.1f}%\n")
            f.write(f"可接受匹配率: {acceptable_count / total_tests * 100:.1f}%\n")
            f.write(f"相关系数: {correlation:.3f}\n\n")

            f.write("数据分布:\n")
            f.write(
                f"- 有档距段标注: {has_pole_spans} ({has_pole_spans / total_tests * 100:.1f}%)\n"
            )
            f.write(
                f"- 仅有电缆段标注: {only_cable_segments} ({only_cable_segments / total_tests * 100:.1f}%)\n"
            )
            f.write(
                f"- 无相关标注: {no_segments} ({no_segments / total_tests * 100:.1f}%)\n\n"
            )

            f.write("档距段评分标准 (基于档距段说明.jpg):\n")
            f.write("- 6分: 台区无档距段或完全符合标准\n")
            f.write("- 5分: 完全符合治理标准要求\n")
            f.write("- 3-4分: 基本符合治理标准要求\n")
            f.write("- 0-2分: 不符合治理标准要求\n\n")

            f.write("结论:\n")
            if correlation > 0.7:
                f.write("- 档距段ML模型与人工评分具有强相关性\n")
            elif correlation > 0.5:
                f.write("- 档距段ML模型与人工评分具有中等相关性\n")
            else:
                f.write("- 档距段ML模型与人工评分相关性较低\n")

            if accurate_count / total_tests > 0.8:
                f.write("- 档距段模型准确率较高，表现良好\n")
            elif accurate_count / total_tests > 0.6:
                f.write("- 档距段模型准确率中等，有改进空间\n")
            else:
                f.write("- 档距段模型准确率较低，需要进一步优化\n")

            f.write(
                f"- 大部分台区({only_cable_segments + no_segments}个)缺少专门的档距段标注，使用电缆段作为替代\n"
            )

        print(f"摘要报告已保存到: {summary_file}")

        # 8. 显示特别案例分析
        print(f"\n特别案例分析:")
        large_diff_cases = df[df["评分差异"] >= 3]
        if len(large_diff_cases) > 0:
            print(f"评分差异≥3的案例 ({len(large_diff_cases)}个):")
            for _, case in large_diff_cases.iterrows():
                print(
                    f"  {case['台区ID']}: 人工={case['人工档距段评分']}, ML={case['档距段ML评分']}, 差异={case['评分差异']}"
                )
        else:
            print("没有评分差异≥3的案例，模型表现较为稳定")

    else:
        print("没有成功测试的样本！")


if __name__ == "__main__":
    test_pole_span_new_data()
