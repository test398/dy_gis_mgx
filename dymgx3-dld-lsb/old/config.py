#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置文件 - 统一管理所有脚本的路径和参数
"""

import os

class Config:
    """配置类，统一管理所有路径和参数"""
    
    def __init__(self, base_dir=None):
        # 基础目录设置
        if base_dir is None:
            self.base_dir = os.path.dirname(os.path.abspath(__file__))
        else:
            self.base_dir = base_dir
        
        # 数据目录
        self.data_dir = os.path.join(self.base_dir, 'data')
        
        # 输出目录
        self.output_dir = os.path.join(self.base_dir, 'output')
        self.charts_dir = os.path.join(self.output_dir, 'charts')
        self.scatter_plots_dir = os.path.join(self.charts_dir, 'scatter_plots')
        self.single_results_dir = os.path.join(self.output_dir, 'single_results')
        
        # 字体目录
        self.fonts_dir = os.path.join(self.base_dir, 'fonts')
        
        # 数据文件路径配置
        self.data_files = {
            # 机器评分数据文件（按优先级排序）
            'machine_scores': [
                os.path.join(self.base_dir, '机器评分结果869_改进版.csv'),
            ],
            
            # 人工评分数据文件（按优先级排序）
            'human_scores': [
                os.path.join(self.base_dir, '人工评分结果869.csv')
            ],
            
            # 台区JSON数据文件（示例文件）
            'taiqu_json': [
                os.path.join(self.data_dir, '5000000430157_zlh.json')
            ],
            
            # 台区JSON数据目录
            'taiqu_json_dir': [
                self.data_dir
            ]
        }
        
        # 字体配置
        self.font_config = {
            'font_path': os.path.join(self.fonts_dir, 'SimHei.ttf'),
            'font_url': 'https://github.com/StellarCN/scp_zh/raw/master/fonts/SimHei.ttf',
            'fallback_fonts': ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
        }
        
        # 图表配置
        self.chart_config = {
            'dpi': 300,
            'figsize': (12, 10),
            'bbox_inches': 'tight'
        }
        
        # 创建必要的目录
        self._create_directories()
    
    def _create_directories(self):
        """创建必要的目录"""
        directories = [
            self.data_dir,
            self.output_dir,
            self.charts_dir,
            self.scatter_plots_dir,
            self.single_results_dir,
            self.fonts_dir
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def get_existing_file(self, file_type):
        """获取存在的文件路径"""
        if file_type not in self.data_files:
            return None
        
        for file_path in self.data_files[file_type]:
            if os.path.exists(file_path):
                return file_path
        
        return None
    
    def get_existing_directory(self, dir_type):
        """获取存在的目录路径"""
        if dir_type not in self.data_files:
            return None
        
        for dir_path in self.data_files[dir_type]:
            if os.path.exists(dir_path) and os.path.isdir(dir_path):
                return dir_path
        
        return None
    
    def print_config_info(self):
        """打印配置信息"""
        print("=== 配置信息 ===")
        print(f"基础目录: {self.base_dir}")
        print(f"数据目录: {self.data_dir}")
        print(f"输出目录: {self.output_dir}")
        print(f"字体目录: {self.fonts_dir}")
        
        print("\n=== 数据文件检查 ===")
        machine_file = self.get_existing_file('machine_scores')
        human_file = self.get_existing_file('human_scores')
        taiqu_dir = self.get_existing_directory('taiqu_json_dir')
        
        print(f"机器评分文件: {'✓' if machine_file else '✗'} {machine_file or '未找到'}")
        print(f"人工评分文件: {'✓' if human_file else '✗'} {human_file or '未找到'}")
        print(f"台区JSON目录: {'✓' if taiqu_dir else '✗'} {taiqu_dir or '未找到'}")

# 创建全局配置实例
config = Config()

# 导出常用路径
DATA_DIR = config.data_dir
OUTPUT_DIR = config.output_dir
CHARTS_DIR = config.charts_dir
FONTS_DIR = config.fonts_dir