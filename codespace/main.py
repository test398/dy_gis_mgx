# 主流程
import base64
import os
import time
import multiprocessing as mp
from functools import partial
import time
import wandb
from pathlib import Path
from beautification import beautification_pipeline
from evaluation import evaluation_pipeline


import wandb
import time
def log_beautification_results(prompt, input_data, output_data, beauty_score, model_name, image_path, input_tokens, output_tokens):
    """ 核心功能：追踪治理过程的关键指标"""
    # 各模型价格（每 1M tokens）- 自行修改
    pricing = {'qwen-vl-max': {'input': 0.1, 'output': 0.3}}
    cost = (input_tokens * pricing[model_name]['input'] / 1e6 + output_tokens * pricing[model_name]['output'] / 1e6)
    results_dict = {
        # 业务指标
        "beauty_score": beauty_score,
        "input_devices": len(input_data),
        "output_devices": len(output_data),
        "improvement": len(output_data) - len(input_data),
        # 成本指标（重要！）
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_cost_usd": cost,
        "cost_per_device": cost / len(input_data) if len(input_data) > 0 else 0,
        # 模型信息
        "model_name": model_name,
        "prompt_length": len(prompt),
        # 可视化
        "input_image": wandb.Image(image_path) if image_path else None,
    }
    # 记录所有关键数据
    wandb.log(results_dict)
    return results_dict

def call_beautification_function(image_path, image_data, model):
    """ 统一的美化治理 API 调用函数"""
    # 调用治理模型
    if 'qwen' in model:
        treatment_result = beautification_pipeline(image_path, image_data)
    # 计算美观性评分
    beauty_score = evaluation_pipeline(treatment_result)
    return {
        'input_data': image_data,
        'output_data': treatment_result['output_data'],
        'beauty_score': beauty_score,
        'input_tokens': treatment_result['input_tokens'],
        'output_tokens': treatment_result['output_tokens'],
        }

def process_single_image(task_data):
    """ 处理单张图像的工作函数"""
    image_path, image_data, model = task_data
    # 调用美化治理 API
    start_time = time.perf_counter()
    result = call_beautification_function(image_path, image_data, model)
    process_time = time.perf_counter() - start_time
    input_data = result['input_data']
    output_data = result['output_data']
    beauty_score = result['beauty_score']
    # 返回结果数据（不在子进程中调用 wandb）
    return {
        'image_path': str(image_path),
        'model': model,
        'input_data': input_data,
        'output_data': output_data,
        'beauty_score': beauty_score,
        'process_time': process_time,
        'input_tokens': result.get('input_tokens', 1500),
        'output_tokens': result.get('output_tokens', 800)
    }


def load_images_to_list(image_dir):
    """
    读取指定文件夹下所有图片，返回 [(图片路径, base64内容), ...] 列表
    """
    image_list = []
    image_dir = Path(image_dir)
    for img_path in image_dir.glob("*.*"):
        if img_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp', '.gif']:
            with open(img_path, "rb") as f:
                img_bytes = f.read()
                img_b64 = base64.b64encode(img_bytes).decode('utf-8')
                image_list.append((str(img_path), img_b64))
    return image_list


def process_batch_with_tracking(input_list, models=['qwen-vl-max'], max_workers=4):
    """ 批量处理多张图像，使用 multiprocessing 并行"""
    # 初始化 WandB（主进程）  国内需要配置代理才能访问wandb
    os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
    os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'
    wandb.init(project="gis-beautification", reinit=True)
    del os.environ['HTTP_PROXY']
    del os.environ['HTTPS_PROXY']
    # 准备任务列表
    tasks = []
    for image_path, image_data in input_list[:5]: # 限制 5 张图测试
        for model in models:
            tasks.append((image_path, image_data, model))
    # 使用进程池并行处理
    with mp.Pool(processes=max_workers) as pool:
        results = pool.map(process_single_image, tasks)
    # 在主进程中记录所有结果到 WandB
    for result in results:
        log_result = log_beautification_results(
                        prompt=" 治理设备位置...",
                        input_data=result['input_data'],
                        output_data=result['output_data'],
                        beauty_score=result['beauty_score'],
                        model_name=result['model'],
                        image_path=result['image_path'],
                        input_tokens=result['input_tokens'],
                        output_tokens=result['output_tokens']
                    )
    # 记录批量处理汇总
    wandb.log({
        'batch_images_count': len(set(r['image_path'] for r in results)),
        'batch_avg_beauty_score': sum(r['beauty_score'] for r in results) / len(results)
        })
    wandb.finish()
    return results


if __name__ == "__main__":
    inputs = load_images_to_list("标注数据目录/治理前标注图片/images")
    process_batch_with_tracking(inputs)