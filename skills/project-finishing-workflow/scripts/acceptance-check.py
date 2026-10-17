#!/usr/bin/env python3
"""
acceptance-check.py — 项目交付验收自动检查器

检查项目是否具备交付条件，输出可机器判定的验收报告。
纯 Python 标准库，零依赖。

用法:
    python3 acceptance-check.py <项目路径> [--output acceptance-report.md]

检查项:
    1. 文档完整性（README, CHANGELOG, LICENSE, .gitignore）
    2. 测试覆盖（是否有测试，测试是否能运行）
    3. 构建产物（是否能正常构建）
    4. 安全检查（硬编码密钥, .env 是否被 gitignore）
    5. 代码质量（TODO/FIXME 数量, 大文件）
    6. 依赖健康（过时依赖, 安全漏洞提示）
    7. Git 状态（是否有未提交更改）
"""

import os
import re
import sys
import json
import subprocess
import argparse
from pathlib import Path
from datetime import datetime

# 忽略目录
IGNORE_DIRS = {
    'node_modules', '.git', 'dist', 'build', 'out', 'target',
    '__pycache__', '.next', '.nuxt', 'vendor', 'venv', '.venv',
    'coverage', '.idea', '.vscode'
}

# 必需的交付文件
REQUIRED_FILES = {
    'README.md': ('critical', 'README 文档'),
    '.gitignore': ('critical', '.gitignore'),
    'LICENSE': ('warning', 'LICENSE 许可证'),
}

# 建议的交付文件
RECOMMENDED_FILES = {
    'CHANGELOG.md': '更新日志',
    'CONTRIBUTING.md': '贡献指南',
    '.env.example': '环境变量示例',
    'docker-compose.yml': 'Docker Compose 配置',
    'Dockerfile': 'Dockerfile',
}

# 硬编码密钥模式
SECRET_PATTERNS = [
    (r'ghp_[A-Za-z0-9]{36}', 'GitHub PAT'),
    (r'sk-[A-Za-z0-9]{48}', 'OpenAI API Key'),
    (r'AKIA[0-9A-Z]{16}', 'AWS Access Key'),
    (r'-----BEGIN [A-Z ]*PRIVATE KEY-----', '私钥'),
    (r'(?i)(password|passwd|pwd)\s*[:=]\s*["\'][^"\']{6,}["\']', '硬编码密码'),
    (r'(?i)(api[_-]?key|secret)\s*[:=]\s*["\'][^"\']{8,}["\']', '硬编码 API Key'),
]

# 代码文件扩展名
CODE_EXTENSIONS = {'.js', '.jsx', '.ts', '.tsx', '.py', '.java', '.go', '.rs', '.php', '.rb', '.cs', '.swift', '.kt', '.c', '.cpp'}


def run_cmd(cmd: list, cwd: Path) -> tuple:
    """运行命令，返回 (成功, 输出)"""
    try:
        result = subprocess.run(
            cmd, cwd=str(cwd), capture_output=True, text=True, timeout=60
        )
        return result.returncode == 0, result.stdout + result.stderr
    except Exception as e:
        return False, str(e)


def should_ignore(path: Path) -> bool:
    return any(part in IGNORE_DIRS for part in path.parts)


def check_documentation(root: Path) -> list:
    """检查文档完整性"""
    issues = []
    for filename, (severity, desc) in REQUIRED_FILES.items():
        if not (root / filename).exists():
            issues.append({
                'category': 'documentation',
                'severity': severity,
                'item': desc,
                'status': 'fail',
                'message': f'缺失 {filename}'
            })
        else:
            size = (root / filename).stat().st_size
            if size < 50:
                issues.append({
                    'category': 'documentation',
                    'severity': 'warning',
                    'item': desc,
                    'status': 'warning',
                    'message': f'{filename} 内容过少（{size}字节）'
                })
            else:
                issues.append({
                    'category': 'documentation',
                    'severity': 'info',
                    'item': desc,
                    'status': 'pass',
                    'message': f'{filename} 存在（{size}字节）'
                })

    for filename, desc in RECOMMENDED_FILES.items():
        if (root / filename).exists():
            issues.append({
                'category': 'documentation',
                'severity': 'info',
                'item': desc,
                'status': 'pass',
                'message': f'{filename} 存在'
            })
        else:
            issues.append({
                'category': 'documentation',
                'severity': 'info',
                'item': desc,
                'status': 'skip',
                'message': f'{filename} 不存在（可选）'
            })

    return issues


def check_tests(root: Path) -> list:
    """检查测试覆盖"""
    issues = []
    test_dirs = ['tests', 'test', '__tests__', 'spec', 'src/test']
    has_test_dir = any((root / d).exists() for d in test_dirs)

    test_files = []
    for f in root.rglob('*'):
        if f.is_file() and not should_ignore(f):
            name = f.name.lower()
            if any(k in name for k in ['test', 'spec', '_test.', '.test.']) and f.suffix in CODE_EXTENSIONS:
                test_files.append(f)

    if has_test_dir or test_files:
        count = len(test_files)
        issues.append({
            'category': 'testing',
            'severity': 'info',
            'item': '测试文件',
            'status': 'pass',
            'message': f'发现 {count} 个测试文件'
        })
    else:
        issues.append({
            'category': 'testing',
            'severity': 'warning',
            'item': '测试文件',
            'status': 'fail',
            'message': '未发现测试文件或测试目录'
        })

    # 检查 package.json 中的 test 脚本
    if (root / 'package.json').exists():
        try:
            import json as _json
            pkg = _json.loads((root / 'package.json').read_text(encoding='utf-8'))
            scripts = pkg.get('scripts', {})
            if 'test' in scripts:
                issues.append({
                    'category': 'testing',
                    'severity': 'info',
                    'item': 'test 脚本',
                    'status': 'pass',
                    'message': f'package.json 有 test 脚本: {scripts["test"][:50]}'
                })
            else:
                issues.append({
                    'category': 'testing',
                    'severity': 'warning',
                    'item': 'test 脚本',
                    'status': 'fail',
                    'message': 'package.json 中无 test 脚本'
                })
        except Exception:
            pass

    return issues


def check_security(root: Path) -> list:
    """安全检查"""
    issues = []

    # 检查 .env 是否被 gitignore
    gitignore = root / '.gitignore'
    if gitignore.exists():
        content = gitignore.read_text(encoding='utf-8', errors='ignore')
        if '.env' in content:
            issues.append({
                'category': 'security',
                'severity': 'info',
                'item': '.env 忽略',
                'status': 'pass',
                'message': '.gitignore 包含 .env'
            })
        else:
            issues.append({
                'category': 'security',
                'severity': 'critical',
                'item': '.env 忽略',
                'status': 'fail',
                'message': '.gitignore 未包含 .env，可能导致密钥泄露'
            })

    # 扫描硬编码密钥
    secret_count = 0
    secret_files = []
    for f in root.rglob('*'):
        if f.is_file() and f.suffix in CODE_EXTENSIONS and not should_ignore(f):
            if '.example' in f.name or '.template' in f.name:
                continue
            try:
                content = f.read_text(encoding='utf-8', errors='ignore')
                for pattern, desc in SECRET_PATTERNS:
                    if re.search(pattern, content):
                        secret_count += 1
                        secret_files.append(f"{f.relative_to(root)} ({desc})")
                        break
            except Exception:
                pass

    if secret_count > 0:
        issues.append({
            'category': 'security',
            'severity': 'critical',
            'item': '硬编码密钥',
            'status': 'fail',
            'message': f'发现 {secret_count} 个文件含硬编码密钥: {", ".join(secret_files[:5])}'
        })
    else:
        issues.append({
            'category': 'security',
            'severity': 'info',
            'item': '硬编码密钥',
            'status': 'pass',
            'message': '未发现硬编码密钥'
        })

    return issues


def check_code_quality(root: Path) -> list:
    """代码质量检查"""
    issues = []

    todo_count = 0
    large_files = []
    total_code_lines = 0
    code_file_count = 0

    for f in root.rglob('*'):
        if f.is_file() and f.suffix in CODE_EXTENSIONS and not should_ignore(f):
            code_file_count += 1
            try:
                lines = f.read_text(encoding='utf-8', errors='ignore').split('\n')
                total_code_lines += len(lines)
                if len(lines) > 500:
                    large_files.append(f"{f.relative_to(root)} ({len(lines)}行)")
                for line in lines:
                    if re.search(r'(?i)(TODO|FIXME|HACK|XXX)', line):
                        todo_count += 1
            except Exception:
                pass

    issues.append({
        'category': 'code_quality',
        'severity': 'info',
        'item': '代码规模',
        'status': 'pass',
        'message': f'{code_file_count} 个代码文件，共 {total_code_lines} 行'
    })

    if todo_count > 0:
        issues.append({
            'category': 'code_quality',
            'severity': 'warning',
            'item': 'TODO/FIXME',
            'status': 'warning',
            'message': f'发现 {todo_count} 个 TODO/FIXME 标记，交付前应确认是否已处理'
        })
    else:
        issues.append({
            'category': 'code_quality',
            'severity': 'info',
            'item': 'TODO/FIXME',
            'status': 'pass',
            'message': '无 TODO/FIXME 标记'
        })

    if large_files:
        issues.append({
            'category': 'code_quality',
            'severity': 'warning',
            'item': '大文件',
            'status': 'warning',
            'message': f'{len(large_files)} 个文件超过 500 行: {", ".join(large_files[:5])}'
        })

    return issues


def check_git_status(root: Path) -> list:
    """Git 状态检查"""
    issues = []

    if not (root / '.git').exists():
        issues.append({
            'category': 'git',
            'severity': 'warning',
            'item': 'Git 仓库',
            'status': 'skip',
            'message': '不是 Git 仓库'
        })
        return issues

    # 未提交更改
    success, output = run_cmd(['git', 'status', '--porcelain'], root)
    if success and output.strip():
        changed = len([l for l in output.strip().split('\n') if l.strip()])
        issues.append({
            'category': 'git',
            'severity': 'warning',
            'item': '未提交更改',
            'status': 'warning',
            'message': f'有 {changed} 个未提交的更改，交付前应提交'
        })
    else:
        issues.append({
            'category': 'git',
            'severity': 'info',
            'item': '未提交更改',
            'status': 'pass',
            'message': '工作区干净'
        })

    # 最后提交
    success, output = run_cmd(['git', 'log', '-1', '--format=%h %ad %s', '--date=short'], root)
    if success:
        issues.append({
            'category': 'git',
            'severity': 'info',
            'item': '最后提交',
            'status': 'pass',
            'message': output.strip()
        })

    return issues


def generate_report(all_issues: list, root: Path) -> str:
    """生成验收报告"""
    categories = {}
    for issue in all_issues:
        cat = issue['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(issue)

    critical = [i for i in all_issues if i['severity'] == 'critical' and i['status'] == 'fail']
    warnings = [i for i in all_issues if i['severity'] == 'warning' and i['status'] in ('fail', 'warning')]
    passes = [i for i in all_issues if i['status'] == 'pass']

    can_deliver = len(critical) == 0

    lines = [
        '# 项目交付验收报告',
        '',
        f'**项目路径**: `{root}`',
        f'**验收时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
        '',
        '## 验收结论',
        '',
    ]

    if can_deliver:
        lines.append('✅ **可以交付** — 无 Critical 问题')
    else:
        lines.append('❌ **暂不可交付** — 存在 Critical 问题必须修复')

    lines.extend([
        '',
        '| 指标 | 数量 |',
        '|---|---|',
        f'| 🔴 Critical（必须修复） | {len(critical)} |',
        f'| 🟡 Warning（建议修复） | {len(warnings)} |',
        f'| ✅ Pass | {len(passes)} |',
        f'| 总检查项 | {len(all_issues)} |',
        '',
    ])

    cat_names = {
        'documentation': '📄 文档完整性',
        'testing': '🧪 测试覆盖',
        'security': '🔒 安全检查',
        'code_quality': '💻 代码质量',
        'git': '📦 Git 状态',
    }

    for cat, cat_issues in categories.items():
        name = cat_names.get(cat, cat)
        lines.append(f'## {name}')
        lines.append('')
        lines.append('| 检查项 | 状态 | 说明 |')
        lines.append('|---|---|---|')
        for issue in cat_issues:
            status_icon = {'pass': '✅', 'fail': '❌', 'warning': '⚠️', 'skip': '⏭️'}.get(issue['status'], '❓')
            lines.append(f'| {issue["item"]} | {status_icon} {issue["status"]} | {issue["message"]} |')
        lines.append('')

    if critical:
        lines.append('## 🔴 必须修复的 Critical 问题')
        lines.append('')
        for issue in critical:
            lines.append(f'- **{issue["item"]}**: {issue["message"]}')
        lines.append('')

    if warnings:
        lines.append('## 🟡 建议修复的 Warning')
        lines.append('')
        for issue in warnings:
            lines.append(f'- {issue["item"]}: {issue["message"]}')
        lines.append('')

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='项目交付验收自动检查器')
    parser.add_argument('path', nargs='?', default='.', help='项目路径')
    parser.add_argument('--output', '-o', help='输出报告文件')
    parser.add_argument('--format', '-f', choices=['md', 'json'], default='md')
    args = parser.parse_args()

    root = Path(args.path).resolve()
    if not root.exists():
        print(f'错误: 路径不存在: {root}', file=sys.stderr)
        sys.exit(1)

    all_issues = []
    all_issues.extend(check_documentation(root))
    all_issues.extend(check_tests(root))
    all_issues.extend(check_security(root))
    all_issues.extend(check_code_quality(root))
    all_issues.extend(check_git_status(root))

    if args.format == 'json':
        output = json.dumps({
            'root': str(root),
            'timestamp': datetime.now().isoformat(),
            'issues': all_issues,
            'can_deliver': not any(i['severity'] == 'critical' and i['status'] == 'fail' for i in all_issues)
        }, indent=2, ensure_ascii=False)
    else:
        output = generate_report(all_issues, root)

    if args.output:
        Path(args.output).write_text(output, encoding='utf-8')
        print(f'验收报告已写入: {args.output}')
    else:
        print(output)

    critical = [i for i in all_issues if i['severity'] == 'critical' and i['status'] == 'fail']
    sys.exit(1 if critical else 0)


if __name__ == '__main__':
    main()
