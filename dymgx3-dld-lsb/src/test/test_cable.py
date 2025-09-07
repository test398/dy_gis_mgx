"""
电缆段评分相关性测试
"""

import json
import os
import sys
import pandas as pd
from scipy.stats import pearsonr

# 添加父目录到Python路径以便导入模块
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from ml_scoring.engineering_ml_cable_scoring import EngineeringMLCableScoring


def test_cable_correlation(
    filtered_scores_file="数据/filtered_human_scores.csv", data_dir="数据/data"
):
    """测试电缆段评分的相关性，只返回相关性"""
    ml_scorer = EngineeringMLCableScoring()

    # 训练模型
    success = ml_scorer.train()
    if not success:
        return None

    # 读取电缆段评分
    df = pd.read_csv(filtered_scores_file)
    cable_col = [col for col in df.columns if "电缆段" in col][0]
    filtered_scores = df.set_index("台区ID")[cable_col].to_dict()
    # 获取预测结果
    y = []
    predictions = []

    for taiwan_id, human_score in filtered_scores.items():
        json_file = f"{data_dir}/{taiwan_id}.json"
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            all_annotations = data.get("annotations", [])
            cable_segments = [
                ann for ann in all_annotations if ann.get("label") == "电缆段"
            ]

            if not cable_segments:
                continue

            # 预测
            ml_score = ml_scorer.predict(cable_segments, all_annotations)

            y.append(human_score)
            predictions.append(ml_score)

        except:
            continue
    # 计算相关性
    correlation, _ = pearsonr(y, predictions)
    return correlation


if __name__ == "__main__":
    correlation = test_cable_correlation()
    if correlation is not None:
        print(f"相关性: {correlation:.4f}")
    else:
        print("测试失败")
