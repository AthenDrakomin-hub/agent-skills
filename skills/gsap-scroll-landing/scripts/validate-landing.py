#!/usr/bin/env python3
"""
validate-landing.py — GSAP 落地页验证器

检查生成的 HTML 是否符合技术约束：
- 是否引入了正确的 GSAP/ScrollTrigger CDN
- 动画是否只操作 transform 和 opacity（不触发重排）
- 是否有移动端降级
- 是否是单文件（无本地依赖）
纯 Python 标准库，零依赖。

用法:
    python3 validate-landing.py <landing.html>
退出码: 0=通过, 1=有问题
"""

import re
import sys
import argparse
from pathlib import Path


def validate_landing(filepath):
    content = Path(filepath).read_text(encoding='utf-8')
    issues = []
    warnings = []
    passes = []

    # 1. 检查 GSAP 引入
    if re.search(r'gsap[\w.-]*\.js', content):
        passes.append("引入了 GSAP 库")
    else:
        issues.append("未引入 GSAP 库")

    # 2. 检查 ScrollTrigger 引入
    if re.search(r'ScrollTrigger[\w.-]*\.js', content):
        passes.append("引入了 ScrollTrigger 插件")
    else:
        issues.append("未引入 ScrollTrigger 插件")

    # 3. 检查 GSAP 版本
    gsap_version = re.search(r'gsap@([\d.]+)', content)
    if gsap_version:
        passes.append(f"GSAP 版本: {gsap_version.group(1)}")
    else:
        warnings.append("未指定 GSAP 版本号，建议锁定 3.12.5")

    # 4. 检查 registerPlugin
    if 'registerPlugin' in content and 'ScrollTrigger' in content:
        passes.append("注册了 ScrollTrigger 插件")
    else:
        issues.append("未调用 gsap.registerPlugin(ScrollTrigger)")

    # 5. 检查动画属性（只允许 transform 和 opacity）
    animated_props = re.findall(r'gsap\.(to|from|fromTo)\s*\([^)]*\{([^}]*)\}', content, re.DOTALL)
    bad_props = []
    for _, props in animated_props:
        for bad in ['top:', 'left:', 'right:', 'bottom:', 'margin:', 'padding:', 'width:', 'height:']:
            if bad in props:
                bad_props.append(bad.strip(':'))
    if bad_props:
        issues.append(f"动画操作了触发重排的属性: {', '.join(set(bad_props))}")
    else:
        passes.append("动画只操作 transform 和 opacity")

    # 6. 检查移动端降级（matchMedia）
    if 'matchMedia' in content:
        passes.append("有移动端降级处理（matchMedia）")
    else:
        warnings.append("没有移动端降级处理，建议添加 gsap.matchMedia()")

    # 7. 检查是否有本地依赖（应该全是 CDN）
    local_refs = re.findall(r'(src|href)="(?!https?://|#|data:)[^"]+"', content)
    if local_refs:
        warnings.append(f"发现 {len(local_refs)} 个本地引用，单文件交付应全部使用 CDN")
    else:
        passes.append("无本地依赖，全部使用 CDN")

    # 8. 检查是否有 ScrollTrigger 配置
    if 'scrollTrigger' in content.lower():
        passes.append("使用了 ScrollTrigger 滚动动画")
    else:
        warnings.append("未使用 ScrollTrigger，页面可能没有滚动动画")

    # 9. 检查 scrub 平滑滚动
    if 'scrub' in content:
        passes.append("使用了 scrub 平滑跟随滚动")

    # 10. 检查 HTML 结构
    if '<!DOCTYPE html>' in content or '<!doctype html>' in content:
        passes.append("有 DOCTYPE 声明")
    else:
        warnings.append("缺少 DOCTYPE 声明")

    return {
        "file": str(filepath),
        "passes": passes,
        "warnings": warnings,
        "issues": issues,
        "valid": len(issues) == 0,
        "score": max(0, 100 - len(issues) * 20 - len(warnings) * 5)
    }


def main():
    parser = argparse.ArgumentParser(description='GSAP 落地页验证器')
    parser.add_argument('input', help='要验证的 HTML 文件路径')
    parser.add_argument('--json', action='store_true', help='JSON 格式输出')
    args = parser.parse_args()

    filepath = Path(args.input)
    if not filepath.exists():
        print(f"错误: 文件不存在: {filepath}", file=sys.stderr)
        sys.exit(1)

    result = validate_landing(filepath)

    if args.json:
        import json
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
            print("✅ 落地页符合技术约束，可以使用。")
        else:
            print("❌ 存在问题，请修复后重新验证。")

    sys.exit(0 if result['valid'] else 1)


if __name__ == '__main__':
    main()
