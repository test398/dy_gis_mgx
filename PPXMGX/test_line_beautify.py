#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
连线美化算法测试和使用示例
"""

import json
import os
import sys
from typing import List, Dict

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from meihua2_optimized import LineBeautifier, output1_optimized
from utils.beautify_config import BeautifyConfig, calculate_aesthetic_score, get_optimal_path_type

def test_line_beautifier():
    """测试连线美化器"""
    print("=== 连线美化器测试 ===")
    
    # 模拟建筑物坐标
    building_coords = {
        'building1': [[118.946388, 34.565009], 180, 100],
        'building2': [[118.946500, 34.565100], 90, 80],
        'building3': [[118.946600, 34.565200], 45, 60]
    }
    
    # 初始化美化器
    beautifier = LineBeautifier(building_coords, 'test_token')
    
    # 测试不同路径类型
    start_point = [118.946300, 34.565000]
    end_point = [118.946700, 34.565300]
    
    print(f"起点: {start_point}")
    print(f"终点: {end_point}")
    
    # 测试贝塞尔曲线
    bezier_path = beautifier.generate_bezier_curve(start_point, end_point)
    print(f"贝塞尔曲线路径点数: {len(bezier_path)}")
    print(f"贝塞尔曲线路径: {bezier_path[:3]}...")  # 只显示前3个点
    
    # 测试正交路径
    orthogonal_path = beautifier.generate_orthogonal_path(start_point, end_point)
    print(f"正交路径点数: {len(orthogonal_path)}")
    print(f"正交路径: {orthogonal_path}")
    
    # 测试避障路径
    obstacles = [
        [[118.946400, 34.565050], [118.946450, 34.565050], 
         [118.946450, 34.565150], [118.946400, 34.565150]]
    ]
    avoidance_path = beautifier.generate_avoidance_path(start_point, end_point, obstacles)
    print(f"避障路径点数: {len(avoidance_path)}")
    print(f"避障路径: {avoidance_path}")
    
    # 测试最优路径生成
    optimal_path = beautifier.generate_optimal_path(start_point, end_point, 'bezier')
    print(f"最优路径点数: {len(optimal_path)}")
    print(f"最优路径: {optimal_path[:3]}...")

def test_aesthetic_scoring():
    """测试美学评分"""
    print("\n=== 美学评分测试 ===")
    
    # 测试不同质量的路径
    test_paths = {
        '直线': [[118.946300, 34.565000], [118.946700, 34.565300]],
        '折线': [[118.946300, 34.565000], [118.946500, 34.565100], [118.946700, 34.565300]],
        '曲线': [[118.946300, 34.565000], [118.946400, 34.565150], [118.946600, 34.565150], [118.946700, 34.565300]]
    }
    
    obstacles = [
        [[118.946400, 34.565050], [118.946450, 34.565050], 
         [118.946450, 34.565150], [118.946400, 34.565150]]
    ]
    
    for path_name, path in test_paths.items():
        score = calculate_aesthetic_score(path, obstacles)
        print(f"{path_name}美学评分: {score:.3f}")

def test_path_type_selection():
    """测试路径类型选择"""
    print("\n=== 路径类型选择测试 ===")
    
    test_cases = [
        (0.00005, 'power_line', 'flat'),
        (0.0002, 'communication_line', 'hilly'),
        (0.0008, 'distribution_line', 'urban'),
        (0.0001, 'power_line', 'mountainous')
    ]
    
    for distance, line_type, terrain_type in test_cases:
        path_type = get_optimal_path_type(distance, line_type, terrain_type)
        print(f"距离: {distance}, 线路类型: {line_type}, 地形: {terrain_type} -> 推荐路径类型: {path_type}")

def test_with_real_data():
    """使用真实数据测试"""
    print("\n=== 真实数据测试 ===")
    
    # 模拟真实的GIS数据
    sample_data = [
        {
            'properties': {
                'psrType': 'dywlgt',
                'id': 'device1',
                'connection': 'conn1'
            },
            'geometry': {
                'type': 'Point',
                'coordinates': [118.946300, 34.565000]
            }
        },
        {
            'properties': {
                'psrType': '3218000',
                'id': 'device2',
                'connection': 'conn1,conn2'
            },
            'geometry': {
                'type': 'Point',
                'coordinates': [118.946500, 34.565100]
            }
        },
        {
            'properties': {
                'psrType': '3112',
                'id': 'device3',
                'connection': 'conn2'
            },
            'geometry': {
                'type': 'Point',
                'coordinates': [118.946700, 34.565200]
            }
        },
        {
            'properties': {
                'psrType': '3201',
                'id': 'line1',
                'connection': 'conn1,conn2'
            },
            'geometry': {
                'type': 'LineString',
                'coordinates': [[118.946300, 34.565000], [118.946700, 34.565200]]
            }
        }
    ]
    
    # 模拟建筑物坐标
    building_coords = {
        'building1': [[118.946400, 34.565050], 180, 100],
        'building2': [[118.946600, 34.565150], 90, 80]
    }
    
    try:
        # 测试优化后的处理函数
        result_path = output1_optimized(
            sample_data, 
            'test_psr', 
            [118.946500, 34.565100], 
            'test_token',
            building_coords
        )
        print(f"处理结果保存到: {result_path}")
        
        # 读取并显示结果
        if os.path.exists(result_path):
            with open(result_path, 'r', encoding='utf-8') as f:
                result_data = json.load(f)
            
            print(f"处理后的特征数量: {len(result_data['features'])}")
            
            # 显示连线信息
            for feature in result_data['features']:
                if feature['geometry']['type'] == 'LineString':
                    coords = feature['geometry']['coordinates']
                    print(f"连线 {feature['properties']['id']}: {len(coords)} 个坐标点")
                    if len(coords) > 2:
                        print(f"  路径示例: {coords[:3]}...")
                    
    except Exception as e:
        print(f"测试过程中出现错误: {e}")

def compare_algorithms():
    """比较不同算法的效果"""
    print("\n=== 算法比较测试 ===")
    
    start_point = [118.946300, 34.565000]
    end_point = [118.946700, 34.565300]
    
    building_coords = {
        'building1': [[118.946400, 34.565050], 180, 100]
    }
    
    beautifier = LineBeautifier(building_coords, 'test_token')
    
    algorithms = {
        '直线': [start_point, end_point],
        '贝塞尔曲线': beautifier.generate_bezier_curve(start_point, end_point),
        '正交路径': beautifier.generate_orthogonal_path(start_point, end_point),
        '避障路径': beautifier.generate_avoidance_path(start_point, end_point, []),
        '最优路径': beautifier.generate_optimal_path(start_point, end_point, 'bezier')
    }
    
    obstacles = [
        [[118.946400, 34.565050], [118.946450, 34.565050], 
         [118.946450, 34.565150], [118.946400, 34.565150]]
    ]
    
    print("算法效果比较:")
    print(f"{'算法名称':<12} {'点数':<6} {'美学评分':<10} {'路径长度':<12}")
    print("-" * 50)
    
    for name, path in algorithms.items():
        score = calculate_aesthetic_score(path, obstacles)
        
        # 计算路径长度
        path_length = 0
        for i in range(len(path) - 1):
            path_length += haversine_distance(path[i], path[i+1])
        
        print(f"{name:<12} {len(path):<6} {score:<10.3f} {path_length:<12.2f}")

def generate_optimization_report():
    """生成优化建议报告"""
    print("\n=== 优化建议报告 ===")
    
    recommendations = [
        {
            'category': '算法优化',
            'items': [
                '使用贝塞尔曲线替代直线连接，提升视觉美感',
                '实现自适应路径类型选择，根据距离和地形选择最优算法',
                '添加建筑物避障功能，避免连线穿过建筑物',
                '实现路径平滑处理，减少锯齿状连线',
                '优化路径简化算法，去除冗余点'
            ]
        },
        {
            'category': '性能优化',
            'items': [
                '实现并行处理，提高大批量数据处理速度',
                '添加路径缓存机制，避免重复计算',
                '优化距离计算算法，使用更高效的地理计算方法',
                '实现增量更新，只处理变化的部分'
            ]
        },
        {
            'category': '质量提升',
            'items': [
                '添加美学评分系统，量化连线质量',
                '实现多种路径生成策略，适应不同场景',
                '支持自定义美化规则和参数',
                '添加质量检查和自动修正功能'
            ]
        },
        {
            'category': '下一步工作',
            'items': [
                '集成建筑物识别模块，自动获取建筑物边界',
                '实现智能路径规划，考虑地形和土地利用',
                '添加用户交互界面，支持手动调整',
                '实现批量处理功能，支持大规模数据',
                '添加导出功能，支持多种格式输出'
            ]
        }
    ]
    
    for category in recommendations:
        print(f"\n{category['category']}:")
        for i, item in enumerate(category['items'], 1):
            print(f"  {i}. {item}")

if __name__ == "__main__":
    print("连线美化算法测试和优化建议")
    print("=" * 50)
    
    # 运行所有测试
    test_line_beautifier()
    test_aesthetic_scoring()
    test_path_type_selection()
    test_with_real_data()
    compare_algorithms()
    generate_optimization_report()
    
    print("\n" + "=" * 50)
    print("测试完成！") 