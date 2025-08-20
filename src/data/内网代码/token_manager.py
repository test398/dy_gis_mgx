#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Token自动获取管理器
用于自动获取思极地图API的authorization token
"""

import requests
import json
import time
import base64
import jwt
from typing import Optional, Dict, Any
import logging
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TokenManager:
    """Token管理器，负责自动获取和管理API token"""
    
    def __init__(self, app_key: str = None, app_secret: str = None, enable_browser_automation: bool = True):
        self.base_url = "https://map.sgcc.com.cn"
        self.login_url = f"{self.base_url}/authentication/v2/login/sysLogin"
        self.token = None
        self.token_expires_at = None
        self.session = requests.Session()
        self.app_key = app_key
        self.app_secret = app_secret
        self.enable_browser_automation = enable_browser_automation  # 内网环境可设置为False
        
        # 设置请求头，模拟浏览器
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': self.base_url,
            'Origin': self.base_url
        })
        
        # 备用token列表（从现有代码中提取的有效token）
        self.backup_tokens = [
            'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJJc3N1YW5jZSI6IlkiLCJhcHBJZCI6IjhkYzU0OThiZDcxMDMzYTA5OTJlNGQ3NzhhMDZlN2UzIiwiY2xpZW50SXAiOiIxODMuMjA2LjEyLjk3IiwiZXhwIjoxNzU1MzU2OTg4LCJpYXQiOjE3NTUzNTMzODgsImlzcyI6Ind3dy5hZWdpcy5jb20iLCJqdGkiOiJIRUFLTUpVTkNCIiwic2NvcGVzIjo3LCJzdWIiOiI2Yzc5MDUwYTI5ODAzMTE4OTlkY2U3NzQ5MzI4OGI5MiIsInN1YlR5cGUiOiJhcHBrZXkiLCJ0b2tlblRUTCI6MzYwMDAwMCwidXNlck5hbWUiOiJ3ancifQ.VxEFW0xOgGD3rCJyxajL3mQtEAsGySLYOYBwRIvm_Ws',
            'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJJc3N1YW5jZSI6IlkiLCJhcHBJZCI6Ijk0YmZiYmU1YWZlYTM3MzVhZDVjYzA2ODlkNGE2YTM1IiwiY2xpZW50SXAiOiIyMi40Ni42NS4xNTAiLCJleHAiOjE3NDcwMjM4MzMsImlhdCI6MTc0NzAyMDIzMywiaXNzIjoid3d3LmFlZ2lzLmNvbSIsImp0aSI6IkRRSVZYREdFT1giLCJzY29wZXMiOjEsInN1YiI6IjY0MmFkOWMwYzBhMjMyYzk4OGQyOTYyMTQ4YjRmYzE2Iiwic3ViVHlwZSI6ImFwcGtleSIsInRva2VuVFRMIjozNjAwMDAwLCJ1c2VyTmFtZSI6Inh1Y29uZ3d1In0.yhn-VDSkbtjM_83pJlCTrzJLiiWHe9T5DXJn1QKkNq0'
        ]
    
    def _decode_jwt_token(self, token: str) -> Optional[Dict]:
        """解码JWT token获取payload信息"""
        try:
            # JWT token不验证签名，只解码payload
            decoded = jwt.decode(token, options={"verify_signature": False})
            return decoded
        except Exception as e:
            logger.error(f"解码JWT token失败: {e}")
            return None
    
    def _is_token_expired(self, token: str) -> bool:
        """检查token是否已过期"""
        try:
            payload = self._decode_jwt_token(token)
            if payload and 'exp' in payload:
                exp_time = payload['exp']
                current_time = time.time()
                # 提前5分钟判断过期
                return current_time >= (exp_time - 300)
            return True
        except Exception:
            return True
    
    def _get_valid_backup_token(self) -> Optional[str]:
        """从备用token列表中找到有效的token"""
        for token in self.backup_tokens:
            if not self._is_token_expired(token) and self.test_token(token):
                logger.info(f"找到有效的备用token: {token[:20]}...")
                return token
        return None
    
    def _try_browser_automation(self) -> Optional[str]:
        """尝试使用浏览器自动化获取token"""
        try:
            logger.info("尝试使用浏览器自动化获取token")
            
            # 配置Chrome选项
            chrome_options = Options()
            # chrome_options.add_argument('--headless')  # 暂时不使用无头模式，方便调试
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-web-security')
            chrome_options.add_argument('--allow-running-insecure-content')
            chrome_options.add_argument('--disable-features=VizDisplayCompositor')
            chrome_options.add_argument('--window-size=1920,1080')
            
            # 启动浏览器
            driver = webdriver.Chrome(options=chrome_options)
            
            try:
                # 访问思极地图页面
                logger.info("正在访问思极地图页面...")
                driver.get(self.base_url)
                
                # 等待页面加载
                time.sleep(5)
                
                # 尝试执行登录脚本
                if self.app_key and self.app_secret:
                    login_script = f"""
                    if (typeof SGMap !== 'undefined' && SGMap.tokenTask && SGMap.tokenTask.login) {{
                        SGMap.tokenTask.login({{
                            appKey: '{self.app_key}',
                            appSecret: '{self.app_secret}'
                        }});
                        return 'Login attempted';
                    }} else {{
                        return 'SGMap not available';
                    }}
                    """
                    
                    result = driver.execute_script(login_script)
                    logger.info(f"登录尝试结果: {result}")
                    
                    # 等待登录完成
                    time.sleep(10)
                
                # 优先从sessionStorage获取accessToken（已验证有效）
                token = driver.execute_script("return sessionStorage.getItem('accessToken');")
                if token and token.strip():
                    logger.info(f"从sessionStorage获取到accessToken: {token[:50]}...")
                    return token.strip()
                
                # 备用方案：尝试从其他位置获取token
                token_scripts = [
                    "return window.bonckToken;",
                    "return window.mapToken;",
                    "return localStorage.getItem('token');",
                    "return localStorage.getItem('mapToken');",
                    "return localStorage.getItem('accessToken');",
                    "return sessionStorage.getItem('token');",
                    "return sessionStorage.getItem('mapToken');",
                    "return localStorage.getItem('authorization');",
                    "return sessionStorage.getItem('authorization');"
                ]
                
                for script in token_scripts:
                    try:
                        token = driver.execute_script(script)
                        if token and isinstance(token, str) and len(token) > 10:
                            logger.info(f"找到备用token: {token[:50]}...")
                            return token.strip()
                    except Exception as e:
                        continue
                
                logger.warning("浏览器中未找到有效token")
                return None
                
            finally:
                driver.quit()
                
        except Exception as e:
            logger.error(f"浏览器自动化获取token失败: {e}")
            return None
    
    def _get_token_from_api(self) -> Optional[str]:
        """使用AppKey和AppSecret通过API获取token"""
        if not self.app_key or not self.app_secret:
            logger.warning("AppKey或AppSecret未设置，跳过API获取")
            return None
            
        try:
            # 思极地图API登录端点（根据mapv3.js中的实现）
            login_url = "https://map.sgcc.com.cn/authentication/v2/login/sysLogin"
            
            # 请求参数（简化版本，不进行复杂加密）
            data = {
                'key': self.app_key,
                'appKey': self.app_key,
                'appSecret': self.app_secret
            }
            
            # 请求头
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'
            }
            
            # 发送登录请求
            response = requests.post(login_url, data=data, headers=headers, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"API登录响应: {result}")
            
            # 检查响应状态
            if result.get('code') != '10000':
                logger.error(f"API登录失败: {result.get('message', '未知错误')}")
                return None
            
            # 获取token
            result_value = result.get('resultValue')
            if not result_value:
                logger.error("API响应中没有resultValue")
                return None
            
            # 尝试解析token（简化处理）
            # 在实际的JS实现中，这里需要复杂的解密过程
            # 目前先尝试直接使用resultValue或从中提取token
            try:
                # 如果resultValue是JSON字符串，尝试解析
                if isinstance(result_value, str) and result_value.startswith('{'):
                    token_data = json.loads(result_value)
                    token = token_data.get('accessToken') or token_data.get('token')
                else:
                    token = result_value
            except:
                token = result_value
            
            if token:
                logger.info(f"成功从API获取token: {str(token)[:20]}...")
                return str(token)
            else:
                logger.error("无法从API响应中提取token")
                return None
            
        except Exception as e:
            logger.error(f"从API获取token失败: {e}")
            return None
    
    def _load_token_from_config(self) -> Optional[str]:
        """从环境变量加载token"""
        # 尝试从多个环境变量中获取token
        env_vars = ['SGCC_MAP_TOKEN', 'AUTH_TOKEN', 'SGCC_TOKEN']
        
        for env_var in env_vars:
            try:
                token = os.environ.get(env_var)
                if token and not self._is_token_expired(token):
                    logger.info(f"从环境变量加载有效token: {env_var}")
                    return token
            except Exception as e:
                logger.error(f"从环境变量 {env_var} 加载token失败: {e}")
        logger.info("未从环境变量中找到有效token")
        return None
    
    def _save_token_to_config(self, token: str):
        """保存token到环境变量"""
        # 设置多个环境变量以确保兼容性
        env_vars = ['SGCC_MAP_TOKEN', 'AUTH_TOKEN', 'SGCC_TOKEN']
        
        for env_var in env_vars:
            try:
                os.environ[env_var] = token
                logger.info(f"已设置环境变量: {env_var}")
            except Exception as e:
                logger.error(f"设置环境变量 {env_var} 失败: {e}")
        
        logger.info("注意: 环境变量设置仅在当前进程有效，重启终端后需要重新设置")
        logger.info("建议将环境变量添加到 ~/.bashrc 或 ~/.zshrc 文件中以保持持久化")
    
    def get_token(self, force_refresh: bool = False) -> Optional[str]:
        """获取有效的authorization token
        
        Args:
            force_refresh: 是否强制刷新token
            
        Returns:
            有效的authorization token，失败时返回None
        """
        # 检查现有token是否仍然有效
        if not force_refresh and self.token and not self._is_token_expired(self.token):
            logger.info("使用缓存的token")
            return self.token
        
        logger.info("开始获取新的authorization token")
        
        # 方法1：从配置文件加载
        token = self._load_token_from_config()
        if token:
            self.token = token
            return token
        
        # 方法2：优先使用API获取（适合内网环境，无需浏览器依赖）
        token = self._get_token_from_api()
        if token:
            self.token = token
            self._save_token_to_config(token)
            return token
        
        # 方法3：浏览器自动化作为备用方案（可在内网环境中禁用）
        if self.enable_browser_automation:
            token = self._try_browser_automation()
            if token:
                self.token = token
                self._save_token_to_config(token)
                return token
        else:
            logger.info("浏览器自动化已禁用（适合内网环境）")
        
        # 方法4：使用备用token
        token = self._get_valid_backup_token()
        if token:
            self.token = token
            self._save_token_to_config(token)
            return token
        
        # 所有方法都失败
        logger.error("所有获取token的方法都失败了")
        logger.info("请手动获取token并设置环境变量")
        logger.info("可用的环境变量名称: SGCC_MAP_TOKEN, AUTH_TOKEN, SGCC_TOKEN")
        logger.info("设置方式: export SGCC_MAP_TOKEN=your_token_here")
        logger.info("建议将环境变量添加到 ~/.bashrc 或 ~/.zshrc 文件中以保持持久化")
        
        return None
    
    def test_token(self, token: str) -> bool:
        """测试token是否有效
        
        通过调用一个简单的API来验证token是否有效
        """
        if not token:
            return False
        
        # 测试多个API端点
        test_urls = [
            "https://map.sgcc.com.cn/geoconv/v2",
            f"{self.base_url}/iserver/services/map-sgcc/rest/maps/vec",
            f"{self.base_url}/api/coordinate/transform",
            f"{self.base_url}/api/v1/coordinate/transform"
        ]
        
        headers = {
            'Authorization': token,
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # 首先尝试GET请求（更安全）
        for url in test_urls:
            try:
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    logger.info(f"Token验证成功，API端点: {url}")
                    return True
            except Exception as e:
                continue
        
        # 如果GET失败，尝试POST请求
        test_data = {
            'coords': '116.3974,39.9093', 
            'from': 1
        }
        
        for url in test_urls:
            try:
                response = requests.post(url, data=test_data, headers=headers, timeout=10)
                if response.status_code == 200:
                    result = response.json()
                    # 检查响应是否包含预期的字段
                    if 'value' in result and result.get('success', True):
                        logger.info(f"Token验证成功，API端点: {url}")
                        return True
                    elif result.get('success') is False:
                        logger.warning(f"Token验证失败: {result.get('message', '未知错误')}")
                        continue
            except Exception as e:
                continue
        
        logger.warning("Token验证失败")
        return False
    
    def manual_set_token(self, token: str) -> bool:
        """手动设置token"""
        if self.test_token(token):
            self.token = token
            self._save_token_to_config(token)
            logger.info("手动设置的token验证成功")
            return True
        else:
            logger.error("手动设置的token验证失败")
            return False

# 全局token管理器实例
_token_manager = None

def get_token_manager(app_key: str = None, app_secret: str = None, enable_browser_automation: bool = True) -> TokenManager:
    """获取全局token管理器实例
    
    Args:
        app_key: API密钥
        app_secret: API密钥
        enable_browser_automation: 是否启用浏览器自动化（内网环境可设置为False）
    """
    global _token_manager
    if _token_manager is None:
        _token_manager = TokenManager(app_key=app_key, app_secret=app_secret, enable_browser_automation=enable_browser_automation)
    elif app_key and app_secret:
        # 如果提供了新的凭据，更新现有管理器
        _token_manager.app_key = app_key
        _token_manager.app_secret = app_secret
        _token_manager.enable_browser_automation = enable_browser_automation
    return _token_manager

def get_valid_token(app_key: str = None, app_secret: str = None, force_refresh: bool = False) -> Optional[str]:
    """获取有效的authorization token（便捷函数）"""
    manager = get_token_manager(app_key=app_key, app_secret=app_secret)
    return manager.get_token(force_refresh=force_refresh)

def set_manual_token(token: str) -> bool:
    """手动设置token（便捷函数）"""
    manager = get_token_manager()
    return manager.manual_set_token(token)

if __name__ == "__main__":
    # 测试token获取
    manager = TokenManager()
    token = manager.get_token()
    
    if token:
        print(f"成功获取token: {token[:50]}...")
        
        # 解码token查看信息
        payload = manager._decode_jwt_token(token)
        if payload:
            print(f"Token信息: {json.dumps(payload, indent=2, ensure_ascii=False)}")
        
        # 测试token是否有效
        if manager.test_token(token):
            print("Token验证成功")
        else:
            print("Token验证失败")
    else:
        print("获取token失败")
        print("\n请手动获取token并使用以下方式设置:")
        print("1. 设置环境变量: export SGCC_MAP_TOKEN=your_token_here")
        print("   可用的环境变量名称: SGCC_MAP_TOKEN, AUTH_TOKEN, SGCC_TOKEN")
        print("2. 为了持久化环境变量，添加到 ~/.bashrc 或 ~/.zshrc 文件中:")
        print("   echo 'export SGCC_MAP_TOKEN=your_token_here' >> ~/.bashrc")
        print("   source ~/.bashrc")
        print("3. 或者在代码中调用: set_manual_token('your_token_here')")