#!/usr/bin/env python3
"""
code-review.py — 代码质量自动审查工具

只读扫描代码库中的可维护性风险，输出结构化审查报告。
检测：重复代码、长函数、神级模块、圈复杂度、耦合度、硬编码、空catch、TODO残留等。
纯 Python 标准库，零依赖。

用法:
    python3 code-review.py <项目路径> [--output report.md]
    python3 code-review.py <项目路径> --json
    python3 code-review.py <项目路径> --threshold 10   # 只显示严重度>=10的问题
退出码: 0=无Critical问题, 1=有Critical问题
"""

import os
import re
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict


# 支持的代码文件扩展名
CODE_EXTENSIONS = {'.js', '.jsx', '.ts', '.tsx', '.py', '.java', '.go', '.rs', '.php', '.rb', '.cs', '.c', '.cpp', '.h', '.swift', '.kt'}

# 忽略目录
IGNORE_DIRS = {'node_modules', '.git', 'dist', 'build', 'out', 'target', '__pycache__',
               '.next', '.nuxt', 'vendor', 'venv', '.venv', 'coverage', '.idea', '.vscode',
               'migrations', 'third_party', '3rdparty'}

# 忽略文件
IGNORE_FILES = {'.min.js', '.bundle.js', 'vendor.js', 'polyfill.js'}


class Finding:
    def __init__(self, severity, category, title, location, issue, recommendation, must_fix=False):
        self.severity = severity  # Critical, High, Medium, Low
        self.category = category
        self.title = title
        self.location = location
        self.issue = issue
        self.recommendation = recommendation
        self.must_fix = must_fix

    def to_dict(self):
        return {
            "severity": self.severity,
            "category": self.category,
            "title": self.title,
            "location": self.location,
            "issue": self.issue,
            "recommendation": self.recommendation,
            "must_fix": self.must_fix
        }


def should_ignore(filepath):
    """判断是否应该忽略该文件"""
    parts = Path(filepath).parts
    if any(p in IGNORE_DIRS for p in parts):
        return True
    name = Path(filepath).name
    if any(name.endswith(suf) for suf in IGNORE_FILES):
        return True
    return False


def find_code_files(root):
    """查找所有代码文件"""
    files = []
    for f in Path(root).rglob('*'):
        if f.is_file() and f.suffix in CODE_EXTENSIONS and not should_ignore(f):
            files.append(f)
    return files


def detect_long_functions(filepath, content):
    """检测长函数"""
    findings = []
    lines = content.split('\n')

    # 简单的函数检测：匹配 function/def/func 等
    func_patterns = [
        (r'\bfunction\s+(\w+)\s*\(', 'JavaScript'),
        (r'\bdef\s+(\w+)\s*\(', 'Python'),
        (r'\bfunc\s+(\w+)\s*\(', 'Go'),
        (r'\b(public|private|protected)\s+\w+\s+(\w+)\s*\(', 'Java/C#'),
    ]

    for pattern, lang in func_patterns:
        for match in re.finditer(pattern, content):
            func_name = match.group(1) if match.lastindex == 1 else match.group(2)
            start_line = content[:match.start()].count('\n') + 1

            # 估算函数长度：从函数开始到下一个同级函数或文件结束
            brace_count = 0
            end_line = start_line
            in_func = False
            for i in range(start_line - 1, min(start_line + 200, len(lines))):
                line = lines[i]
                brace_count += line.count('{') - line.count('}')
                if '{' in line:
                    in_func = True
                if in_func and brace_count <= 0 and '}' in line:
                    end_line = i + 1
                    break
                end_line = i + 1

            func_length = end_line - start_line + 1
            if func_length > 80:
                severity = "Critical" if func_length > 200 else "High" if func_length > 120 else "Medium"
                findings.append(Finding(
                    severity=severity,
                    category="Long Function",
                    title=f"函数过长: {func_name} ({func_length}行)",
                    location=f"{filepath}:{start_line}",
                    issue=f"函数 '{func_name}' 有 {func_length} 行，超过 80 行的建议上限",
                    recommendation="拆分为多个小函数，每个函数只做一件事",
                    must_fix=func_length > 200
                ))

    return findings


def detect_god_modules(filepath, content):
    """检测神级模块（文件过大）"""
    findings = []
    lines = content.split('\n')
    line_count = len(lines)

    if line_count > 500:
        severity = "Critical" if line_count > 1000 else "High" if line_count > 800 else "Medium"
        findings.append(Finding(
            severity=severity,
            category="God Module",
            title=f"文件过大: {Path(filepath).name} ({line_count}行)",
            location=str(filepath),
            issue=f"文件有 {line_count} 行，超过 500 行的建议上限",
            recommendation="按职责拆分为多个模块/文件",
            must_fix=line_count > 1000
        ))

    return findings


def detect_duplication(files_contents):
    """检测重复代码（简单的相似度检测）"""
    findings = []
    # 提取所有 6 行以上的代码块，比较相似度
    blocks = defaultdict(list)

    for filepath, content in files_contents.items():
        lines = [l.strip() for l in content.split('\n') if l.strip() and not l.strip().startswith('//') and not l.strip().startswith('#')]
        for i in range(len(lines) - 5):
            block = '\n'.join(lines[i:i+6])
            # 简单哈希：去掉变量名后的内容
            normalized = re.sub(r'\b\w+\b', 'X', block)
            normalized = re.sub(r'\s+', ' ', normalized)
            blocks[normalized].append((filepath, i + 1))

    # 找出在多个文件中出现的相同块
    for block_hash, locations in blocks.items():
        if len(locations) >= 2:
            file_set = set(loc[0] for loc in locations)
            if len(file_set) >= 2:
                findings.append(Finding(
                    severity="Medium",
                    category="Duplication",
                    title=f"重复代码块（出现在 {len(file_set)} 个文件中）",
                    location=", ".join(f"{f}:{l}" for f, l in locations[:3]),
                    issue=f"相同的 6 行代码块出现在 {len(file_set)} 个文件中",
                    recommendation="提取为公共函数或工具类",
                    must_fix=False
                ))
                if len(findings) > 10:  # 限制重复代码报告数量
                    break

    return findings


def detect_hardcoded_secrets(filepath, content):
    """检测硬编码密钥"""
    findings = []
    secret_patterns = [
        (r'ghp_[A-Za-z0-9]{36}', 'GitHub PAT'),
        (r'sk-[A-Za-z0-9]{48}', 'OpenAI API Key'),
        (r'AKIA[0-9A-Z]{16}', 'AWS Access Key'),
        (r'-----BEGIN [A-Z ]*PRIVATE KEY-----', '私钥'),
        (r'(?i)(password|passwd|pwd)\s*[:=]\s*["\'][^"\']{6,}["\']', '硬编码密码'),
        (r'(?i)(api[_-]?key|secret|token)\s*[:=]\s*["\'][^"\']{8,}["\']', '硬编码密钥'),
    ]

    for pattern, desc in secret_patterns:
        for match in re.finditer(pattern, content):
            line_num = content[:match.start()].count('\n') + 1
            findings.append(Finding(
                severity="Critical",
                category="Security",
                title=f"硬编码密钥: {desc}",
                location=f"{filepath}:{line_num}",
                issue=f"发现疑似 {desc}，可能导致安全漏洞",
                recommendation="移到环境变量或配置文件，并轮换已泄露的密钥",
                must_fix=True
            ))

    return findings


def detect_empty_catch(filepath, content):
    """检测空 catch 块"""
    findings = []
    # 匹配 catch (...) { 只有空白或注释的 }
    pattern = r'catch\s*\([^)]*\)\s*\{\s*(//[^\n]*\s*|/\*.*?\*/\s*)*\}'
    for match in re.finditer(pattern, content, re.DOTALL):
        line_num = content[:match.start()].count('\n') + 1
        findings.append(Finding(
            severity="High",
            category="Error Handling",
            title="空 catch 块",
            location=f"{filepath}:{line_num}",
            issue="catch 块为空，异常被静默吞掉",
            recommendation="至少记录日志，或根据业务需要重新抛出",
            must_fix=False
        ))

    return findings


def detect_todo_fixme(filepath, content):
    """检测 TODO/FIXME 残留"""
    findings = []
    for match in re.finditer(r'(?i)(TODO|FIXME|HACK|XXX)\s*[:(]?\s*(.*)', content):
        line_num = content[:match.start()].count('\n') + 1
        note = match.group(2).strip()[:50]
        findings.append(Finding(
            severity="Low",
            category="Technical Debt",
            title=f"{match.group(1).upper()} 残留",
            location=f"{filepath}:{line_num}",
            issue=f"待办事项: {note or '(无说明)'}",
            recommendation="确认是否已处理，未处理则记录到 issue tracker",
            must_fix=False
        ))
    return findings[:20]  # 限制数量


def detect_cyclomatic_complexity(filepath, content):
    """简单的圈复杂度检测"""
    findings = []
    # 统计决策点数量
    decision_points = len(re.findall(r'\b(if|else if|elif|for|while|case|catch|&&|\|\||\?)\b', content))

    if decision_points > 30:
        severity = "High" if decision_points > 50 else "Medium"
        findings.append(Finding(
            severity=severity,
            category="Complexity",
            title=f"圈复杂度过高: {decision_points} 个决策点",
            location=str(filepath),
            issue=f"文件中有 {decision_points} 个决策点（if/for/while/&&/||等），可能难以维护",
            recommendation="拆分复杂逻辑，提取辅助函数",
            must_fix=decision_points > 50
        ))

    return findings


def detect_debug_code(filepath, content):
    """检测调试代码残留"""
    findings = []
    debug_patterns = [
        (r'console\.log\s*\(', 'console.log'),
        (r'\bprint\s*\(', 'print'),
        (r'\bdebugger\b', 'debugger'),
        (r'\bvar_dump\s*\(', 'var_dump'),
        (r'\bSystem\.out\.println\s*\(', 'System.out.println'),
    ]

    for pattern, desc in debug_patterns:
        matches = list(re.finditer(pattern, content))
        if matches:
            line_num = content[:matches[0].start()].count('\n') + 1
            findings.append(Finding(
                severity="Low",
                category="Debug Code",
                title=f"调试代码残留: {desc} ({len(matches)}处)",
                location=f"{filepath}:{line_num}",
                issue=f"发现 {len(matches)} 处 {desc}，生产代码不应包含调试输出",
                recommendation="删除或替换为正式的日志记录",
                must_fix=False
            ))

    return findings


def review_codebase(root, threshold=None):
    """审查整个代码库"""
    files = find_code_files(root)
    findings = []
    files_contents = {}

    for filepath in files:
        try:
            content = filepath.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            continue

        rel_path = str(filepath.relative_to(root))
        files_contents[rel_path] = content

        findings.extend(detect_long_functions(rel_path, content))
        findings.extend(detect_god_modules(rel_path, content))
        findings.extend(detect_hardcoded_secrets(rel_path, content))
        findings.extend(detect_empty_catch(rel_path, content))
        findings.extend(detect_todo_fixme(rel_path, content))
        findings.extend(detect_cyclomatic_complexity(rel_path, content))
        findings.extend(detect_debug_code(rel_path, content))

    # 跨文件重复检测
    findings.extend(detect_duplication(files_contents))

    # 按严重度排序
    severity_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
    findings.sort(key=lambda f: severity_order.get(f.severity, 4))

    # 统计
    stats = defaultdict(int)
    categories = defaultdict(int)
    must_fix_count = 0
    for f in findings:
        stats[f.severity] += 1
        categories[f.category] += 1
        if f.must_fix:
            must_fix_count += 1

    return {
        "root": str(root),
        "timestamp": datetime.now().isoformat(),
        "files_scanned": len(files),
        "total_findings": len(findings),
        "must_fix": must_fix_count,
        "stats": dict(stats),
        "categories": dict(categories),
        "findings": [f.to_dict() for f in findings]
    }


def generate_report(result):
    """生成 Markdown 报告"""
    lines = []
    lines.append("# 代码质量审查报告")
    lines.append("")
    lines.append(f"**审查路径**: `{result['root']}`")
    lines.append(f"**审查时间**: {result['timestamp']}")
    lines.append(f"**扫描文件**: {result['files_scanned']} 个")
    lines.append(f"**发现问题**: {result['total_findings']} 个")
    lines.append(f"**必须修复**: {result['must_fix']} 个")
    lines.append("")

    # 结论
    if result['must_fix'] > 0 or result['stats'].get('Critical', 0) > 0:
        lines.append("## 结论: ❌ needs_changes")
        lines.append("")
        lines.append("存在 Critical 问题或必须修复项，修复后才能合并。")
    elif result['stats'].get('High', 0) > 0:
        lines.append("## 结论: ⚠️ needs_changes (High)")
        lines.append("")
        lines.append("存在 High 级别问题，建议修复后合并。")
    else:
        lines.append("## 结论: ✅ pass")
        lines.append("")
        lines.append("无阻塞性问题，可以合并。")
    lines.append("")

    # 统计
    lines.append("## 问题统计")
    lines.append("")
    lines.append("| 严重度 | 数量 |")
    lines.append("|---|---|")
    for sev in ["Critical", "High", "Medium", "Low"]:
        count = result['stats'].get(sev, 0)
        icon = {"Critical": "🔴", "High": "🟠", "Medium": "🟡", "Low": "🔵"}[sev]
        lines.append(f"| {icon} {sev} | {count} |")
    lines.append("")

    lines.append("## 按类别统计")
    lines.append("")
    lines.append("| 类别 | 数量 |")
    lines.append("|---|---|")
    for cat, count in sorted(result['categories'].items(), key=lambda x: -x[1]):
        lines.append(f"| {cat} | {count} |")
    lines.append("")

    # 详细问题
    lines.append("## 详细问题")
    lines.append("")

    current_severity = None
    for f in result['findings']:
        if f['severity'] != current_severity:
            current_severity = f['severity']
            icon = {"Critical": "🔴", "High": "🟠", "Medium": "🟡", "Low": "🔵"}[current_severity]
            lines.append(f"### {icon} {current_severity}")
            lines.append("")

        must = " **[必须修复]**" if f['must_fix'] else ""
        lines.append(f"**{f['title']}**{must}")
        lines.append(f"- 位置: `{f['location']}`")
        lines.append(f"- 类别: {f['category']}")
        lines.append(f"- 问题: {f['issue']}")
        lines.append(f"- 建议: {f['recommendation']}")
        lines.append("")

    if not result['findings']:
        lines.append("未发现可维护性问题。")
        lines.append("")

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='代码质量自动审查工具')
    parser.add_argument('path', help='项目路径')
    parser.add_argument('--output', '-o', help='输出报告文件')
    parser.add_argument('--json', action='store_true', help='JSON 格式输出')
    parser.add_argument('--threshold', choices=['Critical', 'High', 'Medium', 'Low'],
                        help='只显示指定严重度及以上的问题')
    args = parser.parse_args()

    root = Path(args.path)
    if not root.exists():
        print(f"错误: 路径不存在: {root}", file=sys.stderr)
        sys.exit(1)

    result = review_codebase(root)

    # 过滤严重度
    if args.threshold:
        threshold_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
        min_level = threshold_order[args.threshold]
        result['findings'] = [f for f in result['findings']
                              if threshold_order.get(f['severity'], 4) <= min_level]
        result['total_findings'] = len(result['findings'])

    if args.json:
        output = json.dumps(result, indent=2, ensure_ascii=False)
    else:
        output = generate_report(result)

    if args.output:
        Path(args.output).write_text(output, encoding='utf-8')
        print(f"审查报告已写入: {args.output}")
        print(f"扫描 {result['files_scanned']} 个文件，发现 {result['total_findings']} 个问题（{result['must_fix']} 个必须修复）")
    else:
        print(output)

    sys.exit(1 if result['must_fix'] > 0 or result['stats'].get('Critical', 0) > 0 else 0)


if __name__ == '__main__':
    main()
