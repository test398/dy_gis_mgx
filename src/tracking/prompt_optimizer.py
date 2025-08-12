"""
Prompt优化系统

基于评分对比结果优化提示词，改进评分指导语和示例，提升模型理解和评分准确性
"""

import time
import json
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
import numpy as np
import wandb

# 配置日志
# logging.basicConfig(level=logging.INFO)  # 注释掉，使用main.py中的配置
logger = logging.getLogger(__name__)


@dataclass
class PromptOptimizationResult:
    """Prompt优化结果数据类"""
    optimization_id: str
    timestamp: str
    original_prompt: str
    optimized_prompt: str
    improvement_metrics: Dict[str, float]
    optimization_strategy: str
    reasoning: str
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


@dataclass
class PromptTemplate:
    """Prompt模板数据类"""
    template_id: str
    template_name: str
    template_content: str
    version: str
    performance_metrics: Dict[str, float]
    usage_count: int
    created_at: str
    last_updated: str
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.last_updated is None:
            self.last_updated = datetime.now().isoformat()


class PromptOptimizer:
    """Prompt优化系统主类"""
    
    def __init__(self, wandb_project: str = "gis-prompt-optimization"):
        """
        初始化Prompt优化系统
        
        Args:
            wandb_project: WandB项目名称
        """
        self.wandb_project = wandb_project
        self.prompt_templates = []
        self.optimization_history = []
        
        # 初始化基础模板
        self._initialize_base_templates()
        
        logger.info("Prompt优化系统初始化完成")
    
    def _initialize_base_templates(self):
        """初始化基础Prompt模板"""
        base_templates = [
            {
                "template_id": "base_v1",
                "template_name": "基础评分模板v1",
                "template_content": self._get_base_template_v1(),
                "version": "1.0",
                "performance_metrics": {},
                "usage_count": 0,
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat()
            },
            {
                "template_id": "detailed_v1",
                "template_name": "详细评分模板v1",
                "template_content": self._get_detailed_template_v1(),
                "version": "1.0",
                "performance_metrics": {},
                "usage_count": 0,
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat()
            }
        ]
        
        for template_data in base_templates:
            template = PromptTemplate(**template_data)
            self.prompt_templates.append(template)
    
    def _get_base_template_v1(self) -> str:
        """获取基础模板v1"""
        return """请对以下GIS设备布局图进行美观度评分，评分范围为0-100分。

评分维度：
1. 布局合理性 (25分)
2. 间距协调性 (25分) 
3. 整体和谐性 (25分)
4. 可访问性 (25分)

请给出每个维度的具体分数和总体评分，并简要说明评分理由。"""
    
    def _get_detailed_template_v1(self) -> str:
        """获取详细模板v1"""
        return """请对以下GIS设备布局图进行详细的美观度评分分析。

评分标准：
1. 布局合理性 (25分)
   - 设备分布是否均匀合理
   - 是否符合工程规范要求
   - 是否便于维护和操作

2. 间距协调性 (25分)
   - 设备间距离是否适当
   - 是否满足安全距离要求
   - 整体空间利用是否协调

3. 整体和谐性 (25分)
   - 视觉上是否美观协调
   - 是否符合美学设计原则
   - 与周围环境是否融合

4. 可访问性 (25分)
   - 维护通道是否畅通
   - 操作空间是否充足
   - 标识是否清晰明确

请给出：
- 每个维度的具体分数和详细分析
- 总体评分和综合评价
- 改进建议和优化方向
- 评分依据和参考标准"""
    
    def optimize_prompt_based_on_comparison(self, comparison_result: Dict, 
                                          current_prompt: str) -> PromptOptimizationResult:
        """
        基于对比结果优化Prompt
        
        Args:
            comparison_result: 评分对比结果
            current_prompt: 当前使用的Prompt
            
        Returns:
            PromptOptimizationResult: 优化结果
        """
        logger.info("开始基于对比结果优化Prompt")
        
        # 分析对比结果
        analysis = comparison_result.get("analysis", {})
        improvement_areas = comparison_result.get("improvement_areas", [])
        
        # 确定优化策略
        strategy = self._identify_optimization_strategy(analysis, improvement_areas)
        
        # 生成优化后的Prompt
        optimized_prompt = self._generate_optimized_prompt(current_prompt, strategy)
        
        # 计算改进指标
        improvement_metrics = self._calculate_improvement_metrics(analysis)
        
        # 生成优化推理
        reasoning = self._generate_optimization_reasoning(strategy, improvement_areas)
        
        # 创建优化结果
        optimization_result = PromptOptimizationResult(
            optimization_id=f"opt_{int(time.time())}",
            timestamp=datetime.now().isoformat(),
            original_prompt=current_prompt,
            optimized_prompt=optimized_prompt,
            improvement_metrics=improvement_metrics,
            optimization_strategy=strategy,
            reasoning=reasoning
        )
        
        # 保存到历史记录
        self.optimization_history.append(optimization_result)
        
        logger.info(f"Prompt优化完成，策略: {strategy}")
        return optimization_result
    
    def _identify_optimization_strategy(self, analysis: Dict, improvement_areas: List[str]) -> str:
        """识别优化策略"""
        overall_corr = analysis.get("overall", {}).get("pearson_correlation", 0)
        
        if overall_corr < 0.6:
            return "comprehensive_restructure"
        elif overall_corr < 0.75:
            return "major_enhancement"
        elif overall_corr < 0.85:
            return "targeted_improvement"
        else:
            return "fine_tuning"
    
    def _generate_optimized_prompt(self, current_prompt: str, strategy: str) -> str:
        """生成优化后的Prompt"""
        if strategy == "comprehensive_restructure":
            return self._generate_comprehensive_prompt()
        elif strategy == "major_enhancement":
            return self._generate_enhanced_prompt()
        elif strategy == "targeted_improvement":
            return self._generate_targeted_prompt()
        else:
            return self._generate_fine_tuned_prompt()
    
    def _generate_comprehensive_prompt(self) -> str:
        """生成全面重构的Prompt"""
        return """请对以下GIS设备布局图进行全面的美观度评估，采用多维度、多层次的评分体系。

## 评分框架

### 1. 布局合理性 (25分)
**评估标准：**
- 设备空间分布的科学性和合理性
- 是否符合电力工程设计规范和标准
- 设备排列的逻辑性和系统性
- 未来扩展和维护的便利性

**评分要点：**
- 空间利用率 (8分)
- 规范符合度 (8分)  
- 扩展性 (5分)
- 维护性 (4分)

### 2. 间距协调性 (25分)
**评估标准：**
- 设备间安全距离的合规性
- 操作和维护空间的充足性
- 整体空间布局的协调性
- 视觉平衡和美学效果

**评分要点：**
- 安全距离 (10分)
- 操作空间 (8分)
- 视觉协调 (7分)

### 3. 整体和谐性 (25分)
**评估标准：**
- 与周围环境的融合度
- 整体视觉效果的和谐性
- 设计风格的统一性
- 美学价值的体现

**评分要点：**
- 环境融合 (10分)
- 视觉和谐 (8分)
- 风格统一 (7分)

### 4. 可访问性 (25分)
**评估标准：**
- 维护通道的畅通性
- 操作界面的可达性
- 标识系统的清晰性
- 应急处理的便利性

**评分要点：**
- 通道畅通 (10分)
- 界面可达 (8分)
- 标识清晰 (7分)

## 评分要求

1. **定量评分**：每个维度给出具体分数，并说明扣分原因
2. **定性分析**：提供详细的评估分析和改进建议
3. **综合评估**：给出总体评分和综合评价
4. **优化建议**：提出具体的改进措施和优化方向

## 输出格式

请按以下格式输出：
```
## 评分结果

### 布局合理性：XX分
- 空间利用率：X分
- 规范符合度：X分
- 扩展性：X分
- 维护性：X分
**分析**：[详细分析]

### 间距协调性：XX分
- 安全距离：X分
- 操作空间：X分
- 视觉协调：X分
**分析**：[详细分析]

### 整体和谐性：XX分
- 环境融合：X分
- 视觉和谐：X分
- 风格统一：X分
**分析**：[详细分析]

### 可访问性：XX分
- 通道畅通：X分
- 界面可达：X分
- 标识清晰：X分
**分析**：[详细分析]

## 总体评分：XX分

## 综合评价
[综合分析和评价]

## 改进建议
[具体的改进措施和优化方向]
```

请确保评分客观、公正，分析深入、具体，建议具有可操作性。"""
    
    def _generate_enhanced_prompt(self) -> str:
        """生成增强版Prompt"""
        return """请对以下GIS设备布局图进行专业的美观度评分，重点关注评分标准的细化和分析深度的提升。

## 评分维度详解

### 1. 布局合理性 (25分)
**核心要素：**
- 设备空间分布的合理性 (8分)
- 工程规范符合度 (8分)
- 功能布局的逻辑性 (5分)
- 维护便利性 (4分)

**评估方法：**
- 检查设备间距是否符合安全标准
- 评估空间利用效率
- 分析布局的工程合理性
- 考虑未来维护和扩展需求

### 2. 间距协调性 (25分)
**核心要素：**
- 安全距离合规性 (10分)
- 操作空间充足性 (8分)
- 整体协调性 (7分)

**评估方法：**
- 测量关键设备间距离
- 评估操作和维护空间
- 分析整体视觉平衡效果

### 3. 整体和谐性 (25分)
**核心要素：**
- 环境融合度 (10分)
- 视觉和谐性 (8分)
- 设计一致性 (7分)

**评估方法：**
- 观察与周围环境的协调性
- 评估整体视觉效果
- 检查设计风格的统一性

### 4. 可访问性 (25分)
**核心要素：**
- 维护通道 (10分)
- 操作界面 (8分)
- 标识系统 (7分)

**评估方法：**
- 检查维护通道的畅通性
- 评估操作界面的可达性
- 验证标识的清晰度

## 评分流程

1. **初步观察**：整体浏览布局图，形成初步印象
2. **详细检查**：逐项检查各评分要素
3. **量化评分**：根据检查结果给出具体分数
4. **分析总结**：提供详细的分析和评价
5. **改进建议**：提出具体的优化建议

## 输出要求

请提供：
- 每个维度的详细评分和具体分析
- 总体评分和综合评价
- 针对性的改进建议
- 评分依据和参考标准

确保评分客观准确，分析深入透彻，建议切实可行。"""
    
    def _generate_targeted_prompt(self) -> str:
        """生成针对性改进的Prompt"""
        return """请对以下GIS设备布局图进行美观度评分，重点关注已识别的问题领域，提供针对性的改进建议。

## 评分重点

### 1. 布局合理性 (25分)
**重点关注：**
- 设备分布是否均匀合理
- 是否符合工程规范要求
- 是否便于维护和操作

**评分标准：**
- 优秀 (21-25分)：布局科学合理，完全符合规范
- 良好 (16-20分)：布局基本合理，基本符合规范
- 一般 (11-15分)：布局存在一些问题，部分符合规范
- 较差 (0-10分)：布局不合理，不符合规范要求

### 2. 间距协调性 (25分)
**重点关注：**
- 设备间距离是否适当
- 是否满足安全距离要求
- 整体空间利用是否协调

**评分标准：**
- 优秀 (21-25分)：间距完全协调，安全距离充足
- 良好 (16-20分)：间距基本协调，安全距离满足要求
- 一般 (11-15分)：间距存在一些问题，安全距离基本满足
- 较差 (0-10分)：间距不协调，安全距离不足

### 3. 整体和谐性 (25分)
**重点关注：**
- 视觉上是否美观协调
- 是否符合美学设计原则
- 与周围环境是否融合

**评分标准：**
- 优秀 (21-25分)：整体和谐美观，完全符合美学原则
- 良好 (16-20分)：整体基本和谐，基本符合美学原则
- 一般 (11-15分)：整体和谐性一般，部分符合美学原则
- 较差 (0-10分)：整体不和谐，不符合美学原则

### 4. 可访问性 (25分)
**重点关注：**
- 维护通道是否畅通
- 操作空间是否充足
- 标识是否清晰明确

**评分标准：**
- 优秀 (21-25分)：完全可访问，通道畅通，标识清晰
- 良好 (16-20分)：基本可访问，通道基本畅通，标识基本清晰
- 一般 (11-15分)：可访问性一般，通道存在一些问题
- 较差 (0-10分)：可访问性差，通道不畅，标识不清晰

## 评分要求

1. **客观公正**：基于客观标准进行评分
2. **详细分析**：提供具体的评分理由和分析
3. **改进建议**：针对发现的问题提出改进建议
4. **综合评价**：给出总体评价和优化方向

## 输出格式

请按以下格式输出：
```
## 评分结果

### 布局合理性：XX分
**评分理由**：[具体分析]
**改进建议**：[针对性建议]

### 间距协调性：XX分
**评分理由**：[具体分析]
**改进建议**：[针对性建议]

### 整体和谐性：XX分
**评分理由**：[具体分析]
**改进建议**：[针对性建议]

### 可访问性：XX分
**评分理由**：[具体分析]
**改进建议**：[针对性建议]

## 总体评分：XX分

## 综合评价
[综合分析和评价]

## 主要改进方向
[重点改进领域和具体措施]
```"""
    
    def _generate_fine_tuned_prompt(self) -> str:
        """生成精细调优的Prompt"""
        return """请对以下GIS设备布局图进行精细的美观度评分，重点关注细节优化和品质提升。

## 精细评分标准

### 1. 布局合理性 (25分)
**精细评估：**
- 设备空间分布的精确性 (8分)
- 工程规范符合的严格性 (8分)
- 功能布局的优化程度 (5分)
- 维护便利性的细节 (4分)

**评分细节：**
- 21-25分：布局精确合理，完全符合规范，细节完美
- 16-20分：布局基本合理，基本符合规范，细节良好
- 11-15分：布局基本合理，部分符合规范，细节一般
- 0-10分：布局存在问题，不符合规范，细节较差

### 2. 间距协调性 (25分)
**精细评估：**
- 安全距离的精确性 (10分)
- 操作空间的优化性 (8分)
- 整体协调的精细度 (7分)

**评分细节：**
- 21-25分：间距完全协调，安全距离精确，操作空间优化
- 16-20分：间距基本协调，安全距离满足，操作空间充足
- 11-15分：间距基本协调，安全距离基本满足，操作空间基本充足
- 0-10分：间距不协调，安全距离不足，操作空间不足

### 3. 整体和谐性 (25分)
**精细评估：**
- 环境融合的精细度 (10分)
- 视觉和谐的精确性 (8分)
- 设计一致性的细节 (7分)

**评分细节：**
- 21-25分：环境完全融合，视觉完全和谐，设计完全一致
- 16-20分：环境基本融合，视觉基本和谐，设计基本一致
- 11-15分：环境基本融合，视觉基本和谐，设计基本一致
- 0-10分：环境不融合，视觉不和谐，设计不一致

### 4. 可访问性 (25分)
**精细评估：**
- 维护通道的精细度 (10分)
- 操作界面的优化性 (8分)
- 标识系统的精确性 (7分)

**评分细节：**
- 21-25分：通道完全畅通，界面完全优化，标识完全清晰
- 16-20分：通道基本畅通，界面基本优化，标识基本清晰
- 11-15分：通道基本畅通，界面基本优化，标识基本清晰
- 0-10分：通道不畅，界面不优化，标识不清晰

## 精细评估要求

1. **细节关注**：重点关注布局的细节和品质
2. **精确评分**：基于精细标准进行精确评分
3. **优化建议**：提供具体的优化细节和改进措施
4. **品质提升**：关注整体品质的提升方向

## 输出格式

请按以下格式输出：
```
## 精细评分结果

### 布局合理性：XX分
**精细分析**：[详细分析]
**优化细节**：[具体优化措施]

### 间距协调性：XX分
**精细分析**：[详细分析]
**优化细节**：[具体优化措施]

### 整体和谐性：XX分
**精细分析**：[详细分析]
**优化细节**：[具体优化措施]

### 可访问性：XX分
**精细分析**：[详细分析]
**优化细节**：[具体优化措施]

## 总体评分：XX分

## 精细评价
[精细分析和评价]

## 品质提升建议
[具体的品质提升措施和优化细节]
```"""
    
    def _calculate_improvement_metrics(self, analysis: Dict) -> Dict[str, float]:
        """计算改进指标"""
        overall = analysis.get("overall", {})
        
        return {
            "overall_correlation": overall.get("pearson_correlation", 0),
            "score_consistency": overall.get("score_variance", 0),
            "dimension_consistency": len(analysis.get("dimensions", {}))
        }
    
    def _generate_optimization_reasoning(self, strategy: str, improvement_areas: List[str]) -> str:
        """生成优化推理"""
        strategy_descriptions = {
            "comprehensive_restructure": "全面重构策略：由于整体相关性较低，需要对Prompt进行全面重构，提升评分指导的准确性和全面性。",
            "major_enhancement": "主要增强策略：整体相关性有待提升，需要增强Prompt的指导性和分析深度。",
            "targeted_improvement": "针对性改进策略：整体相关性良好，但存在特定改进领域，需要针对性优化。",
            "fine_tuning": "精细调优策略：整体相关性较高，主要进行细节优化和品质提升。"
        }
        
        reasoning = strategy_descriptions.get(strategy, "未知策略")
        reasoning += f"\n\n主要改进领域：{', '.join(improvement_areas)}"
        
        return reasoning
    
    def add_template(self, template: PromptTemplate) -> None:
        """
        添加新的Prompt模板
        
        Args:
            template: Prompt模板
        """
        self.prompt_templates.append(template)
        logger.info(f"已添加新模板: {template.template_name}")
    
    def get_template(self, template_id: str) -> Optional[PromptTemplate]:
        """
        获取指定模板
        
        Args:
            template_id: 模板ID
            
        Returns:
            Optional[PromptTemplate]: 模板对象，如果不存在则返回None
        """
        for template in self.prompt_templates:
            if template.template_id == template_id:
                return template
        return None
    
    def update_template_performance(self, template_id: str, 
                                  performance_metrics: Dict[str, float]) -> bool:
        """
        更新模板性能指标
        
        Args:
            template_id: 模板ID
            performance_metrics: 性能指标
            
        Returns:
            bool: 更新是否成功
        """
        template = self.get_template(template_id)
        if template:
            template.performance_metrics.update(performance_metrics)
            template.last_updated = datetime.now().isoformat()
            template.usage_count += 1
            logger.info(f"已更新模板性能指标: {template_id}")
            return True
        return False
    
    def get_best_performing_template(self) -> Optional[PromptTemplate]:
        """
        获取性能最好的模板
        
        Returns:
            Optional[PromptTemplate]: 性能最好的模板
        """
        if not self.prompt_templates:
            return None
        
        # 按整体相关性排序
        sorted_templates = sorted(
            self.prompt_templates,
            key=lambda t: t.performance_metrics.get("overall_correlation", 0),
            reverse=True
        )
        
        return sorted_templates[0] if sorted_templates else None
    
    def generate_optimization_report(self, output_dir: str = "reports") -> str:
        """
        生成优化报告
        
        Args:
            output_dir: 输出目录
            
        Returns:
            str: 报告文件路径
        """
        logger.info("开始生成优化报告")
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = output_path / f"prompt_optimization_report_{timestamp}.md"
        
        # 生成报告内容
        report_content = self._generate_optimization_report_content()
        
        # 保存报告
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        logger.info(f"优化报告已生成: {report_file}")
        return str(report_file)
    
    def _generate_optimization_report_content(self) -> str:
        """生成优化报告内容"""
        content = f"""# Prompt优化系统报告

## 报告概览
- **生成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- **模板数量**: {len(self.prompt_templates)}
- **优化次数**: {len(self.optimization_history)}

## 模板性能分析

"""
        
        # 添加模板信息
        for template in self.prompt_templates:
            content += f"""### {template.template_name}
- **模板ID**: {template.template_id}
- **版本**: {template.version}
- **使用次数**: {template.usage_count}
- **创建时间**: {template.created_at}
- **最后更新**: {template.last_updated}
- **性能指标**: {json.dumps(template.performance_metrics, ensure_ascii=False, indent=2)}

"""
        
        # 添加优化历史
        if self.optimization_history:
            content += "## 优化历史记录\n\n"
            for result in self.optimization_history[-5:]:  # 显示最近5次优化
                content += f"""### 优化记录 {result.optimization_id}
- **时间**: {result.timestamp}
- **策略**: {result.optimization_strategy}
- **改进指标**: {json.dumps(result.improvement_metrics, ensure_ascii=False, indent=2)}
- **优化推理**: {result.reasoning}

"""
        
        content += "## 系统状态\n"
        content += f"- **总优化次数**: {len(self.optimization_history)}\n"
        content += f"- **活跃模板数量**: {len(self.prompt_templates)}\n"
        content += f"- **系统运行状态**: 正常\n"
        
        return content
    
    def save_optimization_history(self, output_dir: str = "prompt_optimization") -> str:
        """
        保存优化历史
        
        Args:
            output_dir: 输出目录
            
        Returns:
            str: 保存文件路径
        """
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        history_file = output_path / f"prompt_optimization_history_{timestamp}.json"
        
        # 转换为可序列化的格式
        history_data = []
        for result in self.optimization_history:
            history_data.append({
                "optimization_id": result.optimization_id,
                "timestamp": result.timestamp,
                "optimization_strategy": result.optimization_strategy,
                "improvement_metrics": result.improvement_metrics,
                "reasoning": result.reasoning
            })
        
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"优化历史已保存: {history_file}")
        return str(history_file)
    
    def log_to_wandb(self, optimization_result: PromptOptimizationResult, 
                     project_name: str = None) -> None:
        """
        将优化结果记录到WandB
        
        Args:
            optimization_result: 优化结果
            project_name: WandB项目名称
        """
        if project_name is None:
            project_name = self.wandb_project
        
        try:
            # 初始化WandB
            wandb.init(project=project_name, name="prompt-optimization")
            
            # 记录优化指标
            wandb.log({
                "optimization/strategy": optimization_result.optimization_strategy,
                "optimization/overall_correlation": optimization_result.improvement_metrics.get("overall_correlation", 0),
                "optimization/score_consistency": optimization_result.improvement_metrics.get("score_consistency", 0),
                "optimization/dimension_consistency": optimization_result.improvement_metrics.get("dimension_consistency", 0),
                "optimization/timestamp": optimization_result.timestamp
            })
            
            # 记录Prompt内容
            wandb.log({
                "prompt/original_length": len(optimization_result.original_prompt),
                "prompt/optimized_length": len(optimization_result.optimized_prompt),
                "prompt/improvement_ratio": len(optimization_result.optimized_prompt) / len(optimization_result.original_prompt)
            })
            
            logger.info("优化结果已成功记录到WandB")
            
        except Exception as e:
            logger.error(f"记录到WandB失败: {e}")
        finally:
            wandb.finish()
    
    def export_templates(self, output_dir: str = "templates") -> str:
        """
        导出所有模板
        
        Args:
            output_dir: 输出目录
            
        Returns:
            str: 导出文件路径
        """
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_file = output_path / f"prompt_templates_{timestamp}.json"
        
        # 转换为可序列化的格式
        templates_data = []
        for template in self.prompt_templates:
            templates_data.append({
                "template_id": template.template_id,
                "template_name": template.template_name,
                "template_content": template.template_content,
                "version": template.version,
                "performance_metrics": template.performance_metrics,
                "usage_count": template.usage_count,
                "created_at": template.created_at,
                "last_updated": template.last_updated
            })
        
        with open(export_file, 'w', encoding='utf-8') as f:
            json.dump(templates_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"模板已导出: {export_file}")
        return str(export_file)
    
    def import_templates(self, import_file: str) -> int:
        """
        导入模板
        
        Args:
            import_file: 导入文件路径
            
        Returns:
            int: 导入的模板数量
        """
        try:
            with open(import_file, 'r', encoding='utf-8') as f:
                templates_data = json.load(f)
            
            imported_count = 0
            for template_data in templates_data:
                # 检查是否已存在
                existing = self.get_template(template_data["template_id"])
                if not existing:
                    template = PromptTemplate(**template_data)
                    self.prompt_templates.append(template)
                    imported_count += 1
            
            logger.info(f"成功导入 {imported_count} 个模板")
            return imported_count
            
        except Exception as e:
            logger.error(f"导入模板失败: {e}")
            return 0
    
    def get_optimization_statistics(self) -> Dict[str, Any]:
        """
        获取优化统计信息
        
        Returns:
            Dict[str, Any]: 统计信息
        """
        if not self.optimization_history:
            return {
                "total_optimizations": 0,
                "strategy_distribution": {},
                "average_improvement": 0.0,
                "best_optimization": None
            }
        
        # 策略分布
        strategy_counts = {}
        for result in self.optimization_history:
            strategy = result.optimization_strategy
            strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1
        
        # 平均改进
        overall_correlations = [r.improvement_metrics.get("overall_correlation", 0) 
                               for r in self.optimization_history]
        avg_improvement = np.mean(overall_correlations) if overall_correlations else 0.0
        
        # 最佳优化
        best_optimization = max(self.optimization_history, 
                               key=lambda r: r.improvement_metrics.get("overall_correlation", 0))
        
        return {
            "total_optimizations": len(self.optimization_history),
            "strategy_distribution": strategy_counts,
            "average_improvement": avg_improvement,
            "best_optimization": {
                "id": best_optimization.optimization_id,
                "strategy": best_optimization.optimization_strategy,
                "improvement": best_optimization.improvement_metrics.get("overall_correlation", 0),
                "timestamp": best_optimization.timestamp
            }
        }
    
    def cleanup_old_optimizations(self, days_to_keep: int = 30) -> int:
        """
        清理旧的优化记录
        
        Args:
            days_to_keep: 保留天数
            
        Returns:
            int: 清理的记录数量
        """
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        original_count = len(self.optimization_history)
        
        self.optimization_history = [
            result for result in self.optimization_history
            if datetime.fromisoformat(result.timestamp) > cutoff_date
        ]
        
        cleaned_count = original_count - len(self.optimization_history)
        if cleaned_count > 0:
            logger.info(f"已清理 {cleaned_count} 条旧优化记录")
        
        return cleaned_count


def create_prompt_optimizer(wandb_project: str = "gis-prompt-optimization") -> PromptOptimizer:
    """
    创建Prompt优化器实例
    
    Args:
        wandb_project: WandB项目名称
        
    Returns:
        PromptOptimizer: Prompt优化器实例
    """
    return PromptOptimizer(wandb_project=wandb_project)