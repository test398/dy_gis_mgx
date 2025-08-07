"""
WandB集成示例 - 演示如何在现有pipeline中集成实验追踪

这个示例展示了如何使用WandB的group和tags功能实现:
1. 线条图显示每个Setting的最佳性能演进
2. 散点图显示所有实验结果
3. 自动颜色分组和过滤
"""

import wandb
import random
import time
from typing import Dict, Any
from datetime import datetime, timedelta

# 模拟不同的Setting配置
SETTINGS = {
    "Setting_A": {
        "data_version": "标注数据v1",
        "evaluation_criteria": "5项评分标准",
        "base_score": 65
    },
    "Setting_B": {
        "data_version": "标注数据v2", 
        "evaluation_criteria": "改进评价标准",
        "base_score": 70
    },
    "Setting_C": {
        "data_version": "扩展数据集",
        "evaluation_criteria": "完整评价体系",
        "base_score": 75
    }
}


def simulate_experiment(setting_name: str, experiment_idx: int) -> Dict[str, Any]:
    """模拟实验过程"""
    setting = SETTINGS[setting_name]
    
    # 模拟性能提升 (随时间逐步提升 + 随机波动)
    base = setting["base_score"]
    trend = experiment_idx * 0.8  # 渐进提升
    noise = random.uniform(-3, 5)  # 随机波动
    beauty_score = min(100, max(0, base + trend + noise))
    
    # 模拟其他指标
    improvement_score = beauty_score - base + random.uniform(-2, 8)
    processing_time = random.uniform(1.5, 4.0)
    
    return {
        "beauty_score": beauty_score,
        "improvement_score": improvement_score,
        "processing_time": processing_time,
        "dimension_scores": {
            "overhead_lines": beauty_score + random.uniform(-5, 5),
            "cable_lines": beauty_score + random.uniform(-5, 5),
            "branch_boxes": beauty_score + random.uniform(-5, 5),
            "access_points": beauty_score + random.uniform(-5, 5),
            "meter_boxes": beauty_score + random.uniform(-5, 5)
        }
    }


def run_wandb_experiment_example():
    """运行WandB实验追踪示例"""
    
    print("🚀 开始WandB实验追踪演示...")
    print("📊 将模拟多个Setting的实验历程")
    
    # 项目配置
    project_name = "gis-beautification-demo"
    
    # 模拟每个Setting的实验历程
    for setting_name, setting_config in SETTINGS.items():
        print(f"\n🔄 开始Setting: {setting_name}")
        
        # 每个Setting运行10个实验
        for exp_idx in range(10):
            
            # 初始化WandB运行
            with wandb.init(
                project=project_name,
                group=setting_name,  # 关键: 按Setting分组
                name=f"{setting_name}_exp_{exp_idx+1}",
                config={
                    **setting_config,
                    "experiment_idx": exp_idx + 1,
                    "setting_name": setting_name
                },
                tags=[
                    setting_name,
                    setting_config["data_version"], 
                    setting_config["evaluation_criteria"]
                ],
                reinit=True
            ) as run:
                
                # 模拟实验
                result = simulate_experiment(setting_name, exp_idx)
                
                # 关键: 记录主要指标
                run.log({
                    "beauty_score": result["beauty_score"],  # 主要追踪指标
                    "improvement_score": result["improvement_score"],
                    "processing_time": result["processing_time"],
                    # 分维度指标
                    "dim_overhead_lines": result["dimension_scores"]["overhead_lines"],
                    "dim_cable_lines": result["dimension_scores"]["cable_lines"],
                    "dim_branch_boxes": result["dimension_scores"]["branch_boxes"],
                    "dim_access_points": result["dimension_scores"]["access_points"],
                    "dim_meter_boxes": result["dimension_scores"]["meter_boxes"]
                })
                
                # 判断是否为当前Setting的最佳实验
                # (在实际应用中，这会通过API查询历史最佳值)
                is_best = result["beauty_score"] > setting_config["base_score"] + exp_idx * 0.7
                
                if is_best:
                    # 标记最佳实验
                    run.tags = run.tags + ["best_attempt"]
                    print(f"  ⭐ 最佳实验: 美观性{result['beauty_score']:.1f}分")
                else:
                    print(f"  📊 实验{exp_idx+1}: 美观性{result['beauty_score']:.1f}分")
                
                # 记录摘要
                run.summary.update({
                    "final_beauty_score": result["beauty_score"],
                    "final_improvement": result["improvement_score"],
                    "is_best": is_best
                })
                
                # 模拟实验间隔
                time.sleep(0.1)
    
    print("\n✅ WandB实验追踪演示完成!")
    print(f"🔗 查看结果: https://wandb.ai/your-username/{project_name}")
    print("\n📈 预期效果:")
    print("1. 线图: 每个Setting显示为不同颜色的线，展示最佳性能演进")
    print("2. 散点图: 所有实验点按Setting颜色分组显示")
    print("3. 过滤器: 可按Setting、标签筛选实验")
    print("4. 表格: 详细的实验对比数据")


def demonstrate_wandb_features():
    """演示WandB关键功能"""
    
    print("\n🔧 WandB关键功能演示:")
    
    # 1. Group功能 - 自动分组和颜色
    print("\n1️⃣ Group功能 - 自动生成Setting对比线图")
    print("   wandb.init(group='Setting_A')  # 自动分组")
    print("   → WandB自动为每个group分配颜色")
    print("   → 仪表板中自动创建分组对比视图")
    
    # 2. Tags功能 - 过滤和标记
    print("\n2️⃣ Tags功能 - 标记和过滤实验")
    print("   tags=['best_attempt', '标注数据v1']")
    print("   → 可在仪表板中快速过滤最佳实验")
    print("   → 支持多维度标签组合查询")
    
    # 3. 自动可视化
    print("\n3️⃣ 自动可视化生成")
    print("   run.log({'beauty_score': 78.5})")
    print("   → 自动生成时间序列线图")
    print("   → 支持scatter plot、histogram等多种图表")
    
    # 4. 仪表板配置
    print("\n4️⃣ 自定义仪表板")
    print("   → 线图面板: 按Group显示Setting性能演进")
    print("   → 散点图面板: 显示所有实验分布") 
    print("   → 表格面板: 详细实验对比")
    print("   → 过滤器: 按Setting、时间、标签筛选")


if __name__ == "__main__":
    print("WandB实验追踪集成示例")
    print("="*50)
    
    # 演示功能特性
    demonstrate_wandb_features()
    
    # 询问是否运行实际演示
    response = input("\n是否运行WandB实验演示? (需要WandB API key) [y/N]: ")
    
    if response.lower() in ['y', 'yes']:
        try:
            run_wandb_experiment_example()
        except Exception as e:
            print(f"❌ 演示失败: {e}")
            print("💡 请确保已安装wandb并配置API key:")
            print("   pip install wandb")
            print("   wandb login")
    else:
        print("📝 演示跳过。代码示例可用于实际集成。")
