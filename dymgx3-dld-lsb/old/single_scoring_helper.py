from auto_scoring_system import AutoScoringSystem
import os
from config import config
import engineering_ml_cable_scoring

engineering_ml_cable_scoring.test_single_file(
    "./data1/0818408e-1a2b-4479-be8d-c157becec39c_zlh.json"
)


def score_single_taiqu(file_path, output_dir=None):
    """
    对单个台区进行评分

    Args:
        file_path: 台区JSON文件路径
        output_dir: 输出目录，如果为None则使用默认目录

    Returns:
        dict: 评分结果
    """
    if output_dir is None:
        output_dir = config.single_results_dir
    scorer = AutoScoringSystem()

    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
        return None

    # 计算评分
    results = scorer.calculate_scores(file_path)

    if results:
        # 提取台区ID
        filename = os.path.basename(file_path)
        tq_id = filename.replace("_zlh.json", "").replace(".json", "")

        print(f"台区ID: {tq_id}")
        print(f"设备统计: {results['device_counts']}")
        print(f"评分结果: {results['scores']}")
        print(f"总分: {results['total_score']}")

        # 保存CSV文件
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{tq_id}_评分结果.csv")
        scorer.save_to_csv(results, output_path, tq_id)
        print(f"结果已保存到: {output_path}")

        return results
    else:
        print(f"评分失败: {file_path}")
        return None


# 使用示例
if __name__ == "__main__":
    # 示例用法 - 使用配置文件中的示例文件路径
    json_file = config.get_existing_file("taiqu_json")

    if json_file:
        score_single_taiqu(json_file)
    else:
        print("未找到台区JSON文件")
        print("请在config.py中配置正确的台区JSON文件路径")
