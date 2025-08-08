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

def setup_logging(log_level: str = "INFO") -> None:
    """
    配置日志系统
    
    Args:
        log_level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
        """
    os.makedirs('logs', exist_ok=True)
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        handlers=[
            logging.StreamHandler(),
            # TODO: 添加文件日志处理器
            logging.FileHandler(filename=f'logs/system_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
        ]
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
        '--enable-wandb',
        action='store_true',
        help='启用WandB实验追踪'
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

def process_areas(input_path: str, output_dir: str, models: list, config: dict) -> None:
    """
    处理台区数据 (自动识别单文件或批量目录)
    
    Args:
        input_path: 输入文件路径或目录路径
        output_dir: 输出目录
        models: 模型列表
        config: 配置字典
    """
    from pathlib import Path
    
    input_path_obj = Path(input_path)
    
    if not input_path_obj.exists():
        raise FileNotFoundError(f"输入路径不存在: {input_path}")
    
    if input_path_obj.is_file():
        # 单文件处理 (batch size = 1)
        print(f"🎯 处理单个台区文件: {input_path}")
        input_files = [input_path_obj]
    elif input_path_obj.is_dir():
        # 批量处理 (扫描目录中的所有JSON文件)
        input_files = list(input_path_obj.glob("*.json"))[:20]  # TODO 测试批量运行前五个文件
        print(f"🎯 批量处理台区目录: {input_path}")
        print(f"📋 发现 {len(input_files)} 个数据文件")
    else:
        raise ValueError(f"输入路径既不是文件也不是目录: {input_path}")
    
    if not input_files:
        raise ValueError("未找到任何.json数据文件")
    
    print(f"📊 使用模型: {models}")
    print(f"📁 输出目录: {output_dir}")
    print(f"🔄 并行数: {config['processing']['max_workers']}")
    
    # TODO: 实现统一处理逻辑
    # 1. 加载所有GIS数据文件
    # 2. 创建BatchInput (即使只有1个文件)
    # 3. 调用core.pipeline.process_batch
    # 4. 保存结果
    
    from core.pipeline import process_batch
    from core.data_types import BatchInput, ImageInput, GISData
    from data.input_loader import load_gis_data_from_json
    from data.output_saver import save_batch_results
    # 
    # # 加载所有数据文件并创建ImageInput列表
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
    # # 调用批处理
    if inputs:
        batch_result = process_batch(
            batch_input, 
            models=models,
            max_workers=config['processing']['max_workers']
        )
        # 保存结果到输出目录
        save_batch_results(batch_result, output_dir)
    else:
        logging.info("本次无需治理：全部台区均已存在治理结果与对比图")

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
            logging.info("================ 最终汇总（流程结束） ================")
            logging.info(f"批量处理完成，总成本: ${batch_result.summary.total_cost:.4f}")
            logging.info(f"成功率: {batch_result.summary.success_rate:.1f}%")
            run_id = getattr(batch_result, 'wandb_run_id', None)
            if run_id:
                logging.info(f"WandB运行ID: {run_id}")
            logging.info("=================================================")
        else:
            logging.info("================ 最终汇总（流程结束） ================")
            logging.info("本次未执行治理或无批量汇总可用")
            logging.info("=================================================")
    except Exception:
        pass
 

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
        process_areas(args.input, str(output_dir), models, config)
        
        logger.info("处理完成")
        
    except KeyboardInterrupt:
        print("\n⚠️  用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 系统错误: {e}")
        logging.error(f"系统错误: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    sys.argv = [
        "main.py",
        "--output", "D:\\work\\resGIS",
        "D:\\work\\dy_gis_mgx\\标注数据目录\\有对应关系的标注结果数据"
    ]
    main()