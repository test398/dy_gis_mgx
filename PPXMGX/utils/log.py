import logging
import logging.handlers
import os
import time


def log_file(user=''):
    logDir = f'{"D:/MGXGIS" if os.path.exists("D:/") else "C:/MGXGIS"}/log/{time.strftime("%Y%m")}' 
    os.makedirs(logDir, exist_ok=True)
    log_file = f'{logDir}/{user}{time.strftime("%Y%m%d")}.log'
    handler_test = logging.handlers.RotatingFileHandler(log_file, maxBytes=10240000, backupCount=5, encoding="U8") # stdout to file
    handler_control = logging.StreamHandler()    # stdout to console
    handler_test.setLevel('INFO')               # 设置ERROR级别
    handler_control.setLevel('INFO')             # 设置INFO级别
    selfdef_fmt = '%(asctime)s %(filename)s:%(lineno)d %(funcName)s %(levelname)s %(message)s'
    formatter = logging.Formatter(selfdef_fmt)
    handler_test.setFormatter(formatter)
    handler_control.setFormatter(formatter)
    logger = logging.getLogger(user or 'updateSecurity')
    logger.setLevel('DEBUG')           #设置了这个才会把debug以上的输出到控制台
    logger.addHandler(handler_test)    #添加handler
    logger.addHandler(handler_control)
    return logger

logger = log_file()