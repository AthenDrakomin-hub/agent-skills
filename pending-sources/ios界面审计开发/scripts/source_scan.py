#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iOS UI/UX 源码反模式静态扫描器
=================================
覆盖原生（Swift / Objective-C / Xib / Storyboard / Info.plist）与
H5（UniApp/Vue/CSS/HTML/JS）两套规则，规则编号与 references/ 下
audit-native-source.md / audit-h5-source.md / audit-ipa.md 一一对应。

用法：
  python source_scan.py <工程根目录> [--format text|md|json] [--out FILE]
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
# 常量与分类
# ---------------------------------------------------------------------------

SKIP_DIRS = {
    ".git", "node_modules", "Pods", "Carthage", "build", "dist", "unpackage",
    "DerivedData", ".idea", ".hbuilderx", ".gradle", "target", "out", "bin",
    "obj", "miniprogram_npm", ".svn", "www_temp",
}

KIND_MAP = {
    ".swift": "swift",
    ".m": "objc",
    ".mm": "objc",
    ".h": "objc",
    ".xib": "ib",
    ".storyboard": "ib",
    ".plist": "plist",
    ".html": "html",
    ".htm": "html",
    ".css": "css",
    ".scss": "css",
    ".sass": "css",
    ".less": "css",
    ".vue": "vue",
    ".nvue": "vue",
    ".js": "jscript",
    ".ts": "jscript",
    ".jsx": "jscript",
    ".tsx": "jscript",
}

# 会应用原生行规则的类型
NATIVE_KINDS = {"swift", "objc", "ib"}
# 会应用 H5 行规则的类型（vue 同时包含 style/template/script）
H5_LINE_KINDS = {"html", "css", "vue", "jscript"}
# 整块 CSS 规则（多行匹配）适用的类型
CSS_BLOCK_KINDS = {"css", "vue", "html"}
# 项目聚合统计的 CSS 类文件
CSS_AGG_KINDS = {"css", "vue", "scss", "less"}  # 注意 css kind 已含 scss/less

SEV_ORDER = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}

# 固定按钮类高度 <44 的行级正则（两个方向）
RE_TOUCH_NATIVE = [
    re.compile(r"(?is)(button|btn|tab|item|bar).{0,180}?(equalToConstant:?\s*|constant\s*=\s*|constraint\(equalToConstant:\s*)(2[0-9]|3[0-9]|4[0-3])\b"),
    re.compile(r"(?is)(equalToConstant:?\s*|constant\s*=\s*|constraint\(equalToConstant:\s*)(2[0-9]|3[0-9]|4[0-3])\b.{0,80}?(button|btn|tab|item|bar)"),
]
RE_TOUCH_H5 = [
    re.compile(r"(?is)([^{}]*?(?:btn|button|tab|icon|item)[^{}]*?)\{[^{}]*?height\s*:\s*(2[0-9]|3[0-9]|4[0-3])px[^{}]*?\}"),
]
RE_FONT_INPUT = [
    re.compile(r"(?is)(input|textarea|select|uni-input|u-input|van-field|contenteditable).{0,200}?font-size\s*:\s*((?:1[0-5]|[0-9])(?:\.\d+)?)px"),
    re.compile(r"(?is)font-size\s*:\s*((?:1[0-5]|[0-9])(?:\.\d+)?)px.{0,200}?(input|textarea|select|uni-input|u-input|van-field|contenteditable)"),
]
RE_CN_ASSIGN = re.compile(
    r"((?:\.text\s*=|setText:\s*|setTitle:\s*|\.title\s*=)\s*@?\"[^\"]*[\u4e00-\u9fff]"
    r"|(?:Text|Label)\s*\(\s*\"[^\"]*[\u4e00-\u9fff])"
)
RE_YYYY_IN_QUOTES = re.compile(r"""["'][^"']*Y{2,}[^"']*["']""")
RE_VH = re.compile(r"100vh")
RE_RTL = re.compile(r"""dir\s*=\s*["']rtl["']|direction\s*:\s*rtl|scaleX\(\s*-1|scale\(\s*-1\s*,\s*1""")
RE_OBSOLETE = re.compile(r"-webkit-overflow-scrolling\s*:\s*touch")
RE_USERSELECT_GLOBAL = re.compile(r"(?is)(html|body|\*)\s*[,{][^{}]*?user-select\s*:\s*none")
RE_FIXED_BOTTOM = re.compile(
    r"(?is)([^{}]*?)\{(?=[^{}]*position\s*:\s*fixed)"
    r"(?=[^{}]*bottom\s*:\s*(?:0|0px|0pt)\b)[^{}]*\}")
# 整块里有 backdrop-filter 但无 -webkit- 前缀（以块为单位）
RE_BACKDROP = re.compile(r"[^{}]*\{[^{}]*?(?<!-webkit-)backdrop-filter\s*:[^{}]*?\}")

# ---------------------------------------------------------------------------
# 规则定义
# ---------------------------------------------------------------------------

def rule(rid, title, severity, category, kinds, mode="line",
         patterns=None, doc="", hint=""):
    """构造一条规则。mode: line(逐行正则) / file(整文件存在性) / custom(回调)。"""
    return {
        "id": rid, "title": title, "severity": severity, "category": category,
        "kinds": set(kinds), "mode": mode,
        "patterns": [re.compile(p) for p in (patterns or [])],
        "doc": doc, "hint": hint,
    }

NATIVE_RULES = [
    rule("N-WEB-001", "仍在使用 UIWebView（App Store 拒审 P0）", "P0", "webview",
         ["swift", "objc", "ib"], "line",
         [r"\bUIWebView\b"], "audit-native-source.md §14",
         "UIWebView 已被 Apple 拒审，全面替换为 WKWebView（含三方 SDK 内残留）。"),
    rule("N-ADAPT-001", "按屏宽/机型常量做布局分支", "P2", "adapt",
         ["swift", "objc"], "line",
         [r"(?:UIScreen\.main|mainScreen).{0,100}?\b(320|375|390|393|402|414|428|430|440)\b"],
         "audit-native-source.md §2",
         "用尺寸类 traitCollection.horizontalSizeClass 或 Auto Layout，不按屏宽分支。"),
    rule("N-ADAPT-002", "硬编码 frame 常量布局", "P3", "adapt",
         ["swift", "objc"], "line",
         [r"CGRectMake\s*\(|\.frame\s*=\s*CGRect|CGRect\s*\(\s*x:"],
         "audit-native-source.md §2", "改 Auto Layout 约束布局。"),
    rule("N-SAFE-001", "使用已废弃的 topLayoutGuide/bottomLayoutGuide", "P1", "safearea",
         ["swift", "objc", "ib"], "line",
         [r"topLayoutGuide|bottomLayoutGuide"], "audit-native-source.md §3",
         "iOS 11 起换 safeAreaLayoutGuide。"),
    rule("N-SAFE-002", "contentInsetAdjustmentBehavior=.never 需人工确认补偿", "P2", "safearea",
         ["swift", "objc"], "line",
         [r"contentInsetAdjustmentBehavior\s*=\s*\.never|UIScrollViewContentInsetAdjustmentNever"],
         "audit-native-source.md §3",
         "设为 never 后必须自行用 safeAreaInsets 补偿，否则内容被栏/小黑条遮挡。"),
    rule("N-SAFE-003", "依赖 statusBarFrame 算布局", "P2", "safearea",
         ["swift", "objc"], "line",
         [r"statusBarFrame"], "audit-native-source.md §3",
         "灵动岛/热点状态栏下失效，改用 safeAreaLayoutGuide。"),
    rule("N-DEPRECATED-002", "使用废弃的 keyWindow / UIScreen.main API", "P3", "adapt",
         ["swift", "objc"], "line",
         [r"\bkeyWindow\b|UIScreen\.main\b"], "audit-native-source.md §2",
         "iOS 13/16 起改从 windowScene / 视图所在 window 获取。"),
    rule("N-COLOR-001", "硬编码 RGB 颜色，未提供深色变体", "P2", "darkmode",
         ["swift", "objc"], "line",
         [r"#colorLiteral|UIColor\s*\(\s*red:|colorWithRed:|colorWithWhite:|Color\s*\(\s*red:\s*[0-9.]+"],
         "audit-native-source.md §5",
         "用系统语义色、Asset Catalog 明暗两套，或 init(dynamicProvider:)。"),
    rule("N-DARK-001", "强制浅色模式 overrideUserInterfaceStyle=.light", "P1", "darkmode",
         ["swift", "objc", "ib"], "line",
         [r"overrideUserInterfaceStyle\s*=\s*\.light|UIUserInterfaceStyleLight"],
         "audit-native-source.md §5", "删除强制覆盖，跟随系统深色模式。"),
    rule("N-TYPE-001", "固定字号未接入 Dynamic Type", "P2", "typography",
         ["swift", "objc"], "line",
         [r"systemFont\s*\(\s*ofSize|boldSystemFont\s*\(\s*ofSize|systemFontOfSize:|italicSystemFontOfSize:"],
         "audit-native-source.md §4",
         "用 preferredFont(forTextStyle:)；自定义字体经 UIFontMetrics.scaledFont。"),
    rule("N-TYPE-002", "SwiftUI 固定 .font(.system(size:))", "P2", "typography",
         ["swift"], "line",
         [r"\.font\s*\(\s*\.system\s*\(\s*size:"], "audit-native-source.md §4/§13",
         "用 .body 等文本样式，或 @ScaledMetric 缩放自定义字号。"),
    rule("N-TOUCH-001", "按钮类控件约束高度 <44pt", "P2", "touch",
         ["swift", "objc"], "line", RE_TOUCH_NATIVE, "audit-native-source.md §6",
         "视觉可小，命中热区必须 ≥44pt，用 contentEdgeInsets/透明容器扩热区。"),
    rule("N-I18N-001", "界面文案写死中文，未走本地化", "P2", "i18n",
         ["swift", "objc"], "line", [RE_CN_ASSIGN], "audit-native-source.md §11",
         "用 NSLocalizedString / String(localized:)，文案进 Localizable.strings。"),
    rule("N-I18N-002", "日期格式使用大写 YYYY（周年日跨年 bug）", "P2", "i18n",
         ["swift", "objc", "jscript"], "line", [RE_YYYY_IN_QUOTES],
         "audit-native-source.md §11 / audit-h5-source.md §6",
         "改成小写 yyyy，并显式设置 locale/timeZone。"),
    rule("N-I18N-003", "写死左对齐/左右方向，RTL 不翻转", "P3", "i18n",
         ["swift", "objc"], "line",
         [r"NSTextAlignmentLeft|textAlignment\s*=\s*\.left|multilineTextAlignment\(\s*\.left"],
         "audit-native-source.md §11",
         "文本用 .natural；约束用 leadingAnchor/trailingAnchor。"),
    rule("N-DEPRECATED-001", "UI_USER_INTERFACE_IDIOM() 已废弃", "P2", "adapt",
         ["swift", "objc", "ib"], "line",
         [r"UI_USER_INTERFACE_IDIOM\s*\("], "audit-native-source.md §2",
         "换 UIDevice.current.userInterfaceIdiom。"),
]

# 文件级规则：(rule, 必需全部命中的正则, 对照正则, logic)
# logic="coexist"：必需命中 且 对照正则也全部命中才告警
# logic="missing"：必需命中 但 对照正则全部缺失才告警
NATIVE_FILE_RULES = [
    (rule("N-PERF-001", "cornerRadius + masksToBounds 可能触发离屏渲染", "P3", "performance",
          ["swift", "objc"], "file", doc="audit-native-source.md §8",
          hint="图片圆角优先预裁剪或用 maskedCorners+continuous；避免对滚动 cell 根层裁剪。"),
     [r"cornerRadius"], [r"masksToBounds|clipsToBounds"], "coexist"),
    (rule("N-PERF-002", "shouldRasterize 未配 rasterizationScale（Retina 下发糊）", "P2",
          "performance", ["swift", "objc"], "file",
          doc="audit-native-source.md §8",
          hint="补 layer.rasterizationScale = UIScreen.main.scale；动态内容不要光栅化。"),
     [r"shouldRasterize"], [r"rasterizationScale"], "missing"),
    (rule("N-PERF-003", "阴影未设 shadowPath，每帧离屏求 alpha", "P3", "performance",
          ["swift", "objc"], "file", doc="audit-native-source.md §8",
          hint="设 layer.shadowPath 为圆角矩形路径，或改用预渲染阴影图。"),
     [r"shadowOpacity|shadowColor|setShadowOpacity"], [r"shadowPath"], "missing"),
    (rule("N-A11Y-001", "文件内存在按钮但未发现 accessibilityLabel", "P3", "a11y",
          ["swift", "objc"], "file", doc="audit-native-source.md §6",
          hint="纯图标按钮必须补 accessibilityLabel 与 traits。"),
     [r"UIButton\s*\(|UIButton\.|buttonWithType"], [r"accessibilityLabel"], "missing"),
    (rule("N-GESTURE-001", "Label/ImageView 加手势但未开 isUserInteractionEnabled", "P3",
          "interaction", ["swift", "objc"], "file",
          doc="audit-native-source.md §7",
          hint="显式 isUserInteractionEnabled=true；可点元素优先用 UIButton。"),
     [r"UITapGestureRecognizer", r"UILabel|UIImageView"],
     [r"isUserInteractionEnabled"], "missing"),
]

# ---------------------------------------------------------------------------
# plist 规则
# ---------------------------------------------------------------------------

PLIST_USAGE_EMPTY = re.compile(
    r"<key>\s*(NS\w+UsageDescription)\s*</key>\s*(?:<string\s*/>|<string>\s*</string>)")
PLIST_TRUE_KEYS = {
    "N-CONFIG-001": ("NSAllowsArbitraryLoads", "P1", "config",
                     "ATS 全局放行 HTTP；仅对必要域名开例外或用 NSAllowsArbitraryLoadsInWebContent。"),
    "N-CONFIG-003": ("UIRequiresFullScreen", "P2", "config",
                     "关闭了 iPad 多任务；无硬理由应删除该键或设 false。"),
}
PLIST_STYLE_LIGHT = re.compile(
    r"<key>\s*UIUserInterfaceStyle\s*</key>\s*<string>\s*Light\s*</string>")
PLIST_LAUNCH_IMAGES = re.compile(r"<key>\s*UILaunchImages\s*</key>")
PLIST_DEVICE_FAMILY = re.compile(r"<key>\s*UIDeviceFamily\s*</key>\s*<array>(.*?)</array>", re.S)
PLIST_IPAD_ORI = re.compile(
    r"<key>\s*UISupportedInterfaceOrientations~ipad\s*</key>\s*<array>(.*?)</array>", re.S)

# ---------------------------------------------------------------------------
# 扫描逻辑
# classify / 收集聚合信息
# ---------------------------------------------------------------------------

class Scanner:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.findings = []
        # 项目级聚合
        self.has_css = False
        self.prefers_dark = 0
        self.reduced_motion = 0
        self.text_size_adjust = 0
        self.env_safe = 0
        self.viewport_cover = 0
        self.html_count = 0
        self.scanned = 0

    def add(self, r, rel, line, evidence):
        self.findings.append({
            "id": r["id"], "title": r["title"], "severity": r["severity"],
            "category": r["category"], "path": rel,
            "line": line or 0, "evidence": evidence.strip()[:200],
            "hint": r["hint"], "doc": r["doc"],
        })

    def add_raw(self, rid, title, severity, category, rel, line, evidence, hint, doc):
        self.findings.append({
            "id": rid, "title": title, "severity": severity, "category": category,
            "path": rel, "line": line or 0, "evidence": evidence.strip()[:200],
            "hint": hint, "doc": doc,
        })

    def scan(self):
        if not self.root.exists():
            raise FileNotFoundError(f"目录不存在：{self.root}")
        for path in self._walk():
            kind = self._kind(path)
            if kind is None:
                continue
            self.scanned += 1
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            rel = str(path.relative_to(self.root)).replace("\\", "/")
            if kind == "plist":
                self._scan_plist(text, rel)
            else:
                if kind in NATIVE_KINDS:
                    self._scan_native(text, rel, kind)
                if kind in H5_LINE_KINDS or kind == "vue":
                    self._scan_h5_lines(text, rel, kind)
                if kind in CSS_BLOCK_KINDS:
                    self._scan_css_blocks(text, rel, kind)
                if kind == "html":
                    self.html_count += 1
                    self._scan_html_head(text, rel)
                if kind in ("css", "vue"):
                    self.has_css = True
                    self.prefers_dark += text.count("prefers-color-scheme")
                    self.reduced_motion += text.count("prefers-reduced-motion")
                    self.text_size_adjust += text.count("-webkit-text-size-adjust")
                    if "safe-area-inset" in text:
                        self.env_safe += 1
                if kind == "jscript" and path.name in ("pages.json", "manifest.json"):
                    self._scan_uniapp_config(text, rel)
        self._project_findings()

    def _walk(self):
        for p in self.root.rglob("*"):
            if p.is_dir():
                continue
            if any(part in SKIP_DIRS for part in p.relative_to(self.root).parts):
                continue
            try:
                if p.stat().st_size > 1_500_000:
                    continue
            except OSError:
                continue
            yield p

    @staticmethod
    def _kind(path):
        name = path.name
        if name in ("pages.json", "manifest.json"):
            return "jscript"
        return KIND_MAP.get(path.suffix.lower())

    # -- 原生 --------------------------------------------------------------
    def _scan_native(self, text, rel, kind):
        lines = text.splitlines()
        for r in NATIVE_RULES:
            if kind not in r["kinds"]:
                continue
            if r["mode"] != "line":
                continue
            patterns = r["patterns"]
            for idx, line in enumerate(lines, 1):
                if any(p.search(line) for p in patterns):
                    self.add(r, rel, idx, line)
        # 文件级规则
        for r, required, counterpart, logic in NATIVE_FILE_RULES:
            if kind not in r["kinds"]:
                continue
            req_hits = [re.search(pat, text) for pat in required]
            if not all(req_hits):
                continue
            cp_hits = [re.search(pat, text) for pat in counterpart]
            if logic == "coexist":
                triggered = all(cp_hits)
            else:
                triggered = not any(cp_hits)
            if not triggered:
                continue
            evidence_lines = []
            for m in req_hits + cp_hits:
                if not m:
                    continue
                line_no = text[:m.start()].count("\n") + 1
                evidence_lines.append(f"L{line_no}: " +
                                      text.splitlines()[line_no - 1].strip()[:120])
            self.add(r, rel, 0, "；".join(dict.fromkeys(evidence_lines)))

    # -- plist -------------------------------------------------------------
    def _scan_plist(self, text, rel):
        for rid, (key, sev, cat, hint) in PLIST_TRUE_KEYS.items():
            pat = re.compile(r"<key>\s*%s\s*</key>\s*<true\s*/>" % re.escape(key))
            m = pat.search(text)
            if m:
                self.add_raw(rid, f"Info.plist {key}=true", sev, cat, rel,
                             text[:m.end()].count("\n") + 1,
                             f"<key>{key}</key><true/>", hint,
                             "audit-native-source.md §12 / audit-ipa.md §2")
        m = PLIST_STYLE_LIGHT.search(text)
        if m:
            self.add_raw("N-CONFIG-004", "Info.plist 强制 UIUserInterfaceStyle=Light",
                         "P2", "darkmode", rel, text[:m.start()].count("\n") + 1,
                         "UIUserInterfaceStyle = Light",
                         "删除该键以支持深色模式。", "audit-native-source.md §12")
        m = PLIST_LAUNCH_IMAGES.search(text)
        if m:
            self.add_raw("N-LAUNCH-001", "使用废弃的 UILaunchImages 静态启动图", "P1",
                         "launch", rel, text[:m.start()].count("\n") + 1,
                         "UILaunchImages",
                         "改用 LaunchScreen.storyboard 或 UILaunchScreen 字典。",
                         "audit-native-source.md §12")
        for m in PLIST_USAGE_EMPTY.finditer(text):
            self.add_raw("N-CONFIG-002", f"{m.group(1)} 文案为空", "P1", "config",
                         rel, text[:m.start()].count("\n") + 1, m.group(0),
                         "隐私授权文案为空会导致调用时崩溃/拒审，填写真实用途并本地化。",
                         "audit-native-source.md §12")
        # iPad 方向数量
        fam = PLIST_DEVICE_FAMILY.search(text)
        supports_ipad = bool(fam and re.search(r"<integer>\s*2\s*</integer>", fam.group(1)))
        ori = PLIST_IPAD_ORI.search(text)
        if supports_ipad and ori:
            count = len(re.findall(r"<string>\s*UIInterfaceOrientation", ori.group(1)))
            if 0 < count < 4:
                self.add_raw("N-CONFIG-005",
                             f"iPad 仅声明 {count} 个方向（应支持四个方向）", "P2",
                             "config", rel, text[:ori.start()].count("\n") + 1,
                             "UISupportedInterfaceOrientations~ipad",
                             "补齐两竖两横四个方向，否则 iPad 多任务被禁。",
                             "audit-native-source.md §12")

    # -- H5 行级 -----------------------------------------------------------
    def _scan_h5_lines(self, text, rel, kind):
        lines = text.splitlines()
        for idx, line in enumerate(lines, 1):
            if RE_RTL.search(line):
                self.add_raw("H-RTL-001", "RTL/镜像代码（确认是否误触发）", "P2", "i18n",
                             rel, idx, line,
                             "中文包必须 dir=ltr；scaleX(-1) 仅允许在 [dir=rtl] 条件下用于镜像图标。",
                             "audit-h5-source.md §1")
            if RE_VH.search(line) and "dvh" not in line:
                self.add_raw("H-VH-001", "使用 100vh（iOS 键盘/工具栏下偏大）", "P2",
                             "safearea", rel, idx, line,
                             "双写 min-height:100vh; min-height:100dvh; 或用 flex/visualViewport。",
                             "audit-h5-source.md §5")
            if RE_OBSOLETE.search(line):
                self.add_raw("H-OBSOLETE-001", "-webkit-overflow-scrolling 已废弃", "P3",
                             "performance", rel, idx, line,
                             "iOS 13+ 默认惯性滚动，删除该属性。", "audit-h5-source.md §6")
            if RE_USERSELECT_GLOBAL.search(line):
                self.add_raw("H-A11Y-001", "全局禁用文本选择", "P3", "a11y",
                             rel, idx, line,
                             "不要在 html/body/* 上 user-select:none；消息文本需可选择。",
                             "audit-h5-source.md §7")
            for p in RE_FONT_INPUT:
                m = p.search(line)
                if m:
                    self.add_raw("H-INPUT-001", "输入框字号 <16px（iOS 聚焦自动放大）",
                                 "P2", "typography", rel, idx, line,
                                 "input/textarea/select/uni 输入组件计算字号必须 ≥16px。",
                                 "audit-h5-source.md §3")
                    break

    @staticmethod
    def _line_of(text, pos):
        """把匹配位置换算成行号，跳过块开头的空白行。"""
        while pos < len(text) and text[pos] in " \t\r\n":
            pos += 1
        return text[:pos].count("\n") + 1

    # -- CSS 块级 ----------------------------------------------------------
    def _scan_css_blocks(self, text, rel, kind):
        # fixed + bottom:0 且文件无 safe-area-inset-bottom
        if "safe-area-inset-bottom" not in text:
            for m in RE_FIXED_BOTTOM.finditer(text):
                selector = m.group(1).strip().split("\n")[-1].strip()[:80]
                self.add_raw("H-SAFE-001", "position:fixed 底部元素未适配安全区", "P2",
                             "safearea", rel, text[:m.end(1)].count("\n") + 1,
                             f"{selector} {{ position:fixed; bottom:0 }}",
                             "加 padding-bottom:calc(env(safe-area-inset-bottom)+原间距)，并确认 viewport-fit=cover。",
                             "audit-h5-source.md §4")
        # backdrop-filter 缺 -webkit-
        for m in RE_BACKDROP.finditer(text):
            block = m.group(0)
            if "-webkit-backdrop-filter" not in block:
                self.add_raw("H-BLUR-001", "backdrop-filter 缺 -webkit- 前缀", "P2",
                             "visual", rel, self._line_of(text, m.start()),
                             block.replace("\n", " ")[:180],
                             "WKWebView 需要 -webkit-backdrop-filter，两个都写。",
                             "audit-h5-source.md §6")
        # 小尺寸按钮热区
        for m in RE_TOUCH_H5[0].finditer(text):
            selector = m.group(1).strip().split("\n")[-1].strip()[:80]
            val = m.group(2)
            self.add_raw("H-TOUCH-001", f"可点元素高度 {val}px（<44px 热区）", "P3",
                         "touch", rel, self._line_of(text, m.start(1)),
                         f"{selector} {{ height:{val}px }}",
                         "用 padding 撑命中盒到 ≥44px，视觉尺寸可以更小。",
                         "audit-h5-source.md §7")

    # -- HTML head ---------------------------------------------------------
    def _scan_html_head(self, text, rel):
        m = re.search(r'<meta[^>]+name=["\']viewport["\'][^>]*>', text, re.I)
        if not m:
            self.add_raw("H-VIEWPORT-001", "缺少 viewport meta", "P1", "adapt",
                         rel, 0, "<head> 中未发现 viewport",
                         "加 <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0, viewport-fit=cover\">。",
                         "audit-h5-source.md §2")
            return
        tag = m.group(0)
        if "viewport-fit=cover" not in tag:
            self.add_raw("H-VIEWPORT-001", "viewport 缺少 viewport-fit=cover", "P2",
                         "adapt", rel, text[:m.start()].count("\n") + 1, tag,
                         "补 viewport-fit=cover，否则 env(safe-area-inset-*) 恒为 0。",
                         "audit-h5-source.md §2")
            return
        self.viewport_cover += 1

    # -- UniApp 配置 -------------------------------------------------------
    def _scan_uniapp_config(self, text, rel):
        if Path(rel).name != "pages.json":
            return
        m = re.search(r'"tabBar"\s*:\s*\{([\s\S]{0,3000}?)\n\s{0,8}\}', text)
        if m and re.search(r'"custom"\s*:\s*true', m.group(1)):
            self.add_raw("H-UNI-001", "pages.json 启用 custom 自绘 tabBar", "P2",
                         "navigation", rel, text[:m.start()].count("\n") + 1,
                         '"tabBar": { "custom": true ...',
                         "自绘 tab 无法获得 iOS 26 悬浮液态玻璃栏，须自证安全区/键盘/滚动行为。",
                         "audit-h5-source.md §8")

    # -- 项目聚合 ----------------------------------------------------------
    def _project_findings(self):
        rel = "."
        if self.has_css and self.text_size_adjust == 0:
            self.add_raw("H-TYPE-001", "全局未设置 -webkit-text-size-adjust", "P3",
                         "typography", rel, 0, "项目样式中 0 处命中",
                         "全局 html { -webkit-text-size-adjust:100%; }。",
                         "audit-h5-source.md §3")
        if self.has_css and self.prefers_dark == 0:
            self.add_raw("H-DARK-001", "未发现 prefers-color-scheme 深色模式适配", "P3",
                         "darkmode", rel, 0, "项目样式中 0 处命中",
                         "提供 @media(prefers-color-scheme:dark) 变体；若产品明确不做需记录。",
                         "audit-h5-source.md §7")
        if self.has_css and self.reduced_motion == 0:
            self.add_raw("H-A11Y-002", "未适配 prefers-reduced-motion", "P3", "a11y",
                         rel, 0, "项目样式中 0 处命中",
                         "为动画提供减弱动效降级。", "audit-h5-source.md §7")
        if self.env_safe > 0 and self.viewport_cover == 0 and self.html_count > 0:
            self.add_raw("H-SAFE-002", "使用了 env(safe-area-inset-*) 但 HTML 未配 viewport-fit=cover",
                         "P2", "safearea", rel, 0,
                         f"env() 出现 {self.env_safe} 个文件，viewport-fit=cover 0 处",
                         "所有 HTML 入口 viewport 补 viewport-fit=cover，否则安全区变量恒为 0。",
                         "audit-h5-source.md §2/§4")


# ---------------------------------------------------------------------------
# 输出
# ---------------------------------------------------------------------------

def filter_findings(findings, min_sev):
    threshold = SEV_ORDER[min_sev]
    return [f for f in findings if SEV_ORDER[f["severity"]] <= threshold]


def render_text(findings, root, scanned):
    counts = {s: 0 for s in SEV_ORDER}
    for f in findings:
        counts[f["severity"]] += 1
    lines = [
        f"iOS UI/UX 源码扫描报告 · {root}",
        f"扫描文件数：{scanned}　P0={counts['P0']} P1={counts['P1']} "
        f"P2={counts['P2']} P3={counts['P3']}",
        "=" * 78,
    ]
    for f in sorted(findings, key=lambda x: (SEV_ORDER[x["severity"]], x["path"], x["line"])):
        loc = f"{f['path']}:{f['line']}" if f["line"] else f["path"]
        lines.append(f"[{f['severity']}] {f['id']} {f['title']}")
        lines.append(f"    位置：{loc}")
        lines.append(f"    证据：{f['evidence']}")
        lines.append(f"    修复：{f['hint']}")
        lines.append(f"    参考：references/{f['doc']}")
        lines.append("-" * 78)
    return "\n".join(lines)


def render_md(findings, root, scanned):
    counts = {s: 0 for s in SEV_ORDER}
    for f in findings:
        counts[f["severity"]] += 1
    out = [
        f"# iOS UI/UX 源码扫描报告 · `{root}`",
        "",
        f"扫描文件数：**{scanned}**　"
        f"P0 **{counts['P0']}** / P1 **{counts['P1']}** / "
        f"P2 **{counts['P2']}** / P3 **{counts['P3']}**",
        "",
        "| 级别 | ID | 位置 | 证据 | 修复指向 |",
        "| --- | --- | --- | --- | --- |",
    ]
    for f in sorted(findings, key=lambda x: (SEV_ORDER[x["severity"]], x["path"], x["line"])):
        loc = f"{f['path']}:{f['line']}" if f["line"] else f["path"]
        ev = f["evidence"].replace("|", "\\|").replace("\n", " ")[:120]
        hint = f["hint"].replace("|", "\\|").replace("\n", " ")[:120]
        out.append(f"| {f['severity']} | {f['id']} | `{loc}` | {ev} | {hint} |")
    out.append("")
    out.append("> 规则依据见 references/audit-native-source.md 与 audit-h5-source.md；"
               "评分与报告格式见 references/rubric.md。")
    return "\n".join(out)


def main(argv=None):
    parser = argparse.ArgumentParser(description="iOS UI/UX 源码反模式静态扫描器")
    parser.add_argument("root", help="工程根目录")
    parser.add_argument("--format", choices=["text", "md", "json"], default="text")
    parser.add_argument("--out", help="输出文件路径；不指定则打印到 stdout")
    parser.add_argument("--min-severity", choices=list(SEV_ORDER), default="P3",
                        help="只输出该级别及更严重的问题")
    parser.add_argument("--no-fail", action="store_true", help="即使有 P0/P1 也返回 0")
    args = parser.parse_args(argv)

    try:
        scanner = Scanner(args.root)
        scanner.scan()
    except (FileNotFoundError, OSError) as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 2

    findings = filter_findings(scanner.findings, args.min_severity)
    counts = {s: 0 for s in SEV_ORDER}
    for f in findings:
        counts[f["severity"]] += 1

    if args.format == "json":
        payload = {
            "root": str(scanner.root), "scanned_files": scanner.scanned,
            "counts": {k: counts[k] for k in ("P0", "P1", "P2", "P3")},
            "findings": findings,
        }
        report = json.dumps(payload, ensure_ascii=False, indent=2)
    elif args.format == "md":
        report = render_md(findings, scanner.root, scanner.scanned)
    else:
        report = render_text(findings, scanner.root, scanner.scanned)

    if args.out:
        Path(args.out).write_text(report, encoding="utf-8")
        print(f"报告已写入：{args.out}（P0={counts['P0']} P1={counts['P1']} "
              f"P2={counts['P2']} P3={counts['P3']}）")
    else:
        print(report)

    if not args.no_fail and (counts["P0"] or counts["P1"]):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
