import json
import logging
import os
import time
import gc
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# 确保可同时支持 `from core...` 与 `from src.core...` 的导入路径
from src.import_helper import setup_import_path
setup_import_path()

from src.data.input_loader import load_gis_data_from_json
from src.data.output_saver import save_batch_results
from src.core.pipeline import process_batch
from src.core.data_types import BatchInput, ImageInput


logger = logging.getLogger(__name__)


def _load_resume_state(resume_path: Path) -> Set[str]:
    """
    加载断点续传状态文件，返回已处理文件名集合（含后缀）
    """
    if not resume_path.exists():
        return set()
    try:
        with open(resume_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        processed: List[str] = data.get('processed_files', [])
        return set(processed)
    except Exception as e:
        logger.warning(f"加载断点文件失败，将从头开始: {e}")
        return set()


def _save_resume_state(resume_path: Path, processed_files: Set[str], meta: Optional[Dict] = None) -> None:
    """
    保存断点续传状态文件
    """
    payload = {
        'processed_files': sorted(list(processed_files)),
        'meta': meta or {},
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    with open(resume_path, 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def _scan_input_files(input_dir: Path) -> List[Path]:
    """
    扫描输入目录中的.json文件（仅当前目录层级）
    """
    return sorted(input_dir.glob('*.json'))


def _build_batch_input(file_paths: List[Path], config: Dict) -> BatchInput:
    """
    将一批文件构造成 BatchInput
    """
    inputs: List[ImageInput] = []
    for file_path in file_paths:
        gis_data = load_gis_data_from_json(file_path)
        image_input = ImageInput(
            gis_data=gis_data,
            input_id=file_path.stem,
            json_path=str(file_path)
        )
        inputs.append(image_input)
    batch_input = BatchInput(
        inputs=inputs,
        config=config,
        batch_id=f"batch_{int(time.time())}_{len(inputs)}"
    )
    return batch_input


def bulk_process_directory(
    input_dir: str,
    output_dir: str,
    *,
    models: List[str],
    config: Dict,
    chunk_size: int = 50,
    max_workers: int = 4,
    resume_file: Optional[str] = None,
    enable_wandb: bool = True
) -> Dict[str, float]:
    """
    阶段3：批量处理系统（支持断点续传/进度追踪/资源控制）

    Args:
        input_dir: 输入目录（包含大量台区.json）
        output_dir: 输出目录
        models: 使用的模型列表
        config: 处理配置（会传入到BatchInput和process_batch）
        chunk_size: 每批处理的文件数量（控制内存占用）
        max_workers: 并行进程数
        resume_file: 断点续传状态文件路径（默认存放于输出目录）
        enable_wandb: 是否启用WandB

    Returns:
        Dict[str, float]: 汇总信息 {"total_time_sec": float, "total_cost": float}
    """
    start_t = time.perf_counter()

    input_dir_path = Path(input_dir)
    output_dir_path = Path(output_dir)
    output_dir_path.mkdir(parents=True, exist_ok=True)

    if resume_file is None:
        resume_path = output_dir_path / 'bulk_resume_state.json'
    else:
        resume_path = Path(resume_file)

    all_files = _scan_input_files(input_dir_path)
    processed_files = _load_resume_state(resume_path)

    pending_files: List[Path] = [p for p in all_files if p.name not in processed_files]

    logger.info(f"批量处理启动：输入目录={input_dir_path}，输出目录={output_dir_path}")
    logger.info(f"共发现 {len(all_files)} 个文件，已处理 {len(processed_files)} 个，待处理 {len(pending_files)} 个")
    logger.info(f"参数：chunk_size={chunk_size}，max_workers={max_workers}，models={models}")

    total_cost = 0.0
    total_images = 0

    for start in range(0, len(pending_files), chunk_size):
        end = min(start + chunk_size, len(pending_files))
        chunk = pending_files[start:end]
        logger.info(f"处理批次：{start//chunk_size + 1}/{(len(pending_files)+chunk_size-1)//chunk_size}，文件数={len(chunk)}")

        # 构建批输入
        batch_input = _build_batch_input(chunk, config)

        # 调用批处理
        batch_result = process_batch(
            batch_input=batch_input,
            models=models,
            max_workers=max_workers,
            enable_wandb=enable_wandb
        )

        # 保存结果
        save_batch_results(batch_result, str(output_dir_path))

        # 更新统计
        if batch_result.summary:
            total_cost += getattr(batch_result.summary, 'total_cost', 0.0)
            total_images += getattr(batch_result.summary, 'total_images', 0)

        # 标记已处理文件并保存断点
        processed_files.update([p.name for p in chunk])
        _save_resume_state(
            resume_path,
            processed_files,
            meta={
                'last_batch_id': batch_result.batch_id,
                'processed_count': len(processed_files)
            }
        )

        # 回收内存
        del batch_input
        del batch_result
        gc.collect()

        logger.info(f"批次处理完成：累计已处理 {len(processed_files)}/{len(all_files)}")

    elapsed = time.perf_counter() - start_t
    logger.info(f"批量处理完成：总文件数={len(all_files)}，成功提交={total_images}，总成本=${total_cost:.4f}")
    logger.info(f"用时：{elapsed:.2f} 秒")

    return {
        'total_time_sec': elapsed,
        'total_cost': total_cost,
        'total_files': float(len(all_files)),
        'processed_files': float(len(processed_files))
    }


if __name__ == '__main__':
    # 简单CLI：适合快速测试；生产可接入主入口的参数解析
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # 示例配置（可替换为argparse动态传参）
    input_dir = '标注数据目录/有对应关系的标注结果数据'
    output_dir = 'resGIS'
    models = ['qwen']
    config = {
        'processing': {
            'max_workers': 4
        }
    }

    summary = bulk_process_directory(
        input_dir=input_dir,
        output_dir=output_dir,
        models=models,
        config=config,
        chunk_size=50,
        max_workers=config['processing']['max_workers'],
        resume_file=None,
        enable_wandb=True
    )
    logger.info(f"汇总: {summary}") 