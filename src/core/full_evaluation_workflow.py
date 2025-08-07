import os
import logging
from pathlib import Path
from src.data.input_loader import load_gis_data_from_json
from src.data.output_saver import save_batch_results
from src.core.evaluation import calculate_beauty_score
from src.data.device_position_compare import compare_device_positions
from src.core.data_types import BatchInput, ImageInput

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def full_evaluation_workflow(
    input_path: str,
    output_dir: str,
    models: list,
    config: dict
):
    """
    阶段2：治理前后完整评分对比主流程
    """
    # 1. 数据加载
    input_path_obj = Path(input_path)
    if not input_path_obj.exists():
        raise FileNotFoundError(f"输入路径不存在: {input_path}")
    if input_path_obj.is_file():
        input_files = [input_path_obj]
    elif input_path_obj.is_dir():
        input_files = list(input_path_obj.glob("*.json"))
    else:
        raise ValueError("输入路径既不是文件也不是目录")

    if not input_files:
        raise ValueError("未找到任何.json数据文件")

    logger.info(f"发现{len(input_files)}个台区数据文件，开始处理...")

    # 2. 自动化治理（批量处理）
    inputs = []
    for file_path in input_files:
        gis_data = load_gis_data_from_json(file_path)
        image_input = ImageInput(gis_data=gis_data, input_id=file_path.stem, json_path=str(file_path))
        inputs.append(image_input)
    batch_input = BatchInput(
        inputs=inputs,
        config=config,
        batch_id=f"main_{len(inputs)}files"
    )
    from src.core.pipeline import process_batch
    batch_result = process_batch(
        batch_input,
        models=models,
        max_workers=config['processing']['max_workers']
    )
    save_batch_results(batch_result, output_dir)
    logger.info("自动化治理完成，结果已保存。")

    # 3. 治理前后评分对比与分析
    for file_path in input_files:
        # 治理前数据
        original_data = load_gis_data_from_json(file_path)
        # 治理后数据（假设输出目录下同名文件为治理后结果）
        treated_file = Path(output_dir) / file_path.name
        if not treated_file.exists():
            logger.warning(f"未找到治理后json文件: {treated_file}")
            continue
        treated_data = load_gis_data_from_json(treated_file)

        # 评分对比
        score_result = calculate_beauty_score(original_data, treated_data)
        logger.info(f"台区 {file_path.stem} 治理前后评分对比：")
        logger.info(f"治理前评分: {score_result['original_score']}")
        logger.info(f"治理后评分: {score_result['treated_score']}")
        logger.info(f"分数提升: {score_result['score_improvement']:.2f}，提升百分比: {score_result['improvement_percentage']:.1f}%")
        logger.info(f"结论: {score_result['reasoning']}")

        # 4. 设备位置对比图
        out_img_path = Path(output_dir) / f"{file_path.stem}_设备位置对比.png"
        compare_device_positions(str(file_path), str(treated_file), str(out_img_path))
        logger.info(f"设备位置对比图已生成: {out_img_path}")

        # 5. 结果保存（可选：保存详细评分JSON）
        result_json_path = Path(output_dir) / f"{file_path.stem}_评分对比结果.json"
        with open(result_json_path, 'w', encoding='utf-8') as f:
            import json
            json.dump(score_result, f, ensure_ascii=False, indent=2)
        logger.info(f"评分对比结果已保存: {result_json_path}")

if __name__ == "__main__":
    # 示例参数（实际可用argparse等方式传参）TODO 测试使用，后续再修改
    input_path = "标注数据目录/有对应关系的标注结果数据"
    output_dir = "resGIS"
    models = ["qwen"]
    config = {
        "processing": {
            "max_workers": 4
        }
    }
    full_evaluation_workflow(input_path, output_dir, models, config) 