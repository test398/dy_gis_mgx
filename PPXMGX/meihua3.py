""" 有坐标文件时使用这个  """

import math
import json
import os

import requests

from utils.config import Config
LNG, LAT = 0, 0

def output1(list_data, psrId, center, mapToken):
    global LNG, LAT
    # if not list_data:
    #     first_data = json.loads(open(r"C:\Users\Administrator\Desktop\detail.json", 'r', encoding="U8").read())
    #     dict_data = first_data.get("data", {}).get("geojson", {})
    #     list_data = dict_data.get("features", [])
    for x in list_data:
        if x['properties'].get('psrType') in ["dywlgt", '0110']:
            break
    else:
        return False  # 不是柱上变压器，不用此方法处理
    
    dic1 = {x['properties']['connection']: x['properties']['psrId'] for x in list_data if 'connection' in x['properties']}  # con -- id
    dic2 = {x['properties']['psrId']: x for x in list_data if 'connection' in x['properties']}  # id -- con
    bxDict = {x['properties']['psrId']: x for x in list_data if x['properties']['objType'] == 410300000}  # con -- id
    coorJson = os.path.join(Config.Coors, f'{psrId}.json')
    print(coorJson)
    if not os.path.exists(coorJson):
        return "坐标JSON文件不存在"
    coorDict = json.loads(open(coorJson, 'r', encoding="U8").read())
    print('center:  ', center)
    LNG, LAT = [x - center[i] for i, x in enumerate(v2Function(mapToken, ','.join([str(y) for y in center])))]
    for psrid, psr in bxDict.items():
        bxXian = [y for x, y in dic1.items() if psr['properties']['connection'] in x and psr['properties']['connection'] != x]
        bxXianCoor = dic2.get(bxXian[0], {}).get('geometry', {}).get('coordinates', [])
        if len(bxXian) != 1 or not bxXianCoor:
            continue
        bxCoor = psr['geometry']['coordinates']
        idx = 0 if bxXianCoor[0] == bxCoor else -1
        bxNewCoor = calcNewCoor(coorDict, bxCoor, psrid)
        if not bxNewCoor:
            continue
        psr['geometry']['coordinates'] = bxNewCoor
        dic2.get(bxXian[0], {}).get('geometry', {}).get('coordinates', [])[idx] = bxNewCoor
        tempXian = dic2.get(bxXian[0], {}).get('geometry', {}).get('coordinates', [])
        dic2.get(bxXian[0], {}).get('geometry', {}).get('coordinates', [])[:] = [tempXian[0], tempXian[-1]]
        start, end = f"{tempXian[0][0] + LNG}, {tempXian[0][1] + LAT}", f"{tempXian[-1][0] + LNG}, {tempXian[-1][1] + LAT}"
        reqRes = walking(start, end, start, mapToken)
        reqRes[2] = [[x - LNG, y - LAT] for x, y in reqRes[2]]
        reqRes[2].insert(0, tempXian[0])
        reqRes[2].append(tempXian[-1])
        dic2.get(bxXian[0], {}).get('geometry', {}).get('coordinates', [])[:] = reqRes[2]

        # break
    # open(r"C:\Users\Administrator\Desktop\detail2.json", 'w', encoding="U8").write(json.dumps({'features': list_data}, indent=4, ensure_ascii=False))
    open(os.path.join(Config.Geo1, f'{psrId}.json'), 'w', encoding="U8").write(json.dumps({'features': list_data}, indent=4, ensure_ascii=False))
    return os.path.join(Config.Geo1, f'{psrId}.json')


def v2Function(mapToken, coor):
    url = f"{Config.MAPURL}/geoconv/v2"  # http://map-jx.sgcc.com.cn/geoconv/v2  # "https://map.sgcc.com.cn/geoconv/v2"
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
    output1('')
