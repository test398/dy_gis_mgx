#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于工程标准的机器学习档距段评分系统
根据档距段说明.jpg中的评分标准设计
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


class PoleSpanMLScoring:
    def __init__(self, model_file="pole_span_ml_model.pkl"):
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_names = []
        self.model_file = model_file
    
    def extract_pole_span_features(self, cable_segments, all_annotations):
        """基于档距段评分标准的特征提取"""
        if not cable_segments:
            return np.array([6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])  # 台区无档距段，记为满分相关特征
        
        features = []
        
        # === 1. 基础统计特征 (3个) ===
        segment_count = len(cable_segments)
        
        # 计算所有档距段长度
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
        
        features.extend([segment_count, avg_length, total_length])
        
        # === 2. 等长原则特征 (4个) ===
        length_compliance_features = self._analyze_length_compliance(lengths)
        features.extend(length_compliance_features)
        
        # === 3. 交叉折叠特征 (4个) ===
        crossing_features = self._analyze_crossing_folding(cable_segments)
        features.extend(crossing_features)
        
        # === 4. 折角特征 (4个) ===
        angle_features = self._analyze_angles(cable_segments)
        features.extend(angle_features)
        
        return np.array(features)
    
    def _analyze_length_compliance(self, lengths):
        """分析等长原则符合情况"""
        if not lengths:
            return [1.0, 0, 0, 0]  # 无档距段时返回理想值
        
        # 特征1: 长度标准差（越小越好）
        length_std = np.std(lengths)
        length_consistency = max(0, 1 - length_std / 100)  # 标准化
        
        # 特征2: 符合50-100米标准的比例
        optimal_count = sum(1 for length in lengths if 50 <= length <= 100)
        optimal_ratio = optimal_count / len(lengths)
        
        # 特征3: 超长档距段比例（>100米）
        overlong_count = sum(1 for length in lengths if length > 100)
        overlong_ratio = overlong_count / len(lengths)
        
        # 特征4: 超短档距段比例（<50米）
        undershort_count = sum(1 for length in lengths if length < 50)
        undershort_ratio = undershort_count / len(lengths)
        
        return [length_consistency, optimal_ratio, overlong_ratio, undershort_ratio]
    
    def _analyze_crossing_folding(self, cable_segments):
        """分析档距段交叉折叠情况"""
        if len(cable_segments) < 2:
            return [1.0, 0, 0, 0]  # 少于2个档距段时无交叉
        
        # 特征1: 档距段交叉数量
        crossing_count = 0
        total_pairs = 0
        
        for i, seg1 in enumerate(cable_segments):
            for j, seg2 in enumerate(cable_segments[i+1:], i+1):
                total_pairs += 1
                if self._segments_intersect(seg1, seg2):
                    crossing_count += 1
        
        crossing_ratio = crossing_count / max(total_pairs, 1)
        
        # 特征2: 档距段重叠程度
        overlap_severity = self._calculate_overlap_severity(cable_segments)
        
        # 特征3: 档距段间最小距离
        min_distance = self._calculate_min_segment_distance(cable_segments)
        min_distance_score = min(1.0, min_distance / 20.0)  # 20米作为参考
        
        # 特征4: 档距段分布密度
        distribution_density = self._calculate_distribution_density(cable_segments)
        
        return [1 - crossing_ratio, 1 - overlap_severity, min_distance_score, 1 - distribution_density]
    
    def _analyze_angles(self, cable_segments):
        """分析档距段折角情况"""
        if not cable_segments:
            return [1.0, 0, 0, 0]
        
        all_angles = []
        sharp_angle_count = 0
        
        for segment in cable_segments:
            points = segment.get('points', [])
            if len(points) < 3:
                continue
            
            # 计算每个点的转角
            for i in range(1, len(points) - 1):
                p1, p2, p3 = points[i-1], points[i], points[i+1]
                
                # 计算向量
                vec1 = (p1[0] - p2[0], p1[1] - p2[1])
                vec2 = (p3[0] - p2[0], p3[1] - p2[1])
                
                # 计算夹角
                angle = self._calculate_vector_angle(vec1, vec2)
                all_angles.append(angle)
                
                # 统计锐角（小于90度）
                if angle < math.pi / 2:
                    sharp_angle_count += 1
        
        if not all_angles:
            return [1.0, 0, 0, 0]
        
        # 特征1: 平均角度（越接近180度越好）
        avg_angle = np.mean(all_angles)
        angle_quality = avg_angle / math.pi  # 归一化到0-1
        
        # 特征2: 锐角比例（越少越好）
        sharp_angle_ratio = sharp_angle_count / len(all_angles)
        
        # 特征3: 角度标准差（越小越好，表示角度一致）
        angle_std = np.std(all_angles)
        angle_consistency = max(0, 1 - angle_std / math.pi)
        
        # 特征4: 最小角度
        min_angle = min(all_angles)
        min_angle_score = min_angle / (math.pi / 2)  # 以90度为参考
        
        return [angle_quality, 1 - sharp_angle_ratio, angle_consistency, min_angle_score]
    
    # === 辅助函数 ===
    def _segments_intersect(self, seg1, seg2):
        """检查两个档距段是否相交"""
        points1 = seg1.get('points', [])
        points2 = seg2.get('points', [])
        
        if len(points1) < 2 or len(points2) < 2:
            return False
        
        # 检查线段相交
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
    
    def _calculate_overlap_severity(self, cable_segments):
        """计算重叠严重程度"""
        # 简化实现
        return 0.1
    
    def _calculate_min_segment_distance(self, cable_segments):
        """计算档距段间最小距离"""
        if len(cable_segments) < 2:
            return 100.0  # 只有一个档距段时返回大值
        
        min_dist = float('inf')
        for i, seg1 in enumerate(cable_segments):
            for seg2 in cable_segments[i+1:]:
                dist = self._segment_to_segment_distance(seg1, seg2)
                min_dist = min(min_dist, dist)
        
        return min_dist if min_dist != float('inf') else 100.0
    
    def _segment_to_segment_distance(self, seg1, seg2):
        """计算两个档距段之间的最小距离"""
        # 简化实现 - 返回估计距离
        return 15.0
    
    def _calculate_distribution_density(self, cable_segments):
        """计算档距段分布密度"""
        if not cable_segments:
            return 0
        
        # 计算所有档距段的空间范围
        all_points = []
        for segment in cable_segments:
            all_points.extend(segment.get('points', []))
        
        if len(all_points) < 2:
            return 0
        
        x_coords = [p[0] for p in all_points]
        y_coords = [p[1] for p in all_points]
        
        x_range = max(x_coords) - min(x_coords)
        y_range = max(y_coords) - min(y_coords)
        area = max(x_range * y_range, 1)
        
        # 密度 = 档距段数量 / 覆盖面积
        density = len(cable_segments) / area * 10000  # 归一化
        return min(density, 1.0)
    
    def _calculate_vector_angle(self, vec1, vec2):
        """计算两个向量之间的夹角"""
        len1 = math.sqrt(vec1[0]**2 + vec1[1]**2)
        len2 = math.sqrt(vec2[0]**2 + vec2[1]**2)
        
        if len1 == 0 or len2 == 0:
            return math.pi  # 返回180度
        
        dot_product = vec1[0] * vec2[0] + vec1[1] * vec2[1]
        cos_angle = dot_product / (len1 * len2)
        cos_angle = max(-1, min(1, cos_angle))  # 防止数值误差
        
        angle = math.acos(abs(cos_angle))  # 取绝对值，确保角度为正
        return angle
    
    def save_model(self):
        """保存训练好的档距段ML模型"""
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
            
            print(f"档距段ML模型已保存到: {self.model_file}")
            return True
            
        except Exception as e:
            print(f"保存档距段ML模型失败: {e}")
            return False
    
    def load_model(self):
        """加载已保存的档距段ML模型"""
        if not os.path.exists(self.model_file):
            print(f"档距段ML模型文件 {self.model_file} 不存在")
            return False
        
        try:
            with open(self.model_file, 'rb') as f:
                model_data = pickle.load(f)
            
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.feature_names = model_data['feature_names']
            self.is_trained = model_data['is_trained']
            
            print(f"档距段ML模型已从 {self.model_file} 加载成功")
            return True
            
        except Exception as e:
            print(f"加载档距段ML模型失败: {e}")
            return False
    
    def load_training_data(self, manual_scores_file="人工评分_筛选结果.csv", data_dir="data1"):
        """加载档距段训练数据"""
        manual_scores = {}
        with open(manual_scores_file, "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            header = next(reader)  # 跳过标题行
            for row in reader:
                if len(row) >= 3:  # ID, 电缆段, 档距段
                    manual_scores[row[0]] = int(row[2])  # 取档距段评分
        
        X = []
        y = []
        valid_ids = []
        
        for taiwan_id, score in manual_scores.items():
            json_file = f"{data_dir}/{taiwan_id}_zlh.json"
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                all_annotations = data.get("annotations", [])
                # 寻找档距段标注，如果没有则使用电缆段作为代替
                pole_spans = [ann for ann in all_annotations if ann.get("label") in ["档距段", "电缆段"]]
                
                # 使用档距段特征提取
                features = self.extract_pole_span_features(pole_spans, all_annotations)
                
                X.append(features)
                y.append(score)
                valid_ids.append(taiwan_id)
                
            except Exception as e:
                print(f"跳过台区 {taiwan_id}: {e}")
                continue
        
        print(f"成功加载 {len(X)} 个档距段训练样本")
        return np.array(X), np.array(y), valid_ids
    
    def train_and_evaluate_models(self, X, y):
        """训练和评估档距段模型"""
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
        """训练档距段ML模型"""
        # 首先尝试加载已保存的模型
        if not force_retrain and self.load_model():
            print("已加载现有档距段ML模型，无需重新训练")
            return True
        
        print("开始加载档距段训练数据...")
        X, y, valid_ids = self.load_training_data(manual_scores_file, data_dir)
        
        if len(X) == 0:
            print("没有有效的训练数据！")
            return False
        
        print(f"档距段特征维度: {X.shape[1]}")
        print(f"标签分布: {np.bincount(y)}")
        
        # 特征标准化
        X_scaled = self.scaler.fit_transform(X)
        
        # 训练和评估模型
        print("\n开始训练档距段ML模型...")
        best_model, results = self.train_and_evaluate_models(X_scaled, y)
        
        if best_model is not None:
            best_model.fit(X_scaled, y)
            self.model = best_model
            self.is_trained = True
            
            # 保存训练好的模型
            self.save_model()
            
            print("\n档距段ML模型训练完成！")
            return True
        else:
            print("所有模型训练都失败了！")
            return False
    
    def predict(self, pole_spans, all_annotations=None):
        """预测档距段评分"""
        if not self.is_trained:
            print("模型还未训练！")
            return 6  # 默认满分
        
        if all_annotations is None:
            all_annotations = []
        
        # 如果没有档距段，返回满分6
        if not pole_spans:
            return 6
        
        # 提取档距段特征
        features = self.extract_pole_span_features(pole_spans, all_annotations)
        
        # 标准化
        features_scaled = self.scaler.transform(features.reshape(1, -1))
        
        # 预测
        score = self.model.predict(features_scaled)[0]
        
        # 确保分数在0-6范围内
        score = max(0, min(6, round(score)))
        
        return int(score)


def test_single_file(file_path, model_file="pole_span_ml_model.pkl"):
    """测试单个文件，输入文件名输出档距段分数"""
    print(f"测试文件: {file_path}")
    
    # 创建评分器实例
    ml_scorer = PoleSpanMLScoring(model_file)
    
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
        # 寻找档距段标注，如果没有则使用电缆段作为代替
        pole_spans = [ann for ann in all_annotations if ann.get("label") in ["档距段", "电缆段"]]
        
        if not pole_spans:
            print("警告: 文件中没有找到档距段或电缆段标注，返回满分")
            return 6  # 台区无档距段，记为满分
        
        # 预测分数
        score = ml_scorer.predict(pole_spans, all_annotations)
        
        print(f"预测分数: {score}")
        print(f"档距段数量: {len([ann for ann in pole_spans if ann.get('label') == '档距段'])}")
        print(f"电缆段数量: {len([ann for ann in pole_spans if ann.get('label') == '电缆段'])}")
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


def test_pole_span_ml_scoring():
    """测试档距段ML评分系统"""
    print("=" * 60)
    print("档距段机器学习评分系统测试")
    print("=" * 60)
    
    ml_scorer = PoleSpanMLScoring()
    
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
                manual_scores[row[0]] = int(row[2])  # 档距段评分
    
    results = []
    total_error = 0
    valid_count = 0
    
    for taiwan_id, manual_score in manual_scores.items():
        try:
            json_file = f"data1/{taiwan_id}_zlh.json"
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            all_annotations = data.get("annotations", [])
            pole_spans = [ann for ann in all_annotations if ann.get("label") in ["档距段", "电缆段"]]
            
            # 档距段ML预测
            ml_score = ml_scorer.predict(pole_spans, all_annotations)
            
            error = abs(ml_score - manual_score)
            total_error += error
            valid_count += 1
            
            results.append({
                '台区ID': taiwan_id,
                '人工评分': manual_score,
                '档距段ML评分': ml_score,
                '评分差异': error
            })
            
            accuracy = "完美" if error == 0 else "准确" if error <= 1 else "可接受" if error <= 2 else "偏差大"
            print(f"台区 {taiwan_id}: 人工={manual_score}, 档距段ML={ml_score}, 差异={error} ({accuracy})")
            
        except Exception as e:
            print(f"台区 {taiwan_id} 测试失败: {e}")
            continue
    
    # 输出统计结果
    if valid_count > 0:
        avg_error = total_error / valid_count
        perfect_count = sum(1 for r in results if r['评分差异'] == 0)
        accurate_count = sum(1 for r in results if r['评分差异'] <= 1)
        
        print("\n" + "=" * 60)
        print("档距段ML评分系统测试结果")
        print("=" * 60)
        print(f"测试样本数: {valid_count}")
        print(f"平均绝对误差: {avg_error:.2f}")
        print(f"完美匹配: {perfect_count} ({perfect_count/valid_count*100:.1f}%)")
        print(f"准确匹配 (差异≤1): {accurate_count} ({accurate_count/valid_count*100:.1f}%)")
        
        # 保存详细结果
        with open("档距段ML评分对比结果.csv", "w", newline='', encoding='utf-8-sig') as f:
            fieldnames = ['台区ID', '人工评分', '档距段ML评分', '评分差异']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for result in results:
                writer.writerow(result)
        
        print(f"\n详细结果已保存到: 档距段ML评分对比结果.csv")
    
    return ml_scorer


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # 如果提供了文件路径参数，测试单个文件
        file_path = sys.argv[1]
        model_file = sys.argv[2] if len(sys.argv) > 2 else "pole_span_ml_model.pkl"
        score = test_single_file(file_path, model_file)
        if score is not None:
            print(f"\n最终评分: {score}")
    else:
        # 否则运行完整测试
        test_pole_span_ml_scoring()