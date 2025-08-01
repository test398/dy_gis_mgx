#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
账号密码：
wangr8
wr3185*!!

'''

import os
import getpass
import platform
import sys

from websockets import WebSocketServerProtocol

from utils.regedit import queryArea
from utils.tools import getRandomPort
from utils.area import AREA

RPC: WebSocketServerProtocol = None  # 


class Config:
    '''配置文件'''

    ##
    # 程序基础配置信息
    ##
    appName = f'GIS美观性 v1.0.0.0'  # 应用名称
    appNameEN = 'ppx'    # 应用名称-英文（用于生成缓存文件夹，必须是英文）
    appVersion = "V4.2.2"  # 应用版本号
    appDeveloper = "PanGao"  # 应用开发者
    appBlogs = "https://blog.pangao.vip"  # 个人博客
    appPackage = 'vip.pangao'    # 应用包名，用于在本地电脑生成 vip.pangao.ppx 唯一文件夹
    appUpdateUrl = 'https://api.github.com/repos/pangao1990/ppx/releases/latest'    # 获取程序更新信息 https://api.github.com/repos/pangao1990/ppx/releases/latest
    appISSID = 'F35003AB-441A-C0A6-4527-937E6A02F789'    # Inno Setup 打包唯一编号。在执行 pnpm run init 之前，请设置为空，程序会自动生成唯一编号，生成后请勿修改！！！

    ##
    # 系统配置信息（不需要修改，可以自动获取）
    ##
    appSystem = platform.system()    # 本机系统类型
    appIsMacOS = appSystem == 'Darwin'    # 是否为macOS系统
    codeDir = sys.path[0].replace('base_library.zip', '')    # 代码根目录
    appDir = codeDir.replace(appName+'.app/Contents/MacOS/', '')    # 程序所在绝对目录
    staticDir = os.path.join(codeDir, 'static')    # 程序包中的static文件夹的绝对路径
    storageDir = ''    # 电脑上的存储目录
    gisDir = "D:/MGXGIS" if os.path.exists("D:/") else "C:/MGXGIS"
    os.makedirs(gisDir, exist_ok=True)
    logDir = os.path.join(gisDir, 'log')
    os.makedirs(logDir, exist_ok=True)

    oriDir = os.path.join(gisDir, 'oriGis')
    os.makedirs(oriDir, exist_ok=True)
    oriGeo = os.path.join(gisDir, 'oriGeo')
    os.makedirs(oriGeo, exist_ok=True)
    Geo1 = os.path.join(gisDir, 'Geo1')
    os.makedirs(Geo1, exist_ok=True)
    Building = os.path.join(gisDir, 'Building')
    os.makedirs(Building, exist_ok=True)
    Coors = os.path.join(gisDir, 'coors')
    os.makedirs(Coors, exist_ok=True)
    Png = os.path.join(gisDir, '截图')
    os.makedirs(Png, exist_ok=True)
    USERDIR = os.path.expanduser('~')
    downloadDir = ''    # 电脑上的下载目录
    HOST, PORT, PORT2, area = queryArea(AREA)
    MAPADDR = {
        'jilin': "http://map-jl.sgcc.com.cn",
        'jiangsu': "https://map.sgcc.com.cn",
        'henan': "http://map-ha.sgcc.com.cn"
    }
    MAPURL = MAPADDR.get(area, 'https://map.sgcc.com.cn')

    devPort = str(getRandomPort(9001, 9300))  # '9528'    # 开发环境中的前端页面端口
    proxyServerPort = getRandomPort(9301, 9600)  # porxyServerPort
    remoteDebuggingPort = getRandomPort(9601, 9900)  # 远程调式端口
    webapiPort = getRandomPort(9901, 19900)  # websocket 端口
    devEnv = True  # 是否为开发环境，不需要手动更改，在程序运行的时候自动判断
    debug = False  # 是否开启调试模式
    proxy = {'http': None, 'https': None}
    goverFlag = True