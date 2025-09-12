"""
核心处理流程

实现单图处理和批量处理的主要流程逻辑
"""

import time
import multiprocessing as mp
from functools import partial
from typing import List, Optional, Dict, Any, Callable, Set
import logging
import gc

from core.data_types import EvaluationResponse, TreatmentResponse

# 导入核心数据类型
try:
    from .data_types import (
        ImageInput, TreatmentResult, BatchInput, BatchResult,
        ModelInfo, GISData
    )
    # 导入模型接口
    from ..models import get_model, BaseModel
    # 导入实验追踪
    from ..tracking import (
        GISExperimentTracker,
        APICallRecord
    )
except ImportError:
    # 绝对导入
    from core.data_types import (
        ImageInput, TreatmentResult, BatchInput, BatchResult,
        ModelInfo, GISData
    )
    from models import get_model, BaseModel
    from tracking import (
        GISExperimentTracker,
        APICallRecord
    )

# 配置日志
logger = logging.getLogger(__name__)


def process_single_image(
    image_input: ImageInput, 
    models: List[str] = None,
    prompt: Optional[str] = None,
    experiment_tracker: Optional[GISExperimentTracker] = None,
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
            logger.info(f"🔧 获取模型实例: {model_name}")
            model = _get_model_instance(model_name, **kwargs)
            logger.info(f"✅ 模型实例创建成功: {model_name}")
            
            # 4. 准备GIS数据字典格式
            logger.info(f"📋 准备GIS数据字典格式")
            gis_dict = {
                "devices": validated_input.gis_data.devices,
                "buildings": validated_input.gis_data.buildings,
                "roads": validated_input.gis_data.roads,
                "rivers": validated_input.gis_data.rivers,
                "boundaries": validated_input.gis_data.boundaries,
                "metadata": validated_input.gis_data.metadata
            }
            logger.info(f"📊 GIS数据统计 - 设备: {len(gis_dict.get('devices', []))}, 建筑: {len(gis_dict.get('buildings', []))}, 道路: {len(gis_dict.get('roads', []))}, 河流: {len(gis_dict.get('rivers', []))}")
            
            # 5. 调用治理模型
            logger.info(f"🤖 开始调用治理模型: {model_name}")
            treatment_start = time.perf_counter()
            treatment_resp: TreatmentResponse = model.beautify(gis_dict, prompt, validated_input.visual_image_path)
            treatment_time = time.perf_counter() - treatment_start
            logger.info(f"✅ 治理模型调用完成: {model_name}, 用时: {treatment_time:.2f}s")
            
            # 记录治理API调用到实验追踪器
            if experiment_tracker:
                _record_api_call_to_tracker(
                    experiment_tracker, model_name, "beautify", 
                    gis_dict, treatment_resp, treatment_time, True
                )
            
            logger.info(f"治理完成，用时: {treatment_time:.2f}s")
            
            # 6. 生成治理后的可视化图片
            logger.info(f"🖼️ 生成治理后的可视化图片")
            treated_image_path = _generate_treated_visualization(treatment_resp.treated_gis_data)
            logger.info(f"✅ 可视化图片生成完成: {treated_image_path}")
            
            # 7. 调用评分模型
            logger.info(f"📊 准备治理后的GIS数据用于评分")
            eval_start = time.perf_counter()
            treated_gis_dict = {
                "devices": treatment_resp.treated_gis_data.devices,
                "buildings": treatment_resp.treated_gis_data.buildings,
                "roads": treatment_resp.treated_gis_data.roads,
                "rivers": treatment_resp.treated_gis_data.rivers,
                "boundaries": treatment_resp.treated_gis_data.boundaries,
                "metadata": treatment_resp.treated_gis_data.metadata
            }
            logger.info(f"🤖 开始调用评分模型: {model_name}")
            evaluation_resp: EvaluationResponse = model.evaluate(gis_dict, treated_gis_dict)
            eval_time = time.perf_counter() - eval_start
            logger.info(f"✅ 评分模型调用完成: {model_name}, 用时: {eval_time:.2f}s")
            
            # 记录评分API调用到实验追踪器
            if experiment_tracker:
                _record_api_call_to_tracker(
                    experiment_tracker, model_name, "evaluate", 
                    {"original": gis_dict, "treated": treated_gis_dict}, 
                    evaluation_resp, eval_time, True
                )
            
            logger.info(f"评分完成，用时: {eval_time:.2f}s, 美观性评分: {evaluation_resp.beauty_score}")
            
            # 7. 计算成本
            total_token_usage = treatment_resp.token_usage
            total_token_usage.input_tokens += evaluation_resp.token_usage.input_tokens
            total_token_usage.output_tokens += evaluation_resp.token_usage.output_tokens
            total_token_usage.total_tokens = total_token_usage.input_tokens + total_token_usage.output_tokens
            
            cost = model.calculate_cost(total_token_usage.input_tokens, total_token_usage.output_tokens)
            
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
    
    # 治理成功的判断：有治理后的GIS数据且设备数量大于0
    successful_results = [r for r in results if 
                         hasattr(r, 'treated_gis_data') and r.treated_gis_data and 
                         len(getattr(r.treated_gis_data, 'devices', []) or []) > 0]
    failed_results = [r for r in results if r not in successful_results]
    logger.info(f"单图处理完成，成功: {len(successful_results)}, 失败: {len(failed_results)}")
    return results


def process_batch(
    batch_input: BatchInput,
    models: List[str] = None,
    max_workers: int = 4,
    enable_wandb: bool = True,
    on_progress: Optional[Callable[[int, int, str], None]] = None,
    skip_ids: Optional[Set[str]] = None,
    experiment_tracker: Optional[GISExperimentTracker] = None,
    qwen_batch_config = None,
    **kwargs
) -> BatchResult:
    """
    批量处理流程
    
    Args:
        batch_input: 批量输入数据
        models: 使用的模型列表
        max_workers: 最大并行进程数
        enable_wandb: 是否启用WandB追踪
        on_progress: 进度回调 (done, total, current_id)
        skip_ids: 可选，跳过这些input_id
        experiment_tracker: 可选，实验追踪器实例
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
    if skip_ids is None:
        skip_ids = set()
    
    # 过滤需处理的输入
    pending_inputs = [inp for inp in batch_input.inputs if inp.input_id not in skip_ids]
    skipped = len(batch_input.inputs) - len(pending_inputs)
    if skipped > 0:
        logger.info(f"跳过已处理: {skipped} 项，待处理: {len(pending_inputs)}")
    
    logger.info(f"开始批量处理，图片数量: {len(pending_inputs)}, 模型: {models}, 并行数: {max_workers}")
    
    # 1. 初始化WandB（如果启用）
    wandb_run_id = None
    if enable_wandb:
        try:
            wandb_run_id = _init_wandb_tracking(batch_input, models)
        except Exception as e:
            logger.warning(f"WandB初始化失败，继续处理: {e}")
    
    # 2. 准备任务参数
    all_results = []
    total = len(pending_inputs)
    
    try:
        # 3. 并行处理
        if max_workers > 1 and total > 1:
            logger.info("使用多进程并行处理")
            all_results = _process_batch_parallel(pending_inputs, models, max_workers, on_progress=on_progress, experiment_tracker=experiment_tracker, qwen_batch_config=qwen_batch_config, **kwargs)
        else:
            logger.info("使用单进程顺序处理")
            all_results = _process_batch_sequential(pending_inputs, models, on_progress=on_progress, experiment_tracker=experiment_tracker, qwen_batch_config=qwen_batch_config, **kwargs)
        
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
        # 轻量内存回收
        del pending_inputs
        gc.collect()


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
    
    # 为千问模型传递分批配置
    model_kwargs = kwargs.copy()
    if model_name == 'qwen' and 'qwen_batch_config' in kwargs:
        model_kwargs['batch_config'] = kwargs['qwen_batch_config']
        # 移除qwen_batch_config，避免传递给其他模型
        model_kwargs.pop('qwen_batch_config', None)
    
    return get_model(model_name, api_key=api_key, **model_kwargs)


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
    on_progress: Optional[Callable[[int, int, str], None]] = None,
    experiment_tracker: Optional[GISExperimentTracker] = None,
    qwen_batch_config = None,
    **kwargs
) -> List[TreatmentResult]:
    """并行批量处理"""
    logger.info(f"🚀 开始并行批量处理，输入数量: {len(inputs)}, 工作进程数: {max_workers}, 模型: {models}")
    
    # 准备任务列表
    tasks = []
    for i, image_input in enumerate(inputs):
        # 将qwen_batch_config添加到kwargs中
        task_kwargs = kwargs.copy()
        if qwen_batch_config is not None:
            task_kwargs['qwen_batch_config'] = qwen_batch_config
        tasks.append((image_input, models, experiment_tracker, task_kwargs))
        if i < 5:  # 只记录前5个任务的详细信息
            logger.info(f"  任务 {i+1}: {image_input.input_id}")
    
    if len(inputs) > 5:
        logger.info(f"  ... 还有 {len(inputs)-5} 个任务")
    
    logger.info(f"📋 任务准备完成，开始创建进程池 (进程数: {max_workers})")
    
    # 使用进程池并行处理
    try:
        with mp.Pool(processes=max_workers) as pool:
            logger.info(f"✅ 进程池创建成功，开始分发任务")
            
            # 使用partial来传递固定参数
            process_func = partial(_process_single_task)
            results_nested = []
            total = len(tasks)
            
            logger.info(f"🔄 开始处理 {total} 个任务...")
            
            for idx, result_list in enumerate(pool.imap(process_func, tasks), start=1):
                results_nested.append(result_list)
                
                # 每处理10个任务或者是最后一个任务时记录进度
                if idx % 10 == 0 or idx == total:
                    logger.info(f"📊 并行处理进度: {idx}/{total} ({idx/total*100:.1f}%) - 当前任务: {tasks[idx-1][0].input_id}")
                
                if on_progress:
                    try:
                        on_progress(idx, total, tasks[idx-1][0].input_id)
                    except Exception as e:
                        logger.warning(f"进度回调失败: {e}")
            
            logger.info(f"🎉 所有任务处理完成，开始整理结果")
    
    except Exception as e:
        logger.error(f"❌ 进程池处理过程中发生错误: {e}")
        raise
    
    # 展平结果列表
    all_results = []
    for result_list in results_nested:
        all_results.extend(result_list)
    
    logger.info(f"✨ 并行批量处理完成，总结果数: {len(all_results)}")
    return all_results


def _process_batch_sequential(
    inputs: List[ImageInput], 
    models: List[str],
    on_progress: Optional[Callable[[int, int, str], None]] = None,
    experiment_tracker: Optional[GISExperimentTracker] = None,
    qwen_batch_config = None,
    **kwargs
) -> List[TreatmentResult]:
    """顺序批量处理"""
    logger.info(f"🔄 开始顺序批量处理，输入数量: {len(inputs)}, 模型: {models}")
    
    all_results = []
    
    total = len(inputs)
    for i, image_input in enumerate(inputs):
        logger.info(f"📋 处理图片 {i+1}/{total}: {image_input.input_id}")
        
        try:
            start_time = time.perf_counter()
            
            # 将qwen_batch_config添加到kwargs中
            task_kwargs = kwargs.copy()
            if qwen_batch_config is not None:
                task_kwargs['qwen_batch_config'] = qwen_batch_config
            
            results = process_single_image(image_input, models, experiment_tracker=experiment_tracker, **task_kwargs)
            all_results.extend(results)
            
            end_time = time.perf_counter()
            processing_time = end_time - start_time
            
            logger.info(f"✅ 图片处理完成 {i+1}/{total}: {image_input.input_id}, 用时: {processing_time:.2f}s, 结果数: {len(results)}")
            
        except Exception as e:
            logger.error(f"❌ 处理图片 {image_input.input_id} 失败: {e}")
            import traceback
            logger.error(f"❌ 错误堆栈: {traceback.format_exc()}")
        finally:
            if on_progress:
                try:
                    on_progress(i+1, total, image_input.input_id)
                except Exception as e:
                    logger.warning(f"进度回调失败: {e}")
    
    logger.info(f"✨ 顺序批量处理完成，总结果数: {len(all_results)}")
    return all_results


def _record_api_call_to_tracker(experiment_tracker: GISExperimentTracker, 
                               model_name: str, api_type: str, 
                               input_data: Dict, output_data: Any, 
                               response_time: float, success: bool) -> None:
    """
    记录API调用到实验追踪器
    
    Args:
        experiment_tracker: 实验追踪器实例
        model_name: 模型名称
        api_type: API类型（beautify或evaluate）
        input_data: 输入数据
        output_data: 输出数据
        response_time: 响应时间
        success: 是否成功
    """
    try:
        # 计算成本和token使用量
        cost = 0.0
        tokens_used = 0
        
        if hasattr(output_data, 'token_usage') and output_data.token_usage:
            tokens_used = output_data.token_usage.total_tokens
            # 这里可以根据模型计算实际成本
            cost = tokens_used * 0.0001  # 简化的成本计算
        
        # 将输入数据转换为可序列化格式
        serializable_input = _make_serializable(input_data)
        
        # 将输出数据转换为可序列化格式
        if hasattr(output_data, '__dict__'):
            serializable_output = _make_serializable(output_data.__dict__)
        else:
            serializable_output = {"raw_output": str(output_data)}
        
        # 记录API调用
        experiment_tracker.log_api_call(
            model_name=f"{model_name}_{api_type}",
            input_data=serializable_input,
            output=serializable_output,
            metrics={
                'response_time': response_time,
                'success': success,
                'api_type': api_type
            },
            cost=cost,
            tokens_used=tokens_used
        )
        
    except Exception as e:
        logger.warning(f"记录API调用到追踪器失败: {e}")


def _make_serializable(data: Any) -> Dict:
    """
    将数据转换为JSON可序列化的格式
    
    Args:
        data: 需要转换的数据
        
    Returns:
        Dict: 可序列化的字典
    """
    if isinstance(data, dict):
        result = {}
        for key, value in data.items():
            if hasattr(value, '__dict__'):  # 自定义对象
                result[key] = _make_serializable(value.__dict__)
            elif isinstance(value, (list, tuple)):
                result[key] = [_make_serializable(item) if hasattr(item, '__dict__') else item for item in value]
            elif isinstance(value, dict):
                result[key] = _make_serializable(value)
            else:
                try:
                    # 尝试JSON序列化测试
                    import json
                    json.dumps(value)
                    result[key] = value
                except (TypeError, ValueError):
                    # 不可序列化的对象转为字符串
                    result[key] = str(value)
        return result
    elif hasattr(data, '__dict__'):
        return _make_serializable(data.__dict__)
    else:
        return {"value": str(data)}


def _process_single_task(task_data) -> List[TreatmentResult]:
    """处理单个任务（用于多进程）"""
    image_input, models, experiment_tracker, kwargs = task_data
    
    # 获取进程ID用于日志标识
    import os
    pid = os.getpid()
    
    logger.info(f"🔧 [PID:{pid}] 开始处理任务: {image_input.input_id}, 模型: {models}")
    
    try:
        start_time = time.perf_counter()
        result = process_single_image(image_input, models, experiment_tracker=experiment_tracker, **kwargs)
        end_time = time.perf_counter()
        
        processing_time = end_time - start_time
        logger.info(f"✅ [PID:{pid}] 任务完成: {image_input.input_id}, 用时: {processing_time:.2f}s, 结果数: {len(result)}")
        
        return result
    except Exception as e:
        logger.error(f"❌ [PID:{pid}] 处理任务失败: {image_input.input_id}, 错误: {e}")
        import traceback
        logger.error(f"❌ [PID:{pid}] 错误堆栈: {traceback.format_exc()}")
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