import os
import pandas as pd


def filter_human_scores_by_data_files(human_scores_path, data_dir_path):
    """
    根据数据/data文件夹下的文件名筛选人工评分结果

    Args:
        human_scores_path: 人工评分结果CSV文件路径
        data_dir_path: 数据文件夹路径

    Returns:
        过滤后的DataFrame，只包含在data文件夹中有对应文件的评分记录
    """
    # 读取人工评分结果
    df = pd.read_csv(human_scores_path, encoding="utf-8-sig")

    # 获取data文件夹中的所有文件名（去除扩展名）
    data_files = os.listdir(data_dir_path)
    data_file_ids = []

    for filename in data_files:
        if filename.endswith("_zlh.json"):
            # 去除_zlh.json后缀
            file_id = filename.replace("_zlh.json", "")
            data_file_ids.append(file_id)

    # 筛选出台区ID在data文件列表中的记录
    filtered_df = df[df["台区ID"].isin(data_file_ids)]

    return filtered_df


if __name__ == "__main__":
    # 测试代码
    res = filter_human_scores_by_data_files("./数据/人工评分结果869.csv", "数据/data")
    ## 保存为csv
    print(res)
    res.to_csv("数据/filtered_human_scores.csv", index=False)
    pass
