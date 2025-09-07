#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析线性回归模型的权重和方程
"""

from ml_cable_scoring import MLCableScoringSystem
import numpy as np


def analyze_linear_model():
    """分析线性回归模型"""
    print("分析线性回归模型...")

    # 创建并训练模型
    ml_scorer = MLCableScoringSystem()
    success = ml_scorer.train()

    if not success or not ml_scorer.is_trained:
        print("模型训练失败！")
        return

    # 获取线性回归模型
    model = ml_scorer.model

    print(f"模型类型: {type(model).__name__}")

    # 特征名称
    feature_names = [
        "segment_count",
        "total_points",
        "avg_points",
        "max_points",
        "min_points",
        "total_length",
        "avg_length",
        "max_length",
        "min_length",
        "std_length",
        "x_range",
        "y_range",
        "area",
        "short_ratio",
        "abnormal_ratio",
    ]

    if hasattr(model, "coef_") and hasattr(model, "intercept_"):
        print(f"\n线性回归方程:")
        print(f"score = {model.intercept_:.3f}", end="")

        # 按权重绝对值排序
        coef_pairs = list(zip(feature_names, model.coef_))
        coef_pairs.sort(key=lambda x: abs(x[1]), reverse=True)

        print("\n\n权重分析（按重要性排序）:")
        print("-" * 50)
        for name, coef in coef_pairs:
            direction = "正向影响" if coef > 0 else "负向影响"
            print(f"{name:15} = {coef:8.3f}  ({direction})")

        print(f"\n线性回归完整方程:")
        equation = f"score = {model.intercept_:.3f}"
        for name, coef in zip(feature_names, model.coef_):
            sign = "+" if coef >= 0 else ""
            equation += f" {sign}{coef:.3f}*{name}"
        print(equation)

        # 分析重要特征
        print(f"\n关键发现:")
        important_features = [(name, coef) for name, coef in coef_pairs[:5]]
        for name, coef in important_features:
            if abs(coef) > 0.1:
                effect = "提高评分" if coef > 0 else "降低评分"
                print(f"- {name} 对评分有显著影响: {effect}")

    else:
        print("模型不支持权重分析")


if __name__ == "__main__":
    analyze_linear_model()
