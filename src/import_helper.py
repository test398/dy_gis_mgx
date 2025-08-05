"""
导入辅助模块

解决Python相对导入和绝对导入的兼容性问题
"""

import sys
import os
from pathlib import Path


def setup_import_path():
    """设置导入路径，确保模块可以被找到"""
    # 获取src目录的绝对路径
    src_dir = Path(__file__).parent.absolute()
    project_root = src_dir.parent
    
    # 添加src目录到Python路径
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))
    
    # 添加项目根目录到Python路径
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    return src_dir, project_root


def safe_import(module_name, package=None, relative_names=None):
    """
    安全导入模块，同时尝试相对导入和绝对导入
    
    Args:
        module_name: 模块名称
        package: 包名称（相对导入时使用）
        relative_names: 相对导入的名称列表
        
    Returns:
        导入的模块或None
    """
    # 首先尝试相对导入
    if package and relative_names:
        try:
            if len(relative_names) == 1:
                return __import__(f".{module_name}", package=package, fromlist=relative_names)
            else:
                return __import__(f".{module_name}", package=package, fromlist=relative_names)
        except ImportError:
            pass
    
    # 然后尝试绝对导入
    try:
        return __import__(module_name, fromlist=relative_names or [])
    except ImportError:
        pass
    
    # 最后尝试从src导入
    try:
        return __import__(f"src.{module_name}", fromlist=relative_names or [])
    except ImportError:
        pass
    
    return None


# 初始化导入路径
setup_import_path()