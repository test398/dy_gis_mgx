"""
大模型接口模块

提供统一的大模型接口，支持多种模型的治理和评分功能
"""

from .base_model import BaseModel, ModelPricing
from .qwen_model import QwenModel
from .glm_model import GLMModel
from .kimi_model import KimiModel

# 模型注册表
MODEL_REGISTRY = {
    'qwen': QwenModel,
    'glm': GLMModel,
    'kimi': KimiModel,
    # 其他模型将在后续添加
    # 'openai': OpenAIModel,
}

def get_model(model_type: str, **kwargs) -> BaseModel:
    """
    模型工厂函数 - 统一创建各种大模型
    
    Args:
        model_type: 模型类型 ('qwen', 'openai', 'kimi', 'glm')
        **kwargs: 模型初始化参数 (api_key, model_name等)
    
    Returns:
        BaseModel: 模型实例
    
    Example:
        model = get_model('qwen', api_key='sk-xxx', model_name='qwen-vl-max-latest')
        result = model.beautify(gis_data, prompt)
    """
    if model_type not in MODEL_REGISTRY:
        available_models = list(MODEL_REGISTRY.keys())
        raise ValueError(f"不支持的模型类型: {model_type}. 可用模型: {available_models}")
    
    model_class = MODEL_REGISTRY[model_type]
    return model_class(**kwargs)

def list_available_models() -> list:
    """列出所有可用模型"""
    return list(MODEL_REGISTRY.keys())