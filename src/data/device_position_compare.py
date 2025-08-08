import matplotlib
matplotlib.use('Agg')
import json
import matplotlib.pyplot as plt
import os
import logging
import warnings
from matplotlib import rcParams
import matplotlib.patches as mpatches
from itertools import cycle

# 配置中文字体与负号显示，尽量避免Glyph缺字告警
rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'SimSun', 'Arial Unicode MS', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False
# 如仍有个别字符缺字，屏蔽相关UserWarning
warnings.filterwarnings("ignore", category=UserWarning, message=r"Glyph .* missing from current font")


def compare_device_positions(file1, file2, out_img_path='设备位置对比_auto.png'):
    """
    对比两个json文件中的设备位置，并生成对比图片（左右两个子图）。
    - 按points围成区域绘制：>=3点绘制填充多边形；2点绘制线段；1点绘制散点
    - 不同设备(label/type)使用不同颜色，并在右上角图例标识
    - 左右子图坐标范围一致、等比例
    Args:
        file1: 原始标注json路径
        file2: 治理后json路径
        out_img_path: 输出图片路径
    """
    

    logger = logging.getLogger(__name__)

    def parse_annotations(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        annotations = []
        for ann in data.get('annotations', []):
            pts = ann.get('points', [])
            if not pts:
                continue
            label = ann.get('label') or ann.get('type') or '未命名'
            annotations.append({'label': label, 'points': pts})
        return annotations

    def compute_extent(anns_list):
        all_pts = []
        for anns in anns_list:
            for ann in anns:
                all_pts.extend(ann['points'])
        if not all_pts:
            return 0, 100, 0, 100
        xs = [p[0] for p in all_pts]
        ys = [p[1] for p in all_pts]
        pad_x = max(1, (max(xs) - min(xs)) * 0.05)
        pad_y = max(1, (max(ys) - min(ys)) * 0.05)
        return min(xs) - pad_x, max(xs) + pad_x, min(ys) - pad_y, max(ys) + pad_y

    def build_color_map(labels):
        cmap = plt.get_cmap('tab20')
        palette = list(cmap.colors)
        color_cycle = cycle(palette)
        mapping = {}
        for lab in sorted(labels):
            mapping[lab] = next(color_cycle)
        return mapping

    def draw_annotations(ax, anns, color_map):
        for ann in anns:
            label = ann['label']
            color = color_map.get(label, '#333333')
            pts = ann['points']
            if len(pts) >= 3:
                xs = [p[0] for p in pts] + [pts[0][0]]
                ys = [p[1] for p in pts] + [pts[0][1]]
                ax.fill(xs, ys, facecolor=color, alpha=0.25, edgecolor=color, linewidth=1)
            elif len(pts) == 2:
                xs = [pts[0][0], pts[1][0]]
                ys = [pts[0][1], pts[1][1]]
                ax.plot(xs, ys, color=color, linewidth=1.8, alpha=0.9)
            else:
                ax.scatter([pts[0][0]], [pts[0][1]], c=[color], marker='o', s=24, alpha=0.9)

    # 解析两份数据
    anns1 = parse_annotations(file1)
    anns2 = parse_annotations(file2)

    # 尝试计算评分与提升分析（健壮，不影响绘图）
    def _build_gis(anns):
        devices = []
        for a in anns:
            pts = a['points']
            if not pts:
                continue
            if len(pts) == 1:
                cx, cy = pts[0][0], pts[0][1]
            else:
                cx = sum(p[0] for p in pts) / len(pts)
                cy = sum(p[1] for p in pts) / len(pts)
            devices.append({
                'type': a['label'],  # 评分器按type过滤，这里用label兜底
                'x': cx,
                'y': cy
            })
        return {'devices': devices}

    def _extract_total(res):
        if res is None:
            return None
        if isinstance(res, (int, float)):
            return float(res)
        if isinstance(res, dict):
            if isinstance(res.get('total_score'), (int, float)):
                return float(res['total_score'])
            # 兼容：子项相加
            def _s(v):
                if isinstance(v, (int, float)):
                    return float(v)
                if isinstance(v, dict):
                    return float(v.get('score') or 0)
                return 0.0
            return _s(res.get('pole_score')) + _s(res.get('bracket_score'))
        return None

    score_summary = None
    per_axis_text = {'left': None, 'right': None}
    try:
        from src.core.overhead_line_scorer import OverheadLineScorer
        scorer = OverheadLineScorer()
        res1 = scorer.score_overhead_lines(_build_gis(anns1))
        res2 = scorer.score_overhead_lines(_build_gis(anns2))
        t1 = _extract_total(res1)
        t2 = _extract_total(res2)
        if t1 is not None and t2 is not None:
            diff = t2 - t1
            pct = (diff / t1 * 100) if t1 != 0 else 0.0
            score_summary = f"评分摘要：前={t1:.1f}，后={t2:.1f}，提升={diff:+.1f}（{pct:+.1f}%）"
            # 左右子图角落显示子项简要
            def _axis_text(res, total):
                if not isinstance(res, dict):
                    return f"总分: {total:.1f}"
                ps = res.get('pole_score')
                bs = res.get('bracket_score')
                def _fmt(x):
                    if isinstance(x, dict):
                        sc = x.get('score')
                        lv = x.get('level')
                        return f"{sc if isinstance(sc,(int,float)) else '-'}{(' / '+lv) if isinstance(lv,str) else ''}"
                    if isinstance(x, (int, float)):
                        return f"{x:.1f}"
                    return "-"
                return f"总分: {total:.1f}\n杆塔: {_fmt(ps)}\n墙支架: {_fmt(bs)}"
            per_axis_text['left'] = _axis_text(res1, t1)
            per_axis_text['right'] = _axis_text(res2, t2)
    except Exception:
        # 忽略评分异常，保证绘图
        pass

    # 统一颜色映射（两份数据的label全集）
    all_labels = {a['label'] for a in anns1} | {a['label'] for a in anns2}
    color_map = build_color_map(all_labels)

    # 计算统一显示范围
    x_min, x_max, y_min, y_max = compute_extent([anns1, anns2])

    # 绘图（左右子图）
    fig, axes = plt.subplots(1, 2, figsize=(14, 7))

    # 左：原始标注
    ax = axes[0]
    draw_annotations(ax, anns1, color_map)
    ax.set_title('原始标注')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.set_aspect('equal')
    ax.grid(True, linestyle='--', alpha=0.3)
    # 图例（右上角）
    handles = [mpatches.Patch(color=color_map[lab], label=lab) for lab in sorted(all_labels)]
    if handles:
        ax.legend(handles=handles, loc='upper right', fontsize=8)
    # 左侧评分文字
    if per_axis_text['left']:
        ax.text(0.02, 0.98, per_axis_text['left'], transform=ax.transAxes, va='top', ha='left',
                fontsize=9, bbox=dict(facecolor='white', alpha=0.6, edgecolor='none', boxstyle='round'))

    # 右：治理后
    ax = axes[1]
    draw_annotations(ax, anns2, color_map)
    ax.set_title('治理后')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.set_aspect('equal')
    ax.grid(True, linestyle='--', alpha=0.3)
    # 图例（右上角）
    if handles:
        ax.legend(handles=handles, loc='upper right', fontsize=8)
    # 右侧评分文字
    if per_axis_text['right']:
        ax.text(0.02, 0.98, per_axis_text['right'], transform=ax.transAxes, va='top', ha='left',
                fontsize=9, bbox=dict(facecolor='white', alpha=0.6, edgecolor='none', boxstyle='round'))

    # 总标题与评分摘要
    fig.suptitle('设备位置对比（按设备类别上色，区域/线段/点）', fontsize=12)
    if score_summary:
        fig.text(0.5, 0.02, score_summary, ha='center', va='bottom', fontsize=10)

    plt.tight_layout()
    plt.savefig(out_img_path, dpi=200, bbox_inches='tight')
    plt.close(fig)

    logger.info(f"对比图片已保存为 {out_img_path}") 