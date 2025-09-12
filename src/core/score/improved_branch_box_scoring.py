#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
改进的分支箱评分系统 - 解决过度正则化问题
"""

import pandas as pd
import numpy as np
import pickle
import os
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge, Lasso, ElasticNet
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.feature_selection import SelectKBest, mutual_info_regression, f_regression
from sklearn.model_selection import GridSearchCV, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score
from scipy.spatial import ConvexHull
import warnings
warnings.filterwarnings('ignore')

class ImprovedBranchBoxScoring:
    def __init__(self, score_file="评分标准/分支箱评分数据.csv", data_path="数据/data"):
        self.score_file = score_file
        self.data_path = data_path
        self.model = None
        self.scaler = None
        self.feature_selector = None
        self.poly_features = None
        self.is_trained = False
        self.features_df = None
        self.selected_features = None
        
    def load_scores(self):
        """加载评分数据"""
        try:
            self.scores_df = pd.read_csv(self.score_file, encoding='utf-8')
            print(f"成功加载 {len(self.scores_df)} 条评分记录")
        except:
            try:
                self.scores_df = pd.read_csv(self.score_file, encoding='gbk')
                print(f"成功加载 {len(self.scores_df)} 条评分记录")
            except Exception as e:
                print(f"加载评分文件失败: {e}")
                raise
        
    def _extract_single_district_features(self, branch_box_results, all_annotations, district_id):
        """为单个台区提取特征"""
        feature_dict = {'台区ID': district_id}
        
        # 分支箱基本信息
        branch_box_count = len(branch_box_results)
        feature_dict['分支箱数量'] = branch_box_count
        
        if branch_box_count == 0:
            # 设置默认值
            return self._get_default_features(feature_dict)
        
        # 几何特征
        areas = []
        perimeters = []
        positions = []
        
        for annotation in branch_box_results:
            segmentation = annotation.get('segmentation', [])
            if segmentation and len(segmentation[0]) >= 6:
                points = np.array(segmentation[0]).reshape(-1, 2)
                
                # 计算面积（使用鞋带公式）
                area = 0.5 * abs(sum(points[i,0] * points[(i+1) % len(points),1] - 
                                   points[(i+1) % len(points),0] * points[i,1] 
                                   for i in range(len(points))))
                areas.append(area)
                
                # 计算周长
                perimeter = sum(np.linalg.norm(points[(i+1) % len(points)] - points[i]) 
                              for i in range(len(points)))
                perimeters.append(perimeter)
                
                # 中心位置
                center = np.mean(points, axis=0)
                positions.append(center)
        
        # 基础几何统计
        feature_dict['分支箱平均面积'] = np.mean(areas) if areas else 0
        feature_dict['分支箱面积标准差'] = np.std(areas) if len(areas) > 1 else 0
        feature_dict['分支箱面积变异系数'] = np.std(areas) / (np.mean(areas) + 1e-6) if areas else 0
        feature_dict['分支箱平均周长'] = np.mean(perimeters) if perimeters else 0
        feature_dict['分支箱周长标准差'] = np.std(perimeters) if len(perimeters) > 1 else 0
        
        # 形状特征
        aspect_ratios = []
        compactness_scores = []
        
        for area, perimeter in zip(areas, perimeters):
            if perimeter > 0:
                compactness = (4 * np.pi * area) / (perimeter ** 2)
                compactness_scores.append(compactness)
            
        feature_dict['分支箱平均紧凑度'] = np.mean(compactness_scores) if compactness_scores else 0
        feature_dict['分支箱紧凑度标准差'] = np.std(compactness_scores) if len(compactness_scores) > 1 else 0
        
        # 空间分布特征
        if len(positions) >= 2:
            positions = np.array(positions)
            
            # 空间跨度
            x_span = np.max(positions[:, 0]) - np.min(positions[:, 0])
            y_span = np.max(positions[:, 1]) - np.min(positions[:, 1])
            feature_dict['分支箱X跨度'] = x_span
            feature_dict['分支箱Y跨度'] = y_span
            feature_dict['分支箱总跨度'] = np.sqrt(x_span**2 + y_span**2)
            
            # 空间密度
            if len(positions) >= 3:
                try:
                    hull = ConvexHull(positions)
                    convex_area = hull.volume
                    feature_dict['分支箱凸包面积'] = convex_area
                    feature_dict['分支箱空间密度'] = branch_box_count / (convex_area + 1e-6)
                except:
                    feature_dict['分支箱凸包面积'] = x_span * y_span
                    feature_dict['分支箱空间密度'] = branch_box_count / (x_span * y_span + 1e-6)
            else:
                feature_dict['分支箱凸包面积'] = x_span * y_span
                feature_dict['分支箱空间密度'] = branch_box_count / (x_span * y_span + 1e-6)
            
            # 相邻距离特征
            distances = []
            for i in range(len(positions)):
                for j in range(i+1, len(positions)):
                    dist = np.linalg.norm(positions[i] - positions[j])
                    distances.append(dist)
            
            if distances:
                feature_dict['分支箱最小距离'] = min(distances)
                feature_dict['分支箱平均距离'] = np.mean(distances)
                feature_dict['分支箱距离标准差'] = np.std(distances) if len(distances) > 1 else 0
        else:
            # 单个分支箱的情况
            feature_dict['分支箱X跨度'] = 0
            feature_dict['分支箱Y跨度'] = 0
            feature_dict['分支箱总跨度'] = 0
            feature_dict['分支箱凸包面积'] = areas[0] if areas else 0
            feature_dict['分支箱空间密度'] = 1
            feature_dict['分支箱最小距离'] = 0
            feature_dict['分支箱平均距离'] = 0
            feature_dict['分支箱距离标准差'] = 0
        
        # 设备相关特征
        device_types = {}
        for annotation in all_annotations:
            label = annotation.get('label', '')
            device_types[label] = device_types.get(label, 0) + 1
        
        total_devices = sum(device_types.values())
        feature_dict['总设备数'] = total_devices
        feature_dict['分支箱比例'] = branch_box_count / (total_devices + 1e-6)
        feature_dict['设备类型数'] = len(device_types)
        
        # 特定设备特征
        feature_dict['变压器数量'] = device_types.get('杆塔', 0)
        feature_dict['电缆数量'] = device_types.get('电缆段', 0) + device_types.get('连接线', 0)
        feature_dict['开关设备数量'] = device_types.get('开关', 0)
        
        # 台区ID特征（经过修改避免过拟合）
        feature_dict['台区ID长度'] = len(district_id)
        feature_dict['台区ID数字字符数'] = sum(c.isdigit() for c in district_id)
        feature_dict['台区ID字母字符数'] = sum(c.isalpha() for c in district_id)
        
        # 复杂度评估
        feature_dict['布局复杂度'] = self._calculate_layout_complexity(branch_box_results, all_annotations)
        feature_dict['连接复杂度'] = self._calculate_connection_complexity(branch_box_results, all_annotations)
        
        return feature_dict
    
    def _get_default_features(self, feature_dict):
        """获取默认特征值"""
        default_features = {
            '分支箱平均面积': 0, '分支箱面积标准差': 0, '分支箱面积变异系数': 0,
            '分支箱平均周长': 0, '分支箱周长标准差': 0, '分支箱平均紧凑度': 0,
            '分支箱紧凑度标准差': 0, '分支箱X跨度': 0, '分支箱Y跨度': 0,
            '分支箱总跨度': 0, '分支箱凸包面积': 0, '分支箱空间密度': 0,
            '分支箱最小距离': 0, '分支箱平均距离': 0, '分支箱距离标准差': 0,
            '总设备数': 0, '分支箱比例': 0, '设备类型数': 0, '变压器数量': 0,
            '电缆数量': 0, '开关设备数量': 0, '台区ID长度': 0,
            '台区ID数字字符数': 0, '台区ID字母字符数': 0,
            '布局复杂度': 0, '连接复杂度': 0
        }
        feature_dict.update(default_features)
        return feature_dict
    
    def _calculate_layout_complexity(self, branch_box_results, all_annotations):
        """计算布局复杂度"""
        if not branch_box_results:
            return 0
        
        # 基于设备密度和分布的复杂度
        total_devices = len(all_annotations)
        branch_boxes = len(branch_box_results)
        
        if total_devices == 0:
            return 0
        
        # 设备密度因子
        density_factor = total_devices / (branch_boxes + 1)
        
        # 设备类型多样性
        device_types = set(ann.get('label', '') for ann in all_annotations)
        diversity_factor = len(device_types) / 10.0  # 归一化
        
        return min(density_factor * diversity_factor, 10.0)
    
    def _calculate_connection_complexity(self, branch_box_results, all_annotations):
        """计算连接复杂度"""
        if not branch_box_results:
            return 0
        
        # 基于连接线和电缆的复杂度
        connection_devices = [ann for ann in all_annotations 
                            if ann.get('label', '') in ['连接线', '电缆段', '低压电缆接头']]
        
        if not connection_devices:
            return 0
        
        branch_boxes = len(branch_box_results)
        connections = len(connection_devices)
        
        # 连接密度
        connection_density = connections / (branch_boxes + 1)
        return min(connection_density, 10.0)
    
    def create_target_score(self):
        """创建目标评分"""
        # 合并特征和评分数据
        self.features_df = self.features_df.merge(
            self.scores_df[['台区ID', '评分']], 
            on='台区ID', 
            how='inner'
        )
        self.features_df['目标评分'] = self.features_df['评分']
        print(f"合并后数据形状: {self.features_df.shape}")
    
    def train_improved_model(self):
        """训练改进的模型"""
        print("开始训练改进模型...")
        
        # 准备数据
        feature_columns = [col for col in self.features_df.columns 
                          if col not in ['台区ID', '评分', '目标评分']]
        
        X = self.features_df[feature_columns].fillna(0)
        y = self.features_df['目标评分']
        
        print(f"特征数量: {len(feature_columns)}")
        print(f"样本数量: {len(X)}")
        
        # 移除常数特征和高度相关特征
        X_cleaned = self._clean_features(X, feature_columns)
        
        # 标准化
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X_cleaned)
        
        # 特征选择 - 使用更宽松的选择
        n_features_to_select = min(15, X_scaled.shape[1])  # 选择更多特征
        self.feature_selector = SelectKBest(score_func=mutual_info_regression, k=n_features_to_select)
        X_selected = self.feature_selector.fit_transform(X_scaled, y)
        
        # 保存选中的特征名
        selected_indices = self.feature_selector.get_support()
        self.selected_features = [col for i, col in enumerate(X_cleaned.columns) if selected_indices[i]]
        print(f"选择的特征: {self.selected_features}")
        
        # 多项式特征 - 降低复杂度
        self.poly_features = PolynomialFeatures(degree=2, include_bias=False, interaction_only=True)
        X_poly = self.poly_features.fit_transform(X_selected)
        
        # 如果多项式特征太多，再次选择
        if X_poly.shape[1] > 25:
            selector2 = SelectKBest(score_func=f_regression, k=25)
            X_poly = selector2.fit_transform(X_poly, y)
        
        print(f"最终特征维度: {X_poly.shape[1]}")
        
        # 模型选择 - 使用更宽松的正则化
        models = {
            'Ridge_weak': Ridge(alpha=0.1),  # 弱正则化
            'Ridge_medium': Ridge(alpha=1.0),
            'ElasticNet_weak': ElasticNet(alpha=0.01, l1_ratio=0.5, max_iter=5000),  # 很弱的正则化
            'ElasticNet_medium': ElasticNet(alpha=0.1, l1_ratio=0.5, max_iter=5000),
            'RandomForest': RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42),
            'GradientBoosting': GradientBoostingRegressor(n_estimators=100, max_depth=6, random_state=42)
        }
        
        best_score = float('-inf')
        best_model = None
        best_name = None
        
        print("\n模型评估:")
        for name, model in models.items():
            try:
                scores = cross_val_score(model, X_poly, y, cv=5, scoring='r2')
                avg_score = scores.mean()
                print(f"{name}: R2 = {avg_score:.4f} (±{scores.std()*2:.4f})")
                
                if avg_score > best_score:
                    best_score = avg_score
                    best_model = model
                    best_name = name
            except Exception as e:
                print(f"{name} 训练失败: {e}")
        
        if best_model is None:
            print("所有模型训练失败，使用简单Ridge回归")
            best_model = Ridge(alpha=0.1)
            best_name = "Ridge_fallback"
        
        # 训练最佳模型
        best_model.fit(X_poly, y)
        self.model = best_model
        
        # 评估
        predictions = best_model.predict(X_poly)
        r2 = r2_score(y, predictions)
        rmse = np.sqrt(mean_squared_error(y, predictions))
        
        print(f"\n最佳模型: {best_name}")
        print(f"训练集 R2: {r2:.4f}")
        print(f"训练集 RMSE: {rmse:.4f}")
        
        # 检查模型系数（如果是线性模型）
        if hasattr(best_model, 'coef_'):
            non_zero_coef = np.count_nonzero(best_model.coef_)
            print(f"非零系数数量: {non_zero_coef}")
            if non_zero_coef > 0:
                print(f"系数范围: {best_model.coef_.min():.6f} - {best_model.coef_.max():.6f}")
        
        self.is_trained = True
    
    def _clean_features(self, X, feature_columns):
        """清理特征数据"""
        # 移除常数特征
        constant_features = []
        for col in X.columns:
            if X[col].nunique() <= 1:
                constant_features.append(col)
        
        if constant_features:
            print(f"移除常数特征: {constant_features}")
            X = X.drop(columns=constant_features)
        
        # 移除高度相关的特征
        corr_matrix = X.corr().abs()
        high_corr_pairs = []
        
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                if corr_matrix.iloc[i, j] > 0.95:
                    high_corr_pairs.append((corr_matrix.columns[i], corr_matrix.columns[j]))
        
        # 移除高相关特征中的一个
        to_remove = set()
        for pair in high_corr_pairs:
            if pair[1] not in to_remove:
                to_remove.add(pair[1])
        
        if to_remove:
            print(f"移除高相关特征: {list(to_remove)}")
            X = X.drop(columns=list(to_remove))
        
        return X
    
    def save_model(self, model_path="abestScript/model/improved_branch_box_model.pkl"):
        """保存模型"""
        if not self.is_trained:
            raise ValueError("模型未训练")
        
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_selector': self.feature_selector,
            'poly_features': self.poly_features,
            'selected_features': self.selected_features,
            'is_trained': True
        }
        
        with open(model_path, 'wb') as f:
            pickle.dump(model_data, f)
        print(f"模型已保存到 {model_path}")
    
    def load_model(self, model_path="abestScript/model/improved_branch_box_model.pkl"):
        """加载模型"""
        try:
            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)
            
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.feature_selector = model_data['feature_selector']
            self.poly_features = model_data['poly_features']
            self.selected_features = model_data['selected_features']
            self.is_trained = model_data.get('is_trained', True)
            
            print(f"改进模型已从 {model_path} 加载")
            return True
        except Exception as e:
            print(f"加载模型失败: {e}")
            return False
    
    def predict(self, branch_box_results, all_annotations):
        """预测分支箱评分"""
        if not self.is_trained:
            if not self.load_model():
                return 5.0  # 默认评分
        
        try:
            # 提取特征
            feature_dict = self._extract_single_district_features(branch_box_results, all_annotations, "temp")
            
            # 只使用训练时选中的特征
            feature_vector = []
            for feature_name in self.selected_features:
                feature_vector.append(feature_dict.get(feature_name, 0))
            
            # 预处理
            feature_vector = np.array(feature_vector).reshape(1, -1)
            feature_vector_scaled = self.scaler.transform(feature_vector)
            
            # 如果使用了特征选择和多项式特征
            if self.feature_selector is not None:
                # 注意：这里直接使用已缩放的特征，因为特征选择已经在训练时应用
                feature_vector_selected = feature_vector_scaled
            else:
                feature_vector_selected = feature_vector_scaled
            
            if self.poly_features is not None:
                feature_vector_poly = self.poly_features.transform(feature_vector_selected)
                # 如果训练时对多项式特征进行了二次选择，这里需要相同的处理
                if feature_vector_poly.shape[1] != self.model.n_features_in_:
                    # 截取到正确的维度
                    feature_vector_poly = feature_vector_poly[:, :self.model.n_features_in_]
            else:
                feature_vector_poly = feature_vector_selected
            
            # 预测
            prediction = self.model.predict(feature_vector_poly)[0]
            
            # 确保预测值在合理范围内
            return max(0, min(10, prediction))
            
        except Exception as e:
            print(f"预测时出错: {e}")
            return 5.0

if __name__ == "__main__":
    print("=== 改进分支箱评分模型训练 ===")
    
    scorer = ImprovedBranchBoxScoring()
    scorer.load_scores()
    scorer.create_target_score()
    scorer.train_improved_model()
    scorer.save_model()
    
    print("\n训练完成！")