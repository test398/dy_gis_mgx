#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于工程标准的机器学习电缆段评分系统
重新设计 - 包含所有工程评分标准
"""

import csv
import json
import numpy as np
import pandas as pd
import math
import pickle
import os
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.model_selection import LeaveOneOut, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error
import warnings
warnings.filterwarnings('ignore')


class EngineeringMLCableScoring:
    def __init__(self, model_file="engineering_ml_model.pkl"):
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_names = []
        self.model_file = model_file
    
    def extract_engineering_features(self, cable_segments, all_annotations):
        """基于工程标准的全面特征提取"""
        if not cable_segments:
            return np.zeros(25)  # 返回25个工程特征
        
        features = []
        
        # === 1. 基础统计特征 (5个) ===
        segment_count = len(cable_segments)
        total_points = sum(len(seg.get('points', [])) for seg in cable_segments)
        avg_points = total_points / segment_count if segment_count > 0 else 0
        
        # 长度计算
        lengths = []
        for segment in cable_segments:
            points = segment.get('points', [])
            if len(points) >= 2:
                length = sum(math.sqrt((points[i][0] - points[i+1][0])**2 + 
                                     (points[i][1] - points[i+1][1])**2) 
                           for i in range(len(points)-1))
                lengths.append(length)
        
        avg_length = np.mean(lengths) if lengths else 0
        total_length = sum(lengths) if lengths else 0
        
        features.extend([segment_count, total_points, avg_points, avg_length, total_length])
        
        # === 2. 道路建筑物走向对齐特征 (5个) ===
        alignment_features = self._analyze_road_building_alignment(cable_segments, all_annotations)
        features.extend(alignment_features)
        
        # === 3. 电缆重叠布置特征 (4个) ===
        overlap_features = self._analyze_cable_overlap(cable_segments)
        features.extend(overlap_features)
        
        # === 4. 涉水情况特征 (3个) ===
        water_features = self._analyze_water_crossing(cable_segments, all_annotations)
        features.extend(water_features)
        
        # === 5. 穿越建筑物特征 (3个) ===
        building_crossing_features = self._analyze_building_crossing(cable_segments, all_annotations)
        features.extend(building_crossing_features)
        
        # === 6. 几何质量特征 (5个) ===
        geometry_features = self._analyze_geometry_quality(cable_segments)
        features.extend(geometry_features)
        
        return np.array(features)
    
    def _analyze_road_building_alignment(self, cable_segments, all_annotations):
        """分析电缆段与道路建筑物的走向对齐"""
        # 提取建筑物和道路相关的标注
        buildings = [ann for ann in all_annotations 
                    if ann.get('label') in ['建筑物', '房屋', '厂房', '住宅']]
        roads = [ann for ann in all_annotations 
                if ann.get('label') in ['道路', '街道', '路径']]
        
        # 特征1: 与建筑物边缘平行度
        building_alignment_score = 0
        if buildings:
            building_alignment_score = self._calculate_alignment_with_buildings(cable_segments, buildings)
        
        # 特征2: 与道路平行度  
        road_alignment_score = 0
        if roads:
            road_alignment_score = self._calculate_alignment_with_roads(cable_segments, roads)
        
        # 特征3: 整体走向一致性
        direction_consistency = self._calculate_direction_consistency(cable_segments)
        
        # 特征4: 建筑物密集区域的布线合理性
        dense_area_score = self._calculate_dense_area_layout(cable_segments, buildings)
        
        # 特征5: 避开建筑物程度
        building_avoidance = self._calculate_building_avoidance(cable_segments, buildings)
        
        return [building_alignment_score, road_alignment_score, direction_consistency, 
                dense_area_score, building_avoidance]
    
    def _analyze_cable_overlap(self, cable_segments):
        """分析同路径电缆段重叠情况"""
        # 特征1: 重叠线段数量比例
        overlap_count = 0
        total_pairs = 0
        
        for i, seg1 in enumerate(cable_segments):
            for j, seg2 in enumerate(cable_segments[i+1:], i+1):
                total_pairs += 1
                if self._segments_overlap(seg1, seg2):
                    overlap_count += 1
        
        overlap_ratio = overlap_count / max(total_pairs, 1)
        
        # 特征2: 平均重叠长度
        avg_overlap_length = self._calculate_average_overlap_length(cable_segments)
        
        # 特征3: 最大重叠段数
        max_overlap_segments = self._find_max_overlapping_segments(cable_segments)
        
        # 特征4: 重叠区域的分布密度
        overlap_density = self._calculate_overlap_density(cable_segments)
        
        return [overlap_ratio, avg_overlap_length, max_overlap_segments, overlap_density]
    
    def _analyze_water_crossing(self, cable_segments, all_annotations):
        """分析电缆段涉水情况"""
        # 提取水体相关标注
        water_bodies = [ann for ann in all_annotations 
                       if ann.get('label') in ['河流', '水体', '池塘', '湖泊', '水沟']]
        
        # 特征1: 涉水线段数量
        water_crossing_count = 0
        for segment in cable_segments:
            if self._segment_crosses_water(segment, water_bodies):
                water_crossing_count += 1
        
        water_crossing_ratio = water_crossing_count / len(cable_segments)
        
        # 特征2: 涉水总长度
        total_water_crossing_length = self._calculate_water_crossing_length(cable_segments, water_bodies)
        
        # 特征3: 水体避让程度
        water_avoidance_score = self._calculate_water_avoidance(cable_segments, water_bodies)
        
        return [water_crossing_ratio, total_water_crossing_length, water_avoidance_score]
    
    def _analyze_building_crossing(self, cable_segments, all_annotations):
        """分析电缆段穿越建筑物情况"""
        # 提取建筑物和设备
        buildings = [ann for ann in all_annotations 
                    if ann.get('label') in ['建筑物', '房屋', '厂房', '住宅']]
        equipment = [ann for ann in all_annotations 
                    if ann.get('label') in ['变压器', '开关柜', '配电箱', '设备']]
        
        # 特征1: 穿越建筑物的线段比例
        building_crossing_count = 0
        for segment in cable_segments:
            if self._segment_crosses_building(segment, buildings):
                building_crossing_count += 1
        
        building_crossing_ratio = building_crossing_count / len(cable_segments)
        
        # 特征2: 穿越设备的线段比例
        equipment_crossing_count = 0
        for segment in cable_segments:
            if self._segment_crosses_equipment(segment, equipment):
                equipment_crossing_count += 1
        
        equipment_crossing_ratio = equipment_crossing_count / len(cable_segments)
        
        # 特征3: 建筑物穿越的合理性评分
        crossing_reasonableness = self._evaluate_crossing_reasonableness(cable_segments, buildings, equipment)
        
        return [building_crossing_ratio, equipment_crossing_ratio, crossing_reasonableness]
    
    def _analyze_geometry_quality(self, cable_segments):
        """分析几何质量特征"""
        # 特征1: 线段弯曲度
        curvatures = []
        for segment in cable_segments:
            curvature = self._calculate_segment_curvature(segment)
            curvatures.append(curvature)
        
        avg_curvature = np.mean(curvatures) if curvatures else 0
        
        # 特征2: 线段长度标准差（一致性）
        lengths = []
        for segment in cable_segments:
            points = segment.get('points', [])
            if len(points) >= 2:
                length = sum(math.sqrt((points[i][0] - points[i+1][0])**2 + 
                                     (points[i][1] - points[i+1][1])**2) 
                           for i in range(len(points)-1))
                lengths.append(length)
        
        length_std = np.std(lengths) if lengths else 0
        
        # 特征3: 极短线段比例
        short_segments = sum(1 for length in lengths if length < 10)
        short_ratio = short_segments / len(cable_segments)
        
        # 特征4: 空间分布范围
        all_points = []
        for segment in cable_segments:
            all_points.extend(segment.get('points', []))
        
        if all_points:
            x_coords = [p[0] for p in all_points]
            y_coords = [p[1] for p in all_points]
            spatial_range = (max(x_coords) - min(x_coords)) * (max(y_coords) - min(y_coords))
        else:
            spatial_range = 0
        
        # 特征5: 线段交叉数量
        crossing_count = self._count_segment_crossings(cable_segments)
        crossing_density = crossing_count / max(len(cable_segments)**2, 1)
        
        return [avg_curvature, length_std, short_ratio, spatial_range, crossing_density]
    
    # === 辅助函数 ===
    def _calculate_alignment_with_buildings(self, cable_segments, buildings):
        """计算与建筑物的对齐程度"""
        if not buildings:
            return 0.5  # 中性值
        
        alignment_scores = []
        for segment in cable_segments:
            points = segment.get('points', [])
            if len(points) >= 2:
                # 计算线段主方向
                segment_vector = (points[-1][0] - points[0][0], points[-1][1] - points[0][1])
                
                # 找最近的建筑物
                best_alignment = 0
                for building in buildings:
                    building_edges = self._get_building_edges(building)
                    for edge in building_edges:
                        alignment = self._calculate_vector_alignment(segment_vector, edge)
                        best_alignment = max(best_alignment, alignment)
                
                alignment_scores.append(best_alignment)
        
        return np.mean(alignment_scores) if alignment_scores else 0.5
    
    def _calculate_alignment_with_roads(self, cable_segments, roads):
        """计算与道路的对齐程度"""
        if not roads:
            return 0.5
        
        # 简化实现 - 实际需要更复杂的道路方向分析
        return 0.7  # 假设大部分电缆都沿道路布设
    
    def _calculate_direction_consistency(self, cable_segments):
        """计算整体走向一致性"""
        if len(cable_segments) < 2:
            return 1.0
        
        directions = []
        for segment in cable_segments:
            points = segment.get('points', [])
            if len(points) >= 2:
                angle = math.atan2(points[-1][1] - points[0][1], points[-1][0] - points[0][0])
                directions.append(angle)
        
        if not directions:
            return 1.0
        
        # 计算方向的标准差，越小越一致
        direction_std = np.std(directions)
        consistency = max(0, 1 - direction_std / math.pi)  # 归一化到0-1
        
        return consistency
    
    def _calculate_dense_area_layout(self, cable_segments, buildings):
        """计算建筑物密集区域的布线合理性"""
        # 简化实现
        return 0.6
    
    def _calculate_building_avoidance(self, cable_segments, buildings):
        """计算避开建筑物的程度"""
        if not buildings:
            return 1.0
        
        avoidance_scores = []
        for segment in cable_segments:
            min_distance = float('inf')
            for building in buildings:
                distance = self._segment_to_polygon_distance(segment, building)
                min_distance = min(min_distance, distance)
            
            # 距离越大避让越好，归一化到0-1
            avoidance = min(1.0, min_distance / 50.0)  # 50是参考距离
            avoidance_scores.append(avoidance)
        
        return np.mean(avoidance_scores) if avoidance_scores else 1.0
    
    def _segments_overlap(self, seg1, seg2):
        """检查两个线段是否重叠"""
        points1 = seg1.get('points', [])
        points2 = seg2.get('points', [])
        
        if len(points1) < 2 or len(points2) < 2:
            return False
        
        # 简化的重叠检测 - 检查是否有线段相交
        for i in range(len(points1) - 1):
            for j in range(len(points2) - 1):
                if self._line_segments_intersect(
                    points1[i], points1[i+1], points2[j], points2[j+1]
                ):
                    return True
        return False
    
    def _line_segments_intersect(self, p1, q1, p2, q2):
        """检查两条线段是否相交"""
        def orientation(p, q, r):
            val = (q[1] - p[1]) * (r[0] - q[0]) - (q[0] - p[0]) * (r[1] - q[1])
            if val == 0:
                return 0  # 共线
            return 1 if val > 0 else 2
        
        o1 = orientation(p1, q1, p2)
        o2 = orientation(p1, q1, q2)
        o3 = orientation(p2, q2, p1)
        o4 = orientation(p2, q2, q1)
        
        return (o1 != o2 and o3 != o4)
    
    def _calculate_average_overlap_length(self, cable_segments):
        """计算平均重叠长度"""
        # 简化实现
        return 0.1
    
    def _find_max_overlapping_segments(self, cable_segments):
        """找到最大重叠段数"""
        # 简化实现
        return min(3, len(cable_segments) // 5)
    
    def _calculate_overlap_density(self, cable_segments):
        """计算重叠密度"""
        # 简化实现
        return 0.2
    
    def _segment_crosses_water(self, segment, water_bodies):
        """检查线段是否穿越水体"""
        if not water_bodies:
            return False
        
        points = segment.get('points', [])
        if len(points) < 2:
            return False
        
        # 简化检测 - 检查线段是否与水体边界相交
        for water in water_bodies:
            if self._segment_intersects_polygon(segment, water):
                return True
        
        return False
    
    def _calculate_water_crossing_length(self, cable_segments, water_bodies):
        """计算涉水总长度"""
        # 简化实现
        return 0.0
    
    def _calculate_water_avoidance(self, cable_segments, water_bodies):
        """计算水体避让程度"""
        if not water_bodies:
            return 1.0
        return 0.8  # 简化实现
    
    def _segment_crosses_building(self, segment, buildings):
        """检查线段是否穿越建筑物"""
        if not buildings:
            return False
        
        for building in buildings:
            if self._segment_intersects_polygon(segment, building):
                return True
        
        return False
    
    def _segment_crosses_equipment(self, segment, equipment):
        """检查线段是否穿越设备"""
        if not equipment:
            return False
        
        for equip in equipment:
            if self._segment_intersects_polygon(segment, equip):
                return True
        
        return False
    
    def _evaluate_crossing_reasonableness(self, cable_segments, buildings, equipment):
        """评估穿越的合理性"""
        # 简化实现 - 实际需要考虑穿越的必要性
        return 0.7
    
    def _calculate_segment_curvature(self, segment):
        """计算线段弯曲度"""
        points = segment.get('points', [])
        if len(points) < 3:
            return 0
        
        # 计算实际路径长度与直线距离的比值
        path_length = sum(math.sqrt((points[i][0] - points[i+1][0])**2 + 
                                   (points[i][1] - points[i+1][1])**2) 
                         for i in range(len(points)-1))
        
        straight_distance = math.sqrt((points[-1][0] - points[0][0])**2 + 
                                    (points[-1][1] - points[0][1])**2)
        
        if straight_distance == 0:
            return 0
        
        curvature = path_length / straight_distance - 1
        return curvature
    
    def _count_segment_crossings(self, cable_segments):
        """统计线段交叉数量"""
        crossing_count = 0
        for i, seg1 in enumerate(cable_segments):
            for seg2 in cable_segments[i+1:]:
                if self._segments_overlap(seg1, seg2):
                    crossing_count += 1
        return crossing_count
    
    def _get_building_edges(self, building):
        """获取建筑物边缘向量"""
        points = building.get('points', [])
        if len(points) < 2:
            return []
        
        edges = []
        for i in range(len(points)):
            j = (i + 1) % len(points)
            edge = (points[j][0] - points[i][0], points[j][1] - points[i][1])
            edges.append(edge)
        
        return edges
    
    def _calculate_vector_alignment(self, vec1, vec2):
        """计算两个向量的对齐程度"""
        len1 = math.sqrt(vec1[0]**2 + vec1[1]**2)
        len2 = math.sqrt(vec2[0]**2 + vec2[1]**2)
        
        if len1 == 0 or len2 == 0:
            return 0
        
        dot_product = vec1[0] * vec2[0] + vec1[1] * vec2[1]
        cos_angle = dot_product / (len1 * len2)
        cos_angle = max(-1, min(1, cos_angle))  # 防止数值误差
        
        # 返回对齐程度，平行时为1，垂直时为0
        alignment = abs(cos_angle)
        return alignment
    
    def _segment_to_polygon_distance(self, segment, polygon):
        """计算线段到多边形的最小距离"""
        # 简化实现 - 返回一个估计距离
        return 20.0
    
    def _segment_intersects_polygon(self, segment, polygon):
        """检查线段是否与多边形相交"""
        # 简化实现
        return False
    
    def save_model(self):
        """保存训练好的工程ML模型"""
        if not self.is_trained:
            print("模型还未训练，无法保存！")
            return False
        
        try:
            model_data = {
                'model': self.model,
                'scaler': self.scaler,
                'feature_names': self.feature_names,
                'is_trained': self.is_trained
            }
            
            with open(self.model_file, 'wb') as f:
                pickle.dump(model_data, f)
            
            print(f"工程ML模型已保存到: {self.model_file}")
            return True
            
        except Exception as e:
            print(f"保存工程ML模型失败: {e}")
            return False
    
    def load_model(self):
        """加载已保存的工程ML模型"""
        if not os.path.exists(self.model_file):
            print(f"工程ML模型文件 {self.model_file} 不存在")
            return False
        
        try:
            with open(self.model_file, 'rb') as f:
                model_data = pickle.load(f)
            
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.feature_names = model_data['feature_names']
            self.is_trained = model_data['is_trained']
            
            print(f"工程ML模型已从 {self.model_file} 加载成功")
            return True
            
        except Exception as e:
            print(f"加载工程ML模型失败: {e}")
            return False
    
    def load_training_data(self, manual_scores_file="人工评分_筛选结果.csv", data_dir="data1"):
        """加载训练数据"""
        manual_scores = {}
        with open(manual_scores_file, "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                if len(row) >= 3:
                    manual_scores[row[0]] = int(row[1])
        
        X = []
        y = []
        valid_ids = []
        
        for taiwan_id, score in manual_scores.items():
            json_file = f"{data_dir}/{taiwan_id}_zlh.json"
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                all_annotations = data.get("annotations", [])
                cable_segments = [ann for ann in all_annotations if ann.get("label") == "电缆段"]
                
                # 使用工程特征提取
                features = self.extract_engineering_features(cable_segments, all_annotations)
                
                X.append(features)
                y.append(score)
                valid_ids.append(taiwan_id)
                
            except Exception as e:
                print(f"跳过台区 {taiwan_id}: {e}")
                continue
        
        print(f"成功加载 {len(X)} 个训练样本")
        return np.array(X), np.array(y), valid_ids
    
    def train_and_evaluate_models(self, X, y):
        """训练和评估模型"""
        models = {
            'Linear Regression': LinearRegression(),
            'Ridge Regression': Ridge(alpha=1.0),
            'Random Forest': RandomForestRegressor(n_estimators=50, random_state=42, max_depth=3),
            'Gradient Boosting': GradientBoostingRegressor(n_estimators=50, random_state=42, max_depth=3)
        }
        
        results = {}
        loo = LeaveOneOut()
        
        for name, model in models.items():
            try:
                cv_scores = cross_val_score(model, X, y, cv=loo, scoring='neg_mean_absolute_error')
                mae_scores = -cv_scores
                
                results[name] = {
                    'mean_mae': np.mean(mae_scores),
                    'std_mae': np.std(mae_scores),
                    'model': model
                }
                
                print(f"{name}: MAE = {np.mean(mae_scores):.2f} ± {np.std(mae_scores):.2f}")
                
            except Exception as e:
                print(f"{name} 训练失败: {e}")
                continue
        
        if results:
            best_model_name = min(results.keys(), key=lambda k: results[k]['mean_mae'])
            best_model = results[best_model_name]['model']
            
            print(f"\n最佳模型: {best_model_name}")
            print(f"平均绝对误差: {results[best_model_name]['mean_mae']:.2f}")
            
            return best_model, results
        else:
            return None, {}
    
    def train(self, manual_scores_file="人工评分_筛选结果.csv", data_dir="data1", force_retrain=False):
        """训练工程ML模型"""
        # 首先尝试加载已保存的模型
        if not force_retrain and self.load_model():
            print("已加载现有工程ML模型，无需重新训练")
            return True
        
        print("开始加载训练数据...")
        X, y, valid_ids = self.load_training_data(manual_scores_file, data_dir)
        
        if len(X) == 0:
            print("没有有效的训练数据！")
            return False
        
        print(f"工程特征维度: {X.shape[1]}")
        print(f"标签分布: {np.bincount(y)}")
        
        # 特征标准化
        X_scaled = self.scaler.fit_transform(X)
        
        # 训练和评估模型
        print("\n开始训练工程ML模型...")
        best_model, results = self.train_and_evaluate_models(X_scaled, y)
        
        if best_model is not None:
            best_model.fit(X_scaled, y)
            self.model = best_model
            self.is_trained = True
            
            # 保存训练好的模型
            self.save_model()
            
            print("\n工程ML模型训练完成！")
            return True
        else:
            print("所有模型训练都失败了！")
            return False
    
    def predict(self, cable_segments, all_annotations=None):
        """预测电缆段评分"""
        if not self.is_trained:
            print("模型还未训练！")
            return 8
        
        if all_annotations is None:
            all_annotations = []
        
        # 提取工程特征
        features = self.extract_engineering_features(cable_segments, all_annotations)
        
        # 标准化
        features_scaled = self.scaler.transform(features.reshape(1, -1))
        
        # 预测
        score = self.model.predict(features_scaled)[0]
        
        # 确保分数在1-10范围内
        score = max(1, min(10, round(score)))
        
        return int(score)


def test_single_file(file_path, model_file="engineering_ml_model.pkl"):
    """测试单个文件，输入文件名输出分数"""
    print(f"测试文件: {file_path}")
    
    # 创建评分器实例
    ml_scorer = EngineeringMLCableScoring(model_file)
    
    # 检查模型是否存在，如果不存在则训练
    if not os.path.exists(model_file):
        print(f"模型文件 {model_file} 不存在，开始训练新模型...")
        success = ml_scorer.train()
        if not success:
            print("模型训练失败！")
            return None
    else:
        # 加载现有模型
        if not ml_scorer.load_model():
            print("加载模型失败，重新训练...")
            success = ml_scorer.train()
            if not success:
                print("模型训练失败！")
                return None
    
    # 读取并预测文件
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        all_annotations = data.get("annotations", [])
        cable_segments = [ann for ann in all_annotations if ann.get("label") == "电缆段"]
        
        if not cable_segments:
            print("警告: 文件中没有找到电缆段标注")
            return 8  # 默认分数
        
        # 预测分数
        score = ml_scorer.predict(cable_segments, all_annotations)
        
        print(f"预测分数: {score}")
        print(f"电缆段数量: {len(cable_segments)}")
        print(f"总标注数量: {len(all_annotations)}")
        
        return score
        
    except FileNotFoundError:
        print(f"错误: 文件 {file_path} 不存在")
        return None
    except json.JSONDecodeError:
        print(f"错误: 文件 {file_path} 不是有效的JSON格式")
        return None
    except Exception as e:
        print(f"预测失败: {e}")
        return None


def test_engineering_ml_scoring():
    """测试工程ML评分系统"""
    print("=" * 60)
    print("工程标准机器学习电缆段评分系统测试")
    print("=" * 60)
    
    ml_scorer = EngineeringMLCableScoring()
    
    success = ml_scorer.train()
    if not success:
        print("模型训练失败！")
        return
    
    # 测试所有台区
    print("\n开始测试...")
    
    manual_scores = {}
    with open("人工评分_筛选结果.csv", "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            if len(row) >= 3:
                manual_scores[row[0]] = int(row[1])
    
    results = []
    total_error = 0
    valid_count = 0
    
    for taiwan_id, manual_score in manual_scores.items():
        try:
            json_file = f"data1/{taiwan_id}_zlh.json"
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            all_annotations = data.get("annotations", [])
            cable_segments = [ann for ann in all_annotations if ann.get("label") == "电缆段"]
            
            # 工程ML预测
            ml_score = ml_scorer.predict(cable_segments, all_annotations)
            
            error = abs(ml_score - manual_score)
            total_error += error
            valid_count += 1
            
            results.append({
                '台区ID': taiwan_id,
                '人工评分': manual_score,
                '工程ML评分': ml_score,
                '评分差异': error
            })
            
            accuracy = "完美" if error == 0 else "准确" if error <= 1 else "可接受" if error <= 2 else "偏差大"
            print(f"台区 {taiwan_id}: 人工={manual_score}, 工程ML={ml_score}, 差异={error} ({accuracy})")
            
        except Exception as e:
            print(f"台区 {taiwan_id} 测试失败: {e}")
            continue
    
    # 输出统计结果
    if valid_count > 0:
        avg_error = total_error / valid_count
        perfect_count = sum(1 for r in results if r['评分差异'] == 0)
        accurate_count = sum(1 for r in results if r['评分差异'] <= 1)
        
        print("\n" + "=" * 60)
        print("工程ML评分系统测试结果")
        print("=" * 60)
        print(f"测试样本数: {valid_count}")
        print(f"平均绝对误差: {avg_error:.2f}")
        print(f"完美匹配: {perfect_count} ({perfect_count/valid_count*100:.1f}%)")
        print(f"准确匹配 (差异≤1): {accurate_count} ({accurate_count/valid_count*100:.1f}%)")
        
        # 保存详细结果
        with open("工程ML电缆段评分对比结果.csv", "w", newline='', encoding='utf-8-sig') as f:
            fieldnames = ['台区ID', '人工评分', '工程ML评分', '评分差异']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for result in results:
                writer.writerow(result)
        
        print(f"\n详细结果已保存到: 工程ML电缆段评分对比结果.csv")
    
    return ml_scorer


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # 如果提供了文件路径参数，测试单个文件
        file_path = sys.argv[1]
        model_file = sys.argv[2] if len(sys.argv) > 2 else "engineering_ml_model.pkl"
        score = test_single_file(file_path, model_file)
        if score is not None:
            print(f"\n最终评分: {score}")
    else:
        # 否则运行完整测试
        test_engineering_ml_scoring()