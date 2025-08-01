#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Description: 生成客户端主程序
usage: 运行前，请确保本机已经搭建Python3开发环境，且已经安装 pywebview 模块。
'''

import argparse
import gzip
import os
from io import BytesIO
import re
from threading import Thread
import time
from typing import Dict
from utils.log import logger
import webview
import traceback
from seleniumwire import webdriver
from seleniumwire.request import Request, Response
from api.api import API
from utils.config import Config
from utils.area import AREA, HTML
from selenium.webdriver.support.wait import WebDriverWait
from webview.platforms.cef import settings, command_line_switches

command_line_switches.update({'proxy-server': f'http://127.0.0.1:{Config.proxyServerPort}'})
settings.update({'remote_debugging_port': Config.remoteDebuggingPort})

cfg = Config()    # 配置
BROWSER: Dict[str, webdriver.Chrome] = {'browser': None}
js_api = API(BROWSER)    # 本地接口
WINDOW, TEMPLATE, WINDOW2, globalUser, CHUNK, equipUrl = None, "", None, "", None, None

def interceptor(request: Request):
    global WINDOW, TEMPLATE, globalUser, equipUrl
    if "themes/green/controls.css" in request.url or "iconfont.css" in request.url:  # "yj-pms-portal/portalController/getUser" in request.url:
        WINDOW.load_url(TEMPLATE)
        logger.info(f"加载完成")
    if f"chunk-{AREA[Config.area].get('chunk')}" in request.url and request.url.endswith('.js'):
        jsFile = os.path.join(Config.USERDIR, request.url.split('/')[-1])
        logger.info(f"测试拦截: {request.url}, {os.path.exists(jsFile)}")
        if os.path.exists(jsFile):
            with open(jsFile, 'rb') as fil:
                body = fil.read()
                request.create_response(
                    status_code=200,
                    headers={'Content-Type': 'application/javascript'},
                    body=body
                )
    if "epgis-js-1.5.0.min.js" in request.url and request.url.endswith('.js'):
        logger.info(f"测试拦截: {request.url}")
        jsFile = os.path.join(Config.USERDIR, request.url.split('/')[-1])
        if os.path.exists(jsFile):
            with open(jsFile, 'rb') as fil:
                body = fil.read()
                request.create_response(
                    status_code=200,
                    headers={'Content-Type': 'application/javascript'},
                    body=body
                )
    # if 'shebei/detail' in request.url:
    #     with open(r"C:\Users\Administrator\Desktop\detail.json", 'rb') as fil:
    #         body = fil.read()
    #         request.create_response(status_code=200, headers={'Content-Type': 'application/json'}, body=body)

def interceptor_res(request: Request, res: Response):
    global CHUNK
    if CHUNK is None and f"chunk-{AREA[Config.area].get('chunk')}" in request.url and request.url.endswith('.js'):
        logger.info(f'测试拦截RES: {request.url}')
        try:
            jsFile = os.path.join(Config.USERDIR, request.url.split('/')[-1])
            if not os.path.exists(jsFile):
                oriText, repText = "this.zoom=this.map.getZoom();", "this.zoom=this.map.getZoom();window.bonck=this;window.bonckDone=true;"
                if 'gzip' in res.headers.get('Content-Encoding', '').lower():
                    with gzip.GzipFile(fileobj=BytesIO(res.body)) as gz:
                        content = gz.read().decode(encoding="U8").replace(oriText, repText)
                        open(jsFile, 'w', encoding="U8").write(content)
                        time.sleep(3)
                else:
                    with BytesIO(res.body) as gz:
                        content = gz.read().decode(encoding="U8").replace(oriText, repText)
                        open(jsFile, 'w', encoding="U8").write(content)
                        time.sleep(3)
        except Exception:
            logger.info(traceback.format_exc())
                # BROWSER['browser'].close()
    # print(f"检测到需要替换的JS请求, chunk-{AREA[Config.area].get('chunk')}, {request.url}")
    if "epgis-js-1.5.0.min.js" in request.url:
        jsFile = os.path.join(Config.USERDIR, request.url.split('/')[-1])
        with gzip.GzipFile(fileobj=BytesIO(res.body)) as gz:
            if not os.path.exists(jsFile):
                content = gz.read().decode(encoding="U8").replace("e.accessToken&&!", "window.bonckToken=e.accessToken,e.accessToken&&!")
                open(jsFile, 'w', encoding="U8").write(content)
                time.sleep(2)
                BROWSER['browser'].close()
        logger.info(f"检测到需要替换的JS请求, {CHUNK}")

def initBrowser():
    global BROWSER, WINDOW2, globalUser
    try:
        driverPath = os.path.abspath(os.path.join(os.path.dirname(__file__), "utils/chromedriver.exe"))
        logger.info(driverPath + str(os.path.exists(driverPath)))
        options = webdriver.ChromeOptions()
        options.add_argument('--disable-application-cache')
        options.add_experimental_option("debuggerAddress", f"127.0.0.1:{Config.remoteDebuggingPort}")
        logger.info("链接成功")
        browser = webdriver.Chrome(executable_path=driverPath, chrome_options=options, seleniumwire_options={"port": Config.proxyServerPort})
        logger.info("链接成功")
        BROWSER['browser'] = browser
        browser.request_interceptor = interceptor
        browser.response_interceptor = interceptor_res
        wait = WebDriverWait(browser, 30)
        # wait.until(lambda x: x.find_element_by_xpath('//*[@id="adCode"]')).clear()
        # wait.until(lambda x: x.find_element_by_xpath('//*[@id="adCode"]')).send_keys('xulibing')  # wangr8, gaox2
        # wait.until(lambda x: x.find_element_by_xpath('//*[@id="pwd"]')).clear()
        # wait.until(lambda x: x.find_element_by_xpath('//*[@id="pwd"]')).send_keys('xlb69923!')  # wr3185*!!, pms3.0xmz
        # wait.until(lambda x: x.find_element_by_xpath('//*[@id="imageField"]')).click()
    except Exception:
        logger.info(traceback.format_exc())


def on_shown():
    logger.info('程序启动')


def on_loaded():
    WINDOW.evaluate_js('''
        var originalWindowOpen = window.open;
        window.open = function(url, name, specs) {
            console.log('window.open, URL:', url)
            pywebview.api.openGisUrl(url);
            return originalWindowOpen.apply(this, arguments);
        }
        ''')
    # js_api.openGisUrl(f"{Config.HOST}:{Config.PORT}/yj-pms-coordinate-editing/#/tranManager")

def on_closing():
    os.system('taskkill /f /im chromedriver.exe')
    logger.info('程序关闭')

def on_closed():
    logger.info('完全退出')
    os._exit(0)

def WebViewApp(debug=False):
    global WINDOW, TEMPLATE, WINDOW2, HTML
    os.system("taskkill /f /im chromedriver.exe")
    Thread(target=initBrowser, args=(), daemon=True).start()

    template2 = f"{Config.HOST}:{Config.PORT}/yj-pms-portalui/default.html"
    window = webview.create_window(title=Config.appName, url=template2, maximized=True, text_select=True, js_api=js_api)
    # 获取窗口实例
    # js_api.setWindow(window, webview, BROWSER, js_api)
    WINDOW, WINDOW2 = window, None
    TEMPLATE = f"{Config.HOST}:{Config.PORT}/yj-pms-coordinate-editing/#/tranManager"
    # 绑定事件
    window.events.shown += on_shown
    window.events.loaded += on_loaded
    window.events.closing += on_closing
    window.events.closed += on_closed

    debug = True if debug else False
    logger.info(f"是否开启了DEBUG模式: {Config.debug}")
    webview.start(debug=False, gui="cef")


if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("-c", "--cef", action="store_true", dest="cef", help="是否开启cef模式", default=False)
        args = parser.parse_args()
        debugMod = True    # 是否开启cef模式
        WebViewApp(debugMod)
    except Exception:
        logger.info(traceback.format_exc())
