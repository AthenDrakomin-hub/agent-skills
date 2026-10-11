# REA 逆向工程环境检测脚本
# 用法: powershell -ExecutionPolicy Bypass -File check-env.ps1
# 检测 Node.js、REA CLI、逆向引擎（Ghidra/IDA/Hopper/JADX）、JDK、Chrome 等

$ErrorActionPreference = "SilentlyContinue"
$results = @()

function Add-Result {
    param(
        [string]$Category,
        [string]$Item,
        [string]$Status,   # OK / WARN / FAIL / INFO
        [string]$Detail
    )
    $script:results += [PSCustomObject]@{
        Category = $Category
        Item     = $Item
        Status   = $Status
        Detail   = $Detail
    }
}

function Test-Command {
    param([string]$Command)
    return [bool](Get-Command $Command -ErrorAction SilentlyContinue)
}

function Get-VersionOrNull {
    param([string]$Command, [string]$Arg = "--version")
    try {
        $output = & $Command $Arg 2>&1
        if ($output) { return ($output | Select-Object -First 1).ToString().Trim() }
    } catch {}
    return $null
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  REA Reverse Engineering - Environment Check" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# === 1. Node.js ===
$nodeVersion = Get-VersionOrNull "node"
if ($nodeVersion) {
    # 解析版本号
    if ($nodeVersion -match 'v?(\d+)\.(\d+)\.(\d+)') {
        $major = [int]$Matches[1]
        $minor = [int]$Matches[2]
        if ($major -ge 22 -and $minor -ge 19 -or $major -ge 24 -or $major -ge 26) {
            Add-Result "Runtime" "Node.js" "OK" "$nodeVersion (满足 >= 22.19 要求)"
        } elseif ($major -ge 22) {
            Add-Result "Runtime" "Node.js" "WARN" "$nodeVersion (需 >= 22.19，当前小版本不足，建议升级)"
        } else {
            Add-Result "Runtime" "Node.js" "FAIL" "$nodeVersion (需 >= 22.19，当前主版本过低)"
        }
    } else {
        Add-Result "Runtime" "Node.js" "WARN" "版本解析失败: $nodeVersion"
    }
} else {
    Add-Result "Runtime" "Node.js" "FAIL" "未安装。REA 需要 Node.js >= 22.19"
}

# === 2. npm ===
$npmVersion = Get-VersionOrNull "npm"
if ($npmVersion) {
    Add-Result "Runtime" "npm" "OK" $npmVersion
} else {
    Add-Result "Runtime" "npm" "FAIL" "未安装（通常随 Node.js 一起安装）"
}

# === 3. REA CLI ===
$reaVersion = Get-VersionOrNull "rea"
if ($reaVersion) {
    Add-Result "REA" "rea CLI" "OK" "$reaVersion (全局安装)"
} else {
    # 检查 npm 全局包
    $globalPkgs = & npm list -g rea-agents --depth=0 2>&1
    if ($globalPkgs -match "rea-agents@") {
        Add-Result "REA" "rea-agents" "OK" "已全局安装（npm 包），但 rea 命令不在 PATH 中"
    } else {
        Add-Result "REA" "rea CLI" "WARN" "未全局安装。可用 npx -y rea-agents@latest [command] 临时调用，或运行: npm install --global rea-agents"
    }
}

# === 4. MCP 配置检测（常见代理配置文件）===
$mcpConfigured = $false
$mcpLocations = @(
    "$env:USERPROFILE\.claude.json",
    "$env:USERPROFILE\.cursor\mcp.json",
    "$env:APPDATA\Cursor\User\mcp.json",
    "$env:USERPROFILE\.codex\config.toml",
    "$env:USERPROFILE\.gemini\config.json"
)
foreach ($loc in $mcpLocations) {
    if (Test-Path $loc) {
        $content = Get-Content $loc -Raw -ErrorAction SilentlyContinue
        if ($content -match "rea-agents|rea") {
            $mcpConfigured = $true
            Add-Result "REA" "MCP 配置" "OK" "已在 $loc 中检测到 REA 配置"
            break
        }
    }
}
if (-not $mcpConfigured) {
    Add-Result "REA" "MCP 配置" "INFO" "未检测到已配置的 MCP。运行: npx rea-agents@latest setup 来注册 REA 到 AI 代理"
}

# === 5. 原生逆向引擎 ===
# Ghidra
$ghidraFound = $false
$ghidraPaths = @(
    "C:\Program Files\ghidra\*\ghidraRun.bat",
    "C:\ghidra\*\ghidraRun.bat",
    "$env:USERPROFILE\ghidra\*\ghidraRun.bat",
    "C:\tools\ghidra\*\ghidraRun.bat"
)
foreach ($p in $ghidraPaths) {
    $found = Get-ChildItem $p -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($found) {
        Add-Result "Native Engine" "Ghidra" "OK" "找到: $($found.FullName)"
        $ghidraFound = $true
        break
    }
}
if (-not $ghidraFound) {
    if (Test-Command "ghidraRun") {
        Add-Result "Native Engine" "Ghidra" "OK" "在 PATH 中找到 ghidraRun"
    } else {
        Add-Result "Native Engine" "Ghidra" "WARN" "未找到。Ghidra 是免费开源的原生分析引擎（NSA 出品）。下载: https://ghidra-sre.org/  （原生二进制分析需要）"
    }
}

# IDA Pro
$idaFound = $false
$idaPaths = @(
    "C:\Program Files\IDA Professional*\ida64.exe",
    "C:\Program Files\IDA*\ida64.exe",
    "C:\IDA*\ida64.exe"
)
foreach ($p in $idaPaths) {
    $found = Get-ChildItem $p -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($found) {
        Add-Result "Native Engine" "IDA Pro" "OK" "找到: $($found.FullName)"
        $idaFound = $true
        break
    }
}
if (-not $idaFound) {
    Add-Result "Native Engine" "IDA Pro" "INFO" "未找到（商业软件，非必需。Ghidra 可作为免费替代）"
}

# Hopper（Windows 不支持，仅提示）
Add-Result "Native Engine" "Hopper" "INFO" "Windows 平台不支持 Hopper（仅 macOS）。macOS 用户可让 REA setup 自动安装"

# === 6. Android APK 分析 ===
# Java/JDK
$javaVersion = Get-VersionOrNull "java"
if ($javaVersion) {
    Add-Result "Android" "JDK" "OK" $javaVersion
} else {
    Add-Result "Android" "JDK" "WARN" "未找到。APK 分析需要 JDK 17+。下载: https://adoptium.net/"
}

# JADX
$jadxFound = $false
if (Test-Command "jadx") {
    Add-Result "Android" "JADX" "OK" "在 PATH 中找到 jadx"
    $jadxFound = $true
} else {
    $jadxPaths = @(
        "C:\jadx\*\bin\jadx.bat",
        "C:\tools\jadx\*\bin\jadx.bat",
        "$env:USERPROFILE\jadx\*\bin\jadx.bat"
    )
    foreach ($p in $jadxPaths) {
        $found = Get-ChildItem $p -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($found) {
            Add-Result "Android" "JADX" "OK" "找到: $($found.FullName)"
            $jadxFound = $true
            break
        }
    }
}
if (-not $jadxFound) {
    Add-Result "Android" "JADX" "WARN" "未找到。REA setup 可能自动下载 JADX。也可手动下载: https://github.com/skylot/jadx/releases  （APK 分析需要）"
}

# === 7. 固件分析（Windows 不支持 Binwalk）===
Add-Result "Firmware" "Binwalk/Unblob" "INFO" "Windows 原生不支持。固件分析需在 Linux 或 WSL2 中进行"

# === 8. 网站分析（Chrome）===
$chromeFound = $false
$chromePaths = @(
    "C:\Program Files\Google\Chrome\Application\chrome.exe",
    "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    "$env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe"
)
foreach ($p in $chromePaths) {
    if (Test-Path $p) {
        Add-Result "Website" "Chrome" "OK" "找到: $p"
        $chromeFound = $true
        break
    }
}
if (-not $chromeFound) {
    if (Test-Command "chrome") {
        Add-Result "Website" "Chrome" "OK" "在 PATH 中找到"
    } else {
        Add-Result "Website" "Chrome" "WARN" "未找到 Chrome。网站分析需要 Chrome 系浏览器"
    }
}

# === 9. 平台信息 ===
$os = (Get-CimInstance Win32_OperatingSystem).Caption
$arch = $env:PROCESSOR_ARCHITECTURE
Add-Result "System" "OS" "INFO" "$os ($arch)"

# === 输出结果 ===
Write-Host ""
Write-Host "=== 检测结果 ===" -ForegroundColor Cyan
Write-Host ""

foreach ($r in $results) {
    $color = switch ($r.Status) {
        "OK"   { "Green" }
        "WARN" { "Yellow" }
        "FAIL" { "Red" }
        "INFO" { "Gray" }
        default { "White" }
    }
    $symbol = switch ($r.Status) {
        "OK"   { "[PASS]" }
        "WARN" { "[WARN]" }
        "FAIL" { "[FAIL]" }
        "INFO" { "[INFO]" }
        default { "[????]" }
    }
    Write-Host ("{0,-7} {1,-16} {2}" -f $symbol, $r.Item, $r.Detail) -ForegroundColor $color
}

# === 汇总 ===
Write-Host ""
$okCount   = ($results | Where-Object { $_.Status -eq "OK" }).Count
$warnCount = ($results | Where-Object { $_.Status -eq "WARN" }).Count
$failCount = ($results | Where-Object { $_.Status -eq "FAIL" }).Count
$infoCount = ($results | Where-Object { $_.Status -eq "INFO" }).Count

Write-Host "汇总: $okCount 通过, $warnCount 警告, $failCount 失败, $infoCount 信息" -ForegroundColor Cyan
Write-Host ""

# === 快速开始建议 ===
Write-Host "=== 快速开始 ===" -ForegroundColor Cyan
if ($failCount -gt 0) {
    Write-Host "1. 先解决 [FAIL] 项（主要是 Node.js 版本）" -ForegroundColor Yellow
}
Write-Host "2. 安装 REA: npx rea-agents@latest setup" -ForegroundColor White
Write-Host "3. 重启 AI 代理以加载 MCP 配置" -ForegroundColor White
Write-Host "4. 原生二进制分析需安装 Ghidra（免费）: https://ghidra-sre.org/" -ForegroundColor White
Write-Host "5. JS/Electron/.NET 分析无需额外引擎，可直接开始" -ForegroundColor White
Write-Host ""

# 返回 JSON 供程序解析
$jsonOutput = $results | ConvertTo-Json -Depth 3
Write-Output $jsonOutput
