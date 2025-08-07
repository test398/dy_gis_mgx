import os
import json
import logging


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
    for result in batch_result.results:
        psrId = result.original_input.gis_data.metadata['台区id']
        width, height = [(x[0], x[1]) for x in result.original_input.gis_data.boundaries['coors'] if x[0] > 0 and x[1] > 0][0]
        outGISData, annotations = {}, []
        for device in result.treated_gis_data.devices:
            ann = {'id': device['id'], 'points': device['points'], 'label': device.get('label') or device.get('type', 'unknown')}
            annotations.append(ann)
        outGISData = {'width': width, 'height': height, 'annotations': annotations}
        out_path = os.path.join(output_dir, f'{psrId}.json')
        with open(out_path, 'w') as f:
            json.dump(outGISData, f)
        logger.info(f"已保存台区 {psrId} 结果到 {out_path}")
    logger.info(f"全部批处理结果已保存到 {output_dir}")