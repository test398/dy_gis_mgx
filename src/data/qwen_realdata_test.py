import os
import json
from src.utils.qwen_api_client import QwenAPIClient

# 配置API KEY
API_KEY = os.getenv("QWEN_API_KEY", "sk-12ddc17853354879ba2a18830f3a41d7")  # 建议用环境变量

# 标注数据目录
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../标注数据目录/有对应关系的标注结果数据'))
IMG_DIR_BEFORE = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../标注数据目录/治理前标注图片/images'))
IMG_DIR_AFTER = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../标注数据目录/治理后标注图片/images'))

# 自动匹配样本对（假设文件名规则：xxx_zlq.json/xxx_zlh.json）
def find_sample_pairs(data_dir):
    zlq_files = sorted([f for f in os.listdir(data_dir) if f.endswith('_zlq.json')])
    pairs = []
    for zlq in zlq_files:
        prefix = zlq[:-9]
        zlh = prefix + '_zlh.json'
        if os.path.exists(os.path.join(data_dir, zlh)):
            pairs.append((zlq, zlh, prefix))
    return pairs

def find_image_file(img_dir, prefix):
    for fname in os.listdir(img_dir):
        if fname.startswith(prefix) and fname.endswith('.png'):
            return os.path.join(img_dir, fname)
    return None

def main():
    client = QwenAPIClient(api_key=API_KEY)
    pairs = find_sample_pairs(DATA_DIR)
    results = []
    for zlq, zlh, prefix in pairs[:5]:  # 只取前5组做示例
        json_path1 = os.path.join(DATA_DIR, zlq)
        json_path2 = os.path.join(DATA_DIR, zlh)
        with open(json_path1, 'r', encoding='utf-8') as f1, open(json_path2, 'r', encoding='utf-8') as f2:
            gis_data1 = json.load(f1)
            gis_data2 = json.load(f2)
        img1 = find_image_file(IMG_DIR_BEFORE, prefix)
        img2 = find_image_file(IMG_DIR_AFTER, prefix)
        if not img1 or not img2:
            print(f"样本 {prefix} 缺少图片，跳过")
            continue
        print(f"测试样本: {prefix}")
        resp = client.call_beautification_api(img1, img2, gis_data1, gis_data2)
        print(f"运行时间: {resp.get('run_time', 'N/A'):.2f} 秒, 有效输出: {resp.get('valid', False)}")
        results.append({
            'prefix': prefix,
            'run_time': resp.get('run_time'),
            'valid': resp.get('valid'),
            'error': resp.get('error'),
        })
    # 统计指标
    total = len(results)
    valid_count = sum(1 for r in results if r.get('valid'))
    avg_time = sum(r['run_time'] for r in results if r.get('run_time')) / max(1, total)
    print(f"\n=== 测试完成 ===\n总样本: {total}, 有效输出: {valid_count}, 平均响应时间: {avg_time:.2f} 秒")
    # 保存结果
    with open('qwen_realdata_test_result.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    main()