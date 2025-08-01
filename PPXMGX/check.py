from collections import defaultdict
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import logging
import math
import os
import shutil
import sys
from urllib import parse
import openpyxl
from tqdm import tqdm
import requests
import csv
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
from threading import Thread
import time
import traceback
from typing import Dict
from urllib import parse
import openpyxl
import requests
from seleniumwire import webdriver
from tqdm import tqdm



import webview
# from webview.platforms.cef import settings, command_line_switches
from selenium.webdriver.support.wait import WebDriverWait
from openpyxl.worksheet.worksheet import Worksheet
# 江西 http://25.60.239.237:31002 北京  http://22.32.128.1:80
BASEURL = "http://pms.pro.js.sgcc.com.cn:32100"  # "http://25.214.205.81"  # http://pms.pro.js.sgcc.com.cn:32100/  http://25.55.39.199:30006  http://25.55.39.199:30006  重庆 http://pms3.cq.sgcc.com.cn
BASEURL2 = "http://pms.pro.js.sgcc.com.cn:32100"
QUERYURI = "querydevice"  # astquerydevice
PSRIDLIST = []


def checkFlyCount(userJson, user):
    """ 第四步计算飞点飞线的数量, 并生成json """
    logDir = f'{os.path.dirname(os.path.dirname(userJson))}/GIS{os.path.basename(userJson)[:-5]}'
    flyDir = os.path.join(os.path.dirname(logDir), 'flyDir')
    os.makedirs(flyDir, exist_ok=True)
    doneDict = defaultdict(int)
    for x in os.listdir(logDir):
        if not os.path.isdir(os.path.join(logDir, x)):
            continue
        for y in os.listdir(os.path.join(logDir, x)):
            doneDict[y.split('_')[-1][:-5]] = os.path.join(logDir, x, y)
    try:
        dic = json.loads(open(userJson, encoding="U8").read())
    except Exception:
        return
    flyDict, mount = defaultdict(list), 0
    for item in tqdm(dic['resultValue']['items'], desc='计算飞点飞线'):
        mount += 1
        if doneDict.get(item['PSR_ID']) and item['PSR_ID'] not in PSRIDLIST:
            count, _ = calcuFlyCount(doneDict.get(item['PSR_ID']), user)
            PSRIDLIST.append(item['PSR_ID'])
            if count > 0:
                flyDict[item['PSR_ID']] = [item['MAINT_GROUP'], item['NAME'], count, item['MAINT_ORG']]
        if mount > 3000:
            break
    open(f'{logDir}/{os.path.basename(userJson)[:-5]}_{user}fly.json', 'w', encoding="U8").write(json.dumps(flyDict, indent=4, ensure_ascii=False))
    if len(flyDict) > 0:
        shutil.copy(f'{logDir}/{os.path.basename(userJson)[:-5]}_{user}fly.json', os.path.join(flyDir, f'{os.path.basename(userJson)[:-5]}_{user}fly.json'))
    return len(flyDict)
    
def calcuFlyCount(jsonPath, user):
    """ 计算飞点飞线的线段 """
    try:
        oriDic = json.loads(open(jsonPath, encoding="U8").read())
    except Exception:
        return 0, ''
    if oriDic['message'] != "success":
        return 0, ''
    dic = json.loads(oriDic['result']['content'])
    lineDict, pointDict = defaultdict(), defaultdict()
    for feature in dic['features']:
        if feature['geometry']['type'] == 'LineString':
            if len(feature['properties']['connection'].split(',')) != 2 or 'psrId' not in feature['properties']:
                continue
            con1, con2 = feature['properties']['connection'].split(',')
            district = feature['properties']['district']
            coor1, coor2 = feature['geometry']['coordinates'][0], feature['geometry']['coordinates'][-1]
            lineDict[feature['properties']['psrId']] = {con1: [coor1, 1, district, con1], con2: [coor2, 2, district, con2]}
        if feature['geometry']['type'] == 'Point':
            if not feature['properties'].get('connection'):
                continue
            con = feature['properties']['connection']
            coor = feature['geometry']['coordinates']
            district = feature['properties']['district']
            pointDict[con] = [coor, district]
    count = 0
    for k, v in lineDict.items():
        # if pointDict.get(v[2][3]) is None:
        #     continue
        # point = pointDict.get(v[2][3])
        # if len(v[2][3]) <= len(v[1][3]) and v[2][3] < v[1][3] and (int(v[1][0][0] * 100000) != int(point[0][0] * 100000) or int(v[1][0][1] * 100000) != int(point[0][1] * 100000)):
        #     print(k, v[1][0], point[0])
        #     count += 1
        for con, coor in v.items():
            if pointDict.get(con) is None:
                continue
            # if coor[2] == pointDict.get(con)[1] and coor[1] == 1:
            #     continue
            if (int(coor[0][0] * 100000) != int(pointDict.get(con)[0][0] * 100000) or int(coor[0][1] * 100000) != int(pointDict.get(con)[0][1] * 100000)):
                print(k, coor, pointDict.get(con))
                count += 1
    return count, ''


def method9():
    fenDir = r"D:\生产验收文件夹\江苏\ppxTemp\fenDir2"
    count = 0
    for jsonName in os.listdir(fenDir):
        jsonPath = os.path.join(fenDir, jsonName)
        count += checkFlyCount(jsonPath, '运检')
        print(count)
        break

def method10():
    jsonPath = r"D:\生产验收文件夹\江苏\ppxTemp\GIS国网南京供电公司_供电服务一中心（栖霞分部）\一中心配电运检班\62632a95-123e-17bc-e053-0a8657155d6el4all2.json"
    oriDic = json.loads(open(jsonPath, encoding="U8").read())
    dic = json.loads(oriDic['result']['content'])
    open(r"C:\Users\Administrator\Desktop\temp.json", 'w', encoding="U8").write(json.dumps(dic, indent=4, ensure_ascii=False))

if __name__ == "__main__":
    # method9()  # 计算飞线台区
    count = calcuFlyCount(r"D:\生产验收文件夹\江苏\ppxTemp\GIS国网南京供电公司_供电服务一中心（栖霞分部）\一中心配电运检班\62632a95-123e-17bc-e053-0a8657155d6el4all2.json", '')
    print(count)
    method10()

