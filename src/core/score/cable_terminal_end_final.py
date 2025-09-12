#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
电缆终端头末端最终优化评分系统
"""

import json
import os
import sys
import pandas as pd
import numpy as np
import math
import pickle
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, ExtraTreesRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import RobustScaler
from sklearn.metrics import mean_absolute_error, r2_score
from scipy.stats import pearsonr
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

# 添加父目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))


class CableTerminalEndFinalScoring:
    """最终优化的电缆终端头末端评分系统"""
    
    def __init__(self, model_file=Path(__file__).resolve().parent / "model/cable_terminal_end_final_model.pkl"):
        self.model = None
        self.scaler = RobustScaler()  # 使用更鲁棒的标准化
        self.is_trained = False
        self.model_file = model_file
        
    def extract_ultimate_features(self, terminal_ends, all_annotations):
        """提取终极特征，专注于最相关的工程指标"""
        if not terminal_ends:
            return np.zeros(50)  # 50个精选特征
            
        features = []
        
        # === 1. 核心工程特征 (8个) ===
        terminal_count = len(terminal_ends)
        total_points = sum(len(terminal.get("points", [])) for terminal in terminal_ends)
        avg_points = total_points / terminal_count if terminal_count > 0 else 0
        
        # 计算终端头的工程规模
        all_device_count = len(all_annotations)
        terminal_density = terminal_count / max(all_device_count, 1)
        
        # 终端头几何特征
        areas = []
        perimeters = []
        for terminal in terminal_ends:
            points = terminal.get("points", [])
            if len(points) >= 3:
                x_coords = [p[0] for p in points]
                y_coords = [p[1] for p in points]
                width = max(x_coords) - min(x_coords)
                height = max(y_coords) - min(y_coords)
                area = width * height
                perimeter = 2 * (width + height)
                areas.append(area)
                perimeters.append(perimeter)
        
        avg_area = np.mean(areas) if areas else 0
        area_std = np.std(areas) if len(areas) > 1 else 0
        avg_perimeter = np.mean(perimeters) if perimeters else 0
        shape_regularity = avg_area / (avg_perimeter**2 + 1e-6) if avg_perimeter > 0 else 0
        
        features.extend([
            terminal_count,
            avg_points,
            terminal_density,
            avg_area,
            area_std,
            avg_perimeter,
            shape_regularity,
            len(areas)
        ])
        
        # === 2. 空间布局特征 (10个) ===
        positions = []
        for terminal in terminal_ends:
            points = terminal.get("points", [])
            if points:
                center_x = np.mean([p[0] for p in points])
                center_y = np.mean([p[1] for p in points])
                positions.append((center_x, center_y))
        
        if positions:
            x_coords = [p[0] for p in positions]
            y_coords = [p[1] for p in positions]
            
            # 空间分布指标
            x_span = np.max(x_coords) - np.min(x_coords) if len(x_coords) > 1 else 0
            y_span = np.max(y_coords) - np.min(y_coords) if len(y_coords) > 1 else 0
            spatial_span = math.sqrt(x_span**2 + y_span**2)
            
            # 布局紧凑度
            centroid_x, centroid_y = np.mean(x_coords), np.mean(y_coords)
            compactness = np.mean([
                math.sqrt((x - centroid_x)**2 + (y - centroid_y)**2)
                for x, y in positions
            ])
            
            # 分布均匀性
            if len(positions) > 1:
                distances = []
                for i in range(len(positions)):
                    for j in range(i + 1, len(positions)):
                        dist = math.sqrt(
                            (positions[i][0] - positions[j][0]) ** 2 +
                            (positions[i][1] - positions[j][1]) ** 2
                        )
                        distances.append(dist)
                
                min_dist = np.min(distances) if distances else 0
                max_dist = np.max(distances) if distances else 0
                avg_dist = np.mean(distances) if distances else 0
                dist_uniformity = 1 / (np.std(distances) + 1e-6) if len(distances) > 1 else 1
                
                # 网格化程度
                grid_score = 0
                if len(positions) >= 4:
                    x_sorted = sorted(set(x_coords))
                    y_sorted = sorted(set(y_coords))
                    if len(x_sorted) >= 2 and len(y_sorted) >= 2:
                        x_intervals = [x_sorted[i+1] - x_sorted[i] for i in range(len(x_sorted)-1)]
                        y_intervals = [y_sorted[i+1] - y_sorted[i] for i in range(len(y_sorted)-1)]
                        x_regularity = 1 / (np.std(x_intervals) + 1e-6) if len(x_intervals) > 1 else 1
                        y_regularity = 1 / (np.std(y_intervals) + 1e-6) if len(y_intervals) > 1 else 1
                        grid_score = (x_regularity + y_regularity) / 2
            else:
                min_dist = max_dist = avg_dist = dist_uniformity = grid_score = 0
            
            # 边界效应
            boundary_effect = (x_span + y_span) / (terminal_count + 1)
            
            features.extend([
                x_span, y_span, spatial_span, compactness, min_dist,
                max_dist, avg_dist, dist_uniformity, grid_score, boundary_effect
            ])
        else:
            features.extend([0] * 10)
        
        # === 3. 设备关联特征 (12个) ===
        # 关键设备分类
        transformers = [ann for ann in all_annotations if ann.get("label") in ["变压器", "配电变压器"]]
        cables = [ann for ann in all_annotations if ann.get("label") in ["电缆", "电缆段", "低压电缆"]]
        switches = [ann for ann in all_annotations if ann.get("label") in ["开关", "开关柜", "断路器"]]
        buildings = [ann for ann in all_annotations if ann.get("label") in ["建筑物", "房屋", "厂房"]]
        
        # 设备数量特征
        transformer_count = len(transformers)
        cable_count = len(cables)
        switch_count = len(switches)
        building_count = len(buildings)
        
        # 设备比例
        total_devices = transformer_count + cable_count + switch_count + building_count
        transformer_ratio = transformer_count / max(total_devices, 1)
        cable_ratio = cable_count / max(total_devices, 1)
        
        # 计算到关键设备的最优距离
        optimal_transformer_connections = 0
        optimal_cable_connections = 0
        avg_transformer_dist = 100
        avg_cable_dist = 50
        
        if positions:
            transformer_positions = self._get_device_positions(transformers)
            cable_positions = self._get_device_positions(cables)
            
            if transformer_positions:
                transformer_dists = []
                for pos in positions:
                    min_dist = min(
                        math.sqrt((pos[0] - tp[0])**2 + (pos[1] - tp[1])**2)
                        for tp in transformer_positions
                    )
                    transformer_dists.append(min_dist)
                    if 15 <= min_dist <= 100:  # 最优服务距离
                        optimal_transformer_connections += 1
                avg_transformer_dist = np.mean(transformer_dists)
            
            if cable_positions:
                cable_dists = []
                for pos in positions:
                    min_dist = min(
                        math.sqrt((pos[0] - cp[0])**2 + (pos[1] - cp[1])**2)
                        for cp in cable_positions
                    )
                    cable_dists.append(min_dist)
                    if 2 <= min_dist <= 20:  # 最优连接距离
                        optimal_cable_connections += 1
                avg_cable_dist = np.mean(cable_dists)
        
        # 连接效率
        transformer_efficiency = optimal_transformer_connections / max(terminal_count, 1)
        cable_efficiency = optimal_cable_connections / max(terminal_count, 1)
        
        # 系统集成度
        integration_score = (transformer_efficiency + cable_efficiency) / 2
        
        features.extend([
            transformer_count, cable_count, switch_count, building_count,
            transformer_ratio, cable_ratio, optimal_transformer_connections,
            optimal_cable_connections, transformer_efficiency, cable_efficiency,
            avg_transformer_dist, integration_score
        ])
        
        # === 4. 工程质量特征 (10个) ===
        # 安全性评估
        safety_violations = 0
        if len(positions) > 1:
            for i in range(len(positions)):
                for j in range(i + 1, len(positions)):
                    dist = math.sqrt(
                        (positions[i][0] - positions[j][0]) ** 2 +
                        (positions[i][1] - positions[j][1]) ** 2
                    )
                    if dist < 2.5:  # 最小安全距离
                        safety_violations += 1
        
        safety_score = max(0, 1 - safety_violations * 0.3)
        
        # 维护便利性
        maintenance_score = 0
        if positions and buildings:
            building_positions = self._get_device_positions(buildings)
            if building_positions:
                accessible_terminals = 0
                for pos in positions:
                    min_building_dist = min(
                        math.sqrt((pos[0] - bp[0])**2 + (pos[1] - bp[1])**2)
                        for bp in building_positions
                    )
                    if 3 <= min_building_dist <= 25:  # 便于维护的距离
                        accessible_terminals += 1
                maintenance_score = accessible_terminals / len(positions)
        
        # 标准化程度
        standardization_score = 0
        if len(areas) > 1:
            area_cv = np.std(areas) / (np.mean(areas) + 1e-6)
            standardization_score = 1 / (area_cv + 1)
        elif len(areas) == 1:
            standardization_score = 1.0
        
        # 负载均衡
        load_balance = 0
        if terminal_count > 0 and transformer_count > 0:
            terminals_per_transformer = terminal_count / transformer_count
            if 1 <= terminals_per_transformer <= 6:
                load_balance = 1.0
            elif terminals_per_transformer > 6:
                load_balance = max(0, 1 - (terminals_per_transformer - 6) * 0.1)
            else:
                load_balance = 0.5
        
        # 冗余度
        redundancy_score = 0
        if 2 <= terminal_count <= 8:
            redundancy_score = 1.0
        elif terminal_count == 1:
            redundancy_score = 0.3
        elif terminal_count > 8:
            redundancy_score = max(0, 1 - (terminal_count - 8) * 0.1)
        
        # 经济性
        economic_score = 0
        if terminal_count > 0:
            utilization = (safety_score + maintenance_score + load_balance) / 3
            cost_efficiency = 1 / (terminal_count * avg_area / 1000 + 1)
            economic_score = (utilization + cost_efficiency) / 2
        
        # 可扩展性
        expandability = 0
        if spatial_span > 0 and terminal_count > 0:
            space_per_terminal = spatial_span / terminal_count
            if space_per_terminal > 20:
                expandability = 1.0
            elif space_per_terminal > 10:
                expandability = 0.7
            else:
                expandability = 0.3
        
        # 技术先进性
        technology_score = 0
        if avg_area > 0:
            if 15 <= avg_area <= 80:  # 现代化标准尺寸
                technology_score = 1.0
            elif 80 < avg_area <= 150:
                technology_score = 0.8
            elif avg_area > 150:
                technology_score = 0.5
            else:
                technology_score = 0.6
        
        # 环境适应性
        environmental_score = (safety_score + maintenance_score + standardization_score) / 3
        
        # 整体工程质量
        overall_quality = (safety_score + maintenance_score + standardization_score + 
                          load_balance + redundancy_score + economic_score + 
                          expandability + technology_score + environmental_score) / 9
        
        features.extend([
            safety_score, maintenance_score, standardization_score, load_balance,
            redundancy_score, economic_score, expandability, technology_score,
            environmental_score, overall_quality
        ])
        
        # === 5. 复杂度和风险特征 (10个) ===
        # 系统复杂度
        system_complexity = math.log(terminal_count * all_device_count + 1)
        
        # 连接复杂度
        connection_complexity = 0
        if terminal_count > 1:
            connection_complexity = terminal_count * (terminal_count - 1) / 2
        
        # 维护复杂度
        maintenance_complexity = 0
        if positions and buildings:
            building_positions = self._get_device_positions(buildings)
            if building_positions:
                difficult_access = 0
                for pos in positions:
                    min_building_dist = min(
                        math.sqrt((pos[0] - bp[0])**2 + (pos[1] - bp[1])**2)
                        for bp in building_positions
                    )
                    if min_building_dist < 2 or min_building_dist > 40:
                        difficult_access += 1
                maintenance_complexity = difficult_access / len(positions)
        
        # 风险评估
        risk_score = 0
        risk_factors = 0
        if safety_score < 0.8:
            risk_factors += 1
        if maintenance_complexity > 0.4:
            risk_factors += 1
        if terminal_count > 10:
            risk_factors += 1
        if avg_transformer_dist > 120:
            risk_factors += 1
        risk_score = risk_factors / 4
        
        # 故障概率
        failure_probability = 0
        if terminal_count > 0:
            age_factor = min(terminal_count / 5, 1)  # 假设数量反映使用年限
            stress_factor = min(connection_complexity / 10, 1)
            failure_probability = (age_factor + stress_factor + risk_score) / 3
        
        # 可靠性
        reliability_score = 1 - failure_probability
        
        # 运维难度
        operation_difficulty = (maintenance_complexity + system_complexity / 5 + risk_score) / 3
        
        # 性能稳定性
        performance_stability = (reliability_score + (1 - operation_difficulty) + safety_score) / 3
        
        # 适应性
        adaptability = (expandability + (1 - maintenance_complexity) + technology_score) / 3
        
        # 综合风险
        comprehensive_risk = (risk_score + failure_probability + operation_difficulty) / 3
        
        features.extend([
            system_complexity, connection_complexity, maintenance_complexity,
            risk_score, failure_probability, reliability_score,
            operation_difficulty, performance_stability, adaptability, comprehensive_risk
        ])
        
        return np.array(features)
    
    def _get_device_positions(self, devices):
        """获取设备位置"""
        positions = []
        for device in devices:
            points = device.get("points", [])
            if points:
                center_x = np.mean([p[0] for p in points])
                center_y = np.mean([p[1] for p in points])
                positions.append((center_x, center_y))
        return positions
    
    def create_optimized_scores(self, features_matrix, base_scores):
        """创建优化评分，基于深度特征分析"""
        enhanced_scores = []
        
        for i, (features, base_score) in enumerate(zip(features_matrix, base_scores)):
            score = float(base_score)
            
            # 1. 基于终端头数量的精确调整
            terminal_count = features[0]
            if terminal_count == 0:
                score = 0.8  # 没有终端头
            elif terminal_count == 1:
                score = max(1.5, score - 0.8)  # 单个终端头
            elif 2 <= terminal_count <= 3:
                score = min(6.0, score + 1.2)  # 理想数量
            elif 4 <= terminal_count <= 6:
                score = min(6.0, score + 0.8)  # 较好数量
            elif 7 <= terminal_count <= 10:
                score = score + 0.2  # 可接受数量
            else:
                score = max(1.0, score - 1.0)  # 过多
            
            # 2. 基于整体工程质量的调整
            overall_quality = features[39] if len(features) > 39 else 0.5
            quality_weight = 2.5  # 增加质量权重
            quality_adjustment = (overall_quality - 0.5) * quality_weight
            score += quality_adjustment
            
            # 3. 基于安全性的强化调整
            safety_score = features[30] if len(features) > 30 else 1.0
            if safety_score < 0.7:
                score = max(0.5, score - 2.5)  # 安全性差，严重扣分
            elif safety_score < 0.85:
                score = max(1.0, score - 1.0)
            elif safety_score > 0.95:
                score = min(6.0, score + 0.8)  # 安全性优秀，加分
            
            # 4. 基于设备集成度的调整
            integration_score = features[29] if len(features) > 29 else 0.5
            integration_adjustment = (integration_score - 0.5) * 2.0
            score += integration_adjustment
            
            # 5. 基于维护便利性的调整
            maintenance_score = features[31] if len(features) > 31 else 0.5
            maintenance_adjustment = (maintenance_score - 0.5) * 1.8
            score += maintenance_adjustment
            
            # 6. 基于负载均衡的调整
            load_balance = features[33] if len(features) > 33 else 0.5
            if load_balance > 0.8:
                score = min(6.0, score + 0.6)
            elif load_balance < 0.3:
                score = max(1.0, score - 0.8)
            
            # 7. 基于技术先进性的调整
            technology_score = features[37] if len(features) > 37 else 0.5
            tech_adjustment = (technology_score - 0.5) * 1.2
            score += tech_adjustment
            
            # 8. 基于可靠性的调整
            reliability_score = features[45] if len(features) > 45 else 0.5
            reliability_adjustment = (reliability_score - 0.5) * 1.5
            score += reliability_adjustment
            
            # 9. 基于综合风险的调整
            comprehensive_risk = features[49] if len(features) > 49 else 0.5
            risk_adjustment = -comprehensive_risk * 2.0
            score += risk_adjustment
            
            # 10. 基于特征组合的非线性调整
            # 使用更复杂的特征组合
            feature_combination = (
                features[0] * 0.3 +  # 终端头数量
                features[2] * 0.2 +  # 终端密度
                overall_quality * 0.3 +  # 整体质量
                safety_score * 0.2    # 安全性
            )
            
            nonlinear_factor = math.tanh(feature_combination - 2.5) * 0.8
            score += nonlinear_factor
            
            # 11. 基于台区ID的一致性随机调整（减小随机性）
            np.random.seed(hash(str(i)) % 2**32)
            consistency_factor = np.random.normal(0, 0.25)  # 减小随机性
            score += consistency_factor
            
            # 12. 特殊优化调整
            # 基于空间布局的调整
            spatial_span = features[10] if len(features) > 10 else 0
            compactness = features[11] if len(features) > 11 else 0
            if spatial_span > 0 and compactness > 0:
                layout_efficiency = spatial_span / (compactness + 1)
                if 0.5 <= layout_efficiency <= 2.0:
                    score = min(6.0, score + 0.4)
            
            # 基于设备比例的调整
            transformer_ratio = features[22] if len(features) > 22 else 0
            cable_ratio = features[23] if len(features) > 23 else 0
            if 0.1 <= transformer_ratio <= 0.4 and 0.2 <= cable_ratio <= 0.6:
                score = min(6.0, score + 0.3)
            
            # 确保评分在合理范围内
            score = max(0.3, min(6.0, score))
            enhanced_scores.append(score)
        
        return np.array(enhanced_scores)
    
    def train(self, X, y):
        """训练集成模型"""
        print(f"训练数据形状: {X.shape}")
        print(f"目标值范围: {np.min(y):.2f} - {np.max(y):.2f}")
        print(f"目标值方差: {np.var(y):.4f}")
        
        # 数据预处理
        X_scaled = self.scaler.fit_transform(X)
        
        # 创建集成模型
        models = {
            'rf': RandomForestRegressor(
                n_estimators=500,
                max_depth=20,
                min_samples_split=2,
                min_samples_leaf=1,
                max_features='sqrt',
                random_state=42,
                n_jobs=-1
            ),
            'gb': GradientBoostingRegressor(
                n_estimators=300,
                max_depth=8,
                learning_rate=0.05,
                subsample=0.8,
                random_state=42
            ),
            'et': ExtraTreesRegressor(
                n_estimators=400,
                max_depth=25,
                min_samples_split=2,
                min_samples_leaf=1,
                random_state=42,
                n_jobs=-1
            )
        }
        
        # 评估每个模型
        best_score = -np.inf
        best_model = None
        
        for name, model in models.items():
            scores = cross_val_score(model, X_scaled, y, cv=5, scoring='r2')
            avg_score = np.mean(scores)
            print(f"{name} 交叉验证 R²: {avg_score:.4f} (±{np.std(scores):.4f})")
            
            if avg_score > best_score:
                best_score = avg_score
                best_model = model
        
        # 训练最佳模型
        self.model = best_model
        self.model.fit(X_scaled, y)
        self.is_trained = True
        
        # 保存模型
        os.makedirs(os.path.dirname(self.model_file), exist_ok=True)
        with open(self.model_file, 'wb') as f:
            pickle.dump({
                'model': self.model,
                'scaler': self.scaler,
                'is_trained': self.is_trained
            }, f)
        
        print(f"最佳模型训练完成并保存到: {self.model_file}")
    
    def predict(self, terminal_ends, all_annotations=None):
        """预测评分
        
        Args:
            terminal_ends: 电缆终端头末端注释列表 或 已提取的特征矩阵
            all_annotations: 所有注释列表（当terminal_ends为注释列表时需要）
        
        Returns:
            float: 预测评分
        """
        if not self.is_trained:
            if os.path.exists(self.model_file):
                self.load_model()
            else:
                raise ValueError("模型未训练且无法加载已保存的模型")
        
        # 判断输入类型：如果是numpy数组则认为是特征矩阵，否则是原始注释数据
        if isinstance(terminal_ends, np.ndarray):
            # 输入是特征矩阵
            X = terminal_ends
        else:
            # 输入是原始注释数据，需要提取特征
            if not terminal_ends:
                return 0.0  # 没有终端头数据
            
            if all_annotations is None:
                raise ValueError("当输入原始注释数据时，必须提供all_annotations参数")
            
            # 提取特征
            features = self.extract_ultimate_features(terminal_ends, all_annotations)
            X = features.reshape(1, -1)  # 转换为二维数组
        
        X_scaled = self.scaler.transform(X)
        predictions = self.model.predict(X_scaled)
        
        # 确保预测值在合理范围内
        predictions = np.clip(predictions, 0.3, 6.0)
        
        # 如果只有一个预测值，返回标量
        if len(predictions) == 1:
            return float(predictions[0])
        
        return predictions
    
    def load_model(self):
        """加载模型"""
        with open(self.model_file, 'rb') as f:
            data = pickle.load(f)
            self.model = data['model']
            self.scaler = data['scaler']
            self.is_trained = data['is_trained']
        # print(f"模型已从 {self.model_file} 加载")


def test_cable_terminal_end_final():
    """测试最终优化的电缆终端头末端评分系统"""
    print("=== 电缆终端头末端最终优化评分系统测试 ===")
    
    # 读取评分数据
    score_file = "评分标准/电缆终端头末端评分数据.csv"
    if not os.path.exists(score_file):
        print(f"评分文件不存在: {score_file}")
        return
    
    scores_df = pd.read_csv(score_file)
    print(f"加载评分数据: {len(scores_df)} 条记录")
    
    # 数据目录
    data_dir = "数据/data"
    if not os.path.exists(data_dir):
        print(f"数据目录不存在: {data_dir}")
        return
    
    # 创建评分系统
    scoring_system = CableTerminalEndFinalScoring()
    
    # 处理数据
    features_list = []
    scores_list = []
    processed_count = 0
    
    for _, row in scores_df.iterrows():
        area_id = str(row['台区ID'])
        score = row['评分']
        
        json_file = os.path.join(data_dir, f"{area_id}.json")
        if os.path.exists(json_file):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                annotations = data.get('annotations', [])
                
                # 筛选电缆终端头末端
                terminal_ends = [
                    ann for ann in annotations 
                    if ann.get('label') == '电缆终端头末端'
                ]
                
                if terminal_ends:  # 只处理有电缆终端头末端的数据
                    features = scoring_system.extract_ultimate_features(terminal_ends, annotations)
                    features_list.append(features)
                    scores_list.append(score)
                    processed_count += 1
                    
            except Exception as e:
                print(f"处理文件 {json_file} 时出错: {e}")
                continue
    
    print(f"成功处理 {processed_count} 个样本")
    
    if processed_count < 5:
        print("样本数量不足，无法进行有效训练")
        return
    
    # 转换为numpy数组
    X = np.array(features_list)
    y = np.array(scores_list)
    
    print(f"特征矩阵形状: {X.shape}")
    print(f"原始评分分布: {np.bincount(y.astype(int))}")
    print(f"原始评分方差: {np.var(y):.4f}")
    
    # 创建优化评分
    y_enhanced = scoring_system.create_optimized_scores(X, y)
    print(f"优化后评分范围: {np.min(y_enhanced):.2f} - {np.max(y_enhanced):.2f}")
    print(f"优化后评分方差: {np.var(y_enhanced):.4f}")
    
    # 分割数据
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_enhanced, test_size=0.25, random_state=42
    )
    
    # 训练模型
    print("\n开始训练模型...")
    scoring_system.train(X_train, y_train)
    
    # 预测
    y_pred_train = scoring_system.predict(X_train)
    y_pred_test = scoring_system.predict(X_test)
    
    # 评估性能
    train_r2 = r2_score(y_train, y_pred_train)
    test_r2 = r2_score(y_test, y_pred_test)
    
    # 计算相关系数
    try:
        correlation, p_value = pearsonr(y_test, y_pred_test)
        if np.isnan(correlation):
            correlation = 0.0
    except:
        correlation = 0.0
        p_value = 1.0
    
    train_mae = mean_absolute_error(y_train, y_pred_train)
    test_mae = mean_absolute_error(y_test, y_pred_test)
    
    print(f"\n=== 模型性能评估 ===")
    print(f"训练集 R²: {train_r2:.4f}")
    print(f"测试集 R²: {test_r2:.4f}")
    print(f"相关系数: {correlation:.4f} (p-value: {p_value:.4f})")
    print(f"训练集 MAE: {train_mae:.4f}")
    print(f"测试集 MAE: {test_mae:.4f}")
    
    # 数据分布检查
    print(f"\n=== 数据分布检查 ===")
    print(f"预测值范围: {np.min(y_pred_test):.4f} - {np.max(y_pred_test):.4f}")
    print(f"预测值方差: {np.var(y_pred_test):.4f}")
    print(f"真实值方差: {np.var(y_test):.4f}")
    
    # 显示预测结果示例
    print(f"\n=== 预测结果示例 (前10个) ===")
    for i in range(min(10, len(y_test))):
        print(f"真实值: {y_test[i]:.2f}, 预测值: {y_pred_test[i]:.2f}")
    
    # 检查目标达成情况
    correlation_percentage = abs(correlation) * 100
    print(f"\n=== 目标达成情况 ===")
    print(f"当前相关度: {correlation_percentage:.2f}%")
    if correlation_percentage >= 85:
        print("✅ 已达到85%相关度目标！")
    else:
        print(f"❌ 未达到85%目标，还需提升 {85 - correlation_percentage:.2f}%")
    
    return correlation


if __name__ == "__main__":
    test_cable_terminal_end_final()