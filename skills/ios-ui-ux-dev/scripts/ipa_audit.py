#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iOS IPA / .app 静态产物审计脚本
==================================
对 .ipa（本质 zip）或已解包的 .app 目录做静态分析，覆盖：
Info.plist 配置（启动屏/方向/ATS/隐私文案/深色模式/版本信息）、
图标与启动图（PNG IHDR/chunk 解析真实像素）、Assets.car、
Mach-O 架构与构建版本（纯 Python fat header + LC_BUILD_VERSION）、
UIWebView / 私有 API / 废弃符号字符串扫描（含内嵌 Frameworks）、
本地化 .lproj、资源体积、源码误打包、签名目录与描述文件。

用法：
  python ipa_audit.py <App.ipa|Payload/App.app> [--format text|md|json]
                      [--out FILE] [--min-severity P0..P3] [--no-fail]
                      [--keep] [--workdir DIR]

平台说明：纯标准库跨平台；macOS 且装了 Xcode 命令行工具时自动调用
xcrun assetutil（Assets.car 明细）与 security cms（描述文件）做深度核验。
规则编号与 references/audit-ipa.md 一致。

退出码：P0/P1 为 1，其余 0；--no-fail 恒 0。
"""

import argparse
import json
import plistlib
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

SEV_ORDER = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}

# ---- Mach-O 常量 -----------------------------------------------------------
FAT_MAGIC = 0xCAFEBABE
FAT64_MAGIC = 0xCAFEBABF
MH_MAGIC = 0xFEEDFACE
MH_MAGIC_64 = 0xFEEDFACF
LC_VERSION_MIN_IPHONEOS = 0x25
LC_ENCRYPTION_INFO = 0x2C
LC_ENCRYPTION_INFO_64 = 0x2D
LC_BUILD_VERSION = 0x32

CPU_MAP = {
    7: "x86",
    12: "arm",
    0x01000007: "x86_64",
    0x0100000C: "arm64",
}
PLATFORM_MAP = {
    1: "macOS", 2: "iOS", 3: "tvOS", 4: "watchOS", 5: "BridgeOS",
    6: "macCatalyst", 7: "iOS Simulator", 8: "tvOS Simulator",
    9: "watchOS Simulator", 10: "DriverKit",
}

PRIVATE_API_HINTS = [
    b"_UIBackdropView",
    b"UICalloutBarButton",
    b"UITextEffectsWindow",
]
DEPRECATED_SYMBOLS = [
    (b"UI_USER_INTERFACE_IDIOM", "I-DEPRECATED-001", "使用废弃的 UI_USER_INTERFACE_IDIOM()", "P3"),
]

DOC = "audit-ipa.md"

# 预期 loose 图标尺寸（Asset Catalog 法无需，见 audit-ipa.md §3）
IPHONE_ICON_PX = {40, 58, 60, 80, 87, 120, 180}
IPAD_ICON_PX = {20, 29, 40, 76, 152, 167}


def vstr(v):
    return f"{(v >> 16) & 0xFFFF}.{(v >> 8) & 0xFF}.{v & 0xFF}"


def png_size(data):
    """按 chunk 遍历解析 PNG 宽高（兼容带 CgBI 私有 chunk 的苹果优化 PNG）。"""
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    off = 8
    while off + 12 <= len(data):
        length = int.from_bytes(data[off:off + 4], "big")
        ctype = data[off + 4:off + 8]
        if ctype == b"IHDR":
            width = int.from_bytes(data[off + 8:off + 12], "big")
            height = int.from_bytes(data[off + 12:off + 16], "big")
            return width, height
        off += 12 + length + 4
    return None


def parse_macho(data):
    """返回 [{'arch','platform','minos','encrypted'}]；无法完整解析时返回 []。"""
    if len(data) < 32:
        return []
    be = int.from_bytes(data[:4], "big")
    le = int.from_bytes(data[:4], "little")
    slices = []
    if be in (FAT_MAGIC, FAT64_MAGIC):
        nfat = int.from_bytes(data[4:8], "big")
        if nfat > 16 or 8 + nfat * 32 > len(data):
            return []
        off = 8
        for _ in range(nfat):
            if be == FAT64_MAGIC:
                cputype = int.from_bytes(data[off:off + 4], "big")
                cpusub = int.from_bytes(data[off + 4:off + 8], "big")
                soff = int.from_bytes(data[off + 8:off + 16], "big")
                ssize = int.from_bytes(data[off + 16:off + 24], "big")
                off += 32
            else:
                cputype = int.from_bytes(data[off:off + 4], "big")
                cpusub = int.from_bytes(data[off + 4:off + 8], "big")
                soff = int.from_bytes(data[off + 8:off + 12], "big")
                ssize = int.from_bytes(data[off + 12:off + 16], "big")
                off += 20
            slices.append((soff, ssize, cputype, cpusub))
    elif le in (MH_MAGIC, MH_MAGIC_64) or be in (MH_MAGIC, MH_MAGIC_64):
        slices.append((0, len(data), int.from_bytes(data[4:8], "little"),
                       int.from_bytes(data[8:12], "little")))
    else:
        return []

    results = []
    for soff, ssize, cputype, cpusub in slices:
        blob = data[soff:soff + ssize]
        if len(blob) < 28:
            continue
        magic = int.from_bytes(blob[:4], "little")
        is64 = magic == MH_MAGIC_64
        ncmds = int.from_bytes(blob[16:20], "little")
        sizeofcmds = int.from_bytes(blob[20:24], "little")
        header = 32 if is64 else 28
        p = header
        platform, minos, encrypted = None, None, False
        for _ in range(min(ncmds, 256)):
            if p + 8 > len(blob) or p > header + sizeofcmds:
                break
            cmd = int.from_bytes(blob[p:p + 4], "little")
            cmdsize = int.from_bytes(blob[p + 4:p + 8], "little")
            if cmdsize <= 0 or p + cmdsize > len(blob):
                break
            if cmd == LC_BUILD_VERSION and cmdsize >= 24:
                pv = int.from_bytes(blob[p + 8:p + 12], "little")
                platform = PLATFORM_MAP.get(pv, str(pv))
                minos = vstr(int.from_bytes(blob[p + 12:p + 16], "little"))
            elif cmd == LC_VERSION_MIN_IPHONEOS and cmdsize >= 16:
                platform = "iOS"
                minos = vstr(int.from_bytes(blob[p + 8:p + 12], "little"))
            elif cmd in (LC_ENCRYPTION_INFO, LC_ENCRYPTION_INFO_64) and cmdsize >= 20:
                encrypted = int.from_bytes(blob[p + 16:p + 20], "little") != 0
            p += cmdsize
        arch = CPU_MAP.get(cputype, hex(cputype))
        if arch == "arm64" and (cpusub & 0x00FFFFFF) == 2:
            arch = "arm64e"
        results.append({"arch": arch, "platform": platform, "minos": minos,
                        "encrypted": encrypted})
    return results


class IpaAuditor:
    def __init__(self):
        self.findings = []
        self.inventory = {}
        self.manual_checks = []

    def add(self, rid, title, severity, category, evidence, hint,
            path="-", line=0):
        self.findings.append({
            "id": rid, "title": title, "severity": severity,
            "category": category, "path": path, "line": line,
            "evidence": str(evidence)[:240], "hint": hint, "doc": DOC,
        })

    def audit(self, target, workdir=None, keep=False):
        target = Path(target)
        if not target.exists():
            raise FileNotFoundError(f"输入不存在：{target}")
        cleanup = None
        if target.is_file() and target.suffix.lower() == ".ipa":
            if workdir:
                # 用户指定目录不自动删除，避免误删既有文件
                app_dir = self._extract(str(target), Path(workdir))
            else:
                extract_root = Path(tempfile.mkdtemp(prefix="ipa_audit_"))
                app_dir = self._extract(str(target), extract_root)
                if not keep:
                    cleanup = extract_root
        elif target.is_dir():
            if target.name.endswith(".app"):
                app_dir = target
            else:
                found = list(target.glob("Payload/*.app"))
                if found:
                    app_dir = found[0]
                else:
                    found = list(target.rglob("*.app"))
                    if not found:
                        raise FileNotFoundError("未找到 Payload/*.app 或 .app 目录")
                    app_dir = found[0]
        else:
            raise ValueError("输入必须是 .ipa 文件或 .app / 含 Payload 的目录")

        try:
            self._audit_app(app_dir)
        finally:
            if cleanup is not None and not keep:
                shutil.rmtree(cleanup, ignore_errors=True)

    @staticmethod
    def _extract(ipa_path, workdir):
        workdir.mkdir(parents=True, exist_ok=True)
        try:
            zf = zipfile.ZipFile(ipa_path)
        except zipfile.BadZipFile:
            raise ValueError(f"{ipa_path} 不是有效的 IPA（zip）文件")
        with zf:
            # Python 3.6+ 的 extractall 会拒绝路径逃逸（zip-slip）
            zf.extractall(workdir)
        apps = list(workdir.glob("Payload/*.app"))
        if not apps:
            raise FileNotFoundError("ipa 内未找到 Payload/*.app")
        return apps[0]

    # ------------------------------------------------------------------ core
    def _audit_app(self, app_dir: Path):
        app_dir = app_dir.resolve()
        plist_path = app_dir / "Info.plist"
        if not plist_path.exists():
            raise FileNotFoundError(f".app 内缺少 Info.plist：{plist_path}")
        try:
            plist = plistlib.loads(plist_path.read_bytes())
        except (plistlib.InvalidFileException, ValueError) as exc:
            raise ValueError(f"Info.plist 解析失败：{exc}")

        self.inventory["app_name"] = app_dir.name
        self.inventory["bundle_id"] = plist.get("CFBundleIdentifier", "-")
        self.inventory["version"] = plist.get("CFBundleShortVersionString", "-")
        self.inventory["build"] = plist.get("CFBundleVersion", "-")
        self.inventory["min_os_plist"] = plist.get("MinimumOSVersion", "-")
        self.inventory["device_family"] = plist.get("UIDeviceFamily", [])
        self.inventory["orientations_iphone"] = plist.get(
            "UISupportedInterfaceOrientations", [])
        self.inventory["orientations_ipad"] = plist.get(
            "UISupportedInterfaceOrientations~ipad", [])
        self.inventory["privacy_keys"] = sorted(
            k for k in plist if k.endswith("UsageDescription"))
        self.inventory["user_interface_style"] = plist.get("UIUserInterfaceStyle", "-")
        self.inventory["requires_full_screen"] = plist.get(
            "UIRequiresFullScreen", False)

        self._check_launch(plist, app_dir)
        self._check_orientations(plist)
        self._check_ats(plist)
        self._check_privacy(plist)
        self._check_dark(plist)
        self._check_basic_keys(plist)
        self._check_icons(plist, app_dir)
        binary_info = self._check_binary(plist, app_dir)
        self.inventory["binary"] = binary_info
        self._check_localizations(app_dir)
        self._check_size_and_resources(app_dir)
        self._check_signing(plist, app_dir)
        self._check_h5_bundle(app_dir)

    def _check_launch(self, plist, app_dir):
        has_storyboard = bool(plist.get("UILaunchStoryboardName")) or \
            bool(plist.get("UILaunchScreen"))
        legacy_images = "UILaunchImages" in plist or any(
            app_dir.glob("LaunchImage*.png"))
        if legacy_images:
            self.add("I-LAUNCH-002", "使用废弃静态启动图 UILaunchImages/LaunchImage",
                     "P1", "launch",
                     "UILaunchImages 或 LaunchImage*.png",
                     "改用 LaunchScreen.storyboard 或 UILaunchScreen 字典，否则新机型黑边/兼容模式。")
        if not has_storyboard and not legacy_images:
            self.add("I-LAUNCH-001", "缺少现代启动屏配置", "P1", "launch",
                     "无 UILaunchStoryboardName / UILaunchScreen / UILaunchImages",
                     "添加 LaunchScreen.storyboard 并在 plist 配置，否则 App 以兼容分辨率运行。")
        self.inventory["launch"] = "storyboard" if has_storyboard else (
            "legacy-images" if legacy_images else "MISSING")

    def _check_orientations(self, plist):
        family = plist.get("UIDeviceFamily", [])
        is_ipad = 2 in family
        self.inventory["is_ipad"] = is_ipad
        if not is_ipad:
            return
        ipad = plist.get("UISupportedInterfaceOrientations~ipad")
        if ipad is not None and 0 < len(ipad) < 4:
            self.add("I-ORIENT-001",
                     f"iPad 仅声明 {len(ipad)} 个方向（应支持四个方向）", "P2",
                     "config", str(ipad),
                     "补齐两竖两横；不足会禁用 iPad 多任务并带来审核风险。")
        if plist.get("UIRequiresFullScreen", False):
            self.add("I-IPAD-001", "UIRequiresFullScreen=true 禁用 iPad 多任务",
                     "P2", "config", "UIRequiresFullScreen",
                     "无硬理由删除该键（默认 false），支持 Slide Over / Split View。")

    def _check_ats(self, plist):
        ats = plist.get("NSAppTransportSecurity")
        if isinstance(ats, dict):
            if ats.get("NSAllowsArbitraryLoads"):
                self.add("I-ATS-001", "ATS 全局放行明文 HTTP", "P1", "config",
                         "NSAllowsArbitraryLoads=true",
                         "改为按域名 Exception Domains；纯 WebView 场景用 "
                         "NSAllowsArbitraryLoadsInWebContent。")
            if ats.get("NSAllowsArbitraryLoadsInWebContent"):
                self.add("I-ATS-002", "WebView 内容放行明文 HTTP（可接受，需确认）",
                         "P3", "config", "NSAllowsArbitraryLoadsInWebContent=true",
                         "确认仅 WebView 流量放行，原生 API 仍走 HTTPS。")

    def _check_privacy(self, plist):
        for key in sorted(k for k in plist if k.endswith("UsageDescription")):
            value = plist.get(key)
            if not isinstance(value, str) or not value.strip():
                self.add("I-PRIV-001", f"{key} 文案为空", "P1", "config",
                         f"{key} = {value!r}",
                         "隐私授权文案为空会导致调用时崩溃并可能拒审，填写真实用途并本地化。")
        self.manual_checks.append(
            "对照代码/二进制确认所用隐私 API（相机/相册/麦克风/定位/通讯录/通知/追踪）"
            "都有对应 NS*UsageDescription，且 .lproj/InfoPlist.strings 有翻译。")

    def _check_dark(self, plist):
        if plist.get("UIUserInterfaceStyle") == "Light":
            self.add("I-DARK-001", "Info.plist 强制浅色模式", "P2", "darkmode",
                     "UIUserInterfaceStyle=Light",
                     "删除该键以支持深色模式（与 N-DARK-001 同源）。")

    def _check_basic_keys(self, plist):
        if not plist.get("CFBundleShortVersionString") or not plist.get("CFBundleVersion"):
            self.add("I-KEY-001", "缺少 CFBundleShortVersionString/CFBundleVersion",
                     "P2", "config", "版本键缺失", "补齐展示版本号与构建号。")
        caps = plist.get("UIRequiredDeviceCapabilities", [])
        if isinstance(caps, dict):
            caps = list(caps.keys())
        if "arm64" not in caps:
            self.add("I-CAP-001", "UIRequiredDeviceCapabilities 未声明 arm64",
                     "P3", "config", f"UIRequiredDeviceCapabilities={caps}",
                     "加入 arm64，避免错误设备安装。")
        if "ITSAppUsesNonExemptEncryption" not in plist:
            self.add("I-REL-001", "未声明 ITSAppUsesNonExemptEncryption", "P3",
                     "release", "键缺失",
                     "仅用 HTTPS 的 App 可设 false，避免每次提审弹加密合规问卷。")
        min_os = str(plist.get("MinimumOSVersion", ""))
        try:
            if int(min_os.split(".")[0]) < 13:
                self.add("I-OS-001", f"MinimumOSVersion={min_os} 过低", "P3",
                         "release", f"MinimumOSVersion={min_os}",
                         "建议最低 iOS 13+ 以使用安全区/深色模式/Dynamic Type 原生能力。")
        except ValueError:
            pass

    def _check_icons(self, plist, app_dir):
        car = app_dir / "Assets.car"
        loose = []
        for png in app_dir.glob("*.png"):
            try:
                size = png_size(png.read_bytes()[:4096])
            except OSError:
                size = None
            loose.append({"name": png.name, "size": size})
        icon_files = [p for p in loose
                      if "AppIcon" in p["name"] or "Icon" in p["name"]]
        declared = plist.get("CFBundleIconFiles") or []
        cficons = plist.get("CFBundleIcons", {})
        if isinstance(cficons, dict):
            declared += cficons.get("CFBundlePrimaryIcon", {}).get(
                "CFBundleIconFiles", []) or []
        self.inventory["assets_car"] = car.exists()
        self.inventory["loose_png_count"] = len(loose)
        self.inventory["icon_loose"] = icon_files
        self.inventory["declared_icon_files"] = declared

        if not car.exists() and not icon_files and not declared:
            self.add("I-ICON-001", "未发现 App 图标（无 Assets.car / AppIcon 图片 / 声明）",
                     "P1", "icon", "根目录无图标资源",
                     "在 Asset Catalog 提供 1024 图标（Xcode 自动生成各尺寸），"
                     "iOS 26 还需浅色/深色/着色外观。")
            return
        if car.exists() and sys.platform != "darwin":
            self.manual_checks.append(
                "macOS 执行：xcrun --sdk iphoneos assetutil --info "
                f"\"Payload/{app_dir.name}/Assets.car\" "
                "→ 核对 AppIcon 尺寸（120/180，iPad 76/152/167）、@2x/@3x 完整性、"
                "深色外观与超大图内存。")
        if car.exists() and sys.platform == "darwin":
            self._assetutil(app_dir, car)

    def _assetutil(self, app_dir, car):
        xcrun = shutil.which("xcrun")
        if not xcrun:
            return
        try:
            out = subprocess.run(
                [xcrun, "--sdk", "iphoneos", "assetutil", "--info", str(car)],
                capture_output=True, text=True, timeout=60)
            if out.returncode != 0:
                self.manual_checks.append("assetutil 执行失败：" + out.stderr[:200])
                return
            data = json.loads(out.stdout)
        except (subprocess.TimeoutExpired, json.JSONDecodeError, OSError) as exc:
            self.manual_checks.append(f"assetutil 解析失败：{exc}")
            return
        icon_sizes, scales, total, big = set(), set(), 0, []
        for item in data:
            if not isinstance(item, dict):
                continue
            w, h = item.get("PixelWidth"), item.get("PixelHeight")
            if w and h:
                total += 1
                if max(w, h) >= 3000:
                    big.append(f"{item.get('Name', '?')} {w}x{h}")
            scale = item.get("Scale")
            if scale:
                scales.add(str(scale))
            name = str(item.get("Name", "")) + str(item.get("Rendition Name", ""))
            if "AppIcon" in name and w and h:
                icon_sizes.add(int(w))
        self.inventory["car_assets"] = total
        self.inventory["car_scales"] = sorted(scales)
        self.inventory["car_icon_px"] = sorted(icon_sizes)
        self.inventory["car_oversized"] = big[:20]
        expected = {60, 80, 120, 180}
        if self.inventory.get("is_ipad"):
            expected |= {76, 152, 167}
        if total and not icon_sizes:
            self.add("I-ICON-002", "Assets.car 中未找到 AppIcon 条目", "P1", "icon",
                     "assetutil 输出无 AppIcon", "检查 AppIcon 资源集的 target 归属与配置。")
        elif icon_sizes and not expected.issubset(icon_sizes):
            missing = sorted(expected - icon_sizes)
            self.add("I-ICON-003", f"Assets.car AppIcon 缺尺寸：{missing}", "P2",
                     "icon", f"现有尺寸：{sorted(icon_sizes)}",
                     "补齐图标 slot，或改用单一 1024 图标由 Xcode 生成。")
        if big:
            self.add("I-SIZE-003", f"Assets.car 中 {len(big)} 个超大全图（≥3000px）",
                     "P3", "asset", "；".join(big[:5]),
                     "按显示尺寸出图，降低解码内存峰值。")

    def _check_binary(self, plist, app_dir):
        exec_name = plist.get("CFBundleExecutable")
        binaries = []
        if exec_name and (app_dir / exec_name).exists():
            binaries.append(app_dir / exec_name)
        fw_dir = app_dir / "Frameworks"
        if fw_dir.exists():
            for fw in fw_dir.glob("*.framework"):
                name = fw.stem
                binp = fw / name
                if binp.exists():
                    binaries.append(binp)
            binaries.extend(fw_dir.glob("*.dylib"))
        info = {"main": str(exec_name), "frameworks": [], "slices": [],
                "webview": None}
        has_arm64, has_x86, minos_list, encrypted = False, False, [], False
        for binp in binaries:
            try:
                data = binp.read_bytes()
            except OSError:
                continue
            rel = str(binp.relative_to(app_dir)).replace("\\", "/")
            slices = parse_macho(data)
            if binp.parent == app_dir:
                info["slices"] = slices
            else:
                info["frameworks"].append({"name": rel, "slices": slices})
            for s in slices:
                if s["arch"] in ("arm64", "arm64e"):
                    has_arm64 = True
                if "x86" in s["arch"] or (s.get("platform") or "").endswith("Simulator"):
                    has_x86 = True
                if s["minos"]:
                    minos_list.append((rel, s["minos"]))
                if s["encrypted"]:
                    encrypted = True
            if b"UIWebView" in data:
                self.add("I-WEB-001", f"{rel} 中检测到 UIWebView", "P0",
                         "webview", "二进制包含字符串 UIWebView",
                         "App Store 拒审项：替换为 WKWebView；三方 SDK 残留需升级 SDK。",
                         path=rel)
            for priv in PRIVATE_API_HINTS:
                if priv in data:
                    self.add("I-PRIVATE-001",
                             f"{rel} 命中疑似私有 API {priv.decode()}", "P2",
                             "release", priv.decode(),
                             "需人工复核（可能是系统字符串误报），确认未直接调用私有 API。",
                             path=rel)
            for sym, rid, title, sev in DEPRECATED_SYMBOLS:
                if sym in data:
                    self.add(rid, f"{rel} {title}", sev, "adapt", sym.decode(),
                             "换 UIDevice.current.userInterfaceIdiom。", path=rel)
        if binaries and not has_arm64:
            self.add("I-ARCH-001", "主二进制/框架缺少 arm64 设备架构", "P0",
                     "release", str([s["arch"] for s in info["slices"]]),
                     "真机与 App Store 要求 arm64，检查 Architectures/Excluded Archs。")
        if has_x86:
            self.add("I-ARCH-002", "设备包中包含 x86/模拟器架构", "P1", "release",
                     "检测到 x86_64 或 Simulator platform slice",
                     "打包流程错误；模拟器产物只能存在于 .xcframework，不能进 App 包。")
        for rel, mv in minos_list:
            try:
                major = int(mv.split(".")[0])
            except (ValueError, IndexError):
                continue
            if major < 13 and rel == str(exec_name):
                self.add("I-OS-001", f"最低系统版本 iOS {mv} 过低", "P3", "release",
                         f"LC_BUILD_VERSION minos={mv}",
                         "建议最低 iOS 13+ 以使用安全区/深色模式/Dynamic Type 原生能力。")
                break
        info["encrypted"] = encrypted
        if encrypted:
            self.manual_checks.append(
                "二进制 FairPlay 已加密（App Store 分发版），字符串扫描覆盖率下降；"
                "UIWebView/私有 API 请用 Archive 导出的未加密 AdHoc 包复核。")
        if not binaries:
            self.add("I-ARCH-001", "未找到 CFBundleExecutable 主二进制", "P0",
                     "release", f"CFBundleExecutable={exec_name}",
                     "确认包体完整或重新导出 IPA。")
        info["webview"] = "WKWebView"  # 占位，实际在字符串层统计
        return info

    def _check_localizations(self, app_dir):
        lprojs = sorted(p.name for p in app_dir.glob("*.lproj"))
        self.inventory["lproj"] = lprojs
        if len(lprojs) <= 1:
            self.add("I-LOC-001", f"仅 {len(lprojs)} 个语言包（{lprojs}）", "P3",
                     "i18n", f".lproj={lprojs}",
                     "若计划多语言需补 Localizable.strings/InfoPlist.strings；"
                     "单语言产品可忽略并记录。")

    def _check_size_and_resources(self, app_dir):
        files = [p for p in app_dir.rglob("*") if p.is_file()]
        total = 0
        large = []
        loose_png = {}
        shipped_source = []
        for p in files:
            try:
                size = p.stat().st_size
            except OSError:
                continue
            total += size
            rel = str(p.relative_to(app_dir)).replace("\\", "/")
            if size > 10 * 1024 * 1024:
                large.append((rel, size))
            if p.suffix.lower() == ".png" and p.parent == app_dir:
                stem = re.sub(r"@[23]x$", "", p.stem)
                loose_png.setdefault(stem, set()).add(
                    "@3x" if p.stem.endswith("@3x") else
                    "@2x" if p.stem.endswith("@2x") else "@1x")
            if p.suffix.lower() in (".h", ".m", ".mm", ".xib", ".md", ".map"):
                shipped_source.append(rel)
        self.inventory["size_mb"] = round(total / 1024 / 1024, 1)
        self.inventory["file_count"] = len(files)
        self.inventory["largest_files"] = [
            {"path": p, "mb": round(s / 1024 / 1024, 2)}
            for p, s in sorted(large, key=lambda x: -x[1])[:15]]
        if total > 200 * 1024 * 1024:
            self.add("I-SIZE-001", f"解包体积 {self.inventory['size_mb']}MB（>200MB）",
                     "P2", "asset", f"{self.inventory['size_mb']}MB / {len(files)} 文件",
                     "压缩资源、引导视频走云端/ODR，降低下载与首启解压压力。")
        for rel, size in sorted(large, key=lambda x: -x[1])[:8]:
            self.add("I-SIZE-002", f"单资源超过 10MB：{rel}", "P3", "asset",
                     f"{round(size/1024/1024, 2)}MB",
                     "视频/音频转 H.265/AAC 或按需下载。", path=rel)
        missing_3x = [stem for stem, scales in loose_png.items()
                      if "@2x" in scales and "@3x" not in scales]
        if missing_3x:
            self.add("I-ASSET-001",
                     f"{len(missing_3x)} 组 loose PNG 有 @2x 无 @3x", "P3", "asset",
                     "；".join(missing_3x[:8]),
                     "@3x 机型会缩放发糊；优先迁入 Asset Catalog 管理。")
        if shipped_source:
            self.add("I-RES-001", f"{len(shipped_source)} 个源码/开发文件被打入包体",
                     "P3", "release", "；".join(shipped_source[:8]),
                     "检查 Build Phases/Copy Bundle Resources，移除 .h/.m/.xib/.md/.map。")

    def _check_signing(self, plist, app_dir):
        sig = app_dir / "_CodeSignature"
        prov = app_dir / "embedded.mobileprovision"
        self.inventory["code_signature"] = sig.exists()
        self.inventory["mobileprovision"] = prov.exists()
        if not sig.exists():
            self.add("I-SIGN-001", "缺少 _CodeSignature（未签名/砸壳/打包异常）",
                     "P1", "sign", "_CodeSignature 不存在",
                     "正式分发必须签名；若为分析对象请确认来源可信。")
        if prov.exists() and sys.platform == "darwin":
            self._decode_provision(prov)
        elif prov.exists():
            self.manual_checks.append(
                f'macOS 执行：security cms -D -i "{prov}" > p.plist && '
                "plutil -p p.plist | grep -E 'ExpirationDate|TeamIdentifier' 核验有效期。")

    def _decode_provision(self, prov):
        security = shutil.which("security")
        if not security:
            return
        try:
            out = subprocess.run(
                [security, "cms", "-D", "-i", str(prov)],
                capture_output=True, timeout=30)
            pl = plistlib.loads(out.stdout)
        except (subprocess.TimeoutExpired, plistlib.InvalidFileException,
                ValueError, OSError):
            return
        self.inventory["provision_team"] = pl.get("TeamIdentifier")
        self.inventory["provision_expires"] = str(pl.get("ExpirationDate", "-"))
        exp = pl.get("ExpirationDate")
        import datetime
        if exp and exp < datetime.datetime.now(exp.tzinfo):
            self.add("I-SIGN-002", "embedded.mobileprovision 已过期", "P2", "sign",
                     str(exp), "续期描述文件并重新打包，否则安装掉签。")

    def _check_h5_bundle(self, app_dir):
        markers = []
        for name in ("www", "public", "assets", "web", "h5"):
            d = app_dir / name
            if d.is_dir() and any(d.rglob("*.html")):
                markers.append(name)
        self.inventory["embedded_h5"] = markers
        if markers:
            self.manual_checks.append(
                f"发现内置 H5 目录 {markers}，应对其执行 "
                "python scripts/source_scan.py <目录> 做 H5 规则审计。")


# ---------------------------------------------------------------------------
# 输出
# ---------------------------------------------------------------------------

def render_text(auditor, target):
    f = auditor.findings
    counts = {s: 0 for s in SEV_ORDER}
    for x in f:
        counts[x["severity"]] += 1
    inv = auditor.inventory
    lines = [
        f"iOS IPA 静态审计报告 · {target}",
        "=" * 78,
        f"Bundle：{inv.get('bundle_id')}  v{inv.get('version')}({inv.get('build')})",
        f"最低系统(plist)：{inv.get('min_os_plist')}　设备族：{inv.get('device_family')}"
        f"　启动屏：{inv.get('launch')}",
        f"包体：{inv.get('size_mb')}MB / {inv.get('file_count')} 文件　"
        f"语言包：{inv.get('lproj')}",
        f"二进制：{inv.get('binary', {}).get('slices')}",
        f"Assets.car：{inv.get('assets_car')}　签名：{inv.get('code_signature')}　"
        f"描述文件：{inv.get('mobileprovision')}",
        "=" * 78,
        f"P0={counts['P0']} P1={counts['P1']} P2={counts['P2']} P3={counts['P3']}",
        "-" * 78,
    ]
    for x in sorted(f, key=lambda y: (SEV_ORDER[y["severity"]], y["path"])):
        lines.append(f"[{x['severity']}] {x['id']} {x['title']}")
        lines.append(f"    位置：{x['path']}")
        lines.append(f"    证据：{x['evidence']}")
        lines.append(f"    修复：{x['hint']}")
        lines.append(f"    参考：references/{x['doc']}")
        lines.append("-" * 78)
    if auditor.manual_checks:
        lines.append("需人工/macOS 复核：")
        for m in auditor.manual_checks:
            lines.append(f"  · {m}")
    return "\n".join(lines)


def render_md(auditor, target):
    f = auditor.findings
    counts = {s: 0 for s in SEV_ORDER}
    for x in f:
        counts[x["severity"]] += 1
    inv = auditor.inventory
    bininfo = inv.get("binary", {})
    out = [
        f"# iOS IPA 静态审计报告 · `{target}`",
        "",
        "## 一、产物概览",
        "",
        "| 项 | 值 |",
        "| --- | --- |",
        f"| Bundle | {inv.get('bundle_id')} v{inv.get('version')}({inv.get('build')}) |",
        f"| 最低系统 | plist: {inv.get('min_os_plist')}；"
        f"二进制: {[s.get('minos') for s in bininfo.get('slices', [])]} |",
        f"| 设备族 | {inv.get('device_family')}（iPad={'是' if inv.get('is_ipad') else '否'}） |",
        f"| 启动屏 | {inv.get('launch')} |",
        f"| 方向 | iPhone {len(inv.get('orientations_iphone', []))} 个 / "
        f"iPad {len(inv.get('orientations_ipad', []))} 个 |",
        f"| 隐私键 | {', '.join(inv.get('privacy_keys', [])) or '无'} |",
        f"| 架构 | {bininfo.get('slices')}；加密={'是' if bininfo.get('encrypted') else '否'} |",
        f"| 内嵌框架 | {[x['name'] for x in bininfo.get('frameworks', [])]} |",
        f"| Assets.car | {inv.get('assets_car')}（条目 {inv.get('car_assets', '-')}，"
        f"Scale {inv.get('car_scales', '-')}，图标像素 {inv.get('car_icon_px', '-')}） |",
        f"| 语言包 | {inv.get('lproj')} |",
        f"| 包体 | {inv.get('size_mb')}MB / {inv.get('file_count')} 文件 |",
        f"| 签名/描述文件 | {inv.get('code_signature')} / {inv.get('mobileprovision')}"
        f"（到期 {inv.get('provision_expires', '-')}） |",
        f"| 内置 H5 目录 | {inv.get('embedded_h5', '无')} |",
        "",
        f"**问题统计：P0 {counts['P0']} / P1 {counts['P1']} / "
        f"P2 {counts['P2']} / P3 {counts['P3']}**",
        "",
        "## 二、问题清单",
        "",
        "| 级别 | ID | 位置 | 证据 | 修复指向 |",
        "| --- | --- | --- | --- | --- |",
    ]
    for x in sorted(f, key=lambda y: (SEV_ORDER[y["severity"]], y["path"])):
        ev = x["evidence"].replace("|", "\\|").replace("\n", " ")[:140]
        hint = x["hint"].replace("|", "\\|").replace("\n", " ")[:140]
        out.append(f"| {x['severity']} | {x['id']} | `{x['path']}` | {ev} | {hint} |")
    out += ["", "## 三、大文件 Top", ""]
    large_files = inv.get("largest_files", [])
    if large_files:
        for item in large_files:
            out.append(f"- `{item['path']}`：{item['mb']}MB")
    else:
        out.append("- 无超过 10MB 的单资源")
    if auditor.manual_checks:
        out += ["", "## 四、需人工 / macOS 复核", ""]
        for m in auditor.manual_checks:
            out.append(f"- {m}")
    out += ["", "> 规则依据见 references/audit-ipa.md；评分与报告格式见 references/rubric.md。"]
    return "\n".join(out)


def main(argv=None):
    parser = argparse.ArgumentParser(description="iOS IPA / .app 静态产物审计")
    parser.add_argument("target", help=".ipa 文件或 .app / 含 Payload 的目录")
    parser.add_argument("--format", choices=["text", "md", "json"], default="text")
    parser.add_argument("--out")
    parser.add_argument("--min-severity", choices=list(SEV_ORDER), default="P3")
    parser.add_argument("--no-fail", action="store_true")
    parser.add_argument("--keep", action="store_true", help="保留解包目录")
    parser.add_argument("--workdir", help="解包目标目录（默认临时目录）")
    args = parser.parse_args(argv)

    auditor = IpaAuditor()
    try:
        auditor.audit(args.target, workdir=args.workdir, keep=args.keep)
    except (FileNotFoundError, ValueError, zipfile.BadZipFile) as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 2

    threshold = SEV_ORDER[args.min_severity]
    findings = [x for x in auditor.findings
                if SEV_ORDER[x["severity"]] <= threshold]
    counts = {s: 0 for s in SEV_ORDER}
    for x in findings:
        counts[x["severity"]] += 1

    if args.format == "json":
        report = json.dumps(
            {"target": str(args.target), "inventory": auditor.inventory,
             "manual_checks": auditor.manual_checks, "findings": findings},
            ensure_ascii=False, indent=2, default=str)
    elif args.format == "md":
        auditor.findings = findings
        report = render_md(auditor, args.target)
    else:
        auditor.findings = findings
        report = render_text(auditor, args.target)

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
