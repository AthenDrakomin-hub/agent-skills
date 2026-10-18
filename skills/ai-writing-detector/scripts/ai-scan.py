#!/usr/bin/env python3
"""
ai-scan.py — AI 写作特征自动扫描器

扫描文本中的 AI 写作特征，输出带位置引用的检测报告。
检测 22 个 AI 指纹中的可自动化检测项，其余需要语义判断的项给出提示。
纯 Python 标准库，零依赖。

用法:
    python3 ai-scan.py <文章.txt> [--output report.md]
    python3 ai-scan.py <文章.txt> --json
    echo "文本内容" | python3 ai-scan.py -
退出码: 0=完成（无论是否命中特征）
"""

import re
import sys
import json
import argparse
import statistics
from pathlib import Path
from datetime import datetime


# ============================================================
# 22 个 AI 特征定义
# ============================================================

FEATURES = {
    1: {"name": "堵住所有反驳", "severity": "中", "auto": False,
        "desc": "论证无懈可击，把所有可能的反驳都提前堵上"},
    2: {"name": "知识全部输出", "severity": "中", "auto": False,
        "desc": "堆砌术语和数据展示专业度"},
    3: {"name": "匀速排比", "severity": "强", "auto": True,
        "desc": "三句以上结构相同、长度相近的排比句",
        "patterns": [r'([^。！？\n]{4,30}[，。]){3,}']},
    4: {"name": "同一个让步模板反复用", "severity": "中", "auto": True,
        "desc": "「虽然…但是…」「尽管…然而…」等结构重复出现",
        "patterns": [r'虽然[^。]{0,40}但是', r'尽管[^。]{0,40}然而', r'固然[^。]{0,40}但']},
    5: {"name": "给概念起名字的仪式", "severity": "弱", "auto": False,
        "desc": "反复给概念起名字制造记忆点"},
    6: {"name": "情绪曲线太光滑", "severity": "中", "auto": False,
        "desc": "情绪推进过于平滑，没有毛边和卡顿"},
    7: {"name": "替读者说蠢话然后纠正", "severity": "中", "auto": True,
        "desc": "「你可能以为…其实…」「很多人觉得…但…」",
        "patterns": [r'你可能以为', r'很多人觉得', r'有人说', r'或许你会']},
    8: {"name": "「不是X是Y」高密度", "severity": "强", "auto": True,
        "desc": "800字内出现3次以上「不是…而是…」结构",
        "patterns": [r'不是[^，。]{2,20}而是', r'不是[^，。]{2,20}是', r'与其说[^，。]{2,20}不如说']},
    9: {"name": "没有任何犹豫", "severity": "中", "auto": False,
        "desc": "全文没有任何不确定的表达"},
    10: {"name": "精确到不真实的情绪细节", "severity": "中", "auto": True,
        "desc": "「1.7秒」「2.3秒」等过于精确的数字",
        "patterns": [r'\d+\.\d+\s*秒', r'\d+\.\d+\s*分钟', r'\d+\.\d+\s*小时']},
    11: {"name": "脆弱感服务于论点", "severity": "弱", "auto": False,
        "desc": "用个人经历增强说服力，但经历过于贴合论点"},
    12: {"name": "把结论包装成「协议」", "severity": "中", "auto": True,
        "desc": "结尾给出简化版清单/协议/步骤",
        "patterns": [r'总结一下', r'最后，', r'记住以下', r'三个原则', r'五个步骤']},
    13: {"name": "每个段落都有收束金句", "severity": "中", "auto": True,
        "desc": "每段结尾都有一句漂亮的总结",
        "patterns": []},  # 特殊检测：段落结尾句模式
    14: {"name": "句子节奏过于均匀", "severity": "强", "auto": True,
        "desc": "句子长度方差过小，读起来像机器",
        "patterns": []},  # 特殊检测：句子长度统计
    15: {"name": "用身体感受替代论证", "severity": "中", "auto": True,
        "desc": "「身体知道答案」「直觉告诉我」等",
        "patterns": [r'身体知道', r'直觉告诉', r'骨子里觉得', r'本能地']},
    16: {"name": "开头「钩子+痛点+承诺」三件套", "severity": "强", "auto": True,
        "desc": "开头先卖焦虑，再给承诺",
        "patterns": [r'你是否', r'你有没有', r'是不是经常', r'为什么你总是', r'99%的人']},
    17: {"name": "连接词过度使用且位置固定", "severity": "中", "auto": True,
        "desc": "「然而」「事实上」「值得注意的是」高频出现",
        "patterns": [r'然而', r'事实上', r'值得注意的是', r'值得一提的是', r'与此同时', r'不仅如此']},
    18: {"name": "同义词刻意替换", "severity": "弱", "auto": False,
        "desc": "同一段里换好几个词说同一件事"},
    19: {"name": "中文翻译腔", "severity": "中", "auto": True,
        "desc": "「作为」「关于」「基于」「进行」等翻译腔词汇",
        "patterns": [r'作为一个', r'关于这个', r'基于以上', r'进行了', r'使得', r'从而']},
    20: {"name": "虚假的「讲个故事」", "severity": "中", "auto": True,
        "desc": "「我有一个朋友」式的虚构故事",
        "patterns": [r'我有一个朋友', r'我认识一个人', r'有这么一个', r'曾经有一个']},
    21: {"name": "结尾「你值得」式祝福", "severity": "中", "auto": True,
        "desc": "结尾空洞的祝福和鼓励",
        "patterns": [r'你值得', r'愿你', r'加油', r'相信自己', r'你可以的', r'共勉']},
    22: {"name": "对「深刻」的过拟合", "severity": "中", "auto": True,
        "desc": "「本质上」「归根结底」等升维表达",
        "patterns": [r'本质上', r'归根结底', r'说到底', r'从根本上', r'深层次']},
}


def split_sentences(text):
    """按句号、问号、感叹号、换行分割句子"""
    sentences = re.split(r'[。！？\n]+', text)
    return [s.strip() for s in sentences if s.strip()]


def split_paragraphs(text):
    """按空行分割段落"""
    paragraphs = re.split(r'\n\s*\n', text)
    return [p.strip() for p in paragraphs if p.strip()]


def detect_feature(feature_id, text, sentences, paragraphs):
    """检测单个特征，返回命中列表"""
    feature = FEATURES[feature_id]
    hits = []

    if not feature["auto"]:
        return hits  # 非自动检测项跳过

    # 特殊检测：句子节奏均匀 (#14)
    if feature_id == 14:
        if len(sentences) >= 5:
            lengths = [len(s) for s in sentences]
            mean_len = statistics.mean(lengths)
            std_len = statistics.stdev(lengths) if len(lengths) > 1 else 0
            cv = std_len / mean_len if mean_len > 0 else 0
            if cv < 0.25:  # 变异系数小于0.25说明过于均匀
                hits.append({
                    "location": f"全文{len(sentences)}句",
                    "quote": f"平均句长{mean_len:.0f}字，标准差{std_len:.1f}，变异系数{cv:.2f}",
                    "detail": f"句子长度过于均匀（CV={cv:.2f} < 0.25），读起来像机器生成"
                })
        return hits

    # 特殊检测：每段收束金句 (#13)
    if feature_id == 13:
        golden_count = 0
        for para in paragraphs:
            para_sentences = split_sentences(para)
            if para_sentences:
                last = para_sentences[-1]
                # 金句特征：短句、有哲理感、以总结词开头
                if (len(last) < 25 and
                    (re.search(r'这就是|这才是|所以说|归根结底|本质上|说到底|最终|终究|毕竟', last) or
                     re.match(r'^[^\s]{2,15}$', last))):
                    golden_count += 1
        if golden_count >= 3 and len(paragraphs) >= 3:
            hits.append({
                "location": f"{golden_count}/{len(paragraphs)}段",
                "quote": f"{golden_count}个段落以金句收束",
                "detail": f"超过半数段落有收束金句，过于工整"
            })
        return hits

    # 通用正则检测
    for pattern in feature.get("patterns", []):
        for match in re.finditer(pattern, text):
            start = max(0, match.start() - 20)
            end = min(len(text), match.end() + 20)
            context = text[start:end].replace('\n', ' ')
            hits.append({
                "location": f"第{text[:match.start()].count(chr(10))+1}行附近",
                "quote": context,
                "detail": f"命中模式: {match.group()}"
            })

    # 特征8特殊处理：800字内3次以上
    if feature_id == 8 and len(hits) >= 3:
        return hits[:5]  # 最多显示5处
    elif feature_id == 8 and len(hits) < 3:
        return []  # 不足3次不判定

    return hits


def scan_text(text):
    """扫描全文，返回检测结果"""
    sentences = split_sentences(text)
    paragraphs = split_paragraphs(text)
    char_count = len(text)
    word_count = len(re.findall(r'[\u4e00-\u9fff]', text))

    results = []
    total_hits = 0

    for fid, feature in FEATURES.items():
        if not feature["auto"]:
            results.append({
                "id": fid,
                "name": feature["name"],
                "severity": feature["severity"],
                "auto": False,
                "hits": [],
                "note": "需人工判断"
            })
            continue

        hits = detect_feature(fid, text, sentences, paragraphs)
        total_hits += len(hits)
        results.append({
            "id": fid,
            "name": feature["name"],
            "severity": feature["severity"],
            "auto": True,
            "hits": hits,
            "note": ""
        })

    # 计算 AI 指数（0-100）
    strong_hits = sum(len(r["hits"]) for r in results if r["severity"] == "强")
    medium_hits = sum(len(r["hits"]) for r in results if r["severity"] == "中")
    weak_hits = sum(len(r["hits"]) for r in results if r["severity"] == "弱")

    ai_score = min(100, strong_hits * 12 + medium_hits * 6 + weak_hits * 3)

    return {
        "char_count": char_count,
        "word_count": word_count,
        "sentence_count": len(sentences),
        "paragraph_count": len(paragraphs),
        "total_hits": total_hits,
        "strong_hits": strong_hits,
        "medium_hits": medium_hits,
        "weak_hits": weak_hits,
        "ai_score": ai_score,
        "features": results
    }


def generate_report(scan_result, filename=None):
    """生成 Markdown 检测报告"""
    lines = []
    lines.append("# AI 写作特征检测报告")
    lines.append("")
    if filename:
        lines.append(f"**检测文件**: `{filename}`")
    lines.append(f"**检测时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"**字数**: {scan_result['word_count']} 字 / {scan_result['char_count']} 字符")
    lines.append(f"**句子数**: {scan_result['sentence_count']} / **段落数**: {scan_result['paragraph_count']}")
    lines.append("")

    # AI 指数
    score = scan_result["ai_score"]
    if score >= 60:
        level = "🔴 高 AI 味"
    elif score >= 30:
        level = "🟡 中等 AI 味"
    else:
        level = "🟢 低 AI 味"
    lines.append(f"## AI 指数: {score}/100 — {level}")
    lines.append("")
    lines.append(f"强信号: {scan_result['strong_hits']} 处 | 中信号: {scan_result['medium_hits']} 处 | 弱信号: {scan_result['weak_hits']} 处")
    lines.append("")

    # 按严重度排序展示命中项
    for severity in ["强", "中", "弱"]:
        features_with_hits = [f for f in scan_result["features"]
                              if f["severity"] == severity and f["hits"]]
        if not features_with_hits:
            continue

        icon = {"强": "🔴", "中": "⚠️", "弱": "💡"}[severity]
        lines.append(f"## {icon} {severity}信号（{len(features_with_hits)}个特征）")
        lines.append("")

        for f in features_with_hits:
            lines.append(f"### 特征 #{f['id']} {f['name']}（{len(f['hits'])}处）")
            lines.append("")
            for i, hit in enumerate(f["hits"][:5], 1):
                lines.append(f"**第{i}处**（{hit['location']}）")
                lines.append(f"> {hit['quote']}")
                lines.append(f"{hit['detail']}")
                lines.append("")
            if len(f["hits"]) > 5:
                lines.append(f"*还有 {len(f['hits'])-5} 处，略*")
                lines.append("")

    # 需人工判断的特征
    manual = [f for f in scan_result["features"] if not f["auto"]]
    lines.append(f"## 📋 需人工判断的特征（{len(manual)}个）")
    lines.append("")
    lines.append("以下特征需要语义理解，脚本无法自动检测，请人工对照检查：")
    lines.append("")
    for f in manual:
        lines.append(f"- **#{f['id']} {f['name']}**（{f['severity']}）: {FEATURES[f['id']]['desc']}")
    lines.append("")

    # 总结
    lines.append("## 总结")
    lines.append("")
    if score >= 60:
        lines.append("AI 特征明显。建议重点关注强信号项，这些是最容易被识别为 AI 生成的地方。")
    elif score >= 30:
        lines.append("有一定 AI 特征。中信号项可以优化，强信号项需要重点修改。")
    else:
        lines.append("AI 特征较少。文本整体比较自然，只需关注个别命中项。")
    lines.append("")
    lines.append("以上是检测结果，不涉及修改。如果你希望去除这些 AI 特征，可以针对每一处问题思考自己真正想表达的方式。")

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='AI 写作特征扫描器')
    parser.add_argument('input', help='输入文本文件路径，或 - 表示从 stdin 读取')
    parser.add_argument('--output', '-o', help='输出报告文件路径')
    parser.add_argument('--json', action='store_true', help='JSON 格式输出')
    args = parser.parse_args()

    if args.input == '-':
        text = sys.stdin.read()
        filename = None
    else:
        filepath = Path(args.input)
        if not filepath.exists():
            print(f"错误: 文件不存在: {filepath}", file=sys.stderr)
            sys.exit(1)
        text = filepath.read_text(encoding='utf-8')
        filename = filepath.name

    if not text.strip():
        print("错误: 输入文本为空", file=sys.stderr)
        sys.exit(1)

    result = scan_text(text)

    if args.json:
        output = json.dumps(result, indent=2, ensure_ascii=False)
    else:
        output = generate_report(result, filename)

    if args.output:
        Path(args.output).write_text(output, encoding='utf-8')
        print(f"检测报告已写入: {args.output}")
        print(f"AI 指数: {result['ai_score']}/100")
        print(f"命中: {result['total_hits']} 处（强{result['strong_hits']}/中{result['medium_hits']}/弱{result['weak_hits']}）")
    else:
        print(output)


if __name__ == '__main__':
    main()
