#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分支箱评分系统 - 简化包装版
基于BranchBoxScoringOptimizer的统一接口封装
"""

from core.score.branch_box_scoring_optimization import BranchBoxScoringOptimizer

class BranchBoxScoring:
    def __init__(self):
        """初始化分支箱评分系统"""
        self.optimizer = BranchBoxScoringOptimizer()
    
    def predict(self, branch_box_results, all_annotations):
        """
        预测分支箱评分
        
        Args:
            branch_box_results: 分支箱标注结果列表
            all_annotations: 所有标注数据列表
            
        Returns:
            float: 预测评分
        """
        return self.optimizer.predict(branch_box_results, all_annotations)