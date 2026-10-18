#!/usr/bin/env python3
"""
md2wechat.py — Markdown 转微信公众号 HTML 转换器

把 Markdown 文稿转换成符合微信公众号粘贴规范的行内样式 HTML。
内置 15 种风格，所有样式直接写在每个元素的 style 属性上。
纯 Python 标准库，零依赖。

用法:
    python3 md2wechat.py <input.md> [--style minimal] [--output output.html]
    python3 md2wechat.py <input.md> --all                  # 生成全部15种风格
    python3 md2wechat.py <input.md> --preview              # 生成6种推荐风格+总览页
    python3 md2wechat.py --list-styles                     # 列出所有风格
"""

import os
import re
import sys
import argparse
import html as html_mod
from pathlib import Path

# ============================================================
# 15 种风格定义（从 templates/styles.md 提取）
# 每种风格: {元素名: style字符串}
# ============================================================

STYLES = {
    "minimal": {
        "name": "极简黑白",
        "body": 'font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;font-size:16px;line-height:1.82;color:#2b2b2b;max-width:740px;margin:0 auto;padding:24px 22px;background-color:#fff;',
        "h1": 'font-size:24px;line-height:1.35;font-weight:800;text-align:left;margin:34px 0 24px;color:#111;padding-bottom:16px;border-bottom:1px solid #111;',
        "h2": 'font-size:19px;line-height:1.45;font-weight:800;margin:42px 0 14px;color:#111;',
        "h3": 'font-size:17px;line-height:1.5;font-weight:760;margin:30px 0 10px;color:#222;',
        "p": 'margin:12px 0;line-height:1.82;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;font-size:16px;color:#2b2b2b;',
        "blockquote": 'margin:20px 0;padding:13px 16px;border-left:3px solid #111;background-color:#f7f7f7;color:#555;font-style:normal;',
        "ul": 'margin:12px 0;padding-left:20px;',
        "ol": 'margin:12px 0;padding-left:20px;',
        "li": 'margin:7px 0;line-height:1.82;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;font-size:16px;color:#2b2b2b;',
        "strong": 'font-weight:850;color:#111;',
        "code": 'font-family:"SFMono-Regular",Consolas,"Liberation Mono",Menlo,monospace;background-color:#f2f2f2;color:#111;padding:2px 6px;border-radius:3px;font-size:14px;',
        "pre": 'background-color:#f2f2f2;color:#111;padding:14px 16px;overflow:auto;font-size:14px;line-height:1.6;',
        "hr": 'border:none;border-top:1px solid #e0e0e0;margin:32px 0;',
    },
    "medium": {
        "name": "Medium Essay",
        "body": 'font-family:Georgia,"Times New Roman","Songti SC","Noto Serif CJK SC",SimSun,serif;font-size:16px;line-height:1.92;color:#242424;max-width:680px;margin:0 auto;padding:34px 24px;background-color:#fff;',
        "h1": 'font-size:28px;line-height:1.28;font-weight:700;text-align:left;margin:42px 0 28px;color:#111;',
        "h2": 'font-size:22px;line-height:1.35;font-weight:700;margin:52px 0 18px;color:#111;',
        "h3": 'font-size:18px;line-height:1.45;font-weight:700;margin:34px 0 12px;color:#333;',
        "p": 'margin:15px 0;line-height:1.92;font-family:Georgia,"Times New Roman","Songti SC","Noto Serif CJK SC",SimSun,serif;font-size:16px;color:#242424;',
        "blockquote": 'margin:28px 0;padding:0 0 0 22px;border-left:3px solid #242424;color:#444;font-size:17px;line-height:1.86;font-style:italic;',
        "ul": 'margin:15px 0;padding-left:24px;',
        "ol": 'margin:15px 0;padding-left:24px;',
        "li": 'margin:8px 0;line-height:1.9;font-family:Georgia,"Times New Roman","Songti SC","Noto Serif CJK SC",SimSun,serif;font-size:16px;color:#242424;',
        "strong": 'font-weight:800;color:#111;',
        "code": 'font-family:"SFMono-Regular",Consolas,"Liberation Mono",Menlo,monospace;background-color:#f2f2f2;color:#222;padding:2px 6px;border-radius:3px;font-size:14px;',
        "pre": 'background-color:#f2f2f2;color:#222;padding:14px 16px;overflow:auto;font-size:14px;line-height:1.6;',
        "hr": 'border:none;border-top:1px solid #d8d8d8;margin:40px auto;width:34%;',
    },
    "wired": {
        "name": "WIRED Feature",
        "body": 'font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;font-size:16px;line-height:1.74;color:#111;max-width:750px;margin:0 auto;padding:22px;background-color:#fff;',
        "h1": 'font-size:28px;line-height:1.16;font-weight:950;text-align:left;margin:36px 0 26px;color:#111;border-top:6px solid #111;border-bottom:6px solid #111;padding:16px 0;',
        "h2": 'font-size:20px;line-height:1.35;font-weight:950;margin:44px 0 14px;color:#111;background-color:#f5ff00;padding:10px 12px;',
        "h3": 'font-size:18px;line-height:1.4;font-weight:900;margin:32px 0 10px;color:#111;text-decoration:underline;text-decoration-thickness:4px;text-decoration-color:#00e5ff;text-underline-offset:5px;',
        "p": 'margin:12px 0;line-height:1.74;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;font-size:16px;color:#111;',
        "blockquote": 'margin:22px 0;padding:15px 16px;background-color:#111;color:#fff;border-left:0;font-weight:750;font-style:normal;',
        "ul": 'margin:12px 0;padding-left:0;list-style:none;',
        "ol": 'margin:12px 0;padding-left:20px;',
        "li": 'margin:8px 0;line-height:1.72;padding:8px 10px;background-color:#f2f2f2;border-left:5px solid #111;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;font-size:16px;color:#111;',
        "strong": 'font-weight:950;color:#111;background-color:#f5ff00;',
        "code": 'font-family:"SFMono-Regular",Consolas,"Liberation Mono",Menlo,monospace;background-color:#111;color:#00e5ff;padding:2px 6px;border-radius:0;font-size:14px;',
        "pre": 'background-color:#111;color:#00e5ff;padding:14px 16px;overflow:auto;font-size:14px;line-height:1.6;',
        "hr": 'border:none;height:5px;background-color:#111;margin:34px 0;',
    },
    "stripe": {
        "name": "Stripe Docs",
        "body": 'font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC",sans-serif;font-size:16px;line-height:1.78;color:#333;max-width:720px;margin:0 auto;padding:28px 24px;background-color:#fff;',
        "h1": 'font-size:26px;line-height:1.3;font-weight:700;margin:36px 0 24px;color:#111;',
        "h2": 'font-size:20px;line-height:1.4;font-weight:700;margin:44px 0 16px;color:#111;padding-left:14px;border-left:4px solid #635bff;',
        "h3": 'font-size:17px;line-height:1.5;font-weight:600;margin:30px 0 10px;color:#222;',
        "p": 'margin:14px 0;line-height:1.78;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC",sans-serif;font-size:16px;color:#333;',
        "blockquote": 'margin:20px 0;padding:14px 18px;background-color:#f6f9fc;border-left:4px solid #635bff;color:#444;',
        "ul": 'margin:14px 0;padding-left:22px;',
        "ol": 'margin:14px 0;padding-left:22px;',
        "li": 'margin:8px 0;line-height:1.78;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC",sans-serif;font-size:16px;color:#333;',
        "strong": 'font-weight:700;color:#111;',
        "code": 'font-family:"SFMono-Regular",Consolas,Menlo,monospace;background-color:#f6f9fc;color:#635bff;padding:2px 6px;border-radius:4px;font-size:14px;',
        "pre": 'background-color:#f6f9fc;color:#333;padding:16px 18px;overflow:auto;font-size:14px;line-height:1.6;border-radius:6px;',
        "hr": 'border:none;border-top:1px solid #e6ebf1;margin:36px 0;',
    },
    "ft": {
        "name": "FT Analysis",
        "body": 'font-family:Georgia,"Times New Roman","Songti SC",serif;font-size:16px;line-height:1.85;color:#333;max-width:700px;margin:0 auto;padding:30px 26px;background-color:#fff1e5;',
        "h1": 'font-size:26px;line-height:1.3;font-weight:700;margin:38px 0 26px;color:#111;border-bottom:2px solid #111;padding-bottom:14px;',
        "h2": 'font-size:20px;line-height:1.4;font-weight:700;margin:42px 0 14px;color:#111;',
        "h3": 'font-size:17px;line-height:1.5;font-weight:700;margin:28px 0 10px;color:#222;',
        "p": 'margin:14px 0;line-height:1.85;font-family:Georgia,"Times New Roman","Songti SC",serif;font-size:16px;color:#333;',
        "blockquote": 'margin:24px 0;padding:14px 18px;border-left:4px solid #111;background-color:#fff;color:#444;font-style:italic;',
        "ul": 'margin:14px 0;padding-left:22px;',
        "ol": 'margin:14px 0;padding-left:22px;',
        "li": 'margin:8px 0;line-height:1.85;font-family:Georgia,"Times New Roman","Songti SC",serif;font-size:16px;color:#333;',
        "strong": 'font-weight:700;color:#111;',
        "code": 'font-family:"SFMono-Regular",Consolas,Menlo,monospace;background-color:#fff;color:#111;padding:2px 6px;border-radius:3px;font-size:14px;',
        "pre": 'background-color:#fff;color:#333;padding:14px 16px;overflow:auto;font-size:14px;line-height:1.6;',
        "hr": 'border:none;border-top:2px solid #111;margin:36px 0;',
    },
    "course": {
        "name": "课程讲义",
        "body": 'font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;font-size:16px;line-height:1.8;color:#2c3e50;max-width:740px;margin:0 auto;padding:26px 24px;background-color:#fff;',
        "h1": 'font-size:24px;line-height:1.35;font-weight:700;margin:32px 0 22px;color:#1a1a2e;padding:12px 16px;background-color:#e8f4f8;border-left:5px solid #3498db;',
        "h2": 'font-size:19px;line-height:1.45;font-weight:700;margin:38px 0 14px;color:#1a1a2e;border-bottom:2px solid #3498db;padding-bottom:8px;',
        "h3": 'font-size:17px;line-height:1.5;font-weight:600;margin:26px 0 10px;color:#2c3e50;',
        "p": 'margin:12px 0;line-height:1.8;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;font-size:16px;color:#2c3e50;',
        "blockquote": 'margin:18px 0;padding:12px 16px;background-color:#fef9e7;border-left:4px solid #f39c12;color:#7d6608;',
        "ul": 'margin:12px 0;padding-left:20px;',
        "ol": 'margin:12px 0;padding-left:20px;',
        "li": 'margin:6px 0;line-height:1.8;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;font-size:16px;color:#2c3e50;',
        "strong": 'font-weight:700;color:#1a1a2e;',
        "code": 'font-family:"SFMono-Regular",Consolas,Menlo,monospace;background-color:#e8f4f8;color:#2980b9;padding:2px 6px;border-radius:3px;font-size:14px;',
        "pre": 'background-color:#e8f4f8;color:#2c3e50;padding:14px 16px;overflow:auto;font-size:14px;line-height:1.6;border-radius:4px;',
        "hr": 'border:none;border-top:2px dashed #bdc3c7;margin:30px 0;',
    },
    "apple": {
        "name": "Apple Newsroom",
        "body": 'font-family:-apple-system,BlinkMacSystemFont,"SF Pro Text","Segoe UI",sans-serif;font-size:17px;line-height:1.7;color:#1d1d1f;max-width:720px;margin:0 auto;padding:32px 28px;background-color:#fff;',
        "h1": 'font-size:32px;line-height:1.2;font-weight:700;margin:40px 0 28px;color:#1d1d1f;letter-spacing:-0.5px;',
        "h2": 'font-size:24px;line-height:1.3;font-weight:700;margin:48px 0 18px;color:#1d1d1f;letter-spacing:-0.3px;',
        "h3": 'font-size:19px;line-height:1.4;font-weight:600;margin:34px 0 12px;color:#1d1d1f;',
        "p": 'margin:16px 0;line-height:1.7;font-family:-apple-system,BlinkMacSystemFont,"SF Pro Text","Segoe UI",sans-serif;font-size:17px;color:#1d1d1f;',
        "blockquote": 'margin:28px 0;padding:16px 22px;border-left:4px solid #0071e3;color:#555;font-size:18px;',
        "ul": 'margin:16px 0;padding-left:24px;',
        "ol": 'margin:16px 0;padding-left:24px;',
        "li": 'margin:10px 0;line-height:1.7;font-family:-apple-system,BlinkMacSystemFont,"SF Pro Text","Segoe UI",sans-serif;font-size:17px;color:#1d1d1f;',
        "strong": 'font-weight:700;color:#1d1d1f;',
        "code": 'font-family:"SF Mono",Consolas,Menlo,monospace;background-color:#f5f5f7;color:#1d1d1f;padding:2px 6px;border-radius:4px;font-size:14px;',
        "pre": 'background-color:#f5f5f7;color:#1d1d1f;padding:16px 18px;overflow:auto;font-size:14px;line-height:1.6;border-radius:8px;',
        "hr": 'border:none;border-top:1px solid #d2d2d7;margin:44px 0;',
    },
    "linear": {
        "name": "Linear Changelog",
        "body": 'font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;font-size:15px;line-height:1.7;color:#37352f;max-width:700px;margin:0 auto;padding:28px 24px;background-color:#fff;',
        "h1": 'font-size:22px;line-height:1.3;font-weight:600;margin:30px 0 20px;color:#37352f;',
        "h2": 'font-size:18px;line-height:1.4;font-weight:600;margin:36px 0 14px;color:#37352f;',
        "h3": 'font-size:16px;line-height:1.5;font-weight:600;margin:26px 0 10px;color:#37352f;',
        "p": 'margin:12px 0;line-height:1.7;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;font-size:15px;color:#37352f;',
        "blockquote": 'margin:18px 0;padding:12px 16px;background-color:#f7f6f3;border-left:3px solid #5e6ad2;color:#555;',
        "ul": 'margin:12px 0;padding-left:20px;',
        "ol": 'margin:12px 0;padding-left:20px;',
        "li": 'margin:6px 0;line-height:1.7;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;font-size:15px;color:#37352f;',
        "strong": 'font-weight:600;color:#37352f;',
        "code": 'font-family:"SFMono-Regular",Consolas,Menlo,monospace;background-color:#f1f1ef;color:#5e6ad2;padding:2px 5px;border-radius:3px;font-size:13px;',
        "pre": 'background-color:#f7f6f3;color:#37352f;padding:14px 16px;overflow:auto;font-size:13px;line-height:1.6;border-radius:4px;',
        "hr": 'border:none;border-top:1px solid #e9e9e7;margin:30px 0;',
    },
    "github": {
        "name": "GitHub README",
        "body": 'font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;font-size:16px;line-height:1.6;color:#24292f;max-width:760px;margin:0 auto;padding:28px 24px;background-color:#fff;',
        "h1": 'font-size:2em;line-height:1.25;font-weight:600;margin:32px 0 16px;color:#24292f;padding-bottom:0.3em;border-bottom:1px solid #d0d7de;',
        "h2": 'font-size:1.5em;line-height:1.3;font-weight:600;margin:40px 0 16px;color:#24292f;padding-bottom:0.3em;border-bottom:1px solid #d0d7de;',
        "h3": 'font-size:1.25em;line-height:1.4;font-weight:600;margin:30px 0 12px;color:#24292f;',
        "p": 'margin:12px 0;line-height:1.6;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;font-size:16px;color:#24292f;',
        "blockquote": 'margin:16px 0;padding:0 1em;color:#57606a;border-left:0.25em solid #d0d7de;',
        "ul": 'margin:12px 0;padding-left:2em;',
        "ol": 'margin:12px 0;padding-left:2em;',
        "li": 'margin:6px 0;line-height:1.6;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;font-size:16px;color:#24292f;',
        "strong": 'font-weight:600;color:#24292f;',
        "code": 'font-family:"SFMono-Regular",Consolas,"Liberation Mono",Menlo,monospace;background-color:rgba(175,184,193,0.2);color:#24292f;padding:0.2em 0.4em;border-radius:6px;font-size:85%;',
        "pre": 'background-color:#f6f8fa;color:#24292f;padding:16px;overflow:auto;font-size:85%;line-height:1.45;border-radius:6px;',
        "hr": 'border:none;border-top:1px solid #d0d7de;margin:32px 0;',
    },
    "notion": {
        "name": "Notion Memo",
        "body": 'font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;font-size:16px;line-height:1.7;color:#37352f;max-width:720px;margin:0 auto;padding:28px 24px;background-color:#fff;',
        "h1": 'font-size:26px;line-height:1.3;font-weight:700;margin:30px 0 20px;color:#37352f;',
        "h2": 'font-size:20px;line-height:1.4;font-weight:600;margin:34px 0 14px;color:#37352f;',
        "h3": 'font-size:17px;line-height:1.5;font-weight:600;margin:26px 0 10px;color:#37352f;',
        "p": 'margin:12px 0;line-height:1.7;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;font-size:16px;color:#37352f;',
        "blockquote": 'margin:16px 0;padding:10px 16px;background-color:#f7f6f3;border-left:3px solid #37352f;color:#555;',
        "ul": 'margin:12px 0;padding-left:22px;',
        "ol": 'margin:12px 0;padding-left:22px;',
        "li": 'margin:6px 0;line-height:1.7;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;font-size:16px;color:#37352f;',
        "strong": 'font-weight:600;color:#37352f;background-color:#fef3c7;padding:0 2px;',
        "code": 'font-family:"SFMono-Regular",Consolas,Menlo,monospace;background-color:#f1f1ef;color:#eb5757;padding:2px 5px;border-radius:3px;font-size:14px;',
        "pre": 'background-color:#f7f6f3;color:#37352f;padding:14px 16px;overflow:auto;font-size:14px;line-height:1.6;',
        "hr": 'border:none;border-top:1px solid #e9e9e7;margin:28px 0;',
    },
    "magazine": {
        "name": "Magazine Feature",
        "body": 'font-family:Georgia,"Times New Roman",serif;font-size:17px;line-height:1.85;color:#222;max-width:680px;margin:0 auto;padding:36px 30px;background-color:#fafafa;',
        "h1": 'font-size:32px;line-height:1.2;font-weight:700;margin:44px 0 30px;color:#111;text-align:center;letter-spacing:-1px;',
        "h2": 'font-size:24px;line-height:1.3;font-weight:700;margin:50px 0 20px;color:#111;text-align:center;',
        "h3": 'font-size:19px;line-height:1.4;font-weight:700;margin:36px 0 14px;color:#222;',
        "p": 'margin:18px 0;line-height:1.85;font-family:Georgia,"Times New Roman",serif;font-size:17px;color:#222;text-align:justify;',
        "blockquote": 'margin:32px 0;padding:20px 28px;border-top:2px solid #111;border-bottom:2px solid #111;color:#444;font-size:19px;font-style:italic;text-align:center;',
        "ul": 'margin:18px 0;padding-left:24px;',
        "ol": 'margin:18px 0;padding-left:24px;',
        "li": 'margin:10px 0;line-height:1.85;font-family:Georgia,"Times New Roman",serif;font-size:17px;color:#222;',
        "strong": 'font-weight:700;color:#111;',
        "code": 'font-family:"SFMono-Regular",Consolas,Menlo,monospace;background-color:#eee;color:#111;padding:2px 6px;border-radius:3px;font-size:14px;',
        "pre": 'background-color:#eee;color:#222;padding:16px 18px;overflow:auto;font-size:14px;line-height:1.6;',
        "hr": 'border:none;border-top:1px solid #ccc;margin:44px auto;width:50%;',
    },
    "editorial": {
        "name": "Editorial Column",
        "body": 'font-family:"PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;font-size:16px;line-height:1.9;color:#333;max-width:700px;margin:0 auto;padding:30px 26px;background-color:#fff;',
        "h1": 'font-size:26px;line-height:1.35;font-weight:700;margin:36px 0 24px;color:#111;',
        "h2": 'font-size:20px;line-height:1.4;font-weight:700;margin:40px 0 16px;color:#111;padding-left:12px;border-left:4px solid #c0392b;',
        "h3": 'font-size:17px;line-height:1.5;font-weight:600;margin:28px 0 10px;color:#333;',
        "p": 'margin:14px 0;line-height:1.9;font-family:"PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;font-size:16px;color:#333;',
        "blockquote": 'margin:22px 0;padding:14px 18px;background-color:#fdf2f2;border-left:4px solid #c0392b;color:#555;',
        "ul": 'margin:14px 0;padding-left:22px;',
        "ol": 'margin:14px 0;padding-left:22px;',
        "li": 'margin:8px 0;line-height:1.9;font-family:"PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;font-size:16px;color:#333;',
        "strong": 'font-weight:700;color:#c0392b;',
        "code": 'font-family:"SFMono-Regular",Consolas,Menlo,monospace;background-color:#fdf2f2;color:#c0392b;padding:2px 6px;border-radius:3px;font-size:14px;',
        "pre": 'background-color:#fdf2f2;color:#333;padding:14px 16px;overflow:auto;font-size:14px;line-height:1.6;',
        "hr": 'border:none;border-top:1px solid #ddd;margin:34px 0;',
    },
    "newspaper": {
        "name": "Newspaper Report",
        "body": 'font-family:Georgia,"Times New Roman","Songti SC",SimSun,serif;font-size:16px;line-height:1.8;color:#222;max-width:720px;margin:0 auto;padding:28px 24px;background-color:#fff;',
        "h1": 'font-size:28px;line-height:1.25;font-weight:700;margin:34px 0 22px;color:#111;border-bottom:3px double #111;padding-bottom:14px;',
        "h2": 'font-size:20px;line-height:1.35;font-weight:700;margin:38px 0 14px;color:#111;border-bottom:1px solid #111;padding-bottom:6px;',
        "h3": 'font-size:17px;line-height:1.45;font-weight:700;margin:28px 0 10px;color:#222;',
        "p": 'margin:12px 0;line-height:1.8;font-family:Georgia,"Times New Roman","Songti SC",SimSun,serif;font-size:16px;color:#222;text-align:justify;',
        "blockquote": 'margin:20px 0;padding:12px 16px;border-left:4px solid #111;background-color:#f5f5f5;color:#444;',
        "ul": 'margin:12px 0;padding-left:22px;',
        "ol": 'margin:12px 0;padding-left:22px;',
        "li": 'margin:6px 0;line-height:1.8;font-family:Georgia,"Times New Roman","Songti SC",SimSun,serif;font-size:16px;color:#222;',
        "strong": 'font-weight:700;color:#111;',
        "code": 'font-family:"SFMono-Regular",Consolas,Menlo,monospace;background-color:#f0f0f0;color:#111;padding:2px 6px;font-size:14px;',
        "pre": 'background-color:#f0f0f0;color:#222;padding:14px 16px;overflow:auto;font-size:14px;line-height:1.6;',
        "hr": 'border:none;border-top:1px solid #999;margin:32px 0;',
    },
    "verge": {
        "name": "The Verge Briefing",
        "body": 'font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;font-size:16px;line-height:1.75;color:#222;max-width:740px;margin:0 auto;padding:24px 22px;background-color:#fff;',
        "h1": 'font-size:28px;line-height:1.2;font-weight:800;margin:34px 0 24px;color:#111;',
        "h2": 'font-size:21px;line-height:1.35;font-weight:800;margin:42px 0 16px;color:#111;',
        "h3": 'font-size:18px;line-height:1.45;font-weight:700;margin:30px 0 12px;color:#222;',
        "p": 'margin:14px 0;line-height:1.75;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;font-size:16px;color:#222;',
        "blockquote": 'margin:22px 0;padding:14px 18px;background-color:#f5f5f5;border-left:5px solid #ff3b30;color:#444;font-weight:600;',
        "ul": 'margin:14px 0;padding-left:22px;',
        "ol": 'margin:14px 0;padding-left:22px;',
        "li": 'margin:8px 0;line-height:1.75;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;font-size:16px;color:#222;',
        "strong": 'font-weight:800;color:#111;',
        "code": 'font-family:"SFMono-Regular",Consolas,Menlo,monospace;background-color:#f5f5f5;color:#ff3b30;padding:2px 6px;border-radius:3px;font-size:14px;',
        "pre": 'background-color:#1a1a1a;color:#00ff88;padding:14px 16px;overflow:auto;font-size:14px;line-height:1.6;',
        "hr": 'border:none;border-top:3px solid #111;margin:36px 0;',
    },
    "event": {
        "name": "活动公告",
        "body": 'font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;font-size:16px;line-height:1.8;color:#333;max-width:720px;margin:0 auto;padding:28px 24px;background-color:#fff;',
        "h1": 'font-size:26px;line-height:1.3;font-weight:800;margin:32px 0 22px;color:#fff;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);padding:16px 20px;border-radius:8px;text-align:center;',
        "h2": 'font-size:20px;line-height:1.4;font-weight:700;margin:38px 0 14px;color:#667eea;border-bottom:2px solid #667eea;padding-bottom:6px;',
        "h3": 'font-size:17px;line-height:1.5;font-weight:600;margin:26px 0 10px;color:#444;',
        "p": 'margin:12px 0;line-height:1.8;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;font-size:16px;color:#333;',
        "blockquote": 'margin:20px 0;padding:14px 18px;background-color:#f0f0ff;border-left:4px solid #667eea;color:#555;border-radius:0 8px 8px 0;',
        "ul": 'margin:12px 0;padding-left:22px;',
        "ol": 'margin:12px 0;padding-left:22px;',
        "li": 'margin:8px 0;line-height:1.8;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;font-size:16px;color:#333;',
        "strong": 'font-weight:700;color:#667eea;',
        "code": 'font-family:"SFMono-Regular",Consolas,Menlo,monospace;background-color:#f0f0ff;color:#667eea;padding:2px 6px;border-radius:3px;font-size:14px;',
        "pre": 'background-color:#f0f0ff;color:#333;padding:14px 16px;overflow:auto;font-size:14px;line-height:1.6;border-radius:6px;',
        "hr": 'border:none;border-top:2px dashed #667eea;margin:30px 0;',
    },
}

RECOMMENDED = ["minimal", "medium", "stripe", "wired", "ft", "course"]
ALL_STYLES = list(STYLES.keys())


# ============================================================
# Markdown 解析
# ============================================================

def parse_inline(text):
    """解析行内 Markdown: **粗体**, `代码`, 链接"""
    text = html_mod.escape(text)
    # 粗体
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    # 行内代码
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    # 链接 [text](url) -> text（公众号不支持链接，保留文本）
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    return text


def parse_markdown(md_text):
    """解析 Markdown，返回 (title, html_body_elements列表)"""
    lines = md_text.split('\n')
    elements = []
    title = None
    i = 0
    in_code_block = False
    code_buffer = []
    list_buffer = []
    list_type = None

    def flush_list():
        nonlocal list_buffer, list_type
        if list_buffer:
            tag = 'ul' if list_type == 'ul' else 'ol'
            items = ''.join(f'<li>{parse_inline(item)}</li>' for item in list_buffer)
            elements.append(f'<{tag}>{items}</{tag}>')
            list_buffer = []
            list_type = None

    while i < len(lines):
        line = lines[i]

        # 代码块
        if line.strip().startswith('```'):
            if in_code_block:
                elements.append(f'<pre><code>{html_mod.escape(chr(10).join(code_buffer))}</code></pre>')
                code_buffer = []
                in_code_block = False
            else:
                flush_list()
                in_code_block = True
            i += 1
            continue

        if in_code_block:
            code_buffer.append(line)
            i += 1
            continue

        stripped = line.strip()

        # 空行
        if not stripped:
            flush_list()
            i += 1
            continue

        # 分割线
        if stripped == '---' or stripped == '***':
            flush_list()
            elements.append('<hr>')
            i += 1
            continue

        # 标题
        h_match = re.match(r'^(#{1,6})\s+(.+)$', stripped)
        if h_match:
            flush_list()
            level = len(h_match.group(1))
            text = h_match.group(2)
            if level == 1 and title is None:
                title = text  # 第一个一级标题作为文章标题，不进入正文
            elif level == 1:
                elements.append(f'<h2>{parse_inline(text)}</h2>')  # 后续一级标题降级为 h2
            else:
                tag = f'h{min(level, 3)}'
                elements.append(f'<{tag}>{parse_inline(text)}</{tag}>')
            i += 1
            continue

        # 引用
        if stripped.startswith('>'):
            flush_list()
            quote_text = stripped.lstrip('> ').strip()
            elements.append(f'<blockquote>{parse_inline(quote_text)}</blockquote>')
            i += 1
            continue

        # 无序列表
        if re.match(r'^[-*+]\s+', stripped):
            if list_type and list_type != 'ul':
                flush_list()
            list_type = 'ul'
            list_buffer.append(re.sub(r'^[-*+]\s+', '', stripped))
            i += 1
            continue

        # 有序列表
        if re.match(r'^\d+\.\s+', stripped):
            if list_type and list_type != 'ol':
                flush_list()
            list_type = 'ol'
            list_buffer.append(re.sub(r'^\d+\.\s+', '', stripped))
            i += 1
            continue

        # 普通段落
        flush_list()
        # 合并连续非空行
        para_lines = [stripped]
        i += 1
        while i < len(lines) and lines[i].strip() and not re.match(r'^(#{1,6}\s|>|[-*+]\s|\d+\.\s|```|---|\*\*\*)', lines[i].strip()):
            para_lines.append(lines[i].strip())
            i += 1
        para_text = ' '.join(para_lines)
        # 去掉段末中文句号
        para_text = re.sub(r'。$', '', para_text)
        elements.append(f'<p>{parse_inline(para_text)}</p>')

    flush_list()
    if in_code_block and code_buffer:
        elements.append(f'<pre><code>{html_mod.escape(chr(10).join(code_buffer))}</code></pre>')

    return title, elements


def apply_styles(elements, style_id):
    """把风格样式应用到每个元素"""
    style = STYLES[style_id]
    styled = []
    for el in elements:
        # 给每个标签加 style（替换所有匹配，不只是第一个）
        for tag in ['h1', 'h2', 'h3', 'p', 'blockquote', 'ul', 'ol', 'li', 'pre', 'hr']:
            pattern = f'<{tag}>'
            if pattern in el:
                el = el.replace(pattern, f'<{tag} style="{style.get(tag, "")}">')
        # strong 和 code 是行内的，也要加样式
        el = el.replace('<strong>', f'<strong style="{style.get("strong", "")}">')
        el = el.replace('<code>', f'<code style="{style.get("code", "")}">')
        styled.append(el)
    return styled


def generate_html(title, elements, style_id):
    """生成完整 HTML"""
    style = STYLES[style_id]
    body_style = style.get("body", "")
    title_text = title or "公众号文章"

    body_content = '\n  '.join(elements)

    return f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html_mod.escape(title_text)}</title>
</head>
<body style="{body_style}">
  {body_content}
</body>
</html>'''


def generate_overview(output_dir, base_name, generated):
    """生成总览页"""
    cards = []
    for style_id, filepath in generated:
        style_name = STYLES[style_id]["name"]
        cards.append(f'''<div style="margin:16px 0;padding:16px;border:1px solid #ddd;border-radius:8px;">
  <h3 style="margin:0 0 8px;font-size:18px;">{style_name} <code style="background:#f0f0f0;padding:2px 6px;border-radius:3px;font-size:13px;">{style_id}</code></h3>
  <a href="{filepath.name}" style="color:#0066cc;text-decoration:none;">打开预览 →</a>
</div>''')

    overview = f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <title>公众号HTML风格总览</title>
</head>
<body style="max-width:800px;margin:0 auto;padding:24px;font-family:sans-serif;">
  <h1>公众号HTML风格总览</h1>
  <p>共 {len(generated)} 种风格，点击打开预览，全选复制粘贴到公众号后台。</p>
  {''.join(cards)}
</body>
</html>'''
    overview_path = output_dir / "00_公众号HTML风格总览.html"
    overview_path.write_text(overview, encoding='utf-8')
    return overview_path


def main():
    parser = argparse.ArgumentParser(description='Markdown 转微信公众号 HTML')
    parser.add_argument('input', nargs='?', help='输入 Markdown 文件路径')
    parser.add_argument('--style', default='minimal', help='风格 id（默认 minimal）')
    parser.add_argument('--output', '-o', help='输出 HTML 文件路径')
    parser.add_argument('--all', action='store_true', help='生成全部15种风格')
    parser.add_argument('--preview', action='store_true', help='生成6种推荐风格+总览页')
    parser.add_argument('--list-styles', action='store_true', help='列出所有风格')
    args = parser.parse_args()

    if args.list_styles:
        print("可用风格：")
        for sid, s in STYLES.items():
            marker = " ★推荐" if sid in RECOMMENDED else ""
            print(f"  {sid:12s} {s['name']}{marker}")
        return

    if not args.input:
        parser.error("请指定输入 Markdown 文件")

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"错误: 文件不存在: {input_path}", file=sys.stderr)
        sys.exit(1)

    md_text = input_path.read_text(encoding='utf-8')
    title, elements = parse_markdown(md_text)

    if not elements:
        print("警告: Markdown 内容为空", file=sys.stderr)

    output_dir = input_path.parent / "公众号HTML输出"
    output_dir.mkdir(exist_ok=True)
    base_name = input_path.stem

    if args.all or args.preview:
        style_list = ALL_STYLES if args.all else RECOMMENDED
        generated = []
        for sid in style_list:
            styled = apply_styles(elements, sid)
            html_content = generate_html(title, styled, sid)
            style_name = STYLES[sid]["name"]
            out_file = output_dir / f"{base_name}_{sid}_{style_name}_微信公众号版.html"
            out_file.write_text(html_content, encoding='utf-8')
            generated.append((sid, out_file))
            print(f"  ✓ {sid} ({style_name}) -> {out_file.name}")

        overview = generate_overview(output_dir, base_name, generated)
        print(f"\n总览页: {overview}")
        print(f"输出目录: {output_dir}")
    else:
        if args.style not in STYLES:
            print(f"错误: 未知风格 '{args.style}'，可用: {', '.join(STYLES.keys())}", file=sys.stderr)
            sys.exit(1)

        styled = apply_styles(elements, args.style)
        html_content = generate_html(title, styled, args.style)

        if args.output:
            out_file = Path(args.output)
        else:
            style_name = STYLES[args.style]["name"]
            out_file = output_dir / f"{base_name}_{args.style}_{style_name}_微信公众号版.html"

        out_file.write_text(html_content, encoding='utf-8')
        print(f"✓ 已生成: {out_file}")
        print(f"  风格: {args.style} ({STYLES[args.style]['name']})")
        print(f"  标题: {title or '(无)'}")
        print(f"  元素数: {len(elements)}")
        print(f"\n使用方法: 打开 HTML → Cmd+A 全选 → Cmd+C 复制 → 粘贴到公众号后台")


if __name__ == '__main__':
    main()
