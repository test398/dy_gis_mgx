#!/usr/bin/env python3
"""
电网台区美化治理与打分系统 - 主程序入口

这是系统的正式主入口程序，负责：
1. 解析命令行参数
2. 初始化系统配置
3. 调用核心处理模块
4. 输出结果

作者: Yilong Ju
日期: 2025年8月4日
版本: Phase 1 基础框架
"""

import sys
import os
from datetime import datetime
from pathlib import Path
import argparse
import logging

# 添加src目录到Python路径
current_dir = Path(__file__).parent.absolute()
src_dir = current_dir / 'src'
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from src.data.device_position_compare import compare_device_positions
from src.tracking import (
    GISExperimentTracker, 
    GISExperimentConfig, 
    create_gis_experiment_tracker,
    calculate_gis_improvement_metrics,
    generate_gis_metrics_report
)
from src.core.evaluation import evaluation_pipeline, calculate_beauty_score
from src.core.full_evaluation_workflow import full_evaluation_workflow
from core.pipeline import process_batch
from core.data_types import BatchInput, ImageInput, GISData
from data.input_loader import load_gis_data_from_json
from data.output_saver import save_batch_results

def setup_logging(log_level: str = "INFO") -> None:
    """
    配置日志系统
    
    Args:
        log_level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
        """
    os.makedirs('logs', exist_ok=True)
    
    # 创建自定义格式器
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    
    # 创建控制台处理器，设置UTF-8编码
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # 创建文件处理器，设置UTF-8编码
    file_handler = logging.FileHandler(
        filename=f'logs/system_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log',
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    
    # 配置根日志器
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        handlers=[console_handler, file_handler],
        force=True  # 强制重新配置
    )

def parse_arguments() -> argparse.Namespace:
    """
    解析命令行参数
        
    Returns:
        解析后的参数对象
    """
    parser = argparse.ArgumentParser(
        description="电网台区美化治理与打分系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python main.py data/area_001.json --output results/              # 单文件处理
  python main.py data/batch/ --models qwen,openai --output results/ # 批量处理
        """
    )
    
    # 输入选项
    parser.add_argument(
        'input', 
        type=str,
        help='台区数据文件路径或目录路径 (单文件或批量目录)'
    )
    
    # 输出选项
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='./results',
        help='结果输出目录 (默认: ./results)'
    )
    
    # 模型选项
    parser.add_argument(
        '--models', '-m',
        type=str,
        default='qwen',
        help='使用的模型列表，用逗号分隔 (默认: qwen)'
    )
    
    # 配置选项
    parser.add_argument(
        '--config', '-c',
        type=str,
        help='配置文件路径 (YAML/JSON格式)'
    )
    
    # 并行处理选项
    parser.add_argument(
        '--workers', '-w',
        type=int,
        default=4,
        help='并行处理的worker数量 (默认: 4)'
    )
    
    # 日志选项
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='日志级别 (默认: INFO)'
    )
    
    # 实验追踪选项
    parser.add_argument(
        '--enable-tracking',
        action='store_true',
        help='启用WandB实验追踪'
    )
    
    parser.add_argument(
        '--experiment-name',
        type=str,
        help='实验名称（用于WandB追踪）'
    )
    
    parser.add_argument(
        '--setting-name',
        type=str,
        default='Setting_A',
        help='实验设置名称（默认: Setting_A）'
    )
    
    # WandB恢复选项
    parser.add_argument(
        '--resume-run-id',
        type=str,
        help='要恢复的WandB运行ID（如果提供，将恢复现有运行而不是创建新运行）'
    )
    
    parser.add_argument(
        '--resume-mode',
        type=str,
        choices=['allow', 'must', 'never'],
        default='allow',
        help='WandB恢复模式：allow=允许恢复或创建新运行，must=必须恢复现有运行，never=总是创建新运行（默认: allow）'
    )
    
    # 评分选项
    parser.add_argument(
        '--enable-scoring',
        action='store_true',
        help='启用治理前后评分对比分析'
    )
    
    parser.add_argument(
        '--scoring-only',
        action='store_true',
        help='仅执行评分分析，不进行治理（需要已有治理结果）'
    )
    
    parser.add_argument(
        '--save-scoring-details',
        action='store_true',
        help='保存详细评分结果到JSON文件'
    )
    
    return parser.parse_args()

def load_config(config_path: str = None) -> dict:
    """
    加载系统配置
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        配置字典
    """
    # TODO: 实现配置文件加载
    # 1. 加载默认配置
    # 2. 加载用户配置文件 (如果提供)
    # 3. 加载环境变量配置
    # 4. 合并配置
    
    default_config = {
        'models': {
            'qwen': {
                'api_key': os.getenv('QWEN_API_KEY'),
                'model_name': 'qwen-vl-max-2025-04-08',
                'timeout': 30
            }
            # TODO: 添加其他模型配置
        },
        'processing': {
            'max_workers': 4,
            'timeout': 300,
            'retry_count': 3
        },
        'output': {
            'save_images': True,
            'save_logs': True,
            'format': 'json'
        }
    }
    
    return default_config

def process_areas(input_path: str, output_dir: str, models: list, config: dict, 
                 enable_tracking: bool = False, experiment_name: str = None, 
                 setting_name: str = 'Setting_A', enable_scoring: bool = False,
                 scoring_only: bool = False, save_scoring_details: bool = False,
                 resume_run_id: str = None, resume_mode: str = 'allow') -> None:
    """
    处理台区数据的主函数
    
    Args:
        input_path: 输入路径（文件或目录）
        output_dir: 输出目录
        models: 模型列表
        config: 配置字典
        enable_tracking: 是否启用实验追踪
        experiment_name: 实验名称
        setting_name: 设置名称
        enable_scoring: 是否启用治理前后评分对比分析
        scoring_only: 是否仅执行评分分析（不进行治理）
        save_scoring_details: 是否保存详细评分结果到JSON文件
        resume_run_id: 要恢复的WandB运行ID（可选）
        resume_mode: WandB恢复模式（allow/must/never）
    """
    from pathlib import Path
    
    logger = logging.getLogger(__name__)
    input_path_obj = Path(input_path)
    
    if not input_path_obj.exists():
        raise FileNotFoundError(f"输入路径不存在: {input_path}")
    
    if input_path_obj.is_file():
        # 单文件处理 (batch size = 1)
        logger.info(f"🎯 处理单个台区文件: {input_path}")
        input_files = [input_path_obj]
    elif input_path_obj.is_dir():
        # 批量处理 (扫描目录中的所有JSON文件)
        input_files = list(input_path_obj.glob("*.json"))[:20]  # TODO 测试批量运行前五个文件
        logger.info(f"🎯 批量处理台区目录: {input_path}")
        logger.info(f"📋 发现 {len(input_files)} 个数据文件")
    else:
        raise ValueError(f"输入路径既不是文件也不是目录: {input_path}")
    
    if not input_files:
        raise ValueError("未找到任何.json数据文件")
    
    logger.info(f"📊 使用模型: {models}")
    logger.info(f"📁 输出目录: {output_dir}")
    logger.info(f"🔄 并行数: {config['processing']['max_workers']}")
    
    # 初始化实验追踪器
    experiment_tracker = None
    if enable_tracking:
        if not experiment_name:
            experiment_name = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        experiment_config = GISExperimentConfig(
            experiment_id=experiment_name,
            setting_name=setting_name,
            data_version="标注数据v1",
            evaluation_criteria="5项评分标准",
            model_name=models[0] if models else "qwen",
            algorithm_version="v1.0",
            prompt_version="v1.0",
            tags=["main_process", setting_name, f"models_{'-'.join(models)}"],
            notes=f"主流程批量处理，输入: {input_path}, 模型: {models}"
        )
        
        experiment_tracker = create_gis_experiment_tracker(
            experiment_id=experiment_config.experiment_id,
            setting_name=experiment_config.setting_name,
            data_version=experiment_config.data_version,
            evaluation_criteria=experiment_config.evaluation_criteria,
            model_name=experiment_config.model_name,
            algorithm_version=experiment_config.algorithm_version,
            prompt_version=experiment_config.prompt_version,
            tags=experiment_config.tags,
            notes=experiment_config.notes,
            resume_run_id=resume_run_id,
            resume_mode=resume_mode
        )
        logger.info(f"🔬 实验追踪已启用: {experiment_name} (Setting: {setting_name})")
    
    # 加载所有数据文件并创建ImageInput列表
    # 仅选择未治理文件：优先 _zlq.json，其次无后缀，排除 _zlh.json
    def _base_id(p):
        name = p.stem
        return name.replace('_zlq', '').replace('_zlh', '')

    selected_map = {}
    for p in input_files:
        if p.name.endswith('_zlh.json'):
            continue  # 排除已治理文件，避免重复
        b = _base_id(p)
        # 如果已有候选且不是_zlq，优先用_zlq替换
        if b in selected_map:
            # 现有候选是否为_zlq
            if not selected_map[b].name.endswith('_zlq.json') and p.name.endswith('_zlq.json'):
                selected_map[b] = p
        else:
            selected_map[b] = p

    selected_files = list(selected_map.values())
    logging.info(f"筛选后待处理文件数: {len(selected_files)}（排除_zlh已治理文件）")

    # 基于输出目录现状做二次筛选：若同时存在治理后JSON与对比图，则彻底跳过
    files_to_process = []
    skipped_by_existing = []
    skipped_by_existing_ids = []
    for file_path in selected_files:
        base_id = file_path.stem.replace('_zlq', '').replace('_zlh', '')
        treated_json = os.path.join(output_dir, f"{base_id}_zlh.json")
        compare_png = os.path.join(output_dir, f"{base_id}_result.png")
        if os.path.exists(treated_json) and os.path.exists(compare_png):
            skipped_by_existing.append(file_path)
            skipped_by_existing_ids.append(base_id)
        else:
            files_to_process.append(file_path)

    # 延后打印“已跳过”明细到批处理开始之后，以便pipeline日志先出现

    inputs = []
    for file_path in files_to_process:
        gis_data = load_gis_data_from_json(file_path)
        image_input = ImageInput(gis_data=gis_data, input_id=file_path.stem)
        inputs.append(image_input)
    # 
    # # 创建BatchInput
    batch_input = BatchInput(
        inputs=inputs,
        config=config,
        batch_id=f"main_{len(inputs)}files"
    )
    # 
    # # 调用批处理（如果不是仅评分模式）
    batch_result = None
    if inputs and not scoring_only:
        batch_result = process_batch(
            batch_input, 
            models=models,
            max_workers=config['processing']['max_workers'],
            experiment_tracker=experiment_tracker
        )
        # 保存结果到输出目录
        save_batch_results(batch_result, output_dir)
        
        # 记录实验结果到追踪器
        if experiment_tracker and batch_result.results:
            _record_batch_results_to_tracker(experiment_tracker, batch_result, experiment_name, setting_name)
            
    elif not inputs and not scoring_only:
        logging.info("本次无需治理：全部台区均已存在治理结果与对比图")
    
    # 执行评分分析（如果启用）
    if enable_scoring or scoring_only:
        _perform_scoring_analysis(
            selected_files, output_dir, save_scoring_details, 
            experiment_tracker, setting_name
        )

    # 现在输出已跳过的台区明细与统计（保证出现在pipeline开始日志之后）
    if skipped_by_existing_ids:
        for base_id in skipped_by_existing_ids:
            logging.info(f"检测到已治理且已有对比图，跳过: {base_id}")
        logging.info(f"已跳过 {len(skipped_by_existing_ids)} 个台区（均已存在JSON与对比图）")
 
    # === 生成设备位置对比图 ===
    # 规则：只要有治理后JSON但缺少对比图，就补齐对比图；否则跳过
    for file1 in selected_files:
        base_id = file1.stem.replace('_zlq', '').replace('_zlh', '')
        file2 = os.path.join(output_dir, base_id + '_zlh.json')
        out_img_path = os.path.join(output_dir, base_id + '_result.png')
        if not Path(file2).exists():
            logging.warning(f"未找到治理后json文件，无法生成对比图: {file2}")
            continue
        if Path(out_img_path).exists():
            logging.info(f"对比图已存在，跳过生成: {out_img_path}")
            continue
        # 读取治理结果，若无设备则跳过生成对比图
        try:
            import json
            with open(file2, 'r', encoding='utf-8') as f:
                treated = json.load(f)
            anns = treated.get('annotations', []) or []
            if len(anns) == 0:
                logging.warning(f"治理后无设备（annotations空），跳过对比图: {file2}")
                continue
        except Exception as e:
            logging.warning(f"读取治理后结果失败，跳过对比图: {file2}，原因: {e}")
            continue
        compare_device_positions(file1, file2, out_img_path)
    # === 最终汇总日志（放在流程最末，避免被后续日志淹没） ===
    try:
        if 'batch_result' in locals() and batch_result and getattr(batch_result, 'summary', None):
            logging.info("================ 最终汇总（流程结束） =================")
            logging.info(f"批量处理完成，总成本: ${batch_result.summary.total_cost:.4f}")
            logging.info(f"成功率: {batch_result.summary.success_rate:.1f}%")
            run_id = getattr(batch_result, 'wandb_run_id', None)
            if run_id:
                logging.info(f"WandB运行ID: {run_id}")
            logging.info("=================================================")
        else:
            logging.info("================ 最终汇总（流程结束） =================")
            logging.info("本次未执行治理或无批量汇总可用")
            logging.info("=================================================")
    except Exception:
        pass
    
    # === 完成实验追踪并上传到服务器 ===
    if experiment_tracker:
        try:
            # 生成最终实验报告
            final_report = experiment_tracker.generate_experiment_report()
            logging.info(f"实验报告已生成: {len(experiment_tracker.experiment_results)} 个结果")
            
            # 上传实验数据到服务器（参考codespace/main.py的上传功能）
            _upload_experiment_to_server(experiment_tracker, final_report, output_dir)
            
            # 完成WandB实验
            experiment_tracker.finish_experiment()
            logging.info("✅ 实验追踪已完成并上传到服务器")
            
        except Exception as e:
            logging.warning(f"完成实验追踪时出错: {e}")
            # 即使出错也要尝试完成实验
            try:
                experiment_tracker.finish_experiment()
            except:
                pass


def _record_batch_results_to_tracker(experiment_tracker: GISExperimentTracker, 
                                    batch_result, experiment_name: str, setting_name: str) -> None:
    """
    将批处理结果记录到实验追踪器
    
    Args:
        experiment_tracker: 实验追踪器实例
        batch_result: 批处理结果
        experiment_name: 实验名称
        setting_name: 实验设置名称
    """
    try:
        from src.tracking import GISExperimentResult
        
        # 计算总体指标
        total_results = len(batch_result.results)
        successful_results = [r for r in batch_result.results if r.success]
        success_rate = len(successful_results) / total_results if total_results > 0 else 0.0
        
        # 计算平均美观性分数和改善分数
        beauty_scores = []
        improvement_scores = []
        dimension_scores_sum = {}
        
        for result in successful_results:
            if hasattr(result, 'evaluation_result') and result.evaluation_result:
                eval_result = result.evaluation_result
                if hasattr(eval_result, 'total_score'):
                    beauty_scores.append(eval_result.total_score)
                if hasattr(eval_result, 'improvement_score'):
                    improvement_scores.append(eval_result.improvement_score)
                if hasattr(eval_result, 'dimension_scores'):
                    for dim, score in eval_result.dimension_scores.items():
                        if dim not in dimension_scores_sum:
                            dimension_scores_sum[dim] = []
                        dimension_scores_sum[dim].append(score)
        
        avg_beauty_score = sum(beauty_scores) / len(beauty_scores) if beauty_scores else 0.0
        avg_improvement_score = sum(improvement_scores) / len(improvement_scores) if improvement_scores else 0.0
        
        # 计算平均维度分数
        avg_dimension_scores = {}
        for dim, scores in dimension_scores_sum.items():
            avg_dimension_scores[dim] = sum(scores) / len(scores) if scores else 0.0
        
        # 计算总成本和token使用量
        total_cost = batch_result.summary.total_cost if hasattr(batch_result.summary, 'total_cost') else 0.0
        total_tokens = sum([r.tokens_used for r in batch_result.results if hasattr(r, 'tokens_used') and r.tokens_used]) or 0
        
        # 计算平均处理时间
        processing_times = [r.processing_time for r in batch_result.results if hasattr(r, 'processing_time') and r.processing_time]
        avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0.0
        
        # 创建实验结果记录
        experiment_result = GISExperimentResult(
            experiment_id=experiment_name,
            timestamp=datetime.now().isoformat(),
            setting_name=setting_name,
            data_version="标注数据v1",
            evaluation_criteria="5项评分标准",
            beauty_score=avg_beauty_score,
            improvement_score=avg_improvement_score,
            dimension_scores=avg_dimension_scores,
            model_name=experiment_tracker.config.model_name,
            algorithm_version=experiment_tracker.config.algorithm_version,
            prompt_version=experiment_tracker.config.prompt_version,
            api_success_rate=success_rate,
            json_parse_success_rate=success_rate,  # 简化处理
            processing_time=avg_processing_time,
            total_tokens=total_tokens,
            total_cost=total_cost,
            is_best_attempt=True  # 主流程的结果标记为最佳尝试
        )
        
        # 记录到追踪器
        experiment_tracker.log_experiment_result(experiment_result)
        
        # 计算和记录改善指标
        if beauty_scores and improvement_scores:
            improvement_metrics = calculate_gis_improvement_metrics(
                before_scores=beauty_scores,  # 简化处理，实际应该是治理前分数
                after_scores=[s + i for s, i in zip(beauty_scores, improvement_scores)],
                dimension_improvements=avg_dimension_scores
            )
            experiment_tracker.log_improvement_metrics(improvement_metrics)
        
        # 生成并记录指标报告
        metrics_report = generate_gis_metrics_report(
            experiment_results=[experiment_result],
            setting_name=setting_name
        )
        experiment_tracker.log_metrics_report(metrics_report)
        
        logging.info(f"实验结果已记录到追踪器: 平均美观性分数={avg_beauty_score:.2f}, 成功率={success_rate:.2%}")
        
    except Exception as e:
        logging.warning(f"记录实验结果到追踪器失败: {e}")


def _perform_scoring_analysis(selected_files: list, output_dir: str, 
                            save_scoring_details: bool, experiment_tracker, 
                            setting_name: str) -> None:
    """
    执行治理前后评分对比分析
    
    Args:
        selected_files: 待分析的文件列表
        output_dir: 输出目录
        save_scoring_details: 是否保存详细评分结果
        experiment_tracker: 实验追踪器
        setting_name: 实验设置名称
    """
    logging.info("🎯 开始执行治理前后评分对比分析...")
    
    scoring_results = []
    successful_analyses = 0
    
    for file_path in selected_files:
        try:
            base_id = file_path.stem.replace('_zlq', '').replace('_zlh', '')
            treated_file = Path(output_dir) / f"{base_id}_zlh.json"
            
            # 检查治理后文件是否存在
            if not treated_file.exists():
                logging.warning(f"未找到治理后文件，跳过评分分析: {treated_file}")
                continue
            
            # 加载治理前后数据
            from src.data.input_loader import load_gis_data_from_json
            original_gis_data = load_gis_data_from_json(file_path)
            treated_gis_data = load_gis_data_from_json(treated_file)
            
            # 将GISData对象转换为字典格式（evaluation函数期望字典输入）
            original_data = {
                'devices': original_gis_data.devices,
                'buildings': original_gis_data.buildings,
                'roads': original_gis_data.roads,
                'rivers': original_gis_data.rivers,
                'boundaries': original_gis_data.boundaries,
                'metadata': original_gis_data.metadata
            }
            treated_data = {
                'devices': treated_gis_data.devices,
                'buildings': treated_gis_data.buildings,
                'roads': treated_gis_data.roads,
                'rivers': treated_gis_data.rivers,
                'boundaries': treated_gis_data.boundaries,
                'metadata': treated_gis_data.metadata
            }
            
            # 执行评分对比
            score_result = calculate_beauty_score(original_data, treated_data)
            
            # 添加文件信息
            score_result['file_info'] = {
                'base_id': base_id,
                'original_file': str(file_path),
                'treated_file': str(treated_file)
            }
            
            scoring_results.append(score_result)
            successful_analyses += 1
            
            # 记录到实验追踪器
            if experiment_tracker:
                _record_scoring_to_tracker(experiment_tracker, score_result, base_id, setting_name)
            
            # 输出评分结果
            original_score = score_result['original_score']
            treated_score = score_result['treated_score']
            
            logging.info(f"📊 台区 {base_id} 评分分析完成:")
            logging.info(f"   治理前: {original_score['total_score']:.2f}分 ({original_score['level']})")
            logging.info(f"   治理后: {treated_score['total_score']:.2f}分 ({treated_score['level']})")
            
            improvement = treated_score['total_score'] - original_score['total_score']
            improvement_pct = (improvement / max(original_score['total_score'], 0.1)) * 100
            logging.info(f"   改善度: {improvement:+.2f}分 ({improvement_pct:+.1f}%)")
            
            # 保存详细评分结果（如果启用）
            if save_scoring_details:
                result_json_path = Path(output_dir) / f"{base_id}_评分详情.json"
                with open(result_json_path, 'w', encoding='utf-8') as f:
                    import json
                    json.dump(score_result, f, ensure_ascii=False, indent=2)
                logging.info(f"   详细评分已保存: {result_json_path}")
                
        except Exception as e:
            logging.error(f"评分分析失败 {file_path}: {e}")
            continue
    
    # 生成汇总报告
    if scoring_results:
        _generate_scoring_summary(scoring_results, output_dir, save_scoring_details)
        logging.info(f"✅ 评分分析完成: 成功分析 {successful_analyses}/{len(selected_files)} 个台区")
    else:
        logging.warning("❌ 评分分析失败: 没有成功分析的台区")


def _record_scoring_to_tracker(experiment_tracker, score_result: dict, 
                              base_id: str, setting_name: str) -> None:
    """
    将评分结果记录到实验追踪器
    """
    try:
        from src.tracking import GISExperimentResult
        
        original_score = score_result['original_score']
        treated_score = score_result['treated_score']
        improvement = treated_score['total_score'] - original_score['total_score']
        
        # 创建实验结果记录
        experiment_result = GISExperimentResult(
            experiment_id=f"scoring_{base_id}",
            timestamp=datetime.now().isoformat(),
            setting_name=setting_name,
            data_version="标注数据v1",
            evaluation_criteria="5项评分标准",
            beauty_score=treated_score['total_score'],
            improvement_score=improvement,
            dimension_scores={
                'overhead': treated_score.get('overhead', {}).get('total_score', 0),
                'cable_lines': treated_score.get('cable_lines', {}).get('total_score', 0),
                'branch_boxes': treated_score.get('branch_boxes', {}).get('total_score', 0),
                'access_points': treated_score.get('access_points', {}).get('total_score', 0),
                'meter_boxes': treated_score.get('meter_boxes', {}).get('total_score', 0)
            },
            model_name="scoring_analysis",
            algorithm_version="v1.0",
            prompt_version="v1.0",
            api_success_rate=1.0,
            json_parse_success_rate=1.0,
            processing_time=0.0,
            total_tokens=0,
            total_cost=0.0,
            is_best_attempt=True
        )
        
        experiment_tracker.log_experiment_result(experiment_result)
        
    except Exception as e:
        logging.warning(f"记录评分结果到追踪器失败: {e}")


def _generate_scoring_summary(scoring_results: list, output_dir: str, 
                            save_details: bool) -> None:
    """
    生成评分分析汇总报告
    """
    try:
        total_count = len(scoring_results)
        
        # 计算汇总统计
        original_scores = [r['original_score']['total_score'] for r in scoring_results]
        treated_scores = [r['treated_score']['total_score'] for r in scoring_results]
        improvements = [t - o for o, t in zip(original_scores, treated_scores)]
        
        avg_original = sum(original_scores) / total_count
        avg_treated = sum(treated_scores) / total_count
        avg_improvement = sum(improvements) / total_count
        avg_improvement_pct = (avg_improvement / max(avg_original, 0.1)) * 100
        
        # 改善统计
        improved_count = sum(1 for imp in improvements if imp > 0)
        unchanged_count = sum(1 for imp in improvements if imp == 0)
        degraded_count = sum(1 for imp in improvements if imp < 0)
        
        # 输出汇总日志
        logging.info("📈 评分分析汇总报告:")
        logging.info(f"   分析台区数量: {total_count}")
        logging.info(f"   平均治理前分数: {avg_original:.2f}分")
        logging.info(f"   平均治理后分数: {avg_treated:.2f}分")
        logging.info(f"   平均改善度: {avg_improvement:+.2f}分 ({avg_improvement_pct:+.1f}%)")
        logging.info(f"   改善台区: {improved_count} ({improved_count/total_count*100:.1f}%)")
        logging.info(f"   无变化台区: {unchanged_count} ({unchanged_count/total_count*100:.1f}%)")
        logging.info(f"   退化台区: {degraded_count} ({degraded_count/total_count*100:.1f}%)")
        
        # 保存汇总报告（如果启用）
        if save_details:
            summary_data = {
                'analysis_summary': {
                    'total_count': total_count,
                    'avg_original_score': avg_original,
                    'avg_treated_score': avg_treated,
                    'avg_improvement': avg_improvement,
                    'avg_improvement_percentage': avg_improvement_pct,
                    'improved_count': improved_count,
                    'unchanged_count': unchanged_count,
                    'degraded_count': degraded_count
                },
                'detailed_results': scoring_results,
                'timestamp': datetime.now().isoformat()
            }
            
            summary_path = Path(output_dir) / "评分分析汇总报告.json"
            with open(summary_path, 'w', encoding='utf-8') as f:
                import json
                json.dump(summary_data, f, ensure_ascii=False, indent=2)
            logging.info(f"   汇总报告已保存: {summary_path}")
            
    except Exception as e:
        logging.error(f"生成评分汇总报告失败: {e}")


def _upload_experiment_to_server(experiment_tracker: GISExperimentTracker, 
                                final_report: dict, output_dir: str) -> None:
    """
    上传实验数据到服务器（参考codespace/main.py的上传功能）
    
    Args:
        experiment_tracker: 实验追踪器实例
        final_report: 最终实验报告
        output_dir: 输出目录
    """
    try:
        import wandb
        import os
        from pathlib import Path
        
        logger = logging.getLogger(__name__)
        
        # 确保WandB已初始化
        if not experiment_tracker.wandb_run:
            logger.warning("WandB未初始化，跳过上传")
            return
        
        # 记录最终实验汇总到WandB
        if experiment_tracker.wandb_run and hasattr(experiment_tracker.wandb_run, 'log'):
            try:
                # 记录实验汇总统计
                experiment_summary = {
                    'total_experiment_results': len(experiment_tracker.experiment_results),
                    'total_api_calls': len(experiment_tracker.api_calls),
                    'experiment_duration': final_report.get('experiment_metadata', {}).get('duration', 0),
                    'setting_name': experiment_tracker.config.setting_name,
                    'model_name': experiment_tracker.config.model_name
                }
                
                # 如果有性能统计，添加到汇总中
                if 'performance_statistics' in final_report:
                    perf_stats = final_report['performance_statistics']
                    if 'beauty_score' in perf_stats:
                        experiment_summary.update({
                            'avg_beauty_score': perf_stats['beauty_score'].get('mean', 0),
                            'max_beauty_score': perf_stats['beauty_score'].get('max', 0),
                            'min_beauty_score': perf_stats['beauty_score'].get('min', 0)
                        })
                    if 'improvement_score' in perf_stats:
                        experiment_summary.update({
                            'avg_improvement_score': perf_stats['improvement_score'].get('mean', 0),
                            'max_improvement_score': perf_stats['improvement_score'].get('max', 0)
                        })
                
                # 记录到WandB
                wandb.log({
                    'experiment_final_summary': experiment_summary,
                    'final_report': final_report
                })
                
                logger.info(f"✅ 实验数据已上传到WandB服务器")
                logger.info(f"📊 实验结果数量: {experiment_summary['total_experiment_results']}")
                logger.info(f"🔗 API调用次数: {experiment_summary['total_api_calls']}")
                
                # 打印WandB访问链接
                if hasattr(experiment_tracker, 'wandb_run') and experiment_tracker.wandb_run:
                    wandb_url = experiment_tracker.wandb_run.url
                    if wandb_url:
                        logger.info("="*60)
                        logger.info("🌐 WandB实验追踪链接")
                        logger.info("="*60)
                        logger.info(f"📊 实验访问链接: {wandb_url}")
                        logger.info(f"📈 您可以通过上述链接查看详细的实验结果和可视化图表")
                        logger.info(f"🔍 包含：模型调用记录、评分详情、成本统计、性能指标等")
                        logger.info("="*60)
                    else:
                        logger.info(f"🌐 WandB实验ID: {experiment_tracker.wandb_run.id}")
                        logger.info(f"📈 请访问 https://wandb.ai 查看实验结果")
                
            except Exception as e:
                logger.warning(f"上传实验数据到WandB失败: {e}")
        
        # 保存本地实验数据备份
        try:
            experiment_data_dir = Path(output_dir) / 'experiment_data'
            experiment_data_dir.mkdir(exist_ok=True)
            
            # 保存实验报告
            report_path = experiment_data_dir / 'final_experiment_report.json'
            with open(report_path, 'w', encoding='utf-8') as f:
                import json
                json.dump(final_report, f, ensure_ascii=False, indent=2)
            
            # 保存实验配置
            config_path = experiment_data_dir / 'experiment_config.json'
            with open(config_path, 'w', encoding='utf-8') as f:
                import json
                from dataclasses import asdict
                json.dump(asdict(experiment_tracker.config), f, ensure_ascii=False, indent=2)
            
            logger.info(f"📁 实验数据本地备份已保存: {experiment_data_dir}")
            
        except Exception as e:
            logger.warning(f"保存本地实验数据备份失败: {e}")
        
        # 清理代理设置
        try:
            del os.environ['HTTP_PROXY']
            del os.environ['HTTPS_PROXY']
        except KeyError:
            pass
            
    except Exception as e:
        logger.error(f"上传实验数据到服务器失败: {e}")
        # 不抛出异常，避免影响主流程


def main() -> None:
    """
    主函数
    """
    try:
        # 解析命令行参数
        args = parse_arguments()
        
        # 设置日志
        setup_logging(args.log_level)
        logger = logging.getLogger(__name__)
        
        # 加载配置
        config = load_config(args.config)
        
        # 解析模型列表
        models = [m.strip() for m in args.models.split(',')]
        
        # 创建输出目录
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"电网台区美化治理与打分系统启动")
        logger.info(f"使用模型: {models}")
        logger.info(f"输出目录: {output_dir}")
        
        # 统一处理：自动识别单文件或批量目录
        process_areas(
            input_path=args.input,
            output_dir=str(output_dir),
            models=models,
            config=config,
            enable_tracking=args.enable_tracking,
            experiment_name=args.experiment_name,
            setting_name=args.setting_name,
            enable_scoring=args.enable_scoring,
            scoring_only=args.scoring_only,
            save_scoring_details=args.save_scoring_details,
            resume_run_id=args.resume_run_id,
            resume_mode=args.resume_mode
        )
        
        logger.info("处理完成")
        
    except KeyboardInterrupt:
        logger.warning("\n⚠️  用户中断操作")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ 系统错误: {e}")
        logging.error(f"系统错误: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    sys.argv = [
        "main.py",
        "--output", "D:\\work\\resGIS_qwen",
        "--enable-scoring",
        "--enable-tracking",
        "--save-scoring-details",
        "--resume-run-id", "eyunvwgr",
        "D:\\work\\dy_gis_mgx\\标注数据目录\\有对应关系的标注结果数据"
    ]
    main()