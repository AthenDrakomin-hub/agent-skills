# daily-evolve.ps1
# Daily skill repository evolution script
# Scans local skill directories, auto-includes qualifying new skills, validates, and pushes.

$ErrorActionPreference = "Stop"

# === Configuration ===
# Option A: the agent-facing identifier (`name`) stays an ASCII slug; the
# human/Chinese display title lives in the optional `label` frontmatter field.
# No hardcoded user paths here: repo root derives from this script's location
# (scripts/../) and both are env-overridable, so the pipeline stays portable
# and clean under the CI hardcoded-path scan.
$RepoRoot = if ($env:SKILL_REPO_ROOT) { $env:SKILL_REPO_ROOT } else { Split-Path -Parent $PSScriptRoot }
$SkillsDir = Join-Path $RepoRoot "skills"
$LogFile = Join-Path $RepoRoot "evolve.log"

$LocalSkillRoots = if ($env:SKILL_LOCAL_ROOTS) {
    $env:SKILL_LOCAL_ROOTS.Split(',')
} else {
    @(
        "$env:LOCALAPPDATA\DoubaoWork\User Data\Default\.doubaowork\agent_mode\workspace\.user_skills",
        "$env:USERPROFILE\DoubaoWork\skills",
        "$env:USERPROFILE\.agents\skills"
    )
}

# Quality thresholds (raised to avoid thin/duplicate skills)
$MaxLines = 500
$MinLines = 80
$MinDescLength = 150
# Option A: agent identifiers stay ASCII lowercase-hyphen. Chinese display
# titles are carried by the optional `label` frontmatter field instead.
$NamePattern = '^[a-z][a-z0-9-]*[a-z0-9]$'
$TriggerPattern = 'use when|triggers?|触发|适用于|Use when'

# Option A: Chinese name -> ASCII slug map for skills whose frontmatter name
# is not yet ASCII. ASCII-looking names are auto-normalized (case/punctuation
# cleaned); pure-Chinese names REQUIRE an entry here, otherwise they stay in
# PENDING.md with an actionable reason instead of being silently dropped.
$SlugMap = @{
    'AI写作检测'         = 'ai-writing-detector'
    'GitHub技术优化顾问'  = 'github-tech-advisor'
    'GSAP广告大片复刻'    = 'gsap-ad-replica'
    'iOS界面审计开发'     = 'ios-ui-audit'
    'JTBD任务模型'        = 'jtbd-task-model'
    'uni-app发版查询'      = 'uniapp-release-notes'
    'uni-app多端体验审计'  = 'uniapp-multi-audit'
    'Web设计规范审查'      = 'web-design-review'
    '专家聊天室'          = 'expert-chatroom'
    '传播效果分析'        = 'diffusion-analysis'
    '公众号HTML转换'      = 'wechat-article-html'
    '内容共鸣分析'        = 'content-resonance-analysis'
    '内容系统整理'        = 'content-organization'
    '内容诊断'            = 'content-diagnosis'
    '内容风险检查'        = 'content-risk-check'
    '商业工具箱'          = 'business-toolbox'
    '商业问题拆解'        = 'business-problem-breakdown'
    '奥派经济学聊天室'    = 'austrian-economics-chatroom'
    '学习文章拆分'        = 'study-article-splitter'
    '对标筛选'            = 'benchmark-screening'
    '小红书标题生成'      = 'xiaohongshu-title-gen'
    '截图转前端代码'      = 'screenshot-to-frontend'
    '执行阻滞诊断'        = 'execution-blockage-diagnosis'
    '技能制作器'          = 'skill-forge'
    '技能安装器'          = 'skill-installer'
    '技能库更新'          = 'skills-library-update'
    '标准答案生成'        = 'standard-answer-gen'
    '理论支撑分析'        = 'theory-support-analysis'
    '目标追问'            = 'goal-probing'
    '知识库构建'          = 'knowledge-base-builder'
    '短视频开头优化'      = 'short-video-hook-optimizer'
    '短视频脚本检查'      = 'short-video-script-check'
    '自动诊断分流'        = 'auto-triage'
    '视频内容提取'        = 'video-content-extraction'
    '设计审美前端'        = 'design-aesthetic-frontend'
    '诊断报告生成'        = 'diagnosis-report-gen'
    '诊断状态保存'        = 'diagnosis-state-save'
    '诊断状态恢复'        = 'diagnosis-state-restore'
    '长期决策跟踪'        = 'long-term-decision-tracker'
    '问题改写优化'        = 'question-rewriting'
    '项目规则迁移'        = 'project-rules-migration'
}

# Known duplicates of skills already in repo (skip these)
$DuplicateBlacklist = @('vibecoding-gsap-ad', 'gsap广告大片复刻', 'uniapp-multi-platform-audit', 'uni-app多端体验审计', 'github技术优化顾问', 'ios界面审计开发', 'web设计规范审查', '截图转前端代码', '设计审美前端', 'uni-app发版查询')

# === Logging ===
function Write-Log {
    param([string]$Msg)
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $line = "[$ts] $Msg"
    Add-Content -Path $LogFile -Value $line -Encoding UTF8
    Write-Output $line
}

# === Extract frontmatter from SKILL.md ===
function Get-Frontmatter {
    param([string]$Path)
    $content = Get-Content $Path -Raw -Encoding UTF8
    $fm = @{}
    if ($content -match '(?s)^---\s*\n(.*?)\n---') {
        foreach ($l in ($matches[1] -split "`n")) {
            if ($l -match '^(\w+):\s*(.+)$') {
                $fm[$matches[1]] = $matches[2].Trim().Trim('"')
            }
        }
    }
    return $fm
}

# === Resolve ASCII slug for a (possibly Chinese) frontmatter name ===
# Option A: identifier must stay ASCII lowercase-hyphen; the Chinese title
# is carried by the optional `label` field. Pure-Chinese names map via
# $SlugMap; ASCII-looking names are normalized (lowercase, punctuation to
# hyphens, hyphens collapsed/trimmed).
function Get-SkillSlug {
    param([string]$Name)
    if ($SlugMap.ContainsKey($Name)) { return @{ Slug = $SlugMap[$Name]; Label = $Name } }
    if ($Name -match '^[A-Za-z0-9 ./_-]+$') {
        $slug = $Name.ToLower()
        $slug = [regex]::Replace($slug, '[ ./_]', '-')
        $slug = [regex]::Replace($slug, '-{2,}', '-')
        $slug = $slug.Trim('-')
        if ($slug -match $NamePattern) { return @{ Slug = $slug; Label = $Name } }
    }
    return @{ Slug = $null; Label = $Name }  # unresolved: keep pending
}

# === Quality check ===
function Test-SkillQuality {
    param([string]$SkillDir)
    $md = Join-Path $SkillDir "SKILL.md"
    if (-not (Test-Path $md)) { return @{ Pass = $false; Reason = "No SKILL.md" } }

    $content = Get-Content $md -Raw -Encoding UTF8
    $lines = ($content -split "`n").Count
    $fm = Get-Frontmatter $md
    $name = $fm.name
    $desc = $fm.description

    if (-not $name) { return @{ Pass = $false; Reason = "Missing name in frontmatter" } }
    # Option A: normalize identifier to ASCII slug; a Chinese name must either
    # resolve via $SlugMap or it stays pending with an actionable reason.
    $resolved = Get-SkillSlug $name
    if (-not $resolved.Slug) {
        return @{ Pass = $false; Reason = "Name '$name' not in \$SlugMap — add a slug mapping, then name becomes '$($resolved.Label)' as label" }
    }
    $slug = $resolved.Slug
    if ($fm.label) { $label = $fm.label } elseif ($name -match '[\u4e00-\u9fff]') { $label = $name } else { $label = $null }
    if ($lines -lt $MinLines) { return @{ Pass = $false; Reason = "Too thin: $lines lines (min $MinLines)" } }
    if ($lines -gt $MaxLines) { return @{ Pass = $false; Reason = "$lines lines exceeds $MaxLines" } }
    if (-not $desc -or $desc.Length -lt $MinDescLength) { return @{ Pass = $false; Reason = "Description too short ($($desc.Length) chars, need $MinDescLength)" } }
    if ($desc -notmatch $TriggerPattern) { return @{ Pass = $false; Reason = "Description missing trigger keywords (use when/触发/适用于)" } }
    if ($content -match 'C:\\Users\\|/Users/[a-z]+/|/home/[a-z]+/') { return @{ Pass = $false; Reason = "Contains hardcoded local path" } }

    return @{ Pass = $true; Reason = "OK"; Slug = $slug; Label = $label; OrigName = $name; Lines = $lines; DescLen = $desc.Length }
}

# === Main ===
Write-Log "=== Daily evolve started ==="

# Get existing skill slugs in repo (Option A: dedupe on normalized slug,
# not raw name, so a Chinese source skill matching an existing slug is
# correctly treated as "already in repo").
$existing = @{}
Get-ChildItem $SkillsDir -Directory | ForEach-Object {
    $md = Join-Path $_.FullName "SKILL.md"
    if (Test-Path $md) {
        $fm = Get-Frontmatter $md
        if ($fm.name) {
            $sl = Get-SkillSlug $fm.name
            if ($sl.Slug) { $existing[$sl.Slug] = $_.Name }
        }
    }
}
Write-Log "Existing skills in repo: $($existing.Count)"

# Scan local roots
$candidates = @()
$pending = @()
foreach ($root in $LocalSkillRoots) {
    if (-not (Test-Path $root)) { continue }
    Get-ChildItem $root -Directory | ForEach-Object {
        $skillDir = $_.FullName
        $md = Join-Path $skillDir "SKILL.md"
        if (-not (Test-Path $md)) { return }
        $fm = Get-Frontmatter $md
        if (-not $fm.name) { return }
        $sl = Get-SkillSlug $fm.name
        if ($sl.Slug -and $existing.ContainsKey($sl.Slug)) { return }  # already in repo (by slug)
        # known duplicates: match on slug, folder name, or Chinese label/name
        $black = @()
        $black += @($fm.name, $_.Name)
        if ($sl.Slug) { $black += $sl.Slug }
        if ($fm.label) { $black += $fm.label }
        foreach ($b in $black) { if ($b -and $DuplicateBlacklist -contains $b) { return } }
        $quality = Test-SkillQuality $skillDir
        if ($quality.Pass) {
            $candidates += [PSCustomObject]@{ Slug = $quality.Slug; Label = $quality.Label; OrigName = $quality.OrigName; Source = $skillDir; Lines = $quality.Lines }
        } else {
            $pending += [PSCustomObject]@{ Slug = $quality.Slug; Label = $quality.Label; OrigName = $quality.OrigName; Source = $skillDir; Reason = $quality.Reason }
        }
    }
}

Write-Log "New qualifying candidates: $($candidates.Count)"
Write-Log "Pending (needs manual normalization): $($pending.Count)"

# Auto-copy qualifying candidates (Option A: directory + frontmatter use the
# ASCII slug; the Chinese title, if any, is written as `label:`).
$added = 0
foreach ($c in $candidates) {
    $dst = Join-Path $SkillsDir $c.Slug
    if (Test-Path $dst) { continue }
    Copy-Item $c.Source $dst -Recurse -Force
    # Rewrite frontmatter identifiers so the CI name gate passes:
    #   name: <ascii-slug>
    #   label: <original Chinese title>   (only when a Chinese title existed)
    $mdDst = Join-Path $dst "SKILL.md"
    $dstContent = Get-Content $mdDst -Raw -Encoding UTF8
    # 1) rewrite ONLY the first frontmatter `name:` line to the slug (count=1,
    #    so a body line that happens to start with `name:` is left alone)
    $dstContent = [regex]::Replace($dstContent, '(?m)^name:.*$', "name: $($c.Slug)", 1)
    # 2) if this skill carries a Chinese label, add `label:` right after name:
    if ($c.Label -and $c.Label -cne $c.Slug) {
        $labelLine = "name: $($c.Slug)`nlabel: $($c.Label)"
        $dstContent = [regex]::Replace($dstContent, "(?m)^name: $([regex]::Escape($c.Slug))\r?$", $labelLine, 1)
    }
    Set-Content -Path $mdDst -Value $dstContent -Encoding UTF8 -NoNewline
    # Remove personal agents/ config
    $agentsDir = Join-Path $dst "agents"
    if (Test-Path $agentsDir) { Remove-Item $agentsDir -Recurse -Force }
    $tag = if ($c.Label) { " (label: $($c.Label))" } else { "" }
    Write-Log "  ADDED: $($c.Slug)$tag ($($c.Lines) lines)"
    $added++
}

# Write pending list (Option A: show the slug mapping so each entry is
# actionable — add `Name` to $SlugMap to resolve it)
$pendingFile = Join-Path $RepoRoot "PENDING.md"
if ($pending.Count -gt 0) {
    $pendingContent = "# Pending Skills (need manual normalization)`n`n"
    $pendingContent += "| Name | Slug | Label | Reason | Source |`n|---|---|---|---|---|`n"
    foreach ($p in $pending) {
        $slug = if ($p.Slug) { $p.Slug } else { "-" }
        $label = if ($p.Label) { $p.Label } else { "-" }
        $pendingContent += "| $($p.OrigName) | $slug | $label | $($p.Reason) | $($p.Source) |`n"
    }
    Set-Content -Path $pendingFile -Value $pendingContent -Encoding UTF8
    Write-Log "Pending list written to PENDING.md ($($pending.Count) items)"
} elseif (Test-Path $pendingFile) {
    Remove-Item $pendingFile -Force
}

# Validate with npx skills
Write-Log "Running npx skills validation..."
Set-Location $RepoRoot
$validate = & npx -y skills add ./ --list 2>&1
if ($validate -match "Found (\d+) skills") {
    Write-Log "Validation passed: $($matches[1]) skills recognized"
} else {
    Write-Log "WARNING: validation output unexpected"
}

# Git commit and push
$gitStatus = git status --porcelain
if ($gitStatus) {
    git add .
    $date = Get-Date -Format "yyyy-MM-dd"
    git commit -m "daily-evolve: $date (auto-added $added skills, $($pending.Count) pending)" 2>&1 | Out-Null
    git push origin main 2>&1 | Out-Null
    Write-Log "Pushed $($gitStatus.Count) changed files"
} else {
    Write-Log "No changes to commit"
}

Write-Log "=== Daily evolve complete: added=$added, pending=$($pending.Count) ==="
Write-Output ""
Write-Output "Summary: added=$added, pending=$($pending.Count), total=$($existing.Count + $added)"
