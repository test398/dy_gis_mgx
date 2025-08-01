#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
from threading import Thread
import time
import traceback
import execjs
import requests
import webview
from api.oriGeo import main1
from api.auto_dichotomy import main2
from api.auto_dichotomy2 import main3
from api.auto_dichotomy3 import main4
from PIL import Image
from utils.config import Config
from seleniumwire.webdriver import  Chrome
from selenium.webdriver.support.wait import WebDriverWait
from api.js.security import jieMiJs
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from pynput.mouse import Button, Controller
import mouse
from utils.log import logger
from pynput.keyboard import Key, Controller as KeyCon


def wait_xpath(browser, xpath):
    try:
        element = browser.find_element(By.XPATH, xpath)
        if element:
            element.click()
            return True
        else:
            return False
    except Exception as e:
        print(e)
        return False

class JSAPI():
    def __init__(self, browser, detailUrl, psrId, lineId, openYx: callable) -> None:
        self.browser: Chrome = browser['browser']
        self.detailUrl = detailUrl
        self.psrId = psrId
        self.lineId = lineId
        self.shebeiId = None
        self.openYx: callable = openYx
        self.current = 0
        self.browser.switch_to.window(self.browser.window_handles[-1])
        self.wait = WebDriverWait(self.browser, 30)
        self.center = []
        self.zoom = 0
        self.width = 0
        self.height = 0
        self.mapToken = ""
        Thread(target=self.canvasToPng, args=(), daemon=True).start()


    def canvasToPng(self):
        try:
            while True:
                if len(self.browser.window_handles) >= 2:
                    self.browser.switch_to.window(self.browser.window_handles[-1])
                    print("检测到新窗口")
                    break
            # time.sleep(5)
            for i in range(1, 401):
                if self.browser.execute_script('return window.bonckDone;'):
                    print('地图加载完成')
                    time.sleep(0.3)
                    break
                if i % 40 == 0:
                    self.browser.refresh()
                time.sleep(0.5)
            self.mapToken = self.browser.execute_script('return window.bonckToken;')
            self.layers = self.browser.execute_script('return window.bonck.defaultCheckedKeys;')
            self.center = self.browser.execute_script('return window.bonck.map.getCenter();')
            if self.center and isinstance(self.center, dict):
                self.center = [self.center['lng'], self.center['lat']]
            print('mapToken............: ', self.mapToken)
            if 'exValue=0110' in self.detailUrl:
                self.wait.until(lambda x: x.find_element_by_xpath('//*[@class="mapStyleBox-curr"]')).click()
                time.sleep(1)
                self.wait.until(lambda x: x.find_element_by_xpath('//*[@class="map-stylesList"]/li[2]')).click()
                self.wait.until(lambda x: x.find_element_by_xpath('//*[@class="mapTop_lt"]')).click()
                time.sleep(2)
                self.browser.save_screenshot(os.path.join(Config.Png, f"{self.psrId}_美化前.png"))
                self.test()
                return
            else:
                # self.wait.until(lambda x: x.find_element_by_xpath('//*[@title="Zoom out"]')).click()
                self.browser.execute_script('window.bonck.map.setZoom(18.0);')
                time.sleep(2)
            self.zoom = self.browser.execute_script('return window.bonck.map.getZoom();')
            for layer in self.layers:
                self.browser.execute_script("""
                    var t = arguments[0];
                    var layer = window.bonck.map.getLayer(t);
                    if (layer) {
                        window.bonck.map.removeLayer(t);
                    }
                    var layer = window.bonck.map.getLayer(t + '-symbol');
                    if (layer) {
                        window.bonck.map.removeLayer(t + '-symbol');
                    }
                """, layer)
            self.canvas = self.wait.until(lambda x: x.find_element_by_xpath('//*[@class="epgis-canvas"]'))
            self.width, self.height = int(self.canvas.get_attribute('width')), int(self.canvas.get_attribute('height'))
            
            print(f"center: {self.center}, zoom: {self.zoom}, width: {self.width}, height: {self.height}, psrid: {self.psrId}")
            self.browser.save_screenshot(f"{Config.Building}/{self.psrId}.png")
            image = Image.open(f"{Config.Building}/{self.psrId}.png")
            elementImage = image.crop((200, 1018 - self.height, 1520, 1080))
            elementImage.save(f"{Config.Building}/{self.psrId}.png")
            self.browser.refresh()
            time.sleep(3)
            while True:
                if self.browser.execute_script('return window.bonckDone;'):
                    print('地图加载完成')
                    time.sleep(0.3)
                    break
                time.sleep(0.5)
            self.browser.save_screenshot(os.path.join(Config.Png, f"{self.psrId}_美化前.png"))
            self.test()
        except Exception as e:
            logger.info(traceback.format_exc())
            Config.goverFlag = True

    def test0(self):
        self.browser.switch_to.window(self.browser.window_handles[-1])
        self.cookie = [x['value'] for x in self.browser.get_cookies() if x['name'] == "_at"][0]
        jsonPath, self.shebeiId = main1(self.detailUrl, self.cookie, self.psrId)
        self.wait.until(lambda x: x.find_element_by_xpath('(//*[@class="uploadFileInput"])[1]')).send_keys(jsonPath)
        self.current = 0
        self.openYx()
        time.sleep(4)
        self.browser.save_screenshot(os.path.join(Config.Png, f"{self.psrId}_原图.png"))

    def wait_xpath(self, browser, xpath):
        try:
            element = browser.find_element(By.XPATH, xpath)
            if element:
                element.click()
                return True
            else:
                return False
        except Exception as e:
            print(e)
            return False

    def test(self):
        wait = WebDriverWait(self.browser, 30)
        self.browser.switch_to.window(self.browser.window_handles[-1])
        self.cookie = [x['value'] for x in self.browser.get_cookies() if x['name'] == "_at"][0]
        jsonPath = main2(self.detailUrl, self.cookie, self.psrId, self.width, self.height, self.zoom, self.center, self.mapToken)
        print(jsonPath)
        if jsonPath and os.path.exists(jsonPath):
            wait.until(lambda x: x.find_element_by_xpath('(//*[@class="uploadFileInput"])[1]')).send_keys(jsonPath)
        else:
            self.browser.execute_script(f'console.log("{jsonPath}")')
        self.current = 1
        
        self.openYx()
        time.sleep(4)
        self.browser.save_screenshot(os.path.join(Config.Png, f"{self.psrId}_美化后.png"))
        time.sleep(5)
        self.wait.until(lambda x: x.find_element_by_xpath('//*[@class="mapTools2"]/div[1]')).click()
        time.sleep(1)
        self.wait.until(lambda x: x.find_element_by_xpath('//*[@class="kuangxuanBox-con"]/p[1]')).click()
        time.sleep(1)
        self.wait.until(lambda x: x.find_element_by_xpath('//*[@title="Zoom out"]')).click()
        time.sleep(1)
        self.canvas = self.wait.until(lambda x: x.find_element_by_xpath('//*[@class="epgis-canvas"]'))
        self.canvas_location = self.canvas.location
        startx, starty = self.canvas_location['x'] + 50, self.canvas_location['y'] + 80
        endx, endy = self.canvas_location['x'] + 1220, self.canvas_location['y'] + 927
        mouseA = Controller()
        # self.browser.maximize_window()
        mouse.move(startx, starty, duration=1)
        time.sleep(1)
        mouseA.click(Button.left, count=1)
        time.sleep(1)
        mouse.move(endx, endy, duration=1)
        time.sleep(1)
        mouseA.click(Button.left, count=1)
        keyboard = KeyCon()
        keyboard.press(Key.left)
        keyboard.release(Key.left)
        time.sleep(2)
        # self.wait_xpath(self.browser, '//*[@id="app"]/div/div[4]/div[2]/div[1]/button[2]')  # 图形发布
        # self.wait_xpath(self.browser, '//*[@id="app"]/div/div[6]/div/div[3]/span/button[2]')  # 确认发布
        time.sleep(2)
        # while Config.goverFlag is True:
        
        # self.browser.close()
        # Config.goverFlag = True

    def test2(self):
        wait = WebDriverWait(self.browser, 30)
        self.browser.switch_to.window(self.browser.window_handles[-1])
        self.cookie = [x['value'] for x in self.browser.get_cookies() if x['name'] == "_at"][0]
        jsonPath, self.shebeiId = main3(self.detailUrl, self.cookie, self.psrId)
        wait.until(lambda x: x.find_element_by_xpath('(//*[@class="uploadFileInput"])[1]')).send_keys(jsonPath)
        self.current = 2
        self.openYx()
        time.sleep(4)
        self.browser.save_screenshot(os.path.join(Config.Png, f"{self.psrId}_直线型.png"))

    def test3(self):
        wait = WebDriverWait(self.browser, 30)
        self.browser.switch_to.window(self.browser.window_handles[-1])
        self.cookie = [x['value'] for x in self.browser.get_cookies() if x['name'] == "_at"][0]
        jsonPath, self.shebeiId = main4(self.detailUrl, self.cookie, self.psrId)
        wait.until(lambda x: x.find_element_by_xpath('(//*[@class="uploadFileInput"])[1]')).send_keys(jsonPath)
        self.current = 3
        self.openYx()
        time.sleep(4)
        self.browser.save_screenshot(os.path.join(Config.Png, f"{self.psrId}_发散型.png"))

    def test4(self):
        self.browser.save_screenshot(os.path.join(Config.Png, f"{self.psrId}_美化后.png"))
        time.sleep(2)
        Config.goverFlag = True

    def test4_ori(self):
        if self.current == 1:
            newGeoPath = os.path.join(Config.Geo1, f'{self.psrId}.json')
        elif self.current == 2:
            newGeoPath = os.path.join(Config.Geo2, f'{self.psrId}.json')
        elif self.current == 3:
            newGeoPath = os.path.join(Config.Geo3, f'{self.psrId}.json')
        else:
            return self.current
        if not os.path.exists(newGeoPath) or not self.shebeiId:
            return 99
        GeoJson = json.loads(open(newGeoPath, 'r', encoding="U8").read())
        data = {
            "geojson": f"{json.dumps(GeoJson)}",
            "lineId": self.lineId,
            "lineType": "dytq",
            "psrId": self.psrId,
            "psrType": "02",
            "shebeiId": self.shebeiId
        }
        header = {"Cookie": f"_at={self.cookie}", 'web-token': "78826a12547b4da599faa439c4ee6f30"}
        saveUrl = f"{Config.HOST}:{Config.PORT}/yj-pms-coordinate-editing/shebei/save"
        res = requests.post(saveUrl, json=data, headers=header, timeout=20)
        # print(self.psrId, self.lineId, self.shebeiId)
        # print(data)
        # print(res.text)
        if '"succ"' in res.text:
            return self.current
        return 99


class API():
    '''业务层API，供前端JS调用'''
    """
    // 一条线形状           
    var beautifyButton = document.createElement("button");
    beautifyButton.type = "button";
    beautifyButton.id = "zhixian";
    beautifyButton.className = 'el-button el-button--primary el-button--medium';
    beautifyButton.innerHTML = "<span>直线</span>";
    beautifyButton.onclick = function() {
        pywebview.api.test2();
        // alert("一键美化功能已触发！");
    };
    root.appendChild(beautifyButton);
                
    // 发散形状
    var beautifyButton = document.createElement("button");
    beautifyButton.type = "button";
    beautifyButton.id = "fasan";
    beautifyButton.className = 'el-button el-button--primary el-button--medium';
    beautifyButton.innerHTML = "<span>发散</span>";
    beautifyButton.onclick = function() {
        pywebview.api.test3();
        // alert("一键美化功能已触发！");
    };
    root.appendChild(beautifyButton);
    """
    def __init__(self, browser) -> None:
        self.browser = browser
        self.ctx = execjs.compile(jieMiJs)
    

    def openGisUrl(self, url):
        ''' 获取窗口实例 '''
        def openYx():
            window.evaluate_js('''
                setTimeout(function(){
                        const intervalId = setInterval(function() {
                            var icon = document.getElementsByClassName('el-popover__reference')[1];
                            if (icon.textContent !== "图层控制") {
                                var icon = document.getElementsByClassName('el-popover__reference')[2];
                            }
                            var yx = document.getElementsByClassName('el-tree-node__label')[1];
                            if (yx.textContent !== "营销设备") {
                                var yx = document.getElementsByClassName('el-tree-node__label')[0];
                            }
                            if (icon) {
                                icon.click();
                                yx.click();
                            }
                            console.log(yx, yx.textContent, yx.parentElement.childNodes[1].className)
                            if (yx.parentElement.childNodes[1].className === "el-checkbox") {
                                clearInterval(intervalId);
                                document.getElementsByClassName('el-popover el-popper')[2].style.display = 'none';
                                document.getElementsByClassName('epgis-canvas')[0].click();
                            }
                        }, 500);
                }, 2000);
                ''')
        
        def on_loaded():
            window.evaluate_js('''
                const intervalId = setInterval(function() {
                var root = document.getElementsByClassName("box_body")[0];
                var yjmh = document.getElementById("yijianmeihua");
                if (root && !yjmh) {
                    var beautifyButton = document.createElement("button");
                    beautifyButton.type = "button";
                    beautifyButton.id = "oriGis";
                    beautifyButton.className = 'el-button el-button--primary el-button--medium';
                    beautifyButton.innerHTML = "<span>原图</span>";
                    beautifyButton.onclick = function() {
                        pywebview.api.test0();
                        // alert("一键美化功能已触发！");
                    };
                    root.appendChild(beautifyButton);

                    var beautifyButton = document.createElement("button");
                    beautifyButton.type = "button";
                    beautifyButton.id = "yijianmeihua";
                    beautifyButton.className = 'el-button el-button--primary el-button--medium';
                    beautifyButton.innerHTML = "<span>一键美化</span>";
                    beautifyButton.onclick = function() {
                        pywebview.api.test();
                        // alert("一键美化功能已触发！");
                    };
                    root.appendChild(beautifyButton);
                               
                    // 保存当前
                    var beautifyButton = document.createElement("button");
                    beautifyButton.type = "button";
                    beautifyButton.id = "fasan";
                    beautifyButton.className = 'el-button el-button--primary el-button--medium';
                    beautifyButton.innerHTML = "<span>下一个</span>";
                    beautifyButton.onclick = async function() {
                        var iii = await pywebview.api.test4();
                    };
                    root.appendChild(beautifyButton);
                    clearInterval(intervalId);
                }
            }, 500);
                ''')
            openYx()

        # uri = self.ctx.call('jieMiJs', url.split('?')[-1])
        # psrId = [x.split('=')[-1] for x in uri.split('&') if x.split('=')[0] in ['psrId']][0]
        # lineId = [x.split('=')[-1] for x in uri.split('&') if x.split('=')[0] in ['lineId']][0]
        # detailUrl = f"{Config.HOST}:{Config.PORT}/yj-pms-coordinate-editing/shebei/detail?{'&'.join([x for x in uri.split('&') if x.split('=')[0] in ['psrId', 'psrType', 'exValue']])}"
        # window = webview.create_window('GIS图美观性', f"{Config.HOST}:{Config.PORT}{url}", maximized=True, js_api=JSAPI(self.browser, detailUrl, psrId, lineId, openYx), text_select=True)

        dic = json.loads(open(os.path.join(os.path.expanduser('~'), r"Desktop\待治理.json"), 'r', encoding="U8").read())
        for idx, (key, val) in enumerate(dic.items()):
            if os.path.exists(os.path.join(Config.Png, f'{key}_美化后.png')):
                print(f'治理过了, {key}')
                continue
            # if key != "90fe080c21ff808081608043e3016090fdd6784fdc":
            #     continue
            url = 'http://pms.pro.js.sgcc.com.cn:32100/yj-pms-coordinate-editing/#/equipManage?cHNySWQ9OGU4YzgzNzEtM2YzNy00ZGNhLTllZTItMmIyYjVlY2NlZTdmJmlzSmx4QWRkcmVzcz10cnVlJnBzclR5cGU9MDImZXhWYWx1ZT0wMzAyJmxpbmVJZD14c2JQZGJ5cVRyZWVHcm91cEA3MjY1NzcyYS1iNjU5LTQ2YjktOGE5My0wYTI3MWRkMjgxNTImbGluZVR5cGU9ZHl0cSZzYm1jPSVFNiVCMiVBQSVFNiVCMSU5RiVFNSU5NSU4NiVFOCVCNCVCOCVFNSU5RiU4RSMxMiVFNyVBRSVCMSVFNSU4RiU5OCZwc3JJZHM9'  # val[3]
            uri = self.ctx.call('jieMiJs', url.split('?')[-1])
            psrId = [x.split('=')[-1] for x in uri.split('&') if x.split('=')[0] in ['psrId']][0]
            browser = self.browser if not isinstance(self.browser, dict) else self.browser['browser']
            while True:
                if len(browser.window_handles) > 1:
                    browser.switch_to_window(browser.window_handles[-1])
                    browser.close()
                    browser.switch_to_window(browser.window_handles[0])
                else:
                    break
            browser.switch_to.window(browser.window_handles[0])
            lineId = [x.split('=')[-1] for x in uri.split('&') if x.split('=')[0] in ['lineId']][0]
            detailUrl = f"{Config.HOST}:{Config.PORT}/yj-pms-coordinate-editing/shebei/detail?{'&'.join([x for x in uri.split('&') if x.split('=')[0] in ['psrId', 'psrType', 'exValue']])}"
            print(detailUrl, psrId, lineId, url)
            # window = webview.create_window('GIS图美观性', f"{Config.HOST}:{Config.PORT}{url}", maximized=True, js_api=JSAPI(self.browser, detailUrl, psrId, lineId, openYx), text_select=True)
            window = webview.create_window('GIS图美观性', f"{url}", maximized=True, js_api=JSAPI(self.browser, detailUrl, psrId, lineId, openYx), text_select=True)
            # html_content_new = html_content.replace('http://pms.pro.js.sgcc.com.cn:32100/yj-pms-portalui/default.html', f"{Config.HOST}:{Config.PORT}{url}")
            # window = webview.create_window('GIS图审核', html=html_content_new, maximized=True, js_api=JSAPI(self.browser, detailUrl), text_select=True)
            window.events.loaded += on_loaded
            Config.goverFlag = False
            # for _ in range(600):
            while True:
                if Config.goverFlag is True:
                    break
                time.sleep(0.5)
            break

