#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从人工评分结果和机器评分结果中筛选出data1文件夹下存在的JSON文件对应的行，
并提取ID、电缆段、档距段字段
"""

import os
import pandas as pd
import glob


def get_json_ids_from_data1(data1_folder):
    """获取data1文件夹中所有JSON文件的ID"""
    json_files = glob.glob(os.path.join(data1_folder, "*.json"))
    json_ids = set()

    for json_file in json_files:
        # 获取文件名（不含扩展名）
        filename = os.path.splitext(os.path.basename(json_file))[0]
        # 移除可能的后缀如"_zlh"
        if "_zlh" in filename:
            filename = filename.split("_zlh")[0]
        json_ids.add(filename)

    return json_ids


def filter_scores_by_json_ids(csv_file, json_ids, output_file):
    """根据JSON ID过滤CSV文件中的评分结果"""
    try:
        # 读取CSV文件
        df = pd.read_csv(csv_file, encoding="utf-8-sig")

        # 确保'台区ID'列存在
        if "台区ID" not in df.columns:
            print(f"错误: CSV文件 {csv_file} 中找不到'台区ID'列")
            return

        # 过滤出台区ID在json_ids中的行
        filtered_df = df[df["台区ID"].isin(json_ids)]

        print(f"原始CSV行数: {len(df)}")
        print(f"匹配的行数: {len(filtered_df)}")

        # 只保留需要的列
        columns_needed = ["台区ID", "3.电缆段", "8.档距段"]

        # 检查这些列是否存在
        existing_columns = [col for col in columns_needed if col in filtered_df.columns]
        if len(existing_columns) < len(columns_needed):
            print(f"警告: 部分列不存在，实际存在的列: {existing_columns}")

        result_df = filtered_df[existing_columns]

        # 重命名列为更简洁的名称
        result_df = result_df.rename(
            columns={"台区ID": "ID", "3.电缆段": "电缆段", "8.档距段": "档距段"}
        )

        # 保存结果到新文件
        result_df.to_csv(output_file, index=False, encoding="utf-8-sig")
        print(f"结果已保存到: {output_file}")

        # 显示前几行结果
        print("\n前5行结果:")
        print(result_df.head())

        return result_df

    except Exception as e:
        print(f"处理CSV文件时出错: {e}")
        return None


def main():
    # 设置文件路径
    base_dir = r"C:\Users\A\Downloads\dymgx3-main\dymgx3-main"
    data1_folder = os.path.join(base_dir, "新的图片")

    # 人工评分和机器评分文件路径
    manual_score_file = os.path.join(base_dir, "人工评分结果869.csv")
    machine_score_file = os.path.join(base_dir, "机器评分结果869_改进版.csv")

    # 输出文件路径
    output_manual = os.path.join(base_dir, "人工评分_筛选结果2.csv")
    output_machine = os.path.join(base_dir, "机器评分_筛选结果2.csv")

    print("开始处理...")
    print(f"Data1文件夹: {data1_folder}")

    # 获取data1文件夹中的JSON文件ID
    json_ids = get_json_ids_from_data1(data1_folder)
    print(f"找到 {len(json_ids)} 个JSON文件")

    # 如果没有找到JSON文件，尝试其他可能的路径
    if len(json_ids) == 0:
        print("尝试查找其他可能的JSON文件路径...")
        # 可以在这里添加其他路径的搜索逻辑

    if len(json_ids) == 0:
        print("警告: 未找到任何JSON文件")
        return

    print(f"前5个JSON ID示例: {list(json_ids)[:5]}")

    # 处理人工评分结果
    print(f"\n处理人工评分结果: {manual_score_file}")
    if os.path.exists(manual_score_file):
        filter_scores_by_json_ids(manual_score_file, json_ids, output_manual)
    else:
        print(f"文件不存在: {manual_score_file}")

    # 处理机器评分结果
    print(f"\n处理机器评分结果: {machine_score_file}")
    if os.path.exists(machine_score_file):
        filter_scores_by_json_ids(machine_score_file, json_ids, output_machine)
    else:
        print(f"文件不存在: {machine_score_file}")


if __name__ == "__main__":
    main()
