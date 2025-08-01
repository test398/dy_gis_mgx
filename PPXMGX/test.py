from collections import defaultdict
import json
import os

from tqdm import tqdm

def main():
    jsonPath = r"D:\work\开发目录\PPXMGX\index.json"
    dic = json.loads(open(jsonPath, 'r', encoding="U8").read())
    for k, v in dic.items():
        dic[k] = f'{v[1]},{v[0]}'
    open(r"D:\work\开发目录\PPXMGX\index2.json", 'w', encoding="U8").write(json.dumps(dic, indent=4, ensure_ascii=False))


def main2():
    resList = []
    
    jsonDir = r"D:\美观性数据\江苏\GIS国网南京供电公司_供电服务三中心（鼓楼分部、建邺分部）"
    saveDir = os.path.join(os.path.dirname(jsonDir), 'COOR')
    os.makedirs(saveDir, exist_ok=True)
    savePath = os.path.join(saveDir, os.path.basename(jsonDir) + '.json')
    for jsonName in tqdm(os.listdir(jsonDir)):
        jsonPath = os.path.join(jsonDir, jsonName)
        # jsonPath = r"D:\美观性数据\江苏\江北新区数据\ee03e12405ff808081563861730156ee01bd962e4a.json"
        try:
            data = json.loads(open(jsonPath, 'r', encoding="U8").read())['data']
        except Exception as e:
            print(jsonPath)
            raise e
        if not data:
            return
        features = json.loads(data['geojson'])['features']
        for feature in features:
            if feature['properties'].get('psrType') == '0110':
                resList.append({'psrId': feature['properties']['psrId'], 'coordinates': feature['geometry']['coordinates'][0]})
    open(savePath, 'w', encoding="U8").write(json.dumps(resList, indent=4, ensure_ascii=False))


def main3():
    jsonPath = r"D:\生产验收文件夹\河南\二次检测\ppxTemp\GIS国网河南省电力公司三门峡供电公司_国网河南渑池县供电公司\池底供电所\27439be6-8150-4e85-b2cb-14756daebb88.json"
    dic = json.loads(open(jsonPath, 'r', encoding="U8").read())
    content = json.loads(dic['result']['content'])
    open('tempJson.json', 'w', encoding="U8").write(json.dumps(content, indent=4, ensure_ascii=False))

def main4():
    dic, lis1, lis2 = defaultdict(list), [], []
    GISDir = r"D:\生产验收文件夹\河南\四次检测\ppxTemp"
    for gisName in tqdm(os.listdir(GISDir)):
        if not gisName.startswith('GIS'):
            continue
        gisPath = os.path.join(GISDir, gisName)
        for jsonName1 in os.listdir(gisPath):
            jsonDir = os.path.join(gisPath, jsonName1)
            if not os.path.isdir(jsonDir):
                continue
            for jsonName in os.listdir(jsonDir):
                jsonPath = os.path.join(jsonDir, jsonName)
                try:
                    oriDic = json.loads(open(jsonPath, encoding="U8").read())
                except Exception:
                    print(1111, jsonPath)
                    lis1.append(jsonPath)
                    continue
                if oriDic['message'] != "success":
                    print(22222, jsonPath)
                    lis1.append(jsonPath)
                    continue
                dic2 = json.loads(oriDic['result']['content'])
                for _, feature in enumerate(dic2["features"]):
                    try:
                        if feature['properties']['psrType'] in ['0302', '0110']:
                            psrId, name, lineId, psrType = feature['properties']['psrId'], feature['properties']['name'], feature['properties']['parentPsrid'], feature['properties']['parentPsrtype']
                            if psrId in dic:
                                lis2.append((psrId, psrType, dic[psrId]))
                                print(psrId)
                            else:
                                dic[psrId] = psrType  # [lineId, name, feature['properties']['psrType']]
                    except Exception:
                        pass
    open(r"C:\Users\Administrator\Desktop\河南.json", 'w', encoding="U8").write(json.dumps(dic, ensure_ascii=False, indent=4))
    open(r"C:\Users\Administrator\Desktop\河南1.json", 'w', encoding="U8").write(json.dumps(lis1, ensure_ascii=False, indent=4))
    open(r"C:\Users\Administrator\Desktop\河南2.json", 'w', encoding="U8").write(json.dumps(lis2, ensure_ascii=False, indent=4))


if __name__ == "__main__":
    main4()