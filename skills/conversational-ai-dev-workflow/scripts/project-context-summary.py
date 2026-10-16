#!/usr/bin/env python3
"""
项目上下文摘要生成器
为对话式AI（豆包/Grok/ChatGPT）生成可直接粘贴的项目上下文摘要。
解决"每次开新对话都要重新交代背景"的痛点。

用法：
    python project-context-summary.py <项目目录>
    python project-context-summary.py <项目目录> --module <模块名>
    python project-context-summary.py <项目目录> --format text|json

输出：一段可直接粘贴到豆包/Grok 的项目上下文摘要
"""

import os
import sys
import json
import argparse
from pathlib import Path
from collections import defaultdict

# 配置文件 -> 技术栈映射
TECH_STACK_MAP = {
    'package.json': 'Node.js',
    'pnpm-lock.yaml': 'Node.js (pnpm)',
    'yarn.lock': 'Node.js (yarn)',
    'requirements.txt': 'Python',
    'pyproject.toml': 'Python',
    'Pipfile': 'Python (Pipenv)',
    'go.mod': 'Go',
    'Cargo.toml': 'Rust',
    'pom.xml': 'Java (Maven)',
    'build.gradle': 'Java (Gradle)',
    'composer.json': 'PHP',
    'Gemfile': 'Ruby',
    'mix.exs': 'Elixir',
    'vite.config': 'Vite',
    'webpack.config': 'Webpack',
    'next.config': 'Next.js',
    'nuxt.config': 'Nuxt.js',
    'tailwind.config': 'Tailwind CSS',
    'vue.config': 'Vue.js',
    'angular.json': 'Angular',
    'manifest.json': 'uni-app / PWA / Chrome Extension',
    'Dockerfile': 'Docker',
    'docker-compose.yml': 'Docker Compose',
    '.github/workflows': 'GitHub Actions',
}

# 代码文件扩展名
CODE_EXTENSIONS = {
    '.js', '.jsx', '.ts', '.tsx', '.vue', '.py', '.go', '.rs', '.java',
    '.php', '.rb', '.ex', '.exs', '.c', '.cpp', '.h', '.hpp', '.cs',
    '.swift', '.kt', '.dart', '.sql', '.sh', '.ps1', '.html', '.css', '.scss'
}

# 忽略的目录
IGNORE_DIRS = {
    'node_modules', '.git', '__pycache__', 'venv', '.venv', 'dist', 'build',
    'target', 'bin', 'obj', '.next', '.nuxt', 'vendor', '.idea', '.vscode',
    'coverage', '.tox', 'migrations', 'logs', 'tmp', 'temp'
}


def detect_tech_stack(project_path: Path) -> list:
    """检测项目技术栈"""
    stacks = []
    for config_file, stack in TECH_STACK_MAP.items():
        if (project_path / config_file).exists():
            if stack not in stacks:
                stacks.append(stack)
    # 检查子目录中的配置
    for item in project_path.iterdir():
        if item.is_dir() and item.name in TECH_STACK_MAP:
            stack = TECH_STACK_MAP[item.name]
            if stack not in stacks:
                stacks.append(stack)
    return stacks if stacks else ['未知（未检测到标准配置文件）']


def scan_directory(project_path: Path, max_depth: int = 3) -> dict:
    """扫描项目目录结构"""
    structure = defaultdict(list)
    file_count = 0
    code_lines = 0
    code_files = 0

    for root, dirs, files in os.walk(project_path):
        # 过滤忽略目录
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS and not d.startswith('.')]

        rel_root = Path(root).relative_to(project_path)
        depth = len(rel_root.parts)
        if depth > max_depth:
            dirs[:] = []
            continue

        for f in files:
            file_path = Path(root) / f
            ext = file_path.suffix.lower()
            if ext in CODE_EXTENSIONS:
                code_files += 1
                try:
                    code_lines += sum(1 for _ in open(file_path, 'r', encoding='utf-8', errors='ignore'))
                except:
                    pass
            file_count += 1
            if depth <= 2:
                structure[str(rel_root)].append(f)

    return {
        'structure': dict(structure),
        'total_files': file_count,
        'code_files': code_files,
        'code_lines': code_lines,
    }


def get_dir_tree(project_path: Path, max_depth: int = 2) -> str:
    """生成目录树（简化版）"""
    lines = []
    for root, dirs, files in os.walk(project_path):
        dirs[:] = sorted([d for d in dirs if d not in IGNORE_DIRS and not d.startswith('.')])
        rel_root = Path(root).relative_to(project_path)
        depth = len(rel_root.parts)
        if depth > max_depth:
            dirs[:] = []
            continue

        indent = '  ' * depth
        name = rel_root.name if rel_root.name else project_path.name
        lines.append(f"{indent}{name}/")

        if depth < max_depth:
            subindent = '  ' * (depth + 1)
            for f in sorted(files)[:10]:
                if not f.startswith('.'):
                    lines.append(f"{subindent}{f}")
            if len(files) > 10:
                lines.append(f"{subindent}... ({len(files)-10} more files)")

    return '\n'.join(lines)


def find_key_files(project_path: Path) -> list:
    """查找关键文件（README、配置、入口文件等）"""
    key_files = []
    key_patterns = ['README', 'readme', 'main.', 'index.', 'app.', 'server.', 'App.', 'vite.config', 'webpack.config']
    for root, dirs, files in os.walk(project_path):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for f in files:
            if any(p in f for p in key_patterns) and not f.startswith('.'):
                rel = str(Path(root, f).relative_to(project_path))
                if rel not in key_files and len(key_files) < 15:
                    key_files.append(rel)
    return key_files


def generate_summary(project_path: Path, module: str = None, fmt: str = 'text') -> str:
    """生成项目上下文摘要"""
    project_path = project_path.resolve()
    project_name = project_path.name

    tech_stack = detect_tech_stack(project_path)
    scan = scan_directory(project_path)
    dir_tree = get_dir_tree(project_path)
    key_files = find_key_files(project_path)

    if fmt == 'json':
        return json.dumps({
            'project_name': project_name,
            'tech_stack': tech_stack,
            'total_files': scan['total_files'],
            'code_files': scan['code_files'],
            'code_lines': scan['code_lines'],
            'key_files': key_files,
            'directory_tree': dir_tree,
        }, indent=2, ensure_ascii=False)

    # 文本格式（可直接粘贴到豆包/Grok）
    lines = []
    lines.append(f"【项目上下文摘要】")
    lines.append(f"项目名：{project_name}")
    lines.append(f"技术栈：{', '.join(tech_stack)}")
    lines.append(f"规模：{scan['code_files']} 个代码文件，约 {scan['code_lines']:,} 行代码")
    lines.append("")

    if module:
        lines.append(f"【当前模块】{module}")
        lines.append("")

    lines.append("【目录结构】")
    lines.append(dir_tree)
    lines.append("")

    lines.append("【关键文件】")
    for kf in key_files:
        lines.append(f"  - {kf}")
    lines.append("")

    lines.append("【使用说明】")
    lines.append("以上是项目当前状态摘要。开新对话时，将此摘要粘贴在对话开头，")
    lines.append("AI 就能快速了解项目背景，不需要你重新交代。")
    if module:
        lines.append(f"本次要开发/修改的模块是：{module}")

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='生成项目上下文摘要（为对话式AI准备）')
    parser.add_argument('project_dir', help='项目目录路径')
    parser.add_argument('--module', '-m', help='当前要开发的模块名', default=None)
    parser.add_argument('--format', '-f', choices=['text', 'json'], default='text', help='输出格式')
    parser.add_argument('--output', '-o', help='输出到文件（默认输出到终端）')

    args = parser.parse_args()

    project_path = Path(args.project_dir)
    if not project_path.exists():
        print(f"错误：目录不存在 - {project_path}", file=sys.stderr)
        sys.exit(1)
    if not project_path.is_dir():
        print(f"错误：不是目录 - {project_path}", file=sys.stderr)
        sys.exit(1)

    summary = generate_summary(project_path, args.module, args.format)

    if args.output:
        Path(args.output).write_text(summary, encoding='utf-8')
        print(f"摘要已保存到：{args.output}")
    else:
        print(summary)


if __name__ == '__main__':
    main()
