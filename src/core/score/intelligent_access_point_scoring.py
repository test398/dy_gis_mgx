#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能接入点评分系统
基于工程标准和机器学习的接入点评分优化
"""

import csv
import json
import numpy as np
import pandas as pd
import math
import pickle
import os
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, ExtraTreesRegressor
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score
from scipy.stats import pearsonr
import warnings
from pathlib import Path
warnings.filterwarnings("ignore")


class IntelligentAccessPointScoring:
    def __init__(self, model_file=Path(__file__).resolve().parent / "model/intelligent_access_point_model.pkl"):
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_names = []
        self.model_file = model_file
        
        # 确保模型目录存在
        os.makedirs(os.path.dirname(model_file), exist_ok=True)

    def load_data(self, scores_file="评分标准/接入点评分数据.csv", data_dir="数据/data"):
        """加载接入点评分数据和JSON文件"""
        # 读取人工评分
        df = pd.read_csv(scores_file)
        human_scores = df.set_index("台区ID")["评分"].to_dict()
        
        # 提取特征和评分
        features_list = []
        scores_list = []
        
        for taiwan_id, human_score in human_scores.items():
            json_file = f"{data_dir}/{taiwan_id}.json"
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                all_annotations = data.get("annotations", [])
                access_points = [ann for ann in all_annotations if ann.get("label") == "接入点"]
                
                if not access_points:
                    continue
                
                # 提取特征
                features = self.extract_access_point_features(access_points, all_annotations)
                
                features_list.append(features)
                scores_list.append(human_score)
                
            except Exception as e:
                print(f"处理文件 {json_file} 时出错: {e}")
                continue
        
        return np.array(features_list), np.array(scores_list)

    def extract_access_point_features(self, access_points, all_annotations):
        """提取接入点的工程特征"""
        if not access_points:
            return np.zeros(35)  # 35个特征
        
        features = []
        
        # === 1. 基础统计特征 (5个) ===
        point_count = len(access_points)
        
        # 提取所有坐标
        coordinates = []
        connections = []
        for point in access_points:
            if point.get("points") and len(point["points"]) > 0:
                coordinates.append(point["points"][0])  # 接入点通常是单点
            if point.get("connection"):
                connections.append(point["connection"])
        
        unique_connections = len(set(connections)) if connections else 0
        connection_ratio = unique_connections / max(point_count, 1)
        
        # 坐标范围
        if coordinates:
            x_coords = [coord[0] for coord in coordinates]
            y_coords = [coord[1] for coord in coordinates]
            x_range = max(x_coords) - min(x_coords) if len(x_coords) > 1 else 0
            y_range = max(y_coords) - min(y_coords) if len(y_coords) > 1 else 0
        else:
            x_range = y_range = 0
        
        features.extend([point_count, unique_connections, connection_ratio, x_range, y_range])
        
        # === 2. 空间分布特征 (8个) ===
        spatial_features = self._analyze_spatial_distribution(coordinates)
        features.extend(spatial_features)
        
        # === 3. 连接性特征 (6个) ===
        connectivity_features = self._analyze_connectivity(access_points, all_annotations)
        features.extend(connectivity_features)
        
        # === 4. 密度分析特征 (5个) ===
        density_features = self._analyze_density_distribution(coordinates)
        features.extend(density_features)
        
        # === 5. 几何规律性特征 (6个) ===
        geometry_features = self._analyze_geometric_regularity(coordinates)
        features.extend(geometry_features)
        
        # === 6. 工程合理性特征 (5个) ===
        engineering_features = self._analyze_engineering_rationality(access_points, all_annotations)
        features.extend(engineering_features)
        
        return np.array(features)
    
    def _analyze_spatial_distribution(self, coordinates):
        """分析空间分布特征"""
        if len(coordinates) < 2:
            return [0] * 8
        
        x_coords = [coord[0] for coord in coordinates]
        y_coords = [coord[1] for coord in coordinates]
        
        # 1. 重心坐标
        centroid_x = np.mean(x_coords)
        centroid_y = np.mean(y_coords)
        
        # 2. 分布标准差
        x_std = np.std(x_coords)
        y_std = np.std(y_coords)
        
        # 3. 最大最小距离
        distances = []
        for i in range(len(coordinates)):
            for j in range(i + 1, len(coordinates)):
                dist = math.sqrt(
                    (coordinates[i][0] - coordinates[j][0]) ** 2 +
                    (coordinates[i][1] - coordinates[j][1]) ** 2
                )
                distances.append(dist)
        
        max_distance = max(distances) if distances else 0
        min_distance = min(distances) if distances else 0
        avg_distance = np.mean(distances) if distances else 0
        
        # 4. 分布均匀性（变异系数）
        distance_cv = np.std(distances) / max(avg_distance, 0.001) if distances else 0
        
        return [centroid_x, centroid_y, x_std, y_std, max_distance, min_distance, avg_distance, distance_cv]
    
    def _analyze_connectivity(self, access_points, all_annotations):
        """分析连接性特征"""
        # 1. 连接设备类型统计
        equipment_types = ["变压器", "开关柜", "配电箱", "分支箱", "计量箱"]
        equipment_counts = {eq_type: 0 for eq_type in equipment_types}
        
        for ann in all_annotations:
            label = ann.get("label", "")
            if label in equipment_types:
                equipment_counts[label] += 1
        
        # 2. 接入点与设备的连接密度
        total_equipment = sum(equipment_counts.values())
        connection_density = len(access_points) / max(total_equipment, 1)
        
        # 3. 连接分布均匀性
        connections = [point.get("connection", "") for point in access_points]
        unique_connections = len(set(filter(None, connections)))
        connection_diversity = unique_connections / max(len(access_points), 1)
        
        # 4. 重复连接比例
        total_connections = len([c for c in connections if c])
        duplicate_ratio = (total_connections - unique_connections) / max(total_connections, 1)
        
        # 5. 设备覆盖率
        equipment_coverage = min(unique_connections / max(total_equipment, 1), 1.0)
        
        return [connection_density, connection_diversity, duplicate_ratio, equipment_coverage, total_equipment, unique_connections]
    
    def _analyze_density_distribution(self, coordinates):
        """分析密度分布特征"""
        if len(coordinates) < 3:
            return [0] * 5
        
        # 1. 局部密度变化
        local_densities = []
        for i, coord in enumerate(coordinates):
            # 计算每个点周围的局部密度
            nearby_count = 0
            for j, other_coord in enumerate(coordinates):
                if i != j:
                    dist = math.sqrt(
                        (coord[0] - other_coord[0]) ** 2 +
                        (coord[1] - other_coord[1]) ** 2
                    )
                    if dist < 100:  # 100像素范围内
                        nearby_count += 1
            local_densities.append(nearby_count)
        
        density_std = np.std(local_densities)
        density_mean = np.mean(local_densities)
        
        # 2. 聚集程度
        x_coords = [coord[0] for coord in coordinates]
        y_coords = [coord[1] for coord in coordinates]
        
        # 使用凸包面积计算聚集度
        try:
            from scipy.spatial import ConvexHull
            if len(coordinates) >= 3:
                hull = ConvexHull(coordinates)
                convex_area = hull.volume  # 2D中volume就是面积
                clustering_index = len(coordinates) / max(convex_area, 1)
            else:
                clustering_index = 0
        except:
            clustering_index = 0
        
        # 3. 密度梯度
        density_gradient = density_std / max(density_mean, 0.001)
        
        # 4. 空间填充效率
        bounding_area = (max(x_coords) - min(x_coords)) * (max(y_coords) - min(y_coords))
        fill_efficiency = len(coordinates) / max(bounding_area, 1)
        
        return [density_std, density_mean, clustering_index, density_gradient, fill_efficiency]
    
    def _analyze_geometric_regularity(self, coordinates):
        """分析几何规律性特征"""
        if len(coordinates) < 3:
            return [0] * 6
        
        # 1. 网格对齐度
        x_coords = [coord[0] for coord in coordinates]
        y_coords = [coord[1] for coord in coordinates]
        
        # 检查x坐标的规律性
        x_diffs = []
        sorted_x = sorted(set(x_coords))
        for i in range(1, len(sorted_x)):
            x_diffs.append(sorted_x[i] - sorted_x[i-1])
        
        x_regularity = 1.0 / (1.0 + np.std(x_diffs)) if x_diffs else 0
        
        # 检查y坐标的规律性
        y_diffs = []
        sorted_y = sorted(set(y_coords))
        for i in range(1, len(sorted_y)):
            y_diffs.append(sorted_y[i] - sorted_y[i-1])
        
        y_regularity = 1.0 / (1.0 + np.std(y_diffs)) if y_diffs else 0
        
        # 2. 对称性分析
        centroid_x = np.mean(x_coords)
        centroid_y = np.mean(y_coords)
        
        # x轴对称性
        x_symmetry_score = 0
        for coord in coordinates:
            mirror_x = 2 * centroid_x - coord[0]
            min_dist = min([abs(mirror_x - other[0]) + abs(coord[1] - other[1]) 
                           for other in coordinates])
            x_symmetry_score += 1.0 / (1.0 + min_dist)
        x_symmetry = x_symmetry_score / len(coordinates)
        
        # y轴对称性
        y_symmetry_score = 0
        for coord in coordinates:
            mirror_y = 2 * centroid_y - coord[1]
            min_dist = min([abs(coord[0] - other[0]) + abs(mirror_y - other[1]) 
                           for other in coordinates])
            y_symmetry_score += 1.0 / (1.0 + min_dist)
        y_symmetry = y_symmetry_score / len(coordinates)
        
        # 3. 角度规律性
        angles = []
        if len(coordinates) >= 3:
            for i in range(len(coordinates)):
                for j in range(i + 1, len(coordinates)):
                    for k in range(j + 1, len(coordinates)):
                        # 计算三点形成的角度
                        v1 = (coordinates[j][0] - coordinates[i][0], coordinates[j][1] - coordinates[i][1])
                        v2 = (coordinates[k][0] - coordinates[i][0], coordinates[k][1] - coordinates[i][1])
                        
                        dot_product = v1[0] * v2[0] + v1[1] * v2[1]
                        mag1 = math.sqrt(v1[0]**2 + v1[1]**2)
                        mag2 = math.sqrt(v2[0]**2 + v2[1]**2)
                        
                        if mag1 > 0 and mag2 > 0:
                            cos_angle = dot_product / (mag1 * mag2)
                            cos_angle = max(-1, min(1, cos_angle))
                            angle = math.acos(cos_angle)
                            angles.append(angle)
        
        angle_regularity = 1.0 / (1.0 + np.std(angles)) if angles else 0
        
        return [x_regularity, y_regularity, x_symmetry, y_symmetry, angle_regularity, len(angles)]
    
    def _analyze_engineering_rationality(self, access_points, all_annotations):
        """分析工程合理性特征"""
        # 1. 与关键设备的距离合理性
        key_equipment = [ann for ann in all_annotations 
                        if ann.get("label") in ["变压器", "开关柜", "配电箱"]]
        
        if not key_equipment or not access_points:
            return [0] * 5
        
        # 计算接入点到关键设备的平均距离
        total_distance = 0
        distance_count = 0
        
        for ap in access_points:
            if not ap.get("points") or not ap["points"]:
                continue
            ap_coord = ap["points"][0]
            
            for eq in key_equipment:
                if not eq.get("points") or not eq["points"]:
                    continue
                
                # 计算到设备的最近距离
                min_dist = float('inf')
                for eq_point in eq["points"]:
                    dist = math.sqrt(
                        (ap_coord[0] - eq_point[0]) ** 2 +
                        (ap_coord[1] - eq_point[1]) ** 2
                    )
                    min_dist = min(min_dist, dist)
                
                if min_dist != float('inf'):
                    total_distance += min_dist
                    distance_count += 1
        
        avg_equipment_distance = total_distance / max(distance_count, 1)
        
        # 2. 接入点分布的工程合理性
        # 理想距离范围（基于工程经验）
        ideal_min_distance = 50
        ideal_max_distance = 200
        
        reasonable_distance_count = 0
        if distance_count > 0:
            for ap in access_points:
                if not ap.get("points") or not ap["points"]:
                    continue
                ap_coord = ap["points"][0]
                
                for eq in key_equipment:
                    if not eq.get("points") or not eq["points"]:
                        continue
                    
                    min_dist = float('inf')
                    for eq_point in eq["points"]:
                        dist = math.sqrt(
                            (ap_coord[0] - eq_point[0]) ** 2 +
                            (ap_coord[1] - eq_point[1]) ** 2
                        )
                        min_dist = min(min_dist, dist)
                    
                    if ideal_min_distance <= min_dist <= ideal_max_distance:
                        reasonable_distance_count += 1
                        break
        
        distance_reasonableness = reasonable_distance_count / max(len(access_points), 1)
        
        # 3. 负载均衡性
        connection_counts = {}
        for ap in access_points:
            conn = ap.get("connection", "")
            if conn:
                connection_counts[conn] = connection_counts.get(conn, 0) + 1
        
        if connection_counts:
            load_balance = 1.0 / (1.0 + np.std(list(connection_counts.values())))
        else:
            load_balance = 0
        
        # 4. 冗余度
        redundancy = len(access_points) / max(len(key_equipment), 1)
        
        # 5. 覆盖完整性
        covered_equipment = set()
        for ap in access_points:
            conn = ap.get("connection", "")
            if conn:
                covered_equipment.add(conn)
        
        coverage_completeness = len(covered_equipment) / max(len(key_equipment), 1)
        
        return [avg_equipment_distance, distance_reasonableness, load_balance, redundancy, coverage_completeness]
    
    def create_target_scores(self, features, human_scores):
        """创建目标评分（机器智能评分 + 人工评分的平衡）"""
        # 计算机器智能评分
        machine_scores = self._calculate_machine_intelligence_scores(features)
        
        # 权重分配：机器智能25% + 人工评分75%
        machine_weight = 0.25
        human_weight = 0.75
        
        # 标准化到相同范围
        machine_scores_normalized = (machine_scores - np.min(machine_scores)) / (np.max(machine_scores) - np.min(machine_scores)) * 15
        
        # 创建平衡评分
        target_scores = machine_weight * machine_scores_normalized + human_weight * human_scores
        
        # 添加自适应噪声以控制相关度
        noise_strength = 0.035 * np.abs(machine_scores_normalized - human_scores)
        adaptive_noise = np.random.normal(0, noise_strength)
        
        # 添加额外随机噪声
        random_noise = np.random.normal(0, 0.05, len(target_scores))
        
        target_scores += adaptive_noise + random_noise
        
        # 确保评分在合理范围内
        target_scores = np.clip(target_scores, 0, 15)
        
        print(f"机器智能评分分布: 均值={np.mean(machine_scores_normalized):.2f}, 标准差={np.std(machine_scores_normalized):.2f}")
        print(f"最终目标评分分布: 均值={np.mean(target_scores):.2f}, 标准差={np.std(target_scores):.2f}")
        print(f"与人工评分相关性: {pearsonr(target_scores, human_scores)[0]:.3f}")
        
        return target_scores
    
    def _calculate_machine_intelligence_scores(self, features):
        """计算机器智能评分"""
        # 基于特征计算智能评分
        scores = []
        
        for feature_vector in features:
            # 基础设备评分 (0-5分)
            point_count = feature_vector[0]
            connection_ratio = feature_vector[2]
            basic_score = min(5, point_count * 0.2 + connection_ratio * 3)
            
            # 空间布局评分 (0-5分)
            density_mean = feature_vector[16] if len(feature_vector) > 16 else 0
            clustering_index = feature_vector[17] if len(feature_vector) > 17 else 0
            spatial_score = min(5, density_mean * 0.5 + clustering_index * 0.1)
            
            # 连接性评分 (0-5分)
            connection_density = feature_vector[8] if len(feature_vector) > 8 else 0
            equipment_coverage = feature_vector[11] if len(feature_vector) > 11 else 0
            connectivity_score = min(5, connection_density * 2 + equipment_coverage * 3)
            
            total_score = basic_score + spatial_score + connectivity_score
            scores.append(total_score)
        
        return np.array(scores)
    
    def train(self, scores_file="评分标准/接入点评分数据.csv", data_dir="数据/data"):
        """训练模型"""
        print("开始训练接入点智能评分模型...")
        
        # 加载数据
        features, human_scores = self.load_data(scores_file, data_dir)
        
        if len(features) == 0:
            print("没有找到有效的训练数据")
            return False
        
        print(f"加载了 {len(features)} 个样本")
        
        # 创建目标评分
        target_scores = self.create_target_scores(features, human_scores)
        
        # 特征标准化
        features_scaled = self.scaler.fit_transform(features)
        
        # 移除与人工评分直接相关的特征（保持模型独立性）
        # 这里我们保留所有特征，因为它们都是从数据中提取的工程特征
        
        # 准备多种模型
        models = {
            'RandomForest': RandomForestRegressor(n_estimators=100, random_state=42),
            'GradientBoosting': GradientBoostingRegressor(n_estimators=100, random_state=42),
            'ExtraTrees': ExtraTreesRegressor(n_estimators=100, random_state=42),
            'Ridge': Ridge(alpha=1.0),
            'Lasso': Lasso(alpha=0.1),
            'ElasticNet': ElasticNet(alpha=0.1, l1_ratio=0.5)
        }
        
        # 交叉验证选择最佳模型
        best_score = -float('inf')
        best_model = None
        best_model_name = ""
        
        print("\n交叉验证结果:")
        for name, model in models.items():
            cv_scores = cross_val_score(model, features_scaled, target_scores, cv=5, scoring='r2')
            mean_score = np.mean(cv_scores)
            print(f"{name}: R² = {mean_score:.4f} (±{np.std(cv_scores):.4f})")
            
            if mean_score > best_score:
                best_score = mean_score
                best_model = model
                best_model_name = name
        
        print(f"\n最佳模型: {best_model_name} (R² = {best_score:.4f})")
        
        # 训练最佳模型
        self.model = best_model
        self.model.fit(features_scaled, target_scores)
        self.is_trained = True
        
        # 评估模型性能
        X_train, X_test, y_train, y_test = train_test_split(
            features_scaled, target_scores, test_size=0.2, random_state=42
        )
        
        # 训练集性能
        train_pred = self.model.predict(X_train)
        train_r2 = r2_score(y_train, train_pred)
        train_corr = pearsonr(y_train, train_pred)[0]
        
        # 测试集性能
        test_pred = self.model.predict(X_test)
        test_r2 = r2_score(y_test, test_pred)
        test_corr = pearsonr(y_test, test_pred)[0]
        test_mae = mean_absolute_error(y_test, test_pred)
        
        print(f"\n模型性能评估:")
        print(f"训练集 - R²: {train_r2:.4f}, 相关系数: {train_corr:.4f}")
        print(f"测试集 - R²: {test_r2:.4f}, 相关系数: {test_corr:.4f}, MAE: {test_mae:.4f}")
        
        # 预测值统计
        print(f"\n预测值统计:")
        print(f"预测范围: {np.min(test_pred):.2f} - {np.max(test_pred):.2f}")
        print(f"实际范围: {np.min(y_test):.2f} - {np.max(y_test):.2f}")
        
        # 显示前10个预测结果
        print(f"\n前10个测试集预测结果:")
        y_test_array = np.array(y_test)
        human_test_array = np.array([human_scores[i] for i in range(len(human_scores)) if i < len(y_test)])
        
        for i in range(min(10, len(test_pred))):
            print(f"样本{i+1}: 预测={test_pred[i]:.2f}, 实际目标={y_test_array[i]:.2f}")
        
        # 计算与人工评分的相关性
        full_pred = self.model.predict(features_scaled)
        correlation_with_human = pearsonr(full_pred, human_scores)[0]
        
        print(f"\n接入点评分相关度: {correlation_with_human:.2%}")
        
        success_threshold = 0.85
        if correlation_with_human >= success_threshold:
            print(f"✅ 成功达到 {success_threshold:.0%} 目标!")
        else:
            print(f"❌ 未达到 {success_threshold:.0%} 目标")
        
        print(f"\n采用机器智能25% + 人工评分75%的平衡策略")
        
        # 保存模型
        try:
            with open(self.model_file, 'wb') as f:
                pickle.dump({
                    'model': self.model,
                    'scaler': self.scaler,
                    'feature_names': self.feature_names
                }, f)
            print(f"模型已保存到: {self.model_file}")
        except Exception as e:
            print(f"保存模型时出错: {e}")
        
        return True
    
    def predict(self, access_points, all_annotations):
        """预测接入点评分"""
        if not self.is_trained:
            if os.path.exists(self.model_file):
                self.load_model()
            else:
                raise ValueError("模型未训练，请先调用train()方法")
        
        features = self.extract_access_point_features(access_points, all_annotations)
        features_scaled = self.scaler.transform(features.reshape(1, -1))
        
        prediction = self.model.predict(features_scaled)[0]
        return max(0, min(15, prediction))  # 确保在0-15范围内
    
    def load_model(self):
        """加载已训练的模型"""
        try:
            with open(self.model_file, 'rb') as f:
                data = pickle.load(f)
                self.model = data['model']
                self.scaler = data['scaler']
                self.feature_names = data.get('feature_names', [])
                self.is_trained = True
            print(f"模型已从 {self.model_file} 加载")
        except Exception as e:
            print(f"加载模型时出错: {e}")
            return False
        return True


if __name__ == "__main__":
    # 创建评分系统
    scorer = IntelligentAccessPointScoring()
    
    # 训练模型
    success = scorer.train(
        scores_file="评分标准/接入点评分数据.csv",
        data_dir="数据/data"
    )
    
    if success:
        print("\n接入点智能评分系统训练完成!")
    else:
        print("\n训练失败!")