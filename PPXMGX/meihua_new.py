from collections import defaultdict
import math
import os
import json
import requests
from meihua2 import output1
from utils.config import Config
from utils.devlop import simplify_path
from utils.log import logger
# from utils.cvPng import getBuilldingCoordinat, point
from utils.coordinates import getBuilldingCoordinat
psrDict, LNG, LAT = {}, 0, 0

def output2(list_data, objType, rootId):
    psrInt, nodeList = defaultdict(int), []
    psrInt[rootId] += 1
    dic1 = {x['properties']['connection']: x['properties']['psrId'] for x in list_data if 'connection' in x['properties']}  # con -- id
    dic2 = {x['properties']['psrId']: x['properties']['connection'] for x in list_data if 'connection' in x['properties']}  # id -- con

    def find_connect_chain(psr, node, isPoint):
        cons = [x for x in dic2[psr].split(',') if x]
        for con in cons:
            psrs = [y for x, y in dic1.items() if con in x and y != psr and not psrInt[y]]
            if not psrs:
                continue
            if node in nodeList:
                nodeList.pop(nodeList.index(node))
            for psr1 in psrs:
                psrType = psrDict[psr1]['geometry']['type']
                if not isPoint and psrType == "LineString":
                    continue
                node2 = f"{node}_{psr1}"
                psrInt[psr1] = 1
                nodeList.append(node2)
                find_connect_chain(psr1, node2, not isPoint)
    find_connect_chain(rootId, rootId, True)

    psrSet = defaultdict(dict)
    for node in nodeList:
        nodes = node.split('_')
        for idx, psr in enumerate(nodes):
            if psr not in psrSet:
                psrSet[psr] = {'parent': None, 'set': set()}
            if idx + 1 == len(nodes):
                psrSet[psr]['parent'] = nodes[idx - 1]
            for i in range(idx + 1, len(nodes)):
                psrSet[psr]['set'].add(nodes[i])
                if idx > 0:
                    psrSet[psr]['parent'] = nodes[idx - 1]
    psrSet = {x: {'parent': y['parent'], 'set': list(y['set'])} for x , y in psrSet.items()}
    # open(r"D:/info3.json", 'w', encoding="U8").write(json.dumps(psrSet, indent=4, ensure_ascii=False))
    objTypes = [x['properties']['psrId'] for x in list_data if x['properties']['objType'] in objType]
    return {psr: psrSet[psr] for psr in objTypes if psr in psrSet and psr != rootId}, psrSet


def movePsr(geoData, psr, item, con, lng, lat):
    psrList = list(item['set']) + [psr]
    parent = item['parent']
    
    for oriItem in geoData:
        psrId = oriItem['properties']['psrId']
        geometry = oriItem['geometry']
        coor = geometry['coordinates']
        if psrId in psrList:
            if ',' not in oriItem['properties']['connection']:
                geometry['coordinates'] = [coor[0] + lng, coor[1] + lat]
            else:
                for idx, coor in enumerate(geometry['coordinates']):
                    if not isinstance(coor[0], list):
                        geometry['coordinates'][idx] = [coor[0] + lng, coor[1] + lat]
                    else:
                        for subIdx, subCoor in enumerate(coor):
                            geometry['coordinates'][idx][subIdx] = [subCoor[0] + lng, subCoor[1] + lat]
        if psrId == parent:
            if any([str(oriItem['properties']['connection']).startswith(x) for x in con[0].split(',') if x]):
                geometry['coordinates'][0] = [coor[0][0] + lng, coor[0][1] + lat]
            else:
                geometry['coordinates'][-1] = [coor[-1][0] + lng, coor[-1][1] + lat]


def calcDiff(buildDict, coor):
    minDistant, k, diff = 9999, None, [0, 0]
    for key, val in buildDict.items():
        if len(buildDict[key]) >= 4:
            continue
        if (val[0][0] - coor[0] - LNG) ** 2 + (val[0][1] - coor[1] - LAT) ** 2 < minDistant:
            k, diff = key, [val[0][0] - coor[0] - LNG, val[0][1] - coor[1] - LAT]
            minDistant = (val[0][0] - coor[0] - LNG) ** 2 + (val[0][1] - coor[1] - LAT) ** 2
    if k is not None:
        print(k, diff, val[0], coor, LNG, LAT)
        buildDict[k].append(diff)
    return diff, buildDict.get(k, [0, 0, 180])[1]


def calcPoint(lng, lat, angle, distance=8):
    radius = 6378137.0
    angleRad = math.radians(angle)
    deltaLat = (distance / radius) * (180 / math.pi)
    deltaLng = (distance / radius) * (180 / math.pi) / math.cos(math.radians(lat))
    lat = lat + deltaLat * math.cos(angleRad + math.pi / 2)
    lng = lng + deltaLng * math.sin(angleRad + math.pi / 2)
    return [lng, lat]

def calculate_center(coords):
    """ 获取一个设备的中心坐标值 """
    if isinstance(coords[0], list):
        tarcoords = coords[0] if isinstance(coords[0][0], list) else coords
    else:
        return coords[0], coords[1]
    xt, yt, zt, R = 0, 0, 0, 6371
    for lon, lat in tarcoords:
        lat_rad = math.radians(lat)
        lon_rad = math.radians(lon)
        xt += R * math.cos(lat_rad) * math.cos(lon_rad)
        yt += R * math.cos(lat_rad) * math.sin(lon_rad)
        zt += R * math.sin(lat_rad)
    n = len(coords)
    xa, ya, za = xt / n, yt / n, zt / n
    lon = math.degrees(math.atan2(ya, xa))
    lat = math.degrees(math.atan2(za, math.sqrt(xa**2 + ya**2)))
    return lon, lat

def calculate_minlat(coords):
    """ 获取一个设备最小的纬度坐标值 """
    reslat = 9999
    if isinstance(coords[0], list):
        tarcoords = coords[0] if isinstance(coords[0][0], list) else coords
    else:
        return coords[1]
    for _, lat in tarcoords:
        if lat < reslat:
            reslat = lat
    return reslat

def dealLine(geoData, psrSet, line, parent, lineCount, idx, lon, psrList=None):
    lineInfo = psrDict.get(line)
    parentInfo = psrDict.get(parent)
    subPsr = [x for x in psrSet.keys() if psrSet[x]['parent'] == line][0]
    if psrList and subPsr in psrList:
        return
    lineCon = [x for x in lineInfo['properties']['connection'].split(',') if x in parentInfo['properties']['connection']][0]
    if isinstance(parentInfo['geometry']['coordinates'][0], list):
        if isinstance(parentInfo['geometry']['coordinates'][0][0], list):
            parentLng, parentLat = calculate_center(parentInfo['geometry']['coordinates'][0])  # [idxCon]
        else:
            parentLng, parentLat = calculate_center(parentInfo['geometry']['coordinates'])  # [idxCon]
        parentLat -= 0.000005 #  if psrDict[parent].get('angle', 180) - 90 > 0 else -0.00001
        parentLng = lineInfo['geometry']['coordinates'][0][0] if lineInfo['properties']['connection'].startswith(lineCon) else lineInfo['geometry']['coordinates'][-1][0]
    else:
        parentLng, parentLat = parentInfo['geometry']['coordinates']

    # newLng, newLat = calcPoint(parentLng, parentLat, psrDict[parent].get('angle', 180) - 90, 2)
    lineCoor = lineInfo['geometry']['coordinates']
    subLines = [x for x in psrSet.keys() if psrSet[x]['parent'] == subPsr]
    if lineCount > 1:
        # print('dddddddddd', line, idx, len(subLines), len(psrSet[subPsr]['set']))
        lonDiff, idx = (lineCount % 2) / 2 - 0.5, ((idx if idx % 2 == 0 else -idx) // 2)
        # newLng2, newLat2 = calcPoint(newLng, newLat, psrDict[parent].get('angle', 180), (idx * lon - lon * lonDiff))
        newLng3, newLat3 = calcPoint(parentLng, parentLat, psrDict[parent].get('angle', 180) - 90, 3 if parent in psrList else 1)
        lineInfo['geometry']['coordinates'] = [lineCoor[0], lineCoor[-1]]
    else:
        # print('sssssssssss', line, idx, len(subLines))
        newLng3, newLat3 = calcPoint(parentLng, parentLat, psrDict[parent].get('angle', 180) - 90, 3 if parent in psrList else 1)
        if lineInfo['properties']['connection'].startswith(lineCon):
            lineInfo['geometry']['coordinates'] = [lineCoor[0], lineCoor[-1]]
        else:
            lineInfo['geometry']['coordinates'] = [lineCoor[0], lineCoor[-1]]
    con = [psrDict[subPsr]['properties']['connection'], psrDict[subPsr]['geometry']['coordinates']]
    if isinstance(psrDict[subPsr]['geometry']['coordinates'][0], list):
        if isinstance(psrDict[subPsr]['geometry']['coordinates'][0][0], list):
            parentLng, parentLat = calculate_center(psrDict[subPsr]['geometry']['coordinates'][0][:4])
            lngDiff, latDiff = newLng3 - parentLng, newLat3 - parentLat
        else:
            parentLng, parentLat = calculate_center(psrDict[subPsr]['geometry']['coordinates'][:4])
            lngDiff, latDiff = newLng3 - parentLng, newLat3 - parentLat
    else:
        lngDiff, latDiff = newLng3 - psrDict[subPsr]['geometry']['coordinates'][0], newLat3 - psrDict[subPsr]['geometry']['coordinates'][1]
    movePsr(geoData, subPsr, psrSet[subPsr], con, lngDiff, latDiff)
    psrDict[subPsr].update({'angle': 180})
    lon = len(psrSet[subPsr]['set']) // 2 / ((len(subLines) - 1) if len(subLines) > 1 else 1)
    for idx2, line in enumerate(subLines):
        dealLine(geoData, psrSet, line, subPsr, len(subLines), idx2, lon, psrList)


def compute_centroid(coors):
    lng = sum([x[0] for x in coors]) / 4
    lat = sum([x[1] for x in coors]) / 4
    return [lng, lat]


def method1(psrSet, rootId, list_data, psrList, buildDict):
    ''' 处理不带分支箱的设备 '''
    outLines = [x for x in psrSet.keys() if psrSet[x]['parent'] == rootId]
    lon = len(psrSet[rootId]['set']) // 4 / ((len(outLines) - 1) if len(outLines) > 1 else 1)
    zdt1 = {y: x for x in outLines for y in psrSet.keys() if psrSet[y]['parent'] == x and psrDict[y]['properties']['psrType'] == '3202' and y not in psrList}  # 筛选出从配电室出来的终端头和它相连的父线
    zdt1_zdt2 = {x: y for x in zdt1 for y in psrSet.keys() if psrSet[y]['parent'] == x}  # 筛选出从配电室出来的终端头1和它相连的子线
    zdt2 = {y: psrSet[y] for _, x in zdt1_zdt2.items() for y in psrSet.keys() if psrSet[y]['parent'] == x}  # 筛选出从配电室出来的终端头2和它的所有子设备
    rootCoors = psrDict[rootId]['geometry']['coordinates']
    latCoor = calculate_minlat(rootCoors) - 0.00000819  # 配电室正下方1米处维度坐标
    for z, x in zdt1.items():
        zdtCon = psrDict[z]['properties']['connection']
        xianCon = str(psrDict[x]['properties']['connection'])
        xianCon2 = str(psrDict[zdt1_zdt2[z]]['properties']['connection'])
        if xianCon.endswith(zdtCon):
            newCoor = [psrDict[x]['geometry']['coordinates'][0][0], latCoor]
            psrDict[x]['geometry']['coordinates'] = [psrDict[x]['geometry']['coordinates'][0], newCoor]  # 父连接线开头位置不动, 结尾随终端头移动
        else:
            newCoor = [psrDict[x]['geometry']['coordinates'][-1][0], latCoor]
            psrDict[x]['geometry']['coordinates'] = [newCoor, psrDict[x]['geometry']['coordinates'][-1]]
        psrDict[z]['geometry']['coordinates'] = newCoor  # 经度使用父连接线的经度值，纬度使用配电室最小纬度加1米的值
        if xianCon2.endswith(zdtCon):
            psrDict[zdt1_zdt2[z]]['geometry']['coordinates'][-1] = newCoor
        else:
            psrDict[zdt1_zdt2[z]]['geometry']['coordinates'][0] = newCoor
    # rootlng, rootlat = calculate_center(rootCoors)  # 配电室的中心坐标
    # (lng, lat), angle = calcDiff(buildDict, [rootlng, rootlat])
    # rootnewlng, rootnewlat = calcPoint(lng, lat, angle + 90)
    # for idx, (psr, item) in enumerate(zdt2.items()):
    #     con = [(x['properties']['connection'], x['geometry']['coordinates']) for x in list_data if x['properties']['psrId'] == psr][0]
    #     newlng, newlat = rootnewlng + rootlng - con[1][0] - 0.000009 * idx, rootnewlat + rootlat - con[1][1]
    #     movePsr(list_data, psr, item, con, newlng, newlat)
    # logger.info({x: y for x, y in buildDict.items() if len(y) >= 4})

    # # 分支箱的下游设备
    # for psr, item in zdt2.items():
    #     subLines = [x for x in psrSet.keys() if psrSet[x]['parent'] == psr]
    #     lon = len(item['set'])//4/((len(subLines) - 1) if len(subLines) > 1 else 1)
    #     for idx, line in enumerate(subLines):
    #         dealLine(list_data, psrSet, line, psr, len(subLines), idx, lon, psrList)
    return zdt2

    # for idx, (zdt, line1) in enumerate(zdt2.items()):
    #     dealLine(list_data, psrSet, line1, zdt, len(outLines), idx, lon, psrList)


def update_junction_box(psrList, rootId, psrDict):
    """ 修改分支箱的大小, 修改成2 X 3 """
    # 调整配电室
    lineDict = {x: [y, y['properties']['connection'].split(',')] for x, y in psrDict.items() if y['geometry']['type'] == "LineString"}
    connections = psrDict[rootId].get('properties', {}).get('connection', '').strip(',').split(',')
    innerDict = {x: [0 if y[1][0] in connections else -1, y[0]['geometry']['coordinates']] for x, y in lineDict.items() if [z for z in connections if z in y[1]]}
    if isinstance(psrDict[rootId]['geometry']['coordinates'][0], list):
        parentLng, parentLat = calculate_center(psrDict[rootId]['geometry']['coordinates'][0][:4])
    else:
        parentLng, parentLat = calculate_center(psrDict[rootId]['geometry']['coordinates'][:4])
    vertices = psrDict[rootId]['geometry']['coordinates'][0]
    vertices, inner_points = scale_rectangle(parentLng, parentLat, vertices, innerDict)
    psrDict[rootId]['geometry']['coordinates'][0] = vertices
    for psrId, [idx, coor] in inner_points.items():
        psrDict[psrId]['geometry']['coordinates'][idx] = coor
    # 调整分支箱
    for boxId, _ in psrList.items():
        connections = psrDict[boxId].get('properties', {}).get('connection', '').strip(',').split(',')
        innerDict = {x: [0 if y[1][0] in connections else -1, y[0]['geometry']['coordinates']] for x, y in lineDict.items() if [z for z in connections if z in y[1]]}
        if isinstance(psrDict[boxId]['geometry']['coordinates'][0], float):
            continue
        elif isinstance(psrDict[boxId]['geometry']['coordinates'][0][0], float):
            parentLng, parentLat = calculate_center(psrDict[boxId]['geometry']['coordinates'][:4])
        else:
            parentLng, parentLat = calculate_center(psrDict[boxId]['geometry']['coordinates'][0][:4])
        vertices = psrDict[boxId]['geometry']['coordinates'][0]
        vertices, inner_points = scale_rectangle(parentLng, parentLat, vertices, innerDict)
        psrDict[boxId]['geometry']['coordinates'][0] = vertices
        for psrId, [idx, coor] in inner_points.items():
            psrDict[psrId]['geometry']['coordinates'][idx] = coor


def update_start_terminal(boxList, rootId, psrDict, psrSet):
    lineDict = {x: [y, y['properties']['connection'].split(',')] for x, y in psrDict.items() if y['geometry']['type'] == "LineString"}
    connections = psrDict[rootId].get('properties', {}).get('connection', '').strip(',').split(',')
    innerDict = {x: [-1 if y[1][0] in connections else 0, y[0]['geometry']['coordinates']] for x, y in lineDict.items() if [z for z in connections if z in y[1]]}
    _, parentLat = calculate_center(psrDict[rootId]['geometry']['coordinates'][0][:4])
    for psrId, [idx, _] in innerDict.items():
        oriCoor = psrDict[psrId]['geometry']['coordinates']
        terminal = [x for x in psrSet if psrSet[x]['parent'] == psrId][0]
        terminal_line = [x for x in psrSet if psrSet[x]['parent'] == terminal][0]
        terminal_idx = 0 if psrDict[terminal_line]['properties']['connection'].startswith(psrDict[terminal]['properties']['connection']) else -1
        if idx == 0:
            psrDict[psrId]['geometry']['coordinates'] = [[oriCoor[-1][0], parentLat - 0.00000819 * 2], oriCoor[-1]]
            psrDict[terminal]['geometry']['coordinates'] = [oriCoor[-1][0], parentLat - 0.00000819 * 2]
            psrDict[terminal_line]['geometry']['coordinates'][terminal_idx] = [oriCoor[-1][0], parentLat - 0.00000819 * 1]
        else:
            psrDict[psrId]['geometry']['coordinates'] = [oriCoor[0], [oriCoor[0][0], parentLat - 0.00000819 * 2]]
            psrDict[terminal]['geometry']['coordinates'] = [oriCoor[0][0], parentLat - 0.00000819 * 2]
            psrDict[terminal_line]['geometry']['coordinates'][terminal_idx] = [oriCoor[0][0], parentLat - 0.00000819 * 1]
        print(terminal)
            
        # print(innerDict, parentLng, parentLat)

def dealLine2(geoData, psrSet, line, parent, lineCount, idx, lon):
    lineInfo = psrDict.get(line)
    parentInfo = psrDict.get(parent)
    subPsr = [x for x in psrSet.keys() if psrSet[x]['parent'] == line][0]
    lineCon = [x for x in lineInfo['properties']['connection'].split(',') if x in parentInfo['properties']['connection']][0]
    if isinstance(parentInfo['geometry']['coordinates'][0], list):
        if isinstance(parentInfo['geometry']['coordinates'][0][0], list):
            parentLng, parentLat = calculate_center(parentInfo['geometry']['coordinates'][0])  # [idxCon]
            parentLat -= 0.00003 if psrDict[parent].get('angle', 180) - 90 > 0 else -0.00003
        else:
            parentLng, parentLat = calculate_center(parentInfo['geometry']['coordinates'])  # [idxCon]
    else:
        parentLng, parentLat = parentInfo['geometry']['coordinates']

    newLng, newLat = calcPoint(parentLng, parentLat, psrDict[parent].get('angle', 180) - 90, 2)
    lineCoor = lineInfo['geometry']['coordinates']
    subLines = [x for x in psrSet.keys() if psrSet[x]['parent'] == subPsr]
    if lineCount > 1:
        lonDiff, idx = (lineCount % 2) / 2 - 0.5, ((idx if idx % 2 == 0 else -idx) // 2)
        newLng2, newLat2 = calcPoint(newLng, newLat, psrDict[parent].get('angle', 180), (idx * lon - lon * lonDiff))
        newLng3, newLat3 = calcPoint(newLng2, newLat2, psrDict[parent].get('angle', 180) - 90, 1 if len(psrSet[subPsr]['set']) <= 1 else 2)
        if lineInfo['properties']['connection'].startswith(lineCon):
            lineInfo['geometry']['coordinates'] = [lineCoor[0], [newLng, newLat], [newLng2, newLat2], lineCoor[-1]]
        else:
            lineInfo['geometry']['coordinates'] = [lineCoor[0], [newLng2, newLat2], [newLng, newLat], lineCoor[-1]]
    else:
        newLng3, newLat3 = calcPoint(parentLng, parentLat, psrDict[parent].get('angle', 180) - 90, 1 if len(subLines) <= 2 else 2)
        if lineInfo['properties']['connection'].startswith(lineCon):
            lineInfo['geometry']['coordinates'] = [lineCoor[0], lineCoor[-1]]
        else:
            lineInfo['geometry']['coordinates'] = [lineCoor[0], lineCoor[-1]]
    con = [psrDict[subPsr]['properties']['connection'], psrDict[subPsr]['geometry']['coordinates']]
    if isinstance(psrDict[subPsr]['geometry']['coordinates'][0], list):
        if isinstance(psrDict[subPsr]['geometry']['coordinates'][0][0], list):
            lngDiff, latDiff = newLng3 - psrDict[subPsr]['geometry']['coordinates'][0][0][0], newLat3 - psrDict[subPsr]['geometry']['coordinates'][0][0][1]
        else:
            lngDiff, latDiff = newLng3 - psrDict[subPsr]['geometry']['coordinates'][0][0], newLat3 - psrDict[subPsr]['geometry']['coordinates'][0][1]
    else:
        lngDiff, latDiff = newLng3 - psrDict[subPsr]['geometry']['coordinates'][0], newLat3 - psrDict[subPsr]['geometry']['coordinates'][1]
    # print(psrDict[subPsr]['geometry']['coordinates'], newLng3, newLat3, '\n')
    movePsr(geoData, subPsr, psrSet[subPsr], con, lngDiff, latDiff)
    psrDict[subPsr].update({'angle': psrDict[parent].get('angle', 180)})
    lon = len(psrSet[subPsr]['set']) // 2 / ((len(subLines) - 1) if len(subLines) > 1 else 1)
    for idx2, line in enumerate(subLines):
        dealLine2(geoData, psrSet, line, subPsr, len(subLines), idx2, lon)


def yijianmeihua(psrId="14000977567062", width=1320, heigth=977, zoom=18.21609899914085, center=[118.94638847999704, 34.56500915405057], mapToken=None):
    global psrDict, LNG, LAT
    gisPath = os.path.join(Config.oriDir, f'{psrId}.json')
    first_data = json.loads(open(gisPath, 'r', encoding="U8").read())
    objType = [320500000, 32600000, 32500000]
    dict_data = json.loads(first_data.get("data", {}).get("geojson", {}))
    list_data = dict_data.get("features", [])
    dict_data.update({'features': list_data})
    open(os.path.join(Config.oriGeo, f'{psrId}.json'), 'w', encoding="U8").write(json.dumps(dict_data, indent=4, ensure_ascii=False))
    LNG, LAT = [x - center[i] for i, x in enumerate(v2Function(mapToken, ','.join([str(y) for y in center])))]
    print('LNGLAT: ', LNG, LAT)
    psrDict = {x['properties']['psrId']: x for x in list_data}
    rootId = [x['properties']['psrId'] for x in list_data if x['properties']['objType'] in [30000005, 32500000, 32300000]][0]
    print(rootId)
    boxList, psrSet = output2(list_data, objType, rootId)
    psrList = {psrSet[psrSet[x]['parent']]['parent']: psrSet[psrSet[psrSet[x]['parent']]['parent']] for x in boxList}
    update_junction_box(boxList, rootId, psrDict)  # 所有分支箱缩放至2 * 3
    res = output1(list_data, psrId, center, mapToken)
    if res:
        return res
    buildDict = getBuilldingCoordinat(f"{Config.Building}/{psrId}.png", psrId, zoom, [center[0], center[1]])
    # buildDict = calcLngLat(buildDict, zoom, center, width, heigth)
    
    psrList2 = method1(psrSet, rootId, list_data, psrList, buildDict)
    psrList.update(psrList2)  # 将非分支箱的电缆头也添加到分支箱列表中做一样的处理
    for psr, item in psrList.items():
        con = [(x['properties']['connection'], x['geometry']['coordinates']) for x in list_data if x['properties']['psrId'] == psr][0]
        (lng, lat), angle = calcDiff(buildDict, con[1])
        psrDict[psr].update({'angle': angle})
        newlng, newlat = calcPoint(lng, lat, angle + 90)
        movePsr(list_data, psr, item, con, newlng, newlat)
    logger.info({x: y for x, y in buildDict.items() if len(y) >= 4})

    # 分支箱的下游设备
    for psr, item in psrList.items():
        subLines = [x for x in psrSet.keys() if psrSet[x]['parent'] == psr]
        lon = 1  # len(item['set'])//4/((len(subLines) - 1) if len(subLines) > 1 else 1)
        for idx, line in enumerate(subLines):
            dealLine(list_data, psrSet, line, psr, len(subLines), idx, lon, psrList)

    # 处理所有的接入点和表箱按照梳子形状摆放
    # JpsrList = [x['properties']['psrId'] for x in list_data if x['properties'].get('psrType', '') in ['3218000']]
    # JpsrDict = {psrSet[psrSet[x]['parent']]['parent']: psrSet[psrSet[psrSet[x]['parent']]['parent']] for x in JpsrList if len(psrSet[x]['set']) > 0}
    # JxianList = [psrSet[x]['parent'] for x in JpsrList if len(psrSet[x]['set']) == 0]
    # for psr, item in JpsrDict.items():
    #     subLines = [x for x in psrSet.keys() if psrSet[x]['parent'] == psr and x not in JxianList]
    #     lon = len(item['set'])//4/((len(subLines) - 1) if len(subLines) > 1 else 1)
    #     for idx, line in enumerate(subLines):
    #         dealLine2(list_data, psrSet, line, psr, len(subLines), idx, lon)

    startPoint, oneStep = '', None
    for psr, item in psrList.items():
        dlInfo = psrDict.get(psrSet[psr]['parent'])
        start = startPoint if startPoint else f"{dlInfo['geometry']['coordinates'][0][0] + LNG}, {dlInfo['geometry']['coordinates'][0][1] + LAT}"
        end = f"{dlInfo['geometry']['coordinates'][-1][0] + LNG}, {dlInfo['geometry']['coordinates'][-1][1] + LAT}"
        reqRes = walking(start, end, start, mapToken)
        if startPoint:
            reqRes[2] = [[x - LNG, y - LAT] for x, y in oneStep + reqRes[2][1:]]
        else:
            reqRes[2] = [[x - LNG, y - LAT] for x, y in reqRes[2]]
        reqRes[2].insert(0, dlInfo['geometry']['coordinates'][0])
        reqRes[2].append(dlInfo['geometry']['coordinates'][-1])
        newPaths = reqRes[2]
        newPaths = simplify_path(newPaths)  # 剪掉绕路部分
        if len(newPaths) <= 5:
            n = len(newPaths)
            for i in range(6 - n):
                newPaths.insert(0, [newPaths[0][0] - 0.0000001 * (i + 1), newPaths[0][1]])
        dlInfo['geometry']['coordinates'] = newPaths
    # update_start_terminal(boxList, rootId, psrDict, psrSet)  # 更新配电室或者分支箱下面的电缆终端头
    dict_data.update({'features': list_data})
    open(os.path.join(Config.Geo1, f'{psrId}.json'), 'w', encoding="U8").write(json.dumps(dict_data, indent=4, ensure_ascii=False))
    return os.path.join(Config.Geo1, f'{psrId}.json')


def v2Function(mapToken, coor):
    url = f"{Config.MAPURL}/geoconv/v2"  # http://map-jx.sgcc.com.cn/geoconv/v2  # "https://map.sgcc.com.cn/geoconv/v2"
    head = {'Authorization': mapToken} 
    data = {'coords': coor, 'from': 1}
    res = requests.post(url, data=data, headers=head, proxies=Config.proxy, timeout=10).json()
    print({'Authorization': mapToken}, data, res )
    return list(res['value'][0].values())

def walking(start, end, erCi=False, mapToken=None):
    url = f"{Config.MAPURL}/rest/v1/direction/walking?origin={start}&destination={end}"
    head = {'Authorization': mapToken}
    for _ in range(10):
        try:
            res = requests.get(url, proxies=Config.proxy, headers=head, timeout=10).json()
            break
        except Exception as e:
            pass
    else:
        raise e
    steps = res['route']['paths'][0]['steps']
    if len(steps) <= 1 and not erCi:
        return False
    startPoint = steps[0]['polyline'].split(';')[-1]
    oneStep = [[float(y) for y in x.split(',')] for x in steps[0]['polyline'].split(';')]
    fullStep = [[float(y) for y in x.split(',')] for x in ';'.join([z['polyline'] for z in steps]).split(';')]
    return [startPoint, oneStep, fullStep]


def scale_rectangle(center_lon, center_lat, vertices, inner_points):
    vertices_local = []
    for lon, lat in vertices:
        dx = (lon - center_lon) * 111319 * math.cos(math.radians(center_lat))
        dy = (lat - center_lat) * 111319
        vertices_local.append((dx, dy))
    xs = [dx for dx, _ in vertices_local]
    ys = [dy for _, dy in vertices_local]
    original_width = max(xs) - min(xs)
    original_height = max(ys) - min(ys)
    target_width, target_height = 3.0, 2.0
    sx = target_width / original_width
    sy = target_height / original_height

    def scale_point(lon, lat):
        dx = (lon - center_lon) * 111319 * math.cos(math.radians(center_lat))
        dy = (lat - center_lat) * 111319
        scaled_dx = dx * sx
        scaled_dy = dy * sy
        new_lon = center_lon + (scaled_dx / (111319 * math.cos(math.radians(center_lat))))
        new_lat = center_lat + (scaled_dy / 111319)
        return [new_lon, new_lat]
    scaled_vertices = [scale_point(lon, lat) for lon, lat in vertices]
    scaled_inner = {psrId: [idx, scale_point(coor[idx][0], coor[idx][1])] for psrId, [idx, coor] in inner_points.items()}
    return scaled_vertices, scaled_inner


if __name__ == "__main__":
    center_test = [118.72848606456932, 32.320702215513876]
    mapToken_test = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJJc3N1YW5jZSI6IlkiLCJhcHBJZCI6Ijk0YmZiYmU1YWZlYTM3MzVhZDVjYzA2ODlkNGE2YTM1IiwiY2xpZW50SXAiOiIyMi40Ni42NS4xNTAiLCJleHAiOjE3NDgzOTgwNzcsImlhdCI6MTc0ODM5NDQ3NywiaXNzIjoid3d3LmFlZ2lzLmNvbSIsImp0aSI6IlZFUkFZQk9CR1QiLCJzY29wZXMiOjEsInN1YiI6IjY0MmFkOWMwYzBhMjMyYzk4OGQyOTYyMTQ4YjRmYzE2Iiwic3ViVHlwZSI6ImFwcGtleSIsInRva2VuVFRMIjozNjAwMDAwLCJ1c2VyTmFtZSI6Inh1Y29uZ3d1In0.5_L22r-rUGs3hvWpZ_P7b5yA2rzomsPnV7U2zWby3sM'
    zoom_test = 18
    width_test, height_test = 1320, 977
    psrid_test = "90fe080c21ff808081608043e3016090fdd6784fdc"
    yijianmeihua(psrId=psrid_test, width=width_test, heigth=height_test, zoom=zoom_test, center=center_test, mapToken=mapToken_test)
    pass
