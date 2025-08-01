# _*_ coding:utf-8 _*_
from collections import defaultdict
import copy
import math
import os
import traceback
import urllib.parse

import requests
import json

import logging

from utils.config import Config


def main4(url, cookie_2=None, psrId=None):
    for i in range(10):
        try:
            gisPath = os.path.join(Config.oriDir, f'{psrId}.json')
            if not os.path.exists(gisPath):
                header = {"Cookie": f"_at={cookie_2}", 'web-token': "78826a12547b4da599faa439c4ee6f30"}
                logging.info(f"url2 : {url}")
                reps_data = requests.get(url, headers=header)
                first_data = reps_data.json()
                open(gisPath, 'w', encoding="U8").write(json.dumps(first_data, indent=4, ensure_ascii=False))
            first_data = json.loads(open(gisPath, 'r', encoding="U8").read())
            return output(first_data, psrId), first_data.get("data", {}).get("shebeiId")
        except Exception as e:
            print(traceback.format_exc())


def rotate_line(point1, point2, angle):
    (x1, y1), (x2, y2) = point1, point2
    length = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    alpha = math.atan2(y2 - y1, x2 - x1)
    angle = math.radians(angle)
    newAngle = alpha + angle
    x3, y3 = x1 + length * math.cos(newAngle), y1 + length * math.sin(newAngle)
    return [x3, y3]


def output(body_data, psrId):
    point_number = 0
    all_data = {}
    other_data = defaultdict(list)
    biaoxiang_data = {}
    dict_data = json.loads(body_data.get("data", {}).get("geojson", {}))
    oriGeoPath = os.path.join(Config.oriGeo, f'{psrId}.json')
    geo3Path = os.path.join(Config.Geo3, f'{psrId}.json')
    if not os.path.exists(oriGeoPath):
        open(oriGeoPath, 'w', encoding="U8").write(json.dumps(dict_data, indent=4, ensure_ascii=False))
    if os.path.exists(geo3Path):
        return geo3Path
    list_data = dict_data.get("features", [])
    # 标箱挑出来
    for info in list_data:
        if info.get("geometry", {}).get("type", '') == "Point" and info.get("properties", {}).get("psrType", "") == "3112":
            point_number += 1
            connection = info.get('properties', {}).get("connection", '')
            biaoxiang_data.setdefault(connection, info)

    # j节点挑出来, 标箱挑出来
    for info in list_data:
        if info.get("geometry", {}).get("type", '') == "Point" and info.get("properties", {}).get("psrType", "") == "3218000":
            point_number += 1
            connection = info.get('properties', {}).get("connection", '')
            all_data.setdefault(connection, info)

    # 其他设备点
    for info in list_data:
        if info.get("geometry", {}).get("type", '') == "Point" and info.get("properties", {}).get("psrType", "") not in ["3218000", '3112']:
            point_number += 1
            connection = info.get('properties', {}).get("connection", '')
            other_data.setdefault(connection, info)

    # 线挑出来
    line_data = defaultdict(list)
    for info in list_data:
        connection = info.get("properties", {}).get("connection", "").split(",")
        psrId = info.get("properties", {}).get("id", "")
        psr_type = info.get("properties", {}).get("psrType", False)
        if info.get("geometry", {}).get("type", '') == "LineString":
            j_list = [x for x in connection if all_data.get(x)]
            if any([other_data.get(x) for x in connection]) and j_list:
                line_data[all_data.get(j_list[0]).get("properties", {}).get("id", "") + '_head'].append([info, [other_data.get(x) for x in connection if other_data.get(x)][0]])
            elif j_list:
                bxs = [biaoxiang_data.get(x) for x in connection if biaoxiang_data.get(x)]
                line_data[all_data.get(j_list[0]).get("properties", {}).get("id", "")].append([info, bxs[0] if bxs else None])

    for k, v in line_data.items():
        if '_head' in k:
            continue
        head = line_data.get(k + '_head', [])
        symbol = -1 if len(head) > 0 and head[0][0].get('geometry', {}).get("coordinates", [])[-1][-1] < head[0][0].get('geometry', {}).get("coordinates", [])[0][1] else 1
        angle = 360 / len(v)
        for i in range(len(v)):
            if not v[i][0] or not v[i][1]:
                continue
            if not v[i][0].get('geometry', {}) or not v[i][1].get('geometry', {}):
                continue
            line_coordinates = v[i][0].get('geometry', {}).get("coordinates", [])
            point_coordinates = v[i][1].get('geometry', {}).get("coordinates", [])
            one = v[i][0].get('properties', {}).get("connection", []).split(',')[0]
            idx = -1 if one == v[i][1].get('properties', {}).get("connection", []) else 0  # 判断是左连接点还是右连接点
            if idx == 0:
                newPoint = rotate_line(line_coordinates[0], [line_coordinates[0][0], line_coordinates[0][1] - 0.00002 * symbol], angle * i)
                line_coordinates[:] = [line_coordinates[0], newPoint]
            else:
                newPoint = rotate_line(line_coordinates[idx], [line_coordinates[idx][0], line_coordinates[idx][1] - 0.00002 * symbol], angle * i)
                line_coordinates[:] = [newPoint, line_coordinates[idx]]
            point_coordinates[:2] = newPoint

    with open(geo3Path, 'w', encoding='utf-8') as current_data2:
        current_data2.write(json.dumps(dict_data, indent=4, ensure_ascii=False))
    return geo3Path


if __name__ == "__main__":
    # cookie_1 = ""
    # cookie_2 = "eyJhbGciOiJIUzI1NiJ9.eyJqdGkiOiIxMzk1NTA3MDgiLCJpYXQiOjE3MzE2MzI4NjQsInN1YiI6IndhbmdyOCIsImV4cCI6MTczMTcxOTI2NH0.b5zNzD7psBUvUQo4nyU-aFTTNvD5Fpyxvoqr4CtV7nE"
    # psrId = "7d891462088a06deed6056103501607d87b66828f8"

    # main2(psrId, '安峰082#刘马村台公变')
    print(os.path.abspath('name.json'))
