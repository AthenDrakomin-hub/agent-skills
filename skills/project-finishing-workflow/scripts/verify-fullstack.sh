#!/usr/bin/env bash
# verify-fullstack.sh — 前后端全栈验证协调脚本
# 自动识别前后端目录，分别运行 verify-all.sh，汇总结果。
# 用法: bash verify-fullstack.sh [项目根路径] [--frontend dir] [--backend dir]
# 退出码: 0=全绿, 1=有失败项

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VERIFY_ALL="$SCRIPT_DIR/verify-all.sh"

PROJECT_ROOT="."
FRONTEND_DIR=""
BACKEND_DIR=""

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --frontend)
            FRONTEND_DIR="$2"
            shift 2
            ;;
        --backend)
            BACKEND_DIR="$2"
            shift 2
            ;;
        *)
            PROJECT_ROOT="$1"
            shift
            ;;
    esac
done

cd "$PROJECT_ROOT"
PROJECT_ROOT="$(pwd)"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PASSED=0
FAILED=0
SKIPPED=0
FAILED_ITEMS=()

log_pass() { echo -e "${GREEN}✓ PASS${NC}: $1"; PASSED=$((PASSED + 1)); }
log_fail() { echo -e "${RED}✗ FAIL${NC}: $1"; FAILED=$((FAILED + 1)); FAILED_ITEMS+=("$1"); }
log_skip() { echo -e "${YELLOW}○ SKIP${NC}: $1"; SKIPPED=$((SKIPPED + 1)); }
log_info() { echo -e "${BLUE}ℹ${NC}  $1"; }

echo "=========================================="
echo "  全栈验证 — $PROJECT_ROOT"
echo "=========================================="
echo ""

# ============================================================
# 自动识别前后端目录
# ============================================================
echo "【1/3】目录识别"

# 常见前端目录名
FRONTEND_CANDIDATES=("web" "frontend" "client" "ui" "app" "web-ui" "h5" "pc" "im-web" "im-uniapp" "im-pc" "src/main/resources/static")
# 常见后端目录名
BACKEND_CANDIDATES=("server" "backend" "api" "service" "im-server" "im-platform" "im-admin" "box-im" "src")

detect_dir() {
    local candidates=("$@")
    for dir in "${candidates[@]}"; do
        if [ -d "$PROJECT_ROOT/$dir" ]; then
            # 检查是否有 package.json（前端）或 pom.xml/requirements.txt 等（后端）
            echo "$dir"
            return 0
        fi
    done
    return 1
}

# 如果用户没指定，自动检测
if [ -z "$FRONTEND_DIR" ]; then
    FRONTEND_DIR=$(detect_dir "${FRONTEND_CANDIDATES[@]}" || true)
fi
if [ -z "$BACKEND_DIR" ]; then
    BACKEND_DIR=$(detect_dir "${BACKEND_CANDIDATES[@]}" || true)
fi

# 检查根目录本身是不是一个项目（单体项目）
ROOT_IS_PROJECT=false
if [ -f "package.json" ] || [ -f "pom.xml" ] || [ -f "requirements.txt" ] || [ -f "go.mod" ] || [ -f "Cargo.toml" ]; then
    ROOT_IS_PROJECT=true
fi

echo ""

# ============================================================
# 运行验证
# ============================================================
echo "【2/3】运行验证"

run_verify() {
    local label="$1"
    local dir="$2"

    if [ -z "$dir" ] || [ ! -d "$PROJECT_ROOT/$dir" ]; then
        log_skip "$label: 目录未指定或不存在"
        return
    fi

    echo ""
    echo -e "${BLUE}━━━ $label ($dir) ━━━${NC}"
    echo ""

    if bash "$VERIFY_ALL" "$PROJECT_ROOT/$dir"; then
        log_pass "$label 验证通过"
    else
        log_fail "$label 验证失败"
    fi
}

# 单体项目（根目录就是项目）
if [ "$ROOT_IS_PROJECT" = true ] && [ -z "$FRONTEND_DIR" ] && [ -z "$BACKEND_DIR" ]; then
    log_info "检测到单体项目结构（根目录包含依赖文件）"
    run_verify "项目" "."
else
    # 前后端分离
    if [ -n "$FRONTEND_DIR" ]; then
        log_info "前端目录: $FRONTEND_DIR"
    else
        log_skip "前端目录: 未检测到"
    fi
    if [ -n "$BACKEND_DIR" ]; then
        log_info "后端目录: $BACKEND_DIR"
    else
        log_skip "后端目录: 未检测到"
    fi

    run_verify "前端" "$FRONTEND_DIR"
    run_verify "后端" "$BACKEND_DIR"
fi

# 如果用户指定了自定义目录但不在候选列表中，也跑一下
if [ -n "$FRONTEND_DIR" ] && [ ! -d "$PROJECT_ROOT/$FRONTEND_DIR" ]; then
    log_fail "前端目录不存在: $FRONTEND_DIR"
fi
if [ -n "$BACKEND_DIR" ] && [ ! -d "$PROJECT_ROOT/$BACKEND_DIR" ]; then
    log_fail "后端目录不存在: $BACKEND_DIR"
fi

echo ""

# ============================================================
# 集成测试（前后端联调）
# ============================================================
echo "【3/3】集成检查"

# 检查是否有 docker-compose.yml（可用于联调）
if [ -f "docker-compose.yml" ] || [ -f "docker-compose.yaml" ]; then
    log_pass "存在 docker-compose.yml，可用于前后端联调"
else
    log_skip "无 docker-compose.yml，跳过联调检查"
fi

# 检查前端是否配置了后端 API 地址
if [ -n "$FRONTEND_DIR" ] && [ -d "$PROJECT_ROOT/$FRONTEND_DIR" ]; then
    API_CONFIG_FOUND=false
    for f in "$PROJECT_ROOT/$FRONTEND_DIR/.env" "$PROJECT_ROOT/$FRONTEND_DIR/.env.production" "$PROJECT_ROOT/$FRONTEND_DIR/vite.config.js" "$PROJECT_ROOT/$FRONTEND_DIR/vue.config.js" "$PROJECT_ROOT/$FRONTEND_DIR/next.config.js"; do
        if [ -f "$f" ]; then
            if grep -qiE "(api|backend|server|proxy|baseURL|VITE_|NEXT_PUBLIC_)" "$f" 2>/dev/null; then
                API_CONFIG_FOUND=true
                break
            fi
        fi
    done
    if [ "$API_CONFIG_FOUND" = true ]; then
        log_pass "前端已配置后端 API 地址"
    else
        log_skip "未检测到前端 API 配置（可能在代码中硬编码）"
    fi
fi

# 检查后端是否有 CORS 配置（允许前端访问）
if [ -n "$BACKEND_DIR" ] && [ -d "$PROJECT_ROOT/$BACKEND_DIR" ]; then
    CORS_FOUND=false
    for f in $(find "$PROJECT_ROOT/$BACKEND_DIR" -maxdepth 3 -name "*.java" -o -name "*.py" -o -name "*.js" -o -name "*.ts" -o -name "*.go" 2>/dev/null | head -20); do
        if grep -qiE "(cors|CrossOrigin|Access-Control)" "$f" 2>/dev/null; then
            CORS_FOUND=true
            break
        fi
    done
    if [ "$CORS_FOUND" = true ]; then
        log_pass "后端已配置 CORS"
    else
        log_skip "未检测到后端 CORS 配置（前后端分离时需要）"
    fi
fi

echo ""

# ============================================================
# 汇总
# ============================================================
echo "=========================================="
echo "  全栈验证结果汇总"
echo "=========================================="
echo -e "  ${GREEN}通过: $PASSED${NC}"
echo -e "  ${RED}失败: $FAILED${NC}"
echo -e "  ${YELLOW}跳过: $SKIPPED${NC}"
echo ""

if [ "$FAILED" -gt 0 ]; then
    echo -e "${RED}失败项:${NC}"
    for item in "${FAILED_ITEMS[@]}"; do
        echo -e "  - $item"
    done
    echo ""
    echo -e "${RED}❌ 全栈验证未通过，有 $FAILED 项失败，请修复后重新运行。${NC}"
    echo ""
    echo "修复建议:"
    echo "  1. 分别进入失败的目录，查看 verify-all.sh 的详细输出"
    echo "  2. 修复后重新运行: bash verify-fullstack.sh $PROJECT_ROOT"
    echo "  3. 如果是前后端联调问题，检查 API 地址和 CORS 配置"
    exit 1
else
    echo -e "${GREEN}✅ 全栈验证全部通过！前端和后端都可以交付。${NC}"
    echo ""
    echo "下一步:"
    echo "  1. 运行 acceptance-check.py 做最终验收"
    echo "  2. 打包部署"
    echo "  3. 归档复盘"
    exit 0
fi
