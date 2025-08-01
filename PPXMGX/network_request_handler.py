#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网络请求处理器
对应 self.js 中的 fetch Promise 处理逻辑
"""

import requests
from typing import Optional, Callable, Any, Union
from dataclasses import dataclass

@dataclass
class RequestError:
    """请求错误类 - 对应JS中的St类"""
    message: str
    status: int
    url: str
    
    def __str__(self):
        return f"RequestError: {self.message} (Status: {self.status}, URL: {self.url})"

class NetworkRequestHandler:
    """网络请求处理器"""
    
    def __init__(self):
        self.session = requests.Session()
    
    def fetch_with_handler(self, url: str, 
                          callback: Callable, 
                          error_callback: Callable,
                          clone_response: bool = False,
                          **kwargs) :
        """
        发送网络请求并处理响应
        
        参数:
        url: 请求URL
        callback: 成功回调函数
        error_callback: 错误回调函数
        clone_response: 是否克隆响应
        **kwargs: 其他请求参数
        """
        try:
            # 发送请求
            response = self.session.get(url, proxies={'http': 'http://127.0.0.1:7890', 'https': 'http://127.0.0.1:7890'}, **kwargs)
            
            # 检查响应状态
            if response.ok:
                # 如果成功，克隆响应（如果需要）
                cloned_response = None
                if clone_response:
                    cloned_response = self._clone_response(response)
                
                # 调用成功回调
                result = callback(response, cloned_response, url)
                print(f"请求成功: {url}")
                print(f"响应状态: {response.status_code}")
                print(f"响应内容长度: {len(response.content)} 字节")
                print(f"计算结果: {response.content[:100]}")
                return response.content
            else:
                # 请求失败，创建错误对象
                error = RequestError(
                    message=response.reason,
                    status=response.status_code,
                    url=url
                )
                error_callback(error)
                print(f"请求失败: {error}")
                return None
                
        except requests.exceptions.RequestException as e:
            # 网络请求异常
            error_code = getattr(e, 'code', None)
            if error_code != 20:
                error_callback(e)
                print(f"网络请求异常: {e}")
            else:
                print(f"忽略的错误代码: {e}")
            return None
    
    def _clone_response(self, response: requests.Response) -> requests.Response:
        """克隆响应对象"""
        # 创建一个新的Response对象，复制原始响应的内容
        cloned = requests.Response()
        cloned.status_code = response.status_code
        cloned.headers = response.headers.copy()
        cloned.url = response.url
        # 注意：content是只读属性，这里我们返回原始响应
        # 在实际使用中，可以通过response.content访问内容
        return response

# 示例回调函数
def success_callback(response: requests.Response, cloned_response: Optional[requests.Response], url: str) -> dict:
    """
    成功回调函数 - 对应JS中的c函数
    
    参数:
    response: 原始响应对象
    cloned_response: 克隆的响应对象（如果启用）
    url: 请求URL
    
    返回:
    处理结果
    """
    result = {
        'url': url,
        'status_code': response.status_code,
        'content_length': len(response.content),
        'headers': dict(response.headers),
        'content_type': response.headers.get('content-type', ''),
        'has_cloned_response': cloned_response is not None
    }
    
    # 如果是JSON响应，尝试解析
    if 'application/json' in response.headers.get('content-type', ''):
        try:
            result['json_data'] = response.json()
        except:
            result['json_data'] = None
    
    # 如果是二进制数据，显示前100字节的十六进制
    if len(response.content) > 0:
        result['content_preview'] = response.content[:100].hex()
    
    return result

def error_callback(error: Union[RequestError, Exception]) -> None:
    """
    错误回调函数 - 对应JS中的r函数
    
    参数:
    error: 错误对象
    """
    print(f"错误回调被调用: {error}")

# 使用示例
def demo_sync_request():
    """演示同步请求"""
    print("同步网络请求示例")
    print("=" * 50)
    
    handler = NetworkRequestHandler()
    
    # 示例URL
    test_url = "https://map.sgcc.com.cn:21610/v1/aegis.SGPoi-Web.nBnK,aegis.SGAnchor-Web.nBnK,aegis.SGPolygon-Web.rynK,aegis.SGLine-Web.nBnK/15/27191/10533.sg"
    
    print(f"发送请求到: {test_url}")
    
    # 发送请求
    result = handler.fetch_with_handler(
        url=test_url,
        callback=success_callback,
        error_callback=error_callback,
        clone_response=True,
        timeout=10
    )
    
    return result

def demo_error_handling():
    """演示错误处理"""
    print("\n错误处理示例")
    print("=" * 50)
    
    handler = NetworkRequestHandler()
    
    # 测试404错误
    error_url = "https://httpbin.org/status/404"
    print(f"测试404错误: {error_url}")
    
    result = handler.fetch_with_handler(
        url=error_url,
        callback=success_callback,
        error_callback=error_callback,
        clone_response=False
    )
    
    # 测试网络错误
    network_error_url = "https://invalid-domain-that-does-not-exist.com"
    print(f"\n测试网络错误: {network_error_url}")
    
    result2 = handler.fetch_with_handler(
        url=network_error_url,
        callback=success_callback,
        error_callback=error_callback,
        clone_response=False
    )

def demo_vector_tile_request():
    """演示矢量瓦片请求"""
    print("\n矢量瓦片请求示例")
    print("=" * 50)
    
    handler = NetworkRequestHandler()
    
    # 示例矢量瓦片URL（需要替换为实际的URL和认证信息）
    tile_url = "https://map.sgcc.com.cn:21610/v1/aegis.SGPoi-Web.nBnK,aegis.SGAnchor-Web.nBnK,aegis.SGPolygon-Web.rynK,aegis.SGLine-Web.nBnK/15/27191/10533.sg"  # 这里用测试URL代替
    
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://map.sgcc.com.cn/',
    }
    
    print(f"发送矢量瓦片请求到: {tile_url}")
    
    # 发送请求
    result = handler.fetch_with_handler(
        url=tile_url,
        callback=success_callback,
        error_callback=error_callback,
        clone_response=True,
        headers=headers,
        timeout=30
    )
    
    return result

def get_pbf_data_from_network(url: str, headers: dict = None) -> Optional[bytes]:
    """
    从网络获取PBF数据并返回content
    
    参数:
    url: 请求URL
    headers: 请求头
    
    返回:
    PBF二进制数据
    """
    handler = NetworkRequestHandler()
    
    def content_callback(response, cloned_response, url):
        """专门用于获取content的回调函数"""
        return response.content
    
    try:
        content = handler.fetch_with_handler(
            url=url,
            callback=content_callback,
            error_callback=error_callback,
            clone_response=False,
            headers=headers or {},
            timeout=30
        )
        
        if content:
            print(f"成功获取PBF数据，大小: {len(content)} 字节")
            return content
        else:
            print("获取PBF数据失败")
            return None
            
    except Exception as e:
        print(f"获取PBF数据时出错: {e}")
        return None

if __name__ == "__main__":
    # 运行所有示例
    print("网络请求处理器演示")
    print("=" * 60)
    
    # 同步请求示例
    sync_result = demo_sync_request()
    
    # 错误处理示例
    demo_error_handling()
    
    # 矢量瓦片请求示例
    tile_result = demo_vector_tile_request()
    
    print("\n" + "=" * 60)
    print("所有示例完成")
    
    # 打印最终结果
    print(f"\n同步请求结果: {sync_result}")
    print(f"矢量瓦片请求结果: {tile_result}")
    
    print("\n使用说明:")
    print("1. 替换 tile_url 为实际的矢量瓦片URL")
    print("2. 添加必要的认证头信息")
    print("3. 根据需要调整超时时间")
    print("4. 可以根据响应内容类型进行不同的处理") 