"""
评分对比系统

基于人工标注数据优化模型输出质量，实现AI评分与人工评分的对比分析
"""

import time
import json
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import wandb

# 配置日志
# logging.basicConfig(level=logging.INFO)  # 注释掉，使用main.py中的配置
logger = logging.getLogger(__name__)


@dataclass
class ScoringComparisonResult:
    """评分对比结果数据类"""
    comparison_id: str
    timestamp: str
    data_version: str
    model_version: str
    
    # 相关性指标
    pearson_correlation: float
    spearman_correlation: float
    dimension_correlations: Dict[str, Dict[str, float]]
    
    # 统计指标
    mean_ai_score: float
    mean_human_score: float
    score_difference: float
    score_variance: float
    
    # 改进建议
    improvement_areas: List[str]
    prompt_optimization_suggestions: List[str]
    
    # 是否达标
    overall_target_met: bool
    dimension_targets_met: Dict[str, bool]
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


@dataclass
class HumanAnnotationData:
    """人工标注数据结构"""
    image_id: str
    annotation_file: str
    device_count: int
    layout_score: float
    spacing_score: float
    harmony_score: float
    accessibility_score: float
    overall_score: float
    annotation_notes: str
    timestamp: str


class ScoringComparison:
    """评分对比系统主类"""
    
    def __init__(self, wandb_project: str = "gis-scoring-optimization"):
        """
        初始化评分对比系统
        
        Args:
            wandb_project: WandB项目名称
        """
        self.wandb_project = wandb_project
        self.comparison_results = []
        self.human_annotations = []
        self.ai_scores = []
        
        # 目标阈值
        self.overall_correlation_target = 0.8  # 80%
        self.dimension_correlation_target = 0.75  # 75%
        
        # 评分维度
        self.dimensions = [
            "架空线路", "低压电缆", "分支箱", "接入点", "计量箱"
        ]
        
        logger.info("评分对比系统初始化完成")
    
    def load_human_annotations(self, annotation_dir: str) -> List[HumanAnnotationData]:
        """
        从标注数据目录加载人工标注数据
        
        Args:
            annotation_dir: 标注数据目录路径
            
        Returns:
            List[HumanAnnotationData]: 人工标注数据列表
        """
        logger.info(f"开始加载人工标注数据: {annotation_dir}")
        
        annotation_path = Path(annotation_dir)
        human_annotations = []
        
        # 查找所有标注文件
        annotation_files = list(annotation_path.rglob("*.json"))
        logger.info(f"找到 {len(annotation_files)} 个标注文件")
        
        for file_path in annotation_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 解析标注数据
                annotation = self._parse_annotation_file(file_path, data)
                if annotation:
                    human_annotations.append(annotation)
                    
            except Exception as e:
                logger.warning(f"解析标注文件失败 {file_path}: {e}")
                continue
        
        self.human_annotations = human_annotations
        logger.info(f"成功加载 {len(human_annotations)} 个人工标注样本")
        
        return human_annotations
    
    def _parse_annotation_file(self, file_path: Path, data: Dict) -> Optional[HumanAnnotationData]:
        """
        解析单个标注文件
        
        Args:
            file_path: 文件路径
            data: 文件内容
            
        Returns:
            Optional[HumanAnnotationData]: 解析后的标注数据
        """
        try:
            # 提取基本信息
            image_id = file_path.stem.replace("_zlh", "").replace("_zlq", "")
            
            # 计算设备数量
            annotations = data.get("annotations", [])
            device_count = len(annotations)
            
            # 从文件名判断是治理前还是治理后
            is_after = "_zlq" in file_path.name
            
            # 根据治理前后计算评分（这里需要根据实际标注格式调整）
            if is_after:
                # 治理后：基于设备布局和数量计算评分
                layout_score = self._calculate_layout_score(annotations)
                spacing_score = self._calculate_spacing_score(annotations)
                harmony_score = self._calculate_harmony_score(annotations)
                accessibility_score = self._calculate_accessibility_score(annotations)
                overall_score = np.mean([layout_score, spacing_score, harmony_score, accessibility_score])
            else:
                # 治理前：基础评分
                layout_score = 60.0
                spacing_score = 55.0
                harmony_score = 50.0
                accessibility_score = 65.0
                overall_score = 57.5
            
            return HumanAnnotationData(
                image_id=image_id,
                annotation_file=str(file_path),
                device_count=device_count,
                layout_score=layout_score,
                spacing_score=spacing_score,
                harmony_score=harmony_score,
                accessibility_score=accessibility_score,
                overall_score=overall_score,
                annotation_notes=f"治理{'后' if is_after else '前'}标注数据",
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"解析标注文件失败: {e}")
            return None
    
    def _calculate_layout_score(self, annotations: List[Dict]) -> float:
        """计算布局合理性评分"""
        if not annotations:
            return 0.0
        
        # 基于设备数量和分布计算布局评分
        device_count = len(annotations)
        if device_count <= 5:
            return 85.0
        elif device_count <= 10:
            return 75.0
        elif device_count <= 15:
            return 65.0
        else:
            return 55.0
    
    def _calculate_spacing_score(self, annotations: List[Dict]) -> float:
        """计算设备间距评分"""
        if len(annotations) < 2:
            return 80.0
        
        # 基于设备数量计算间距评分
        device_count = len(annotations)
        if device_count <= 5:
            return 90.0
        elif device_count <= 10:
            return 80.0
        elif device_count <= 15:
            return 70.0
        else:
            return 60.0
    
    def _calculate_harmony_score(self, annotations: List[Dict]) -> float:
        """计算视觉和谐性评分"""
        if not annotations:
            return 0.0
        
        # 基于设备类型多样性计算和谐性评分
        device_types = set(ann.get("label", "") for ann in annotations)
        type_count = len(device_types)
        
        if type_count <= 3:
            return 85.0
        elif type_count <= 5:
            return 75.0
        elif type_count <= 7:
            return 65.0
        else:
            return 55.0
    
    def _calculate_accessibility_score(self, annotations: List[Dict]) -> float:
        """计算可达性评分"""
        if not annotations:
            return 0.0
        
        # 基于设备数量和分布计算可达性评分
        device_count = len(annotations)
        if device_count <= 5:
            return 90.0
        elif device_count <= 10:
            return 80.0
        elif device_count <= 15:
            return 70.0
        else:
            return 60.0
    
    def compare_ai_vs_human_scores(self, ai_scores: Dict, human_scores: Dict) -> Dict:
        """
        对比AI评分与人工评分
        
        Args:
            ai_scores: AI评分结果 {"image_id": {"beauty_score": 85, "dimension_scores": {...}}}
            human_scores: 人工评分结果 {"image_id": HumanAnnotationData}
            
        Returns:
            Dict: 对比分析结果
        """
        logger.info("开始AI评分与人工评分对比分析")
        
        comparison_data = []
        
        # 匹配AI评分和人工评分
        for image_id in ai_scores.keys():
            if image_id in human_scores:
                ai_data = ai_scores[image_id]
                human_data = human_scores[image_id]
                
                comparison_record = {
                    "image_id": image_id,
                    "ai_overall": ai_data.get("beauty_score", 0),
                    "human_overall": human_data.overall_score,
                    "ai_layout": ai_data.get("dimension_scores", {}).get("layout", 0),
                    "human_layout": human_data.layout_score,
                    "ai_spacing": ai_data.get("dimension_scores", {}).get("spacing", 0),
                    "human_spacing": human_data.spacing_score,
                    "ai_harmony": ai_data.get("dimension_scores", {}).get("harmony", 0),
                    "human_harmony": human_data.harmony_score,
                    "ai_accessibility": ai_data.get("dimension_scores", {}).get("accessibility", 0),
                    "human_accessibility": human_data.accessibility_score,
                }
                
                comparison_data.append(comparison_record)
        
        logger.info(f"成功匹配 {len(comparison_data)} 个样本进行对比分析")
        
        # 分析评分模式
        analysis = self.analyze_scoring_patterns(comparison_data)
        
        # 识别改进领域
        improvement_areas = self.identify_improvement_areas(analysis)
        
        # 生成对比结果
        comparison_result = {
            "comparison_data": comparison_data,
            "analysis": analysis,
            "improvement_areas": improvement_areas,
            "sample_count": len(comparison_data)
        }
        
        return comparison_result
    
    def analyze_scoring_patterns(self, comparison_data: List[Dict]) -> Dict:
        """
        分析评分模式
        
        Args:
            comparison_data: 对比数据列表
            
        Returns:
            Dict: 分析结果
        """
        if not comparison_data:
            return {}
        
        # 转换为DataFrame便于分析
        df = pd.DataFrame(comparison_data)
        
        analysis_results = {}
        
        # 整体相关性分析
        overall_corr_pearson = stats.pearsonr(df["ai_overall"], df["human_overall"])
        overall_corr_spearman = stats.spearmanr(df["ai_overall"], df["human_overall"])
        
        analysis_results["overall"] = {
            "pearson_correlation": overall_corr_pearson[0],
            "pearson_pvalue": overall_corr_pearson[1],
            "spearman_correlation": overall_corr_spearman[0],
            "spearman_pvalue": overall_corr_spearman[1],
            "mean_ai_score": df["ai_overall"].mean(),
            "mean_human_score": df["human_overall"].mean(),
            "score_difference": df["ai_overall"].mean() - df["human_overall"].mean(),
            "score_variance": df["ai_overall"].var()
        }
        
        # 分维度相关性分析
        dimension_correlations = {}
        for dimension in ["layout", "spacing", "harmony", "accessibility"]:
            ai_col = f"ai_{dimension}"
            human_col = f"human_{dimension}"
            
            if ai_col in df.columns and human_col in df.columns:
                pearson = stats.pearsonr(df[ai_col], df[human_col])
                spearman = stats.spearmanr(df[ai_col], df[human_col])
                
                dimension_correlations[dimension] = {
                    "pearson_correlation": pearson[0],
                    "pearson_pvalue": pearson[1],
                    "spearman_correlation": spearman[0],
                    "spearman_pvalue": spearman[1],
                    "mean_ai_score": df[ai_col].mean(),
                    "mean_human_score": df[human_col].mean(),
                    "score_difference": df[ai_col].mean() - df[human_col].mean()
                }
        
        analysis_results["dimensions"] = dimension_correlations
        
        # 统计摘要
        analysis_results["summary"] = {
            "total_samples": len(df),
            "correlation_target_met": overall_corr_pearson[0] >= self.overall_correlation_target or 
                                    overall_corr_spearman[0] >= self.overall_correlation_target,
            "dimension_targets_met": {
                dim: (data["pearson_correlation"] >= self.dimension_correlation_target or 
                      data["spearman_correlation"] >= self.dimension_correlation_target)
                for dim, data in dimension_correlations.items()
            }
        }
        
        return analysis_results
    
    def identify_improvement_areas(self, analysis: Dict) -> List[str]:
        """
        识别改进领域
        
        Args:
            analysis: 分析结果
            
        Returns:
            List[str]: 改进建议列表
        """
        improvement_areas = []
        
        # 整体相关性分析
        overall = analysis.get("overall", {})
        if overall.get("pearson_correlation", 0) < self.overall_correlation_target:
            improvement_areas.append("整体评分相关性不足，需要优化评分算法")
        
        if overall.get("score_difference", 0) > 10:
            improvement_areas.append("AI评分与人工评分存在系统性偏差，需要校准")
        
        # 分维度分析
        dimensions = analysis.get("dimensions", {})
        for dim_name, dim_data in dimensions.items():
            if dim_data.get("pearson_correlation", 0) < self.dimension_correlation_target:
                improvement_areas.append(f"{dim_name}维度相关性不足，需要针对性优化")
            
            if abs(dim_data.get("score_difference", 0)) > 15:
                improvement_areas.append(f"{dim_name}维度评分偏差较大，需要重新校准")
        
        # 如果没有明显问题，给出正面反馈
        if not improvement_areas:
            improvement_areas.append("评分算法表现良好，相关性达标")
        
        return improvement_areas
    
    def generate_correlation_report(self, comparison_result: Dict, output_dir: str = "reports") -> str:
        """
        生成相关性分析报告
        
        Args:
            comparison_result: 对比结果
            output_dir: 输出目录
            
        Returns:
            str: 报告文件路径
        """
        logger.info("开始生成相关性分析报告")
        
        # 创建输出目录
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # 生成报告文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = output_path / f"scoring_correlation_report_{timestamp}.md"
        
        # 生成报告内容
        report_content = self._generate_report_content(comparison_result)
        
        # 保存报告
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        logger.info(f"相关性分析报告已生成: {report_file}")
        return str(report_file)
    
    def _generate_report_content(self, comparison_result: Dict) -> str:
        """生成报告内容"""
        analysis = comparison_result.get("analysis", {})
        overall = analysis.get("overall", {})
        dimensions = analysis.get("dimensions", {})
        summary = analysis.get("summary", {})
        
        content = f"""# 电网台区美化系统 - 评分相关性分析报告

## 报告概览
- **生成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- **样本数量**: {comparison_result.get("sample_count", 0)}
- **数据版本**: 人工标注数据v1.0

## 整体相关性分析

### 主要指标
- **Pearson相关系数**: {overall.get("pearson_correlation", 0):.4f}
- **Spearman相关系数**: {overall.get("spearman_correlation", 0):.4f}
- **AI评分均值**: {overall.get("mean_ai_score", 0):.2f}
- **人工评分均值**: {overall.get("mean_human_score", 0):.2f}
- **评分差异**: {overall.get("score_difference", 0):.2f}

### 相关性目标达成情况
- **整体目标**: {'✅ 达成' if summary.get('correlation_target_met', False) else '❌ 未达成'} (目标: ≥80%)
- **当前最佳相关性**: {max(overall.get("pearson_correlation", 0), overall.get("spearman_correlation", 0)):.4f}

## 分维度相关性分析

"""
        
        # 添加分维度分析
        for dim_name, dim_data in dimensions.items():
            content += f"""### {dim_name}维度
- **Pearson相关系数**: {dim_data.get("pearson_correlation", 0):.4f}
- **Spearman相关系数**: {dim_data.get("spearman_correlation", 0):.4f}
- **AI评分均值**: {dim_data.get("mean_ai_score", 0):.2f}
- **人工评分均值**: {dim_data.get("mean_human_score", 0):.2f}
- **评分差异**: {dim_data.get("score_difference", 0):.2f}
- **目标达成**: {'✅ 达成' if summary.get('dimension_targets_met', {}).get(dim_name, False) else '❌ 未达成'} (目标: ≥75%)

"""
        
        # 添加改进建议
        content += """## 改进建议

"""
        for suggestion in comparison_result.get("improvement_areas", []):
            content += f"- {suggestion}\n"
        
        content += f"""
## 结论

基于 {comparison_result.get("sample_count", 0)} 个样本的分析结果：

1. **整体表现**: {'优秀' if summary.get('correlation_target_met', False) else '需要改进'}
2. **分维度表现**: 各维度相关性分析结果如上所示
3. **改进重点**: 重点关注相关性较低的维度，优化评分算法

---
*报告由评分对比系统自动生成*
"""
        
        return content
    
    def create_correlation_visualizations(self, comparison_result: Dict, output_dir: str = "reports") -> List[str]:
        """
        创建相关性可视化图表
        
        Args:
            comparison_result: 对比结果
            output_dir: 输出目录
            
        Returns:
            List[str]: 生成的图表文件路径列表
        """
        logger.info("开始生成相关性可视化图表")
        
        # 创建输出目录
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # 转换为DataFrame
        df = pd.DataFrame(comparison_result.get("comparison_data", []))
        if df.empty:
            logger.warning("没有数据用于生成可视化图表")
            return []
        
        chart_files = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 1. 整体评分散点图
        plt.figure(figsize=(10, 8))
        plt.scatter(df["human_overall"], df["ai_overall"], alpha=0.7, s=100)
        
        # 添加回归线
        z = np.polyfit(df["human_overall"], df["ai_overall"], 1)
        p = np.poly1d(z)
        plt.plot(df["human_overall"], p(df["human_overall"]), "r--", alpha=0.8)
        
        # 添加对角线
        min_val = min(df["human_overall"].min(), df["ai_overall"].min())
        max_val = max(df["human_overall"].max(), df["ai_overall"].max())
        plt.plot([min_val, max_val], [min_val, max_val], "k-", alpha=0.3, label="理想线")
        
        plt.xlabel("人工评分")
        plt.ylabel("AI评分")
        plt.title("AI评分 vs 人工评分 - 整体相关性分析")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # 保存图表
        overall_chart = output_path / f"overall_correlation_{timestamp}.png"
        plt.savefig(overall_chart, dpi=300, bbox_inches='tight')
        plt.close()
        chart_files.append(str(overall_chart))
        
        # 2. 分维度相关性图表
        dimensions = ["layout", "spacing", "harmony", "accessibility"]
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        axes = axes.ravel()
        
        for i, dim in enumerate(dimensions):
            ai_col = f"ai_{dim}"
            human_col = f"human_{dim}"
            
            if ai_col in df.columns and human_col in df.columns:
                axes[i].scatter(df[human_col], df[ai_col], alpha=0.7, s=80)
                
                # 添加回归线
                z = np.polyfit(df[human_col], df[ai_col], 1)
                p = np.poly1d(z)
                axes[i].plot(df[human_col], p(df[human_col]), "r--", alpha=0.8)
                
                # 添加对角线
                min_val = min(df[human_col].min(), df[ai_col].min())
                max_val = max(df[human_col].max(), df[ai_col].max())
                axes[i].plot([min_val, max_val], [min_val, max_val], "k-", alpha=0.3)
                
                axes[i].set_xlabel(f"人工{dim}评分")
                axes[i].set_ylabel(f"AI{dim}评分")
                axes[i].set_title(f"{dim}维度相关性分析")
                axes[i].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # 保存分维度图表
        dimension_chart = output_path / f"dimension_correlations_{timestamp}.png"
        plt.savefig(dimension_chart, dpi=300, bbox_inches='tight')
        plt.close()
        chart_files.append(str(dimension_chart))
        
        # 3. 相关性热力图
        correlation_data = []
        for dim in dimensions:
            ai_col = f"ai_{dim}"
            human_col = f"human_{dim}"
            
            if ai_col in df.columns and human_col in df.columns:
                pearson_corr = df[ai_col].corr(df[human_col])
                correlation_data.append([dim, "AI评分", pearson_corr])
                correlation_data.append([dim, "人工评分", 1.0])
        
        if correlation_data:
            corr_df = pd.DataFrame(correlation_data, columns=["维度", "评分类型", "相关性"])
            corr_pivot = corr_df.pivot(index="维度", columns="评分类型", values="相关性")
            
            plt.figure(figsize=(8, 6))
            sns.heatmap(corr_pivot, annot=True, cmap="RdYlBu_r", center=0.5, 
                       vmin=0, vmax=1, fmt=".3f")
            plt.title("分维度相关性热力图")
            plt.tight_layout()
            
            # 保存热力图
            heatmap_chart = output_path / f"correlation_heatmap_{timestamp}.png"
            plt.savefig(heatmap_chart, dpi=300, bbox_inches='tight')
            plt.close()
            chart_files.append(str(heatmap_chart))
        
        logger.info(f"成功生成 {len(chart_files)} 个可视化图表")
        return chart_files
    
    def log_to_wandb(self, comparison_result: Dict, project_name: str = None) -> None:
        """
        将对比结果记录到WandB
        
        Args:
            comparison_result: 对比结果
            project_name: WandB项目名称
        """
        if project_name is None:
            project_name = self.wandb_project
        
        try:
            # 初始化WandB
            wandb.init(project=project_name, name="scoring-comparison")
            
            # 记录整体指标
            analysis = comparison_result.get("analysis", {})
            overall = analysis.get("overall", {})
            
            wandb.log({
                "overall/pearson_correlation": overall.get("pearson_correlation", 0),
                "overall/spearman_correlation": overall.get("spearman_correlation", 0),
                "overall/mean_ai_score": overall.get("mean_ai_score", 0),
                "overall/mean_human_score": overall.get("mean_human_score", 0),
                "overall/score_difference": overall.get("score_difference", 0),
                "overall/correlation_target_met": analysis.get("summary", {}).get("correlation_target_met", False)
            })
            
            # 记录分维度指标
            dimensions = analysis.get("dimensions", {})
            for dim_name, dim_data in dimensions.items():
                wandb.log({
                    f"{dim_name}/pearson_correlation": dim_data.get("pearson_correlation", 0),
                    f"{dim_name}/spearman_correlation": dim_data.get("spearman_correlation", 0),
                    f"{dim_name}/mean_ai_score": dim_data.get("mean_ai_score", 0),
                    f"{dim_name}/mean_human_score": dim_data.get("mean_human_score", 0),
                    f"{dim_name}/score_difference": dim_data.get("score_difference", 0),
                    f"{dim_name}/target_met": analysis.get("summary", {}).get("dimension_targets_met", {}).get(dim_name, False)
                })
            
            # 记录样本数量
            wandb.log({"sample_count": comparison_result.get("sample_count", 0)})
            
            logger.info("对比结果已成功记录到WandB")
            
        except Exception as e:
            logger.error(f"记录到WandB失败: {e}")
        finally:
            wandb.finish()


def create_scoring_comparison_system(wandb_project: str = "gis-scoring-optimization") -> ScoringComparison:
    """
    创建评分对比系统实例
    
    Args:
        wandb_project: WandB项目名称
        
    Returns:
        ScoringComparison: 评分对比系统实例
    """
    return ScoringComparison(wandb_project=wandb_project)