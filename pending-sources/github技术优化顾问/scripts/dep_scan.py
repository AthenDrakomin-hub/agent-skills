#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目技术栈与依赖清单扫描器
=========================
扫描项目根目录，识别核心语言、前端框架、UI 组件库、样式方案、构建工具、
状态管理、后端框架与数据库，输出技术栈现状清单，供 github-tech-optimizer
Step 1「项目技术栈扫描」直接使用。

支持：package.json / pnpm-lock.yaml / yarn.lock / requirements.txt /
pyproject.toml / Pipfile / go.mod / Cargo.toml / pom.xml / build.gradle /
vite.config.* / webpack.config.* / next.config.* / nuxt.config.* /
tailwind.config.* / uni.scss / manifest.json。

用法：
  python dep_scan.py [项目根目录] [--out FILE] [--format text|md|json]

仅依赖 Python 3.8+ 标准库。退出码恒为 0（信息采集类）。
"""

import argparse
import json
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# 技术栈指纹库：包名关键字 -> (类别, 识别名)
# ---------------------------------------------------------------------------

FRAMEWORK_HINTS = {
    "react": ("前端框架", "React"),
    "react-dom": ("前端框架", "React"),
    "vue": ("前端框架", "Vue"),
    "nuxt": ("前端框架", "Nuxt"),
    "@angular/core": ("前端框架", "Angular"),
    "svelte": ("前端框架", "Svelte"),
    "next": ("前端框架", "Next.js"),
}

UI_LIB_HINTS = {
    "antd": ("UI 组件库", "Ant Design"),
    "ant-design-vue": ("UI 组件库", "Ant Design Vue"),
    "element-ui": ("UI 组件库", "Element UI"),
    "element-plus": ("UI 组件库", "Element Plus"),
    "naive-ui": ("UI 组件库", "Naive UI"),
    "vant": ("UI 组件库", "Vant"),
    "uview-ui": ("UI 组件库", "uView UI"),
    "uview-plus": ("UI 组件库", "uView Plus"),
    "nutui": ("UI 组件库", "NutUI"),
    "uni-ui": ("UI 组件库", "uni-ui"),
    "thorui-uni": ("UI 组件库", "ThorUI"),
    "@shadcn/ui": ("UI 组件库", "shadcn/ui"),
    "@mui/material": ("UI 组件库", "MUI"),
    "bootstrap": ("UI 组件库", "Bootstrap"),
}

STYLE_HINTS = {
    "tailwindcss": ("样式方案", "Tailwind CSS"),
    "styled-components": ("样式方案", "styled-components"),
    "@emotion/react": ("样式方案", "Emotion"),
    "sass": ("样式方案", "Sass/SCSS"),
    "less": ("样式方案", "Less"),
    "postcss": ("样式方案", "PostCSS"),
}

BUILD_HINTS = {
    "vite": ("构建工具", "Vite"),
    "webpack": ("构建工具", "Webpack"),
    "rollup": ("构建工具", "Rollup"),
    "esbuild": ("构建工具", "esbuild"),
    "turbo": ("构建工具", "Turbopack"),
    "gulp": ("构建工具", "Gulp"),
}

STATE_HINTS = {
    "redux": ("状态管理", "Redux"),
    "@reduxjs/toolkit": ("状态管理", "Redux Toolkit"),
    "mobx": ("状态管理", "MobX"),
    "pinia": ("状态管理", "Pinia"),
    "vuex": ("状态管理", "Vuex"),
    "zustand": ("状态管理", "Zustand"),
    "jotai": ("状态管理", "Jotai"),
}

NET_HINTS = {
    "axios": ("数据请求", "Axios"),
    "@tanstack/react-query": ("数据请求", "React Query"),
    "swr": ("数据请求", "SWR"),
    "got": ("数据请求", "Got"),
}

# ---------------------------------------------------------------------------
# 单文件解析
# ---------------------------------------------------------------------------

def parse_package_json(path: Path, found: dict):
    try:
        data = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except Exception as e:  # noqa: BLE001
        found.setdefault("解析警告", []).append(f"package.json 解析失败：{e}")
        return

    deps = {}
    for section in ("dependencies", "devDependencies"):
        deps.update(data.get(section, {}) or {})

    found.setdefault("核心语言", []).append("JavaScript/TypeScript (Node)")
    if data.get("packageManager"):
        found.setdefault("包管理器", []).append(data["packageManager"].split("@")[0])

    def match(hint_map):
        for pkg, (cat, name) in hint_map.items():
            if any(pkg in d for d in deps):
                found.setdefault(cat, set()).add(name)

    match(FRAMEWORK_HINTS)
    match(UI_LIB_HINTS)
    match(STYLE_HINTS)
    match(BUILD_HINTS)
    match(STATE_HINTS)
    match(NET_HINTS)

    # TypeScript
    if "typescript" in deps:
        found.setdefault("语言", []).append("TypeScript")
    # uniapp
    if "@dcloudio/uni-app" in deps or any("@dcloudio" in d for d in deps):
        found.setdefault("前端框架", set()).add("uni-app")


def parse_requirements(path: Path, found: dict):
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        pkg = re.split(r"[=<>\[]", line, 1)[0].strip().lower()
        py_map = {
            "django": ("后端框架", "Django"),
            "flask": ("后端框架", "Flask"),
            "fastapi": ("后端框架", "FastAPI"),
            "tornado": ("后端框架", "Tornado"),
            "sanic": ("后端框架", "Sanic"),
            "gunicorn": ("部署/服务", "Gunicorn"),
            "uvicorn": ("部署/服务", "Uvicorn"),
            "celery": ("任务队列", "Celery"),
            "sqlalchemy": ("ORM", "SQLAlchemy"),
            "tortoise-orm": ("ORM", "Tortoise ORM"),
            "pymysql": ("数据库驱动", "PyMySQL"),
            "psycopg2": ("数据库驱动", "psycopg2"),
            "redis": ("缓存", "redis-py"),
        }
        for key, (cat, name) in py_map.items():
            if key in pkg:
                found.setdefault(cat, set()).add(name)


def parse_pyproject(path: Path, found: dict):
    text = path.read_text(encoding="utf-8", errors="ignore")
    found.setdefault("核心语言", []).append("Python (pyproject)")
    if "fastapi" in text.lower():
        found.setdefault("后端框架", set()).add("FastAPI")
    if "flask" in text.lower():
        found.setdefault("后端框架", set()).add("Flask")
    if "django" in text.lower():
        found.setdefault("后端框架", set()).add("Django")


def parse_go_mod(path: Path, found: dict):
    text = path.read_text(encoding="utf-8", errors="ignore")
    found.setdefault("核心语言", []).append("Go")
    go_hints = {
        "gin-gonic/gin": ("后端框架", "Gin"),
        "labstack/echo": ("后端框架", "Echo"),
        "gofiber/fiber": ("后端框架", "Fiber"),
        "go-chi/chi": ("后端框架", "Chi"),
        "gorm.io/gorm": ("ORM", "GORM"),
        "entgo.io/ent": ("ORM", "Ent"),
    }
    for key, (cat, name) in go_hints.items():
        if key in text:
            found.setdefault(cat, set()).add(name)


def parse_cargo(path: Path, found: dict):
    text = path.read_text(encoding="utf-8", errors="ignore").lower()
    found.setdefault("核心语言", []).append("Rust")
    if "actix-web" in text:
        found.setdefault("后端框架", set()).add("Actix Web")
    if "rocket" in text:
        found.setdefault("后端框架", set()).add("Rocket")
    if "warp" in text:
        found.setdefault("后端框架", set()).add("Warp")


def parse_pom(path: Path, found: dict):
    text = path.read_text(encoding="utf-8", errors="ignore").lower()
    found.setdefault("核心语言", []).append("Java (Maven)")
    if "spring-boot" in text:
        found.setdefault("后端框架", set()).add("Spring Boot")
    if "mybatis" in text:
        found.setdefault("ORM", set()).add("MyBatis")
    if "druid" in text:
        found.setdefault("连接池", set()).add("Druid")


def parse_gradle(path: Path, found: dict):
    text = path.read_text(encoding="utf-8", errors="ignore").lower()
    found.setdefault("核心语言", []).append("Java/Kotlin (Gradle)")
    if "spring-boot" in text:
        found.setdefault("后端框架", set()).add("Spring Boot")


def detect_configs(root: Path, found: dict):
    """通过配置文件名识别构建/样式工具。"""
    config_map = {
        "vite.config.": ("构建工具", "Vite"),
        "webpack.config.": ("构建工具", "Webpack"),
        "next.config.": ("前端框架", "Next.js"),
        "nuxt.config.": ("前端框架", "Nuxt"),
        "tailwind.config.": ("样式方案", "Tailwind CSS"),
        "uni.scss": ("移动端框架", "uni-app"),
        "manifest.json": ("移动端框架", "uni-app/HBuilder"),
    }
    for p in root.iterdir():
        if not p.is_file():
            continue
        name = p.name.lower()
        for key, (cat, val) in config_map.items():
            if key in name:
                found.setdefault(cat, set()).add(val)


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------

PARSERS = {
    "package.json": parse_package_json,
    "requirements.txt": parse_requirements,
    "pyproject.toml": parse_pyproject,
    "go.mod": parse_go_mod,
    "Cargo.toml": parse_cargo,
    "pom.xml": parse_pom,
    "build.gradle": parse_gradle,
    "build.gradle.kts": parse_gradle,
}


def scan(root: Path) -> dict:
    found = {}
    for fname, parser in PARSERS.items():
        p = root / fname
        if p.exists():
            parser(p, found)
    detect_configs(root, found)

    # README 存在性
    readme = next(root.glob("README*"), None)
    found["README"] = [readme.name] if readme else ["未找到 README"]

    # 去重
    result = {}
    for k, v in found.items():
        if isinstance(v, set):
            result[k] = sorted(v)
        elif isinstance(v, list):
            result[k] = sorted(set(v))
        else:
            result[k] = v
    return result


def render_md(result: dict, root: Path) -> str:
    lines = [
        f"# 项目技术栈现状清单",
        "",
        f"- 项目根目录：`{root}`",
        "",
        "| 维度 | 识别结果 |",
        "|------|----------|",
    ]
    for k, v in result.items():
        if isinstance(v, list):
            val = "、".join(str(x) for x in v)
        else:
            val = str(v)
        lines.append(f"| {k} | {val} |")
    lines.append("")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="项目技术栈与依赖清单扫描器")
    ap.add_argument("root", nargs="?", default=".", help="项目根目录（默认当前目录）")
    ap.add_argument("--format", choices=["text", "md", "json"], default="md")
    ap.add_argument("--out", help="输出文件")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"错误：目录不存在 {root}", file=sys.stderr)
        sys.exit(1)

    result = scan(root)

    if args.format == "json":
        text = json.dumps(result, ensure_ascii=False, indent=2)
    elif args.format == "md":
        text = render_md(result, root)
    else:
        text = "\n".join(f"{k}: {v}" for k, v in result.items())

    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"报告已写入：{args.out}")
    else:
        print(text)


if __name__ == "__main__":
    main()
