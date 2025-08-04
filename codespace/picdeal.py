from collections import defaultdict
import json
import math
import os
import sys
import cv2
import numpy as np
from tqdm import tqdm
# try:
#     from utils.cvPng import point
# except Exception:
#     from cvPng import point
TARGETLIST = [[249, 249, 249], [252, 252, 252], [239, 247, 251], [254, 251, 246], [253, 242, 242], [244, 240, 249], [234, 246, 229]]  # 建筑
TARGETLIST2 = [[255, 255, 255], [255, 240, 187]]   # 道路
TARGETLIST3 = [[178, 206, 254], [251, 204, 180]]  # 河流

def temp(dic, count, i, j, image_rgb, roundList, wh, ht, target_list=TARGETLIST):
    stack = [(i, j)]  # 使用栈代替递归
    dic[(i, j)] = count

    while stack:
        i, j = stack.pop()  # 取出当前像素
        for k1, k2 in roundList:
            x, y = i + k1, j + k2
            if (x, y) in dic:  # 已访问过
                continue
            if 0 <= x < wh and 0 <= y < ht:
                if list(image_rgb[x][y]) in target_list:
                    dic[(x, y)] = count
                    stack.append((x, y))  # 将相邻像素加入栈


def calculate_angle(point1, point2, degrees=True, image_coordinate=True):
    dx = point2[0] - point1[0]
    dy = point2[1] - point1[1]
    if image_coordinate:
        dy = -dy
    if dx == 0 and dy == 0:
        raise ValueError("两点坐标重合，无法计算角度")
    angle_rad = math.atan2(dy, dx)
    if degrees:
        angle = math.degrees(angle_rad)
        while angle > 90:
            angle -= 180
        while angle < -90:
            angle += 180
        return round(angle, 2)
    return round(angle_rad, 2)


def calculate_pixel_distance(point1, point2, precision=2):
    x1, y1 = point1
    x2, y2 = point2
    dx = x2 - x1
    dy = y2 - y1
    distance = math.sqrt(dx**2 + dy**2)
    return round(distance, precision)


def getBuilldingCoordinat2(image_rgb, psrId, zoom, center_point, target_list=TARGETLIST2):
    data_dict = {}
    width, height = image_rgb.shape[:2]

    # image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    dic, count = defaultdict(int), 1
    roundList = [(1, -1), (1, 1), (1, 0), (0, 1), (-1, 1), (-1, -1), (-1, 0), (0, -1), (0, 0)]
    for i in range(width):
        for j in range(height):
            if list(image_rgb[i][j]) in target_list:
                if dic.get((i, j), 0) != 0:
                    continue
                temp(dic, count, i, j, image_rgb, roundList, width, height, target_list)
                count += 1
    # print('width, height ', width, height, 'dic', len(dic))
    dic2 = defaultdict(list)
    for key, val in dic.items():
        dic2[val].append(key)

    # 在中心位置画一个红色的点
    for k1, k2 in roundList:
        if 0 <= width // 2 + k1 < len(image_rgb) and 0 <= height // 2 + k2 < len(image_rgb[width // 2 + k1]):
            image_rgb[width // 2 + k1][height // 2 + k2] = [255, 0, 0]
    dic2 = {idx: val for idx, (_, val) in enumerate(dic2.items()) if len(val) > 50}
    for key, val in dic2.items():
        vertices_list = []  # 新增：存储每个绿色区域的像素坐标列表
        for x, y in val:
            image_rgb[x][y] = [255, 255, 0] if target_list == TARGETLIST3 else [0, 0, 255]
            vertices_list.append((y, x))
        points = dic2[key]
        points_array = np.array(points)
        rect = cv2.minAreaRect(points_array)
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        distance1 = calculate_pixel_distance(box[0], box[1])
        distance2 = calculate_pixel_distance(box[0], box[2])
        distance3 = calculate_pixel_distance(box[0], box[3])
        distance = sorted([distance1, distance2, distance3])[1]
        point2 = box[1] if distance == distance1 else (box[2] if distance == distance2 else box[3])
        angle = calculate_angle(box[0], point2, degrees=True, image_coordinate=True)
        center = np.mean(points_array, axis=0)
        center = [int(coord) for coord in center]
        dic2[key] = [center, angle, len(val)]
        for k1, k2 in roundList:
            if 0 <= center[0] + k1 < len(image_rgb) and 0 <= center[1] + k2 < len(image_rgb[center[0] + k1]):
                image_rgb[center[0] + k1, center[1] + k2] = [255, 0, 0]
        lng, lat = point(center[1], center[0], zoom, center_point, height, width)
        data_dict[key] = {'center': [(lng, lat), (center[1], center[0])], 'angle': round(angle + 90, 2), 'area': len(val), 'vertices': []}

        # 新增：提取绿色区域顶点并转换为经纬度
        mask = np.zeros((width, height), dtype=np.uint8)
        for px, py in points:
            mask[px, py] = 255
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            for vertex in cnt:
                vx, vy = vertex[0]
                image_rgb[vy, vx] = [0, 255, 0]
                # lng_v, lat_v = point(vy, vx, zoom, center_point, height, width)
                # vertices_list.append([(lng_v, lat_v), (int(vy), int(vx))])
        data_dict[key]['vertices'] = json.dumps(vertices_list, ensure_ascii=False)

    return image_rgb, data_dict


def getBuilldingCoordinat(image_path, psrId, zoom, center_point):
    data_dict = {}
    image = cv2.imread(image_path)
    width, height = image.shape[:2]
    # print(width, height)
    # return

    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    dic, count = defaultdict(int), 1
    roundList = [(1, -1), (1, 1), (1, 0), (0, 1), (-1, 1), (-1, -1), (-1, 0), (0, -1), (0, 0)]
    for i in range(width):
        for j in range(height):
            if list(image_rgb[i][j]) in TARGETLIST:
                if dic.get((i, j), 0) != 0:
                    continue
                temp(dic, count, i, j, image_rgb, roundList, width, height)
                count += 1
    # print('width, height ', width, height, 'dic', len(dic))
    dic2 = defaultdict(list)
    for key, val in dic.items():
        dic2[val].append(key)

    # 在中心位置画一个红色的点
    for k1, k2 in roundList:
        if 0 <= width // 2 + k1 < len(image_rgb) and 0 <= height // 2 + k2 < len(image_rgb[width // 2 + k1]):
            image_rgb[width // 2 + k1][height // 2 + k2] = [255, 0, 0]
    dic2 = {idx: val for idx, (_, val) in enumerate(dic2.items()) if len(val) > 50}
    for key, val in dic2.items():
        vertices_list = []  # 新增：存储每个绿色区域的像素坐标列表
        for x, y in val:
            image_rgb[x][y] = [0, 255, 0]
            vertices_list.append((y, x))
        points = dic2[key]
        points_array = np.array(points)
        rect = cv2.minAreaRect(points_array)
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        distance1 = calculate_pixel_distance(box[0], box[1])
        distance2 = calculate_pixel_distance(box[0], box[2])
        distance3 = calculate_pixel_distance(box[0], box[3])
        distance = sorted([distance1, distance2, distance3])[1]
        point2 = box[1] if distance == distance1 else (box[2] if distance == distance2 else box[3])
        angle = calculate_angle(box[0], point2, degrees=True, image_coordinate=True)
        center = np.mean(points_array, axis=0)
        center = [int(coord) for coord in center]
        dic2[key] = [center, angle, len(val)]
        for k1, k2 in roundList:
            if 0 <= center[0] + k1 < len(image_rgb) and 0 <= center[1] + k2 < len(image_rgb[center[0] + k1]):
                image_rgb[center[0] + k1, center[1] + k2] = [255, 0, 0]
        lng, lat = point(center[1], center[0], zoom, center_point, height, width)
        data_dict[key] = {'center': [(lng, lat), (center[1], center[0])], 'angle': round(angle + 90, 2), 'area': len(val), 'vertices': []}

        # 新增：提取绿色区域顶点并转换为经纬度
        mask = np.zeros((width, height), dtype=np.uint8)
        for px, py in points:
            mask[px, py] = 255
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            for vertex in cnt:
                vx, vy = vertex[0]
                image_rgb[vy, vx] = [0, 0, 255]
                # lng_v, lat_v = point(vy, vx, zoom, center_point, height, width)
                # vertices_list.append([(lng_v, lat_v), (int(vy), int(vx))])
        data_dict[key]['vertices'] = json.dumps(vertices_list, ensure_ascii=False)
    # 输出每个绿色区域的顶点经纬度列表
    # for key, vertices in green_area_vertices.items():
    #     print(f"绿色区域 {key} 顶点经纬度坐标：", vertices)
    image_rgb, sub_data = getBuilldingCoordinat2(image_rgb, psrId, zoom, center_point, TARGETLIST2)
    image_rgb, sub_data2 = getBuilldingCoordinat2(image_rgb, psrId, zoom, center_point, TARGETLIST3)
    resDict = {'建筑': data_dict, '道路': sub_data, '河流': sub_data2}
    image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
    
    cv2.imshow("Contour Image", image_bgr)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    os.makedirs("d:/res", exist_ok=True)
    json.dump(resDict, open(f'd:/res/{psrId}.json', 'w', encoding="U8"), ensure_ascii=False, indent=4)
    os.makedirs("d:/res", exist_ok=True)
    cv2.imwrite(f"d:/res/{psrId}.png", image_bgr)
    # print(len(dic2), len(data_dict), data_dict.keys())
    return data_dict


def main():
    picDir = r"C:\Users\jjf55\Desktop\Building"
    for pic in tqdm(os.listdir(picDir)):
        if not pic.endswith('.png'):
            continue
        img = os.path.join(picDir, pic)
        psrId = pic.split('.')[0]
        json_path = os.path.join(picDir, f'{psrId}.json')
        center_point = json.loads(open(json_path, 'r', encoding='utf-8').read())['center']
        zoom = 18
        getBuilldingCoordinat(img, psrId, zoom, center_point)


if __name__ == "__main__":
    main()
