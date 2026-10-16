# Site Launch Phases 1-14 (Detailed Reference)

> 本文件包含 Phase 1-14 的详细检查清单。SKILL.md 中只保留各阶段摘要，详细内容按需加载本文件。

## Phase 1: Domain & Infrastructure

Most of this is one-click via Cloudflare's dashboard if the domain is on Cloudflare.

Ask first: "Is the domain already on Cloudflare with the standard config from previous launches?" (`yes-standard` | `yes-needs-review` | `no-fresh-setup`)

Checklist:

- [ ] Cloudflare: proxy ON for apex + www, TLS 1.3 minimum, "Always Use HTTPS" enabled, HSTS preload enabled in Cloudflare SSL/TLS settings
- [ ] DNS A/AAAA or CNAME pointing to Vercel (verify with `dig +short A example.com`)
- [ ] MX records for Google Workspace (verify with `dig +short MX example.com`)
- [ ] SPF, DKIM, DMARC records (verify all 3 with the dig commands above)
- [ ] CAA records restricting cert issuance (verify with `dig +short CAA example.com`)
- [ ] DNSSEC enabled at registrar level (verify with `dig +dnssec`)
- [ ] Vercel: project linked to repo, prod + preview env vars set, custom domain attached, prod and preview aliases correct
- [ ] Decide www vs apex canonical, configure 308 redirect for the non-canonical (verify with `curl -sIL https://www.example.com`)
- [ ] Custom 404 page renders (verify with `curl -sI https://example.com/does-not-exist`)
- [ ] Custom 500 page exists (cannot easily verify without forcing an error, ask user)
- [ ] If migration: 301 redirect map for every old URL (loop verification with `curl -sIL` per URL)

### Backups

If you don't configure backups at launch, you never will. Do it now.

Ask the user: "Which data stores does this app write to?" (`database-only` | `database-plus-file-storage` | `file-storage-only` | `stateless-no-persistent-data`). If `stateless-no-persistent-data`, skip this section.

**Database:**

- [ ] Automated daily backups enabled at the provider level (Neon, Supabase, PlanetScale, Railway, RDS — each has a one-click toggle). Verify by opening the backup panel and confirming the last backup timestamp is recent.
- [ ] Retention policy set to ≥30 days
- [ ] Point-in-time recovery (PITR) enabled if available (Neon, Supabase, RDS all support it)
- [ ] Off-site copy: if the provider stores backups in the same region as the primary, configure cross-region replication or a nightly export to a separate storage account (S3, R2, GCS)
- [ ] **Restore drill performed before launch**: pick a recent backup, restore to a staging database, verify row counts and a sample query. A backup you haven't tested is not a backup.

**File storage (if applicable — S3, R2, GCS, Cloudflare Images):**

- [ ] Versioning enabled on the primary bucket
- [ ] Cross-region replication or a scheduled sync to a secondary bucket. Backblaze B2 is a cheap, reliable option for off-site copies (significantly cheaper than S3/GCS egress). Use `rclone` to sync from S3/R2/GCS → B2 on a daily cron.
- [ ] Lifecycle rule: transition old versions to cheaper storage after 30 days, delete after 90 days (adjust to cost tolerance)

**Secrets / environment variables:**

- [ ] All env vars documented and stored in a secrets manager (1Password, Doppler, Vault, or equivalent). Not in a `.env` file on someone's laptop.
- [ ] Verify: if every engineer's machine burned tonight, could a new team member restore prod from scratch using only the secrets manager + git?

**Monitoring:**

- [ ] Set up an alert (email or Slack) if the daily backup job fails. Most providers support this natively; configure it before closing the backup panel.

---

## Phase 2: Analytics & Observability

Most third-party integrations are one-click via Cloudflare or Vercel.

**For the conditional tools (Crisp, Sentry, BetterStack), ask the user** to confirm per site type. See `references/decisions.md` for the observability tier matrix.

**Always-on:**

- [ ] Google Analytics 4: property created, measurement ID embedded, gated behind CNIL consent
- [ ] PostHog: based on user's earlier answer:
  - If `hogpost.samber.dev`: configure client with `api_host: "https://hogpost.samber.dev"` and verify CORS allows the new domain (test with browser console or `curl -H "Origin: https://newsite.com" -I https://hogpost.samber.dev/decide`)
  - If `set-up-new-proxy`: add path rewrite in `next.config.js` to `us.i.posthog.com` and `us-assets.i.posthog.com`, init client with `api_host: "/ingest"`
  - If `skip-PostHog`: skip
- [ ] Google Search Console: site verified (DNS TXT or HTML file), sitemap submitted
- [ ] Bing Webmaster Tools: site verified, sitemap submitted, IndexNow key file at `/{key}.txt` on root (verify with `curl -sI https://example.com/{key}.txt`)
- [ ] Ahrefs: site added to dashboard for tracking
- [ ] Add the site to the internal stats spreadsheet (PostHog properties registry + GitHub Sponsors tracking sheet if applicable)

**Brand monitoring (Google Alerts):**

For each alert, use these settings: **Frequency**: once a day | **Sources**: Automatic | **How many**: All results | **Region**: Any region

Set up one alert per keyword via alerts.google.com:

- [ ] Domain name (e.g., `example.com`)
- [ ] Brand or product name (quoted if multi-word, e.g., `"My Brand"`)
- [ ] Key feature or library names if the site documents a project
- [ ] Competitor brand names (optional — ask user: `yes-monitor-competitors` | `skip`)

Ask the user: "Which additional keywords to monitor?" (`product-name-only` | `domain-plus-brand` | `full-set-with-competitors` | `custom-list`)

**Developer community monitoring (F5bot) — for `doc-site` and `SaaS-app` targeting developers:**

F5bot (f5bot.com) monitors Reddit, Hacker News, and Lobste.rs for keyword mentions and sends email alerts. Free, no API required.

Set up one keyword per line at f5bot.com/add:

- [ ] Brand or product name
- [ ] Domain name (catches link shares)
- [ ] Key feature or library names
- [ ] Common misspellings if applicable

**Competitor analysis (`marketing/lead-gen`, `SaaS-app`, `training/paid-course` only):**

Before writing copy, setting up ads, or planning content, run a competitor analysis to understand what is already working in the market — positioning, messaging angles, CTA patterns, pricing presentation, and content strategy.

Use a deep research tool or a competitor analysis skill if one is available in the toolchain. Ask:

- "Do you already have competitor names/URLs to analyze?" (`yes-provide-list` | `no-discover-for-me` | `skip`)
- If `yes-provide-list`: ask the user to paste 2-5 names or URLs (free text)
- "What are we looking to extract?" (`positioning-and-messaging` | `pricing-strategy` | `content-and-seo` | `full-spectrum`)

Feed the output into:

- Phase 5 keyword strategy (target queries they rank for but you can outrank or flank)
- `TONE.md` voice calibration (deliberately differentiate from the dominant tone in the category)
- Phase 6 OG copy and CTA language (borrow proven frames, don't clone verbatim)
- Copywriting sub-skills invoked later (pass the competitor snapshot as context)

**Conditional (ask user, default per site type from `references/decisions.md`):**

- [ ] Crisp
- [ ] Sentry
- [ ] BetterStack

---

## Phase 3: Legal & Compliance (FR)

Ask first: "Is this site subject to French law?" (`yes-FR-operator-or-audience` | `no-EU-only` | `no-non-EU`). If no, ask whether GDPR or equivalent applies and adjust.

For FR sites:

- [ ] Mentions légales page (mandatory, fines up to 75k€ per omission)
- [ ] CGV (Conditions Générales de Vente) if commercial activity
- [ ] Privacy policy
- [ ] Terms of service
- [ ] CNIL-compliant cookie consent that **gates** GA4, PostHog, Crisp, Sentry script loading (not just a banner that always loads trackers). Use a CMP (Axeptio, Tarteaucitron, or custom). Verify with browser Network tab: no tracker fires before explicit consent.

---

## Phase 4: Security

Delegate the deep audit to `trailofbits/skills`. The items below are the must-pass checklist.

Ask first: CSP tightness level (`strict-default-src-none` | `balanced-allow-self` | `permissive-for-marketing`). See `references/templates.md` for the CSP template per level.

- [ ] CSP: target chosen tightness level. No `'unsafe-inline'` for scripts (use nonces). Verify with `curl -sI ... | grep -i content-security-policy`.
- [ ] HSTS: `max-age=31536000; includeSubDomains; preload`. Submit to hstspreload.org. Verify with `curl -sI ... | grep -i strict-transport`.
- [ ] X-Frame-Options: `DENY`
- [ ] X-Content-Type-Options: `nosniff`
- [ ] Referrer-Policy: `strict-origin-when-cross-origin`
- [ ] Permissions-Policy: deny camera, microphone, geolocation, payment unless used
- [ ] Run all headers in one go: `curl -sI https://example.com | grep -iE 'content-security|strict-transport|x-frame|x-content-type|referrer-policy|permissions-policy'`
- [ ] securityheaders.com: target A+ (verify via Claude Chrome extension or `curl https://securityheaders.com/?q=URL` and parse)
- [ ] observatory.mozilla.org: target 90+ (via Chrome extension)
- [ ] Run `trailofbits/skills` security audit on the codebase
- [ ] Verify no leaked secrets in client bundle: open Chrome DevTools Network tab via Claude Chrome extension, grep response bodies for `sk_`, `pk_`, `AKIA`, `ghp_`, `Bearer`

---

## Phase 5: SEO & GEO

Delegate the full audit to `AgriciDaniel/claude-seo`. The items below are the orchestration list.

See `references/templates.md` for `robots.txt`, `llms.txt`, and `manifest.json` templates. See `references/decisions.md` for the AI scraper policy matrix by site type.

- [ ] `/robots.txt` present, references sitemap (verify with `curl -s https://example.com/robots.txt`)
- [ ] `/sitemap.xml` present, valid (verify with `curl -s https://example.com/sitemap.xml | head -40`). Sitemap-index with per-language sitemaps if multilingual.
- [ ] `/llms.txt` present (per llmstxt.org spec, verify with `curl -s https://example.com/llms.txt`)
- [ ] AI scraper policy encoded in `robots.txt`. Apply the matrix from `references/decisions.md` based on site type, then **ask via the question tool to confirm each non-default decision** — this ships in a public file, get it right before it's crawled.
- [ ] Schema markup (JSON-LD): `Organization` + `WebSite` + `BreadcrumbList` site-wide; per-page types where applicable (`SoftwareApplication` for lib homepages, `Article` for blog posts, `FAQPage` for FAQs, `Person` for author bio). Verify with `curl -s URL | grep -A 50 'application/ld+json'`. Validate structured data via **Google Rich Results Test** and **Schema.org Validator**.
- [ ] Meta tags per page: unique `<title>` (50-60 chars), unique `<meta description>` (150-160 chars), `<link rel="canonical">`, `<meta name="robots">` if needed
- [ ] `hreflang` tags on every page if multilingual (every language version declares all alternates including self). Verify with `curl -s URL | grep -i hreflang`.
- [ ] **Keyword analysis using both Google Trends and Ahrefs** (they answer different questions, not interchangeable):
  - **Google Trends**: trajectory (rising vs declining), geographic distribution, seasonal patterns, related queries breakout, head-to-head comparison. Use to **validate direction and timing**.
  - **Exploding Topics**: surfaces emerging trends weeks or months before they peak in Google Trends.
  - **Answer The Public**: maps search questions, comparisons, and related queries around a seed keyword.
  - **Ahrefs Keywords Explorer**: monthly volume, keyword difficulty, SERP analysis, CPC, parent topic, traffic potential. Use to **size the opportunity**.
  - Combined output: a ranked shortlist of 3-5 target queries per page, with rationale.
- [ ] **AI visibility audit via productrank.ai**: open productrank.ai in a browser, submit multiple category or product searches, run the full AI SEO report.
- [ ] Typo and grammar pass on all visible text content
- [ ] Backlink profile audit: run **Ahrefs Backlink Checker** and **Moz Link Explorer** to assess domain authority and surface toxic or broken inbound links before launch
- [ ] Internal linking audit: every important page reachable in ≤3 clicks from the homepage

**Destination Pages Strategy:** Build these destination pages _before_ submitting to directories:

### 1. Alternative pages (highest ROI)

Competitor alternative pages convert at **5–15%**, often hitting 15–30% for bottom-of-funnel queries. One page per top competitor:

- `/alternatives/[competitor-1]` through `/alternatives/[competitor-4]`

Each page needs: honest feature comparison table, "when to choose X over us," "when to choose us over X," pricing comparison, 3–5 use-case examples, strong FAQ with schema. **Critical:** Be honest. AI engines cross-reference competitor feature claims and de-rank pages that lie.

### 2. Use-case / ICP pages

Every ICP gets a dedicated landing page:

- `/for/[audience]` — coaches, agencies, ecommerce, SaaS, consultants, etc.
- `/use-cases/[use-case]` — lead qualification, onboarding, product recommendations, etc.

### 3. Template / asset gallery (if applicable)

Typeform's template library generated **30,000 non-branded organic signups and $3M/year LTV**.

- One indexable page per template at `/templates/[slug]`.
- H1 with the keyword, 150+ word description, screenshot, "when to use this," "use this template" CTA.
- Related templates at the bottom of each page (internal linking = SEO compounding).
- 100 templates by day 30, 300 by day 90 is the realistic target.

### 4. "Best of" listicles you wrote yourself

Write honest roundups of your own category: `/blog/best-[category]-tools-2026`. Include yourself + 10 competitors with real reviews.

### 5. Integration pages (when integrations ship)

Every integration = one landing page at `/integrations/[partner]`. Follows the Zapier playbook: ~2.6M monthly organic visits from programmatic integration pages.

**GEO (Generative Engine Optimization):** In 2026, 30–50% of "research a tool" queries happen inside ChatGPT, Claude, Perplexity, or Google AI Overviews.

### Tactics that get pages cited

1. **One H1 per page, sequential heading hierarchy.** 2.8× higher citation rate.
2. **Dense, factual content with citable stats.** AI engines prefer specific numbers over vague claims.
3. **FAQ schema on every landing page.** AI engines heavily weight `FAQPage` JSON-LD.
4. **Comparison tables.** Extractable, structured — exactly what an AI answer needs.
5. **Explicit "what it is" paragraph in the first 100 words.**
6. **Get cited on Reddit and Hacker News.** Claude and Perplexity index these heavily.
7. **Publish original research.** "We analyzed 10,000 [things] and found X" becomes the primary citation.
8. **Claim Crunchbase, LinkedIn company page, and Wikidata entries.** All three feed AI training corpora.
9. **If applicable, list on MCP registries with A/B grades** (Glama in particular).

### Measurement

Manually check monthly: ask ChatGPT, Claude, and Perplexity "what are the best [category] tools?" and log where the product appears. Free GEO tracking tools (GeoTracker, llmrefs) automate this.

---

## Phase 6: Open Graph & Social Preview

Verify all OG and Twitter tags with: `curl -s URL | grep -iE 'og:|twitter:'`

- [ ] `og:title`, `og:description`, `og:url`, `og:type`, `og:site_name`
- [ ] `og:image` 1200×630px, absolute URL, `og:image:width` and `og:image:height` declared, `og:image:alt` set
- [ ] **Per-page `og:image`**, not one global. For doc sites: generate dynamically from page title. For blog posts: per-article custom image.
- [ ] `og:locale` + `og:locale:alternate` for each language if multilingual
- [ ] Twitter Cards: `twitter:card=summary_large_image`, `twitter:title`, `twitter:description`, `twitter:image`, `twitter:site` (handle)
- [ ] Validate with opengraph.xyz (covers FB, LinkedIn, Slack, Discord, WhatsApp previews) via Claude Chrome extension
- [ ] Validate with Twitter's card validator
- [ ] Manual check: paste URL in a LinkedIn DM, a Slack channel, a Discord, an iMessage. Preview must render correctly in all.

---

## Phase 7: Favicons & Web Manifest

See `references/templates.md` for the `manifest.json` template.

Generate from a single 1024×1024 source PNG using realfavicongenerator.net or favicon.io.

**Minimum modern set:**

- [ ] `/favicon.ico` (multi-res 16/32/48). Verify with `curl -sI https://example.com/favicon.ico`.
- [ ] `/favicon.svg` with embedded `<style>@media (prefers-color-scheme: dark) { ... }</style>` for dark mode. Verify with `curl -sI https://example.com/favicon.svg`.
- [ ] `/favicon-96x96.png` (PNG fallback)
- [ ] `/apple-touch-icon.png` 180×180px, no transparency, opaque background. Verify with `curl -sI`.
- [ ] `/web-app-manifest-192x192.png` (Android PWA icon)
- [ ] `/web-app-manifest-512x512.png` (Android splash)
- [ ] `/manifest.json` referencing both PNGs, with `theme_color`, `background_color`, `name`, `short_name`, `display`. Verify with `curl -s https://example.com/manifest.json | jq .`.

**Skip (deprecated):**

- `mstile-*.png` (Windows tiles)
- `safari-pinned-tab.svg` (deprecated since macOS Big Sur)
- `favicon-16x16.png` / `favicon-32x16.png` (covered by `.ico` and `.svg`)

**HTML head verification:**

```bash
curl -s https://example.com/ | grep -iE 'rel="icon"|rel="apple-touch-icon"|rel="manifest"'
```

---

## Phase 8: Quality Gates

Delegate to `addyosmani/web-quality-skills`. The skill covers 150+ Lighthouse audits across performance, accessibility, SEO, and best practices.

- [ ] **Unlighthouse site-wide crawl**: `npx unlighthouse --site {site}` — crawls all pages and runs Lighthouse on each. Surface pages below 90 on any axis before the per-URL checks.
- [ ] Lighthouse all 4 axes, mobile mode: target ≥90 on each (perf, a11y, best practices, SEO)
- [ ] Lighthouse all 4 axes, desktop mode: target ≥95 on each
- [ ] Core Web Vitals field data (CrUX via PageSpeed Insights): LCP < 2.5s, INP < 200ms, CLS < 0.1, on both mobile and desktop
- [ ] Accessibility (WCAG 2.2 AA via `web-quality-skills`): keyboard nav works for every interactive element, focus rings visible, color contrast ≥4.5:1 for text, all images have `alt`, heading hierarchy is monotonic (H1 → H2 → H3), ARIA labels on icon-only buttons
- [ ] Real mobile device test (not just devtools emulator). Use Claude Chrome extension on mobile viewport on a real device or BrowserStack.
- [ ] Cross-browser smoke test: Chrome, Safari, Firefox latest stable
- [ ] Print stylesheet sanity (Cmd+P should not break layout)

---

## Phase 9: Ecosystem Cross-linking

Internal cross-linking between owned properties. High-leverage SEO action for any multi-domain owner.

Ask the user: "List the other domains in your ecosystem that are topically relevant to this new site." Then for each one:

- [ ] Add a link from the existing site (footer / nav / "other projects" section) to the new site, where topically relevant
- [ ] Add a link to the new site in the README of the matching GitHub repo, if it documents a library
- [ ] Verify reciprocal links: every link added points back where appropriate
- [ ] If the new site documents a Go lib, link from related lib docs

Do not over-link. Only cross-link where topically relevant.

---

## Phase 10: Set up weekly SEO maintenance sub-agent

After launch, set up a scheduled background agent, such as Hermes or Claude Cowork Routine, that runs weekly to monitor SEO health and surface action items.

See `references/weekly-seo-agent.md` for the full agent definition, with a concrete equivalent for each harness. The agent uses these MCP connectors (or their equivalent API calls):

- Ahrefs MCP (backlinks, rankings, keywords)
- PostHog MCP (analytics correlation, AI bot traffic)
- Web search (SERP monitoring, competitor checks)
- Google Search Console (via community MCP or `curl` with service account credentials)

**Ask via the question tool** before creating the file: "Set up the weekly SEO agent now?" (`yes-create-agent-file` | `yes-but-defer` | `skip-for-now`).

When MCP are not available, use Claude for Chrome extension.

---

## Phase 11: Directory Submission Execution

Execute the directory submission workflow from the `directory-submissions` skill. This is the foundation layer of distribution — never the whole strategy.

### Step 1: Choose the tiers (from references/directory-list.md)

| Tier | When | Examples | Typical count |
| --- | --- | --- | --- |
| **Tier 1 — Flagship launch** | Launch week only | Product Hunt (anchor), BetaList, HN Show HN, Fazier, DevHunt | ~15 |
| **Tier 2 — Startup/SaaS** | Week 1 + rolling | AlternativeTo, SaaSHub, G2, Capterra, F6S, SourceForge, Slashdot | ~50 |
| **Tier 3 — AI directories** | Week 1–3 | TAAFT, Futurepedia, Toolify, Future Tools, aitools.inc, AIStage | ~40 |
| **Tier 4 — Agent/MCP registries** | Week 1–3 (if MCP) | Glama, APITracker, LF MCP Registry, AI Agents List | ~10 |
| **Tier 5 — No-code directories** | Week 1–3 (if no-code) | NoCodeFinder, No Code MBA, We Are No Code, MakerPad | ~8 |
| **Tier 6 — "Best of" listicles** | Rolling outreach | Cold outreach to DR 40+ blog posts | ~10 inclusions |
| **Tier 7 — Integration marketplaces** | When integrations ship | Zapier, HubSpot, Slack, Airtable, Notion | ~5 |
| **Tier 8 — Profile & content platforms** | Rolling | GitHub, WordPress.com, Substack, Dev.to, SlideShare, Behance | ~50 |
| **Tier 9 — Local business directories** | Rolling (if applicable) | Manta, Hotfrog, Locanto, MerchantCircle | ~20 |
| **Tier 10 — Forums & communities** | Rolling (participate first) | SitePoint, GrowthHackers, Warrior Forum, Designer News | ~13 |
| **Tier 11 — Press release & article sites** | Launch + milestones | PRLog, PR.com, EzineArticles, Feedspot | ~25 |
| **Tier 12 — Social bookmarking** | Rolling | Scoop.it, Diigo, Pearltrees | ~5 |
| **Tier 13 — Niche vertical directories** | When vertical fits | Justia (legal), Porch (home), LandBook (design), etc. | ~20 |

**Triage rule:** Only submit where the product is a genuine fit. Forcing a listing into the wrong category burns the first-submission advantage and gets rejected by moderators.

### Step 2: Prepare asset variations per tier

For each tier, prep a distinct description variant (from `references/positioning-variations.md`):

- **Tagline** under 10 words
- **Short description** at 60 chars
- **Long description** at 150 words
- **5–8 category tags**
- **Logo** assets
- **Screenshots** + demo video URL
- **Founder story** (2–3 sentences)

**Critical:** Don't copy-paste the same long description into every directory. Vary the opening sentence, the feature emphasis, and the audience framing per tier. AI engines cross-reference and down-weight duplicate content.

### Step 3: Batch submit with tracker

Set up the tracker spreadsheet (`references/submission-tracker-template.csv`). Work left-to-right through it. 2–3 hours per batch is realistic.

Per submission:

1. Copy the tier-appropriate positioning variant.
2. Fill in the form.
3. Upload assets.
4. Submit.
5. Log: date, URL, status, moderator notes.
6. Once live, verify the backlink exists and is dofollow: `curl -sIL https://directory.com/your-listing | grep -i rel=`. If absent, the link is dofollow.

---

## Phase 12: Product Hunt Deep Dive (The Anchor Event)

Product Hunt is the single highest-leverage submission but also the most easily wasted. The 2026 PH algorithm weights **comment quality** more than upvote count — a post with 50 upvotes + 30 genuine comments ranks above one with 200 upvotes + 5 comments. **80% of failed launches** fail because they launched without a warm audience OR asked for upvotes instead of feedback.

### 3-week prep timeline

- **Day -21 to -14:** Warm up hunter account. Upvote + thoughtfully comment on 3 launches/day. Follow 100+ active makers. Build history so your account looks real to the algorithm.
- **Day -14:** Create "Upcoming" page on PH. Drive traffic to it to collect "notify on launch" subscribers.
- **Day -10:** (Optional) book a hunter. Don't pay cash — trade a feature, shoutout, or intro. A known hunter adds ~15% to day-one momentum but isn't required.
- **Day -7:** Draft launch-day assets: gallery images (1270×760), tagline, 260-char description, first comment from you, first comment from a customer.
- **Day -3:** Email list warm-up. "We're launching Tuesday. Here's what to expect. Reply if you want a heads up."
- **Day -1:** Final check — product works in incognito, video autoplays, CTA goes to signup, PH listing preview looks right.

### Launch day execution

- **Launch at 12:01 AM Pacific Time.** Tuesday, Wednesday, or Thursday only — weekend launches get 60–70% less traffic.
- **First 2 hours are everything.** Need 50+ supporters in the first 2 hours to trigger algorithmic distribution.
- **Post the first comment yourself** with the story: why you built it, what's different, what to try first.
- **Reply to every comment** in under 30 minutes. PH measures maker responsiveness.
- **Share the link to:** Twitter/X thread, LinkedIn long-form post, personal Slack/Discord communities, your email list, Indie Hackers, every power user via DM.
- **Never ask for upvotes.** Ask for **feedback**. "Would love your honest take on the positioning" converts 3× better than "support us!"
- **Don't message strangers.** The community flags this and moderators will hide your post.

### Post-launch

- Write a launch recap blog post with numbers + lessons. Honest, not bragging. Publish on day 2.
- Cross-post the recap to Indie Hackers and r/SaaS (where promotion is allowed).
- Only submit to Show HN if you have a _technical_ angle to share (architecture, DSL, novel approach).

---

## Phase 13: Reviews Playbook (G2 / Capterra / TrustRadius)

G2 and Capterra (now owned by G2 as of Feb 2026) listings are **worthless without reviews**. 10 reviews is the magic threshold for Grid appearance. Run the 10-in-30 protocol during launch month.

### The 10-in-30 protocol

1. **Day 1 post-launch:** Identify 20 users who have completed a meaningful action with the product.
2. **Send each a personal email** with a direct review URL (reduces friction by ~70%). No forms, no landing pages — direct link.
3. **Offer a modest thank-you.** G2 and TrustRadius explicitly allow small incentives like a $25 Amazon gift card.
4. **Follow up once** after 5 days. Don't follow up twice — it becomes annoying and damages the relationship.
5. **Target:** 50% conversion → 10 reviews from 20 asks.

### Critical deadlines

- **G2 Summer reports:** cut off ~April 28. Plan review drives to land before this.
- **G2 Fall reports:** cut off ~July 28.
- Missing a cutoff means waiting 3 months for the next grid update.

### Badges and paid plans

- **"Users Love Us" badge** is still free: requires 20 reviews at 4.0+ average.
- **Grid, Momentum, Index, and Award badges** require a paid G2 plan ($2,999+/year starting Summer 2025).
- **Do not spend on paid G2 in year one.** The free listing + Users Love Us badge is sufficient.

### Cross-platform

- TrustRadius follows similar mechanics but smaller volume.
- Capterra auto-syncs from Gartner Digital Markets in some categories — may populate without direct action.

---

## Phase 14: Post-Launch Momentum

Your launch isn't over when the announcement goes live. Now comes adoption and retention work. Don't rely on a single launch event. Regular updates and feature rollouts sustain engagement.

### Immediate Post-Launch Actions

- **Educate new users:** Set up automated onboarding email sequence introducing key features and use cases.
- **Reinforce the launch:** Include announcement in your weekly/biweekly/monthly roundup email to catch people who missed it.
- **Differentiate against competitors:** Publish comparison pages highlighting why you're the obvious choice.
- **Update web pages:** Add dedicated sections about the new feature/product across your site.
- **Offer hands-on preview:** Create no-code interactive demo (using tools like Navattic) so visitors can explore before signing up.

### How to Prioritize What to Announce

Use this matrix to decide how much marketing each update deserves:

**Major updates** (new features, product overhauls):

- Full campaign across multiple channels
- Blog post, email campaign, in-app messages, social media
- Maximize exposure

**Medium updates** (new integrations, UI enhancements):

- Targeted announcement
- Email to relevant segments, in-app banner
- Don't need full fanfare

**Minor updates** (bug fixes, small tweaks):

- Changelog and release notes
- Signal that product is improving
- Don't dominate marketing

### Announcement Tactics

- **Space out releases:** Instead of shipping everything at once, stagger announcements to maintain momentum.
- **Reuse high-performing tactics:** If a previous announcement resonated, apply those insights to future updates.
- **Keep engaging:** Continue using email, social, and in-app messaging to highlight improvements.
- **Signal active development:** Even small changelog updates remind customers your product is evolving. This builds retention and word-of-mouth.
