from collections import defaultdict
import math
import os
import json
import execjs
import requests

from utils.config import Config
from utils.cvPng import getBuilldingCoordinat, point
psrDict, LNG, LAT = {}, 0, 0

def output2(list_data, objType, rootId):
    psrInt, nodeList = defaultdict(int), []
    psrInt[rootId] += 1
    dic1 = {x['properties']['connection']: x['properties']['psrId'] for x in list_data}  # con -- id
    dic2 = {x['properties']['psrId']: x['properties']['connection'] for x in list_data}  # id -- con

    def find_connect_chain(psr, node, isPoint):
        cons = [x for x in dic2[psr].split(',') if x]
        for con in cons:
            psrs = [y for x, y in dic1.items() if con in x and y != psr and not psrInt[y]]
            if not psrs:
                continue
            if node in nodeList:
                nodeList.pop(nodeList.index(node))
            for psr1 in psrs:
                conCount = len([x for x in dic2[psr1].split(',') if x])
                if not isPoint and conCount > 1:
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
    return {psr: psrSet[psr] for psr in objTypes if psr in psrSet}, psrSet


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
                    geometry['coordinates'][idx] = [coor[0] + lng, coor[1] + lat]
        if psrId == parent:
            if str(oriItem['properties']['connection']).startswith(con[0]):
                geometry['coordinates'][0] = [coor[0][0] + lng, coor[0][1] + lat]
            else:
                geometry['coordinates'][-1] = [coor[-1][0] + lng, coor[-1][1] + lat]


def calcLngLat(buildDict, zoom, center, width, heigth):
    for key, val in buildDict.items():
        lng, lat = point(val[1][0], val[1][1], zoom, center, width, heigth)
        buildDict[key].append([lng, lat])
    return buildDict


def calcDiff(buildDict, coor):
    minDistant, k, diff = 9999, None, [0, 0]
    for key, val in buildDict.items():
        if len(buildDict[key]) >= 5:
            continue
        if (val[3][0] - coor[0]) ** 2 + (val[3][1] - coor[1]) ** 2 < minDistant:
            k, diff = key, [val[3][0] - coor[0] - LNG, val[3][1] - coor[1] - LAT]
            minDistant = (val[3][0] - coor[0]) ** 2 + (val[3][1] - coor[1]) ** 2
    if k:
        buildDict[k].append(diff)
    return diff, buildDict.get(k, [0, 0, 180])[2]


def calcPoint(lng, lat, angle, distance=8):
    radius = 6378137.0
    angleRad = math.radians(angle)
    deltaLat = (distance / radius) * (180 / math.pi)
    deltaLng = (distance / radius) * (180 / math.pi) / math.cos(math.radians(lat))
    lat = lat + deltaLat * math.cos(angleRad + math.pi / 2)
    lng = lng + deltaLng * math.sin(angleRad + math.pi / 2)
    return [lng, lat]

def dealLine(geoData, psrSet, line, parent, lineCount, idx, lon):
    lineInfo = psrDict.get(line)
    parentInfo = psrDict.get(parent)
    subPsr = [x for x in psrSet.keys() if psrSet[x]['parent'] == line][0]
    parentLng, parentLat = parentInfo['geometry']['coordinates']
    newLng, newLat = calcPoint(parentLng, parentLat, psrDict[parent].get('angle', 180) - 90, 1)
    lineCoor = lineInfo['geometry']['coordinates']
    if lineCount > 1:
        lonDiff, idx = (lineCount % 2) / 2 - 0.5, ((idx if idx % 2 == 0 else -idx) // 2)
        newLng2, newLat2 = calcPoint(newLng, newLat, psrDict[parent].get('angle', 180), (idx * lon - lon * lonDiff))
        newLng3, newLat3 = calcPoint(newLng2, newLat2, psrDict[parent].get('angle', 180) - 90, 1)
        if lineInfo['properties']['connection'].startswith(parentInfo['properties']['connection']):
            lineInfo['geometry']['coordinates'] = [lineCoor[0], [newLng, newLat], [newLng2, newLat2], lineCoor[-1]]
        else:
            lineInfo['geometry']['coordinates'] = [lineCoor[0], [newLng2, newLat2], [newLng, newLat], lineCoor[-1]]
    else:
        newLng3, newLat3 = newLng, newLat
        if lineInfo['properties']['connection'].startswith(parentInfo['properties']['connection']):
            lineInfo['geometry']['coordinates'] = [lineCoor[0], lineCoor[-1]]
        else:
            lineInfo['geometry']['coordinates'] = [lineCoor[0], lineCoor[-1]]
    con = [psrDict[subPsr]['properties']['connection'], psrDict[subPsr]['geometry']['coordinates']]
    lngDiff, latDiff = newLng3 - psrDict[subPsr]['geometry']['coordinates'][0], newLat3 - psrDict[subPsr]['geometry']['coordinates'][1]
    # print(psrDict[subPsr]['geometry']['coordinates'], newLng3, newLat3, '\n')
    movePsr(geoData, subPsr, psrSet[subPsr], con, lngDiff, latDiff)
    psrDict[subPsr].update({'angle': psrDict[parent].get('angle', 180)})
    subLines = [x for x in psrSet.keys() if psrSet[x]['parent'] == subPsr]
    lon = len(psrSet[subPsr]['set']) // 4 / ((len(subLines) - 1) if len(subLines) > 1 else 1)
    for idx2, line in enumerate(subLines):
        dealLine(geoData, psrSet, line, subPsr, len(subLines), idx2, lon)
        # break
    # psrDict[subPsr]['geometry']['coordinates'] = [psrDict[subPsr]['geometry']['coordinates'][0] + lngDiff, psrDict[subPsr]['geometry']['coordinates'][1] + latDiff]
    # print(subPsr, con, psrSet[subPsr], lngDiff, latDiff, psrDict[subPsr]['geometry']['coordinates'])

def method1(psrSet, rootId, list_data, psrList):
    ''' 处理不带分支箱的设备 '''
    outLines = [x for x in psrSet.keys() if psrSet[x]['parent'] == rootId]
    rootInfo = psrDict[rootId]
    for line in outLines:
        subPsr = [x for x in psrSet.keys() if psrSet[x]['parent'] == line][0]
        subCon = psrDict[subPsr]['properties']['connection']
        subCoor = psrDict[subPsr]['geometry']['coordinates']
        con = psrDict[line]['properties']['connection'].split(',')
        coor = psrDict[line]['geometry']['coordinates']
        if con[0] in rootInfo['properties']['connection']:
            tarCoor = [coor[0][0], coor[0][1] - 0.000025]
        else:
            tarCoor = [coor[-1][0], coor[-1][1] - 0.000025]
        lngDiff, latDiff = tarCoor[0] - subCoor[0], tarCoor[1] - subCoor[1]
        movePsr(list_data, subPsr, psrSet[subPsr], [subCon, psrDict[subPsr]['geometry']['coordinates']], lngDiff, latDiff)
        if [x for x in psrList if x in psrSet[subPsr]['set']]:
            continue
        subLines = [x for x in psrSet.keys() if psrSet[x]['parent'] == subPsr]
        for idx, line in enumerate(subLines):
            dealLine(list_data, psrSet, line, subPsr, len(subLines), idx, 2)
        # print(psrDict[line], con)
        # break


def yijianmeihua(psrId="14000598116387", width=1320, heigth=977, zoom=17.09232830938175, center=[118.94916956937436, 34.57405950742806], mapToken=None):
    global psrDict, LNG, LAT
    LNG, LAT = [x - center[i] for i, x in enumerate(v2Function(mapToken, ','.join([str(y) for y in center])))]
    print('LNGLAT: ', LNG, LAT)
    gisDir = "D:/MGXGIS" if os.path.exists("D:/") else "C:/MGXGIS"
    os.makedirs(gisDir, exist_ok=True)
    oriDir = os.path.join(gisDir, 'oriGis')
    gisPath = os.path.join(oriDir, f'{psrId}.json')
    first_data = json.loads(open(gisPath, 'r', encoding="U8").read())
    objType = [320500000, 32600000]
    dict_data = json.loads(first_data.get("data", {}).get("geojson", {}))
    list_data = dict_data.get("features", [])
    psrDict = {x['properties']['psrId']: x for x in list_data}
    rootId = [x['properties']['psrId'] for x in list_data if x['properties']['objType'] in [30000005, 32500000]][0]
    print(rootId)
    psrList, psrSet = output2(list_data, objType, rootId)
    psrList = {psrSet[psrSet[x]['parent']]['parent']: psrSet[psrSet[psrSet[x]['parent']]['parent']] for x in psrList}
    method1(psrSet, rootId, list_data, psrList)
    buildDict = getBuilldingCoordinat()
    # width, heigth, zoom, center = 1320, 977, 18.193051929382342, [118.762293771661, 34.38361998437705]
    buildDict = calcLngLat(buildDict, zoom, center, width, heigth)
    for psr, item in psrList.items():
        con = [(x['properties']['connection'], x['geometry']['coordinates']) for x in list_data if x['properties']['psrId'] == psr][0]
        (lng, lat), angle = calcDiff(buildDict, con[1])
        psrDict[psr].update({'angle': angle})
        newlng, newlat = calcPoint(lng, lat, angle + 90)
        movePsr(list_data, psr, item, con, newlng, newlat)

    # 分支箱的下游设备
    for psr, item in psrList.items():
        subLines = [x for x in psrSet.keys() if psrSet[x]['parent'] == psr]
        lon = len(item['set'])//4/((len(subLines) - 1) if len(subLines) > 1 else 1)
        for idx, line in enumerate(subLines):
            dealLine(list_data, psrSet, line, psr, len(subLines), idx, lon)

    startPoint, oneStep = '', None
    for psr, item in psrList.items():
        dlInfo = psrDict.get(psrSet[psr]['parent'])
        start = f"{dlInfo['geometry']['coordinates'][0][0] + LNG}, {dlInfo['geometry']['coordinates'][0][1] + LAT}"
        end = f"{dlInfo['geometry']['coordinates'][-1][0] + LNG}, {dlInfo['geometry']['coordinates'][-1][1] + LAT}"
        reqRes = walking(start, end, mapToken=mapToken)
        if not reqRes:
            continue
        startPoint, oneStep = reqRes[0], reqRes[1]
        reqRes[2] = [[x - LNG, y - LAT] for x, y in reqRes[2]]
        reqRes[2].insert(0, dlInfo['geometry']['coordinates'][0])
        reqRes[2].append(dlInfo['geometry']['coordinates'][-1])
        dlInfo['geometry']['coordinates'] = reqRes[2]
        break

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
        dlInfo['geometry']['coordinates'] = reqRes[2]
    dict_data.update({'features': list_data})
    open(os.path.join(Config.Geo1, f'{psrId}.json'), 'w', encoding="U8").write(json.dumps(dict_data, indent=4, ensure_ascii=False))


def v2Function(mapToken, coor):
    url = "https://map.sgcc.com.cn/geoconv/v2"
    head = {'Authorization': mapToken}
    data = {'coords': coor, 'from': 1}
    res = requests.post(url, data=data, headers=head, timeout=10).json()
    return list(res['value'][0].values())

def walking(start, end, erCi=False, mapToken=None):
    url = f"https://map.sgcc.com.cn/rest/v1/direction/walking?origin={start}&destination={end}"
    head = {'Authorization': mapToken}
    res = requests.get(url, headers=head).json()
    steps = res['route']['paths'][0]['steps']
    if len(steps) <= 1 and not erCi:
        return False
    startPoint = steps[0]['polyline'].split(';')[-1]
    oneStep = [[float(y) for y in x.split(',')] for x in steps[0]['polyline'].split(';')]
    fullStep = [[float(y) for y in x.split(',')] for x in ';'.join([z['polyline'] for z in steps]).split(';')]
    return [startPoint, oneStep, fullStep]


def loginMap():
    JSCODE = '''
        tt = function(t, e) {
            if (!o)
                return null;
            var i = o.enc.Utf8.parse(e);
            return a.decrypt({
                ciphertext: o.enc.Base64.parse(t)
            }, i, {
                mode: o.mode.ECB,
                padding: o.pad.Pkcs7
            }).toString(o.enc.Utf8)
        }
        getToken = function(i){return tt(i.substring(64), 'fa8c9b3de1c468bb');}
    '''
    url = "https://map.sgcc.com.cn/authentication/v2/login/sysLogin"
    head = {
        'Referer': 'https://map.sgcc.com.cn/products/js-sdk/v3/example.html?t=capability',
    }
    data = {
        'key': '6c79050a2980311899dce77493288b92',
        'enc': 'c4a07d197f793c481eb8618c66da5996202e8b21a20613d7a984786c9e7f5e02CimLBqJlibXzeN4pEpsACqqFXEXYZ5t9In8E1S3qzpVyADGkbTc5qhGTT5BJ0fW0qAAALgtMZizsVJ36PkmVfkL+jCdhLLMeNvGJq//9K8laFwlGIll5eeCG5NnigAQO'
    }
    res = requests.post(url, data=data, headers=head, timeout=10)
    token = execjs.compile(JSCODE).call('getToken', res.json()['resultValue'])
    print(token)


def test222():
    jsonPath = r"d:\生产验收文件夹\河南\三次检测\ppxTemp\flyDir\国网河南省电力公司驻马店供电公司_城区供电公司_营销url.json"
    dic = json.loads(open(jsonPath, 'r', encoding="U8").read())
    resDict = defaultdict(dict)
    for key, item in dic.items():
        if item[6] == "0302":
            resDict.update({key: [item[1], item[5], item[6], item[7]]})

    open(r"C:\Users\Administrator\Desktop\待治理河南.json", 'w', encoding="U8").write(json.dumps(resDict, indent=4, ensure_ascii=False))


if __name__ == "__main__":
    # yijianmeihua(mapToken='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJJc3N1YW5jZSI6IlkiLCJhcHBJZCI6IjhkYzU0OThiZDcxMDMzYTA5OTJlNGQ3NzhhMDZlN2UzIiwiY2xpZW50SXAiOiIyMi40Ni42NS4xNTAiLCJleHAiOjE3MzcwMzE0MDIsImlhdCI6MTczNzAyNzgwMiwiaXNzIjoid3d3LmFlZ2lzLmNvbSIsImp0aSI6IlFMSUZOUlZNVUgiLCJzY29wZXMiOjEsInN1YiI6IjZjNzkwNTBhMjk4MDMxMTg5OWRjZTc3NDkzMjg4YjkyIiwic3ViVHlwZSI6ImFwcGtleSIsInRva2VuVFRMIjozNjAwMDAwLCJ1c2VyTmFtZSI6IndqdyJ9.Pfu5InH7iiqztoax3-6yNRwDU_pwu7vbG2Kvv2d4CPM')
    # v2Function('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJJc3N1YW5jZSI6IlkiLCJhcHBJZCI6IjhkYzU0OThiZDcxMDMzYTA5OTJlNGQ3NzhhMDZlN2UzIiwiY2xpZW50SXAiOiIyMi40Ni42NS4xNTAiLCJleHAiOjE3MzcwMzE0MDIsImlhdCI6MTczNzAyNzgwMiwiaXNzIjoid3d3LmFlZ2lzLmNvbSIsImp0aSI6IlFMSUZOUlZNVUgiLCJzY29wZXMiOjEsInN1YiI6IjZjNzkwNTBhMjk4MDMxMTg5OWRjZTc3NDkzMjg4YjkyIiwic3ViVHlwZSI6ImFwcGtleSIsInRva2VuVFRMIjozNjAwMDAwLCJ1c2VyTmFtZSI6IndqdyJ9.Pfu5InH7iiqztoax3-6yNRwDU_pwu7vbG2Kvv2d4CPM')
    # walking(start="116.306007, 39.879771", end="116.427281, 39.903719")
    # loginMap()
    test222()
    pass