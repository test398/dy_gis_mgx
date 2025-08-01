from collections import defaultdict
import math
import json
import os

import requests

from utils.config import Config
LNG, LAT = 0, 0

def output1(list_data, psrId, center, mapToken):
    global LNG, LAT
    for x in list_data:
        if x['properties'].get('psrType') in ["dywlgt", '0110']:
            break
    else:
        return False  # 不是柱上变压器，不用此方法处理
    
    Jdict, connDict, JconDict = defaultdict(dict), defaultdict(list), defaultdict(str)
    for info in list_data:
        if info['properties'].get('connection', ''):
            connDict[info['properties']['connection']] = [info['properties']['id'], info]
        if info['geometry']['type'] == 'Point' and info.get('properties', {}).get('psrType', '') == '3218000':
            Jdict[info['properties']['id']] = {'info': info, 'connection': info['properties']['connection'], 'coordinates': info['geometry']['coordinates'], 'child': [], 'parent': {}}
            JconDict[info['properties']['connection']] = info['properties']['id']

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
                if len(connDict.get(connections[idx - 1], [])) < 2:
                    continue
                conn_info = connDict.get(connections[idx - 1], [])
                if len(conn_info) < 2 or conn_info[1] is None:
                    continue
                if conn_info[1]['properties'].get('psrType') == '3112':
                    tempDict = {'lineId': info['properties']['id'], 'lineinfo': info, 'lineidx': lineidx, 'info': conn_info[1]}
                    Jdict[key]['child'].append(tempDict)
                else:
                    tempDict = {'lineId': info['properties']['id'], 'lineinfo': info, 'lineidx': lineidx, 'info': conn_info[1]}
                    Jdict[key]['parent'] = tempDict
    
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
                    lineCoor = item['parent']['lineinfo']['geometry']['coordinates']
                    if item['parent']['lineidx'] == 0:
                        parentCoor = [Jcoor, lineCoor[-1]]
                        item['parent']['lineinfo']['geometry']['coordinates'] = parentCoor
                    else:
                        parentCoor = [lineCoor[0], Jcoor]
                        item['parent']['lineinfo']['geometry']['coordinates'] = parentCoor
                    
                    if child['lineidx'] == -1:
                        newCoor = [[val_lng, val_lat + det * 2], Jcoor]
                    else:
                        newCoor = [Jcoor, [val_lng, val_lat + det * 2]]
                    child['lineinfo']['geometry']['coordinates'] = newCoor
                    break
            else:
                continue
            break
    for info in list_data:
        if info['geometry']['type'] == 'LineString' and info.get('properties', {}).get('psrType', '') == '3201':
            midCoor = [[info['geometry']['coordinates'][0][0] + 0.0000001 * (x + 1), info['geometry']['coordinates'][0][1]] for x in range(5)]
            info['geometry']['coordinates'] = [info['geometry']['coordinates'][0]] + midCoor + [info['geometry']['coordinates'][-1]]
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
    output1([], 'test', [0, 0], 'test_token')
