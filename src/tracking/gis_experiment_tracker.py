"""
电网台区美化系统 - WandB实验追踪器

基于WandB实验追踪方案 - 20250807.md的要求实现
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

from wandb import Settings
# 配置日志
# logging.basicConfig(level=logging.INFO)  # 注释掉，使用main.py中的配置
logger = logging.getLogger(__name__)


@dataclass
class GISExperimentConfig:
    """GIS实验配置"""
    experiment_id: str
    setting_name: str  # Setting_A, Setting_B, Setting_C等
    data_version: str  # 标注数据v1, 标注数据v2, 扩展数据集等
    evaluation_criteria: str  # 5项评分标准, 改进评价标准, 完整评价体系等
    model_name: str = "qwen-vl-max"
    algorithm_version: str = "v1.0"
    prompt_version: str = "v1.0"
    project_name: str = "gis-beautification"
    entity: Optional[str] = None
    tags: List[str] = None
    notes: str = ""
    # WandB恢复相关参数
    resume_run_id: Optional[str] = None  # 要恢复的运行ID
    resume_mode: str = "allow"  # 恢复模式: "allow", "must", "never"

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if not self.tags:
            self.tags = [self.data_version, self.evaluation_criteria]


@dataclass
class GISExperimentResult:
    """GIS实验结果数据类"""
    experiment_id: str
    timestamp: str
    setting_name: str
    data_version: str
    evaluation_criteria: str
    
    # 性能指标
    beauty_score: float  # 美观性总分 (0-100)
    improvement_score: float  # 治理提升分数
    dimension_scores: Dict[str, float]  # 5维度分项分数
    
    # 算法信息
    model_name: str
    algorithm_version: str
    prompt_version: str
    
    # 成功率指标
    api_success_rate: float = 1.0
    json_parse_success_rate: float = 1.0
    
    # 处理时间
    processing_time: float = 0.0
    
    # 成本指标
    total_tokens: int = 0
    total_cost: float = 0.0
    
    # 是否是最佳尝试
    is_best_attempt: bool = False
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


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
    tokens_used: Optional[int] = None
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


class GISExperimentTracker:
    """
    电网台区美化系统WandB实验追踪器
    
    提供完整的实验追踪和结果分析功能，支持Setting分组和性能指标追踪
    """
    
    def __init__(self, config: GISExperimentConfig):
        """
        初始化GIS实验追踪器
        
        Args:
            config: GIS实验配置
        """
        self.config = config
        self.wandb_run = None
        self.api_calls: List[APICallRecord] = []
        self.experiment_results: List[GISExperimentResult] = []
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
            
            # 准备WandB初始化参数
            init_params = {
                "project": self.config.project_name,
                "name": self.config.experiment_id,
                "group": self.config.setting_name,  # 按Setting分组
                "entity": entity,
                "tags": self.config.tags,
                "notes": self.config.notes,
                "config": asdict(self.config),
                "settings": wandb.Settings(
                    init_timeout=15,
                    silent=True,  # 减少输出信息
                    console="off"  # 关闭控制台输出
                )
            }
            
            # 添加resume相关参数
            if self.config.resume_run_id and self.config.resume_mode != "never":
                init_params["id"] = self.config.resume_run_id
                init_params["resume"] = self.config.resume_mode
                logger.info(f"尝试恢复WandB运行: {self.config.resume_run_id} (模式: {self.config.resume_mode})")
            
            # 尝试在线模式
            try:
                self.wandb_run = wandb.init(**init_params)
                logger.info(f"GIS实验已在线初始化: {self.config.experiment_id} (Setting: {self.config.setting_name})")
                return
            except Exception as e:
                logger.warning(f"WandB在线初始化失败({e})，尝试离线模式。")
            
            # 尝试离线模式
            try:
                offline_params = init_params.copy()
                offline_params["settings"] = wandb.Settings(
                    mode="offline",
                    init_timeout=5,
                    silent=True,
                    console="off"
                )
                self.wandb_run = wandb.init(**offline_params)
                logger.info(f"GIS实验已离线初始化: {self.config.experiment_id} (Setting: {self.config.setting_name})")
                return
            except Exception as e2:
                logger.warning(f"WandB离线模式也初始化失败({e2})，尝试禁用模式。")
            
            # 尝试禁用模式
            try:
                self.wandb_run = wandb.init(
                    project=self.config.project_name,
                    name=self.config.experiment_id,
                    group=self.config.setting_name,
                    entity=entity,
                    tags=self.config.tags,
                    notes=self.config.notes,
                    config=asdict(self.config),
                    settings=wandb.Settings(
                        mode="disabled",
                        init_timeout=1,
                        silent=True,
                        console="off"
                    )
                )
                logger.info(f"GIS实验已禁用模式初始化: {self.config.experiment_id} (Setting: {self.config.setting_name})")
                return
            except Exception as e3:
                logger.error(f"WandB禁用模式也初始化失败({e3})，本地将不记录wandb日志。")
                self.wandb_run = None
                
        except Exception as e:
            logger.error(f"GIS实验初始化完全失败: {e}")
            self.wandb_run = None
    
    def log_api_call(self, 
                     model_name: str, 
                     input_data: Dict, 
                     output: Dict, 
                     metrics: Dict,
                     cost: Optional[float] = None,
                     tokens_used: Optional[int] = None) -> None:
        """
        记录API调用结果
        
        Args:
            model_name: 模型名称
            input_data: 输入数据
            output: 输出数据
            metrics: 性能指标
            cost: API调用成本
            tokens_used: 使用的token数量
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
            cost=cost,
            tokens_used=tokens_used
        )
        
        self.api_calls.append(api_record)
        
        # 记录到WandB（仅在正确初始化且非禁用模式下）
        if self.wandb_run and hasattr(self.wandb_run, 'log') and wandb.run is not None:
            try:
                # 确保WandB运行状态正常
                if hasattr(wandb.run, 'mode') and wandb.run.mode != 'disabled':
                    wandb.log({
                        f"{model_name}_api_call": {
                            "response_time": api_record.response_time,
                            "success": api_record.success,
                            "cost": api_record.cost or 0.0,
                            "tokens_used": api_record.tokens_used or 0,
                            "input_hash": input_hash,
                            "output_hash": output_hash
                        }
                    })
                elif hasattr(wandb.run, 'mode'):
                    logger.debug(f"WandB处于禁用模式，跳过API调用记录: {model_name}")
                else:
                    # 如果没有mode属性，尝试直接记录
                    wandb.log({
                        f"{model_name}_api_call": {
                            "response_time": api_record.response_time,
                            "success": api_record.success,
                            "cost": api_record.cost or 0.0,
                            "tokens_used": api_record.tokens_used or 0,
                            "input_hash": input_hash,
                            "output_hash": output_hash
                        }
                    })
            except Exception as e:
                logger.warning(f"记录API调用到WandB失败: {e}")
        
        logger.info(f"API调用已记录: {model_name}, 响应时间: {api_record.response_time:.2f}s")
    
    def log_experiment_result(self,
                             beauty_score: float,
                             improvement_score: float,
                             dimension_scores: Dict[str, float],
                             api_success_rate: float = 1.0,
                             json_parse_success_rate: float = 1.0,
                             processing_time: float = 0.0,
                             total_tokens: int = 0,
                             total_cost: float = 0.0,
                             is_best_attempt: bool = False) -> None:
        """
        记录GIS实验结果
        
        Args:
            beauty_score: 美观性总分 (0-100)
            improvement_score: 治理提升分数
            dimension_scores: 5维度分项分数
            api_success_rate: API成功率
            json_parse_success_rate: JSON解析成功率
            processing_time: 处理时间
            total_tokens: 总token数
            total_cost: 总成本
            is_best_attempt: 是否是最佳尝试
        """
        # 创建实验结果记录
        result = GISExperimentResult(
            experiment_id=self.config.experiment_id,
            timestamp=datetime.now().isoformat(),
            setting_name=self.config.setting_name,
            data_version=self.config.data_version,
            evaluation_criteria=self.config.evaluation_criteria,
            beauty_score=beauty_score,
            improvement_score=improvement_score,
            dimension_scores=dimension_scores,
            model_name=self.config.model_name,
            algorithm_version=self.config.algorithm_version,
            prompt_version=self.config.prompt_version,
            api_success_rate=api_success_rate,
            json_parse_success_rate=json_parse_success_rate,
            processing_time=processing_time,
            total_tokens=total_tokens,
            total_cost=total_cost,
            is_best_attempt=is_best_attempt
        )
        
        self.experiment_results.append(result)
        
        # 记录到WandB（仅在非禁用模式下）
        if self.wandb_run and hasattr(self.wandb_run, 'log'):
            try:
                # 记录主要性能指标
                wandb.log({
                    "beauty_score": beauty_score,
                    "improvement_score": improvement_score,
                    "api_success_rate": api_success_rate,
                    "json_parse_success_rate": json_parse_success_rate,
                    "processing_time": processing_time,
                    "total_tokens": total_tokens,
                    "total_cost": total_cost,
                    "is_best_attempt": is_best_attempt
                })
                
                # 记录各维度分数
                for dimension, score in dimension_scores.items():
                    wandb.log({f"dimension_{dimension}": score})
                
                # 记录Setting信息
                wandb.log({
                    "setting_name": self.config.setting_name,
                    "data_version": self.config.data_version,
                    "evaluation_criteria": self.config.evaluation_criteria
                })
            except Exception as e:
                logger.warning(f"记录实验结果到WandB失败: {e}")
        
        logger.info(f"GIS实验结果已记录: {self.config.experiment_id}, 美观性总分: {beauty_score:.1f}")
    
    def log_model_comparison(self, results: Dict[str, Dict]) -> None:
        """
        记录多模型对比结果
        
        Args:
            results: 多模型结果字典 {model_name: result_dict}
        """
        if not self.wandb_run or not hasattr(self.wandb_run, 'log'):
            return
        
        try:
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
        except Exception as e:
            logger.warning(f"记录模型对比结果到WandB失败: {e}")
    
    def generate_experiment_report(self) -> Dict[str, Any]:
        """
        生成实验报告
        
        Returns:
            Dict: 包含详细分析结果的字典
        """
        if not self.experiment_results:
            return {"error": "没有实验结果可供分析"}
        
        # 计算统计指标
        beauty_scores = [r.beauty_score for r in self.experiment_results]
        improvement_scores = [r.improvement_score for r in self.experiment_results]
        
        # 计算各维度统计
        dimension_stats = {}
        if self.experiment_results:
            all_dimensions = set()
            for result in self.experiment_results:
                all_dimensions.update(result.dimension_scores.keys())
            
            for dimension in all_dimensions:
                scores = [r.dimension_scores.get(dimension, 0) for r in self.experiment_results]
                dimension_stats[dimension] = {
                    "mean": np.mean(scores),
                    "std": np.std(scores),
                    "min": np.min(scores),
                    "max": np.max(scores),
                    "median": np.median(scores)
                }
        
        # 生成报告
        report = {
            "experiment_info": {
                "experiment_id": self.config.experiment_id,
                "setting_name": self.config.setting_name,
                "data_version": self.config.data_version,
                "evaluation_criteria": self.config.evaluation_criteria,
                "start_time": self.experiment_start_time,
                "total_results": len(self.experiment_results),
                "total_api_calls": len(self.api_calls)
            },
            "performance_statistics": {
                "beauty_score": {
                    "mean": np.mean(beauty_scores),
                    "std": np.std(beauty_scores),
                    "min": np.min(beauty_scores),
                    "max": np.max(beauty_scores),
                    "median": np.median(beauty_scores)
                },
                "improvement_score": {
                    "mean": np.mean(improvement_scores),
                    "std": np.std(improvement_scores),
                    "min": np.min(improvement_scores),
                    "max": np.max(improvement_scores),
                    "median": np.median(improvement_scores)
                },
                "dimension_statistics": dimension_stats
            },
            "api_performance": self._analyze_api_performance(),
            "recommendations": self._generate_recommendations()
        }
        
        # 记录到WandB（仅在非禁用模式下）
        if self.wandb_run and hasattr(self.wandb_run, 'log'):
            try:
                wandb.log({"experiment_report": report})
            except Exception as e:
                logger.warning(f"记录实验报告到WandB失败: {e}")
        
        return report
    
    def save_experiment_data(self, output_dir: str = "gis_experiment_data") -> None:
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
            
            # 保存实验结果
            if self.experiment_results:
                results_df = pd.DataFrame([asdict(record) for record in self.experiment_results])
                results_df.to_csv(output_path / "experiment_results.csv", index=False, encoding='utf-8')
            
            # 保存实验配置
            with open(output_path / "experiment_config.json", 'w', encoding='utf-8') as f:
                json.dump(asdict(self.config), f, ensure_ascii=False, indent=2)
            
            # 生成实验报告
            report = self.generate_experiment_report()
            with open(output_path / "experiment_report.json", 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            logger.info(f"GIS实验数据已保存到: {output_path}")
        except PermissionError as e:
            logger.error(f"权限错误，无法保存到 {output_dir}: {e}")
            # 尝试保存到临时目录
            import tempfile
            temp_dir = Path(tempfile.gettempdir()) / "gis_experiment_data"
            temp_dir.mkdir(exist_ok=True)
            
            try:
                # 保存API调用记录
                if self.api_calls:
                    api_calls_df = pd.DataFrame([asdict(record) for record in self.api_calls])
                    api_calls_df.to_csv(temp_dir / "api_calls.csv", index=False, encoding='utf-8')
                
                # 保存实验结果
                if self.experiment_results:
                    results_df = pd.DataFrame([asdict(record) for record in self.experiment_results])
                    results_df.to_csv(temp_dir / "experiment_results.csv", index=False, encoding='utf-8')
                
                # 保存实验配置
                with open(temp_dir / "experiment_config.json", 'w', encoding='utf-8') as f:
                    json.dump(asdict(self.config), f, ensure_ascii=False, indent=2)
                
                # 生成实验报告
                report = self.generate_experiment_report()
                with open(temp_dir / "experiment_report.json", 'w', encoding='utf-8') as f:
                    json.dump(report, f, ensure_ascii=False, indent=2)
                
                logger.info(f"GIS实验数据已保存到临时目录: {temp_dir}")
            except Exception as e2:
                logger.error(f"保存到临时目录也失败: {e2}")
        except Exception as e:
            logger.error(f"保存实验数据时出错: {e}")
    
    def finish_experiment(self) -> None:
        """
        完成实验，关闭WandB运行
        """
        if self.wandb_run and hasattr(self.wandb_run, 'log'):
            try:
                # 记录最终统计
                if self.experiment_start_time:
                    duration = time.time() - self.experiment_start_time
                    wandb.log({"experiment_duration": duration})
                
                wandb.finish()
                logger.info("GIS实验已完成，WandB运行已关闭")
            except Exception as e:
                logger.warning(f"完成WandB实验时出错: {e}")
        else:
            logger.info("GIS实验已完成（本地模式）")
    
    def _calculate_data_hash(self, data: Dict) -> str:
        """计算数据哈希值"""
        import hashlib
        try:
            # 尝试直接序列化
            data_str = json.dumps(data, sort_keys=True)
        except TypeError as e:
            # 如果包含不可序列化的对象，转换为字符串表示
            logger.warning(f"数据包含不可序列化对象，使用字符串表示: {e}")
            data_str = str(data)
        return hashlib.md5(data_str.encode()).hexdigest()
    
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
            total_tokens = sum(call.tokens_used or 0 for call in calls)
            
            performance[model_name] = {
                "total_calls": len(calls),
                "success_rate": success_rate,
                "avg_response_time": np.mean(response_times),
                "max_response_time": np.max(response_times),
                "min_response_time": np.min(response_times),
                "total_cost": total_cost,
                "avg_cost_per_call": total_cost / len(calls) if calls else 0,
                "total_tokens": total_tokens,
                "avg_tokens_per_call": total_tokens / len(calls) if calls else 0
            }
        
        return performance
    
    def _generate_recommendations(self) -> List[str]:
        """
        基于分析结果生成建议
        
        Returns:
            List[str]: 建议列表
        """
        recommendations = []
        
        if not self.experiment_results:
            return recommendations
        
        # 分析性能指标
        beauty_scores = [r.beauty_score for r in self.experiment_results]
        avg_beauty_score = np.mean(beauty_scores)
        
        if avg_beauty_score < 70:
            recommendations.append(f"平均美观性评分较低({avg_beauty_score:.1f})，建议优化算法或数据质量")
        
        # 分析API性能
        api_performance = self._analyze_api_performance()
        for model_name, perf in api_performance.items():
            if perf.get("success_rate", 1) < 0.9:
                recommendations.append(f"{model_name}的API成功率较低({perf['success_rate']:.1%})，建议检查API稳定性")
            
            if perf.get("avg_response_time", 0) > 30:
                recommendations.append(f"{model_name}的平均响应时间较长({perf['avg_response_time']:.1f}s)，建议优化网络连接")
        
        return recommendations


def create_gis_experiment_tracker(experiment_id: str,
                                 setting_name: str,
                                 data_version: str,
                                 evaluation_criteria: str,
                                 resume_run_id: Optional[str] = None,
                                 resume_mode: str = "allow",
                                 **kwargs) -> GISExperimentTracker:
    """
    创建GIS实验追踪器的便捷函数
    
    Args:
        experiment_id: 实验ID
        setting_name: Setting名称 (Setting_A, Setting_B, Setting_C等)
        data_version: 数据集版本 (标注数据v1, 标注数据v2, 扩展数据集等)
        evaluation_criteria: 评价标准 (5项评分标准, 改进评价标准, 完整评价体系等)
        resume_run_id: 要恢复的WandB运行ID (可选)
        resume_mode: 恢复模式 ("allow", "must", "never", 默认"allow")
        **kwargs: 其他配置参数
        
    Returns:
        GISExperimentTracker: GIS实验追踪器实例
    """
    config = GISExperimentConfig(
        experiment_id=experiment_id,
        setting_name=setting_name,
        data_version=data_version,
        evaluation_criteria=evaluation_criteria,
        resume_run_id=resume_run_id,
        resume_mode=resume_mode,
        **kwargs
    )
    
    tracker = GISExperimentTracker(config)
    tracker.init_experiment()
    
    return tracker