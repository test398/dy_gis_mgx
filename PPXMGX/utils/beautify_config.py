#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
连线美化配置文件
包含各种美化参数、规则和阈值
"""

class BeautifyConfig:
    """连线美化配置类"""
    
    # 基础参数
    MIN_DISTANCE = 0.00001          # 最小设备间距
    MAX_CURVE_POINTS = 10           # 最大曲线点数
    BUILDING_RADIUS = 0.00002       # 建筑物半径
    AVOIDANCE_DISTANCE = 0.0001     # 避障距离
    
    # 路径类型阈值
    BEZIER_THRESHOLD = 0.0001       # 贝塞尔曲线适用距离阈值
    ORTHOGONAL_THRESHOLD = 0.0005   # 正交路径适用距离阈值
    
    # 美化规则
    BEAUTIFY_RULES = {
        'power_line': {
            'preferred_style': 'orthogonal',  # 电力线优先正交
            'max_angle': 90,                  # 最大转角
            'min_segment_length': 0.00002,    # 最小段长度
        },
        'communication_line': {
            'preferred_style': 'bezier',      # 通信线优先曲线
            'max_angle': 45,                  # 最大转角
            'min_segment_length': 0.00001,    # 最小段长度
        },
        'distribution_line': {
            'preferred_style': 'mixed',       # 配电线路混合
            'max_angle': 60,                  # 最大转角
            'min_segment_length': 0.000015,   # 最小段长度
        }
    }
    
    # 颜色和样式配置
    LINE_STYLES = {
        'power_line': {
            'color': '#FF0000',
            'width': 3,
            'style': 'solid'
        },
        'communication_line': {
            'color': '#00FF00',
            'width': 2,
            'style': 'dashed'
        },
        'distribution_line': {
            'color': '#0000FF',
            'width': 2.5,
            'style': 'solid'
        }
    }
    
    # 建筑物类型权重
    BUILDING_WEIGHTS = {
        'residential': 1.0,      # 住宅建筑
        'commercial': 1.2,       # 商业建筑
        'industrial': 0.8,       # 工业建筑
        'public': 1.1,           # 公共建筑
        'unknown': 1.0           # 未知类型
    }
    
    # 路径优化参数
    PATH_OPTIMIZATION = {
        'smoothing_window': 3,           # 平滑窗口大小
        'simplify_threshold': 3,         # 简化阈值
        'max_iterations': 100,           # 最大迭代次数
        'convergence_threshold': 0.00001 # 收敛阈值
    }
    
    # 美学评分权重
    AESTHETIC_WEIGHTS = {
        'smoothness': 0.3,       # 平滑度权重
        'symmetry': 0.2,         # 对称性权重
        'parallelism': 0.2,      # 平行度权重
        'spacing': 0.15,         # 间距权重
        'avoidance': 0.15        # 避障权重
    }
    
    @classmethod
    def get_line_style(cls, line_type: str) -> dict:
        """获取线路样式配置"""
        return cls.LINE_STYLES.get(line_type, cls.LINE_STYLES['distribution_line'])
    
    @classmethod
    def get_beautify_rule(cls, line_type: str) -> dict:
        """获取美化规则"""
        return cls.BEAUTIFY_RULES.get(line_type, cls.BEAUTIFY_RULES['distribution_line'])
    
    @classmethod
    def get_building_weight(cls, building_type: str) -> float:
        """获取建筑物权重"""
        return cls.BUILDING_WEIGHTS.get(building_type, cls.BUILDING_WEIGHTS['unknown'])
    
    @classmethod
    def should_use_bezier(cls, distance: float) -> bool:
        """判断是否应该使用贝塞尔曲线"""
        return distance < cls.BEZIER_THRESHOLD
    
    @classmethod
    def should_use_orthogonal(cls, distance: float) -> bool:
        """判断是否应该使用正交路径"""
        return cls.BEZIER_THRESHOLD <= distance < cls.ORTHOGONAL_THRESHOLD
    
    @classmethod
    def should_use_avoidance(cls, distance: float) -> bool:
        """判断是否应该使用避障路径"""
        return distance >= cls.ORTHOGONAL_THRESHOLD

# 电力线路美化规则
POWER_LINE_RULES = {
    'voltage_levels': {
        'high_voltage': {
            'min_height': 10,        # 最小高度(米)
            'clearance': 0.00005,    # 安全距离
            'style': 'orthogonal'
        },
        'medium_voltage': {
            'min_height': 6,
            'clearance': 0.00003,
            'style': 'mixed'
        },
        'low_voltage': {
            'min_height': 3,
            'clearance': 0.00002,
            'style': 'bezier'
        }
    },
    
    'crossing_rules': {
        'power_power': 90,      # 电力线交叉角度
        'power_road': 60,       # 电力线与道路交叉角度
        'power_building': 45,   # 电力线与建筑物交叉角度
    }
}

# 地理约束规则
GEOGRAPHIC_CONSTRAINTS = {
    'terrain_types': {
        'flat': {
            'preferred_style': 'orthogonal',
            'max_slope': 5
        },
        'hilly': {
            'preferred_style': 'bezier',
            'max_slope': 15
        },
        'mountainous': {
            'preferred_style': 'avoidance',
            'max_slope': 30
        }
    },
    
    'land_use': {
        'urban': {
            'avoidance_priority': 'high',
            'preferred_style': 'orthogonal'
        },
        'suburban': {
            'avoidance_priority': 'medium',
            'preferred_style': 'mixed'
        },
        'rural': {
            'avoidance_priority': 'low',
            'preferred_style': 'bezier'
        }
    }
}

# 性能优化配置
PERFORMANCE_CONFIG = {
    'parallel_processing': True,    # 启用并行处理
    'cache_size': 1000,            # 缓存大小
    'batch_size': 50,              # 批处理大小
    'timeout': 30,                 # 超时时间(秒)
    'max_retries': 3               # 最大重试次数
}

# 质量评估标准
QUALITY_METRICS = {
    'smoothness_score': {
        'weight': 0.3,
        'threshold': 0.8
    },
    'symmetry_score': {
        'weight': 0.2,
        'threshold': 0.7
    },
    'parallelism_score': {
        'weight': 0.2,
        'threshold': 0.6
    },
    'spacing_score': {
        'weight': 0.15,
        'threshold': 0.8
    },
    'avoidance_score': {
        'weight': 0.15,
        'threshold': 0.9
    }
}

def get_optimal_path_type(distance: float, line_type: str = 'distribution_line', 
                         terrain_type: str = 'flat') -> str:
    """根据距离、线路类型和地形类型确定最优路径类型"""
    
    # 基础判断
    if BeautifyConfig.should_use_bezier(distance):
        base_style = 'bezier'
    elif BeautifyConfig.should_use_orthogonal(distance):
        base_style = 'orthogonal'
    else:
        base_style = 'avoidance'
    
    # 根据线路类型调整
    rule = BeautifyConfig.get_beautify_rule(line_type)
    if rule['preferred_style'] != 'mixed':
        base_style = rule['preferred_style']
    
    # 根据地形类型调整
    terrain_rule = GEOGRAPHIC_CONSTRAINTS['terrain_types'].get(terrain_type, {})
    if terrain_rule.get('preferred_style'):
        base_style = terrain_rule['preferred_style']
    
    return base_style

def calculate_aesthetic_score(path: list, obstacles: list = None) -> float:
    """计算路径的美学评分"""
    if not path or len(path) < 2:
        return 0.0
    
    scores = {}
    
    # 平滑度评分
    scores['smoothness'] = calculate_smoothness_score(path)
    
    # 对称性评分
    scores['symmetry'] = calculate_symmetry_score(path)
    
    # 平行度评分
    scores['parallelism'] = calculate_parallelism_score(path)
    
    # 间距评分
    scores['spacing'] = calculate_spacing_score(path)
    
    # 避障评分
    scores['avoidance'] = calculate_avoidance_score(path, obstacles) if obstacles else 1.0
    
    # 加权平均
    total_score = 0.0
    total_weight = 0.0
    
    for metric, weight in BeautifyConfig.AESTHETIC_WEIGHTS.items():
        if metric in scores:
            total_score += scores[metric] * weight
            total_weight += weight
    
    return total_score / total_weight if total_weight > 0 else 0.0

def calculate_smoothness_score(path: list) -> float:
    """计算路径平滑度评分"""
    if len(path) < 3:
        return 1.0
    
    angles = []
    for i in range(1, len(path) - 1):
        # 计算三个连续点形成的角度
        p1, p2, p3 = path[i-1], path[i], path[i+1]
        angle = abs(calculate_angle(p1, p2, p3))
        angles.append(angle)
    
    if not angles:
        return 1.0
    
    # 角度越接近180度，越平滑
    avg_angle = sum(angles) / len(angles)
    smoothness = 1.0 - (avg_angle - 180) / 180
    return max(0.0, min(1.0, smoothness))

def calculate_symmetry_score(path: list) -> float:
    """计算路径对称性评分"""
    if len(path) < 3:
        return 1.0
    
    # 简化的对称性计算
    mid_point = len(path) // 2
    left_half = path[:mid_point]
    right_half = path[mid_point:][::-1]  # 反转右半部分
    
    if len(left_half) != len(right_half):
        return 0.5
    
    # 计算对应点的距离差异
    total_diff = 0.0
    for i in range(len(left_half)):
        diff = haversine_distance(left_half[i], right_half[i])
        total_diff += diff
    
    avg_diff = total_diff / len(left_half)
    symmetry = 1.0 - min(1.0, avg_diff / 0.0001)  # 归一化
    return max(0.0, min(1.0, symmetry))

def calculate_parallelism_score(path: list) -> float:
    """计算路径平行度评分"""
    if len(path) < 4:
        return 1.0
    
    # 计算相邻线段的平行度
    angles = []
    for i in range(len(path) - 2):
        seg1 = [path[i], path[i+1]]
        seg2 = [path[i+1], path[i+2]]
        angle = abs(calculate_segment_angle(seg1, seg2))
        angles.append(angle)
    
    if not angles:
        return 1.0
    
    # 角度越接近0度或180度，越平行
    avg_angle = sum(angles) / len(angles)
    parallelism = 1.0 - min(avg_angle, 180 - avg_angle) / 90
    return max(0.0, min(1.0, parallelism))

def calculate_spacing_score(path: list) -> float:
    """计算路径间距评分"""
    if len(path) < 2:
        return 1.0
    
    # 检查点之间的间距是否均匀
    distances = []
    for i in range(len(path) - 1):
        dist = haversine_distance(path[i], path[i+1])
        distances.append(dist)
    
    if not distances:
        return 1.0
    
    avg_distance = sum(distances) / len(distances)
    variance = sum((d - avg_distance) ** 2 for d in distances) / len(distances)
    
    # 方差越小，间距越均匀
    spacing = 1.0 - min(1.0, variance / (avg_distance ** 2))
    return max(0.0, min(1.0, spacing))

def calculate_avoidance_score(path: list, obstacles: list) -> float:
    """计算避障评分"""
    if not obstacles or len(path) < 2:
        return 1.0
    
    min_distance = float('inf')
    for i in range(len(path) - 1):
        for obstacle in obstacles:
            # 简化的距离计算
            obs_center = [sum(p[0] for p in obstacle) / len(obstacle),
                         sum(p[1] for p in obstacle) / len(obstacle)]
            dist = haversine_distance(path[i], obs_center)
            min_distance = min(min_distance, dist)
    
    # 距离越远，避障效果越好
    avoidance = min(1.0, min_distance / BeautifyConfig.AVOIDANCE_DISTANCE)
    return max(0.0, min(1.0, avoidance))

def calculate_angle(p1: list, p2: list, p3: list) -> float:
    """计算三个点形成的角度"""
    import math
    
    # 计算两个向量
    v1 = [p1[0] - p2[0], p1[1] - p2[1]]
    v2 = [p3[0] - p2[0], p3[1] - p2[1]]
    
    # 计算夹角
    dot_product = v1[0] * v2[0] + v1[1] * v2[1]
    mag1 = math.sqrt(v1[0]**2 + v1[1]**2)
    mag2 = math.sqrt(v2[0]**2 + v2[1]**2)
    
    if mag1 == 0 or mag2 == 0:
        return 0.0
    
    cos_angle = dot_product / (mag1 * mag2)
    cos_angle = max(-1.0, min(1.0, cos_angle))  # 限制在[-1, 1]范围内
    
    return math.degrees(math.acos(cos_angle))

def calculate_segment_angle(seg1: list, seg2: list) -> float:
    """计算两个线段的夹角"""
    # 计算线段方向向量
    dir1 = [seg1[1][0] - seg1[0][0], seg1[1][1] - seg1[0][1]]
    dir2 = [seg2[1][0] - seg2[0][0], seg2[1][1] - seg2[0][1]]
    
    # 计算夹角
    dot_product = dir1[0] * dir2[0] + dir1[1] * dir2[1]
    mag1 = math.sqrt(dir1[0]**2 + dir1[1]**2)
    mag2 = math.sqrt(dir2[0]**2 + dir2[1]**2)
    
    if mag1 == 0 or mag2 == 0:
        return 0.0
    
    cos_angle = dot_product / (mag1 * mag2)
    cos_angle = max(-1.0, min(1.0, cos_angle))
    
    return math.degrees(math.acos(cos_angle))

def haversine_distance(point1: list, point2: list) -> float:
    """计算两个经纬度点间的球面距离（米）"""
    import math
    
    lat1, lon1 = point1
    lat2, lon2 = point2
    R = 6371000  # 地球平均半径，单位米
    
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c 