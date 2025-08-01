#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
矢量瓦片要素解析器
实现与 self.js 中 gy 函数相同的功能
用于解析矢量瓦片中的要素属性
"""

import struct
from typing import Dict, List, Any, Optional

class PBFReader:
    """PBF (Protocol Buffer Binary Format) 读取器"""
    
    def __init__(self, data: bytes):
        self.data = data
        self.pos = 0
        
    def read_varint(self) -> int:
        """读取变长整数"""
        result = 0
        shift = 0
        while True:
            if self.pos >= len(self.data):
                raise EOFError("数据读取完毕")
            byte = self.data[self.pos]
            self.pos += 1
            result |= (byte & 0x7F) << shift
            if (byte & 0x80) == 0:
                break
            shift += 7
        return result
    
    def read_bytes(self, length: int) -> bytes:
        """读取指定长度的字节"""
        if self.pos + length > len(self.data):
            raise EOFError("数据读取完毕")
        result = self.data[self.pos:self.pos + length]
        self.pos += length
        return result
    
    def read_string(self) -> str:
        """读取字符串"""
        length = self.read_varint()
        data = self.read_bytes(length)
        return data.decode('utf-8')
    
    def read_float(self) -> float:
        """读取浮点数"""
        data = self.read_bytes(4)
        return struct.unpack('<f', data)[0]
    
    def read_double(self) -> float:
        """读取双精度浮点数"""
        data = self.read_bytes(8)
        return struct.unpack('<d', data)[0]

class VectorTileFeature:
    """矢量瓦片要素类"""
    
    def __init__(self):
        self.id: Optional[int] = None
        self.properties: Dict[str, Any] = {}
        self.type: Optional[int] = None
        self._geometry: Optional[int] = None
        self._keys: List[str] = []
        self._values: List[Any] = []

class VectorTileParser:
    """矢量瓦片解析器"""
    
    def __init__(self, pbf_data: bytes):
        self.pbf = PBFReader(pbf_data)
        
    def parse_feature(self, feature: VectorTileFeature) -> VectorTileFeature:
        """解析单个要素"""
        while self.pbf.pos < len(self.pbf.data):
            try:
                tag = self.pbf.read_varint()
                wire_type = tag & 0x07
                field_number = tag >> 3
                
                # 调用解析函数
                self._parse_feature_field(field_number, feature, self.pbf)
                
            except EOFError:
                break
            except Exception as e:
                print(f"解析要素时出错: {e}")
                break
                
        return feature
    
    def _parse_feature_field(self, field_number: int, feature: VectorTileFeature, pbf: PBFReader):
        """解析要素字段 - 对应JS中的gy函数"""
        if field_number == 1:  # id
            feature.id = pbf.read_varint()
        elif field_number == 2:  # properties
            self._parse_properties(pbf, feature)
        elif field_number == 3:  # type
            feature.type = pbf.read_varint()
        elif field_number == 4:  # geometry
            feature._geometry = pbf.pos
        else:
            # 跳过未知字段
            self._skip_field(pbf, wire_type)
    
    def _parse_properties(self, pbf: PBFReader, feature: VectorTileFeature):
        """解析属性键值对 - 对应JS中的匿名函数"""
        # 读取属性数据长度
        end_pos = pbf.read_varint() + pbf.pos
        
        while pbf.pos < end_pos:
            try:
                # 读取键索引
                key_index = pbf.read_varint()
                # 读取值索引
                value_index = pbf.read_varint()
                
                # 从_keys和_values数组中获取实际的键值
                if key_index < len(feature._keys) and value_index < len(feature._values):
                    key = feature._keys[key_index]
                    value = feature._values[value_index]
                    feature.properties[key] = value
                else:
                    print(f"警告: 键索引 {key_index} 或值索引 {value_index} 超出范围")
                    
            except Exception as e:
                print(f"解析属性时出错: {e}")
                break
    
    def _skip_field(self, pbf: PBFReader, wire_type: int):
        """跳过未知字段"""
        if wire_type == 0:  # varint
            pbf.read_varint()
        elif wire_type == 1:  # 64-bit
            pbf.read_bytes(8)
        elif wire_type == 2:  # length-delimited
            length = pbf.read_varint()
            pbf.read_bytes(length)
        elif wire_type == 5:  # 32-bit
            pbf.read_bytes(4)

class VectorTileLayer:
    """矢量瓦片图层类"""
    
    def __init__(self, pbf_data: bytes):
        self.pbf = PBFReader(pbf_data)
        self.version: Optional[int] = None
        self.name: str = ""
        self.extent: int = 4096
        self.features: List[VectorTileFeature] = []
        self._keys: List[str] = []
        self._values: List[Any] = []
        
    def parse_layer(self) -> Dict[str, Any]:
        """解析整个图层"""
        while self.pbf.pos < len(self.pbf.data):
            try:
                tag = self.pbf.read_varint()
                wire_type = tag & 0x07
                field_number = tag >> 3
                
                if field_number == 15:  # version
                    self.version = self.pbf.read_varint()
                elif field_number == 1:  # name
                    self.name = self.pbf.read_string()
                elif field_number == 5:  # extent
                    self.extent = self.pbf.read_varint()
                elif field_number == 2:  # features
                    feature = self._parse_feature()
                    if feature:
                        self.features.append(feature)
                elif field_number == 3:  # keys
                    self._keys.append(self.pbf.read_string())
                elif field_number == 4:  # values
                    value = self._parse_value()
                    self._values.append(value)
                else:
                    self._skip_field(wire_type)
                    
            except EOFError:
                break
            except Exception as e:
                print(f"解析图层时出错: {e}")
                break
        
        return {
            'version': self.version,
            'name': self.name,
            'extent': self.extent,
            'features': [self._feature_to_dict(f) for f in self.features],
            'keys': self._keys,
            'values': self._values
        }
    
    def _parse_feature(self) -> Optional[VectorTileFeature]:
        """解析单个要素"""
        try:
            feature = VectorTileFeature()
            feature._keys = self._keys
            feature._values = self._values
            
            # 读取要素数据长度
            end_pos = self.pbf.read_varint() + self.pbf.pos
            
            while self.pbf.pos < end_pos:
                tag = self.pbf.read_varint()
                wire_type = tag & 0x07
                field_number = tag >> 3
                
                self._parse_feature_field(field_number, feature)
                
            return feature
            
        except Exception as e:
            print(f"解析要素时出错: {e}")
            return None
    
    def _parse_feature_field(self, field_number: int, feature: VectorTileFeature):
        """解析要素字段"""
        if field_number == 1:  # id
            feature.id = self.pbf.read_varint()
        elif field_number == 2:  # properties
            self._parse_properties(feature)
        elif field_number == 3:  # type
            feature.type = self.pbf.read_varint()
        elif field_number == 4:  # geometry
            feature._geometry = self.pbf.pos
        else:
            self._skip_field(wire_type)
    
    def _parse_properties(self, feature: VectorTileFeature):
        """解析属性键值对"""
        end_pos = self.pbf.read_varint() + self.pbf.pos
        
        while self.pbf.pos < end_pos:
            try:
                key_index = self.pbf.read_varint()
                value_index = self.pbf.read_varint()
                
                if key_index < len(self._keys) and value_index < len(self._values):
                    key = self._keys[key_index]
                    value = self._values[value_index]
                    feature.properties[key] = value
                    
            except Exception as e:
                print(f"解析属性时出错: {e}")
                break
    
    def _parse_value(self) -> Any:
        """解析值"""
        tag = self.pbf.read_varint()
        wire_type = tag & 0x07
        field_number = tag >> 3
        
        if field_number == 1:  # string
            return self.pbf.read_string()
        elif field_number == 2:  # float
            return self.pbf.read_float()
        elif field_number == 3:  # double
            return self.pbf.read_double()
        elif field_number == 4:  # int64
            return self.pbf.read_varint()
        elif field_number == 5:  # uint64
            return self.pbf.read_varint()
        elif field_number == 6:  # sint64
            return self.pbf.read_varint()
        elif field_number == 7:  # bool
            return bool(self.pbf.read_varint())
        else:
            return None
    
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
    
    def _feature_to_dict(self, feature: VectorTileFeature) -> Dict[str, Any]:
        """将要素转换为字典"""
        result = {
            'properties': feature.properties
        }
        if feature.id is not None:
            result['id'] = feature.id
        if feature.type is not None:
            result['type'] = feature.type
        if feature._geometry is not None:
            result['_geometry'] = feature._geometry
        return result

def parse_vector_tile_layer(pbf_data: bytes) -> Dict[str, Any]:
    """解析矢量瓦片图层"""
    layer = VectorTileLayer(pbf_data)
    return layer.parse_layer()

# 使用示例
if __name__ == "__main__":
    print("矢量瓦片要素解析器")
    print("=" * 50)
    
    # 示例用法
    # 你需要提供实际的矢量瓦片PBF数据
    # pbf_file = "vector_tile.pbf"
    # with open(pbf_file, 'rb') as f:
    #     pbf_data = f.read()
    # 
    # result = parse_vector_tile_layer(pbf_data)
    # print(f"图层名称: {result['name']}")
    # print(f"要素数量: {len(result['features'])}")
    # print(f"键数量: {len(result['keys'])}")
    # print(f"值数量: {len(result['values'])}")
    # 
    # # 显示前几个要素的属性
    # for i, feature in enumerate(result['features'][:3]):
    #     print(f"\n要素 {i+1}:")
    #     print(f"  ID: {feature.get('id', 'N/A')}")
    #     print(f"  类型: {feature.get('type', 'N/A')}")
    #     print(f"  属性: {feature['properties']}") 