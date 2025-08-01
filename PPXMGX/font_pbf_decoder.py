#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
字体PBF文件解码器
用于解码 mapbox-gl-js 使用的字体PBF文件
"""

import struct
import base64
import json
from typing import Dict, List, Any, Optional

class PBFDecoder:
    """PBF (Protocol Buffer Binary Format) 解码器"""
    
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
    
    def read_bytes(self, length: int) -> bytes:
        """读取指定长度的字节"""
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

class GlyphPBFDecoder:
    """字体字形PBF解码器"""
    
    def __init__(self, pbf_data: bytes):
        self.pbf = PBFDecoder(pbf_data)
        
    def decode_glyphs(self) -> Dict[str, Any]:
        """解码字体字形数据"""
        result = {
            'glyphs': {},
            'ascender': 0,
            'descender': 0
        }
        
        while self.pbf.pos < len(self.pbf.data):
            try:
                tag = self.pbf.read_varint()
                wire_type = tag & 0x07
                field_number = tag >> 3
                
                if field_number == 1:  # glyphs
                    glyph = self._decode_glyph()
                    if glyph:
                        result['glyphs'][str(glyph['id'])] = glyph
                elif field_number == 2:  # ascender
                    result['ascender'] = self.pbf.read_float()
                elif field_number == 3:  # descender
                    result['descender'] = self.pbf.read_float()
                else:
                    # 跳过未知字段
                    if wire_type == 0:  # varint
                        self.pbf.read_varint()
                    elif wire_type == 1:  # 64-bit
                        self.pbf.read_bytes(8)
                    elif wire_type == 2:  # length-delimited
                        length = self.pbf.read_varint()
                        self.pbf.read_bytes(length)
                    elif wire_type == 5:  # 32-bit
                        self.pbf.read_bytes(4)
                        
            except Exception as e:
                print(f"解码错误: {e}")
                break
                
        return result
    
    def _decode_glyph(self) -> Optional[Dict[str, Any]]:
        """解码单个字形"""
        try:
            glyph = {}
            start_pos = self.pbf.pos
            length = self.pbf.read_varint()
            end_pos = self.pbf.pos + length
            
            while self.pbf.pos < end_pos:
                tag = self.pbf.read_varint()
                wire_type = tag & 0x07
                field_number = tag >> 3
                
                if field_number == 1:  # id
                    glyph['id'] = self.pbf.read_varint()
                elif field_number == 2:  # bitmap
                    bitmap_length = self.pbf.read_varint()
                    glyph['bitmap'] = self.pbf.read_bytes(bitmap_length)
                elif field_number == 3:  # width
                    glyph['width'] = self.pbf.read_varint()
                elif field_number == 4:  # height
                    glyph['height'] = self.pbf.read_varint()
                elif field_number == 5:  # left
                    glyph['left'] = self.pbf.read_varint()
                elif field_number == 6:  # top
                    glyph['top'] = self.pbf.read_varint()
                elif field_number == 7:  # advance
                    glyph['advance'] = self.pbf.read_varint()
                else:
                    # 跳过未知字段
                    if wire_type == 0:
                        self.pbf.read_varint()
                    elif wire_type == 1:
                        self.pbf.read_bytes(8)
                    elif wire_type == 2:
                        length = self.pbf.read_varint()
                        self.pbf.read_bytes(length)
                    elif wire_type == 5:
                        self.pbf.read_bytes(4)
            
            return glyph if 'id' in glyph else None
            
        except Exception as e:
            print(f"字形解码错误: {e}")
            return None

def decode_font_pbf(pbf_data: bytes) -> Dict[str, Any]:
    """解码字体PBF文件"""
    decoder = GlyphPBFDecoder(pbf_data)
    return decoder.decode_glyphs()

def save_glyphs_to_json(glyphs_data: Dict[str, Any], output_file: str):
    """将解码的字形数据保存为JSON文件"""
    # 转换bitmap为base64以便JSON序列化
    result = {
        'ascender': glyphs_data['ascender'],
        'descender': glyphs_data['descender'],
        'glyphs': {}
    }
    
    for glyph_id, glyph in glyphs_data['glyphs'].items():
        glyph_copy = glyph.copy()
        if 'bitmap' in glyph_copy:
            glyph_copy['bitmap'] = base64.b64encode(glyph_copy['bitmap']).decode('utf-8')
        result['glyphs'][glyph_id] = glyph_copy
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"字形数据已保存到: {output_file}")

def analyze_glyph_bitmap(glyph: Dict[str, Any]) -> str:
    """分析字形位图数据"""
    if 'bitmap' not in glyph or 'width' not in glyph or 'height' not in glyph:
        return "无法分析位图"
    
    bitmap = glyph['bitmap']
    width = glyph['width']
    height = glyph['height']
    
    # 简单的位图可视化
    result = f"字形ID: {glyph.get('id', 'unknown')}\n"
    result += f"尺寸: {width}x{height}\n"
    result += f"位置: left={glyph.get('left', 0)}, top={glyph.get('top', 0)}\n"
    result += f"前进宽度: {glyph.get('advance', 0)}\n"
    result += f"位图大小: {len(bitmap)} 字节\n"
    
    return result

# 使用示例
if __name__ == "__main__":
    # 从HAR文件或网络请求中获取的PBF数据
    # 这里需要你提供实际的PBF二进制数据
    
    print("字体PBF解码器")
    print("=" * 50)
    print("请提供PBF二进制数据文件路径:")
    import requests

    headers = {
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Authorization': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJJc3N1YW5jZSI6IlkiLCJhcHBJZCI6IjhkYzU0OThiZDcxMDMzYTA5OTJlNGQ3NzhhMDZlN2UzIiwiY2xpZW50SXAiOiIyMjMuNjUuNTcuMTYzIiwiZXhwIjoxNzUxOTM5MDUwLCJpYXQiOjE3NTE5MzU0NTAsImlzcyI6Ind3dy5hZWdpcy5jb20iLCJqdGkiOiJIUk9LVlRFTEhDIiwic2NvcGVzIjo3LCJzdWIiOiI2Yzc5MDUwYTI5ODAzMTE4OTlkY2U3NzQ5MzI4OGI5MiIsInN1YlR5cGUiOiJhcHBrZXkiLCJ0b2tlblRUTCI6MzYwMDAwMCwidXNlck5hbWUiOiJ3ancifQ.fViVRk_3Qv6hEyVm_SPuYEWQAutnwZTUVRDYnmQkXIA',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Referer': 'https://map.sgcc.com.cn/products/js-sdk/v3/example.html?t=capability',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0',
        'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Microsoft Edge";v="138"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    response = requests.get('https://map.sgcc.com.cn/fonts/v1/aegis/Microsoft%20YaHei%20Regular/65024-65279.pbf', headers=headers, proxies={'http': 'http://127.0.0.1:7890', 'https': 'http://127.0.0.1:7890'})
    
    # 示例用法
    # pbf_file = "font_data.pbf"
    # with open(pbf_file, 'rb') as f:
    #     pbf_data = f.read()
    # 
    pbf_data = response.content
    decoded_data = decode_font_pbf(pbf_data)
    print(f"解码完成，共找到 {len(decoded_data['glyphs'])} 个字形")
    
    # 保存为JSON
    save_glyphs_to_json(decoded_data, "decoded_glyphs.json")
    
    # 分析前几个字形
    for i, (glyph_id, glyph) in enumerate(list(decoded_data['glyphs'].items())[:5]):
        print(f"\n字形 {i+1}:")
        print(analyze_glyph_bitmap(glyph)) 