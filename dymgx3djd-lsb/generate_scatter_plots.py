#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
带数量标注的散点图生成脚本
在每个散点位置标注重叠的数据点数量
"""

import pandas as pd
import matplotlib

matplotlib.use("Agg")  # 使用非交互式后端
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import rcParams
import matplotlib.font_manager as fm
import seaborn as sns
import os
import urllib.request
import zipfile
from collections import Counter

# 导入配置
from config import config


def download_and_setup_font():
    """下载并设置中文字体"""
    try:
        # 使用配置文件中的字体路径
        font_path = config.font_config["font_path"]
        font_url = config.font_config["font_url"]

        # 如果字体文件不存在，下载
        if not os.path.exists(font_path):
            print("正在下载中文字体...")
            urllib.request.urlretrieve(font_url, font_path)
            print(f"字体已下载到: {font_path}")

        # 设置matplotlib使用中文字体
        plt.rcParams["font.sans-serif"] = config.font_config["fallback_fonts"]
        plt.rcParams["axes.unicode_minus"] = False

        # 验证字体是否可用
        fig, ax = plt.subplots(figsize=(1, 1))
        ax.text(0.5, 0.5, "测试中文", fontsize=12, ha="center")
        plt.close(fig)

        print("中文字体设置成功!")
        return True

    except Exception as e:
        print(f"字体设置失败: {e}")
        print("将使用英文标签作为备选方案。")
        return False


def create_scatter_plot_with_count(
    x_data, y_data, title, xlabel, ylabel, save_path, is_chinese=True
):
    """创建带数量标注的散点图"""
    plt.figure(figsize=(12, 10))

    # 统计每个坐标点的数量
    coord_pairs = list(zip(x_data, y_data))
    coord_counts = Counter(coord_pairs)

    # 获取唯一的坐标点和对应的数量
    unique_coords = list(coord_counts.keys())
    counts = list(coord_counts.values())

    x_unique = [coord[0] for coord in unique_coords]
    y_unique = [coord[1] for coord in unique_coords]

    # 创建散点图，点的大小根据数量调整
    sizes = [max(50, count * 20) for count in counts]  # 最小50，按数量放大
    colors = [count for count in counts]  # 颜色深度表示数量

    scatter = plt.scatter(
        x_unique,
        y_unique,
        s=sizes,
        c=colors,
        alpha=0.7,
        cmap="viridis",
        edgecolors="black",
        linewidth=0.5,
    )

    # 添加颜色条
    cbar = plt.colorbar(scatter)
    if is_chinese:
        cbar.set_label("数据点数量", fontsize=12)
    else:
        cbar.set_label("Number of Data Points", fontsize=12)

    # 在每个点旁边标注数量
    for i, (x, y, count) in enumerate(zip(x_unique, y_unique, counts)):
        if count >= 5:  # 只标注数量大于等于5的点
            plt.annotate(
                f"{count}",
                (x, y),
                xytext=(5, 5),
                textcoords="offset points",
                fontsize=10,
                fontweight="bold",
                color="red",
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8),
            )

    # 添加对角线
    min_val = min(min(x_data), min(y_data))
    max_val = max(max(x_data), max(y_data))
    plt.plot(
        [min_val, max_val],
        [min_val, max_val],
        "r--",
        alpha=0.8,
        linewidth=2,
        label="理想对角线" if is_chinese else "Ideal Line",
    )

    # 计算相关系数
    correlation = np.corrcoef(x_data, y_data)[0, 1]

    # 设置标题和标签
    if is_chinese:
        plt.title(
            f"{title}\n相关系数: {correlation:.3f}\n总数据点: {len(x_data)}条, 唯一位置: {len(unique_coords)}个",
            fontsize=14,
            fontweight="bold",
        )
    else:
        plt.title(
            f"{title}\nCorrelation: {correlation:.3f}\nTotal Points: {len(x_data)}, Unique Positions: {len(unique_coords)}",
            fontsize=14,
            fontweight="bold",
        )

    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel(ylabel, fontsize=12)

    # 添加网格
    plt.grid(True, alpha=0.3)

    # 添加图例
    plt.legend()

    # 设置坐标轴范围
    plt.xlim(min_val - 1, max_val + 1)
    plt.ylim(min_val - 1, max_val + 1)

    # 添加统计信息文本框
    stats_text = (
        f"最大重叠: {max(counts)}个点"
        if is_chinese
        else f"Max Overlap: {max(counts)} points"
    )
    plt.text(
        0.02,
        0.98,
        stats_text,
        transform=plt.gca().transAxes,
        fontsize=10,
        verticalalignment="top",
        bbox=dict(boxstyle="round,pad=0.5", facecolor="lightblue", alpha=0.8),
    )

    # 保存图片
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()

    return correlation


def load_and_merge_data():
    """加载并合并数据"""
    # 使用配置文件中的数据路径
    machine_file = config.get_existing_file("machine_scores")
    manual_file = config.get_existing_file("human_scores")

    if machine_file is None:
        raise FileNotFoundError("未找到机器评分数据文件")
    if manual_file is None:
        raise FileNotFoundError("未找到人工评分数据文件")

    machine_df = pd.read_csv(machine_file, encoding="utf-8-sig")
    manual_df = pd.read_csv(manual_file, encoding="utf-8-sig")

    merged_df = pd.merge(
        machine_df, manual_df, on="台区ID", suffixes=("_机器", "_人工")
    )

    print(f"机器评分数据: {len(machine_df)} 条记录")
    print(f"人工评分数据: {len(manual_df)} 条记录")
    print(f"合并数据: {len(merged_df)} 条记录")
    print(f"匹配率: {len(merged_df) / len(machine_df) * 100:.2f}%")

    return merged_df


def generate_all_scatter_plots_with_count(merged_df, use_chinese_font=True):
    """生成所有维度的带数量标注散点图"""
    output_dir = config.scatter_plots_dir

    correlations = {}

    # 定义维度映射
    dimensions = {
        "总分": ("总分_机器", "总分_人工"),
        "1.杆塔": ("1.杆塔_机器", "1.杆塔_人工"),
        "2.墙支架": ("2.墙支架_机器", "2.墙支架_人工"),
        "3.电缆段": ("3.电缆段_机器", "3.电缆段_人工"),
        "4.分支箱": ("4.分支箱_机器", "4.分支箱_人工"),
        "5.接入点": ("5.接入点_机器", "5.接入点_人工"),
        "6.计量箱": ("6.计量箱_机器", "6.计量箱_人工"),
        "7.连接线": ("7.连接线_机器", "7.连接线_人工"),
        "8.档距段": ("8.档距段_机器", "8.档距段_人工"),
        "9.电缆终端头起点": ("9.电缆终端头起点_机器", "9.电缆终端头起点_人工"),
        "10.电缆终端头末端": ("10.电缆终端头末端_机器", "10.电缆终端头末端_人工"),
        "11.低压电缆接头": ("11.低压电缆接头_机器", "11.低压电缆接头_人工"),
        "12.台区整体美观性": ("12.台区整体美观性_机器", "12.台区整体美观性_人工"),
        "13.台区整体偏移": ("13.台区整体偏移_机器", "13.台区整体偏移_人工"),
        "14.台区整体混乱": ("14.台区整体混乱_机器", "14.台区整体混乱_人工"),
    }

    for col_name, (machine_col, manual_col) in dimensions.items():
        if machine_col in merged_df.columns and manual_col in merged_df.columns:
            machine_scores = merged_df[machine_col]
            manual_scores = merged_df[manual_col]

            title_cn = f"{col_name} - 机器评分 vs 人工评分"
            xlabel_cn = f"{col_name} (机器评分)"
            ylabel_cn = f"{col_name} (人工评分)"
            save_path = os.path.join(output_dir, f"{col_name}_散点图.png")

            correlation = create_scatter_plot_with_count(
                machine_scores,
                manual_scores,
                title_cn,
                xlabel_cn,
                ylabel_cn,
                save_path,
                is_chinese=True,
            )
            print(f"已生成散点图: {col_name}, 相关性: {correlation:.3f}")

            correlations[col_name] = correlation

    return correlations


def main():
    """主函数"""
    print("开始生成带数量标注的散点图...")

    # 设置字体
    font_success = download_and_setup_font()

    # 加载数据
    merged_df = load_and_merge_data()

    # 生成带数量标注的散点图
    correlations = generate_all_scatter_plots_with_count(
        merged_df, use_chinese_font=font_success
    )

    # 输出统计信息
    print("\n=== 相关性统计 ===")
    for item, corr in sorted(correlations.items(), key=lambda x: x[1], reverse=True):
        print(f"{item}: {corr:.3f}")

    avg_correlation = np.mean(list(correlations.values()))
    print(f"\n平均相关性: {avg_correlation:.3f}")

    print("\n所有带数量标注的散点图生成成功!")
    print(f"图片已保存到: {config.scatter_plots_dir}/")

    if font_success:
        print("中文字体版本带数量标注散点图生成成功!")
    else:
        print("由于字体问题，已生成英文版本带数量标注散点图作为备选方案。")


if __name__ == "__main__":
    main()
