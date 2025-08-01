AREA = {
    'anhui': {
        'name': '安徽',
        'host': 'http://20.51.33.37',
        'port': '31002',
        'port2': '31002'
    },
    'beijing': {
        'name': '北京'
    },
    'fujian': {
        'name': '福建'
    },
    'gansu': {
        'name': '甘肃'
    },
    'guangdong': {
        'name': '广东'
    },
    'guangxi': {
        'name': '广西'
    },
    'guizhou': {
        'name': '贵州'
    },
    'hainan': {
        'name': '海南'
    },
    'hebei': {
        'name': '河北'
    },
    'henan': {
        'name': '河南'
    },
    'heilongjiang': {
        'name': '黑龙江'
    },
    'hubei': {
        'name': '湖北',
        'host': 'http://25.55.39.199',
        'port': '30006',
        'port2': '30006'
    },
    'hunan': {
        'name': '湖南'
    },
    'jilin': {
        'name': '吉林'
    },
    'jiangsu': {
        'name': '江苏',
        'host': 'http://pms.pro.js.sgcc.com.cn',
        'port': '32100',
        'port2': '32100'
    },
    'jiangxi': {
        'name': '江西'
    },
    'liaoning': {
        'name': '辽宁',
        'host': 'http://25.67.146.223',
        'port': '30010',
        'port2': '30010'
    },
    'neimenggu': {
        'name': '内蒙古'
    },
    'ningxia': {
        'name': '宁夏',
        'host': 'http://25.80.71.79',
        'port': '30002',
        'port2': '30002'
    },
    'qinghai': {
        'name': '青海'
    },
    'shandong': {
        'name': '山东',
        'host': 'http://25.219.141.147',
        'port': '80'
    },
    'shanxi': {
        'name': '山西'
    },
    'shaanxi': {
        'name': '陕西'
    },
    'shanghai': {
        'name': '上海'
    },
    'sichuan': {
        'name': '四川',
        'host': 'http://25.214.205.81',
        'port': '80',
        'port2': '20100'
    },
    'taiwan': {
        'name': '台湾'
    },
    'tianjin': {
        'name': '天津',
        'host': 'http://25.34.94.58',
        'port': '80'
    },
    'xizang': {
        'name': '西藏'
    },
    'xinjiang': {
        'name': '新疆',
        'host': 'http://25.83.0.149',
        'port': '30006',
        'port2': '30006'
    },
    'yunnan': {
        'name': '云南'
    },
    'zhejiang': {
        'name': '浙江'
    },
    'chongqing': {
        'name': '重庆',
        'host': 'http://25.64.40.150',
        'port': '32101',
        'port2': '32101'
    },
    'aomen': {
        'name': '澳门'
    },
    'xianggang': {
        'name': '香港'
    },
}

HTML = """
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
    <link rel="icon" href="<%= BASE_URL %>favicon.ico">
  </head>
  <body>
    <div style='width:100%; top:25%; position:absolute; text-align:center'> 
        <h1>PMS地址或者PMS端口配置错误, <br>请重新安装并配置正确的地址和端口!</h1>
    </div>
  </body>
</html>
"""