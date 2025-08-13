"""
WandB实验追踪器

提供完整的实验追踪和结果分析功能，用于记录API调用、评分结果和模型性能指标
"""

import time
import json
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime
import wandb
import pandas as pd
import numpy as np
from pathlib import Path
import os
from PIL import Image

# 配置日志
# logging.basicConfig(level=logging.INFO)  # 注释掉，使用main.py中的配置
logger = logging.getLogger(__name__)


@dataclass
class ExperimentConfig:
    """实验配置数据类"""
    experiment_name: str
    project_name: str = "grid-beautification"
    entity: Optional[str] = "dy_gis_mgx_"
    tags: List[str] = None
    notes: str = ""

    def __post_init__(self):
        if self.tags is None:
            self.tags = []


@dataclass
class APICallRecord:
    """API调用记录数据类"""
    model_name: str
    input_data_hash: str
    output_data_hash: str
    response_time: float
    success: bool
    error_message: Optional[str] = None
    cost: Optional[float] = None
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


@dataclass
class ScoringRecord:
    """评分记录数据类"""
    image_id: str
    model_name: str
    scores: Dict[str, float]
    human_scores: Optional[Dict[str, float]] = None
    improvement_metrics: Optional[Dict[str, float]] = None
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


class ExperimentTracker:
    """
    WandB实验追踪器

    提供完整的实验追踪和结果分析功能
    """

    def __init__(self, config: ExperimentConfig):
        """
        初始化实验追踪器

        Args:
            config: 实验配置
        """
        self.config = config
        self.wandb_run = None
        self.api_calls: List[APICallRecord] = []
        self.scoring_records: List[ScoringRecord] = []
        self.experiment_start_time = None
        
    def init_experiment(self) -> None:
        """
        初始化WandB实验
        
        Returns:
            None
        """
        import wandb
        self.experiment_start_time = time.time()
        
        try:
            # 自动登录wandb - 使用环境变量或交互式登录
            if not wandb.run:
                import os
                api_key = os.getenv('WANDB_API_KEY')
                if api_key:
                    wandb.login(key=api_key)
                    logger.info("使用环境变量WANDB_API_KEY登录WandB")
                else:
                    # 尝试使用已保存的登录信息
                    try:
                        wandb.login()
                        logger.info("使用已保存的登录信息登录WandB")
                    except Exception as login_e:
                        logger.warning(f"WandB登录失败: {login_e}，将使用离线模式")
            entity = self.config.entity or "dy_gis_mgx_"
            
            # 尝试在线模式
            try:
                self.wandb_run = wandb.init(
                    project=self.config.project_name,
                    name=self.config.experiment_name,
                    entity=entity,
                    tags=self.config.tags,
                    notes=self.config.notes,
                    config=asdict(self.config),
                    settings=wandb.Settings(
                        init_timeout=15  # 更短的超时时间
                    )
                )
                logger.info(f"WandB实验已在线初始化: {self.config.experiment_name}")
                return
            except Exception as e:
                logger.warning(f"WandB在线初始化失败({e})，尝试离线模式。")
            
            # 尝试离线模式
            try:
                self.wandb_run = wandb.init(
                    project=self.config.project_name,
                    name=self.config.experiment_name,
                    entity=entity,
                    tags=self.config.tags,
                    notes=self.config.notes,
                    config=asdict(self.config),
                    settings=wandb.Settings(
                        mode="offline",
                        init_timeout=5  # 离线模式更短超时
                    )
                )
                logger.info(f"WandB实验已离线初始化: {self.config.experiment_name}")
                return
            except Exception as e2:
                logger.warning(f"WandB离线模式也初始化失败({e2})，尝试禁用模式。")
            
            # 尝试禁用模式
            try:
                self.wandb_run = wandb.init(
                    project=self.config.project_name,
                    name=self.config.experiment_name,
                    entity=entity,
                    tags=self.config.tags,
                    notes=self.config.notes,
                    config=asdict(self.config),
                    settings=wandb.Settings(
                        mode="disabled",
                        init_timeout=1
                    )
                )
                logger.info(f"WandB实验已禁用模式初始化: {self.config.experiment_name}")
                return
            except Exception as e3:
                logger.error(f"WandB禁用模式也初始化失败({e3})，本地将不记录wandb日志。")
                self.wandb_run = None
                
        except Exception as e:
            logger.error(f"WandB实验初始化完全失败: {e}")
            self.wandb_run = None

    def log_api_call(self,
                     model_name: str,
                     input_data: Dict,
                     output: Dict,
                     metrics: Dict,
                     cost: Optional[float] = None) -> None:
        """
        记录API调用结果

        Args:
            model_name: 模型名称
            input_data: 输入数据
            output: 输出数据
            metrics: 性能指标
            cost: API调用成本
        """
        # 计算数据哈希
        input_hash = self._calculate_data_hash(input_data)
        output_hash = self._calculate_data_hash(output)

        # 创建API调用记录
        api_record = APICallRecord(
            model_name=model_name,
            input_data_hash=input_hash,
            output_data_hash=output_hash,
            response_time=metrics.get('response_time', 0.0),
            success=metrics.get('success', False),
            error_message=metrics.get('error_message'),
            cost=cost
        )

        self.api_calls.append(api_record)

        # 记录到WandB
        if self.wandb_run:
            wandb.log({
                f"{model_name}_api_call": {
                    "response_time": api_record.response_time,
                    "success": api_record.success,
                    "cost": api_record.cost or 0.0,
                    "input_hash": input_hash,
                    "output_hash": output_hash
                }
            })

        logger.info(f"API调用已记录: {model_name}, 响应时间: {api_record.response_time:.2f}s")

    def log_scoring_result(self,
                           image_id: str,
                           model_name: str,
                           scores: Dict[str, float],
                           human_scores: Optional[Dict[str, float]] = None,
                           before_image_path: Optional[str] = None,
                           after_image_path: Optional[str] = None,
                           result_image_path: Optional[str] = None) -> None:
        """
        记录评分结果

        Args:
            image_id: 图片ID
            model_name: 模型名称
            scores: AI评分结果
            human_scores: 人工评分结果
            before_image_path: 治理前图片路径（可选）
            after_image_path: 治理后图片路径（可选）
            result_image_path: 结果图片路径（可选）
        """
        # 计算改善指标
        improvement_metrics = None
        if human_scores:
            improvement_metrics = self._calculate_improvement_metrics(scores, human_scores)

        # 创建评分记录
        scoring_record = ScoringRecord(
            image_id=image_id,
            model_name=model_name,
            scores=scores,
            human_scores=human_scores,
            improvement_metrics=improvement_metrics
        )

        self.scoring_records.append(scoring_record)

        # 记录到WandB
        if self.wandb_run:
            # 记录各维度评分
            for dimension, score in scores.items():
                wandb.log({
                    f"{model_name}_{dimension}_score": score,
                    "image_id": image_id
                })

            # 记录改善指标
            if improvement_metrics:
                for metric_name, metric_value in improvement_metrics.items():
                    wandb.log({
                        f"{model_name}_{metric_name}": metric_value,
                        "image_id": image_id
                    })

        # 上传相关图片
        if before_image_path and after_image_path:
            self.log_image_comparison(
                before_image_path=before_image_path,
                after_image_path=after_image_path,
                image_id=image_id,
                model_name=model_name
            )
        elif result_image_path:
            self.log_image(
                image_path=result_image_path,
                caption=f"评分结果图片 - {image_id} ({model_name})",
                image_type="scoring_result"
            )
        elif before_image_path:
            self.log_image(
                image_path=before_image_path,
                caption=f"原始图片 - {image_id}",
                image_type="original"
            )
        elif after_image_path:
            self.log_image(
                image_path=after_image_path,
                caption=f"处理后图片 - {image_id} ({model_name})",
                image_type="processed"
            )

        logger.info(f"评分结果已记录: {image_id}, 模型: {model_name}")

    def log_image(self, 
                  image_path: str, 
                  caption: str = "", 
                  step: Optional[int] = None,
                  image_type: str = "result") -> None:
        """
        上传图片到WandB
        
        Args:
            image_path: 图片文件路径
            caption: 图片说明
            step: 步骤编号
            image_type: 图片类型 (original, processed, result, comparison等)
        """
        if not self.wandb_run:
            logger.warning("WandB未初始化，无法上传图片")
            return
            
        try:
            # 检查文件是否存在
            if not os.path.exists(image_path):
                logger.error(f"图片文件不存在: {image_path}")
                return
                
            # 获取图片信息
            image_name = os.path.basename(image_path)
            
            # 上传图片
            wandb_image = wandb.Image(
                image_path, 
                caption=caption or image_name
            )
            
            # 记录到WandB
            log_data = {f"{image_type}_image": wandb_image}
            if step is not None:
                wandb.log(log_data, step=step)
            else:
                wandb.log(log_data)
                
            logger.info(f"图片已上传到WandB: {image_name}, 类型: {image_type}")
            
        except Exception as e:
            logger.error(f"上传图片失败: {e}")
    
    def log_image_comparison(self,
                           before_image_path: str,
                           after_image_path: str,
                           image_id: str,
                           model_name: str = "",
                           step: Optional[int] = None) -> None:
        """
        上传对比图片（治理前后对比）
        
        Args:
            before_image_path: 治理前图片路径
            after_image_path: 治理后图片路径
            image_id: 图片ID
            model_name: 模型名称
            step: 步骤编号
        """
        if not self.wandb_run:
            logger.warning("WandB未初始化，无法上传对比图片")
            return
            
        try:
            # 检查文件是否存在
            if not os.path.exists(before_image_path):
                logger.error(f"治理前图片不存在: {before_image_path}")
                return
            if not os.path.exists(after_image_path):
                logger.error(f"治理后图片不存在: {after_image_path}")
                return
                
            # 创建对比图片
            before_image = wandb.Image(
                before_image_path, 
                caption=f"治理前 - {image_id}"
            )
            after_image = wandb.Image(
                after_image_path, 
                caption=f"治理后 - {image_id} ({model_name})"
            )
            
            # 记录到WandB
            log_data = {
                f"comparison_{image_id}_before": before_image,
                f"comparison_{image_id}_after": after_image,
                "image_id": image_id
            }
            
            if model_name:
                log_data["model_name"] = model_name
                
            if step is not None:
                wandb.log(log_data, step=step)
            else:
                wandb.log(log_data)
                
            logger.info(f"对比图片已上传到WandB: {image_id}, 模型: {model_name}")
            
        except Exception as e:
            logger.error(f"上传对比图片失败: {e}")
    
    def log_batch_images(self,
                        image_paths: List[str],
                        captions: Optional[List[str]] = None,
                        image_type: str = "batch",
                        step: Optional[int] = None) -> None:
        """
        批量上传图片
        
        Args:
            image_paths: 图片路径列表
            captions: 图片说明列表
            image_type: 图片类型
            step: 步骤编号
        """
        if not self.wandb_run:
            logger.warning("WandB未初始化，无法批量上传图片")
            return
            
        if not image_paths:
            logger.warning("图片路径列表为空")
            return
            
        try:
            wandb_images = []
            
            for i, image_path in enumerate(image_paths):
                if not os.path.exists(image_path):
                    logger.warning(f"图片文件不存在，跳过: {image_path}")
                    continue
                    
                caption = ""
                if captions and i < len(captions):
                    caption = captions[i]
                else:
                    caption = os.path.basename(image_path)
                    
                wandb_image = wandb.Image(image_path, caption=caption)
                wandb_images.append(wandb_image)
            
            if wandb_images:
                log_data = {f"{image_type}_images": wandb_images}
                if step is not None:
                    wandb.log(log_data, step=step)
                else:
                    wandb.log(log_data)
                    
                logger.info(f"批量上传了 {len(wandb_images)} 张图片到WandB")
            else:
                logger.warning("没有有效的图片可上传")
                
        except Exception as e:
            logger.error(f"批量上传图片失败: {e}")

    def log_model_comparison(self, results: Dict[str, Dict]) -> None:
        """
        记录多模型对比结果

        Args:
            results: 多模型结果字典 {model_name: result_dict}
        """
        if not self.wandb_run:
            return

        # 记录模型对比指标
        for model_name, result in results.items():
            if 'scores' in result:
                for dimension, score in result['scores'].items():
                    wandb.log({
                        f"comparison_{dimension}_score": score,
                        "model": model_name
                    })

            if 'metrics' in result:
                for metric_name, metric_value in result['metrics'].items():
                    wandb.log({
                        f"comparison_{metric_name}": metric_value,
                        "model": model_name
                    })

    def generate_comparison_report(self) -> Dict[str, Any]:
        """
        生成对比分析报告

        Returns:
            Dict: 包含详细分析结果的字典
        """
        if not self.scoring_records:
            return {"error": "没有评分记录可供分析"}

        # 按模型分组
        model_records = {}
        for record in self.scoring_records:
            if record.model_name not in model_records:
                model_records[record.model_name] = []
            model_records[record.model_name].append(record)

        # 计算各模型统计指标
        model_stats = {}
        for model_name, records in model_records.items():
            stats = self._calculate_model_statistics(records)
            model_stats[model_name] = stats

        # 计算模型间对比
        comparison_metrics = self._calculate_model_comparison(model_records)

        # 生成报告
        report = {
            "experiment_info": {
                "name": self.config.experiment_name,
                "start_time": self.experiment_start_time,
                "total_records": len(self.scoring_records),
                "total_api_calls": len(self.api_calls)
            },
            "model_statistics": model_stats,
            "model_comparison": comparison_metrics,
            "api_performance": self._analyze_api_performance(),
            "recommendations": self._generate_recommendations(model_stats, comparison_metrics)
        }

        # 记录到WandB
        if self.wandb_run:
            wandb.log({"comparison_report": report})

        return report

    def save_experiment_data(self, output_dir: str = "experiment_data") -> None:
        """
        保存实验数据到本地文件
        
        Args:
            output_dir: 输出目录
        """
        try:
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)
            
            # 保存API调用记录
            if self.api_calls:
                api_calls_df = pd.DataFrame([asdict(record) for record in self.api_calls])
                api_calls_df.to_csv(output_path / "api_calls.csv", index=False, encoding='utf-8')
            
            # 保存评分记录
            if self.scoring_records:
                scoring_records_df = pd.DataFrame([asdict(record) for record in self.scoring_records])
                scoring_records_df.to_csv(output_path / "scoring_records.csv", index=False, encoding='utf-8')
            
            # 保存实验配置
            with open(output_path / "experiment_config.json", 'w', encoding='utf-8') as f:
                json.dump(asdict(self.config), f, ensure_ascii=False, indent=2)
            
            # 生成对比报告
            report = self.generate_comparison_report()
            with open(output_path / "comparison_report.json", 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            logger.info(f"实验数据已保存到: {output_path}")
        except PermissionError as e:
            logger.error(f"权限错误，无法保存到 {output_dir}: {e}")
            # 尝试保存到临时目录
            import tempfile
            temp_dir = Path(tempfile.gettempdir()) / "wandb_experiment_data"
            temp_dir.mkdir(exist_ok=True)
            
            try:
                # 保存API调用记录
                if self.api_calls:
                    api_calls_df = pd.DataFrame([asdict(record) for record in self.api_calls])
                    api_calls_df.to_csv(temp_dir / "api_calls.csv", index=False, encoding='utf-8')
                
                # 保存评分记录
                if self.scoring_records:
                    scoring_records_df = pd.DataFrame([asdict(record) for record in self.scoring_records])
                    scoring_records_df.to_csv(temp_dir / "scoring_records.csv", index=False, encoding='utf-8')
                
                # 保存实验配置
                with open(temp_dir / "experiment_config.json", 'w', encoding='utf-8') as f:
                    json.dump(asdict(self.config), f, ensure_ascii=False, indent=2)
                
                # 生成对比报告
                report = self.generate_comparison_report()
                with open(temp_dir / "comparison_report.json", 'w', encoding='utf-8') as f:
                    json.dump(report, f, ensure_ascii=False, indent=2)
                
                logger.info(f"实验数据已保存到临时目录: {temp_dir}")
            except Exception as e2:
                logger.error(f"保存到临时目录也失败: {e2}")
        except Exception as e:
            logger.error(f"保存实验数据时出错: {e}")

    def finish_experiment(self) -> None:
        """
        完成实验，关闭WandB运行
        """
        if self.wandb_run:
            # 记录最终统计
            if self.experiment_start_time:
                duration = time.time() - self.experiment_start_time
                wandb.log({"experiment_duration": duration})

            wandb.finish()
            logger.info("实验已完成，WandB运行已关闭")

    def _calculate_data_hash(self, data: Dict) -> str:
        """计算数据哈希值"""
        import hashlib
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.md5(data_str.encode()).hexdigest()

    def _calculate_improvement_metrics(self,
                                       ai_scores: Dict[str, float],
                                       human_scores: Dict[str, float]) -> Dict[str, float]:
        """
        计算AI评分与人工评分的改善指标

        Args:
            ai_scores: AI评分结果
            human_scores: 人工评分结果

        Returns:
            Dict: 改善指标
        """
        metrics = {}

        # 计算各维度的差异
        for dimension in ai_scores.keys():
            if dimension in human_scores:
                ai_score = ai_scores[dimension]
                human_score = human_scores[dimension]
                metrics[f"{dimension}_difference"] = ai_score - human_score
                metrics[f"{dimension}_relative_error"] = abs(
                    ai_score - human_score) / human_score if human_score != 0 else 0

        # 计算总体指标
        ai_total = sum(ai_scores.values())
        human_total = sum(human_scores.values())
        metrics["total_difference"] = ai_total - human_total
        metrics["total_relative_error"] = abs(ai_total - human_total) / human_total if human_total != 0 else 0

        return metrics

    def _calculate_model_statistics(self, records: List[ScoringRecord]) -> Dict[str, Any]:
        """
        计算模型统计指标

        Args:
            records: 评分记录列表

        Returns:
            Dict: 统计指标
        """
        if not records:
            return {}

        # 提取所有评分维度
        all_dimensions = set()
        for record in records:
            all_dimensions.update(record.scores.keys())

        stats = {
            "total_records": len(records),
            "dimension_statistics": {}
        }

        # 计算各维度的统计指标
        for dimension in all_dimensions:
            scores = [record.scores.get(dimension, 0) for record in records]
            stats["dimension_statistics"][dimension] = {
                "mean": np.mean(scores),
                "std": np.std(scores),
                "min": np.min(scores),
                "max": np.max(scores),
                "median": np.median(scores)
            }

        # 计算总体评分统计
        total_scores = [sum(record.scores.values()) for record in records]
        stats["total_score_statistics"] = {
            "mean": np.mean(total_scores),
            "std": np.std(total_scores),
            "min": np.min(total_scores),
            "max": np.max(total_scores),
            "median": np.median(total_scores)
        }

        return stats

    def _calculate_model_comparison(self, model_records: Dict[str, List[ScoringRecord]]) -> Dict[str, Any]:
        """
        计算模型间对比指标

        Args:
            model_records: 按模型分组的记录

        Returns:
            Dict: 对比指标
        """
        if len(model_records) < 2:
            return {}

        comparison = {
            "model_names": list(model_records.keys()),
            "dimension_comparisons": {}
        }

        # 获取所有维度
        all_dimensions = set()
        for records in model_records.values():
            for record in records:
                all_dimensions.update(record.scores.keys())

        # 计算各维度的模型间对比
        for dimension in all_dimensions:
            dimension_scores = {}
            for model_name, records in model_records.items():
                scores = [record.scores.get(dimension, 0) for record in records]
                dimension_scores[model_name] = {
                    "mean": np.mean(scores),
                    "std": np.std(scores),
                    "count": len(scores)
                }
            comparison["dimension_comparisons"][dimension] = dimension_scores

        return comparison

    def _analyze_api_performance(self) -> Dict[str, Any]:
        """
        分析API性能指标

        Returns:
            Dict: API性能分析
        """
        if not self.api_calls:
            return {}

        # 按模型分组
        model_calls = {}
        for call in self.api_calls:
            if call.model_name not in model_calls:
                model_calls[call.model_name] = []
            model_calls[call.model_name].append(call)

        performance = {}
        for model_name, calls in model_calls.items():
            response_times = [call.response_time for call in calls]
            success_rate = sum(1 for call in calls if call.success) / len(calls)
            total_cost = sum(call.cost or 0 for call in calls)

            performance[model_name] = {
                "total_calls": len(calls),
                "success_rate": success_rate,
                "avg_response_time": np.mean(response_times),
                "max_response_time": np.max(response_times),
                "min_response_time": np.min(response_times),
                "total_cost": total_cost,
                "avg_cost_per_call": total_cost / len(calls) if calls else 0
            }

        return performance

    def _generate_recommendations(self,
                                  model_stats: Dict[str, Any],
                                  comparison: Dict[str, Any]) -> List[str]:
        """
        基于分析结果生成建议

        Args:
            model_stats: 模型统计
            comparison: 模型对比

        Returns:
            List[str]: 建议列表
        """
        recommendations = []

        # 分析模型性能
        for model_name, stats in model_stats.items():
            if stats.get("total_records", 0) > 0:
                total_mean = stats.get("total_score_statistics", {}).get("mean", 0)
                if total_mean < 60:
                    recommendations.append(f"{model_name}的平均评分较低({total_mean:.1f})，建议优化评分算法")

        # 分析API性能
        api_performance = self._analyze_api_performance()
        for model_name, perf in api_performance.items():
            if perf.get("success_rate", 1) < 0.9:
                recommendations.append(f"{model_name}的API成功率较低({perf['success_rate']:.1%})，建议检查API稳定性")

            if perf.get("avg_response_time", 0) > 30:
                recommendations.append(
                    f"{model_name}的平均响应时间较长({perf['avg_response_time']:.1f}s)，建议优化网络连接")

        return recommendations


def create_experiment_tracker(experiment_name: str,
                              project_name: str = "grid-beautification",
                              **kwargs) -> ExperimentTracker:
    """
    创建实验追踪器的便捷函数

    Args:
        experiment_name: 实验名称
        project_name: 项目名称
        **kwargs: 其他配置参数

    Returns:
        ExperimentTracker: 实验追踪器实例
    """
    config = ExperimentConfig(
        experiment_name=experiment_name,
        project_name=project_name,
        **kwargs
    )

    tracker = ExperimentTracker(config)
    tracker.init_experiment()

    return tracker