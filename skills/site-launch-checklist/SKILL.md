---
name: site-launch-checklist
description: "Pre-launch checklist for shipping a new website or web app. Scope: analytics (GA4, PostHog, Google Search Console, Ahrefs), DNS, TLS and backups, legal and CNIL/GDPR compliance, security headers, SEO and GEO (robots.txt, sitemaps, llms.txt, hreflang, schema markup, keyword research), copywriting voice via TONE.md and a humanizer pass, OpenGraph and social previews, favicons and web manifest, Lighthouse, Core Web Vitals and WCAG quality gates, directory submissions, Product Hunt, G2/Capterra reviews, post-launch monitoring. Use when the user says 'checklist for the site', 'ready to ship', 'before I go live', 'ready for prod', 'audit before launch', or asks for a site review, pre-launch audit, or help launching a site or app, deploying a domain to production, or shipping a marketing, docs, SaaS, or lead-magnet site. 网站/应用上线前检查清单。覆盖分析、DNS/TLS/备份、法律合规、安全头、SEO、文案、社交预览、favicon、Lighthouse、可访问性、目录提交、上线后监控。触发词：上线检查, 发布清单, 网站上线, 上线前审计, 生产部署, SEO检查, 网站发布, launch checklist, 发布前检查."
license: MIT
compatibility: Designed for Claude Code, Codex or similar harness. Requires internet access for directory submissions, G2/Capterra reviews, and AI citation checks.
user-invocable: true
metadata:
  author: samber
  version: "2.0.1"
  openclaw:
    emoji: "📊"
    homepage: https://github.com/samber/cc-skills
    install:
      - kind: npm
        package: skills
        bins: [skills]
      - kind: brew
        formula: jq
        bins: [jq]
    requires:
      bins:
        - curl
        - npm
        - npx
        - jq
allowed-tools: Read Edit Write Glob Grep Agent AskUserQuestion
---

**Questions:** Ask the user through the environment's question tool — never as plain-text prose. One question at a time, 2–4 tappable options, wait for the answer. If the environment has no question tool, ask in prose with the same options, one at a time.

# Site Launch Checklist

Pre-launch audit and setup workflow for shipping a new website. Opinionated for Cloudflare DNS + Vercel hosting + PostHog + Legal context.

## Interaction style (READ FIRST)

This skill is intentionally interactive. Ask aggressively instead of assuming. The user will tap, not type.

**Always ask these questions at the start of a run** (one at a time, in this order):

1. Site type: `doc-site` | `marketing/lead-gen` | `SaaS-app` | `training/paid-course` | `personal-portfolio`
2. Migration: `greenfield-new-domain` | `migration-need-301-redirects` | `replacing-existing-on-same-domain`
3. Multilingual: `single-locale` | `en` | `fr+en` | `other-multi`
4. PostHog setup: `hogpost.samber.dev` | `set-up-new-proxy` | `skip-PostHog`
5. AI scraper policy: `use-default-for-site-type` | `customize-per-bot` | `block-all`
6. Browser tool available: `claude-chrome-extension` | `playwright` | `neither-skip-browser-checks`

**Ask again at every decision point throughout the phases**, including:

- Whether to install Sentry / BetterStack / Crisp (depends on site type, ask explicitly)
- www vs apex canonical preference (most sites: apex; ask anyway)
- Which AI bots to allow if user chose `customize-per-bot`
- CSP tightness level: `strict-default-src-none` | `balanced-allow-self` | `permissive-for-marketing`
- Whether to skip a phase entirely (e.g., skip Phase 3 if non-FR site)

Never proceed past a decision point without explicit user input. Verbose checklists without checkpoints are not the goal.

**Never install any MCP server or skill without explicit user confirmation.** Always ask via the question tool before running `npx skills add`, `claude mcp add`, or any equivalent install command — even when the skill selection workflow proposes a curated subset.

## How to use this skill

1. Run the start-of-session questions above.
2. Walk the user through phases 1-14 in order. For each phase: a. List items, ask if any should be skipped. b. For each remaining item, run the verification command (see "Verification tools" below). c. Report pass/fail. On fail, ask the user if they want to fix now or queue for later.
3. End with a status report grouped by phase, with blockers, recommended fixes, and optional improvements clearly separated.

**Detailed checklists for Phases 1-14 are in `references/launch-phases-detail.md`.** Load it when executing a specific phase. This SKILL.md keeps the core workflow, Phase 0 gate, verification tools, and output format.

## Companion skills

Six skill packs are useful for site launches. **Never install full multi-skill packs**. The actual subset to install is decided at invocation time based on the site type the user confirms.

### Pack inventory

| Pack | What it covers | Typically useful for |
| --- | --- | --- |
| `AgriciDaniel/claude-seo` | SEO + GEO + schema + hreflang + sitemaps audits, parallel sub-agents | All site types |
| `addyosmani/web-quality-skills` | Lighthouse, Core Web Vitals, accessibility, performance, best practices | All site types |
| `trailofbits/skills` | Security audit (OWASP, headers, dependencies) | All site types |
| `aaron-he-zhu/seo-geo-claude-skills` | 20 SEO+GEO skills, CORE-EEAT + CITE frameworks, `/seo:` slash commands | Content-heavy sites, competitive niches |
| `coreyhaines31/marketingskills` | ~30 marketing skills (CRO, copywriting, ads, popups, email, paywalls, etc.) | `marketing/lead-gen`, `SaaS-app`, `training/paid-course` |
| `jonathimer/devmarketing-skills` | 33 developer-marketing skills (persona, docs-as-marketing, technical tutorials, etc.) | `doc-site`, `SaaS-app` for developers |

### Skill selection workflow (run at session start)

After the user confirms site type, for **each pack relevant to that site type**:

1. **List available sub-skills**: `npx skills add owner/repo --list`
2. **Propose a curated subset** based on site type and the phases this skill will execute.
3. **Confirm with the user.** Use multi-select when the proposed list has more than 3 items, single-select (`install-as-proposed` | `let-me-modify` | `skip-this-pack`) otherwise.
4. **Bulk install the agreed subset**: `npx skills add owner/repo --skill A B C`

Rules:

- Sub-skill names live in the pack, not in this SKILL.md. Always query `--list` for the current state.
- Never run `npx skills add owner/repo` without `--skill` (that installs everything).
- Site type → packs mapping:
  - `doc-site`: claude-seo, web-quality-skills, trailofbits, seo-geo-claude-skills, devmarketing-skills
  - `marketing/lead-gen`: claude-seo, web-quality-skills, trailofbits, seo-geo-claude-skills, marketingskills
  - `SaaS-app`: all six
  - `training/paid-course`: claude-seo, web-quality-skills, trailofbits, marketingskills
  - `personal-portfolio`: claude-seo, web-quality-skills, trailofbits, seo-geo-claude-skills (lightweight subset)

## Phase 0: Launch Readiness Gate

**Run this BEFORE any other phase.** Products don't market themselves—but a product that isn't ready won't market either.

Two failure modes kill launches from opposite ends:

- **Stealth Mode** — launching too late. "Procrastination in a fancy suit." You keep polishing in private, waiting for the product to be perfect. It never ships.
- **"Just One More Feature"** — never launching. Every proposed launch date gets pushed for one more thing. The scope creeps forever.

The middle path is **SLC — Simple, Lovable, Complete** (Jason Cohen). A launchable v1 is:

- **Simple** — it does _one_ thing. Not many things poorly.
- **Lovable** — people _want_ to use it, not just tolerate it.
- **Complete** — it's a _whole_ experience for that one thing, not a stub with obvious holes.

**Quick check before running the phases:**

- [ ] Does it do one clearly-defined thing? (Simple)
- [ ] Would a target user _choose_ to use it, not just endure it? (Lovable)
- [ ] Is that one thing a whole experience, with no glaring stubs? (Complete)
- [ ] Are you polishing past this bar? → Stop. You're in Stealth Mode. Ship.
- [ ] Are you still adding new things to the scope? → Stop. Cut back to SLC.

**Directory submission readiness:** Ask these 9 questions. If any 1-7 are "no", they're a hard block.

1. Is the product publicly accessible (no password wall)?
2. Is there a pricing page (even "free while in beta")?
3. Are privacy policy + terms live?
4. Logo assets in PNG + SVG + square + favicon?
5. 5–8 real screenshots + 60–90s demo video?
6. Landing pages GEO-ready (single H1, sequential hierarchy, FAQ schema)?
7. At least 3 alternative pages and 3 use-case pages live and indexed?
8. Template gallery or lead magnet asset (if applicable)?
9. At least 20 beta/early users who could leave a review on G2?

**ORB Channel Strategy:** Structure launch marketing across three channel types:

- **Owned Channels** (Email, Blog, Podcast, Community, Website) — start with 1-2 based on audience
- **Rented Channels** (Social media, App stores, YouTube, Reddit) — pick 1-2 where audience is active, drive to owned channels
- **Borrowed Channels** (Guest content, Collaborations, Speaking, Influencers) — be proactive, pitch win-win collaborations

Pass the gate, then run the phases below.

## Copywriting voice and humanizer pass

Every site has visible marketing copy. Two layers of polish are mandatory before launch:

### 1. Define `TONE.md` once per site

Ask: "Does this site already have a `TONE.md`?" (`yes-already-exists` | `no-create-from-template` | `skip-use-default`).

If creating: write it to `.agents/TONE.md` or repo root `TONE.md`. See `references/templates.md` (section "TONE.md template").

### 2. Run a humanizer pass in the matching language

After every drafting step, run a humanizer to strip AI patterns.

- `english-global` → `npx skills add https://github.com/blader/humanizer --skill humanizer`
- `french` → use `samber/cc-skills@humaniseur-fr` or equivalent
- `other` → install matching humanizer if available; otherwise write a short language-specific anti-pattern checklist

Apply to: hero copy, feature descriptions, CTAs, meta descriptions, OG/Twitter card descriptions, blog posts, 404 page text. Skip legal pages.

### 3. Always reference TONE.md when invoking copywriting skills

When delegating to any copywriting sub-skill, include `TONE.md` in the prompt context.

## Browser interaction preference

Many checks require a real browser (Lighthouse, securityheaders.com, opengraph.xyz, Twitter card validator, mobile viewport, screen reader, Network tab).

**Always prefer the Claude Chrome extension.** Fall back to Playwright only if unavailable. If neither, ask the user whether to skip browser checks.

## Verification tools

Most checks are doable from the command line. Use these inline at every phase. Don't trust dashboards alone, verify with curl.

**DNS (Phase 1):**

```bash
dig +short A example.com                          # A record
dig +short AAAA example.com                       # AAAA (IPv6)
dig +short MX example.com                         # MX (mail)
dig +short TXT example.com                        # SPF + verification TXT
dig +short TXT _dmarc.example.com                 # DMARC
dig +short TXT default._domainkey.example.com     # DKIM
dig +short CAA example.com                        # CAA
dig +dnssec example.com | grep RRSIG              # DNSSEC active
```

**TLS / HTTPS (Phase 1):**

```bash
curl -sIL https://example.com | head             # follow redirects
curl -sI https://www.example.com                 # check www handling
openssl s_client -showcerts -connect example.com:443 < /dev/null 2>/dev/null | openssl x509 -noout -dates
```

**Headers (Phase 4):**

```bash
curl -sI https://example.com | grep -iE 'content-security-policy|strict-transport-security|x-frame-options|x-content-type-options|referrer-policy|permissions-policy'
curl -s "https://api.securityheaders.com/?q=https://example.com&followRedirects=on&hide=on" -I | grep -i 'x-grade'
```

**SEO files (Phase 5):**

```bash
curl -s https://example.com/robots.txt
curl -sI https://example.com/sitemap.xml
curl -s https://example.com/llms.txt
curl -s https://example.com/ | grep -A 50 'application/ld+json'   # Schema
curl -s https://example.com/ | grep -i hreflang                   # hreflang
```

**Open Graph & social (Phase 6):**

```bash
curl -s https://example.com/page | grep -iE 'og:|twitter:|<title|name="description"'
```

**Favicons & manifest (Phase 7):**

```bash
curl -sI https://example.com/favicon.ico
curl -sI https://example.com/favicon.svg
curl -sI https://example.com/apple-touch-icon.png
curl -s https://example.com/manifest.json | jq .
```

**404 / 500 / redirects:**

```bash
curl -sI https://example.com/this-does-not-exist
curl -sIL https://example.com/old-url     # verify 301 chain
```

Always run the relevant command, paste the output to the user when reporting, then ask whether to fix immediately or queue.

---

## Phases 1-14 (Detailed checklists in `references/launch-phases-detail.md`)

Load `references/launch-phases-detail.md` when executing each phase. Summary:

| Phase | Focus | Key items |
| --- | --- | --- |
| **1** | Domain & Infrastructure | Cloudflare proxy, DNS records, TLS, MX/SPF/DKIM/DMARC, CAA, DNSSEC, Vercel config, www/apex canonical, 404/500 pages, 301 redirects, **backups** (database + file storage + secrets + monitoring) |
| **2** | Analytics & Observability | GA4, PostHog (3 modes), Google Search Console, Bing Webmaster, Ahrefs, Google Alerts brand monitoring, F5bot dev community monitoring, competitor analysis, Crisp/Sentry/BetterStack (conditional) |
| **3** | Legal & Compliance (FR) | Mentions légales, CGV, Privacy policy, Terms, CNIL-compliant cookie consent that **gates** trackers |
| **4** | Security | CSP (3 tightness levels), HSTS preload, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy, securityheaders.com A+, observatory.mozilla.org 90+, trailofbits audit, no leaked secrets |
| **5** | SEO & GEO | robots.txt, sitemap.xml, llms.txt, AI scraper policy, Schema markup (JSON-LD), meta tags, hreflang, keyword research (Google Trends + Ahrefs + Exploding Topics + AnswerThePublic), AI visibility audit (productrank.ai), backlink audit, internal linking, **Destination Pages** (alternatives, use-cases, templates, listicles, integrations), GEO tactics |
| **6** | Open Graph & Social Preview | og:title/description/url/type/site_name, og:image 1200×630 per-page, og:locale, Twitter Cards, opengraph.xyz validation, manual preview in LinkedIn/Slack/Discord/iMessage |
| **7** | Favicons & Web Manifest | favicon.ico (multi-res), favicon.svg (dark mode), apple-touch-icon 180×180, web-app-manifest 192/512, manifest.json with theme_color/background_color/name/display |
| **8** | Quality Gates | Unlighthouse site-wide crawl, Lighthouse mobile ≥90 / desktop ≥95, Core Web Vitals (LCP<2.5s, INP<200ms, CLS<0.1), WCAG 2.2 AA, real mobile device test, cross-browser smoke, print stylesheet |
| **9** | Ecosystem Cross-linking | Internal cross-links between owned domains, GitHub README links, reciprocal links, only topically relevant |
| **10** | Weekly SEO Maintenance | Scheduled background agent (Hermes/Claude Cowork), Ahrefs/PostHog/GSC MCP connectors, see `references/weekly-seo-agent.md` |
| **11** | Directory Submission | 13-tier directory catalog (Tier 1 Product Hunt anchor → Tier 13 niche), asset variations per tier, batch submit with tracker, dofollow verification |
| **12** | Product Hunt Deep Dive | 3-week prep timeline, launch at 12:01 AM PT Tue/Wed/Thu, first 2 hours = 50+ supporters, ask for **feedback** not upvotes, reply to every comment, post-launch recap |
| **13** | Reviews Playbook (G2/Capterra) | 10-in-30 protocol (20 asks → 10 reviews), G2 report deadlines (Apr 28 / Jul 28), "Users Love Us" badge (20 reviews 4.0+), no paid G2 in year one |
| **14** | Post-Launch Momentum | Onboarding emails, comparison pages, interactive demos, update prioritization matrix (major/medium/minor), staggered releases, signal active development |

---

## KPIs & Tracking Dashboard

Track weekly. If a number isn't moving, investigate — don't just submit more directories.

| Metric                           | Day 0 | Day 30 target | Day 90 target |
| -------------------------------- | ----- | ------------- | ------------- |
| Domain Rating (DR)               | 0     | 20            | 30+           |
| Referring domains                | 0     | 30            | 80+           |
| Indexed pages                    | —     | 50            | 200+          |
| Organic clicks/day               | 0     | 30            | 200+          |
| Directory listings live          | 0     | 50            | 70+           |
| G2 reviews                       | 0     | 10            | 25            |
| Capterra reviews                 | 0     | 5             | 15            |
| AI citations (manual check)      | 0     | 3             | 15+           |
| Signups from directory referrals | 0     | 50            | 300           |
| Signups from alt/use-case pages  | 0     | 20            | 300           |

---

## What NOT to Do

1. **Don't pay for directory submission services** ($60–$200 packages). These are free.
2. **Don't submit to spam directories** (DR under 10, no traffic). They dilute your backlink profile.
3. **Don't submit with the wrong positioning.** Generic descriptions waste the listing.
4. **Don't treat directories as your entire GTM.** They're the foundation.
5. **Don't skip reviews on G2/Capterra.** Zero-review listings are dead.
6. **Don't ask for upvotes on Product Hunt.** The 2026 algorithm penalizes it. Ask for **feedback**.
7. **Don't amend old directory listings every week.** Submit once, check quarterly.
8. **Don't submit before the destination page exists.** Link equity needs a destination.
9. **Don't duplicate descriptions across directories.** AI engines penalize duplicate content.
10. **Don't lie on comparison pages.** AI engines cross-reference and de-rank lies.
11. **Don't over-index on launch-day spike.** The flywheel is templates + alternatives + reviews + ongoing content.
12. **Don't forget Crunchbase, LinkedIn company page, and Wikidata.** These feed AI training corpora.
13. **Don't launch before SLC gate passes.** Stealth Mode and "Just One More Feature" both kill launches.
14. **Don't skip the humanizer pass on marketing copy.** AI patterns tank credibility.
15. **Don't assume analytics "just work."** Verify every integration with curl before launch.
16. **Don't ignore backup drills.** A backup you haven't tested is not a backup.

---

## Output format

At the end of a full run, output a status report grouped by phase:

```
Phase 1: Domain & Infrastructure  [9/10 pass]
  ✓ Cloudflare proxy on
  ✓ DNS records configured
  ...
  ✗ DMARC missing. Fix: add TXT record at _dmarc.example.com with policy v=DMARC1; p=quarantine;...

Phase 2: Analytics & Observability  [6/7 pass]
  ...
```

Followed by three lists, in order:

1. **Blockers** (must fix before launch)
2. **Recommended fixes** (should fix before announcing)
3. **Optional improvements** (post-launch)

End by asking: "Which list do you want to tackle next?" (`blockers` | `recommended` | `optional` | `done-for-now`).

---

## References

- `references/launch-phases-detail.md`: Full detailed checklists for Phases 1-14 (domain, analytics, legal, security, SEO/GEO, social preview, favicons, quality gates, cross-linking, weekly SEO, directory submission, Product Hunt, reviews, post-launch)
- `references/decisions.md`: AI scraper policy matrix by site type, observability tier matrix
- `references/templates.md`: robots.txt, llms.txt, manifest.json, CSP templates per tightness level, security headers reference, TONE.md template
- `references/weekly-seo-agent.md`: Full definition of the weekly SEO maintenance sub-agent (MCPs, tasks, output format)
- `assets/weekly-seo-*.md`, `assets/weekly-seo-vibe.toml`: per-harness agent-definition files linked from `references/weekly-seo-agent.md`
- `references/directory-list.md`: 13-tier directory catalog with submission timing, examples, and counts
- `references/positioning-variations.md`: Positioning variant library per directory tier (tagline, short/long descriptions, category tags)
- `references/submission-tracker-template.csv`: Submission tracker spreadsheet template for logging directory submissions
