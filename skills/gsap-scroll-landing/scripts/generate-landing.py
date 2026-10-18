#!/usr/bin/env python3
"""
generate-landing.py — GSAP 滚动动画落地页生成器

根据用户输入生成完整的单文件 HTML 广告大片落地页。
技术栈：Tailwind CSS CDN + GSAP 3.12.5 + ScrollTrigger，浏览器直接打开即可预览。
纯 Python 标准库，零依赖。

用法:
    python3 generate-landing.py --title "产品名" --output landing.html
    python3 generate-landing.py --title "产品名" --theme dark --accent "#6366f1" --output landing.html
    python3 generate-landing.py --list-templates
"""

import argparse
import html as html_mod
from pathlib import Path


TEMPLATES = {
    "minimal": {
        "name": "极简黑白",
        "bg": "#ffffff",
        "text": "#111111",
        "accent": "#111111",
        "hero_bg": "linear-gradient(135deg, #f5f5f5 0%, #ffffff 100%)",
    },
    "dark": {
        "name": "暗黑科技",
        "bg": "#0a0a0a",
        "text": "#ffffff",
        "accent": "#00ff88",
        "hero_bg": "linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%)",
    },
    "vibrant": {
        "name": "活力渐变",
        "bg": "#ffffff",
        "text": "#1a1a2e",
        "accent": "#6366f1",
        "hero_bg": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    },
    "warm": {
        "name": "温暖橙黄",
        "bg": "#fffbf5",
        "text": "#2d1b00",
        "accent": "#f59e0b",
        "hero_bg": "linear-gradient(135deg, #fef3c7 0%, #fffbf5 100%)",
    },
    "ocean": {
        "name": "深海蓝",
        "bg": "#0c1929",
        "text": "#e0f2fe",
        "accent": "#38bdf8",
        "hero_bg": "linear-gradient(135deg, #0c1929 0%, #1e3a5f 100%)",
    },
}


def generate_html(title, subtitle, template="dark", accent=None, features=None):
    """生成完整的 HTML 落地页"""
    t = TEMPLATES.get(template, TEMPLATES["dark"])
    if accent:
        t["accent"] = accent

    title_esc = html_mod.escape(title or "产品名称")
    subtitle_esc = html_mod.escape(subtitle or "一句话描述你的产品")

    features = features or ["核心功能一", "核心功能二", "核心功能三"]
    feature_html = ""
    for i, f in enumerate(features):
        delay = i * 0.2
        feature_html += f'''
      <div class="feature-card" data-animate="fade-up" style="animation-delay:{delay}s">
        <div class="feature-icon" style="background:{t['accent']}20;color:{t['accent']};">{i+1:02d}</div>
        <h3>{html_mod.escape(f)}</h3>
        <p>简短描述这个功能的价值和优势。</p>
      </div>'''

    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title_esc}</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/gsap.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/ScrollTrigger.min.js"></script>
  <style>
    * {{ margin:0; padding:0; box-sizing:border-box; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", sans-serif;
      background: {t['bg']};
      color: {t['text']};
      overflow-x: hidden;
    }}
    .hero {{
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      text-align: center;
      background: {t['hero_bg']};
      position: relative;
      padding: 2rem;
    }}
    .hero-title {{
      font-size: clamp(2.5rem, 8vw, 6rem);
      font-weight: 900;
      letter-spacing: -0.02em;
      line-height: 1.1;
      margin-bottom: 1.5rem;
    }}
    .hero-title .char {{
      display: inline-block;
      opacity: 0;
      transform: translateY(40px);
    }}
    .hero-subtitle {{
      font-size: clamp(1rem, 2.5vw, 1.5rem);
      opacity: 0;
      transform: translateY(20px);
      max-width: 600px;
      line-height: 1.7;
    }}
    .hero-cta {{
      margin-top: 2.5rem;
      opacity: 0;
      transform: translateY(20px);
    }}
    .btn {{
      display: inline-block;
      padding: 1rem 2.5rem;
      background: {t['accent']};
      color: {t['bg']};
      border: none;
      border-radius: 50px;
      font-size: 1.1rem;
      font-weight: 700;
      cursor: pointer;
      text-decoration: none;
      transition: transform 0.3s, box-shadow 0.3s;
    }}
    .btn:hover {{
      transform: translateY(-2px);
      box-shadow: 0 10px 40px {t['accent']}40;
    }}
    .scroll-hint {{
      position: absolute;
      bottom: 2rem;
      left: 50%;
      transform: translateX(-50%);
      font-size: 0.85rem;
      opacity: 0.5;
      animation: bounce 2s infinite;
    }}
    @keyframes bounce {{
      0%,100% {{ transform: translateX(-50%) translateY(0); }}
      50% {{ transform: translateX(-50%) translateY(10px); }}
    }}
    .section {{
      min-height: 80vh;
      display: flex;
      flex-direction: column;
      justify-content: center;
      padding: 5rem 2rem;
      max-width: 1200px;
      margin: 0 auto;
    }}
    .section-title {{
      font-size: clamp(1.8rem, 4vw, 3rem);
      font-weight: 800;
      margin-bottom: 3rem;
      text-align: center;
    }}
    .features-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 2rem;
    }}
    .feature-card {{
      padding: 2rem;
      border-radius: 16px;
      background: {t['accent']}08;
      border: 1px solid {t['accent']}20;
      opacity: 0;
      transform: translateY(40px);
    }}
    .feature-icon {{
      width: 48px;
      height: 48px;
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 800;
      font-size: 1.2rem;
      margin-bottom: 1rem;
    }}
    .feature-card h3 {{
      font-size: 1.3rem;
      font-weight: 700;
      margin-bottom: 0.5rem;
    }}
    .feature-card p {{
      opacity: 0.7;
      line-height: 1.7;
    }}
    .product-showcase {{
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      position: relative;
      overflow: hidden;
    }}
    .product-item {{
      font-size: clamp(4rem, 15vw, 12rem);
      font-weight: 900;
      opacity: 0.1;
      position: absolute;
      white-space: nowrap;
    }}
    .footer {{
      text-align: center;
      padding: 4rem 2rem;
      opacity: 0.5;
      font-size: 0.9rem;
    }}
    @media (max-width: 768px) {{
      .features-grid {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>

  <!-- Hero 首屏 -->
  <section class="hero" id="hero">
    <h1 class="hero-title" id="heroTitle">{title_esc}</h1>
    <p class="hero-subtitle" id="heroSubtitle">{subtitle_esc}</p>
    <div class="hero-cta" id="heroCta">
      <a href="#features" class="btn">立即体验</a>
    </div>
    <div class="scroll-hint">↓ 向下滚动</div>
  </section>

  <!-- 产品展示（视差层） -->
  <section class="product-showcase" id="showcase">
    <div class="product-item" data-speed="0.3">{title_esc}</div>
    <div class="product-item" data-speed="0.5" style="top:30%;">{title_esc}</div>
    <div class="product-item" data-speed="0.2" style="top:60%;">{title_esc}</div>
  </section>

  <!-- 功能特性 -->
  <section class="section" id="features">
    <h2 class="section-title" data-animate="fade-up">核心功能</h2>
    <div class="features-grid">
      {feature_html}
    </div>
  </section>

  <!-- CTA -->
  <section class="section" id="cta" style="text-align:center;">
    <h2 class="section-title" data-animate="fade-up">准备好开始了吗？</h2>
    <p data-animate="fade-up" style="opacity:0.7;margin-bottom:2rem;font-size:1.2rem;">加入我们，体验不一样的产品</p>
    <a href="#" class="btn" data-animate="fade-up">免费开始</a>
  </section>

  <footer class="footer">
    <p>&copy; 2026 {title_esc}. All rights reserved.</p>
  </footer>

  <script>
    // 注册 ScrollTrigger
    gsap.registerPlugin(ScrollTrigger);

    // ===== Hero 逐字入场动画 =====
    const titleEl = document.getElementById('heroTitle');
    const titleText = titleEl.textContent;
    titleEl.innerHTML = titleText.split('').map(c =>
      c === ' ' ? '<span class="char" style="width:0.3em;"> </span>' : `<span class="char">${{c}}</span>`
    ).join('');

    gsap.to('.hero-title .char', {{
      opacity: 1,
      y: 0,
      duration: 0.8,
      stagger: 0.04,
      ease: 'power3.out',
      delay: 0.3
    }});

    gsap.to('#heroSubtitle', {{
      opacity: 1,
      y: 0,
      duration: 1,
      ease: 'power2.out',
      delay: 1
    }});

    gsap.to('#heroCta', {{
      opacity: 1,
      y: 0,
      duration: 1,
      ease: 'power2.out',
      delay: 1.3
    }});

    // ===== 产品视差滚动 =====
    document.querySelectorAll('.product-item').forEach((item, i) => {{
      const speed = parseFloat(item.dataset.speed) || 0.3;
      gsap.to(item, {{
        xPercent: -20 * (i % 2 === 0 ? 1 : -1),
        ease: 'none',
        scrollTrigger: {{
          trigger: '#showcase',
          start: 'top bottom',
          end: 'bottom top',
          scrub: 1
        }}
      }});
    }});

    // ===== 滚动淡入动画 =====
    document.querySelectorAll('[data-animate="fade-up"]').forEach(el => {{
      gsap.from(el, {{
        opacity: 0,
        y: 40,
        duration: 0.8,
        ease: 'power2.out',
        scrollTrigger: {{
          trigger: el,
          start: 'top 85%',
          toggleActions: 'play none none reverse'
        }}
      }});
    }});

    // ===== 功能卡片入场 =====
    gsap.from('.feature-card', {{
      opacity: 0,
      y: 40,
      duration: 0.8,
      stagger: 0.15,
      ease: 'power2.out',
      scrollTrigger: {{
        trigger: '.features-grid',
        start: 'top 80%'
      }}
    }});

    // ===== 移动端降级 =====
    let mm = gsap.matchMedia();
    mm.add('(max-width: 768px)', () => {{
      // 移动端降低动画强度
      gsap.to('.product-item', {{ opacity: 0.05 }});
    }});

    // 平滑滚动
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {{
      anchor.addEventListener('click', e => {{
        e.preventDefault();
        const target = document.querySelector(anchor.getAttribute('href'));
        if (target) target.scrollIntoView({{ behavior: 'smooth' }});
      }});
    }});
  </script>
</body>
</html>'''


def main():
    parser = argparse.ArgumentParser(description='GSAP 滚动动画落地页生成器')
    parser.add_argument('--title', default='产品名称', help='产品/页面标题')
    parser.add_argument('--subtitle', default='一句话描述你的产品', help='副标题')
    parser.add_argument('--template', default='dark', choices=TEMPLATES.keys(),
                        help='配色模板')
    parser.add_argument('--accent', help='自定义强调色（覆盖模板）')
    parser.add_argument('--features', nargs='*', help='功能列表（最多6个）')
    parser.add_argument('--output', '-o', default='landing.html', help='输出文件路径')
    parser.add_argument('--list-templates', action='store_true', help='列出所有模板')
    args = parser.parse_args()

    if args.list_templates:
        print("可用模板：")
        for tid, t in TEMPLATES.items():
            print(f"  {tid:10s} {t['name']} (主色: {t['accent']})")
        return

    html = generate_html(args.title, args.subtitle, args.template, args.accent, args.features)
    Path(args.output).write_text(html, encoding='utf-8')

    print(f"✓ 已生成: {args.output}")
    print(f"  标题: {args.title}")
    print(f"  模板: {args.template} ({TEMPLATES[args.template]['name']})")
    print(f"  强调色: {args.accent or TEMPLATES[args.template]['accent']}")
    print(f"  功能数: {len(args.features) if args.features else 3}")
    print(f"\n使用方法: 用浏览器打开 {args.output} 即可预览")
    print(f"动画效果: Hero逐字入场 + 产品视差滚动 + 滚动淡入 + 移动端降级")


if __name__ == '__main__':
    main()
