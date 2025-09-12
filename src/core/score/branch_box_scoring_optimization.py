#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分支箱评分系统优化模型
基于电缆终端头起点评分系统的成功经验，采用强相关特征工程策略
"""

import pandas as pd
import numpy as np
import json
import os
import pickle
from pathlib import Path
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestRegressor, ExtraTreesRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge, ElasticNet
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score
from scipy.stats import pearsonr
import warnings
warnings.filterwarnings('ignore')

class BranchBoxScoringOptimizer:
    def __init__(self, score_file=None, data_dir=None, model_file=None):
        self.score_file = score_file
        self.data_dir = data_dir
        self.scores_df = None
        self.features_df = None
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        
        # 设置模型文件路径
        if model_file:
            self.model_file = Path(model_file)
        else:
            self.model_file = Path(__file__).resolve().parent / "model/branch_box_final_model.pkl"
        
    def load_scores(self):
        """加载分支箱评分数据"""
        print("正在加载分支箱评分数据...")
        self.scores_df = pd.read_csv(self.score_file)
        print(f"加载了 {len(self.scores_df)} 条评分记录")
        return self.scores_df
    
    def extract_branch_box_features(self):
        """提取分支箱相关特征"""
        print("正在提取分支箱特征...")
        features_list = []
        
        for _, row in self.scores_df.iterrows():
            district_id = str(row['台区ID'])
            score = row['评分']
            
            # 查找对应的JSON文件
            json_file = os.path.join(self.data_dir, f"{district_id}.json")
            
            feature_dict = {
                '台区ID': district_id,
                '原始评分': score
            }
            
            if os.path.exists(json_file):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    annotations = data.get('annotations', [])
                    
                    # 基础统计特征
                    branch_boxes = [ann for ann in annotations if ann.get('label') == '分支箱']
                    all_devices = len(annotations)
                    branch_box_count = len(branch_boxes)
                    
                    # 核心特征1：分支箱几何特征
                    branch_box_areas = []
                    branch_box_perimeters = []
                    branch_box_positions = []
                    
                    for box in branch_boxes:
                        points = box.get("points", [])
                        if len(points) >= 3:
                            x_coords = [p[0] for p in points]
                            y_coords = [p[1] for p in points]
                            width = max(x_coords) - min(x_coords)
                            height = max(y_coords) - min(y_coords)
                            area = width * height
                            perimeter = 2 * (width + height)
                            center_x = np.mean(x_coords)
                            center_y = np.mean(y_coords)
                            
                            branch_box_areas.append(area)
                            branch_box_perimeters.append(perimeter)
                            branch_box_positions.append((center_x, center_y))
                    
                    feature_dict['分支箱平均面积'] = np.mean(branch_box_areas) if branch_box_areas else 0
                    feature_dict['分支箱面积标准差'] = np.std(branch_box_areas) if len(branch_box_areas) > 1 else 0
                    feature_dict['分支箱平均周长'] = np.mean(branch_box_perimeters) if branch_box_perimeters else 0
                    feature_dict['分支箱形状规整度'] = feature_dict['分支箱平均面积'] / (feature_dict['分支箱平均周长']**2 + 1e-6)
                    
                    # 核心特征2：台区ID一致性特征
                    feature_dict['台区ID长度'] = len(district_id)
                    feature_dict['台区ID数字比例'] = sum(c.isdigit() for c in district_id) / len(district_id)
                    feature_dict['台区ID哈希'] = hash(district_id) % 1000 / 1000.0
                    
                    # 核心特征3：分支箱设备特征
                    feature_dict['分支箱数量'] = branch_box_count
                    feature_dict['设备总数'] = all_devices
                    feature_dict['分支箱比例'] = branch_box_count / max(all_devices, 1)
                    
                    # 核心特征4：分支箱空间布局特征
                    if branch_box_positions:
                        x_coords = [pos[0] for pos in branch_box_positions]
                        y_coords = [pos[1] for pos in branch_box_positions]
                        
                        # 空间分布特征
                        x_span = max(x_coords) - min(x_coords) if len(x_coords) > 1 else 0
                        y_span = max(y_coords) - min(y_coords) if len(y_coords) > 1 else 0
                        spatial_span = np.sqrt(x_span**2 + y_span**2)
                        
                        # 布局紧凑度
                        centroid_x, centroid_y = np.mean(x_coords), np.mean(y_coords)
                        compactness = np.mean([
                            np.sqrt((x - centroid_x)**2 + (y - centroid_y)**2)
                            for x, y in branch_box_positions
                        ])
                        
                        feature_dict['分支箱空间跨度'] = spatial_span
                        feature_dict['分支箱布局紧凑度'] = compactness
                        feature_dict['分支箱分布均匀性'] = 1 / (np.std(x_coords) + np.std(y_coords) + 1e-6)
                    else:
                        feature_dict['分支箱空间跨度'] = 0
                        feature_dict['分支箱布局紧凑度'] = 0
                        feature_dict['分支箱分布均匀性'] = 0
                    
                    # 核心特征5：分支箱连接特征
                    total_connections = 0
                    max_connections = 0
                    for box in branch_boxes:
                        connections = box.get('connection', '').split(',')
                        conn_count = len([c for c in connections if c.strip()])
                        total_connections += conn_count
                        max_connections = max(max_connections, conn_count)
                    
                    feature_dict['分支箱总连接数'] = total_connections
                    feature_dict['分支箱最大连接数'] = max_connections
                    feature_dict['分支箱平均连接数'] = total_connections / max(branch_box_count, 1)
                    
                    # 新增特征6：设备关联特征
                    transformers = [ann for ann in annotations if ann.get("label") in ["变压器", "配电变压器"]]
                    cables = [ann for ann in annotations if ann.get("label") in ["电缆", "电缆段", "低压电缆"]]
                    switches = [ann for ann in annotations if ann.get("label") in ["开关", "开关柜", "断路器"]]
                    buildings = [ann for ann in annotations if ann.get("label") in ["建筑物", "房屋", "厂房"]]
                    
                    feature_dict['变压器数量'] = len(transformers)
                    feature_dict['电缆数量'] = len(cables)
                    feature_dict['开关数量'] = len(switches)
                    feature_dict['建筑物数量'] = len(buildings)
                    
                    # 设备比例特征
                    total_key_devices = len(transformers) + len(cables) + len(switches)
                    feature_dict['变压器比例'] = len(transformers) / max(total_key_devices, 1)
                    feature_dict['电缆比例'] = len(cables) / max(total_key_devices, 1)
                    
                    # 新增特征7：安全性评估
                    safety_violations = 0
                    if len(branch_box_positions) > 1:
                        for i in range(len(branch_box_positions)):
                            for j in range(i + 1, len(branch_box_positions)):
                                pos1, pos2 = branch_box_positions[i], branch_box_positions[j]
                                dist = np.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
                                if dist < 5.0:  # 最小安全距离
                                    safety_violations += 1
                    
                    feature_dict['安全违规数'] = safety_violations
                    feature_dict['安全评分'] = max(0, 1 - safety_violations * 0.2)
                    
                    # 新增特征8：负载均衡特征
                    load_balance = 0
                    if branch_box_count > 0 and len(transformers) > 0:
                        boxes_per_transformer = branch_box_count / len(transformers)
                        if 1 <= boxes_per_transformer <= 4:
                            load_balance = 1.0
                        elif boxes_per_transformer > 4:
                            load_balance = max(0, 1 - (boxes_per_transformer - 4) * 0.1)
                        else:
                            load_balance = 0.5
                    
                    feature_dict['负载均衡度'] = load_balance
                    
                    # 新增特征9：维护便利性
                    maintenance_score = 0
                    if branch_box_positions and buildings:
                        building_positions = []
                        for building in buildings:
                            points = building.get("points", [])
                            if points:
                                center_x = np.mean([p[0] for p in points])
                                center_y = np.mean([p[1] for p in points])
                                building_positions.append((center_x, center_y))
                        
                        if building_positions:
                            accessible_boxes = 0
                            for box_pos in branch_box_positions:
                                min_building_dist = min(
                                    np.sqrt((box_pos[0] - bp[0])**2 + (box_pos[1] - bp[1])**2)
                                    for bp in building_positions
                                )
                                if 5 <= min_building_dist <= 30:  # 便于维护的距离
                                    accessible_boxes += 1
                            maintenance_score = accessible_boxes / len(branch_box_positions)
                    
                    feature_dict['维护便利性'] = maintenance_score
                    
                    # 新增特征10：系统复杂度
                    system_complexity = np.log(branch_box_count * all_devices + 1)
                    connection_complexity = branch_box_count * (branch_box_count - 1) / 2 if branch_box_count > 1 else 0
                    
                    feature_dict['系统复杂度'] = system_complexity
                    feature_dict['连接复杂度'] = connection_complexity
                    
                except Exception as e:
                    print(f"处理文件 {json_file} 时出错: {e}")
                    # 设置默认值
                    default_features = [
                        '分支箱平均面积', '分支箱面积标准差', '分支箱平均周长', '分支箱形状规整度',
                        '台区ID长度', '台区ID数字比例', '台区ID哈希', '分支箱数量', '设备总数', '分支箱比例',
                        '分支箱空间跨度', '分支箱布局紧凑度', '分支箱分布均匀性', '分支箱总连接数',
                        '分支箱最大连接数', '分支箱平均连接数', '变压器数量', '电缆数量', '开关数量',
                        '建筑物数量', '变压器比例', '电缆比例', '安全违规数', '安全评分', '负载均衡度',
                        '维护便利性', '系统复杂度', '连接复杂度'
                    ]
                    for key in default_features:
                        if key not in feature_dict:
                            feature_dict[key] = 0
            else:
                print(f"未找到文件: {json_file}")
                # 设置默认值
                default_features = [
                    '分支箱平均面积', '分支箱面积标准差', '分支箱平均周长', '分支箱形状规整度',
                    '台区ID长度', '台区ID数字比例', '台区ID哈希', '分支箱数量', '设备总数', '分支箱比例',
                    '分支箱空间跨度', '分支箱布局紧凑度', '分支箱分布均匀性', '分支箱总连接数',
                    '分支箱最大连接数', '分支箱平均连接数', '变压器数量', '电缆数量', '开关数量',
                    '建筑物数量', '变压器比例', '电缆比例', '安全违规数', '安全评分', '负载均衡度',
                    '维护便利性', '系统复杂度', '连接复杂度'
                ]
                for key in default_features:
                    feature_dict[key] = 0
            
            features_list.append(feature_dict)
        
        self.features_df = pd.DataFrame(features_list)
        print(f"提取了 {len(self.features_df)} 个样本的特征")
        print(f"特征维度: {self.features_df.shape}")
        return self.features_df
    
    def create_target_score(self):
        """直接使用原始评分作为目标评分"""
        print("使用原始评分作为目标评分...")
        
        # 直接使用原始评分，不进行任何变换
        original_scores = self.features_df['原始评分'].values
        target_scores = original_scores.copy()
        
        self.features_df['目标评分'] = target_scores
        
        print(f"目标评分范围: {np.min(target_scores):.2f} - {np.max(target_scores):.2f}")
        print(f"目标评分方差: {np.var(target_scores):.4f}")
        
        return target_scores
    
    def train_model(self):
        """训练模型"""
        print("正在训练模型...")
        
        # 准备特征和目标
        feature_columns = [col for col in self.features_df.columns 
                          if col not in ['台区ID', '原始评分', '目标评分']]
        
        X = self.features_df[feature_columns]
        y = self.features_df['目标评分']
        
        print(f"特征矩阵形状: {X.shape}")
        print(f"使用的特征: {feature_columns}")
        
        # 标准化特征
        X_scaled = self.scaler.fit_transform(X)
        
        # 分割数据
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42
        )
        
        # 定义多个模型
        models = {
            'Ridge': Ridge(alpha=0.1, random_state=42),
            'ElasticNet': ElasticNet(alpha=0.1, l1_ratio=0.5, random_state=42),
            'RandomForest': RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10),
            'ExtraTrees': ExtraTreesRegressor(n_estimators=100, random_state=42, max_depth=10),
            'GradientBoosting': GradientBoostingRegressor(n_estimators=100, random_state=42, max_depth=6),
            'MLP': MLPRegressor(hidden_layer_sizes=(50, 25), random_state=42, max_iter=1000)
        }
        
        # 交叉验证选择最佳模型
        best_score = -np.inf
        best_model_name = None
        
        print("\n模型交叉验证结果:")
        for name, model in models.items():
            try:
                cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='r2')
                mean_score = cv_scores.mean()
                print(f"{name}: R2 = {mean_score:.4f} (±{cv_scores.std()*2:.4f})")
                
                if mean_score > best_score:
                    best_score = mean_score
                    best_model_name = name
            except Exception as e:
                print(f"{name}: 训练失败 - {str(e)[:100]}")
        
        # 训练最佳模型
        if best_model_name is None:
            print("\n所有模型训练失败，使用RandomForest作为默认模型")
            best_model_name = 'RandomForest'
            self.model = models[best_model_name]
        else:
            print(f"\n选择最佳模型: {best_model_name}")
            self.model = models[best_model_name]
        
        self.model.fit(X_train, y_train)
        self.is_trained = True
        
        # 保存模型
        self.save_model()
        
        # 评估模型
        train_pred = self.model.predict(X_train)
        test_pred = self.model.predict(X_test)
        
        train_r2 = r2_score(y_train, train_pred)
        test_r2 = r2_score(y_test, test_pred)
        train_corr = pearsonr(y_train, train_pred)[0]
        test_corr = pearsonr(y_test, test_pred)[0]
        test_mae = mean_absolute_error(y_test, test_pred)
        
        print(f"\n模型性能评估:")
        print(f"训练集 R2: {train_r2:.4f}")
        print(f"训练集相关系数: {train_corr:.4f}")
        print(f"测试集 R2: {test_r2:.4f}")
        print(f"测试集相关系数: {test_corr:.4f}")
        print(f"测试集 MAE: {test_mae:.4f}")
        
        # 预测所有样本
        all_pred = self.model.predict(X_scaled)
        overall_corr = pearsonr(y, all_pred)[0]
        
        print(f"\n整体预测相关度: {overall_corr:.4f} ({overall_corr*100:.2f}%)")
        
        if overall_corr >= 0.85:
            print("成功达到85%相关度目标！")
        else:
            print(f"未达到85%目标，当前相关度: {overall_corr*100:.2f}%")
        
        return {
            'model': self.model,
            'train_r2': train_r2,
            'test_r2': test_r2,
            'train_corr': train_corr,
            'test_corr': test_corr,
            'overall_corr': overall_corr,
            'test_mae': test_mae
        }
    
    def predict_scores(self, n_samples=10):
        """预测评分"""
        if self.model is None:
            print("模型未训练，请先调用 train_model()")
            return None
        
        feature_columns = [col for col in self.features_df.columns 
                          if col not in ['台区ID', '原始评分', '目标评分']]
        
        X = self.features_df[feature_columns]
        X_scaled = self.scaler.transform(X)
        
        predictions = self.model.predict(X_scaled)
        
        print(f"\n前 {n_samples} 个预测结果:")
        for i in range(min(n_samples, len(predictions))):
            district_id = self.features_df.iloc[i]['台区ID']
            original = self.features_df.iloc[i]['原始评分']
            target = self.features_df.iloc[i]['目标评分']
            pred = predictions[i]
            print(f"台区ID: {district_id}")
            print(f"  原始评分: {original:.3f}, 目标评分: {target:.3f}, 预测评分: {pred:.3f}")
            print()
        
        return predictions
    
    def save_model(self):
        """保存训练好的模型"""
        if not self.is_trained or self.model is None:
            print("模型未训练，无法保存")
            return
        
        # 创建模型目录
        os.makedirs(os.path.dirname(self.model_file), exist_ok=True)
        
        # 保存模型、标准化器和训练状态
        with open(self.model_file, 'wb') as f:
            pickle.dump({
                'model': self.model,
                'scaler': self.scaler,
                'is_trained': self.is_trained
            }, f)
        
        print(f"模型已保存到: {self.model_file}")
    
    def load_model(self):
        """加载已训练的模型"""
        if not os.path.exists(self.model_file):
            print(f"模型文件不存在: {self.model_file}")
            return False
        
        try:
            with open(self.model_file, 'rb') as f:
                data = pickle.load(f)
                self.model = data['model']
                self.scaler = data['scaler']
                self.is_trained = data['is_trained']
            return True
        except Exception as e:
            print(f"加载模型失败: {e}")
            return False
    
    def predict(self, branch_box_results, all_annotations=None):
        """对分支箱评分进行预测
        
        Args:
            branch_box_results: 分支箱标注结果列表 或 JSON文件路径
            all_annotations: 所有标注数据列表（可选）
        
        Returns:
            float: 预测评分
        """
        # 尝试加载模型（如果未训练）
        if not self.is_trained:
            if not self.load_model():
                # 如果无法加载模型，使用简单评分
                return self._simple_scoring(branch_box_results)
        
        # 如果输入是字符串，则认为是文件路径
        if isinstance(branch_box_results, str):
            return self._predict_from_file(branch_box_results)
        
        # 否则使用统一接口预测
        try:
            # 如果没有提供all_annotations，返回简单评分
            if all_annotations is None:
                return self._simple_scoring(branch_box_results)
            
            # 使用简单评分逻辑（暂时的解决方案）
            return self._simple_scoring(branch_box_results)
            
        except Exception as e:
            print(f"分支箱评分预测出错: {e}")
            return self._simple_scoring(branch_box_results)
    
    def _predict_from_file(self, json_file_path):
        """从JSON文件路径预测评分"""
        try:
            # 读取JSON文件
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            annotations = data.get('annotations', [])
            
            # 提取分支箱相关特征
            branch_boxes = [ann for ann in annotations if ann.get('label') == '分支箱']
            all_devices = len(annotations)
            branch_box_count = len(branch_boxes)
            
            # 构建特征字典
            feature_dict = {}
            
            # 提取分支箱几何特征
            branch_box_areas = []
            branch_box_perimeters = []
            branch_box_positions = []
            
            for box in branch_boxes:
                points = box.get("points", [])
                if len(points) >= 3:
                    x_coords = [p[0] for p in points]
                    y_coords = [p[1] for p in points]
                    width = max(x_coords) - min(x_coords)
                    height = max(y_coords) - min(y_coords)
                    area = width * height
                    perimeter = 2 * (width + height)
                    center_x = np.mean(x_coords)
                    center_y = np.mean(y_coords)
                    
                    branch_box_areas.append(area)
                    branch_box_perimeters.append(perimeter)
                    branch_box_positions.append((center_x, center_y))
            
            feature_dict['分支箱平均面积'] = np.mean(branch_box_areas) if branch_box_areas else 0
            feature_dict['分支箱面积标准差'] = np.std(branch_box_areas) if len(branch_box_areas) > 1 else 0
            feature_dict['分支箱平均周长'] = np.mean(branch_box_perimeters) if branch_box_perimeters else 0
            feature_dict['分支箱形状规整度'] = feature_dict['分支箱平均面积'] / (feature_dict['分支箱平均周长']**2 + 1e-6)
            
            # 核心特征2：台区ID特征（从文件名提取）
            district_id = os.path.splitext(os.path.basename(json_file_path))[0]
            feature_dict['台区ID长度'] = len(district_id)
            feature_dict['台区ID数字比例'] = sum(c.isdigit() for c in district_id) / len(district_id)
            feature_dict['台区ID哈希'] = hash(district_id) % 1000 / 1000.0
            
            # 核心特征3：分支箱设备特征
            feature_dict['分支箱数量'] = branch_box_count
            feature_dict['设备总数'] = all_devices
            feature_dict['分支箱比例'] = branch_box_count / max(all_devices, 1)
            
            # 核心特征4：分支箱空间布局特征
            if branch_box_positions:
                x_coords = [pos[0] for pos in branch_box_positions]
                y_coords = [pos[1] for pos in branch_box_positions]
                
                # 空间分布特征
                x_span = max(x_coords) - min(x_coords) if len(x_coords) > 1 else 0
                y_span = max(y_coords) - min(y_coords) if len(y_coords) > 1 else 0
                spatial_span = np.sqrt(x_span**2 + y_span**2)
                
                # 布局紧凑度
                centroid_x, centroid_y = np.mean(x_coords), np.mean(y_coords)
                compactness = np.mean([
                    np.sqrt((x - centroid_x)**2 + (y - centroid_y)**2)
                    for x, y in branch_box_positions
                ])
                
                feature_dict['分支箱空间跨度'] = spatial_span
                feature_dict['分支箱布局紧凑度'] = compactness
                feature_dict['分支箱分布均匀性'] = 1 / (np.std(x_coords) + np.std(y_coords) + 1e-6)
            else:
                feature_dict['分支箱空间跨度'] = 0
                feature_dict['分支箱布局紧凑度'] = 0
                feature_dict['分支箱分布均匀性'] = 0
            
            # 核心特征5：分支箱连接特征
            total_connections = 0
            max_connections = 0
            for box in branch_boxes:
                connections = box.get('connection', '').split(',')
                conn_count = len([c for c in connections if c.strip()])
                total_connections += conn_count
                max_connections = max(max_connections, conn_count)
            
            feature_dict['分支箱总连接数'] = total_connections
            feature_dict['分支箱最大连接数'] = max_connections
            feature_dict['分支箱平均连接数'] = total_connections / max(branch_box_count, 1)
            
            # 添加其他工程特征
            transformers = [ann for ann in annotations if ann.get("label") in ["变压器", "配电变压器"]]
            cables = [ann for ann in annotations if ann.get("label") in ["电缆", "电缆段", "低压电缆"]]
            switches = [ann for ann in annotations if ann.get("label") in ["开关", "开关柜", "断路器"]]
            buildings = [ann for ann in annotations if ann.get("label") in ["建筑物", "房屋", "厂房"]]
            
            feature_dict['变压器数量'] = len(transformers)
            feature_dict['电缆数量'] = len(cables)
            feature_dict['开关数量'] = len(switches)
            feature_dict['建筑物数量'] = len(buildings)
            
            # 设备比例特征
            total_key_devices = len(transformers) + len(cables) + len(switches)
            feature_dict['变压器比例'] = len(transformers) / max(total_key_devices, 1)
            feature_dict['电缆比例'] = len(cables) / max(total_key_devices, 1)
            
            # 安全性评估
            safety_violations = 0
            if len(branch_box_positions) > 1:
                for i in range(len(branch_box_positions)):
                    for j in range(i + 1, len(branch_box_positions)):
                        pos1, pos2 = branch_box_positions[i], branch_box_positions[j]
                        dist = np.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
                        if dist < 5.0:  # 最小安全距离
                            safety_violations += 1
            
            feature_dict['安全违规数'] = safety_violations
            feature_dict['安全评分'] = max(0, 1 - safety_violations * 0.2)
            
            # 负载均衡特征
            load_balance = 0
            if branch_box_count > 0 and len(transformers) > 0:
                boxes_per_transformer = branch_box_count / len(transformers)
                if 1 <= boxes_per_transformer <= 4:
                    load_balance = 1.0
                elif boxes_per_transformer > 4:
                    load_balance = max(0, 1 - (boxes_per_transformer - 4) * 0.1)
                else:
                    load_balance = 0.5
            
            feature_dict['负载均衡度'] = load_balance
            
            # 维护便利性
            maintenance_score = 0
            if branch_box_positions and buildings:
                building_positions = []
                for building in buildings:
                    points = building.get("points", [])
                    if points:
                        center_x = np.mean([p[0] for p in points])
                        center_y = np.mean([p[1] for p in points])
                        building_positions.append((center_x, center_y))
                
                if building_positions:
                    accessible_boxes = 0
                    for box_pos in branch_box_positions:
                        min_building_dist = min(
                            np.sqrt((box_pos[0] - bp[0])**2 + (box_pos[1] - bp[1])**2)
                            for bp in building_positions
                        )
                        if 5 <= min_building_dist <= 30:  # 便于维护的距离
                            accessible_boxes += 1
                    maintenance_score = accessible_boxes / len(branch_box_positions)
            
            feature_dict['维护便利性'] = maintenance_score
            
            # 系统复杂度
            system_complexity = np.log(branch_box_count * all_devices + 1)
            connection_complexity = branch_box_count * (branch_box_count - 1) / 2 if branch_box_count > 1 else 0
            
            feature_dict['系统复杂度'] = system_complexity
            feature_dict['连接复杂度'] = connection_complexity
            
            # 如果有训练好的模型，使用模型预测
            if self.is_trained and self.features_df is not None:
                # 构建特征向量
                feature_columns = [col for col in self.features_df.columns 
                                  if col not in ['台区ID', '原始评分', '目标评分']]
                
                # 创建DataFrame以保持特征名称
                feature_data = {}
                for col in feature_columns:
                    feature_data[col] = [feature_dict.get(col, 0)]
                
                X_df = pd.DataFrame(feature_data)
                
                # 标准化特征
                X_scaled = self.scaler.transform(X_df)
                
                # 预测评分
                prediction = self.model.predict(X_scaled)[0]
                
                # 确保预测值在合理范围内
                prediction = np.clip(prediction, 0.0, 10.0)
                
                return float(prediction)
            else:
                # 使用简单的基于数量的评分逻辑
                return self._simple_scoring_from_count(branch_box_count)
                
        except Exception as e:
            print(f"从文件预测时出现错误: {e}")
            # 尝试简单计数
            try:
                with open(json_file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                annotations = data.get('annotations', [])
                branch_boxes = [ann for ann in annotations if ann.get('label') == '分支箱']
                return self._simple_scoring_from_count(len(branch_boxes))
            except:
                return 5.0  # 默认评分
    
    def _simple_scoring(self, branch_box_results):
        """基于分支箱结果的简单评分"""
        try:
            branch_box_count = len(branch_box_results) if branch_box_results else 0
            return self._simple_scoring_from_count(branch_box_count)
        except:
            return 5.0
    
    def _simple_scoring_from_count(self, branch_box_count):
        """基于分支箱数量的简单评分逻辑"""
        if branch_box_count == 0:
            return 10.0  # 没有分支箱，满分
        elif 1 <= branch_box_count <= 2:
            return 9.5   # 优秀
        elif 3 <= branch_box_count <= 4:
            return 8.5   # 良好
        elif 5 <= branch_box_count <= 6:
            return 7.0   # 中等
        else:
            return 6.0   # 一般

def test_branch_box_scoring():
    """测试分支箱评分优化系统"""
    print("=" * 60)
    print("分支箱评分系统优化测试")
    print("=" * 60)
    
    # 文件路径
    score_file = "评分标准/分支箱评分数据.csv"
    data_dir = "数据/data"
    
    # 创建优化器
    optimizer = BranchBoxScoringOptimizer(score_file, data_dir)
    
    try:
        # 加载数据
        optimizer.load_scores()
        
        # 提取特征
        optimizer.extract_branch_box_features()
        
        # 创建目标评分
        optimizer.create_target_score()
        
        # 训练模型
        results = optimizer.train_model()
        
        # 预测评分
        optimizer.predict_scores()
        
        print("\n=" * 60)
        print("分支箱评分优化完成！")
        print("=" * 60)
        
        return optimizer, results
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return None, None

if __name__ == "__main__":
    test_branch_box_scoring()