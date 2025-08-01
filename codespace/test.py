from collections import defaultdict
import json
import os
import shutil
from openai import OpenAI

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

    print(completion.choices[0].message);


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


def main6():
    bz1 = r"C:\Users\jjf55\Desktop\Jiaoben(2)\Jiaoben\zlqbz.json"
    dic = json.loads(open(bz1, 'r', encoding='utf-8').read())
    res = defaultdict()
    print(dic['annotations'][0]['result'][0]['value']['points'])
    res['width'] = dic['annotations'][0]['result'][0]['original_width']
    res['height'] = dic['annotations'][0]['result'][0]['original_height']
    res['annotations'] = []
    for item in dic['annotations'][0]['result']:
        res['annotations'].append({
            'id': item['id'],
            'points': [[round(x[0], 3), round(x[1], 3)] for x in item['value']['points']],
            'label': item['value']['polygonlabels'][0] if item['value']['polygonlabels'] else '<无>'
        })
    open('zlqbz2.json', 'w', encoding='utf-8').write(json.dumps(res, ensure_ascii=False, indent=4))


def main7():
    zlh = r"C:\Users\jjf55\Desktop\new_biaozhu2.json"
    zlq = r"C:\Users\jjf55\Desktop\new_zlqbz2.json"
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
    open('zlh.json', 'w', encoding='utf-8').write(json.dumps(dic1, ensure_ascii=False, indent=4))
    open('zlq.json', 'w', encoding='utf-8').write(json.dumps(dic2, ensure_ascii=False, indent=4))


def main8():
    dic = {
            "id": "CdRCzZLbxZ",
            "points": [
                [
                    59.12,
                    20.172
                ],
                [
                    59.361,
                    20.156
                ],
                [
                    59.503,
                    20.07
                ],
                [
                    59.639,
                    19.882
                ],
                [
                    59.67,
                    19.638
                ],
                [
                    59.67,
                    19.387
                ],
                [
                    59.54,
                    19.199
                ],
                [
                    59.429,
                    19.112
                ],
                [
                    59.281,
                    19.018
                ],
                [
                    59.169,
                    19.042
                ],
                [
                    59.04,
                    19.089
                ],
                [
                    58.916,
                    19.23
                ],
                [
                    58.823,
                    19.426
                ],
                [
                    58.805,
                    19.583
                ],
                [
                    58.817,
                    19.803
                ],
                [
                    58.873,
                    19.984
                ],
                [
                    58.972,
                    20.093
                ]
            ],
            "label": "接入点"
        }
    print(json.dumps(dic, ensure_ascii=False))

if __name__ == '__main__':
    # main2()
    # main3()
    # main4()
    # main5()
    # main6()
    # main7()
    main8()