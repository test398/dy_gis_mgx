"""
WandB 实验追踪模块

基于WandB官方最佳实践，实现电网台区美化系统的实验追踪
参考: https://docs.wandb.ai/tutorials/experiments/
"""

import wandb
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


class GISExperimentTracker:
    """
    电网台区美化系统实验追踪器
    
    功能特性:
    1. Setting自动分类和分组
    2. 最佳性能追踪
    3. 多维度指标记录
    4. 自动可视化配置
    """
    
    def __init__(self, project_name: str = "gis-beautification-system"):
        self.project_name = project_name
        self.current_run = None
        
    def start_experiment(self, 
                        setting_config: Dict[str, Any],
                        experiment_name: Optional[str] = None,
                        tags: List[str] = None) -> wandb.run:
        """
        启动新实验
        
        Args:
            setting_config: Setting配置 (数据版本、评价标准等)
            experiment_name: 实验名称
            tags: 实验标签
        """
        # 生成Setting标识符
        setting_name = self._generate_setting_name(setting_config)
        
        # 实验配置
        config = {
            **setting_config,
            "setting_name": setting_name,
            "start_time": datetime.now().isoformat(),
            "project_version": "v1.0"
        }
        
        # 实验标签
        experiment_tags = tags or []
        experiment_tags.extend([
            setting_name,
            setting_config.get("data_version", "unknown"),
            setting_config.get("evaluation_criteria", "unknown")
        ])
        
        # 初始化WandB运行
        self.current_run = wandb.init(
            project=self.project_name,
            name=experiment_name or f"{setting_name}_{datetime.now().strftime('%m%d_%H%M')}",
            config=config,
            group=setting_name,  # 按Setting分组
            tags=experiment_tags,
            reinit=True  # 支持多次初始化
        )
        
        logger.info(f"✅ WandB实验已启动: {self.current_run.name}")
        logger.info(f"🔗 实验链接: {self.current_run.url}")
        
        return self.current_run
    
    def log_experiment_result(self, 
                            beauty_score: float,
                            improvement_score: float,
                            dimension_scores: Dict[str, float],
                            processing_time: float,
                            success_metrics: Dict[str, float] = None,
                            is_best_attempt: bool = False) -> None:
        """
        记录实验结果
        
        Args:
            beauty_score: 美观性总分 (0-100)
            improvement_score: 治理提升分数
            dimension_scores: 5维度分项评分
            processing_time: 处理时间
            success_metrics: 成功率等技术指标
            is_best_attempt: 是否为最佳尝试
        """
        if not self.current_run:
            logger.error("❌ 未找到活跃的WandB运行，请先调用start_experiment()")
            return
            
        # 主要性能指标
        metrics = {
            "beauty_score": beauty_score,
            "improvement_score": improvement_score,
            "processing_time": processing_time,
            **{f"dimension_{k}": v for k, v in dimension_scores.items()}
        }
        
        # 技术指标
        if success_metrics:
            metrics.update({f"tech_{k}": v for k, v in success_metrics.items()})
        
        # 记录指标
        self.current_run.log(metrics)
        
        # 标记最佳实验
        if is_best_attempt:
            self.current_run.tags = list(set(self.current_run.tags + ["best_attempt"]))
            
        # 记录摘要信息
        self.current_run.summary.update({
            "final_beauty_score": beauty_score,
            "final_improvement": improvement_score,
            "experiment_timestamp": datetime.now().isoformat()
        })
        
        logger.info(f"📊 实验结果已记录: 美观性{beauty_score:.1f}分, 提升{improvement_score:.1f}分")
    
    def log_model_checkpoint(self, 
                           model_path: str,
                           model_name: str,
                           aliases: List[str] = None) -> None:
        """记录模型检查点"""
        if not self.current_run:
            return
            
        try:
            self.current_run.log_model(
                model_path,
                name=model_name,
                aliases=aliases or ["latest"]
            )
            logger.info(f"💾 模型检查点已保存: {model_name}")
        except Exception as e:
            logger.error(f"❌ 模型保存失败: {e}")
    
    def finish_experiment(self) -> None:
        """结束当前实验"""
        if self.current_run:
            self.current_run.finish()
            logger.info("✅ WandB实验已结束")
            self.current_run = None
    
    def create_custom_visualization(self) -> None:
        """创建自定义可视化面板"""
        if not self.current_run:
            return
            
        # 这里可以创建自定义图表和面板
        # WandB支持通过API创建自定义仪表板
        pass
    
    def _generate_setting_name(self, setting_config: Dict[str, Any]) -> str:
        """生成Setting名称"""
        data_version = setting_config.get("data_version", "unknown")
        eval_criteria = setting_config.get("evaluation_criteria", "unknown")
        
        # 简化Setting名称
        setting_map = {
            ("标注数据v1", "5项评分标准"): "Setting_A",
            ("标注数据v2", "改进评价标准"): "Setting_B", 
            ("扩展数据集", "完整评价体系"): "Setting_C"
        }
        
        key = (data_version, eval_criteria)
        return setting_map.get(key, f"Setting_{hash(str(key)) % 1000}")


class ProgressTracker:
    """进度追踪辅助类"""
    
    @staticmethod
    def get_best_runs_by_setting(project_name: str) -> Dict[str, Dict]:
        """获取每个Setting的最佳运行"""
        try:
            api = wandb.Api()
            runs = api.runs(project_name)
            
            best_runs = {}
            for run in runs:
                if run.state != "finished":
                    continue
                    
                setting = run.config.get("setting_name", "unknown")
                beauty_score = run.summary.get("final_beauty_score", 0)
                
                if setting not in best_runs or beauty_score > best_runs[setting]["score"]:
                    best_runs[setting] = {
                        "run_id": run.id,
                        "score": beauty_score,
                        "url": run.url,
                        "created_at": run.created_at
                    }
            
            return best_runs
        except Exception as e:
            logger.error(f"❌ 获取最佳运行失败: {e}")
            return {}
    
    @staticmethod
    def generate_progress_report() -> str:
        """生成进度报告"""
        # 实现进度报告生成逻辑
        return "Progress report generated"


# 使用示例
def example_usage():
    """使用示例"""
    
    # 初始化追踪器
    tracker = GISExperimentTracker()
    
    # 定义Setting配置
    setting_config = {
        "data_version": "标注数据v1",
        "evaluation_criteria": "5项评分标准",
        "model_name": "qwen-vl-max",
        "algorithm_version": "v2.1"
    }
    
    # 启动实验
    run = tracker.start_experiment(
        setting_config=setting_config,
        experiment_name="baseline_test",
        tags=["baseline", "initial"]
    )
    
    # 模拟实验过程
    time.sleep(1)
    
    # 记录结果
    tracker.log_experiment_result(
        beauty_score=78.5,
        improvement_score=12.3,
        dimension_scores={
            "overhead_lines": 82,
            "cable_lines": 75,
            "branch_boxes": 80,
            "access_points": 77,
            "meter_boxes": 79
        },
        processing_time=2.5,
        success_metrics={
            "api_success_rate": 0.95,
            "json_parse_rate": 0.92
        },
        is_best_attempt=True
    )
    
    # 结束实验
    tracker.finish_experiment()


if __name__ == "__main__":
    # 需要设置WANDB_API_KEY环境变量
    example_usage()
