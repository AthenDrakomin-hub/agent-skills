#!/usr/bin/env python3
"""
context-analyzer.py — AI 编程上下文体积分析器

扫描项目中的文件，分析上下文消耗，给出瘦身建议。
帮助 AI 编程助手避免上下文溢出，实践 "think-in-code" 模式。
纯 Python 标准库，零依赖。

用法:
    python3 context-analyzer.py <项目路径> [--output report.md]
    python3 context-analyzer.py <项目路径> --top 20    # 显示最大的20个文件
    python3 context-analyzer.py <项目路径> --json
退出码: 0=完成
"""

import os
import re
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict


# 代码文件扩展名
CODE_EXTENSIONS = {'.js', '.jsx', '.ts', '.tsx', '.py', '.java', '.go', '.rs', '.php',
                   '.rb', '.cs', '.c', '.cpp', '.h', '.swift', '.kt', '.vue', '.svelte',
                   '.sql', '.sh', '.bash', '.ps1', '.yaml', '.yml', '.json', '.toml',
                   '.md', '.markdown', '.html', '.css', '.scss', '.less'}

# 忽略目录
IGNORE_DIRS = {'node_modules', '.git', 'dist', 'build', 'out', 'target', '__pycache__',
               '.next', '.nuxt', 'vendor', 'venv', '.venv', 'coverage', '.idea', '.vscode',
               'migrations', 'third_party', '3rdparty', '.turbo', '.cache', '.parcel-cache'}

# 大文件阈值（行）
LARGE_FILE_THRESHOLD = 300
# 超大文件阈值（行）
HUGE_FILE_THRESHOLD = 800
# Token 估算系数（中文约1.5字/token，英文约4字符/token，取平均3字符/token）
CHARS_PER_TOKEN = 3


def should_ignore(filepath):
    parts = Path(filepath).parts
    return any(p in IGNORE_DIRS for p in parts)


def estimate_tokens(content):
    """估算 token 数"""
    return len(content) // CHARS_PER_TOKEN


def analyze_project(root, top_n=20):
    """分析项目上下文体积"""
    files = []
    total_size = 0
    total_tokens = 0
    total_lines = 0

    for f in Path(root).rglob('*'):
        if not f.is_file() or should_ignore(f):
            continue
        if f.suffix not in CODE_EXTENSIONS:
            continue

        try:
            content = f.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            continue

        lines = content.count('\n') + 1
        size = len(content.encode('utf-8'))
        tokens = estimate_tokens(content)

        rel_path = str(f.relative_to(root))
        files.append({
            "path": rel_path,
            "lines": lines,
            "size": size,
            "tokens": tokens,
            "extension": f.suffix,
            "category": "code" if f.suffix not in {'.md', '.markdown', '.json', '.yaml', '.yml'} else "config/doc"
        })

        total_size += size
        total_tokens += tokens
        total_lines += lines

    # 按 token 排序
    files.sort(key=lambda x: x['tokens'], reverse=True)

    # 统计
    large_files = [f for f in files if f['lines'] > LARGE_FILE_THRESHOLD]
    huge_files = [f for f in files if f['lines'] > HUGE_FILE_THRESHOLD]
    top_files = files[:top_n]

    # 按扩展名统计
    ext_stats = defaultdict(lambda: {"count": 0, "tokens": 0, "lines": 0})
    for f in files:
        ext_stats[f['extension']]['count'] += 1
        ext_stats[f['extension']]['tokens'] += f['tokens']
        ext_stats[f['extension']]['lines'] += f['lines']

    # 上下文风险评估
    risk_level = "low"
    risk_reasons = []
    if total_tokens > 100000:
        risk_level = "critical"
        risk_reasons.append(f"总 token 估算 {total_tokens:,}，超过 100K，单次 Read 全部文件会溢出")
    elif total_tokens > 50000:
        risk_level = "high"
        risk_reasons.append(f"总 token 估算 {total_tokens:,}，超过 50K，上下文压力大")
    elif total_tokens > 20000:
        risk_level = "medium"
        risk_reasons.append(f"总 token 估算 {total_tokens:,}，需要选择性读取")

    if len(huge_files) > 0:
        risk_reasons.append(f"{len(huge_files)} 个文件超过 {HUGE_FILE_THRESHOLD} 行，不应直接 Read")
    if len(large_files) > 5:
        risk_reasons.append(f"{len(large_files)} 个文件超过 {LARGE_FILE_THRESHOLD} 行，建议用脚本处理")

    # 瘦身建议
    suggestions = []
    if huge_files:
        suggestions.append({
            "priority": "high",
            "action": "对超大文件使用 grep/脚本定向读取",
            "detail": f"以下文件超过 {HUGE_FILE_THRESHOLD} 行：" + ", ".join(f['path'] for f in huge_files[:5])
        })
    if large_files:
        suggestions.append({
            "priority": "medium",
            "action": "大文件先看结构再定向读取",
            "detail": f"{len(large_files)} 个文件超过 {LARGE_FILE_THRESHOLD} 行，先用 grep 定位再 Read 特定行范围"
        })

    # 找出最占空间的扩展名
    top_ext = sorted(ext_stats.items(), key=lambda x: x[1]['tokens'], reverse=True)[:3]
    if top_ext:
        suggestions.append({
            "priority": "low",
            "action": "按文件类型选择性读取",
            "detail": f"最占空间的类型: {', '.join(f'{ext}({stats['tokens']:,} tokens)' for ext, stats in top_ext)}"
        })

    suggestions.append({
        "priority": "high",
        "action": "实践 think-in-code 模式",
        "detail": "用脚本处理数据探索，而不是 Read 整个文件。例如：grep ERROR log.txt | tail -20"
    })

    return {
        "root": str(root),
        "timestamp": datetime.now().isoformat(),
        "total_files": len(files),
        "total_lines": total_lines,
        "total_size_kb": round(total_size / 1024, 1),
        "estimated_tokens": total_tokens,
        "risk_level": risk_level,
        "risk_reasons": risk_reasons,
        "large_files_count": len(large_files),
        "huge_files_count": len(huge_files),
        "top_files": top_files,
        "extension_stats": dict(sorted(ext_stats.items(), key=lambda x: x[1]['tokens'], reverse=True)),
        "suggestions": suggestions
    }


def generate_report(result):
    """生成 Markdown 报告"""
    lines = []
    lines.append("# 上下文体积分析报告")
    lines.append("")
    lines.append(f"**项目路径**: `{result['root']}`")
    lines.append(f"**分析时间**: {result['timestamp']}")
    lines.append("")

    # 风险等级
    risk_icon = {"low": "🟢", "medium": "🟡", "high": "🟠", "critical": "🔴"}[result['risk_level']]
    lines.append(f"## 上下文风险: {risk_icon} {result['risk_level'].upper()}")
    lines.append("")
    lines.append(f"| 指标 | 值 |")
    lines.append("|---|---|")
    lines.append(f"| 文件数 | {result['total_files']} |")
    lines.append(f"| 总行数 | {result['total_lines']:,} |")
    lines.append(f"| 总大小 | {result['total_size_kb']} KB |")
    lines.append(f"| 估算 Token | {result['estimated_tokens']:,} |")
    lines.append(f"| 大文件(>{LARGE_FILE_THRESHOLD}行) | {result['large_files_count']} |")
    lines.append(f"| 超大文件(>{HUGE_FILE_THRESHOLD}行) | {result['huge_files_count']} |")
    lines.append("")

    if result['risk_reasons']:
        lines.append("### 风险原因")
        lines.append("")
        for r in result['risk_reasons']:
            lines.append(f"- {r}")
        lines.append("")

    # Top 文件
    lines.append(f"## 最占空间的 {len(result['top_files'])} 个文件")
    lines.append("")
    lines.append("| # | 文件 | 行数 | 大小 | 估算Token | 类型 |")
    lines.append("|---|---|---|---|---|---|")
    for i, f in enumerate(result['top_files'], 1):
        size_kb = round(f['size'] / 1024, 1)
        warn = " ⚠️" if f['lines'] > LARGE_FILE_THRESHOLD else ""
        lines.append(f"| {i} | `{f['path']}`{warn} | {f['lines']:,} | {size_kb}KB | {f['tokens']:,} | {f['extension']} |")
    lines.append("")

    # 按类型统计
    lines.append("## 按文件类型统计")
    lines.append("")
    lines.append("| 类型 | 文件数 | 行数 | 估算Token | 占比 |")
    lines.append("|---|---|---|---|---|")
    total_tok = result['estimated_tokens'] or 1
    for ext, stats in list(result['extension_stats'].items())[:10]:
        pct = round(stats['tokens'] / total_tok * 100, 1)
        lines.append(f"| {ext} | {stats['count']} | {stats['lines']:,} | {stats['tokens']:,} | {pct}% |")
    lines.append("")

    # 瘦身建议
    lines.append("## 瘦身建议")
    lines.append("")
    priority_order = {"high": 0, "medium": 1, "low": 2}
    for s in sorted(result['suggestions'], key=lambda x: priority_order.get(x['priority'], 3)):
        icon = {"high": "🔴", "medium": "🟡", "low": "🔵"}[s['priority']]
        lines.append(f"### {icon} [{s['priority'].upper()}] {s['action']}")
        lines.append(f"{s['detail']}")
        lines.append("")

    # Think-in-Code 模式
    lines.append("## Think-in-Code 模式示例")
    lines.append("")
    lines.append("```bash")
    lines.append("# ❌ 不要这样：Read 整个 500 行日志")
    lines.append("# Read /var/log/app.log  (50KB → 16K tokens)")
    lines.append("")
    lines.append("# ✅ 应该这样：用脚本定向提取")
    lines.append("grep ERROR /var/log/app.log | tail -20  (2KB → 600 tokens)")
    lines.append("")
    lines.append("# ❌ 不要这样：Read 整个配置文件")
    lines.append("# Read config.yaml  (10KB → 3K tokens)")
    lines.append("")
    lines.append("# ✅ 应该这样：用脚本提取需要的部分")
    lines.append("grep -A5 'database:' config.yaml  (500B → 150 tokens)")
    lines.append("```")
    lines.append("")

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='AI 编程上下文体积分析器')
    parser.add_argument('path', help='项目路径')
    parser.add_argument('--output', '-o', help='输出报告文件')
    parser.add_argument('--json', action='store_true', help='JSON 格式输出')
    parser.add_argument('--top', type=int, default=20, help='显示最大的 N 个文件')
    args = parser.parse_args()

    root = Path(args.path)
    if not root.exists():
        print(f"错误: 路径不存在: {root}", file=sys.stderr)
        sys.exit(1)

    result = analyze_project(root, args.top)

    if args.json:
        output = json.dumps(result, indent=2, ensure_ascii=False)
    else:
        output = generate_report(result)

    if args.output:
        Path(args.output).write_text(output, encoding='utf-8')
        print(f"分析报告已写入: {args.output}")
        print(f"风险等级: {result['risk_level'].upper()}")
        print(f"估算 Token: {result['estimated_tokens']:,}")
        print(f"大文件数: {result['large_files_count']}")
    else:
        print(output)


if __name__ == '__main__':
    main()
