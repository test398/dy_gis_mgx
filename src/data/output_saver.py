import os
import json
import logging
from pathlib import Path


def save_treatment_results(treatment_result, output_path):
    """
    保存单个台区处理结果到指定文件
    """
    # TODO: 实现结果保存逻辑
    pass


def save_batch_results(batch_result, output_dir):
    """
    保存批处理结果到指定目录
    """
    logger = logging.getLogger(__name__)
    output_dir = str(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    for result in batch_result.results:
        # 失败项跳过：无设备或评分<=0 视为失败，不落盘，避免下次被误跳过
        try:
            devices_cnt = len(getattr(result.treated_gis_data, 'devices', []) or [])
        except Exception:
            devices_cnt = 0
        if devices_cnt == 0 or (hasattr(result, 'beauty_score') and (result.beauty_score is None or result.beauty_score <= 0)):
            base_id = getattr(result.original_input, 'input_id', 'unknown').replace('_zlq', '').replace('_zlh', '')
            logger.warning(f"治理结果异常，跳过保存：{base_id}（devices={devices_cnt}, beauty_score={getattr(result, 'beauty_score', None)}）")
            continue

        # 统一ID，去掉已有后缀，避免 *_zlh_zlh.json
        psr_id_raw = result.original_input.gis_data.metadata.get('台区id')
        if not psr_id_raw:
            psr_id_raw = getattr(result.original_input, 'input_id', None) or Path(getattr(result.original_input, 'json_path', 'output')).stem
        base_id = psr_id_raw.replace('_zlq', '').replace('_zlh', '')

        # 尺寸与标注
        try:
            width, height = [(x[0], x[1]) for x in result.original_input.gis_data.boundaries['coors'] if x[0] > 0 and x[1] > 0][0]
        except Exception:
            # 兜底
            width, height = 1320, 1039

        annotations = []
        for device in result.treated_gis_data.devices:
            ann = {
                'id': device.get('id', f"dev_{len(annotations)}"),
                'points': device.get('points', []),
                'label': device.get('label') or device.get('type', 'unknown')
            }
            annotations.append(ann)
        outGISData = {'width': width, 'height': height, 'annotations': annotations}

        out_path = os.path.join(output_dir, f'{base_id}_zlh.json')
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(outGISData, f, ensure_ascii=False)
        logger.info(f"已保存台区 {base_id} 结果到 {out_path}")

    logger.info(f"全部批处理结果已保存到 {output_dir}")