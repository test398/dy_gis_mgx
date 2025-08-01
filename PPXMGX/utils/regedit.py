import os
import winreg

import requests
import utils.log

def readReg(name):
    key, subkey = winreg.HKEY_CURRENT_USER, 'Software\\Bonck\\App'
    try:
        reg_key = winreg.OpenKey(key, subkey)
        value, _ = winreg.QueryValueEx(reg_key, name)
        winreg.CloseKey(reg_key)
        utils.log.logger.info(f'读取到注册表内容: {key}\\{subkey}\\{name}, 值: {value}')
        return value
    except FileNotFoundError:
        utils.log.logger.info(f'未能找到注册表: {key}\\{subkey}\\{name}')
    except PermissionError:
        utils.log.logger.info(f'没有读取注册表权限: {key}\\{subkey}\\{name}')
    except Exception as e:
        utils.log.logger.info(f'读注册表出现异常: {key}\\{subkey}\\{name} 异常: {e}')
    return ''
    

def editReg(name, newValue):
    key, subkey = winreg.HKEY_CURRENT_USER, 'Software\\Bonck\\App'
    try:
        try:
            reg_key = winreg.OpenKey(key, subkey, 0, winreg.KEY_ALL_ACCESS)
        except Exception:
            reg_key = winreg.CreateKeyEx(key, subkey)
        try:
            oriValue, _ = winreg.QueryValueEx(reg_key, name)
        except Exception:
            oriValue = '无原值, 新建值'
        winreg.SetValueEx(reg_key, name, 0, winreg.REG_SZ, str(newValue))
        value, _ = winreg.QueryValueEx(reg_key, name)
        winreg.CloseKey(reg_key)
        utils.log.logger.info(f'修改注册表内容成功: {key}\\{subkey}\\{name}; 原值: {oriValue}; 新值: {value}; 传值: {newValue}')

        return oriValue,value
    except Exception as e:
        utils.log.logger.info(f'修改注册表出现异常: {key}\\{subkey}\\{name}; 传值{newValue}; 异常: {e}')
    return ''


def queryArea(areaDict: dict):
    if os.path.exists(os.path.join(os.path.expanduser('~'), 'config.ini')):
        text = open(os.path.join(os.path.expanduser('~'), 'config.ini'), 'r', encoding="U8").read()
        if len(text.split()) == 2:
            host, port = [x.strip() for x in text.split()]
            return host, port, port, ''
    else:
        open(os.path.join(os.path.expanduser('~'), 'config.ini'), 'w', encoding="U8").write('')

    for _ in range(10):
        for area, attr in areaDict.items():
            host = attr.get('host', '')
            port = attr.get('port', '')
            port2 = attr.get('port2', '')
            try:
                requests.get(f'{host}:{port}', timeout=2)
                # requests.get(f'{host}:{port2}', timeout=2)
                return host, port, port2, area
            except Exception:
                continue
        else:
            return '', '', '', ''
