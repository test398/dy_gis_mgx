#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版要素属性解析器
专门实现 self.js 中 gy 函数的功能
"""

from typing import Dict, List, Any

class SimplePBFReader:
    """简化的PBF读取器"""
    
    def __init__(self, data: bytes):
        self.data = data
        self.pos = 0
    
    def read_varint(self) -> int:
        """读取变长整数"""
        result = 0
        shift = 0
        while True:
            byte = self.data[self.pos]
            self.pos += 1
            result |= (byte & 0x7F) << shift
            if (byte & 0x80) == 0:
                break
            shift += 7
        return result

def parse_feature_properties(t: int, e: Dict[str, Any], r: SimplePBFReader, keys: List[str], values: List[Any]):
    """
    解析要素属性 - 对应JS中的gy函数
    
    参数:
    t: 字段号
    e: 要素对象
    r: PBF读取器
    keys: 键数组
    values: 值数组
    """
    if t == 1:  # id
        e['id'] = r.read_varint()
    elif t == 2:  # properties
        parse_properties(r, e, keys, values)
    elif t == 3:  # type
        e['type'] = r.read_varint()
    elif t == 4:  # geometry
        e['_geometry'] = r.pos

def parse_properties(r: SimplePBFReader, e: Dict[str, Any], keys: List[str], values: List[Any]):
    """
    解析属性键值对 - 对应JS中的匿名函数
    
    参数:
    r: PBF读取器
    e: 要素对象
    keys: 键数组
    values: 值数组
    """
    # 读取属性数据长度
    end_pos = r.read_varint() + r.pos
    
    # 初始化properties字典
    if 'properties' not in e:
        e['properties'] = {}
    
    # 循环读取键值对
    while r.pos < end_pos:
        # 读取键索引
        key_index = r.read_varint()
        # 读取值索引
        value_index = r.read_varint()
        
        # 从keys和values数组中获取实际的键值
        if key_index < len(keys) and value_index < len(values):
            key = keys[key_index]
            value = values[value_index]
            e['properties'][key] = value
        else:
            print(f"警告: 键索引 {key_index} 或值索引 {value_index} 超出范围")
            print(f"keys长度: {len(keys)}, values长度: {len(values)}")

# 使用示例
def demo_usage():
    """演示使用方法"""
    print("简化版要素属性解析器")
    print("=" * 40)
    
    # 模拟数据
    # 在实际使用中，这些数据来自PBF文件
    keys = ["name", "type", "color", "size"]
    values = ["测试点", "POI", "red", 10]
    
    # 模拟要素对象
    feature = {}
    
    # 模拟PBF数据（这里只是示例）
    # 实际使用时，你需要提供真实的PBF二进制数据
    pbf_data = b'\x08\x01\x12\x08\x00\x01\x02\x03\x00\x01\x02\x03\x18\x01'
    reader = SimplePBFReader(pbf_data)
    
    print("模拟解析过程:")
    print(f"初始要素: {feature}")
    print(f"键数组: {keys}")
    print(f"值数组: {values}")
    
    # 模拟解析过程
    try:
        while reader.pos < len(reader.data):
            tag = reader.read_varint()
            field_number = tag >> 3
            
            parse_feature_properties(field_number, feature, reader, keys, values)
            
    except Exception as e:
        print(f"解析完成或出错: {e}")
    
    print(f"解析后要素: {feature}")

if __name__ == "__main__":
    demo_usage() 