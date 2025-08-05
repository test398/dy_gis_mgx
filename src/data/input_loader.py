from datetime import datetime
import json
import os
from core.data_types import GISData


def load_gis_data():
    """
    加载GIS数据 - 从JSON文件或其他数据源加载台区数据
    """
    # TODO: 实现GIS数据加载逻辑
    pass


def load_batch_data():
    """
    加载批量GIS数据 - 从目录或批量文件加载多个台区数据
    """
    # TODO: 实现批量GIS数据加载逻辑
    pass


def load_gis_data_from_json(file_path) -> GISData:
    """
    从单个JSON文件加载GIS数据
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    timestamp = os.path.getctime(file_path)
    dt = datetime.fromtimestamp(timestamp)
    data['annotations'] = data.get('annotations', [])
    devices = data.get('annotations', [])
    buildings = data.get('buildings', [])
    roads = data.get('roads', [])
    rivers = data.get('rivers', [])
    boundaries = {'coors': [[0, 0], [data['width'], 0], [data['width'], data['height']], [0, data['height']]]}  # 默认边界
    metadata = {
        '台区id': os.path.basename(file_path).split('.')[0].replace('_zlq', ''),  # 假设文件名格式为 "id.json"
        '区域名称': data.get('area_name', 'unknown'),
        '坐标系': data.get('coordinate_system', 'local'),
        '创建时间': data.get('creation_time', dt.strftime('%Y-%m-%d %H:%M:%S'))
    }
    return GISData(
        devices=devices,
        buildings=buildings,
        roads=roads,
        rivers=rivers,
        boundaries=boundaries,
        metadata=metadata
    )