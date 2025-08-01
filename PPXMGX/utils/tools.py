import math
import os
import re
import socket
import traceback
from utils.log import logger
import requests
from urllib import parse
import time
import json
from seleniumwire import webdriver
from seleniumwire.request import Request, Response

def calc_dis(distance):
    flag = 1 if distance > 0 else -1
    return abs(distance) % 360 * flag * math.pi / 180

def calcPoint(point, angle, dis):
    lon, lat = math.radians(point[0]), math.radians(point[1])  # 经纬度
    angle = math.radians(angle)
    R = 6371008.8
    new_lat = math.asin(math.sin(lat) * math.cos(dis / R) + math.cos(lat) * math.sin(dis / R) * math.cos(angle))
    new_lon = lon + math.atan2(math.sin(angle) * math.sin(dis / R) * math.cos(lat), math.cos(dis / R) - math.sin(lat) * math.sin(new_lat))
    new_lat, new_lon = round(math.degrees(new_lat), 7), round(math.degrees(new_lon), 7)
    return [new_lon, new_lat]


def getRandomPort(start: int, end: int) -> int:
    for port in range(start, end):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('127.0.0.1', port))
                logger.info(f"开启了端口: {port}")
                return port
            except socket.error:
                pass
    else:
        logger.info(f"开启了端口: {end}")
        return end

def method5(BASEURL=None, head=None, psrId=None, count=0):
    rnd = "a50841ff31136967ba2fa1"
    # head = {'Cookie': f"_at={cookie}", 'web-token': "78826a12547b4da599faa439c4ee6f30"}
    url = f'{BASEURL}/yj-pms-devicemanage/changeorders/getUserInfo/?rnd={rnd}'  # f'{baseUrl}/yj-pms-portal/portalController/getUser?rnd={rnd}'
    try:
        res = requests.get(url, headers=head, timeout=10).json()
        userid, name, ywdwid, ywdwmc, ssdsid, ssdsmc = [res['resultValue'].get(x, '') for x in ['userID', 'RYMC', 'YWDWID', 'YWDWMC', 'SSDSID', 'SSDSMC']]
        url = f'{BASEURL}/yj-pms-portal/bpmController/getTaskList/{userid}/{count}_sbtygl?rnd={rnd}'
        data_response = requests.get(url, headers=head, timeout=10)
        data = data_response.json()
    except Exception:
        logger.info(traceback.format_exc())
        return
    for lis in data['resultValue']['userTaskList']:
        if lis.get('activityName') != '图数维护':
            continue
        prociName, taskId = lis['prociName'], lis.get('businessid') or lis.get('businessKey', 'bbb')
        try:
            url = f'{BASEURL}/yj-pms-devicemanage/changeorders/getChangeDataById/{taskId}'
            res = requests.get(url, headers=head, timeout=10).json()
        except Exception:
            continue
        for item in res['resultValue']:
            if item['feederId'] == psrId:
                return True
    if int(data['resultValue']['count']) > count + 20:
        return method5(BASEURL, head, psrId, count + 20)

def getTaskID(baseUrl, head, psrId, proName):
    # head = {'Cookie': '_at=eyJhbGciOiJIUzI1NiJ9.eyJqdGkiOiIxMzk1NTA3MDgiLCJpYXQiOjE3MTgwNzMyMzEsInN1YiI6IndhbmdyOCIsImV4cCI6MTcxODE1OTYzMX0.sB1Ub4pEpEJLAT-mRbfFouX1BJ9dwbiIDMnoiNVSmfU'}
    rnd = "a50841ff31136967ba2fa1"
    if method5(baseUrl, head, psrId):
        return '', '', '', True
    url = f'{baseUrl}/yj-pms-devicemanage/changeorders/getUserInfo/?rnd={rnd}'  # f'{baseUrl}/yj-pms-portal/portalController/getUser?rnd={rnd}'
    res = requests.get(url, headers=head, timeout=10).json()
    userid, name, ywdwid, ywdwmc, ssdsid, ssdsmc = [res['resultValue'].get(x, '') for x in ['userID', 'RYMC', 'YWDWID', 'YWDWMC', 'SSDSID', 'SSDSMC']]
    # logger.info(userid, name, ywdwid, ywdwmc, ssdsid, ssdsmc)

    url = f'{baseUrl}/yj-pms-portal/bpmController/getTaskList/{userid}/0_sbtygl?rnd={rnd}'
    data_response = requests.get(url, headers=head, timeout=10)
    data = data_response.json()
    for lis in data['resultValue']['userTaskList']:
        if lis.get('activityName') != '图数维护':
            continue
        prociName, taskId = lis['prociName'], lis.get('businessid') or lis.get('businessKey', 'bbb')
        prciId = lis['prciId']
        params = parse.quote(json.dumps({"columns":"sourceApp"}))
        url2 = f'{baseUrl}/yj-pms-devicemanage/changeorders/{taskId}?rnd={rnd}&params={params}'
        res = requests.get(url2, headers=head, timeout=10).json()
        if not res.get('successful'):
            logger.info(f'获取任务信息失败,跳过该任务。获取的内容: {res}')
            continue
        psrIdStr = ';'.join([str(x.get('eqiupchangerea')).replace('None', '') for x in res['resultValue']['items']])
        if psrId in psrIdStr:
            logger.info(f"psrId: {psrId}, 任务已建: {taskId}, 任务名称: {prociName}")
            return taskId, prociName, prciId, False

    for lis in data['resultValue']['userTaskList']:
        if lis.get('activityName') != '图数维护':
            continue
        prociName, taskId = lis['prociName'], lis.get('businessid') or lis.get('businessKey', 'bbb')
        prciId = lis['prciId']
        params = parse.quote(json.dumps({"columns":"sourceApp"}))
        url2 = f'{baseUrl}/yj-pms-devicemanage/changeorders/{taskId}?rnd={rnd}&params={params}'
        res = requests.get(url2, headers=head, timeout=10).json()
        if not res.get('successful'):
            logger.info(f'获取任务信息失败,跳过该任务。获取的内容: {res}')
            continue
        psrIdStr = ';'.join([str(x.get('eqiupchangerea')).replace('None', '') for x in res['resultValue']['items']])
        if not psrIdStr or len([x for x in psrIdStr.split(';')]) >= 1 or 'fdfxids' not in psrIdStr:
            continue
        url3 = f'{baseUrl}/yj-pms-devicemanage/changeorders/save?rnd={rnd}'  # 修改保存
        data = {"items": [{"objId": taskId, "eqiupchangerea": f"{psrIdStr};{psrId}"}]}
        res = requests.post(url3, json=data, headers=head, timeout=15).json()
        logger.info(f"psrId: {psrId}, 任务已建(添加psr): {taskId}, 任务名称: {prociName}")
        return taskId, prociName, prciId, False

    url4 = f'{baseUrl}/yj-pms-devicemanage/changeorders/getNewProNum/08?rnd={rnd}'
    res: dict = requests.get(url4, headers=head, timeout=10).json()
    proNumber = res['resultValue']

    timestr = time.strftime('%Y-%m-%d %H:%M:%S')
    data = {"items":[{"transmissionIdentification":"2", "shyj":"同意", "applicant":userid, "applicantName": name,
                      "applicantUnit": ywdwid, "applicantUnitName": ywdwmc, "city": ssdsid, "cityName": ssdsmc,
                      "applyTime": timestr, "projectSource":"08", "projectName": proName, "projectNumber": proNumber,
                      "changeContent": proName, "eqiupchangerea": f'fdfxids: {psrId}', "planChangeTime": timestr}]}
    url5 = f'{baseUrl}/yj-pms-devicemanage/changeorders/save?rnd={rnd}'
    res = requests.post(url5, json=data, headers=head, timeout=10).json()
    taskId = [x.get('objId') for x in res['resultValue']['items']][0]
    logger.info(f"psrId: {psrId}, 任务创建: {taskId}, 任务名称: {proName}")

    url = f'{baseUrl}/yj-pms-devicemanage/deviceChangeFlow/startFlow?rnd={rnd}'
    data = {"code":"sbtygllc", "businessId": taskId, "userId": userid, "prociName": proName, "notagree": "0", "projectSource":"08", "isyk":"0"}
    res = requests.post(url, json=data, headers=head, timeout=15).json()
    prciId = res['resultValue']
    return taskId, proName, prciId, False


def getBrowser(Config):
    driverPath = os.path.abspath(os.path.join(os.path.dirname(__file__), "chromedriver.exe"))
    logger.info(driverPath + str(os.path.exists(driverPath)))
    options = webdriver.ChromeOptions()
    options.add_experimental_option("debuggerAddress", f"127.0.0.1:{Config.remoteDebuggingPort}")
    logger.info("链接成功")
    browser = webdriver.Chrome(executable_path=driverPath, chrome_options=options, seleniumwire_options={"port": Config.proxyServerPort})
    return browser

def getNewBrowser(url,route_name):

    logger.info(f"getNewBrowser 打开title Route Name: {route_name}")

    driverPath = os.path.abspath(os.path.join(os.path.dirname(__file__), "chrome/chromedriver.exe"))
    logger.info("链接成功")
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')  # 忽略证书错误
    options.add_argument('--ignore-ssl-errors=true')  # 忽略SSL错误
    browser = webdriver.Chrome(executable_path=driverPath, options=options)
    browser.maximize_window()
    browser.get(url)

    browser.execute_script(f'document.title="{route_name}"')
    return browser

def getVersion(baseUrl, head, psrId):
    try:
        url = f"{baseUrl}/nrxt-gis-edit-service/GraphicsEdit/getDiagramEditStableHistorySum"
        data = {"psrType": "dytq", "psrId": psrId}
        res = requests.post(url, json=data, headers=head, timeout=10).json()
        match = re.search("stableDiagrams.*?version: (.*?), versionId: '(.*?)',", res['data'])
        version, versionId = (match.group(1), match.group(2)) if match else ('', '')
    except Exception:
        version, versionId = '', ''
        logger.info(f'跳过获取version的接口')
    return version, versionId

def interceptor(request: Request):
    pass

def interceptor_res(request: Request, response: Response):
    pass

def initBrowser(debugPort, proxyPort, browserDict):
    try:
        driverPath = os.path.abspath(os.path.join(os.path.dirname(__file__), "chromedriver.exe"))
        options = webdriver.ChromeOptions()
        options.add_experimental_option("debuggerAddress", f"127.0.0.1:{debugPort}")
        browser = webdriver.Chrome(executable_path=driverPath, chrome_options=options, seleniumwire_options={"port": int(proxyPort)})
        browser.request_interceptor = interceptor
        browser.response_interceptor = interceptor_res
        browserDict['browser'] = browser
    except Exception:
        print(traceback.format_exc())