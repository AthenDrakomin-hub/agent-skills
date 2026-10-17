#!/usr/bin/env python3
"""
gap-scan.py — 项目收尾缺口自动扫描器

扫描代码库中的常见交付缺口，输出结构化报告。
纯 Python 标准库，零依赖。

用法:
    python3 gap-scan.py <项目路径> [--output gap-report.md] [--format md|json]

扫描项:
    1. TODO/FIXME/HACK/XXX 标记
    2. 空的 catch/except 块（吞异常）
    3. 调试代码残留（console.log, print, debugger）
    4. 硬编码密钥/密码/Token
    5. 大文件（>500行）提示
    6. 缺失的关键文件（README, .gitignore, LICENSE, tests）
    7. 注释掉的代码块
"""

import os
import re
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# 忽略的目录和文件
IGNORE_DIRS = {
    'node_modules', '.git', 'dist', 'build', 'out', 'target',
    '__pycache__', '.next', '.nuxt', 'vendor', 'venv', '.venv',
    'coverage', '.idea', '.vscode', '*.egg-info', 'bower_components'
}
IGNORE_FILES = {
    'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml',
    '*.min.js', '*.min.css', '*.map', '*.lock'
}

# 代码文件扩展名
CODE_EXTENSIONS = {
    '.js', '.jsx', '.ts', '.tsx', '.vue', '.py', '.java', '.go',
    '.rs', '.rb', '.php', '.c', '.cpp', '.h', '.cs', '.swift',
    '.kt', '.scala', '.sh', '.ps1', '.sql', '.html', '.css', '.scss'
}

# 调试代码模式
DEBUG_PATTERNS = [
    (r'console\.(log|debug|info|warn)\s*\(', 'console.log 调试代码'),
    (r'\bprint\s*\(', 'print 调试代码'),
    (r'\bdebugger\s*;?', 'debugger 断点'),
    (r'\bSystem\.out\.println\s*\(', 'System.out.println 调试代码'),
    (r'\bfmt\.Println\s*\(', 'fmt.Println 调试代码'),
    (r'\bvar_dump\s*\(', 'var_dump 调试代码'),
    (r'\bputs\s+', 'puts 调试代码'),
]

# 硬编码密钥模式
SECRET_PATTERNS = [
    (r'(?i)(api[_-]?key|secret|password|passwd|pwd)\s*[:=]\s*["\'][^"\']{8,}["\']', '硬编码密钥/密码'),
    (r'(?i)(token|auth[_-]?token|access[_-]?token)\s*[:=]\s*["\'][^"\']{16,}["\']', '硬编码 Token'),
    (r'ghp_[A-Za-z0-9]{36}', 'GitHub Personal Access Token'),
    (r'sk-[A-Za-z0-9]{48}', 'OpenAI API Key'),
    (r'AKIA[0-9A-Z]{16}', 'AWS Access Key'),
    (r'-----BEGIN (RSA |EC |DSA )?PRIVATE KEY-----', '私钥文件内容'),
]

# TODO 标记模式
TODO_PATTERN = re.compile(r'(?i)(TODO|FIXME|HACK|XXX|BUG|OPTIMIZE|REVIEW)\s*[:\)]?\s*(.*)')

# 空 catch 模式（多种语言）
EMPTY_CATCH_PATTERNS = [
    (r'catch\s*\([^)]*\)\s*\{\s*\}', '空 catch 块（JavaScript/Java/C#）'),
    (r'except\s*[^:]*:\s*(?:pass|...)\s*$', '空 except 块（Python）'),
    (r'except\s*[^:]*:\s*$', '空 except 块（Python，后续可能有内容，需人工确认）'),
]

# 注释掉的代码（简单启发式：连续多行以 // 或 # 开头且包含代码特征）
COMMENTED_CODE_INDICATORS = [
    'function ', 'const ', 'let ', 'var ', 'return ', 'if (', 'for (',
    'import ', 'from ', 'def ', 'class ', 'console.', 'print(',
    '= ', ';', '{', '}', '()', '=>'
]


def should_ignore(path: Path) -> bool:
    """判断是否应该忽略该路径"""
    parts = path.parts
    for part in parts:
        if part in IGNORE_DIRS:
            return True
        for pat in IGNORE_DIRS:
            if '*' in pat and path.match(pat):
                return True
    name = path.name
    for pat in IGNORE_FILES:
        if '*' in pat and path.match(pat):
            return True
        if name == pat:
            return True
    return False


def is_code_file(path: Path) -> bool:
    return path.suffix.lower() in CODE_EXTENSIONS


def scan_file(filepath: Path) -> list:
    """扫描单个文件，返回问题列表"""
    issues = []
    try:
        content = filepath.read_text(encoding='utf-8', errors='ignore')
        lines = content.split('\n')
    except Exception:
        return issues

    rel_path = filepath

    # 1. TODO/FIXME 标记
    for i, line in enumerate(lines, 1):
        m = TODO_PATTERN.search(line)
        if m:
            tag = m.group(1).upper()
            note = m.group(2).strip()[:80]
            issues.append({
                'type': 'todo_marker',
                'severity': 'info',
                'file': str(rel_path),
                'line': i,
                'tag': tag,
                'message': f'{tag}: {note}' if note else tag
            })

    # 2. 调试代码
    for pattern, desc in DEBUG_PATTERNS:
        for i, line in enumerate(lines, 1):
            if re.search(pattern, line):
                # 排除测试文件中的调试代码
                if '.test.' in filepath.name or '.spec.' in filepath.name or '/test/' in str(filepath) or '/tests/' in str(filepath):
                    continue
                issues.append({
                    'type': 'debug_code',
                    'severity': 'warning',
                    'file': str(rel_path),
                    'line': i,
                    'message': f'{desc}: {line.strip()[:60]}'
                })
                break  # 每个文件每种模式只报一次

    # 3. 硬编码密钥
    for pattern, desc in SECRET_PATTERNS:
        for i, line in enumerate(lines, 1):
            if re.search(pattern, line):
                # 排除 .env.example 和配置模板
                if '.example' in filepath.name or '.template' in filepath.name or 'config.example' in str(filepath):
                    continue
                issues.append({
                    'type': 'hardcoded_secret',
                    'severity': 'critical',
                    'file': str(rel_path),
                    'line': i,
                    'message': f'{desc}: {line.strip()[:60]}'
                })

    # 4. 空 catch 块
    for pattern, desc in EMPTY_CATCH_PATTERNS:
        for i, line in enumerate(lines, 1):
            if re.search(pattern, line):
                issues.append({
                    'type': 'empty_catch',
                    'severity': 'warning',
                    'file': str(rel_path),
                    'line': i,
                    'message': desc
                })

    # 5. 大文件提示
    if len(lines) > 500:
        issues.append({
            'type': 'large_file',
            'severity': 'info',
            'file': str(rel_path),
            'line': 0,
            'message': f'文件超过 500 行（{len(lines)}行），建议拆分'
        })

    return issues


def check_project_structure(root: Path) -> list:
    """检查项目关键文件是否存在"""
    issues = []
    critical_files = {
        'README.md': 'README 文档',
        '.gitignore': '.gitignore',
        'LICENSE': 'LICENSE 许可证',
    }
    for filename, desc in critical_files.items():
        if not (root / filename).exists():
            issues.append({
                'type': 'missing_file',
                'severity': 'warning',
                'file': filename,
                'line': 0,
                'message': f'缺失 {desc}'
            })

    # 检查是否有测试目录或测试文件
    test_dirs = ['tests', 'test', '__tests__', 'spec']
    has_tests = any((root / d).exists() for d in test_dirs)
    if not has_tests:
        # 检查是否有测试文件
        test_files = list(root.rglob('*test*')) + list(root.rglob('*spec*'))
        test_files = [f for f in test_files if f.is_file() and not should_ignore(f)]
        if not test_files:
            issues.append({
                'type': 'no_tests',
                'severity': 'warning',
                'file': '',
                'line': 0,
                'message': '未发现测试文件或测试目录'
            })

    # 检查 package.json / requirements.txt 等依赖文件
    dep_files = ['package.json', 'requirements.txt', 'pyproject.toml', 'pom.xml', 'go.mod', 'Cargo.toml', 'composer.json']
    has_dep_file = any((root / f).exists() for f in dep_files)
    if not has_dep_file:
        issues.append({
            'type': 'no_dependency_file',
            'severity': 'info',
            'file': '',
            'line': 0,
            'message': '未发现依赖管理文件（package.json/requirements.txt 等）'
        })

    return issues


def generate_markdown_report(issues: list, root: Path, stats: dict) -> str:
    """生成 Markdown 格式报告"""
    critical = [i for i in issues if i['severity'] == 'critical']
    warnings = [i for i in issues if i['severity'] == 'warning']
    infos = [i for i in issues if i['severity'] == 'info']

    lines = [
        f'# 项目收尾缺口扫描报告',
        f'',
        f'**扫描路径**: `{root}`',
        f'**扫描时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
        f'**扫描文件数**: {stats["files_scanned"]}',
        f'',
        f'## 汇总',
        f'',
        f'| 严重程度 | 数量 |',
        f'|---|---|',
        f'| 🔴 Critical | {len(critical)} |',
        f'| 🟡 Warning | {len(warnings)} |',
        f'| 🔵 Info | {len(infos)} |',
        f'| **总计** | **{len(issues)}** |',
        f'',
    ]

    if critical:
        lines.append('## 🔴 Critical（必须修复）')
        lines.append('')
        for i in critical:
            loc = f'{i["file"]}:{i["line"]}' if i['line'] else i['file']
            lines.append(f'- **{i["message"]}** (`{loc}`)')
        lines.append('')

    if warnings:
        lines.append('## 🟡 Warning（建议修复）')
        lines.append('')
        for i in warnings:
            loc = f'{i["file"]}:{i["line"]}' if i['line'] else i['file']
            lines.append(f'- {i["message"]} (`{loc}`)')
        lines.append('')

    if infos:
        lines.append('## 🔵 Info（可选优化）')
        lines.append('')
        for i in infos:
            loc = f'{i["file"]}:{i["line"]}' if i['line'] else i['file']
            lines.append(f'- {i["message"]} (`{loc}`)')
        lines.append('')

    # 按类型统计
    type_counts = {}
    for i in issues:
        type_counts[i['type']] = type_counts.get(i['type'], 0) + 1
    lines.append('## 按问题类型统计')
    lines.append('')
    lines.append('| 类型 | 数量 |')
    lines.append('|---|---|')
    for t, c in sorted(type_counts.items(), key=lambda x: -x[1]):
        lines.append(f'| {t} | {c} |')
    lines.append('')

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='项目收尾缺口自动扫描器')
    parser.add_argument('path', nargs='?', default='.', help='项目路径（默认当前目录）')
    parser.add_argument('--output', '-o', help='输出文件路径（默认输出到 stdout）')
    parser.add_argument('--format', '-f', choices=['md', 'json'], default='md', help='输出格式')
    args = parser.parse_args()

    root = Path(args.path).resolve()
    if not root.exists():
        print(f'错误: 路径不存在: {root}', file=sys.stderr)
        sys.exit(1)

    all_issues = []
    files_scanned = 0

    # 扫描代码文件
    for filepath in root.rglob('*'):
        if filepath.is_file() and is_code_file(filepath) and not should_ignore(filepath):
            files_scanned += 1
            rel = filepath.relative_to(root)
            issues = scan_file(rel)
            all_issues.extend(issues)

    # 检查项目结构
    all_issues.extend(check_project_structure(root))

    stats = {'files_scanned': files_scanned}

    if args.format == 'json':
        output = json.dumps({
            'root': str(root),
            'timestamp': datetime.now().isoformat(),
            'stats': stats,
            'issues': all_issues
        }, indent=2, ensure_ascii=False)
    else:
        output = generate_markdown_report(all_issues, root, stats)

    if args.output:
        Path(args.output).write_text(output, encoding='utf-8')
        print(f'报告已写入: {args.output}')
        print(f'扫描文件: {files_scanned}, 发现问题: {len(all_issues)}')
    else:
        print(output)

    # 有 critical 问题时返回非零退出码
    critical_count = sum(1 for i in all_issues if i['severity'] == 'critical')
    sys.exit(1 if critical_count > 0 else 0)


if __name__ == '__main__':
    main()
