#!/usr/bin/env python3
"""
逆向思维内容创作校验工具
检查生成的内容是否覆盖逆向思维核心要素，并拦截违规内容。

用法:
    python3 content-check.py <内容文件或文本>
    python3 content-check.py --text "直接传入的文本"
    python3 content-check.py article.md --json

退出码: 0=通过, 1=有警告, 2=有违规
"""

import sys
import re
import json
import argparse
from pathlib import Path

# ========== 逆向思维核心要素关键词 ==========

# 失败路径信号
FAILURE_SIGNALS = [
    "失败", "亏损", "亏掉", "爆仓", "爆雷", "踩雷", "追高", "重仓", "杠杆",
    "听消息", "频繁交易", "被套", "套牢", "割肉", "止损", "风险", "陷阱",
    "错误", "致命", "不可承受", "不可逆", "崩盘", "跑路", "骗局", "操纵",
    "loss", "risk", "fail", "bankrupt", "leverage",
]

# 规避原则信号
AVOIDANCE_SIGNALS = [
    "避免", "远离", "不做", "不参与", "承受", "退出", "离场", "等待",
    "不追", "不押", "不赌", "谨慎", "克制", "边界", "底线", "清单",
    "先活下来", "不犯错", "避开", "规避", "防范",
    "avoid", "stay away", "don't", "never",
]

# 金句/记忆点信号（短句、反差结构）
GOLDEN_SENTENCE_PATTERNS = [
    r"不是.{1,15}而是.{1,15}",       # 不是X而是Y
    r"与其.{1,15}不如.{1,15}",       # 与其X不如Y
    r"真正.{1,20}不是.{1,15}",       # 真正的X不是Y
    r"最.{1,5}的不是.{1,15}而是",    # 最X的不是Y而是
    r"没有.{1,10}只有.{1,10}",       # 没有X只有Y
    r"先.{1,10}再.{1,10}",           # 先X再Y
    r"能.{1,10}才.{1,10}",           # 能X才Y
    r"错过.{1,10}.{0,5}少赚",        # 错过X只是少赚
]

# ========== 违规内容检测 ==========

# 具体买卖指令（个股代码、具体价格、明确买入/卖出）
TRADE_SIGNALS = [
    r"\d{6}",                        # 6位数字（可能是股票代码）
    r"买入\s*[\u4e00-\u9fa5A-Z]{2,}", # 买入XX
    r"卖出\s*[\u4e00-\u9fa5A-Z]{2,}", # 卖出XX
    r"加仓\s*[\u4e00-\u9fa5A-Z]{2,}",
    r"建仓\s*[\u4e00-\u9fa5A-Z]{2,}",
    r"目标价\s*[\d.]+",
    r"止损价\s*[\d.]+",
    r"全仓", "满仓", "梭哈", "all in",
]

# 收益承诺
PROMISE_SIGNALS = [
    "保证收益", "保本保息", "稳赚", "必涨", "一定涨", "肯定赚",
    "零风险", "无风险", "包赚", "翻倍", "翻十倍", "财富自由",
    "guaranteed", "risk-free", "sure profit",
]

# 未经证实的指控
DEFAMATION_SIGNALS = [
    "是骗子", "是诈骗", "传销组织", "非法集资",
]


def analyze_text(text: str) -> dict:
    """分析文本，返回校验结果"""
    result = {
        "length": len(text),
        "failure_signals": [],
        "avoidance_signals": [],
        "golden_sentences": [],
        "violations": [],
        "warnings": [],
        "score": 0,
        "passed": False,
    }

    # 1. 失败路径检测
    for kw in FAILURE_SIGNALS:
        if kw in text:
            result["failure_signals"].append(kw)

    # 2. 规避原则检测
    for kw in AVOIDANCE_SIGNALS:
        if kw in text:
            result["avoidance_signals"].append(kw)

    # 3. 金句检测
    for pattern in GOLDEN_SENTENCE_PATTERNS:
        matches = re.findall(pattern, text)
        result["golden_sentences"].extend(matches)

    # 4. 违规检测
    for pattern in TRADE_SIGNALS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            result["violations"].append({
                "type": "具体买卖指令",
                "matches": matches[:5],
            })

    for kw in PROMISE_SIGNALS:
        if kw in text:
            result["violations"].append({
                "type": "收益承诺",
                "keyword": kw,
            })

    for kw in DEFAMATION_SIGNALS:
        if kw in text:
            result["violations"].append({
                "type": "未经证实指控",
                "keyword": kw,
            })

    # 5. 警告检测
    if len(text) < 50:
        result["warnings"].append("内容过短（<50字），可能未充分展开")

    if not result["failure_signals"]:
        result["warnings"].append("未检测到失败路径分析——逆向思维内容应先描述如何失败")

    if not result["avoidance_signals"]:
        result["warnings"].append('未检测到规避原则——应给出具体的"不做什么"建议')

    if not result["golden_sentences"]:
        result["warnings"].append("未检测到金句/反差结构——建议加入有记忆点的收尾句")

    # 6. 评分
    score = 0
    if result["failure_signals"]:
        score += 30
    if result["avoidance_signals"]:
        score += 30
    if result["golden_sentences"]:
        score += 20
    if 100 <= len(text) <= 2000:
        score += 10
    if not result["violations"]:
        score += 10

    result["score"] = min(score, 100)
    result["passed"] = (
        not result["violations"]
        and len(result["warnings"]) <= 1
        and result["score"] >= 60
    )

    return result


def print_report(result: dict):
    """打印人类可读的校验报告"""
    print("=" * 50)
    print("逆向思维内容校验报告")
    print("=" * 50)
    print(f"内容长度: {result['length']} 字")
    print(f"综合评分: {result['score']}/100")
    print(f"校验结果: {'✅ 通过' if result['passed'] else '❌ 未通过'}")
    print()

    print("【核心要素覆盖】")
    print(f"  失败路径信号 ({len(result['failure_signals'])}): {', '.join(result['failure_signals'][:8]) or '无'}")
    print(f"  规避原则信号 ({len(result['avoidance_signals'])}): {', '.join(result['avoidance_signals'][:8]) or '无'}")
    print(f"  金句/反差结构 ({len(result['golden_sentences'])}):")
    for gs in result["golden_sentences"][:3]:
        print(f"    - {gs}")
    if not result["golden_sentences"]:
        print("    无")
    print()

    if result["violations"]:
        print("【🚫 违规内容】")
        for v in result["violations"]:
            print(f"  - {v['type']}: {v.get('matches') or v.get('keyword')}")
        print()

    if result["warnings"]:
        print("【⚠️ 警告】")
        for w in result["warnings"]:
            print(f"  - {w}")
        print()

    if result["passed"]:
        print("✅ 内容符合逆向思维创作规范")
    else:
        print("❌ 建议修改后重新校验")
    print("=" * 50)


def main():
    parser = argparse.ArgumentParser(description="逆向思维内容创作校验工具")
    parser.add_argument("input", nargs="?", help="内容文件路径")
    parser.add_argument("--text", help="直接传入文本内容")
    parser.add_argument("--json", action="store_true", help="输出 JSON 格式")
    args = parser.parse_args()

    if args.text:
        text = args.text
    elif args.input:
        path = Path(args.input)
        if not path.exists():
            print(f"错误: 文件不存在 {path}", file=sys.stderr)
            sys.exit(2)
        text = path.read_text(encoding="utf-8")
    else:
        # 从 stdin 读取
        text = sys.stdin.read()

    if not text.strip():
        print("错误: 输入内容为空", file=sys.stderr)
        sys.exit(2)

    result = analyze_text(text)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print_report(result)

    # 退出码
    if result["violations"]:
        sys.exit(2)
    elif result["warnings"]:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
