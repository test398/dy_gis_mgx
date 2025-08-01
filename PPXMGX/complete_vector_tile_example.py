#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整的矢量瓦片解析示例
展示从网络请求到解析的完整流程
"""

import requests
import base64
from typing import Dict, Any
from vector_tile_constructor import VectorTileFactory

def fetch_vector_tile(url: str, headers: Dict[str, str] = None) -> bytes:
    """
    从网络获取矢量瓦片数据
    
    参数:
    url: 矢量瓦片URL
    headers: 请求头
    
    返回:
    PBF二进制数据
    """
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.content
    except Exception as e:
        print(f"获取矢量瓦片失败: {e}")
        return None

def parse_vector_tile_from_har(har_response_text: str) -> bytes:
    """
    从HAR文件中的响应内容解析PBF数据
    
    参数:
    har_response_text: HAR文件中base64编码的响应内容
    
    返回:
    PBF二进制数据
    """
    try:
        # 解码base64数据
        pbf_data = base64.b64decode(har_response_text)
        return pbf_data
    except Exception as e:
        print(f"解析HAR响应失败: {e}")
        return None

def analyze_vector_tile(vector_tile) -> Dict[str, Any]:
    """
    分析矢量瓦片内容
    
    参数:
    vector_tile: VectorTile对象
    
    返回:
    分析结果字典
    """
    analysis = {
        'layer_count': len(vector_tile.layers),
        'layer_names': vector_tile.get_layer_names(),
        'total_features': vector_tile.get_feature_count(),
        'layers': {}
    }
    
    for layer_name, layer in vector_tile.layers.items():
        layer_analysis = {
            'feature_count': len(layer.features),
            'key_count': len(layer._keys),
            'value_count': len(layer._values),
            'keys': layer._keys,
            'sample_features': []
        }
        
        # 添加前3个要素作为示例
        for i, feature in enumerate(layer.features[:3]):
            layer_analysis['sample_features'].append({
                'id': feature.id,
                'type': feature.type,
                'properties': feature.properties
            })
        
        analysis['layers'][layer_name] = layer_analysis
    
    return analysis

def demo_complete_workflow():
    """演示完整的矢量瓦片解析流程"""
    print("完整的矢量瓦片解析流程")
    print("=" * 60)
    
    # 方法1: 从网络请求获取数据
    print("方法1: 从网络请求获取矢量瓦片")
    print("-" * 40)
    
    # 示例URL（你需要替换为实际的URL）
    tile_url = "https://map.sgcc.com.cn/v1/aegis.SGPoi-Web.nBnK,aegis.SGAnchor-Web.nBnK,aegis.SGPolygon-Web.rynK,aegis.SGLine-Web.nBnK/12/3399/1316.sg"
    
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Authorization': 'your_auth_token_here',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://map.sgcc.com.cn/',
    }
    
    print(f"请求URL: {tile_url}")
    print("正在获取数据...")
    
    # 获取PBF数据
    pbf_data = fetch_vector_tile(tile_url, headers)
    
    if pbf_data:
        print(f"获取成功，数据大小: {len(pbf_data)} 字节")
        
        # 创建矢量瓦片对象
        vector_tile = VectorTileFactory.create_vector_tile(pbf_data)
        
        # 分析结果
        analysis = analyze_vector_tile(vector_tile)
        
        print("\n解析结果:")
        print(f"- 图层数量: {analysis['layer_count']}")
        print(f"- 图层名称: {analysis['layer_names']}")
        print(f"- 要素总数: {analysis['total_features']}")
        
        # 显示每个图层的详细信息
        for layer_name, layer_info in analysis['layers'].items():
            print(f"\n图层: {layer_name}")
            print(f"  - 要素数量: {layer_info['feature_count']}")
            print(f"  - 键数量: {layer_info['key_count']}")
            print(f"  - 值数量: {layer_info['value_count']}")
            print(f"  - 键列表: {layer_info['keys']}")
            
            # 显示示例要素
            for i, feature in enumerate(layer_info['sample_features']):
                print(f"  - 要素 {i+1}:")
                print(f"    ID: {feature['id']}")
                print(f"    类型: {feature['type']}")
                print(f"    属性: {feature['properties']}")
    
    else:
        print("获取数据失败")
    
    print("\n" + "=" * 60)
    
    # 方法2: 从HAR文件解析数据
    print("方法2: 从HAR文件解析矢量瓦片")
    print("-" * 40)
    
    # 示例HAR响应内容（你需要替换为实际的内容）
    har_response_text = "NjZiZQf3AQgsCQYKByIICfwIggcKAgASNQj7AhgCEhoAAAEAAroDA7sDBAIFhAIGAAf3AQgsCQYKByISCdIevgMyHQ0DAwABBQkfBxU"
    
    print("正在解析HAR响应...")
    
    # 解析PBF数据
    pbf_data = parse_vector_tile_from_har(har_response_text)
    
    if pbf_data:
        print(f"解析成功，数据大小: {len(pbf_data)} 字节")
        
        # 创建矢量瓦片对象
        vector_tile = VectorTileFactory.create_vector_tile(pbf_data)
        
        # 分析结果
        analysis = analyze_vector_tile(vector_tile)
        
        print("\n解析结果:")
        print(f"- 图层数量: {analysis['layer_count']}")
        print(f"- 图层名称: {analysis['layer_names']}")
        print(f"- 要素总数: {analysis['total_features']}")
        
    else:
        print("解析HAR响应失败")

def save_analysis_to_file(analysis: Dict[str, Any], filename: str):
    """将分析结果保存到文件"""
    import json
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)
        print(f"分析结果已保存到: {filename}")
    except Exception as e:
        print(f"保存文件失败: {e}")

if __name__ == "__main__":
    demo_complete_workflow()
    
    print("\n使用说明:")
    print("1. 替换 tile_url 为实际的矢量瓦片URL")
    print("2. 替换 headers 中的认证信息")
    print("3. 替换 har_response_text 为实际的HAR响应内容")
    print("4. 运行脚本查看解析结果") 