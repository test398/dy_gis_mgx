#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
对单个或多个台区进行打分并与人工打分结果对比的脚本
支持批量处理多个台区并生成Markdown报告
"""
import os
import json
import logging
import sys
from typing import Dict, Any, List

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 添加项目根目录和src目录到Python路径
project_root = os.path.abspath(os.path.dirname(__file__))
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, project_root)
sys.path.insert(0, src_path)

# 导入评分器
from core.overhead_line_scorer import OverheadLineScorer
from core.cable_line_scorer import CableLineScorer
from core.branch_box_scorer import BranchBoxScorer
from core.access_point_scorer import AccessPointScorer
from core.meter_box_scorer import MeterBoxScorer


class ScoreComparator:
    """评分对比类"""
    def __init__(self, test_data_path: str, manual_score_path: str):
        """
        初始化对比器
        Args:
            test_data_path: 测试数据文件路径
            manual_score_path: 人工打分结果文件路径
        """
        self.test_data_path = test_data_path
        self.manual_score_path = manual_score_path
        self.test_data = self._load_test_data()
        self.manual_scores = self._load_manual_scores()
        self.scorers = {
            '架空线评分器': OverheadLineScorer(),
            '电缆线路评分器': CableLineScorer(),
            '分支箱评分器': BranchBoxScorer(),
            '接入点评分器': AccessPointScorer(),
            '计量箱评分器': MeterBoxScorer()
        }
        # 单项评分映射表（程序评分项 -> 人工评分项）
        self.score_mapping = {
            '架空线评分器': '架空线路',
            '电缆线路评分器': '电缆线路',
            '分支箱评分器': '分支箱',
            '接入点评分器': '接入点',
            '计量箱评分器': '计量箱'
        }

    def _load_test_data(self) -> Dict[str, Any]:
        """加载测试数据并转换为评分器期望的格式"""
        try:
            with open(self.test_data_path, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)

            # 将标注数据转换为评分器期望的格式
            converted_data = {
                'devices': [],
                'buildings': [],
                'roads': [],
                'rivers': [],
                'boundaries': {}
            }

            # 处理标注数据
            if 'annotations' in raw_data:
                for annotation in raw_data['annotations']:
                    label = annotation.get('label', '')
                    # 映射标注标签到评分器期望的设备类型
                    device_type = label
                    if '电缆终端头' in label or '电缆头' in label:
                        device_type = 'head'
                    elif '电缆段' in label:
                        device_type = 'cable_segment'
                    elif '电杆' in label or '杆塔' in label:
                        device_type = '杆塔'
                    elif '墙支架' in label or '墙担' in label:
                        device_type = '墙支架'
                    elif '分支箱' in label:
                        device_type = '分支箱'
                    elif '接入点' in label:
                        device_type = '接入点'
                    elif '配电箱' in label or '计量箱' in label:
                        device_type = '计量箱'

                    # 计算中心点坐标（如果有多个点）
                    points = annotation.get('points', [])
                    x = y = 0.0
                    if len(points) > 0:
                        x = sum(p[0] for p in points) / len(points)
                        y = sum(p[1] for p in points) / len(points)

                    # 特殊处理分支箱：如果是分支箱，只保留中心点作为唯一的点
                    if '分支箱' in label:
                        points = [[x, y]]

                    device = {
                        'id': annotation.get('id', ''),
                        'type': device_type,
                        'label': label,
                        'points': points,
                        'x': x,
                        'y': y,
                        'properties': {},
                        'flag': annotation.get('flag', '')
                    }
                    converted_data['devices'].append(device)

            logger.info(f"成功加载并转换数据，共{len(converted_data['devices'])}个设备")
            return converted_data
        except FileNotFoundError:
            logger.error(f"测试数据文件不存在: {self.test_data_path}")
            return {
                'devices': [],
                'buildings': [],
                'roads': [],
                'rivers': [],
                'boundaries': {}
            }
        except json.JSONDecodeError as e:
            logger.error(f"解析测试数据失败: {e}")
            return {
                'devices': [],
                'buildings': [],
                'roads': [],
                'rivers': [],
                'boundaries': {}
            }

    def _load_area_test_data(self, tq_id: str) -> Dict[str, Any]:
        """
        根据台区ID加载对应的测试数据文件
        
        Args:
            tq_id: 台区ID
            
        Returns:
            Dict[str, Any]: 加载的测试数据，如果文件不存在则返回空字典
        """
        # 在多个可能的目录中查找台区数据文件
        possible_paths = [
            # 在GisData目录中查找
            os.path.join("GisData", f"{tq_id}.json"),
            os.path.join("GisData", "Building_detail", f"{tq_id}_detail.json"),
            # 在当前目录查找
            f"{tq_id}.json",
            # 在test_data_path同级目录查找
            os.path.join(os.path.dirname(self.test_data_path), f"{tq_id}.json")
        ]
        
        data_file_path = None
        for path in possible_paths:
            if os.path.exists(path):
                data_file_path = path
                break
        
        # 如果指定的台区数据文件不存在，尝试使用默认的测试数据
        if not data_file_path:
            logger.warning(f"台区 {tq_id} 的数据文件在以下路径均不存在: {possible_paths}，使用默认测试数据")
            return self.test_data if self.test_data else {}
        
        try:
            logger.info(f"为台区 {tq_id} 加载专属数据文件: {data_file_path}")
            with open(data_file_path, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)

            # 将标注数据转换为评分器期望的格式
            converted_data = {
                'devices': [],
                'buildings': [],
                'roads': [],
                'rivers': [],
                'boundaries': {}
            }

            # 处理标注数据
            if 'annotations' in raw_data:
                for annotation in raw_data['annotations']:
                    label = annotation.get('label', '')
                    # 映射标注标签到评分器期望的设备类型
                    device_type = label
                    if '电缆终端头' in label or '电缆头' in label:
                        device_type = 'head'
                    elif '电缆段' in label:
                        device_type = 'cable_segment'
                    elif '电杆' in label or '杆塔' in label:
                        device_type = '杆塔'
                    elif '墙支架' in label or '墙担' in label:
                        device_type = '墙支架'
                    elif '分支箱' in label:
                        device_type = '分支箱'
                    elif '接入点' in label:
                        device_type = '接入点'
                    elif '配电箱' in label or '计量箱' in label:
                        device_type = '计量箱'

                    # 计算中心点坐标（如果有多个点）
                    points = annotation.get('points', [])
                    x = y = 0.0
                    if len(points) > 0:
                        x = sum(p[0] for p in points) / len(points)
                        y = sum(p[1] for p in points) / len(points)

                    # 特殊处理分支箱：如果是分支箱，只保留中心点作为唯一的点
                    if '分支箱' in label:
                        points = [[x, y]]

                    device = {
                        'id': annotation.get('id', ''),
                        'type': device_type,
                        'label': label,
                        'points': points,
                        'x': x,
                        'y': y,
                        'properties': {},
                        'flag': annotation.get('flag', '')
                    }
                    converted_data['devices'].append(device)

            logger.info(f"成功加载台区 {tq_id} 的数据，共{len(converted_data['devices'])}个设备")
            return converted_data
        except Exception as e:
            logger.error(f"加载台区 {tq_id} 数据失败: {e}，使用默认测试数据")
            return self.test_data if self.test_data else {}

    def _load_manual_scores(self) -> Dict[str, Any]:
        """加载人工打分结果"""
        try:
            manual_scores = {}
            file_size = os.path.getsize(self.manual_score_path)
            logger.info(f"人工打分结果文件大小: {file_size/1024/1024:.2f}MB")

            # 使用ijson库进行流式解析大JSON文件
            try:
                import ijson
                with open(self.manual_score_path, 'r', encoding='utf-8') as f:
                    # 查找mgx_rating_result数组
                    objects = ijson.items(f, 'mgx_rating_result.item')
                    for item in objects:
                        tq_id = item.get('tq_id', '')
                        if tq_id:
                            manual_scores[tq_id] = item
                            # 同时存储不带前缀的ID作为键，以支持不同格式的查询
                            if '-' in tq_id:
                                short_id = tq_id.split('-')[-1]
                                manual_scores[short_id] = item
                logger.info(f"使用ijson成功加载人工打分结果，共{len(manual_scores)}个台区")
            except ImportError:
                # 如果没有ijson库，尝试使用jsonlines
                try:
                    import jsonlines
                    with jsonlines.open(self.manual_score_path) as reader:
                        for item in reader:
                            if isinstance(item, dict) and 'mgx_rating_result' in item:
                                for result in item['mgx_rating_result']:
                                    tq_id = result.get('tq_id', '')
                                    if tq_id:
                                        manual_scores[tq_id] = result
                                        # 同时存储不带前缀的ID作为键
                                        if '-' in tq_id:
                                            short_id = tq_id.split('-')[-1]
                                            manual_scores[short_id] = result
                    logger.info(f"使用jsonlines成功加载人工打分结果，共{len(manual_scores)}个台区")
                except ImportError:
                    # 如果没有额外库，尝试读取整个文件
                    try:
                        with open(self.manual_score_path, 'r', encoding='utf-8') as f:
                            raw_data = json.load(f)
                            if 'mgx_rating_result' in raw_data:
                                for item in raw_data['mgx_rating_result']:
                                    tq_id = item.get('tq_id', '')
                                    if tq_id:
                                        manual_scores[tq_id] = item
                                        # 同时存储不带前缀的ID作为键
                                        if '-' in tq_id:
                                            short_id = tq_id.split('-')[-1]
                                            manual_scores[short_id] = item
                        logger.info(f"成功加载人工打分结果，共{len(manual_scores)}个台区")
                    except json.JSONDecodeError:
                        logger.error("无法解析人工打分结果文件，请安装ijson或jsonlines库")
                        # 返回空字典
        except FileNotFoundError:
            logger.error(f"人工打分结果文件不存在: {self.manual_score_path}")
            return {}
        return manual_scores

    def score_single_area(self, test_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """对单个台区进行程序打分
        
        Args:
            test_data: 可选的测试数据，如果不提供则使用self.test_data
        """
        # 使用传入的test_data或默认的self.test_data
        data_to_use = test_data if test_data is not None else self.test_data
        
        logger.info("开始对单个台区进行程序打分")
        program_scores = {}
        total_score = 0.0

        for name, scorer in self.scorers.items():
            logger.info(f"\n===== 测试 {name} =====")
            try:
                # 根据评分器类型调用相应的评分方法
                if name == '架空线评分器':
                    result = scorer.score_overhead_lines(data_to_use)
                elif name == '电缆线路评分器':
                    result = scorer.score_cable_lines(data_to_use)
                elif name == '分支箱评分器':
                    result = scorer.score_branch_boxes(data_to_use)
                elif name == '接入点评分器':
                    result = scorer.score_access_points(data_to_use)
                elif name == '计量箱评分器':
                    result = scorer.score_meter_boxes(data_to_use)
                else:
                    logger.warning(f"未知评分器类型: {name}")
                    continue

                # 保存评分结果
                program_scores[name] = {
                    'score': result.get('total_score', 0.0),
                    'level': result.get('level', '未知'),
                    'basis': result.get('basis', [])
                }
                total_score += program_scores[name]['score']

                # 打印评分结果
                logger.info(f"{name} 得分: {program_scores[name]['score']}分")
                logger.info(f"等级: {program_scores[name]['level']}")
                logger.info(f"评分依据:")
                for i, basis in enumerate(program_scores[name]['basis'], 1):
                    logger.info(f"  {i}. {basis}")

            except Exception as e:
                logger.error(f"测试 {name} 失败: {e}")
                program_scores[name] = {'score': 0.0, 'level': '错误', 'basis': [f'评分失败: {str(e)}']}

        # 添加总分
        program_scores['total'] = {
            'score': total_score,
            'level': self._determine_level(total_score)
        }
        logger.info(f"\n程序总得分: {total_score}分")
        logger.info(f"总体等级: {program_scores['total']['level']}")

        return program_scores

    def _determine_level(self, score: float) -> str:
        """根据分数确定等级"""
        if score >= 90:
            return '优秀'
        elif score >= 80:
            return '良好'
        elif score >= 70:
            return '中等'
        elif score >= 60:
            return '合格'
        else:
            return '不合格'

    def compare_with_manual(self, program_scores: Dict[str, Any], tq_id: str) -> Dict[str, Any]:
        """
        对比程序打分和人工打分结果
        Args:
            program_scores: 程序打分结果
            tq_id: 台区ID
        Returns:
            对比结果
        """
        logger.info(f"\n===== 对比程序打分与人工打分 (台区ID: {tq_id}) =====")
        comparison = {
            'tq_id': tq_id,
            'program_total': program_scores['total'],
            'manual_total': {'score': 0.0, 'level': '未知'}, 
            'items': []
        }

        # 获取人工打分结果
        manual_score = self.manual_scores.get(tq_id, {})
        if not manual_score:
            logger.warning(f"未找到台区 {tq_id} 的人工打分结果")
            # 打印所有可用的台区ID，帮助用户选择正确的ID
            if self.manual_scores:
                logger.info(f"可用的台区ID列表: {list(self.manual_scores.keys())[:10]}{'...' if len(self.manual_scores) > 10 else ''}")
            # 函数不需要返回值，删除多余的return语句

        # 提取人工打分总分
        # 尝试多种可能的总分字段路径
        manual_total = 0.0
        if 'final_score' in manual_score:
            manual_total = float(manual_score['final_score'])
        elif 'total_score' in manual_score:
            manual_total = float(manual_score['total_score'])
        elif 'result_content' in manual_score:
            try:
                # 假设result_content是JSON字符串
                result_content = json.loads(manual_score['result_content'])
                # 尝试从result_content中提取总分
                if isinstance(result_content, dict):
                    if 'final_score' in result_content:
                        manual_total = float(result_content['final_score'])
                    elif 'total_score' in result_content:
                        manual_total = float(result_content['total_score'])
                elif isinstance(result_content, list):
                    for item in result_content:
                        if isinstance(item, dict):
                            if 'score' in item:
                                manual_total += float(item.get('score', 0))
                            elif 'children' in item:
                                for child in item['children']:
                                    if isinstance(child, dict) and 'score' in child:
                                        manual_total += float(child.get('score', 0))
            except:
                logger.warning("无法解析人工打分结果中的详细分数")

        comparison['manual_total']['score'] = manual_total
        comparison['manual_total']['level'] = self._determine_level(manual_total)

        # 对比各项评分
        for program_name, program_info in program_scores.items():
            if program_name == 'total':
                continue

            manual_name = self.score_mapping.get(program_name, program_name)
            manual_item_score = 0.0

            # 尝试从人工打分中提取对应项的分数
            if 'result_content' in manual_score:
                try:
                    result_content = json.loads(manual_score['result_content'])
                    if isinstance(result_content, list):
                        for item in result_content:
                            if isinstance(item, dict):
                                # 尝试匹配项目名称
                                if item.get('name') == manual_name or item.get('label') == manual_name:
                                    manual_item_score = float(item.get('score', 0))
                                    break
                                # 检查子项目
                                if 'children' in item:
                                    for child in item['children']:
                                        if isinstance(child, dict) and (child.get('name') == manual_name or child.get('label') == manual_name):
                                            manual_item_score = float(child.get('score', 0))
                                            break
                except:
                    logger.warning(f"无法解析{program_name}的人工打分结果")

            # 计算差异
            difference = program_info['score'] - manual_item_score
            # 当人工得分为0时，差异百分比无意义，设置为None或特殊值
            percentage_diff = (difference / manual_item_score * 100) if manual_item_score > 0 else None

            comparison['items'].append({
                'program_name': program_name,
                'manual_name': manual_name,
                'program_score': program_info['score'],
                'manual_score': manual_item_score,
                'difference': difference,
                'percentage_diff': percentage_diff
            })

        # 计算总分差异
        comparison['total_difference'] = {
            'difference': program_scores['total']['score'] - comparison['manual_total']['score'],
            'percentage_diff': (program_scores['total']['score'] - comparison['manual_total']['score']) / comparison['manual_total']['score'] * 100 if comparison['manual_total']['score'] > 0 else 0
        }

        return comparison

    def batch_compare(self, tq_ids: List[str] = None) -> List[Dict[str, Any]]:
        """
        批量对比多个台区的打分结果
        Args:
            tq_ids: 要对比的台区ID列表，如果为None则对比所有可用台区
        Returns:
            所有台区的对比结果列表
        """
        logger.info("开始批量对比多个台区的打分结果")
        results = []

        # 确定要对比的台区ID列表
        if tq_ids is None:
            # 获取所有唯一的完整台区ID（带前缀）
            unique_tq_ids = set()
            for tq_id in self.manual_scores.keys():
                if '-' in tq_id:
                    unique_tq_ids.add(tq_id)
            tq_ids = list(unique_tq_ids)
            logger.info(f"将对比所有{len(tq_ids)}个台区")
        else:
            logger.info(f"将对比指定的{len(tq_ids)}个台区")

        # 为每个台区进行打分和对比
        for tq_id in tq_ids:
            logger.info(f"\n===== 处理台区: {tq_id} =====")
            try:
                # 为当前台区加载专属的测试数据
                area_test_data = self._load_area_test_data(tq_id)
                # 使用台区专属数据进行程序打分
                program_scores = self.score_single_area(test_data=area_test_data)
                # 对比程序打分和人工打分
                comparison = self.compare_with_manual(program_scores, tq_id)
                results.append(comparison)
            except Exception as e:
                logger.error(f"处理台区 {tq_id} 失败: {e}")
                # 添加错误信息到结果
                results.append({
                    'tq_id': tq_id,
                    'error': str(e)
                })

        return results

    def generate_markdown_report(self, results: List[Dict[str, Any]], output_path: str) -> None:
        """
        生成Markdown格式的对比报告
        Args:
            results: 对比结果列表
            output_path: 输出文件路径
        """
        logger.info(f"开始生成Markdown报告: {output_path}")

        with open(output_path, 'w', encoding='utf-8') as f:
            # 写入报告标题和概述
            f.write("# 台区打分对比分析报告\n\n")
            f.write("## 项目概述\n\n")
            f.write("本报告展示了多个台区的程序自动打分与人工打分结果的详细对比分析。\n\n")
            f.write(f"共对比了 {len(results)} 个台区。\n\n")

            # 为每个台区生成对比表格
            for i, result in enumerate(results, 1):
                if 'error' in result:
                    f.write(f"### 台区 {i}: {result['tq_id']} (处理失败)\n\n")
                    f.write(f"**错误信息**: {result['error']}\n\n")
                    continue

                f.write(f"### 台区 {i}: {result['tq_id']}\n\n")

                # 总分对比
                f.write("#### 总分对比\n\n")
                f.write("| 评分方式 | 总得分 | 等级     |\n")
                f.write("|----------|--------|----------|\n")
                f.write(f"| 程序打分 | {result['program_total']['score']:.1f}   | {result['program_total']['level']}   |\n")
                f.write(f"| 人工打分 | {result['manual_total']['score']:.1f}   | {result['manual_total']['level']}   |\n")
                diff = result['total_difference']['difference']
                percent_diff = result['total_difference']['percentage_diff']
                f.write(f"| 差异     | {diff:.2f}  | {percent_diff:.2f}%  |\n\n")

                # 单项对比
                f.write("#### 单项对比\n\n")
                f.write("| 评分项   | 程序得分 | 人工得分 | 差异 | 差异百分比 |\n")
                f.write("|----------|----------|----------|------|------------|\n")
                for item in result['items']:
                    # 处理差异百分比为None的情况
                    percentage_str = f"{item['percentage_diff']:.2f}%" if item['percentage_diff'] is not None else "N/A"
                    f.write(f"| {item['manual_name']} | {item['program_score']:.1f} | {item['manual_score']:.1f} | {item['difference']:.1f} | {percentage_str} |\n")
                f.write("\n")

            # 添加总结和改进建议
            f.write("## 总结与改进\n\n")
            f.write("1. **人工打分数据提取问题**: 部分单项得分提取不完整，导致显示为0分\n")
            f.write("   - 改进方向: 根据实际数据结构调整提取逻辑，支持更多可能的字段路径\n\n")
            f.write("2. **评分标准一致性**: 程序打分与人工打分的评分标准可能存在差异\n")
            f.write("   - 改进方向: 进一步对齐两者的评分标准，提高对比的准确性\n\n")
            f.write("3. **可视化展示**: 可增加图表展示，如得分对比柱状图、差异分布等\n")
            f.write("   - 改进方向: 集成数据可视化库，生成直观的对比图表\n\n")

        logger.info(f"Markdown报告已生成: {output_path}")

        # 打印对比结果
        if results:
            # 只打印第一个结果作为示例
            result = results[0]
            logger.info(f"程序总得分: {result['program_total']['score']}分 ({result['program_total']['level']})")
            logger.info(f"人工总得分: {result['manual_total']['score']}分 ({result['manual_total']['level']})")
            logger.info(f"总差异: {result['total_difference']['difference']:.2f}分 ({result['total_difference']['percentage_diff']:.2f}%)")
            logger.info("\n单项对比:")
            for item in result['items']:
                logger.info(f"{item['program_name']} ({item['manual_name']}):")
                logger.info(f"  程序得分: {item['program_score']}分")
            logger.info(f"  人工得分: {item['manual_score']}分")
            # 处理差异百分比为None的情况
            percentage_str = f"{item['percentage_diff']:.2f}%" if item['percentage_diff'] is not None else "N/A"
            logger.info(f"  差异: {item['difference']:.2f}分 ({percentage_str})")

        # 函数不需要返回值，删除多余的return语句


def main():
    # 默认使用第一个标注数据文件作为测试数据
    default_test_data = os.path.join(project_root, '标注数据目录', '有对应关系的标注结果数据', 'zlh.json')
    default_manual_score = os.path.join(project_root, 'charts', '人工打分结果.json')
    default_output_report = os.path.join(project_root, '台区打分批量对比报告.md')

    # 解析命令行参数
    import argparse
    parser = argparse.ArgumentParser(description='台区打分对比工具')
    parser.add_argument('--test_data', type=str, default=default_test_data, help='测试数据文件路径')
    parser.add_argument('--manual_score', type=str, default=default_manual_score, help='人工打分结果文件路径')
    parser.add_argument('--tq_id', type=str, default='', help='指定单个台区ID')
    parser.add_argument('--batch', action='store_true', help='批量处理多个台区')
    parser.add_argument('--tq_ids', type=str, default='', help='批量处理的台区ID列表，用逗号分隔')
    parser.add_argument('--output', type=str, default=default_output_report, help='批量处理时的报告输出路径')
    args = parser.parse_args()

    # 检查文件是否存在
    if not os.path.exists(args.test_data):
        logger.error(f"测试数据文件不存在: {args.test_data}")
        sys.exit(1)
    if not os.path.exists(args.manual_score):
        logger.error(f"人工打分结果文件不存在: {args.manual_score}")
        sys.exit(1)

    # 创建对比器
    comparator = ScoreComparator(args.test_data, args.manual_score)

    # 显示可用的台区ID列表（只显示带前缀的完整ID）
    full_ids = [tid for tid in comparator.manual_scores.keys() if '-' in tid]
    if full_ids:
        logger.info(f"共找到{len(full_ids)}个台区的人工打分结果")
        logger.info(f"前10个台区ID: {full_ids[:10]}{'...' if len(full_ids) > 10 else ''}")
    else:
        logger.error("未找到任何台区的人工打分结果，请检查文件格式")
        sys.exit(1)

    if args.batch:
        # 批量处理模式
        logger.info("启用批量处理模式")
        tq_ids = None
        if args.tq_ids:
            # 解析指定的台区ID列表
            tq_ids = [tid.strip() for tid in args.tq_ids.split(',')]
            # 尝试匹配完整ID
            matched_tq_ids = []
            for tid in tq_ids:
                if tid in comparator.manual_scores:
                    matched_tq_ids.append(tid)
                elif '-' not in tid:
                    # 尝试查找匹配的带前缀ID
                    matched = [full_id for full_id in full_ids if full_id.endswith(tid)]
                    if matched:
                        matched_tq_ids.append(matched[0])
                        logger.info(f"找到匹配的台区ID: {matched[0]}")
                    else:
                        logger.warning(f"未找到台区ID: {tid}")
            tq_ids = matched_tq_ids

        # 执行批量对比
        results = comparator.batch_compare(tq_ids)

        # 生成Markdown报告
        comparator.generate_markdown_report(results, args.output)
        logger.info(f"批量对比报告已生成: {args.output}")
    else:
        # 单个台区处理模式
        # 确定台区ID
        tq_id = args.tq_id
        if not tq_id:
            # 如果未通过命令行参数指定，使用第一个可用的台区ID
            tq_id = full_ids[0]
            logger.info(f"未指定台区ID，使用第一个可用的台区ID: {tq_id}")
        else:
            # 检查用户输入的ID是否存在，如果不存在，尝试添加前缀
            if tq_id not in comparator.manual_scores and '-' not in tq_id:
                # 尝试查找匹配的带前缀ID
                matched_ids = [tid for tid in full_ids if tid.endswith(tq_id)]
                if matched_ids:
                    tq_id = matched_ids[0]
                    logger.info(f"找到匹配的台区ID: {tq_id}")
                else:
                    logger.warning(f"未找到台区ID: {tq_id}")
                    logger.info(f"使用第一个可用的台区ID: {full_ids[0]}")
                    tq_id = full_ids[0]

        # 对单个台区进行程序打分
        program_scores = comparator.score_single_area()

        # 对比程序打分和人工打分
        comparator.compare_with_manual(program_scores, tq_id)


if __name__ == '__main__':
    main()