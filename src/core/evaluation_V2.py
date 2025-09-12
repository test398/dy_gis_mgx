"""
评分引擎

集成overhead_line_scorer.py的架空线评分功能，并扩展阶段4其他维度
"""
from typing import Any, Dict, List
import logging

logger = logging.getLogger(__name__)


from typing import List
import matplotlib
matplotlib.use('Agg')  # 使用非GUI后端，避免Qt相关错误

import json
import os
import pandas as pd
from core.score.wall_bracket_scoring import WallBracketScoring
from core.score.cable_joint_enhanced_scoring import CableJointEnhancedScoring
from core.score.cable_terminal_end_final import CableTerminalEndFinalScoring
from core.score.branch_box_scoring import BranchBoxScoring
from core.score.basic_scoring_classes import (
    AccessPointScoring,
    MeteringBoxScoring,
    ConnectionLineScoring,
    SpanSectionScoring,
    CableTerminalStartScoring,
    DistrictAestheticsScoring,
    PoleScoring,
    CableSegmentScoring,
)
from scipy.stats import pearsonr
from sklearn.metrics import mean_absolute_error


def calculate_related(name, optimizer):
    """
    计算机器评分与人工评分的相关性

    Args:
        name: 标注标签名称 (如"分支箱", "墙支架"等)
        optimizer: 评分模型实例

    Returns:
        tuple: (x, y) 其中x是人工评分列表，y是机器评分列表
    """
    # 加载人工评分数据
    manual_scores_df = pd.read_csv("./数据/人工评分结果869.csv")

    # 建立标签映射
    label_mapping = {
        "杆塔": "1.杆塔",
        "墙支架": "2.墙支架",
        "电缆段": "3.电缆段",
        "分支箱": "4.分支箱",
        "接入点": "5.接入点",
        "计量箱": "6.计量箱",
        "连接线": "7.连接线",
        "档距段": "8.档距段",
        "电缆终端头起点": "9.电缆终端头起点",
        "电缆终端头末端": "10.电缆终端头末端",
        "低压电缆接头": "11.低压电缆接头",
        "台区整体美观性": "12.台区整体美观性",
        "台区整体偏移": "13.台区整体偏移",
        "台区整体混乱": "14.台区整体混乱",
    }

    # 获取对应的列名
    column_name = label_mapping.get(name)
    if column_name is None:
        print(f"警告: 未找到标签 '{name}' 对应的列名")
        return [], []

    path = "./数据/data"
    x = []  # 人工评分
    y = []  # 机器评分

    for json_file in os.listdir(path):
        if not json_file.endswith(".json"):
            continue

        json_file_path = os.path.join(path, json_file)

        # 从文件名提取台区ID (去掉.json后缀)
        district_id = os.path.splitext(json_file)[0]

        # 在人工评分数据中查找对应记录
        matching_rows = manual_scores_df[manual_scores_df["台区ID"] == district_id]
        if matching_rows.empty:
            continue  # 找不到对应的人工评分，跳过

        try:
            annotations = get_all_annotations(json_file_path)
            result = get_annotations_by_label(json_file_path, name)

            # 检查是否有该标签的标注
            if not result or len(result) == 0:
                continue  # 没有该标签的标注，跳过

            # 获取机器评分
            machine_score = optimizer.predict(result, annotations)

            # 获取人工评分
            manual_score = matching_rows.iloc[0][column_name]

            x.append(float(manual_score))
            y.append(float(machine_score))

        except Exception as e:
            print(f"处理文件 {json_file} 时出错: {e}")
            continue

    return mean_absolute_error(x, y)

def get_annotations_by_label(json_file_path: str, target_label: str) -> List[str]:
    """
    从JSON文件中提取指定label的注释，返回格式化的列表
    """
    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        results = []
        for _, annotation in enumerate(data.get('annotations', []), 1):
            if annotation.get('label') == target_label:
                result = {"label": target_label, "points": annotation.get('points')}
                results.append(result)
        
        return results
    
    except Exception as e:
        print(f"错误: {e}")
        return []

def get_all_annotations(json_file_path: str):
    """获取JSON文件中的所有注释"""
    try:
        with open(json_file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
        return data.get("annotations", [])
    except Exception as e:
        print(f"错误: {e}")
        return []


def evaluation_pipeline2(json_path: str=None):
    # json_path = r"C:\Users\jjf55\Desktop\dymgx3(1)\dymgx3\数据\data\0ab6ffd36b8a06deec5b922dfb015c0ab410547654.json"

    # 获取所有注释
    all_annotations = get_all_annotations(json_path)
    
    # 用于存储所有得分
    total_score = 0.0

    # 杆塔评分
    pole_results = get_annotations_by_label(json_path, "杆塔")
    pole_score = PoleScoring()
    pole_score = pole_score.predict(pole_results, all_annotations)
    print(f"杆塔得分: {pole_score:.1f}")
    total_score += pole_score

    # 墙支架评分
    wall_bracket_results = get_annotations_by_label(json_path, "墙支架")
    wall_bracket_score = WallBracketScoring()
    wall_score = wall_bracket_score.predict(wall_bracket_results, all_annotations)
    print(f"墙支架得分: {wall_score:.1f}")
    total_score += wall_score

    # 电缆段评分
    cable_segment_results = get_annotations_by_label(json_path, "电缆段")
    cable_segment_score = CableSegmentScoring()
    cable_segment_score = cable_segment_score.predict(cable_segment_results, all_annotations)
    print(f"电缆段得分: {cable_segment_score:.1f}")
    total_score += cable_segment_score

    # 低压电缆接头评分
    cable_joint_results = get_annotations_by_label(json_path, "低压电缆接头")
    cable_joint_score = CableJointEnhancedScoring()
    cable_joint_score = cable_joint_score.predict(cable_joint_results, all_annotations)
    print(f"低压电缆接头得分: {cable_joint_score:.1f}")
    total_score += cable_joint_score

    # 电缆终端头末端评分
    cable_terminal_end_results = get_annotations_by_label(json_path, "电缆终端头末端")
    cable_terminal_end_score = CableTerminalEndFinalScoring()
    terminal_end_score = cable_terminal_end_score.predict(
        cable_terminal_end_results, all_annotations
    )
    print(f"电缆终端头末端得分: {terminal_end_score:.1f}")
    total_score += terminal_end_score

    # 分支箱评分
    branch_box_results = get_annotations_by_label(json_path, "分支箱")
    branch_box_score = BranchBoxScoring()
    branch_score = branch_box_score.predict(branch_box_results, all_annotations)
    print(f"分支箱得分: {branch_score:.1f}")
    total_score += branch_score

    # 接入点评分
    access_point_results = get_annotations_by_label(json_path, "接入点")
    access_point_score = AccessPointScoring()
    access_score = access_point_score.predict(access_point_results, all_annotations)
    print(f"接入点得分: {access_score:.1f}")
    total_score += access_score

    # 计量箱评分
    metering_box_results = get_annotations_by_label(json_path, "计量箱")
    metering_box_score = MeteringBoxScoring()
    metering_score = metering_box_score.predict(metering_box_results, all_annotations)
    print(f"计量箱得分: {metering_score:.1f}")
    total_score += metering_score

    # 连接线评分
    connection_line_results = get_annotations_by_label(json_path, "连接线")
    connection_line_score = ConnectionLineScoring()
    connection_score = connection_line_score.predict(connection_line_results, all_annotations)
    print(f"连接线得分: {connection_score:.1f}")
    total_score += connection_score

    # 档距段评分
    span_section_results = get_annotations_by_label(json_path, "档距段")
    span_section_score = SpanSectionScoring()
    span_score = span_section_score.predict(span_section_results, all_annotations)
    print(f"档距段得分: {span_score:.1f}")
    total_score += span_score

    # 电缆终端头起点评分
    cable_terminal_start_results = get_annotations_by_label(json_path, "电缆终端头起点")
    cable_terminal_start_score = CableTerminalStartScoring()
    terminal_start_score = cable_terminal_start_score.predict(
        cable_terminal_start_results, all_annotations
    )
    print(f"电缆终端头起点得分: {terminal_start_score:.1f}")
    total_score += terminal_start_score

    # 台区整体美观性评分
    district_aesthetics_results = get_annotations_by_label(json_path, "台区整体美观性")
    district_aesthetics_score = DistrictAestheticsScoring()
    district_score = district_aesthetics_score.predict(
        district_aesthetics_results, all_annotations
    )
    print(f"台区整体美观性得分: {district_score:.1f}")
    total_score += district_score
    
    # 输出总得分
    print(f"\n总得分: {total_score:.1f}")
    return {
        'total_score': round(total_score, 1),
        'pole_score': pole_score,
        'wall_bracket_score': wall_score,
        'cable_segment_score': cable_segment_score,
        'cable_joint_score': cable_joint_score,
        'cable_terminal_end_score': terminal_end_score,
        'branch_box_score': branch_score,
        'access_point_score': access_score,
        'metering_box_score': metering_score,
        'connection_line_score': connection_score,
        'span_section_score': span_score,
        'cable_terminal_start_score': terminal_start_score,
        'district_aesthetics_score': district_score,
        'veto': False
    }

def calculate_beauty_score2(original_data: str, treated_data: str) -> Dict[str, Any]:
    """
    计算美观性评分（对治理前后各自调用完整评分器集，返回详细评分结果对比）
    Args:
        original_data: 原始GIS数据（dict，含'devices'）
        treated_data: 治理后GIS数据（dict，含'devices'）
    Returns:
        Dict[str, Any]: 详细评分对比结果
    """
    original_score = evaluation_pipeline2(original_data)
    treated_score = evaluation_pipeline2(treated_data)
    return {
        'original_score': original_score,
        'treated_score': treated_score
    }