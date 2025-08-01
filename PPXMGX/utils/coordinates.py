from collections import defaultdict
import json
import math
import sys
import cv2
import numpy as np
try:
    from utils.cvPng import point
except Exception:
    from cvPng import point
TARGETLIST = [[249, 249, 249], [252, 252, 252]]


def temp2(dic, count, i, j, image_rgb, roundList, wh, ht):
    dic[(i, j)] = count
    lis = []
    for k1, k2 in roundList:
        if dic.get((i + k1, j + k2), 0) != 0:
            continue
        if 0 <= i + k1 < wh and 0 <= j + k2 < ht:
            if list(image_rgb[i + k1][j + k2]) in TARGETLIST:
                lis.append((i + k1, j + k2))
                dic[(i + k1, j + k2)] = count
    for x, y in lis:
        temp(dic, count, x, y, image_rgb, roundList, wh, ht)

def temp(dic, count, i, j, image_rgb, roundList, wh, ht):
    stack = [(i, j)]  # 使用栈代替递归
    dic[(i, j)] = count

    while stack:
        i, j = stack.pop()  # 取出当前像素
        for k1, k2 in roundList:
            x, y = i + k1, j + k2
            if (x, y) in dic:  # 已访问过
                continue
            if 0 <= x < wh and 0 <= y < ht:
                if list(image_rgb[x][y]) in TARGETLIST:
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


def getBuilldingCoordinat(image_path, psrId, zoom, center_point):
    data_dict = {}
    image = cv2.imread(image_path)
    width, height = image.shape[:2]

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
    print('width, height ', width, height, 'dic', len(dic))
    dic2 = defaultdict(list)
    for key, val in dic.items():
        dic2[val].append(key)

    # 在中心位置画一个红色的点
    for k1, k2 in roundList:
        if 0 <= width // 2 + k1 < len(image_rgb) and 0 <= height // 2 + k2 < len(image_rgb[width // 2 + k1]):
            image_rgb[width // 2 + k1][height // 2 + k2] = [255, 0, 0]
    dic2 = {idx: val for idx, (_, val) in enumerate(dic2.items()) if len(val) > 50}
    for key, val in dic2.items():
        for x, y in val:
            image_rgb[x][y] = [0, 255, 0]
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
                image_rgb[center[0] + k1, center[1] + k2] = [(0 if key == 186 else 255), 0, 0]
        lng, lat = point(center[1], center[0], zoom, center_point, height, width)
        data_dict[key] = [[lng, lat - 0.000093], round(angle + 90, 2), len(val)]
    image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
    # cv2.imshow("Contour Image", image_bgr)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    # json.dump(data_dict, open(f'd:/{psrId}.json', 'w'), ensure_ascii=False, indent=4)
    # cv2.imwrite(f"d:/{psrId}.png", image_bgr)
    print(len(dic2), len(data_dict), data_dict.keys())
    return data_dict


if __name__ == "__main__":
    img = r"D:\MGXGIS\Building\0f24d37e-97ba-42b9-986d-5d290cfcb049.png"
    psrId = "0f24d37e-97ba-42b9-986d-5d290cfcb049"
    center_point = [118.93278462262595, 32.416980693731574]
    zoom = 18
    getBuilldingCoordinat(img, psrId, zoom, center_point)
