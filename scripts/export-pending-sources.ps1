# export-pending-sources.ps1
# Runs on the AUTHOR'S Windows machine (where the PENDING source dirs live).
# Exports every PENDING source skill directory into ./pending-sources/<name>/
# so the repo can be committed and migrated on any machine (e.g. the CI
# container) via:  python3 scripts/migrate-pending.py --stage pending-sources
#
# Reads the same PENDING.md Source column that daily-evolve.ps1 wrote.
# Skips dirs that no longer exist (warns, keeps going).

$ErrorActionPreference = "Stop"
$RepoRoot = if ($env:SKILL_REPO_ROOT) { $env:SKILL_REPO_ROOT } else { Split-Path -Parent $PSScriptRoot }
$Pending  = Join-Path $RepoRoot "PENDING.md"
$OutRoot  = Join-Path $RepoRoot "pending-sources"

if (-not (Test-Path $Pending)) { Write-Output "No PENDING.md at $Pending — nothing to export."; exit 0 }

# Parse source paths from the PENDING table (last column of each | row)
$sourcePaths = @()
Get-Content $Pending | ForEach-Object {
    $line = $_
    if ($line -match '^\|\s*[^|]+\s*\|' -and $line -notmatch '^\|\s*(Name|---)') {
        # -split takes a REGEX: bare '|' means "empty-or-empty" and shreds the
        # line into single characters, so $cells[-1] never matches a path.
        # Escaped '\|' splits on the literal pipe. (Reported on PS 5.1.)
        $cells = $line.Trim().Trim('|') -split '\|' | ForEach-Object { $_.Trim() }
        $last = $cells[-1]
        if ($last -and ($last -match '^[A-Za-z]:\\' -or $last -match '^/')) { $sourcePaths += $last }
    }
}
$sourcePaths = $sourcePaths | Select-Object -Unique

if (-not (Test-Path $OutRoot)) { New-Item -ItemType Directory -Path $OutRoot | Out-Null }

$exported = 0
$missing  = @()
foreach ($p in $sourcePaths) {
    if (-not (Test-Path $p)) { $missing += $p; continue }
    $dst = Join-Path $OutRoot (Split-Path $p -Leaf)
    if (Test-Path $dst) { Remove-Item $dst -Recurse -Force }
    Copy-Item $p $dst -Recurse -Force
    # strip personal agents/ config before shipping into the repo
    $agents = Join-Path $dst "agents"
    if (Test-Path $agents) { Remove-Item $agents -Recurse -Force }
    $exported++
}

Write-Output "Exported $exported source skill dir(s) to $OutRoot"
if ($missing.Count -gt 0) {
    Write-Output "Missing on this machine ($($missing.Count)) — still recorded in PENDING.md:"
    $missing | ForEach-Object { Write-Output "  $_" }
}

# Next steps (on the machine that receives the repo):
#   git add -f pending-sources   # force-add: dir is gitignored by default
#   git commit -m "pending-sources: export for migration"
#   git push
#   python3 scripts/migrate-pending.py --stage pending-sources
#   # after PENDING.md is empty: delete pending-sources/ (gitignore entry stays)
