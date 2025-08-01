from collections import defaultdict
import math
import cv2
import numpy as np


def getBuilldingCoordinat(png):
    # image = cv2.imread(r"D:\canvas.png")
    image = cv2.imread(png)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    lower_bound = np.uint8([[[0xF9, 0xF9, 0xF9]]])
    upper_bound = np.uint8([[[0xFC, 0xFC, 0xFC]]])
    mask = cv2.inRange(image_rgb, lower_bound, upper_bound)
    edges = cv2.Canny(mask, 100, 200)
    kernel = np.ones((5,5), np.uint8)
    edges_dilated = cv2.dilate(edges, kernel, iterations=1)
    edges_eroded = cv2.erode(edges_dilated, kernel, iterations=1)
    contours, _ = cv2.findContours(edges_eroded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contour_image = np.zeros_like(edges)
    area_threshold = 200  # 可以根据实际需要调整这个值
    buildDict = defaultdict(list)
    for idx, contour in enumerate(contours):
        area = cv2.contourArea(contour)
        print(idx, area)
        if area > area_threshold or area == 0:
            M = cv2.moments(contour)
            if M['m00'] != 0:
                cx = int((M['m10'] / M['m00']) * 1000) / 1000
                cy = int((M['m01'] / M['m00']) * 1000) / 1000
                rect = cv2.minAreaRect(contour)
                box = cv2.boxPoints(rect)  # 获取矩形的四个顶点
                box = np.int0(box)  # 转换为整数
                cv2.drawContours(contour_image, [box], 0, (255, 255, 255), 1)
                angle = rect[2]
                if rect[1][0] < rect[1][1]:
                    angle += 90  # 修正角度
                # cv2.circle(contour_image, (cx, cy), 5, (255, 255, 255), -1)
                buildDict[idx] = [(image.shape[1], image.shape[0]), (cx, cy), angle]
    cv2.imshow('image', contour_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return buildDict


def getBuilldingCoordinat2(png):
    # image = cv2.imread(r"D:\canvas.png")
    image = cv2.imread(png)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    lower_bound = np.uint8([[[0xF9, 0xF9, 0xF9]]])
    upper_bound = np.uint8([[[0xFC, 0xFC, 0xFC]]])
    mask = cv2.inRange(image_rgb, lower_bound, upper_bound)
    edges = cv2.Canny(mask, 100, 200)
    kernel = np.ones((5,5), np.uint8)
    edges_dilated = cv2.dilate(edges, kernel, iterations=1)
    edges_eroded = cv2.erode(edges_dilated, kernel, iterations=1)
    contours, _ = cv2.findContours(edges_eroded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contour_image = np.zeros_like(edges)
    area_threshold = 200  # 可以根据实际需要调整这个值
    buildDict = defaultdict(list)
    for idx, contour in enumerate(contours):
        area = cv2.contourArea(contour)
        print(idx, area)
        if area > area_threshold or area == 0:
            M = cv2.moments(contour)
            if M['m00'] != 0:
                cx = int((M['m10'] / M['m00']) * 1000) / 1000
                cy = int((M['m01'] / M['m00']) * 1000) / 1000
                rect = cv2.minAreaRect(contour)
                box = cv2.boxPoints(rect)  # 获取矩形的四个顶点
                box = np.int0(box)  # 转换为整数
                cv2.drawContours(contour_image, [box], 0, (255, 255, 255), 1)
                angle = rect[2]
                if rect[1][0] < rect[1][1]:
                    angle += 90  # 修正角度
                # cv2.circle(contour_image, (cx, cy), 5, (255, 255, 255), -1)
                buildDict[idx] = [(image.shape[1], image.shape[0]), (cx, cy), angle]
    cv2.imshow('image', contour_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return buildDict


def Na(t, e, r):
    n, i, a, o = e
    t[0] = r[0] * n + r[4] * i + r[8] * a + r[12] * o
    t[1] = r[1] * n + r[5] * i + r[9] * a + r[13] * o
    t[2] = r[2] * n + r[6] * i + r[10] * a + r[14] * o
    t[3] = r[3] * n + r[7] * i + r[11] * a + r[15] * o
    return t

def point(x, y, zoom, center, width, height):
    i = [x, y, 0, 1]
    r = [x, y, 1, 1]
    pixelList = calc(zoom, center, width, height)
    i = Na(i, i, pixelList)
    r = Na(r, r, pixelList)
    n, o = i[3], r[3]
    s, a = i[0] / n, r[0] / o
    u, h, c, l = i[1] / n, r[1] / o, i[2] / n, r[2] / o
    p = 0 if c == l else (0 - c) / (l - c)
    res = s * (1 - p) + a * p
    res2 = u * (1 - p) + h * p
    res, res2 = res / (2 ** zoom * 512), res2 / (2 ** zoom * 512)
    lng, lat = 360 * res - 180, 360 / math.pi * math.atan(math.exp((180 - 360 * res2) * math.pi / 180)) - 90
    return round(lng, 6), round(lat, 6)

def perspective(t, e, r, n, i):
    o = 1 / math.tan(e / 2)
    t[0] = o / r
    t[1] = 0
    t[2] = 0
    t[3] = 0
    t[4] = 0
    t[5] = o
    t[6] = 0
    t[7] = 0
    t[8] = 0
    t[9] = 0
    t[11] = -1
    t[12] = 0
    t[13] = 0
    t[15] = 0
    if i:
        a = 1 / (n - i)
        t[10] = (i + n) * a
        t[14] = 2 * i * n * a
    else:
        t[10] = -1
        t[14] = -2 * n
    return t

def scale(t, e, r):
    n = r[0]
    i = r[1]
    a = r[2]
    if isinstance(e[0], list) or isinstance(e[0], tuple):
        e = [x[0] if isinstance(x, tuple) else x for x in e[0]]
    if isinstance(t[0], list) or isinstance(t[0], tuple):
        t = [x[0] if isinstance(x, tuple) else x for x in t[0]]
    t[0] = e[0] * n
    t[1] = e[1] * n
    t[2] = e[2] * n
    t[3] = e[3] * n
    t[4] = e[4] * i
    t[5] = e[5] * i
    t[6] = e[6] * i
    t[7] = e[7] * i
    t[8] = e[8] * a
    t[9] = e[9] * a
    t[10] = e[10] * a
    t[11] = e[11] * a
    t[12] = e[12]
    t[13] = e[13]
    t[14] = e[14]
    t[15] = e[15]
    return t

def translate(t, e, r):
    d, m, v = r
    if isinstance(t[0], list) or isinstance(t[0], tuple):
        t = [x[0] if isinstance(x, tuple) else x for x in t[0]]
    if isinstance(e[0], list) or isinstance(e[0], tuple):
        e = [x[0] if isinstance(x, tuple) else x for x in e[0]]
    if e == t:
        t[12] = e[0] * d + e[4] * m + e[8] * v + e[12]
        t[13] = e[1] * d + e[5] * m + e[9] * v + e[13]
        t[14] = e[2] * d + e[6] * m + e[10] * v + e[14]
        t[15] = e[3] * d + e[7] * m + e[11] * v + e[15]
    else:
        n = e[0]
        i = e[1]
        a = e[2]
        o = e[3]
        s = e[4]
        u = e[5]
        l = e[6]
        p = e[7]
        c = e[8]
        h = e[9]
        f = e[10]
        y = e[11]
        t[0] = e[0]
        t[1] = e[1]
        t[2] = e[2]
        t[3] = e[3]
        t[4] = e[4]
        t[5] = e[5]
        t[6] = e[6]
        t[7] = e[7]
        t[8] = e[8]
        t[9] = e[9]
        t[10] = e[10]
        t[11] = e[11]
        t[12] = n * d + s * m + c * v + e[12]
        t[13] = i * d + u * m + h * v + e[13]
        t[14] = a * d + l * m + f * v + e[14]
        t[15] = o * d + p * m + y * v + e[15]
    return t

def rotateX(t, e, r):
    n = math.sin(r)
    i = math.cos(r)
    a = e[4]
    o = e[5]
    s = e[6]
    u = e[7]
    l = e[8]
    p = e[9]
    c = e[10]
    h = e[11]
    if e != t:
        t[0] = e[0]
        t[1] = e[1]
        t[2] = e[2]
        t[3] = e[3]
        t[12] = e[12]
        t[13] = e[13]
        t[14] = e[14]
        t[15] = e[15]
    t[4] = a * i + l * n
    t[5] = o * i + p * n
    t[6] = s * i + c * n
    t[7] = u * i + h * n
    t[8] = l * i - a * n
    t[9] = p * i - o * n
    t[10] = c * i - s * n
    t[11] = h * i - u * n
    return t

def rotateZ(t, e, r):
    n = math.sin(r)
    i = math.cos(r)
    a = e[0]
    o = e[1]
    s = e[2]
    u = e[3]
    l = e[4]
    p = e[5]
    c = e[6]
    h = e[7]
    if e != t:
        t[8] = e[8]
        t[9] = e[9]
        t[10] = e[10]
        t[11] = e[11]
        t[12] = e[12]
        t[13] = e[13]
        t[14] = e[14]
        t[15] = e[15]
    t[0] = a * i + l * n
    t[1] = o * i + p * n
    t[2] = s * i + c * n
    t[3] = u * i + h * n
    t[4] = l * i - a * n
    t[5] = p * i - o * n
    t[6] = c * i - s * n
    t[7] = h * i - u * n
    return t

def Xu(t):
    return 2 * math.pi * 6378137 * math.cos(t * math.pi / 180)

def multiply(t, e, r):
    n = e[0]
    i = e[1]
    a = e[2]
    o = e[3]
    s = e[4]
    u = e[5]
    l = e[6]
    p = e[7]
    c = e[8]
    h = e[9]
    f = e[10]
    y = e[11]
    d = e[12]
    m = e[13]
    v = e[14]
    g = e[15]
    x = r[0]
    b = r[1]
    _ = r[2]
    w = r[3]
    t[0] = x * n + b * s + _ * c + w * d
    t[1] = x * i + b * u + _ * h + w * m
    t[2] = x * a + b * l + _ * f + w * v
    t[3] = x * o + b * p + _ * y + w * g
    x = r[4]
    b = r[5]
    _ = r[6]
    w = r[7]
    t[4] = x * n + b * s + _ * c + w * d
    t[5] = x * i + b * u + _ * h + w * m
    t[6] = x * a + b * l + _ * f + w * v
    t[7] = x * o + b * p + _ * y + w * g
    x = r[8]
    b = r[9]
    _ = r[10]
    w = r[11]
    t[8] = x * n + b * s + _ * c + w * d
    t[9] = x * i + b * u + _ * h + w * m
    t[10] = x * a + b * l + _ * f + w * v
    t[11] = x * o + b * p + _ * y + w * g
    x = r[12]
    b = r[13]
    _ = r[14]
    w = r[15]
    t[12] = x * n + b * s + _ * c + w * d
    t[13] = x * i + b * u + _ * h + w * m
    t[14] = x * a + b * l + _ * f + w * v
    t[15] = x * o + b * p + _ * y + w * g
    return t

def invert(t, e):
    r = e[0]
    n = e[1]
    i = e[2]
    a = e[3]
    o = e[4]
    s = e[5]
    u = e[6]
    l = e[7]
    p = e[8]
    c = e[9]
    h = e[10]
    f = e[11]
    y = e[12]
    d = e[13]
    m = e[14]
    v = e[15]
    g = r * s - n * o
    x = r * u - i * o
    b = r * l - a * o
    _ = n * u - i * s
    w = n * l - a * s
    A = i * l - a * u
    k = p * d - c * y
    S = p * m - h * y
    z = p * v - f * y
    I = c * m - h * d
    C = c * v - f * d
    B = h * v - f * m
    P = g * B - x * C + b * I + _ * z - w * S + A * k
    if P:
        P = 1 / P
        t[0] = (s * B - u * C + l * I) * P
        t[1] = (i * C - n * B - a * I) * P
        t[2] = (d * A - m * w + v * _) * P
        t[3] = (h * w - c * A - f * _) * P
        t[4] = (u * z - o * B - l * S) * P
        t[5] = (r * B - i * z + a * S) * P
        t[6] = (m * b - y * A - v * x) * P
        t[7] = (p * A - h * b + f * x) * P
        t[8] = (o * C - s * z + l * k) * P
        t[9] = (n * z - r * C - a * k) * P
        t[10] = (y * w - d * b + v * g) * P
        t[11] = (c * b - p * w - f * g) * P
        t[12] = (s * S - o * I - u * k) * P
        t[13] = (r * I - n * S + i * k) * P
        t[14] = (d * x - y * _ - m * g) * P
        t[15] = (p * _ - c * x + h * g) * P
        return t

def calc(zoom, center, width, height):
    _fov = 0.6435011087932844
    _pitch = 0
    angle = 0
    worldSize = 2 ** zoom * 512
    # width, height = 840, 456
    # center = [116.42951316666608, 39.874013878676294]
    point = clamp(center[0], center[1], worldSize)
    camera = 0.5 / math.tan(_fov / 2) * height

    e = _fov / 2
    i = math.pi / 2 + _pitch
    r = math.sin(e) * camera / math.sin(math.pi - i - e)
    n = point
    o = n['x']
    s = n['y']
    a = 1.01 * (math.cos(math.pi / 2 - _pitch) * r + camera)
    u = height / 50
    h = list(range(16))
    h = perspective(h, _fov, width / height, u, a)
    h = scale(h, h, [1, -1, 1])
    h = translate(h, h, [0, 0, -camera])
    h = rotateX(h, h, _pitch)
    h = rotateZ(h, h, angle)
    h = translate(h, h, [-o, -s, 0])
    h = scale(h, h, [1, 1, (1/Xu(center[1])) * worldSize, 1])
    projMatrix = h
    c = width % 2 / 2
    l = height % 2 / 2
    p = math.cos(angle)
    f = math.sin(angle)
    d = o - round(o) + p * c + f * l
    g = s - round(s) + p * l + f * c
    _ = list(range(16))
    h = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]
    h = scale(h, h, [width / 2, -height / 2, 1])
    h = translate(h, h, [1, -1, 0])
    labelPlaneMatrix = h
    h = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]
    h = scale(h, h, [1, -1, 1])
    h = translate(h, h, [-1, -1, 0])
    h = scale(h, h, [2 / width, 2 / height, 1])
    pixelMatrix = multiply(list(range(16)), labelPlaneMatrix, projMatrix)
    h = invert(list(range(16)), pixelMatrix)
    return h

def clamp(lng, lat, worldSize):
    e, r = -85.051129, 85.051129
    i = min(r, max(e, lat))
    x = (180 + lng) / 360
    y = (180 - 180 / math.pi * math.log(math.tan(math.pi / 4 + i * math.pi / 360))) / 360
    return {'x': x * worldSize, 'y': y * worldSize}

if __name__ == "__main__":
    build = getBuilldingCoordinat(r"D:\MGXGIS\Building\340f9998b88a06deef6011b5160160340e9a0434f5.png")
    print(build)
    # point(20, 20, 14.581217926093256)