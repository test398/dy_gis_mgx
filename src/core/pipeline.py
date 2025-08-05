"""
核心处理流程

实现单图处理和批量处理的主要流程逻辑
"""

import time
import multiprocessing as mp
from functools import partial
from typing import List, Optional, Dict, Any
import logging

from core.data_types import TreatmentResponse

# 导入核心数据类型
try:
    from .data_types import (
        ImageInput, TreatmentResult, BatchInput, BatchResult,
        ModelInfo, GISData
    )
    # 导入模型接口
    from ..models import get_model, BaseModel
except ImportError:
    # 绝对导入
    from core.data_types import (
        ImageInput, TreatmentResult, BatchInput, BatchResult,
        ModelInfo, GISData
    )
    from models import get_model, BaseModel

# 配置日志
logger = logging.getLogger(__name__)


def process_single_image(
    image_input: ImageInput, 
    models: List[str] = None,
    prompt: Optional[str] = None,
    **kwargs
) -> List[TreatmentResult]:
    """
    单图处理流程
    
    Args:
        image_input: 输入数据（包含GIS数据和可视化图片）
        models: 使用的模型列表，默认['qwen']
        prompt: 治理提示词，如果为None则使用默认提示词
        **kwargs: 其他配置参数
    
    Returns:
        List[TreatmentResult]: 处理结果列表（每个模型一个结果）
    
    流程:
        1. 验证和预处理GIS数据
        2. 生成可视化图片（如果需要）
        3. 调用治理模型（输入：结构化数据+图片，输出：优化后的结构化数据）
        4. 生成治理后的可视化图片
        5. 调用评分模型（对比原始和治理后的数据）
        6. 计算成本和指标
        7. 返回结果
    """
    # 默认参数
    if models is None:
        models = ['qwen']
    if prompt is None:
        prompt = _get_default_treatment_prompt()
    
    logger.info(f"开始单图处理，输入ID: {image_input.input_id}, 模型: {models}")
    logger.info(f"输入设备数量: {image_input.gis_data.get_device_count()}")
    
    results = []
    
    for model_name in models:
        try:
            logger.info(f"使用模型 {model_name} 进行处理")
            
            # 1. 验证和预处理GIS数据
            validated_input = _preprocess_input(image_input)
            
            # 2. 生成可视化图片（如果需要）
            if not validated_input.visual_image_path:
                validated_input.visual_image_path = _generate_visualization_if_needed(validated_input)
            
            # 3. 获取模型实例
            model = _get_model_instance(model_name, **kwargs)
            
            # 4. 准备GIS数据字典格式
            gis_dict = {
                "devices": validated_input.gis_data.devices,
                "buildings": validated_input.gis_data.buildings,
                "roads": validated_input.gis_data.roads,
                "rivers": validated_input.gis_data.rivers,
                "boundaries": validated_input.gis_data.boundaries,
                "metadata": validated_input.gis_data.metadata
            }
            
            # 5. 调用治理模型
            treatment_start = time.perf_counter()
            treatment_resp: TreatmentResponse = model.beautify(gis_dict, prompt, validated_input.visual_image_path)
            treatment_time = time.perf_counter() - treatment_start
            
            logger.info(f"治理完成，用时: {treatment_time:.2f}s")
            
            # 6. 生成治理后的可视化图片
            treated_image_path = _generate_treated_visualization(treatment_resp.treated_gis_data)
            
            # 7. 调用评分模型
            eval_start = time.perf_counter()
            treated_gis_dict = {
                "devices": treatment_resp.treated_gis_data.devices,
                "buildings": treatment_resp.treated_gis_data.buildings,
                "roads": treatment_resp.treated_gis_data.roads,
                "rivers": treatment_resp.treated_gis_data.rivers,
                "boundaries": treatment_resp.treated_gis_data.boundaries,
                "metadata": treatment_resp.treated_gis_data.metadata
            }
            evaluation_resp = model.evaluate(gis_dict, treated_gis_dict)
            eval_time = time.perf_counter() - eval_start
            
            logger.info(f"评分完成，用时: {eval_time:.2f}s, 美观性评分: {evaluation_resp.beauty_score}")
            
            # 7. 计算成本
            total_token_usage = treatment_resp.token_usage
            total_token_usage.input_tokens += evaluation_resp.token_usage.input_tokens
            total_token_usage.output_tokens += evaluation_resp.token_usage.output_tokens
            total_token_usage.total_tokens = total_token_usage.input_tokens + total_token_usage.output_tokens
            
            cost = model.calculate_cost(total_token_usage)
            
            # 8. 组装结果
            result = TreatmentResult(
                original_input=validated_input,
                treated_gis_data=treatment_resp.treated_gis_data,
                treated_image_path=treated_image_path,
                beauty_score=evaluation_resp.beauty_score,
                improvement_metrics=evaluation_resp.improvement_analysis,
                model_info=model.get_model_info(),
                tokens_used=total_token_usage,
                processing_time=treatment_time + eval_time,
                cost=cost
            )
            
            results.append(result)
            logger.info(f"模型 {model_name} 处理完成，成本: ${cost:.4f}")
            
        except Exception as e:
            logger.error(f"模型 {model_name} 处理失败: {e}")
            # 创建一个失败的结果
            failed_result = TreatmentResult(
                original_input=image_input,
                treated_gis_data=image_input.gis_data,  # 使用原始数据
                beauty_score=0.0,  # 表示失败
                improvement_metrics={"error": str(e)},
                model_info=ModelInfo(model_type=model_name, model_name=model_name),
                processing_time=0.0,
                cost=0.0
            )
            results.append(failed_result)
    
    logger.info(f"单图处理完成，成功: {len([r for r in results if r.beauty_score > 0])}, 失败: {len([r for r in results if r.beauty_score <= 0])}")
    return results


def process_batch(
    batch_input: BatchInput,
    models: List[str] = None,
    max_workers: int = 4,
    enable_wandb: bool = True,
    **kwargs
) -> BatchResult:
    """
    批量处理流程
    
    Args:
        batch_input: 批量输入数据
        models: 使用的模型列表
        max_workers: 最大并行进程数
        enable_wandb: 是否启用WandB追踪
        **kwargs: 其他配置参数
    
    Returns:
        BatchResult: 批量处理结果
    
    流程:
        1. 初始化WandB实验
        2. 准备任务队列
        3. Multiprocessing并行处理
        4. 收集结果并记录到WandB
        5. 生成汇总报告
    """
    if models is None:
        models = ['qwen']
    
    logger.info(f"开始批量处理，图片数量: {batch_input.get_total_images()}, 模型: {models}, 并行数: {max_workers}")
    
    # 1. 初始化WandB（如果启用）
    wandb_run_id = None
    if enable_wandb:
        try:
            wandb_run_id = _init_wandb_tracking(batch_input, models)
        except Exception as e:
            logger.warning(f"WandB初始化失败，继续处理: {e}")
    
    # 2. 准备任务参数
    all_results = []
    
    try:
        # 3. 并行处理
        if max_workers > 1 and len(batch_input.inputs) > 1:
            logger.info("使用多进程并行处理")
            all_results = _process_batch_parallel(batch_input.inputs, models, max_workers, **kwargs)
        else:
            logger.info("使用单进程顺序处理")
            all_results = _process_batch_sequential(batch_input.inputs, models, **kwargs)
        
        # 4. 记录结果到WandB
        if enable_wandb and wandb_run_id:
            _log_batch_results_to_wandb(all_results, wandb_run_id)
        
        # 5. 创建批量结果
        batch_result = BatchResult(
            results=all_results,
            wandb_run_id=wandb_run_id,
            batch_id=batch_input.batch_id
        )
        
        logger.info(f"批量处理完成，总成本: ${batch_result.summary.total_cost:.4f}")
        logger.info(f"成功率: {batch_result.summary.success_rate:.1f}%")
        
        return batch_result
        
    except Exception as e:
        logger.error(f"批量处理失败: {e}")
        raise
    finally:
        # 清理WandB
        if enable_wandb and wandb_run_id:
            _finish_wandb_tracking()


def _preprocess_input(image_input: ImageInput) -> ImageInput:
    """预处理输入数据"""
    # TODO: 实现GIS数据验证和预处理
    # 这里可以添加数据清理、坐标系转换等逻辑
    logger.debug(f"预处理输入数据: {image_input.input_id}")
    return image_input


def _generate_visualization_if_needed(image_input: ImageInput) -> Optional[str]:
    """生成可视化图片（如果需要）"""
    # TODO: 实现GIS数据到图片的可视化
    logger.debug("生成可视化图片（placeholder）")
    return None  # placeholder


def _generate_treated_visualization(treated_gis_data: GISData) -> Optional[str]:
    """生成治理后的可视化图片"""
    # TODO: 实现治理后数据的可视化
    logger.debug("生成治理后可视化图片（placeholder）")
    return None  # placeholder


def _get_model_instance(model_name: str, **kwargs) -> BaseModel:
    """获取模型实例"""
    # 从环境变量或配置中获取API密钥
    import os
    
    api_key_map = {
        'qwen': os.getenv('QWEN_API_KEY', 'sk-default-key'),
        'openai': os.getenv('OPENAI_API_KEY'),
        'kimi': os.getenv('KIMI_API_KEY'),
        'glm': os.getenv('GLM_API_KEY')
    }
    
    api_key = api_key_map.get(model_name)
    if not api_key:
        raise ValueError(f"未配置模型 {model_name} 的API密钥")
    
    return get_model(model_name, api_key=api_key, **kwargs)


def _get_default_treatment_prompt() -> str:
    """获取默认的治理提示词"""
    # TODO: 从配置文件或prompt_manager中加载
    return """
请根据电网台区布局优化规则，优化设备的空间布局以提升美观性。

优化原则：
1. 设备布局应整齐有序
2. 设备间距应合理适中
3. 避免设备重叠或过于密集
4. 优化线路走向，减少交叉
5. 考虑地形因素（建筑、道路、河流）

请返回优化后的设备坐标数据。
"""


def _process_batch_parallel(
    inputs: List[ImageInput], 
    models: List[str], 
    max_workers: int,
    **kwargs
) -> List[TreatmentResult]:
    """并行批量处理"""
    # 准备任务列表
    tasks = []
    for image_input in inputs:
        tasks.append((image_input, models, kwargs))
    
    # 使用进程池并行处理
    with mp.Pool(processes=max_workers) as pool:
        # 使用partial来传递固定参数
        process_func = partial(_process_single_task)
        results_nested = pool.map(process_func, tasks)
    
    # 展平结果列表
    all_results = []
    for result_list in results_nested:
        all_results.extend(result_list)
    
    return all_results


def _process_batch_sequential(
    inputs: List[ImageInput], 
    models: List[str],
    **kwargs
) -> List[TreatmentResult]:
    """顺序批量处理"""
    all_results = []
    
    for i, image_input in enumerate(inputs):
        logger.info(f"处理图片 {i+1}/{len(inputs)}: {image_input.input_id}")
        try:
            results = process_single_image(image_input, models, **kwargs)
            all_results.extend(results)
        except Exception as e:
            logger.error(f"处理图片 {image_input.input_id} 失败: {e}")
    
    return all_results


def _process_single_task(task_data) -> List[TreatmentResult]:
    """处理单个任务（用于多进程）"""
    image_input, models, kwargs = task_data
    try:
        return process_single_image(image_input, models, **kwargs)
    except Exception as e:
        logger.error(f"处理任务失败: {e}")
        return []


def _init_wandb_tracking(batch_input: BatchInput, models: List[str]) -> str:
    """初始化WandB追踪"""
    # TODO: 实现WandB初始化
    logger.info("初始化WandB追踪（placeholder）")
    return f"wandb_run_{int(time.time())}"


def _log_batch_results_to_wandb(results: List[TreatmentResult], run_id: str):
    """记录批量结果到WandB"""
    # TODO: 实现WandB结果记录
    logger.info(f"记录结果到WandB: {run_id}（placeholder）")


def _finish_wandb_tracking():
    """完成WandB追踪"""
    # TODO: 实现WandB清理
    logger.info("完成WandB追踪（placeholder）")