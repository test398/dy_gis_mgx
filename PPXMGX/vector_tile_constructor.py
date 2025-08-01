#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VectorTile 类实现
对应 self.js 中的 VectorTile 构造函数
"""

from typing import Dict, Any, Optional
from vector_tile_parser import VectorTileLayer, PBFReader

class VectorTile:
    """
    矢量瓦片类
    对应 self.js 中的 _y.VectorTile
    """
    
    def __init__(self, pbf_reader: PBFReader, end_pos: int, extent: int = 4096):
        """
        初始化矢量瓦片
        
        参数说明:
        t (pbf_reader): PBF读取器对象，用于读取二进制数据
        e (end_pos): 数据结束位置，用于确定读取范围
        r (extent): 瓦片范围，默认为4096，用于坐标转换
        
        参数来源:
        - t: 通常来自网络请求的响应数据，通过 new PBF(data) 创建
        - e: 来自瓦片数据的长度信息，表示当前瓦片数据的结束位置
        - r: 来自瓦片规范，通常是4096（瓦片坐标系的范围）
        """
        self.pbf = pbf_reader
        self.end_pos = end_pos
        self.extent = extent
        self.layers: Dict[str, VectorTileLayer] = {}
        
        # 解析所有图层
        self._parse_layers()
    
    def _parse_layers(self):
        """解析所有图层 - 对应JS中的readFields回调函数"""
        while self.pbf.pos < self.end_pos:
            try:
                # 读取字段标签
                tag = self.pbf.read_varint()
                wire_type = tag & 0x07
                field_number = tag >> 3
                
                # 当字段号为3时，创建图层
                if field_number == 3:
                    self._create_layer()
                else:
                    # 跳过其他字段
                    self._skip_field(wire_type)
                    
            except Exception as e:
                print(f"解析图层时出错: {e}")
                break
    
    def _create_layer(self):
        """创建单个图层 - 对应JS中的new vy()"""
        try:
            # 读取图层数据长度
            layer_length = self.pbf.read_varint()
            layer_end_pos = self.pbf.pos + layer_length
            
            # 读取图层数据
            layer_data = self.pbf.read_bytes(layer_length)
            
            # 创建图层对象
            layer = VectorTileLayer(layer_data)
            layer_result = layer.parse_layer()
            
            # 如果图层有效（有要素），则添加到layers中
            if layer_result['features']:
                self.layers[layer_result['name']] = layer
                print(f"成功解析图层: {layer_result['name']}, 要素数量: {len(layer_result['features'])}")
            else:
                print(f"跳过空图层: {layer_result['name']}")
                
        except Exception as e:
            print(f"创建图层时出错: {e}")
    
    def _skip_field(self, wire_type: int):
        """跳过未知字段"""
        if wire_type == 0:  # varint
            self.pbf.read_varint()
        elif wire_type == 1:  # 64-bit
            self.pbf.read_bytes(8)
        elif wire_type == 2:  # length-delimited
            length = self.pbf.read_varint()
            self.pbf.read_bytes(length)
        elif wire_type == 5:  # 32-bit
            self.pbf.read_bytes(4)
    
    def get_layer(self, name: str) -> Optional[VectorTileLayer]:
        """获取指定名称的图层"""
        return self.layers.get(name)
    
    def get_layer_names(self) -> list:
        """获取所有图层名称"""
        return list(self.layers.keys())
    
    def get_feature_count(self) -> int:
        """获取所有图层的要素总数"""
        total = 0
        for layer in self.layers.values():
            total += len(layer.features)
        return total

class VectorTileFactory:
    """矢量瓦片工厂类 - 对应JS中的_y对象"""
    
    @staticmethod
    def create_vector_tile(pbf_data: bytes, extent: int = 4096) -> VectorTile:
        """
        创建矢量瓦片对象
        
        参数:
        pbf_data: PBF二进制数据
        extent: 瓦片范围，默认为4096
        
        返回:
        VectorTile对象
        """
        pbf_reader = PBFReader(pbf_data)
        return VectorTile(pbf_reader, len(pbf_data), extent)

# 使用示例和参数说明
def demo_vector_tile_usage():
    """演示VectorTile的使用方法"""
    print("VectorTile 使用示例")
    print("=" * 50)
    
    print("参数说明:")
    print("1. t (pbf_reader): PBF读取器对象")
    print("   - 来源: 网络请求的响应数据")
    print("   - 创建: new PBF(response_data)")
    print("   - 作用: 读取二进制PBF数据")
    print()
    
    print("2. e (end_pos): 数据结束位置")
    print("   - 来源: 瓦片数据的长度信息")
    print("   - 计算: 当前读取位置 + 数据长度")
    print("   - 作用: 确定当前瓦片的读取范围")
    print()
    
    print("3. r (extent): 瓦片范围")
    print("   - 来源: 瓦片规范，通常是4096")
    print("   - 含义: 瓦片坐标系的范围")
    print("   - 作用: 用于坐标转换和几何计算")
    print()
    
    print("使用流程:")
    print("1. 从网络请求获取PBF数据")
    print("2. 创建PBF读取器")
    print("3. 创建VectorTile对象")
    print("4. 解析图层和要素")
    print("5. 访问解析后的数据")
    print()

def create_sample_vector_tile():
    """创建示例矢量瓦片数据"""
    print("创建示例矢量瓦片...")
    
    # 从网络获取真实的PBF数据
    from network_request_handler import get_pbf_data_from_network
    
    tile_url = "https://map.sgcc.com.cn:21610/v1/aegis.SGPoi-Web.nBnK,aegis.SGAnchor-Web.nBnK,aegis.SGPolygon-Web.rynK,aegis.SGLine-Web.nBnK/15/27191/10533.sg"
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://map.sgcc.com.cn/',
    }
    
    # 获取网络请求的content
    sample_pbf_data = get_pbf_data_from_network(tile_url, headers)
    
    # 如果网络请求失败，使用示例数据
    if sample_pbf_data is None:
        sample_pbf_data = b'\x1a\x08\x08\x01\x12\x04\x74\x65\x73\x74'  # 示例数据
        print("使用示例数据")
    
    try:
        # 创建矢量瓦片
        vector_tile = VectorTileFactory.create_vector_tile(sample_pbf_data)
        
        print(f"解析完成:")
        print(f"- 图层数量: {len(vector_tile.layers)}")
        print(f"- 图层名称: {vector_tile.get_layer_names()}")
        print(f"- 要素总数: {vector_tile.get_feature_count()}")
        
        # 遍历图层
        for layer_name, layer in vector_tile.layers.items():
            print(f"\n图层: {layer_name}")
            print(f"- 要素数量: {len(layer.features)}")
            print(f"- 键数量: {len(layer._keys)}")
            print(f"- 值数量: {len(layer._values)}")
            
            # 显示前几个要素
            for i, feature in enumerate(layer.features[:3]):
                print(f"  要素 {i+1}: {feature.properties}")
                
    except Exception as e:
        print(f"创建矢量瓦片时出错: {e}")

if __name__ == "__main__":
    demo_vector_tile_usage()
    create_sample_vector_tile() 