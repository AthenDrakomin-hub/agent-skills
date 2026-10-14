# daily-evolve.ps1
# Daily skill repository evolution script
# Scans local skill directories, auto-includes qualifying new skills, validates, and pushes.

$ErrorActionPreference = "Stop"

# === Configuration ===
$RepoRoot = "C:\Users\88903\Desktop\skill"
$SkillsDir = Join-Path $RepoRoot "skills"
$LogFile = Join-Path $RepoRoot "evolve.log"

$LocalSkillRoots = @(
    "C:\Users\88903\AppData\Local\DoubaoWork\User Data\Default\.doubaowork\agent_mode\workspace\.user_skills",
    "C:\Users\88903\DoubaoWork\skills",
    "C:\Users\88903\.agents\skills"
)

# Quality thresholds (raised to avoid thin/duplicate skills)
$MaxLines = 500
$MinLines = 80
$MinDescLength = 150
$NamePattern = '^[a-z][a-z0-9-]*[a-z0-9]$'
$TriggerPattern = 'use when|triggers?|触发|适用于|Use when'

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
    if ($name -notmatch $NamePattern) { return @{ Pass = $false; Reason = "Name '$name' not lowercase-hyphen format" } }
    if ($lines -lt $MinLines) { return @{ Pass = $false; Reason = "Too thin: $lines lines (min $MinLines)" } }
    if ($lines -gt $MaxLines) { return @{ Pass = $false; Reason = "$lines lines exceeds $MaxLines" } }
    if (-not $desc -or $desc.Length -lt $MinDescLength) { return @{ Pass = $false; Reason = "Description too short ($($desc.Length) chars, need $MinDescLength)" } }
    if ($desc -notmatch $TriggerPattern) { return @{ Pass = $false; Reason = "Description missing trigger keywords (use when/触发/适用于)" } }
    if ($content -match 'C:\\Users\\|/Users/[a-z]+/|/home/[a-z]+/') { return @{ Pass = $false; Reason = "Contains hardcoded local path" } }

    return @{ Pass = $true; Reason = "OK"; Name = $name; Lines = $lines; DescLen = $desc.Length }
}

# === Main ===
Write-Log "=== Daily evolve started ==="

# Get existing skill names in repo
$existing = @{}
Get-ChildItem $SkillsDir -Directory | ForEach-Object {
    $md = Join-Path $_.FullName "SKILL.md"
    if (Test-Path $md) {
        $fm = Get-Frontmatter $md
        if ($fm.name) { $existing[$fm.name] = $_.Name }
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
        if ($existing.ContainsKey($fm.name)) { return }  # already in repo
        if ($DuplicateBlacklist -contains $fm.name -or $DuplicateBlacklist -contains $_.Name) { return }  # known duplicate
        $quality = Test-SkillQuality $skillDir
        if ($quality.Pass) {
            $candidates += [PSCustomObject]@{ Name = $fm.name; Source = $skillDir; Lines = $quality.Lines }
        } else {
            $pending += [PSCustomObject]@{ Name = $fm.name; Source = $skillDir; Reason = $quality.Reason }
        }
    }
}

Write-Log "New qualifying candidates: $($candidates.Count)"
Write-Log "Pending (needs manual normalization): $($pending.Count)"

# Auto-copy qualifying candidates
$added = 0
foreach ($c in $candidates) {
    $dst = Join-Path $SkillsDir $c.Name
    if (Test-Path $dst) { continue }
    Copy-Item $c.Source $dst -Recurse -Force
    # Remove personal agents/ config
    $agentsDir = Join-Path $dst "agents"
    if (Test-Path $agentsDir) { Remove-Item $agentsDir -Recurse -Force }
    Write-Log "  ADDED: $($c.Name) ($($c.Lines) lines)"
    $added++
}

# Write pending list
$pendingFile = Join-Path $RepoRoot "PENDING.md"
if ($pending.Count -gt 0) {
    $pendingContent = "# Pending Skills (need manual normalization)`n`n"
    $pendingContent += "| Name | Reason | Source |`n|---|---|---|`n"
    foreach ($p in $pending) {
        $pendingContent += "| $($p.Name) | $($p.Reason) | $($p.Source) |`n"
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
