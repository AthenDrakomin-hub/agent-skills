#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HBuilder X / uni-app 发版说明查询脚本

用法示例:
  # 版本总览（列出所有版本 + 各类型计数）
  python3 query_releasenotes.py overview

  # 查看某个版本的完整变更（按模块分组）
  python3 query_releasenotes.py show --version 5.26.2026091702
  python3 query_releasenotes.py show --version 5.26          # 模糊匹配主.次版本
  python3 query_releasenotes.py show --latest 3              # 最近 3 个版本

  # 关键词搜索（跨版本）
  python3 query_releasenotes.py search --keyword list-view
  python3 query_releasenotes.py search --keyword 暗黑 --module "uni-app x" --platform android

  # 跨版本区间（from 到 to，含两端；from/to 均可模糊匹配）
  python3 query_releasenotes.py range --from 5.0 --to 5.26

  # 常用过滤（可叠加）
  --module "uni-app x"        # HBuilder / uni-app / uni-app x / uts / uniCloud / app / miniprogram
  --platform android          # android / ios / harmony / web / app / windows / macos / mp-weixin / steam(蒸汽模式)
  --type 新增                 # 新增 / 修复 / 优化 / 变更 / 重要 / 升级
  --limit 20                  # 最多输出条数
  --no-links                  # 不输出链接行

退出码: 0 成功; 1 用法错误; 2 无匹配结果
"""
import argparse
import os
import re
import sys

DEFAULT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "references", "releasenotes_zh_CN.md")

# ---- 模块归一化（原始 ### 标题 -> 标准 key）----
MODULE_ALIASES = {
    "hbuilder": "HBuilder",
    "uniapp x": "uni-app x",
    "uniapp x 插件": "uni-app x",
    "uniapp": "uni-app",
    "uniapp 插件": "uni-app",
    "uts插件": "uts插件",
    "uts 插件": "uts插件",
    "unicloud": "uniCloud",
    "unicloud插件": "uniCloud",
    "app插件(含5+app和uni-app的app端)": "App插件",
    "app插件": "App插件",
    "uni小程序sdk": "小程序SDK",
}

# ---- 平台关键词 -> 标准 key（按长度降序匹配，避免 "app" 误中 "app平台" 之外的词）----
PLATFORM_PATTERNS = [
    ("mp-weixin", ["微信小程序平台"]),
    ("mp-alipay", ["支付宝小程序平台"]),
    ("harmony", ["鸿蒙平台"]),
    ("windows", ["Windows平台"]),
    ("macos", ["macOS平台"]),
    ("android", ["Android平台"]),
    ("ios", ["iOS平台"]),
    ("web", ["Web平台"]),
    ("app", ["App平台"]),
    ("steam", ["蒸汽模式"]),
]

# ---- 变更类型关键词（按优先级）----
TYPE_PATTERNS = [
    ("重要", ["【重要】"]),
    ("新增", ["新增"]),
    ("修复", ["修复"]),
    ("优化", ["优化"]),
    ("变更", ["变更"]),
    ("升级", ["升级"]),
    ("更新", ["更新"]),
]

VERSION_RE = re.compile(r"^##\s+(\d+\.\d+\.\d+)\s*$")
SECTION_RE = re.compile(r"^###\s+(.+?)\s*$")
ENTRY_RE = re.compile(r"^\*\s+(.*)$")
LINK_RE = re.compile(r"\[([^\]]*)\]\((https?://[^)]+)\)")
BARE_URL_RE = re.compile(r"<(https?://[^>]+)>")


def norm_module(raw: str) -> str:
    key = raw.strip().lower().replace(" ", "")
    # 去掉括号内容再试一次
    key_noparen = re.sub(r"[（(].*?[)）]", "", key)
    for alias, std in MODULE_ALIASES.items():
        a = alias.replace(" ", "")
        if key == a or key_noparen == a:
            return std
    return raw.strip()


def detect_platforms(text: str):
    found = []
    for std, kws in PLATFORM_PATTERNS:
        if any(kw in text for kw in kws):
            found.append(std)
    return found


def detect_type(text: str):
    for std, kws in TYPE_PATTERNS:
        if any(kw in text for kw in kws):
            return std
    return "其他"


def strip_links(text: str):
    """去掉 markdown 链接与裸 URL，只保留正文，便于关键词匹配与展示"""
    t = LINK_RE.sub("", text)
    t = BARE_URL_RE.sub("", t)
    t = re.sub(r"\s+", " ", t)
    return t.strip()


def extract_links(text: str):
    links = []
    for label, url in LINK_RE.findall(text):
        links.append((label.strip(), url))
    for url in BARE_URL_RE.findall(text):
        links.append(("详情", url))
    return links


def parse(path: str):
    """返回 list[dict]: {version, modules: {mod: [entry,...]}}，按文件顺序（新版在前）"""
    with open(path, encoding="utf-8") as f:
        lines = f.read().splitlines()

    versions = []
    cur_v = None
    cur_mod = None
    for line in lines:
        m = VERSION_RE.match(line)
        if m:
            cur_v = {"version": m.group(1), "modules": {}}
            versions.append(cur_v)
            cur_mod = None
            continue
        m = SECTION_RE.match(line)
        if m and cur_v is not None:
            cur_mod = norm_module(m.group(1))
            cur_v["modules"].setdefault(cur_mod, [])
            continue
        m = ENTRY_RE.match(line)
        if m and cur_v is not None:
            raw = m.group(1).strip()
            if not raw:
                continue
            plain = strip_links(raw)
            entry = {
                "raw": raw,
                "plain": plain,
                "type": detect_type(plain),
                "platforms": detect_platforms(plain),
                "links": extract_links(raw),
            }
            if cur_mod is None:
                cur_mod = "未分类"
                cur_v["modules"].setdefault(cur_mod, [])
            cur_v["modules"][cur_mod].append(entry)
            continue
    return versions


def match_version(version_list, query: str):
    """query 可以是完整版本号，或 '5.26' 这种前缀。返回匹配的 version dict 列表。"""
    query = query.strip()
    if re.match(r"^\d+\.\d+\.\d+$", query):
        for v in version_list:
            if v["version"] == query:
                return [v]
        return []
    # 前缀匹配：主.次 或 仅主版本
    return [v for v in version_list if v["version"].startswith(query + ".") or v["version"].startswith(query)]


def entry_matches(entry, args):
    if args.type and entry["type"] != args.type:
        return False
    if args.platform:
        wanted = args.platform.lower().split(",")
        if not any(p in entry["platforms"] for p in wanted):
            return False
    if args.keyword:
        kw = args.keyword.lower()
        if kw not in entry["plain"].lower():
            return False
    return True


def module_matches(mod_name, args):
    if not args.module:
        return True
    wanted = [m.strip().lower() for m in args.module.split(",")]
    name_l = mod_name.lower()
    return any(w in name_l for w in wanted)


def format_entry(entry, show_links=True):
    line = f"- [{entry['type']}] {entry['plain']}"
    if show_links and entry["links"]:
        links = "  " + "  ".join(f"[{label}]({url})" for label, url in entry["links"][:3])
        line += links
    return line


def cmd_overview(versions, args):
    print(f"共 {len(versions)} 个版本（从新到旧），文件：{os.path.basename(DEFAULT_FILE)}\n")
    for v in versions:
        counts = {}
        total = 0
        for mod, entries in v["modules"].items():
            for e in entries:
                counts[e["type"]] = counts.get(e["type"], 0) + 1
                total += 1
        parts = " ".join(f"{t}:{c}" for t, c in sorted(counts.items(), key=lambda x: -x[1]))
        mods = "/".join(v["modules"].keys())
        print(f"## {v['version']}  （{total} 条 | {parts}）")
        print(f"   模块: {mods}")
    return 0


def cmd_show(versions, args):
    if args.latest:
        selected = versions[: args.latest]
    else:
        selected = match_version(versions, args.version or "")
    if not selected:
        print(f"未找到版本: {args.version}", file=sys.stderr)
        return 2

    out_count = 0
    for v in selected:
        print(f"\n# 版本 {v['version']}")
        for mod, entries in v["modules"].items():
            if not module_matches(mod, args):
                continue
            matched = [e for e in entries if entry_matches(e, args)]
            if not matched:
                continue
            print(f"\n## {mod}")
            for e in matched:
                print(format_entry(e, show_links=not args.no_links))
                out_count += 1
                if args.limit and out_count >= args.limit:
                    return 0
    if out_count == 0:
        print("（无匹配的变更条目）", file=sys.stderr)
        return 2
    return 0


def cmd_search(versions, args):
    out_count = 0
    for v in versions:
        printed_ver = False
        for mod, entries in v["modules"].items():
            if not module_matches(mod, args):
                continue
            matched = [e for e in entries if entry_matches(e, args)]
            if not matched:
                continue
            if not printed_ver:
                print(f"\n# 版本 {v['version']}")
                printed_ver = True
            print(f"  ## {mod}")
            for e in matched:
                print("  " + format_entry(e, show_links=not args.no_links))
                out_count += 1
                if args.limit and out_count >= args.limit:
                    return 0
    if out_count == 0:
        print("（无匹配结果）", file=sys.stderr)
        return 2
    return 0


def cmd_range(versions, args):
    """from/newer -> to/older。文件已是新版在前，按位置切片。"""
    from_list = match_version(versions, args.from_ver)
    to_list = match_version(versions, args.to)
    if not from_list or not to_list:
        print(f"from={args.from_ver} to={args.to} 未全部匹配", file=sys.stderr)
        return 2
    fi = versions.index(from_list[0])
    ti = versions.index(to_list[0])
    if fi > ti:
        fi, ti = ti, fi  # 允许 from/to 顺序颠倒
    sub = versions[fi : ti + 1]

    out_count = 0
    for v in sub:
        printed_ver = False
        for mod, entries in v["modules"].items():
            if not module_matches(mod, args):
                continue
            matched = [e for e in entries if entry_matches(e, args)]
            if not matched:
                continue
            if not printed_ver:
                print(f"\n# 版本 {v['version']}")
                printed_ver = True
            print(f"  ## {mod}")
            for e in matched:
                print("  " + format_entry(e, show_links=not args.no_links))
                out_count += 1
                if args.limit and out_count >= args.limit:
                    return 0
    if out_count == 0:
        print("（区间内无匹配条目）", file=sys.stderr)
        return 2
    return 0


def build_parser():
    p = argparse.ArgumentParser(description="HBuilder X / uni-app 发版说明查询")
    p.add_argument("--file", default=DEFAULT_FILE, help="发版说明 markdown 路径（默认用 skill 内 bundled 文件）")
    sub = p.add_subparsers(dest="cmd", required=True)

    def add_common(sp):
        sp.add_argument("--module", help="模块过滤，逗号分隔：uni-app x,uni-app,uts,uniCloud,app,miniprogram,HBuilder")
        sp.add_argument("--platform", help="平台过滤，逗号分隔：android,ios,harmony,web,app,windows,macos,mp-weixin,steam")
        sp.add_argument("--type", help="变更类型：新增/修复/优化/变更/重要/升级")
        sp.add_argument("--keyword", help="关键词（不区分大小写，匹配条目正文）")
        sp.add_argument("--limit", type=int, help="最多输出条数")
        sp.add_argument("--no-links", action="store_true", help="不输出链接")

    sp_overview = sub.add_parser("overview", help="列出所有版本及计数")
    add_common(sp_overview)

    sp_show = sub.add_parser("show", help="查看指定版本完整变更")
    sp_show.add_argument("--version", help="完整版本号或前缀，如 5.26.2026091702 / 5.26")
    sp_show.add_argument("--latest", type=int, help="查看最近 N 个版本")
    add_common(sp_show)

    sp_search = sub.add_parser("search", help="跨版本关键词搜索")
    add_common(sp_search)

    sp_range = sub.add_parser("range", help="查看两个版本之间的变更")
    sp_range.add_argument("--from", dest="from_ver", required=True, help="起始版本（新，可前缀）")
    sp_range.add_argument("--to", required=True, help="结束版本（旧，可前缀）")
    add_common(sp_range)

    return p


def main():
    args = build_parser().parse_args()
    if not os.path.exists(args.file):
        print(f"发版说明文件不存在: {args.file}", file=sys.stderr)
        return 1
    versions = parse(args.file)

    if args.cmd == "overview":
        return cmd_overview(versions, args)
    if args.cmd == "show":
        if not args.version and not args.latest:
            print("show 需要 --version 或 --latest", file=sys.stderr)
            return 1
        return cmd_show(versions, args)
    if args.cmd == "search":
        return cmd_search(versions, args)
    if args.cmd == "range":
        return cmd_range(versions, args)
    return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BrokenPipeError:
        # 输出被 head/less 截断时静默退出
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())
        sys.exit(0)
