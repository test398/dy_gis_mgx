import requests
from typing import Dict, Any, Callable, Optional, Tuple
import copy

def mt(zxy: Dict[str, int], data: bytes) -> bytes:
    """
    数据解密函数 - 字节重排算法
    对应JS中的mt函数
    
    Args:
        zxy: 包含z, x, y坐标的字典
        data: 原始二进制数据
    
    Returns:
        解密后的二进制数据
    """
    z, x, y = zxy['z'], zxy['x'], zxy['y']
    s = z % 8
    a = x % 8  
    o = y % 8
    l = data
    u = len(l) - s - a - o
    c = u // 3
    h = u // 3
    p = u - c - h
    
    # 根据坐标条件进行字节重排
    if o <= a and a <= s and o <= s:
        i = l[o:p+o]
        n = l[p+a+o:p+h+a+o]
        r = l[p+h+a+o+s:u+s+a+o]
    elif o <= a and s <= a and o <= s:
        i = l[o:p+o]
        r = l[p+s+o:p+c+s+o]
        n = l[p+c+s+o+a:u+s+a+o]
    elif a <= o and o <= s and a <= s:
        n = l[a:h+a]
        i = l[h+a+o:p+h+a+o]
        r = l[p+h+s+o+a:u+s+a+o]
    elif a <= s and s <= o and a <= o:
        n = l[a:h+a]
        r = l[h+a+s:h+c+a+s]
        i = l[h+c+s+o+a:u+s+a+o]
    elif s <= o and o <= a and s <= a:
        r = l[s:c+s]
        i = l[c+s+o:p+c+s+o]
        n = l[p+c+s+o+a:u+s+a+o]
    elif s <= a and a <= o and s <= o:
        r = l[s:c+s]
        n = l[c+s+a:c+h+s+a]
        i = l[c+h+s+o+a:u+s+a+o]
    else:
        raise ValueError("Invalid coordinate combination")
    
    # 重新组合数据
    result = bytearray(u)
    result[0:c] = r
    result[c:c+h] = n
    result[c+h:u] = i
    
    return bytes(result)

def Ct(request_params: Dict[str, Any], callback: Callable) -> Dict[str, Any]:
    """
    发送网络请求的函数
    对应JS中的Ct函数
    
    Args:
        request_params: 请求参数
        callback: 回调函数，接收(error, data, cache_control, expires)参数
    
    Returns:
        包含cancel方法的字典
    """
    try:
        # 提取请求参数
        url = request_params.get('url')
        headers = request_params.get('headers', {})
        
        # 发送请求
        response = requests.get(url, headers=headers, proxies={'http': 'http://127.0.0.1:7890', 'https': 'http://127.0.0.1:7890'})
        response.raise_for_status()
        
        # 读取响应数据
        data = response.content
        
        # 获取缓存控制信息
        cache_control = response.headers.get('Cache-Control')
        expires = response.headers.get('Expires')
        
        # 调用回调函数
        callback(None, data, cache_control, expires)
        
        return {
            'cancel': lambda: None  # 简单的取消函数
        }
        
    except Exception as e:
        raise e
        # 发生错误时调用回调
        callback(str(e), None, None, None)
        return {
            'cancel': lambda: None
        }

def Vt(request_config: Dict[str, Any], callback: Callable) -> Dict[str, Any]:
    """
    主要的请求处理函数
    对应JS中的Vt函数
    
    Args:
        request_config: 请求配置，包含tilesecurity和zxy信息
        callback: 回调函数，接收(error, data, cache_control, expires)参数
    
    Returns:
        包含cancel方法的字典
    """
    # 提取安全配置和坐标信息
    tilesecurity = request_config.pop('tilesecurity', False)
    zxy = request_config.pop('zxy', None)
    
    # 添加arrayBuffer类型
    request_config['type'] = 'arrayBuffer'
    
    def inner_callback(error: Optional[str], data: Optional[bytes], 
                      cache_control: Optional[str], expires: Optional[str]):
        """
        内部回调函数，处理数据解密
        """
        if not error and data and tilesecurity:
            # 如果需要解密，调用mt函数
            data = mt(zxy, data)
        
        # 调用外部回调
        callback(error, data, cache_control, expires)
    
    # 发送请求
    return Ct(request_config, inner_callback)

# 使用示例
def main():
    # 示例请求配置
    request_config = {
        'url': 'https://map.sgcc.com.cn:21610/v1/aegis.SGPoi-Web.nBnK,aegis.SGAnchor-Web.nBnK,aegis.SGPolygon-Web.rynK,aegis.SGLine-Web.nBnK/15/27187/10532.sg',
        'headers': {
            'User-Agent': 'Mozilla/5.0',
            'Accept': '*/*',
            'Authorization': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJJc3N1YW5jZSI6IlkiLCJhcHBJZCI6IjhkYzU0OThiZDcxMDMzYTA5OTJlNGQ3NzhhMDZlN2UzIiwiY2xpZW50SXAiOiIyMjMuNjUuNTcuMTYzIiwiZXhwIjoxNzUxOTU5MTE4LCJpYXQiOjE3NTE5NTU1MTgsImlzcyI6Ind3dy5hZWdpcy5jb20iLCJqdGkiOiJMWVNLS0dMTElOIiwic2NvcGVzIjo3LCJzdWIiOiI2Yzc5MDUwYTI5ODAzMTE4OTlkY2U3NzQ5MzI4OGI5MiIsInN1YlR5cGUiOiJhcHBrZXkiLCJ0b2tlblRUTCI6MzYwMDAwMCwidXNlck5hbWUiOiJ3ancifQ.N2Y9fNyxxYvq_qhZPjRlNQN1c2idEeakEf6VQaEZ4ss'
        },
        'tilesecurity': True,
        'zxy': {
            'z': 10,
            'x': 512,
            'y': 256
        }
    }
    
    def handle_response(error, data, cache_control, expires):
        if error:
            print(f"请求错误: {error}")
        else:
            print(f"请求成功，数据长度: {len(data)} 字节")
            print(f"缓存控制: {cache_control}")
            print(f"过期时间: {expires}")
    
    # 发送请求
    result = Vt(request_config, handle_response)
    print("请求已发送", result) 


if __name__ == "__main__":
    main()


