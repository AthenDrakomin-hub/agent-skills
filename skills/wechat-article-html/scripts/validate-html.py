#!/usr/bin/env python3
"""
validate-html.py — 微信公众号 HTML 粘贴规范验证器

检查生成的 HTML 是否符合微信公众号粘贴规范。
纯 Python 标准库，零依赖。

用法:
    python3 validate-html.py <output.html>
    python3 validate-html.py <output.html> --json   # JSON 格式输出
退出码: 0=通过, 1=有问题
"""

import re
import sys
import json
import argparse
from pathlib import Path


def validate_html(filepath):
    """验证 HTML 是否符合公众号粘贴规范"""
    content = Path(filepath).read_text(encoding='utf-8')
    issues = []
    warnings = []
    passes = []

    # 1. 不包含 <style> 标签
    if re.search(r'<style[\s>]', content, re.IGNORECASE):
        issues.append("包含 <style> 标签，公众号粘贴时会丢失")
    else:
        passes.append("无 <style> 标签")

    # 2. 不包含 class= 或 id=
    if re.search(r'\s(class|id)=', content, re.IGNORECASE):
        issues.append("包含 class= 或 id= 属性，公众号粘贴时会丢失")
    else:
        passes.append("无 class/id 属性")

    # 3. 不包含 :before :after
    if re.search(r':(before|after)', content, re.IGNORECASE):
        issues.append("包含 :before/:after 伪元素，公众号不支持")
    else:
        passes.append("无伪元素")

    # 4. 不包含 <script>
    if re.search(r'<script[\s>]', content, re.IGNORECASE):
        issues.append("包含 <script> 标签，公众号会清洗")
    else:
        passes.append("无 <script> 标签")

    # 5. 不包含外部 URL（除了允许的）
    external_urls = re.findall(r'https?://[^\s"\'<>]+', content)
    # 允许的 URL：只在注释或 meta 中
    if external_urls:
        warnings.append(f"包含 {len(external_urls)} 个外部 URL，公众号可能不加载: {external_urls[:3]}")
    else:
        passes.append("无外部 URL")

    # 6. 不包含 @import
    if '@import' in content:
        issues.append("包含 @import，公众号不支持")
    else:
        passes.append("无 @import")

    # 7. 每个可见正文元素都有 style 属性
    visible_tags = ['p', 'h1', 'h2', 'h3', 'blockquote', 'ul', 'ol', 'li', 'pre', 'hr']
    missing_style = []
    for tag in visible_tags:
        # 匹配 <tag> 但不是 <tag style=...>
        pattern = rf'<{tag}(?![^>]*style=)[^>]*>'
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            missing_style.append(f"{tag} ({len(matches)}个)")
    if missing_style:
        issues.append(f"以下元素缺少 style 属性: {', '.join(missing_style)}")
    else:
        passes.append("所有可见元素都有 style 属性")

    # 8. 每个普通段落都包含 font-size, line-height, color
    # 注意：style 属性值可能包含双引号（如 font-family:"Segoe UI"），用非贪婪匹配到标签结束
    p_tags = re.findall(r'<p\b[^>]*>', content, re.IGNORECASE)
    p_issues = []
    for i, tag in enumerate(p_tags):
        style_match = re.search(r'style="([^"]*(?:"[^"]*"[^"]*)*)"', tag)
        style = style_match.group(1) if style_match else ''
        if 'font-size' not in style:
            p_issues.append(f"第{i+1}个<p>缺少 font-size")
        if 'line-height' not in style:
            p_issues.append(f"第{i+1}个<p>缺少 line-height")
        if 'color' not in style:
            p_issues.append(f"第{i+1}个<p>缺少 color")
    if p_issues:
        issues.append(f"段落样式不完整: {'; '.join(p_issues[:5])}")
    elif p_tags:
        passes.append(f"所有 {len(p_tags)} 个段落样式完整")

    # 9. 列表容器和列表项都有 style
    for tag in ['ul', 'ol', 'li']:
        pattern = rf'<{tag}(?![^>]*style=)[^>]*>'
        if re.search(pattern, content, re.IGNORECASE):
            issues.append(f"<{tag}> 缺少 style 属性")
            break
    else:
        passes.append("列表元素样式完整")

    # 10. HTML 结构基本校验
    if '<!doctype html>' not in content.lower() and '<!DOCTYPE html>' not in content:
        warnings.append("缺少 DOCTYPE 声明")
    if '<html' not in content.lower():
        issues.append("缺少 <html> 标签")
    if '<head>' not in content.lower():
        warnings.append("缺少 <head> 标签")
    if '<body' not in content.lower():
        issues.append("缺少 <body> 标签")

    # 11. 检查是否有未转义的特殊字符
    if re.search(r'&(?!amp;|lt;|gt;|quot;|#\d+;|#x[0-9a-fA-F]+;)', content):
        warnings.append("可能存在未转义的 & 字符")

    return {
        "file": str(filepath),
        "passes": passes,
        "warnings": warnings,
        "issues": issues,
        "valid": len(issues) == 0,
        "score": max(0, 100 - len(issues) * 15 - len(warnings) * 5)
    }


def main():
    parser = argparse.ArgumentParser(description='微信公众号 HTML 验证器')
    parser.add_argument('input', help='要验证的 HTML 文件路径')
    parser.add_argument('--json', action='store_true', help='JSON 格式输出')
    args = parser.parse_args()

    filepath = Path(args.input)
    if not filepath.exists():
        print(f"错误: 文件不存在: {filepath}", file=sys.stderr)
        sys.exit(1)

    result = validate_html(filepath)

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"=== 验证报告: {filepath.name} ===")
        print(f"评分: {result['score']}/100")
        print(f"状态: {'✅ 通过' if result['valid'] else '❌ 未通过'}")
        print()

        if result['passes']:
            print("✅ 通过项:")
            for p in result['passes']:
                print(f"  ✓ {p}")
            print()

        if result['warnings']:
            print("⚠️ 警告:")
            for w in result['warnings']:
                print(f"  ! {w}")
            print()

        if result['issues']:
            print("❌ 问题（必须修复）:")
            for issue in result['issues']:
                print(f"  ✗ {issue}")
            print()

        if result['valid']:
            print("✅ HTML 符合微信公众号粘贴规范，可以使用。")
        else:
            print("❌ 存在问题，请修复后重新验证。")

    sys.exit(0 if result['valid'] else 1)


if __name__ == '__main__':
    main()
