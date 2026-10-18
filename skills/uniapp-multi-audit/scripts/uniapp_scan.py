#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uniapp 多端 UI/UX 静态扫描器
============================
扫描 uniapp 工程（.vue / .css / .scss / pages.json / manifest.json / uni.scss），
定位三端 UI/UX 与兼容性硬伤，规则与 references/ux-checklist.md、
references/compatibility-rules.md 一一对应。

用法：
  python uniapp_scan.py <工程根目录> [--format text|md|json] [--out FILE]
                              [--min-severity P0|P1|P2|P3] [--no-fail]

退出码：存在 P0/P1 问题时返回 1（CI 门禁），否则 0；--no-fail 恒为 0。
仅依赖 Python 3.8+ 标准库，Windows/macOS/Linux 可跑。
"""

import argparse
import json
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------

SKIP_DIRS = {
    ".git", "node_modules", "unpackage", "dist", "build", "components",
    ".hbuilderx", ".idea", ".vscode", "target", "out", "miniprogram_npm",
    "platforms", "plugins",
}

CODE_EXTS = {".vue", ".css", ".scss", ".sass", ".less", ".wxss", ".nvue"}
CONFIG_FILES = {"pages.json", "manifest.json", "uni.scss"}

SEV_ORDER = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
SEV_NAME = {0: "P0", 1: "P1", 2: "P2", 3: "P3"}

# ---------------------------------------------------------------------------
# 行级规则：(规则ID, 严重度, 类别, 描述, 编译正则)
# 编译正则匹配到即报一条，附行号。
# ---------------------------------------------------------------------------

LINE_RULES = [
    # UI 坑点
    ("U-100VH", 1, "H5兼容",
     "使用 100vh，H5 端浏览器地址栏伸缩会导致高度异常，建议用 100% / 动态计算",
     re.compile(r"100vh")),
    ("U-SAFE-HARDCODE", 1, "安全区",
     "硬编码安全区高度（如 44/34px），不同机型/灵动岛会失效，应用 env(safe-area-inset-*)",
     re.compile(r"(padding|margin|top|bottom)\s*:\s*\d{2}\s*px\s*;?")),
    ("U-INPUT-FONT", 1, "键盘输入",
     "输入框 font-size < 16px，iOS Safari/WKWebView 聚焦会自动放大页面",
     re.compile(r"input[^{]*\{[^}]*font-size\s*:\s*(?:1[0-5]|[0-9])px", re.S)),
    ("U-MIRROR", 0, "RTL/镜像",
     "出现 scaleX(-1) / scale(-1,1)，易在 WKWebView 造成文字镜像翻转",
     re.compile(r"scale[XY]?\s*\(\s*-?1")),
    ("U-TEXT-SIZE-ADJUST", 2, "字体",
     "未设置 -webkit-text-size-adjust，iOS 可能自动放大字体，建议显式控制",
     re.compile(r"-webkit-text-size-adjust")),  # 命中=已处理，见下方逻辑
    ("U-BACKDROP-FILTER", 2, "兼容性",
     "backdrop-filter 毛玻璃在 Android 低版本/旧 WebView 需降级",
     re.compile(r"backdrop-filter")),
    ("U-PX-MIX", 3, "单位",
     "样式中混用 px（uniapp 推荐 rpx 做响应式；仅 1px 边框例外）",
     re.compile(r"(?:padding|margin|width|height|font-size)\s*:\s*\d+(?:\.\d+)?px\b")),
]

# 已处理项：命中后降为提示（P3）或直接不报
OK_PATTERNS = {
    "U-TEXT-SIZE-ADJUST": re.compile(r"-webkit-text-size-adjust\s*:\s*100%"),
}


# ---------------------------------------------------------------------------
# 扫描逻辑
# ---------------------------------------------------------------------------

def iter_files(root: Path):
    """遍历工程文件，跳过忽略目录。"""
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        ext = path.suffix.lower()
        name = path.name
        if ext in CODE_EXTS or name in CONFIG_FILES:
            yield path


def scan_file(path: Path, root: Path):
    """单文件扫描，返回问题列表。"""
    issues = []
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:  # noqa: BLE001
        issues.append({
            "rule": "U-READ", "sev": 2, "cat": "读取",
            "file": str(path.relative_to(root)), "line": 0,
            "msg": f"文件读取失败：{e}",
        })
        return issues

    rel = str(path.relative_to(root))
    lines = text.splitlines()

    # 行级规则
    for lineno, line in enumerate(lines, start=1):
        for rule_id, sev, cat, desc, pat in LINE_RULES:
            if pat.search(line):
                # 已处理项降级
                if rule_id in OK_PATTERNS and OK_PATTERNS[rule_id].search(line):
                    continue
                # U-TEXT-SIZE-ADJUST 命中=已设置，反转为提醒“已设置，确认值为 100%”
                issues.append({
                    "rule": rule_id, "sev": sev, "cat": cat,
                    "file": rel, "line": lineno,
                    "msg": desc,
                })

    # #ifdef / #endif 闭合检查（仅 .vue/.nvue）
    if path.suffix.lower() in {".vue", ".nvue"}:
        ifdef_count = len(re.findall(r"#ifdef|#ifndef", text))
        endif_count = len(re.findall(r"#endif", text))
        if ifdef_count != endif_count:
            issues.append({
                "rule": "U-IFDEF", "sev": 1, "cat": "条件编译",
                "file": rel, "line": 0,
                "msg": f"#ifdef/#ifndef 出现 {ifdef_count} 处，但 #endif 仅 {endif_count} 处，存在未闭合的条件编译块",
            })

    # safe-area 适配检查（全站是否使用）
    # 该检查在汇总阶段做，这里只标记是否使用了 safe-area

    return issues, {"uses_safe_area": bool(re.search(r"safe-area-inset", text))}


def summarize_safe_area(root: Path, issues, all_use_safe):
    """全站安全区覆盖提示。"""
    vue_files = [p for p in root.rglob("*.vue") if not any(
        part in SKIP_DIRS for part in p.parts)]
    if vue_files and not all_use_safe:
        issues.append({
            "rule": "U-SAFE-MISS", "sev": 2, "cat": "安全区",
            "file": str(root), "line": 0,
            "msg": "工程内未检测到 safe-area-inset 适配代码，iPhone 刘海/灵动岛/Home 指示条可能被遮挡",
        })
    return issues


def filter_by_severity(issues, min_sev):
    threshold = SEV_ORDER[min_sev]
    return [i for i in issues if i["sev"] <= threshold]


# ---------------------------------------------------------------------------
# 输出
# ---------------------------------------------------------------------------

def render_md(issues, root, min_sev):
    issues = filter_by_severity(issues, min_sev)
    issues.sort(key=lambda i: (i["sev"], i["file"], i["line"]))
    lines = [
        f"# uniapp UI/UX 静态扫描报告",
        "",
        f"- 工程根目录：`{root}`",
        f"- 阈值：≥ {min_sev}",
        f"- 问题总数：{len(issues)}",
        "",
    ]
    counts = {0: 0, 1: 0, 2: 0, 3: 0}
    for i in issues:
        counts[i["sev"]] += 1
    lines.append(f"| P0 | P1 | P2 | P3 |")
    lines.append(f"|----|----|----|----|")
    lines.append(f"| {counts[0]} | {counts[1]} | {counts[2]} | {counts[3]} |")
    lines.append("")
    cur_sev = -1
    for i in issues:
        if i["sev"] != cur_sev:
            cur_sev = i["sev"]
            lines.append(f"## {SEV_NAME[i['sev']]}")
        loc = f"{i['file']}:{i['line']}" if i["line"] else i["file"]
        lines.append(f"- [{i['rule']}] {loc} — {i['msg']}")
    lines.append("")
    return "\n".join(lines)


def render_text(issues, root, min_sev):
    issues = filter_by_severity(issues, min_sev)
    issues.sort(key=lambda i: (i["sev"], i["file"], i["line"]))
    out = [f"uniapp UI/UX 扫描：{root}（阈值≥{min_sev}，共 {len(issues)} 条）"]
    for i in issues:
        loc = f"{i['file']}:{i['line']}" if i["line"] else i["file"]
        out.append(f"  {SEV_NAME[i['sev']]} [{i['rule']}] {loc} — {i['msg']}")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description="uniapp 多端 UI/UX 静态扫描器")
    ap.add_argument("root", help="工程根目录")
    ap.add_argument("--format", choices=["text", "md", "json"], default="md")
    ap.add_argument("--out", help="输出文件（默认 stdout）")
    ap.add_argument("--min-severity", choices=list(SEV_ORDER), default="P1")
    ap.add_argument("--no-fail", action="store_true", help="恒返回 0")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"错误：目录不存在 {root}", file=sys.stderr)
        sys.exit(1)

    all_issues = []
    any_safe = False
    for f in iter_files(root):
        result = scan_file(f, root)
        if isinstance(result, tuple):
            file_issues, meta = result
            all_issues.extend(file_issues)
            if meta.get("uses_safe_area"):
                any_safe = True
        else:
            all_issues.extend(result)

    all_issues = summarize_safe_area(root, all_issues, any_safe)

    if args.format == "json":
        text = json.dumps(filter_by_severity(all_issues, args.min_severity),
                          ensure_ascii=False, indent=2)
    elif args.format == "md":
        text = render_md(all_issues, root, args.min_severity)
    else:
        text = render_text(all_issues, root, args.min_severity)

    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"报告已写入：{args.out}")
    else:
        print(text)

    has_blocking = any(i["sev"] <= 1 for i in all_issues)
    sys.exit(0 if (args.no_fail or not has_blocking) else 1)


if __name__ == "__main__":
    main()
