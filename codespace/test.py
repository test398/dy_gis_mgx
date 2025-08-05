from collections import defaultdict
from datetime import datetime
import json
import os
import shutil
from openai import OpenAI
from tqdm import tqdm

# 设置代理环境变量（你代理的地址和端口）
def main():
    os.environ["HTTP_PROXY"] = "http://127.0.0.1:7897"
    os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7897"
    client = OpenAI(
      api_key="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"
    )

    completion = client.chat.completions.create(
      model="gpt-4o-mini",
      store=True,
      messages=[
        {"role": "user", "content": "write a haiku about ai"}
      ]
    )

    print(completion.choices[0].message)


def main2():
    r1 = r"C:\Users\jjf55\Desktop\标注图片"
    r2 = r"C:\Users\jjf55\Desktop\标注图片2"
    r3 = r"C:\Users\jjf55\Desktop\标注图片3"
    os.makedirs(r3, exist_ok=True)
    for n1 in os.listdir(r2):
        if os.path.exists(os.path.join(r1, n1)):
            continue
        # if n1 in os.listdir(r2):
        #     continue
        print(n1)
        shutil.copy(os.path.join(r2, n1), os.path.join(r3, n1))


def main3():
    r1 = r"C:\Users\jjf55\Desktop\标注图片3"
    r2 = r"C:\Users\jjf55\Desktop\标注治理前2"
    r3 = r"C:\Users\jjf55\Desktop\标注治理前3"
    r4 = r"C:\Users\jjf55\Desktop\标注治理前"
    os.makedirs(r3, exist_ok=True)
    for n1 in os.listdir(r2):
        if not os.path.exists(os.path.join(r1, n1)) or os.path.exists(os.path.join(r4, n1)):
            continue
        print(n1)
        shutil.copy(os.path.join(r2, n1), os.path.join(r3, n1))


def main4():
    bz1 = r"C:\Users\jjf55\Desktop\标注图片3"
    bz2 = r"C:\Users\jjf55\Desktop\标注治理前2"
    for n1 in os.listdir(bz2):
        if not os.path.exists(os.path.join(bz1, n1)):
            print(n1)


def main5():
    bzh = r"D:\标注图片\新建文件夹\Building2"
    bzq = r"D:\标注图片\新建文件夹\Building"
    ybz = r"C:\Users\jjf55\Desktop\标注图片3"
    for name in os.listdir(bzh):
        if not os.path.exists(os.path.join(bzq, name)) or os.path.exists(os.path.join(ybz, name)):
            continue
        if name.endswith(".json"):
            continue
        shutil.copy(os.path.join(bzq, name), os.path.join(os.path.dirname(bzh), '待标注治理前', name))


def main6(dic, savePath):
    # bz1 = r"C:\Users\jjf55\Desktop\Jiaoben(2)\Jiaoben\zlqbz.json"
    # dic = json.loads(open(bz1, 'r', encoding='utf-8').read())
    res = defaultdict()
    # print(dic['annotations'][0]['result'][0]['value']['points'])
    if len(dic['annotations']) == 0 or len(dic['annotations'][0]['result']) == 0:
        print(f"跳过 {savePath}，没有标注数据")
        return
    res['width'] = dic['annotations'][0]['result'][0]['original_width']
    res['height'] = dic['annotations'][0]['result'][0]['original_height']
    res['annotations'] = []
    for item in dic['annotations'][0]['result']:
        res['annotations'].append({
            'id': item['id'],
            'points': [[round(x[0], 3), round(x[1], 3)] for x in item['value']['points']],
            'label': item['value']['polygonlabels'][0] if item['value']['polygonlabels'] else '<无>'
        })
    open(savePath, 'w', encoding='utf-8').write(json.dumps(res, ensure_ascii=False, indent=4))


def main7(zlq, zlh):
    # zlh = r"C:\Users\jjf55\Desktop\new_biaozhu2.json"
    # zlq = r"C:\Users\jjf55\Desktop\new_zlqbz2.json"
    dic1 = json.loads(open(zlh, 'r', encoding='utf-8').read())
    dic2 = json.loads(open(zlq, 'r', encoding='utf-8').read())
    res = defaultdict(list)
    lis = []
    for item in dic1['annotations']:
        if item['label'] in ['建筑物', '道路', '河流']:
            print(item['label'])
            continue
        lis.append(item)
    dic1['annotations'] = lis
    open(zlh, 'w', encoding='utf-8').write(json.dumps(dic1, ensure_ascii=False, indent=4))

    for item in dic1['annotations']:
        item.update({'flag': 'new_pos'})
        res[item['label']].append(item)
    flagDict = defaultdict(int)
    for item in dic2['annotations']:
        label = item['label']
        if label not in res:
            item.update({'flag': 'old_pos'})
            continue
        if flagDict[label] < len(res[label]):
            item['id'] = res[label][flagDict[label]]['id']
            flagDict[label] += 1
            del res[label][flagDict[label] - 1]['flag']
        else:
            item.update({'flag': 'old_pos'})
    print(os.path.join(os.path.dirname(os.path.dirname(zlh)), os.path.basename(zlh)))
    open(os.path.join(os.path.dirname(os.path.dirname(zlh)), os.path.basename(zlh)), 'w', encoding='utf-8').write(json.dumps(dic1, ensure_ascii=False, indent=4))
    open(os.path.join(os.path.dirname(os.path.dirname(zlq)), os.path.basename(zlq)), 'w', encoding='utf-8').write(json.dumps(dic2, ensure_ascii=False, indent=4))


def main8():
    dic = {}
    print(json.dumps(dic, ensure_ascii=False))


def main9():
    print(dict(os.environ).get('OPENAI_API_KEY'))


def main10():
    jsonpath = r"D:\work\dy_gis_mgx\标注数据目录\治理后标注图片\jsondata2.json"
    lis = json.loads(open(jsonpath, 'r', encoding='utf-8').read())
    for item in tqdm(lis):
        # print(jsonpath)
        # print(item['file_upload'])
        main6(item, os.path.join(r"D:\work\dy_gis_mgx\标注数据目录\有对应关系的标注结果数据\temp", item['file_upload'].split('/')[-1])[:-5] + '_zlh.json')
        # print(item.keys())
        # print(item['data'])
        # for annotation in item['annotations']:
        #     print(annotation['result'][0])

        #     break
        # break

def main11():
    tempDir = r"D:\work\dy_gis_mgx\标注数据目录\有对应关系的标注结果数据\temp"
    for n1 in tqdm(os.listdir(tempDir)):
        if not n1.endswith('_zlq.json'):
            continue
        zlq = os.path.join(tempDir, n1)
        zlh = zlq[:-8] + 'zlh.json'
        # print(zlh)
        if not os.path.exists(zlh):
            print(f"跳过 {zlq}，没有对应的 zlh 文件")
            continue
        main7(zlh, zlq)
        # break


def main12():
    tempDir = r"D:\work\dy_gis_mgx\标注数据目录\有对应关系的标注结果数据\temp"
    for n1 in tqdm(os.listdir(tempDir)):
        if n1[8] != '-':
            continue
        newName = n1[9:]
        # print(n1, '==>', newName)
        shutil.move(os.path.join(tempDir, n1), os.path.join(tempDir, newName))

def load_gis_data_from_json(file_path):
    """
    从单个JSON文件加载GIS数据
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    timestamp = os.path.getctime(file_path)
    dt = datetime.fromtimestamp(timestamp)
    data['annotations'] = data.get('annotations', [])
    devices = data.get('annotations', [])
    buildings = data.get('buildings', [])
    roads = data.get('roads', [])
    rivers = data.get('rivers', [])
    # return dt.strftime('%Y-%m-%d %H:%M:%S')
    boundaries = {'coors': [[0, 0], [data['width'], 0], [data['width'], data['height']], [0, data['height']]]}  # 默认边界
    metadata = {
        '台区id': os.path.basename(file_path).split('.')[0].replace('_zlq', ''),  # 假设文件名格式为 "id.json"
        '区域名称': data.get('area_name', 'unknown'),
        '坐标系': data.get('coordinate_system', 'local'),
        '创建时间': data.get('creation_time', dt.strftime('%Y-%m-%d %H:%M:%S'))
    }
    # return GISdata(**data)


if __name__ == '__main__':
    # main2()
    # main3()
    # main4()
    # main5()
    # main6()
    # main7()
    # main8()
    # main9()
    # main10()
    # main11()
    # main12()
    load_gis_data_from_json(r"D:\work\dy_gis_mgx\标注数据目录\有对应关系的标注结果数据\0f24d37e-97ba-42b9-986d-5d290cfcb04_zlq.json")