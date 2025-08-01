# _*_ coding:utf-8 _*_
from collections import defaultdict
import copy
import os
import traceback
import urllib.parse

import requests
import json

import logging

from meihua_new import yijianmeihua
from utils.config import Config


def main2(url, cookie_2=None, psrId=None, width=0, height=0, zoom=0, center=0, mapToken=None):
    for i in range(2):
        try:
            gisPath = os.path.join(Config.oriDir, f'{psrId}.json')

            if not os.path.exists(gisPath):
                header = {"Cookie": f"_at={cookie_2}", 'web-token': "78826a12547b4da599faa439c4ee6f30"}
                logging.info(f"url2 : {url}")
                reps_data = requests.get(url, headers=header)
                first_data = reps_data.json()
                open(gisPath, 'w', encoding="U8").write(json.dumps(first_data, indent=4, ensure_ascii=False))
            first_data = json.loads(open(gisPath, 'r', encoding="U8").read())
            res = yijianmeihua(psrId, width, height, zoom, center, mapToken)
            return res  # output(first_data, psrId), first_data.get("data", {}).get("shebeiId")
        except Exception as e:
            print(traceback.format_exc())


def output(body_data, psrId):
    point_number = 0
    all_data = {}
    other_data = defaultdict(list)
    biaoxiang_data = {}
    dict_data = json.loads(body_data.get("data", {}).get("geojson", {}))
    oriGeoPath = os.path.join(Config.oriGeo, f'{psrId}.json')
    geo1Path = os.path.join(Config.Geo1, f'{psrId}.json')
    if not os.path.exists(oriGeoPath):
        open(oriGeoPath, 'w', encoding="U8").write(json.dumps(dict_data, indent=4, ensure_ascii=False))
    if os.path.exists(geo1Path):
        return geo1Path
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
        # if len(head) > 0:
        #     print(head[0][0].get('geometry', {}).get("coordinates", [])[-1][-1], head[0][0].get('geometry', {}).get("coordinates", [])[0][1], symbol)
        if len(v) % 2 == 1:
            for i in range(len(v)):
                if not v[i][0] or not v[i][1]:
                    continue
                if not v[i][0].get('geometry', {}) or not v[i][1].get('geometry', {}):
                    continue
                line_coordinates = v[i][0].get('geometry', {}).get("coordinates", [])
                point_coordinates = v[i][1].get('geometry', {}).get("coordinates", [])
                one = v[i][0].get('properties', {}).get("connection", []).split(',')[0]
                idx = -1 if one == v[i][1].get('properties', {}).get("connection", []) else 0  # 判断是左连接点还是右连接点
                if i == 0:
                    if idx == 0:
                        line_coordinates[:] = [line_coordinates[0], [line_coordinates[0][0], line_coordinates[0][1] - 0.00004 * symbol]]
                    else:
                        line_coordinates[:] = [[line_coordinates[idx][0], line_coordinates[idx][1] - 0.00004 * symbol], line_coordinates[idx]]
                    point_coordinates[:2] = [line_coordinates[idx][0], line_coordinates[idx][1] - 0.00004 * symbol]
                    continue
                i_ = i // 2 if i % 2 == 0 else (-i - 1) // 2
                if idx == 0:
                    line_coordinates[:] = [line_coordinates[0], [line_coordinates[0][0], line_coordinates[0][1] - 0.00002 * symbol], [line_coordinates[0][0] + (0.00002 * i_ ), line_coordinates[0][1] - 0.00002 * symbol], [line_coordinates[0][0] + (0.00002 * i_), line_coordinates[0][1] - 0.00004 * symbol]]
                else:
                    line_coordinates[:] = [[line_coordinates[idx][0], line_coordinates[idx][1] - 0.00002 * symbol], [line_coordinates[idx][0] + (0.00002 * i_ ), line_coordinates[idx][1] - 0.00002 * symbol], [line_coordinates[idx][0] + (0.00002 * i_), line_coordinates[idx][1] - 0.00004 * symbol], line_coordinates[idx]]
                point_coordinates[:2] = [line_coordinates[idx][0] + (0.00002 * i_), line_coordinates[idx][1] - 0.00004 * symbol]

        if len(v) % 2 == 0:
            for i in range(len(v)):
                if not v[i][0] or not v[i][1]:
                    continue
                if not v[i][0].get('geometry', {}) or not v[i][1].get('geometry', {}):
                    continue
                line_coordinates = v[i][0].get('geometry', {}).get("coordinates", [])
                point_coordinates = v[i][1].get('geometry', {}).get("coordinates", [])
                one = v[i][0].get('properties', {}).get("connection", []).split(',')[0]
                idx = -1 if one == v[i][1].get('properties', {}).get("connection", []) else 0  # 判断是左连接点还是右连接点
                i_ = (i + 2) // 2 if i % 2 == 0 else (-i - 1) // 2
                if idx == 0:
                    line_coordinates[:] = [line_coordinates[0], [line_coordinates[0][0], line_coordinates[0][1] - 0.00002 * symbol], [line_coordinates[0][0] + (0.00002 * i_ ) - 0.00001 * i_ / abs(i_), line_coordinates[0][1] - 0.00002 * symbol], [line_coordinates[0][0] + (0.00002 * i_) - 0.00001 * i_ / abs(i_), line_coordinates[0][1] - 0.00004 * symbol]]
                else:
                    line_coordinates[:] = [[line_coordinates[idx][0], line_coordinates[idx][1] - 0.00002 * symbol], [line_coordinates[idx][0] + (0.00002 * i_ ) - 0.00001 * i_ / abs(i_), line_coordinates[idx][1] - 0.00002 * symbol], [line_coordinates[idx][0] + (0.00002 * i_) - 0.00001 * i_ / abs(i_), line_coordinates[idx][1] - 0.00004 * symbol], line_coordinates[idx]]
                point_coordinates[:2] = [line_coordinates[idx][0] + (0.00002 * i_) - 0.00001 * i_ / abs(i_), line_coordinates[idx][1] - 0.00004 * symbol]

    with open(geo1Path, 'w', encoding='utf-8') as current_data2:
        current_data2.write(json.dumps(dict_data, indent=4, ensure_ascii=False))
    return geo1Path


def tempfunc(resDict, connectDict, root, cure=True):
    for k, lis in root.items():
        for info in connectDict[k]:
            if info['properties']['id'] == lis[0]:
                continue
            subRoot = defaultdict(str)
            connects = info['properties']['connection'].split(',')
            for con in connects:
                if not con or (len(connects) > 1 and con == k):
                    continue
                subRoot[con] = [info['properties']['id'], info['properties']['connection'], info['geometry']['coordinates'], info['properties']['objType']]
                if k not in resDict:
                    resDict[k] = {'key': lis[0], 'connection': lis[1], 'coordinates': lis[2], 'objtype': lis[3]}
                if cure:
                    resDict[k].update({con: defaultdict(dict)})
            for con in subRoot:
                if cure:
                    resDict[k][con] = tempfunc(resDict[k][con], connectDict, subRoot, False if len(connects) == 1 else True)
    return resDict


def output2(first_data, psrId):
    dict_data = json.loads(first_data.get("data", {}).get("geojson", {}))
    list_data = dict_data.get("features", [])
    # 标箱挑出来
    rootId = [x['properties']['id'] for x in list_data if x['properties']['objType'] == 30000005][0]
    resList = []
    for idx, info in enumerate(list_data):
        # connects = [x for x in info['properties']['connection'].split(',') if x]
        # # print(info['properties']['objType'])
        # if info['properties']['objType'] == 30000005:
        #     root = {x: [info['properties']['id'], info['properties']['connection'], info['geometry']['coordinates'], info['properties']['objType']] for x in connects}
        # for con in connects:
        #     connectDict[con].append(info)
        resList.append({'id': idx, 'x': info['properties']['connection']})
    print(resList)

    # print(len(connectDict), root)
    resDict = defaultdict(dict)
    # resDict = tempfunc(resDict, connectDict, root)
    # open('d:/info2.json', 'w', encoding="U8").write(json.dumps(resList))



def test(psrId="1b7f653b618a06deec6612d62f01661b7f2eea519c"):
    gisPath = os.path.join(Config.oriDir, f'{psrId}.json')
    first_data = json.loads(open(gisPath, 'r', encoding="U8").read())
    output2(first_data, psrId)


def output3():
    pass


if __name__ == "__main__":
    # print(os.path.abspath('name.json'))
    # bodydata = json.loads(open('temp2.json', 'r', encoding="U8").read())
    # output(bodydata, 'temp')

    test()
