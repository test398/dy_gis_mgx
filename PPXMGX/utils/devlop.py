from math import radians, sin, cos, sqrt, atan2

def haversine_distance(point1, point2):
    """计算两个经纬度点间的球面距离（米）"""
    lat1, lon1 = point1
    lat2, lon2 = point2
    R = 6371000  # 地球平均半径，单位米
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

def get_intersection(a1, a2, b1, b2):
    """计算两线段交点，假设为平面几何（适用于小范围经纬度）"""
    x1, y1 = a1
    x2, y2 = a2
    x3, y3 = b1
    x4, y4 = b2

    denom = (x1 - x2)*(y3 - y4) - (y1 - y2)*(x3 - x4)
    if denom == 0:
        return None  # 平行或重合

    t_numer = (x1 - x3)*(y3 - y4) - (y1 - y3)*(x3 - x4)
    u_numer = (x1 - x3)*(y1 - y2) - (y1 - y3)*(x1 - x2)
    t = t_numer / denom
    u = u_numer / denom

    if 0 <= t <= 1 and 0 <= u <= 1:
        x = x1 + t * (x2 - x1)
        y = y1 + t * (y2 - y1)
        return (x, y)
    else:
        return None

def simplify_path(points, distance_ratio_threshold=5):
    """简化路径，剪裁自相交和绕远部分"""
    if len(points) < 3:
        return points.copy()
    
    # 处理自相交
    simplified = []
    i = 0
    n = len(points)
    while i < n:
        max_j = -1
        intersect_point = None
        # 检查当前线段与后续所有非相邻线段的相交
        for j in range(i + 2, n - 1):
            ip = get_intersection(points[i], points[i+1], points[j], points[j+1])
            if ip:
                if j > max_j:
                    max_j = j
                    intersect_point = ip
        if max_j != -1 and intersect_point:
            simplified.append(points[i])
            simplified.append(intersect_point)
            i = max_j + 1
        else:
            simplified.append(points[i])
            i += 1
    # 确保最后一个点被加入
    if simplified[-1] != points[-1]:
        simplified.append(points[-1])
    
    # 处理绕远路径
    final = []
    m = len(simplified)
    i = 0
    while i < m:
        final.append(simplified[i])
        best_k = i + 1
        for k in range(i + 1, m):
            path_length = sum(haversine_distance(simplified[n], simplified[n+1]) for n in range(i, k))
            straight_distance = haversine_distance(simplified[i], simplified[k])
            if straight_distance == 0:
                ratio = float('inf')
            else:
                ratio = path_length / straight_distance
            if ratio > distance_ratio_threshold:
                best_k = k
        i = max(i + 1, best_k)
    
    return [[x[0], x[1]] for x in final]

# 示例使用
if __name__ == "__main__":
    # 示例坐标（假设的经纬度列表）
    path = [[118.92334319181613, 32.42174291784471], [118.92334010392457, 32.42171625998488], [118.92358808728459, 32.42172925357188], [118.92358808728459, 32.42172925357188], [118.92360110743458, 32.421429255832884], [118.92360110743458, 32.421429255832884], [118.92361012322458, 32.421195257554885], [118.92361012322458, 32.421195257554885], [118.92361814335457, 32.42090025972488], [118.92361814335457, 32.42090025972488], [118.92362716040458, 32.42064826144488], [118.92362716040458, 32.42064826144488], [118.92363617809458, 32.42038726315988], [118.92363617809458, 32.42038726315988], [118.92363618809458, 32.420244264198885], [118.92363618837457, 32.42024026422788], [118.92288023571457, 32.42024028428288], [118.92287623596458, 32.42024028438788], [118.92287622449457, 32.42040528307188], [118.92287622449457, 32.42040528307188], [118.92288920288458, 32.420704280279885], [118.92288920288458, 32.420704280279885], [118.92290218301459, 32.42097827761688], [118.92290218301459, 32.42097827761688], [118.92290216583459, 32.421225275449885], [118.92290216583459, 32.421225275449885], [118.92290215047458, 32.42144627345488], [118.92290215047458, 32.42144627345488], [118.92290213294459, 32.42169827111788], [118.92290213294459, 32.42169827111788], [118.92290211750458, 32.42192026900288], [118.92289811776457, 32.42192026910188], [118.92338008624458, 32.42193325699688], [118.92338008624458, 32.42193325699688], [118.92390505050457, 32.42196724337188], [118.92395704629457, 32.42198024192388], [118.92397404303458, 32.422011241215884], [118.92397904244459, 32.42201524105288], [118.92396102985458, 32.422020891489154]]
    # path = [[x[1], x[0]] for x in path]
    simplified = simplify_path(path)
    simplified = [[x[0], x[1]] for x in simplified]
    print("简化后的路径点：")
    for p in simplified:
        print(p)
    print(len(path), len(simplified))
    print(simplified)