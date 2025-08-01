from collections import defaultdict
import math
import json
import os
import numpy as np
from typing import List, Tuple, Dict, Optional
import requests

from utils.config import Config
from utils.devlop import simplify_path, haversine_distance, get_intersection

LNG, LAT = 0, 0

class LineBeautifier:
    """连线美化器"""
    
    def __init__(self, building_coords: Dict, map_token: str):
        self.building_coords = building_coords
        self.map_token = map_token
        self.min_distance = 0.00001  # 最小设备间距
        self.max_curve_points = 10   # 最大曲线点数
        
    def generate_bezier_curve(self, start: List[float], end: List[float], 
                             control_points: List[List[float]] = None) -> List[List[float]]:
        """生成贝塞尔曲线路径"""
        if control_points is None:
            # 自动生成控制点
            mid_x = (start[0] + end[0]) / 2
            mid_y = (start[1] + end[1]) / 2
            # 添加一些偏移使曲线更自然
            offset = 0.00002
            control_points = [[mid_x + offset, mid_y + offset]]
        
        points = []
        for t in np.linspace(0, 1, self.max_curve_points):
            if len(control_points) == 1:
                # 二次贝塞尔曲线
                x = (1-t)**2 * start[0] + 2*(1-t)*t * control_points[0][0] + t**2 * end[0]
                y = (1-t)**2 * start[1] + 2*(1-t)*t * control_points[0][1] + t**2 * end[1]
            else:
                # 三次贝塞尔曲线
                x = (1-t)**3 * start[0] + 3*(1-t)**2*t * control_points[0][0] + \
                    3*(1-t)*t**2 * control_points[1][0] + t**3 * end[0]
                y = (1-t)**3 * start[1] + 3*(1-t)**2*t * control_points[0][1] + \
                    3*(1-t)*t**2 * control_points[1][1] + t**3 * end[1]
            points.append([x, y])
        
        return points
    
    def generate_orthogonal_path(self, start: List[float], end: List[float]) -> List[List[float]]:
        """生成正交路径（直角转弯）"""
        mid_x = (start[0] + end[0]) / 2
        mid_y = (start[1] + end[1]) / 2
        
        # 判断是水平优先还是垂直优先
        dx = abs(end[0] - start[0])
        dy = abs(end[1] - start[1])
        
        if dx > dy:
            # 水平优先
            return [start, [mid_x, start[1]], [mid_x, end[1]], end]
        else:
            # 垂直优先
            return [start, [start[0], mid_y], [end[0], mid_y], end]
    
    def generate_avoidance_path(self, start: List[float], end: List[float], 
                               obstacles: List[List[float]]) -> List[List[float]]:
        """生成避障路径"""
        # 简单的避障算法：找到障碍物的边界，绕行
        path = [start]
        
        for obstacle in obstacles:
            # 计算障碍物中心
            obs_center = [sum(p[0] for p in obstacle) / len(obstacle),
                         sum(p[1] for p in obstacle) / len(obstacle)]
            
            # 计算到障碍物的距离
            dist_to_obs = haversine_distance(start, obs_center)
            
            if dist_to_obs < 0.0001:  # 如果太近，需要绕行
                # 计算绕行点
                dx = end[0] - start[0]
                dy = end[1] - start[1]
                length = math.sqrt(dx*dx + dy*dy)
                
                if length > 0:
                    # 垂直方向偏移
                    offset = 0.00003
                    if abs(dx) > abs(dy):
                        # 水平线，垂直偏移
                        bypass_point = [obs_center[0], obs_center[1] + offset]
                    else:
                        # 垂直线，水平偏移
                        bypass_point = [obs_center[0] + offset, obs_center[1]]
                    
                    path.append(bypass_point)
        
        path.append(end)
        return path
    
    def optimize_path_smoothness(self, path: List[List[float]]) -> List[List[float]]:
        """优化路径平滑度"""
        if len(path) < 3:
            return path
        
        # 使用移动平均平滑路径
        smoothed = []
        window_size = 3
        
        for i in range(len(path)):
            start_idx = max(0, i - window_size // 2)
            end_idx = min(len(path), i + window_size // 2 + 1)
            
            window = path[start_idx:end_idx]
            avg_x = sum(p[0] for p in window) / len(window)
            avg_y = sum(p[1] for p in window) / len(window)
            
            smoothed.append([avg_x, avg_y])
        
        return smoothed
    
    def check_building_intersection(self, path: List[List[float]]) -> bool:
        """检查路径是否与建筑物相交"""
        for i in range(len(path) - 1):
            for building_key, building_info in self.building_coords.items():
                if isinstance(building_info, list) and len(building_info) >= 3:
                    building_center = building_info[0]  # 建筑物中心坐标
                    building_radius = 0.00002  # 建筑物半径
                    
                    # 检查线段是否与建筑物圆相交
                    if self.line_circle_intersection(path[i], path[i+1], building_center, building_radius):
                        return True
        return False
    
    def line_circle_intersection(self, line_start: List[float], line_end: List[float], 
                                circle_center: List[float], circle_radius: float) -> bool:
        """检查线段是否与圆相交"""
        # 计算线段到圆心的最短距离
        dx = line_end[0] - line_start[0]
        dy = line_end[1] - line_start[1]
        
        if dx == 0 and dy == 0:
            # 线段长度为0
            dist = math.sqrt((line_start[0] - circle_center[0])**2 + 
                           (line_start[1] - circle_center[1])**2)
            return dist <= circle_radius
        
        # 参数化线段
        t = max(0, min(1, ((circle_center[0] - line_start[0]) * dx + 
                          (circle_center[1] - line_start[1]) * dy) / (dx*dx + dy*dy)))
        
        closest_point = [line_start[0] + t * dx, line_start[1] + t * dy]
        dist = math.sqrt((closest_point[0] - circle_center[0])**2 + 
                        (closest_point[1] - circle_center[1])**2)
        
        return dist <= circle_radius
    
    def generate_optimal_path(self, start: List[float], end: List[float], 
                            path_type: str = 'bezier') -> List[List[float]]:
        """生成最优路径"""
        # 获取建筑物坐标作为障碍物
        obstacles = []
        for building_info in self.building_coords.values():
            if isinstance(building_info, list) and len(building_info) >= 3:
                # 简化为矩形边界
                center = building_info[0]
                radius = 0.00002
                obstacles.append([
                    [center[0] - radius, center[1] - radius],
                    [center[0] + radius, center[1] - radius],
                    [center[0] + radius, center[1] + radius],
                    [center[0] - radius, center[1] + radius]
                ])
        
        # 根据路径类型生成初始路径
        if path_type == 'bezier':
            path = self.generate_bezier_curve(start, end)
        elif path_type == 'orthogonal':
            path = self.generate_orthogonal_path(start, end)
        elif path_type == 'avoidance':
            path = self.generate_avoidance_path(start, end, obstacles)
        else:
            # 默认直线
            path = [start, end]
        
        # 检查是否与建筑物相交
        if self.check_building_intersection(path):
            # 如果相交，使用避障路径
            path = self.generate_avoidance_path(start, end, obstacles)
        
        # 优化路径平滑度
        path = self.optimize_path_smoothness(path)
        
        # 简化路径，去除冗余点
        path = simplify_path(path, distance_ratio_threshold=3)
        
        return path

def output1_optimized(list_data, psrId, center, mapToken, building_coords=None):
    """优化后的主处理函数"""
    global LNG, LAT
    
    # 检查是否为柱上变压器
    for x in list_data:
        if x['properties'].get('psrType') in ["dywlgt", '0110']:
            break
    else:
        return False  # 不是柱上变压器，不用此方法处理
    
    # 初始化连线美化器
    if building_coords is None:
        building_coords = {}
    beautifier = LineBeautifier(building_coords, mapToken)
    
    # 构建连接关系
    Jdict, connDict, JconDict = defaultdict(dict), defaultdict(list), defaultdict(str)
    for info in list_data:
        if info['properties'].get('connection', ''):
            connDict[info['properties']['connection']] = [info['properties']['id'], info]
        if info['geometry']['type'] == 'Point' and info.get('properties', {}).get('psrType', '') == '3218000':
            Jdict[info['properties']['id']] = {
                'info': info, 
                'connection': info['properties']['connection'], 
                'coordinates': info['geometry']['coordinates'], 
                'child': [], 
                'parent': {}
            }
            JconDict[info['properties']['connection']] = info['properties']['id']

    # 处理连接关系
    for info in list_data:
        connections = info['properties'].get('connection', '').split(',')
        if len(connections) != 2:
            continue
        for idx, connection in enumerate(connections):
            key = JconDict.get(connection, '')
            if key:
                if Jdict[key]['info']['geometry']['coordinates'] == info['geometry']['coordinates'][0]:
                    lineidx = 0
                elif Jdict[key]['info']['geometry']['coordinates'] == info['geometry']['coordinates'][-1]:
                    lineidx = -1
                elif str(info['properties'].get('connection', '')).startswith(connection):
                    lineidx = 0
                elif str(info['properties'].get('connection', '')).endswith(connection):
                    lineidx = -1
                else:
                    continue
                
                conn_info = connDict.get(connections[idx - 1], [])
                if len(conn_info) < 2 or conn_info[1] is None:
                    continue
                    
                if conn_info[1]['properties'].get('psrType') == '3112':
                    tempDict = {
                        'lineId': info['properties']['id'], 
                        'lineinfo': info, 
                        'lineidx': lineidx, 
                        'info': conn_info[1]
                    }
                    Jdict[key]['child'].append(tempDict)
                else:
                    tempDict = {
                        'lineId': info['properties']['id'], 
                        'lineinfo': info, 
                        'lineidx': lineidx, 
                        'info': conn_info[1]
                    }
                    Jdict[key]['parent'] = tempDict
    
    # 处理设备位置调整
    gtDict = defaultdict(str)
    for _, item in Jdict.items():
        parent = item['parent']
        for child in item['child']:
            if 'info' in parent:
                gtDict[child['info']['properties']['id']] = parent['info']['geometry']['coordinates']
    
    detDict = defaultdict(float)
    for key, val in gtDict.items():
        for Jpsr, item in Jdict.items():
            for child in item['child']:
                if key == child['info']['properties']['id']:
                    if not detDict.get(Jpsr):
                        det = -0.00000899879 * 2
                        detDict[Jpsr] = det
                    det = detDict[Jpsr]
                    
                    if isinstance(val, (list, tuple)) and len(val) >= 2:
                        val_lng, val_lat = float(val[0]), float(val[1])
                    else:
                        continue
                        
                    Jcoor = [val_lng, val_lat + det]
                    item['info']['geometry']['coordinates'] = Jcoor
                    child['info']['geometry']['coordinates'] = [val_lng, val_lat + det * 2]
                    
                    # 使用优化的连线生成
                    start_coord = Jcoor
                    end_coord = [val_lng, val_lat + det * 2]
                    
                    # 根据距离选择合适的路径类型
                    distance = haversine_distance(start_coord, end_coord)
                    if distance < 0.0001:
                        path_type = 'bezier'
                    elif distance < 0.0005:
                        path_type = 'orthogonal'
                    else:
                        path_type = 'avoidance'
                    
                    optimal_path = beautifier.generate_optimal_path(start_coord, end_coord, path_type)
                    
                    # 更新连线坐标
                    if child['lineidx'] == -1:
                        child['lineinfo']['geometry']['coordinates'] = optimal_path
                    else:
                        child['lineinfo']['geometry']['coordinates'] = optimal_path
                    
                    # 更新父连线
                    lineCoor = item['parent']['lineinfo']['geometry']['coordinates']
                    if item['parent']['lineidx'] == 0:
                        parent_path = beautifier.generate_optimal_path(optimal_path[0], lineCoor[-1], 'bezier')
                        item['parent']['lineinfo']['geometry']['coordinates'] = parent_path
                    else:
                        parent_path = beautifier.generate_optimal_path(lineCoor[0], optimal_path[-1], 'bezier')
                        item['parent']['lineinfo']['geometry']['coordinates'] = parent_path
                    
                    break
            else:
                continue
            break
    
    # 处理其他类型的连线
    for info in list_data:
        if info['geometry']['type'] == 'LineString' and info.get('properties', {}).get('psrType', '') == '3201':
            coords = info['geometry']['coordinates']
            if len(coords) >= 2:
                # 使用贝塞尔曲线美化
                start = coords[0]
                end = coords[-1]
                beautified_path = beautifier.generate_optimal_path(start, end, 'bezier')
                info['geometry']['coordinates'] = beautified_path
    
    # 保存结果
    output_path = os.path.join(Config.Geo1, f'{psrId}_optimized.json')
    open(output_path, 'w', encoding="U8").write(json.dumps({'features': list_data}, indent=4, ensure_ascii=False))
    return output_path

# 保持原有函数兼容性
def output1(list_data, psrId, center, mapToken):
    """保持原有接口兼容性"""
    return output1_optimized(list_data, psrId, center, mapToken)

def v2Function(mapToken, coor):
    url = f"{Config.MAPURL}/geoconv/v2"
    head = {'Authorization': mapToken} 
    data = {'coords': coor, 'from': 1}
    res = requests.post(url, data=data, headers=head, timeout=10).json()
    print({'Authorization': mapToken}, data, res )
    return list(res['value'][0].values())

def walking(start, end, erCi=False, mapToken=None):
    print(start, end, mapToken)
    url = f"{Config.MAPURL}/rest/v1/direction/walking?origin={start}&destination={end}"
    head = {'Authorization': mapToken}
    res = requests.get(url, headers=head).json()
    steps = res['route']['paths'][0]['steps']
    if len(steps) <= 1 and not erCi:
        return False
    startPoint = steps[0]['polyline'].split(';')[-1]
    oneStep = [[float(y) for y in x.split(',')] for x in steps[0]['polyline'].split(';')]
    fullStep = [[float(y) for y in x.split(',')] for x in ';'.join([z['polyline'] for z in steps]).split(';')]
    return [startPoint, oneStep, fullStep]

def calc_dis(distance):
    flag = 1 if distance > 0 else -1
    return abs(distance) % 360 * flag * math.pi / 180

def calcNewCoor(coorDict, bxCoor, psrId):
    length, idx = float('inf'), -1
    for key, coor in coorDict.items():
        if coor[0] is True:
            continue
        o = calc_dis(bxCoor[0] - coor[1])
        s = calc_dis(bxCoor[1] - coor[0])
        a = calc_dis(bxCoor[1])
        l = calc_dis(coor[0])
        u = math.pow(math.sin(o / 2), 2) + math.pow(math.sin(s / 2), 2) * math.cos(a) * math.cos(l)
        calcLen = round(math.atan2(math.sqrt(u), math.sqrt(1 - u)) * 2 * 6371000, 2)
        if calcLen < length and calcLen < 100:
            idx, length = key, calcLen
    print(psrId, idx, length)
    if idx != -1:
        coorDict[idx] = [True, coorDict[idx]]
        return coorDict[idx][1][::-1]

if __name__ == "__main__":
    # 测试优化后的算法
    test_data = []
    test_building_coords = {
        'building1': [[118.946388, 34.565009], 180, 100],
        'building2': [[118.946500, 34.565100], 90, 80]
    }
    output1_optimized(test_data, 'test', [118.946388, 34.565009], 'test_token', test_building_coords) 