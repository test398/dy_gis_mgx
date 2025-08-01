# _*_ coding:utf-8 _*_
from collections import defaultdict
import copy
import os
import shutil
import traceback
import urllib.parse

import requests
import json

import logging

from utils.config import Config


def main1(url, cookie_2=None, psrId=None):
    for i in range(10):
        try:
            gisPath = os.path.join(Config.oriDir, f'{psrId}.json')
            if not os.path.exists(gisPath):
                header = {"Cookie": f"_at={cookie_2}", 'web-token': "78826a12547b4da599faa439c4ee6f30"}
                logging.info(f"url2 : {url}")
                reps_data = requests.get(url, headers=header)
                first_data = reps_data.json()
                open(gisPath, 'w', encoding="U8").write(json.dumps(first_data, indent=4, ensure_ascii=False))
            first_data = json.loads(open(gisPath, 'r', encoding="U8").read())
            dict_data = json.loads(first_data.get("data", {}).get("geojson", {}))
            oriGeoPath = os.path.join(Config.oriGeo, f'{psrId}.json')
            if not os.path.exists(oriGeoPath):
                open(oriGeoPath, 'w', encoding="U8").write(json.dumps(dict_data, indent=4, ensure_ascii=False))
            return oriGeoPath, first_data.get("data", {}).get("shebeiId")
        except Exception as e:
            print(traceback.format_exc())


if __name__ == "__main__":
    # cookie_1 = ""
    # cookie_2 = "eyJhbGciOiJIUzI1NiJ9.eyJqdGkiOiIxMzk1NTA3MDgiLCJpYXQiOjE3MzE2MzI4NjQsInN1YiI6IndhbmdyOCIsImV4cCI6MTczMTcxOTI2NH0.b5zNzD7psBUvUQo4nyU-aFTTNvD5Fpyxvoqr4CtV7nE"
    # psrId = "7d891462088a06deed6056103501607d87b66828f8"

    # main2(psrId, '安峰082#刘马村台公变')
    print(os.path.abspath('name.json'))
