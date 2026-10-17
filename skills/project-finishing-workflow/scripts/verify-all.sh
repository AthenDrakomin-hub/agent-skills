#!/usr/bin/env bash
# verify-all.sh — 项目交付前自动验证脚本
# 自动检测项目类型，运行 lint + test + build，任一失败即退出。
# 用法: bash verify-all.sh [项目路径]
# 退出码: 0=全绿, 1=有失败项

set -euo pipefail

PROJECT_DIR="${1:-.}"
cd "$PROJECT_DIR"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PASSED=0
FAILED=0
SKIPPED=0
FAILED_ITEMS=()

log_pass() { echo -e "${GREEN}✓ PASS${NC}: $1"; PASSED=$((PASSED + 1)); }
log_fail() { echo -e "${RED}✗ FAIL${NC}: $1"; FAILED=$((FAILED + 1)); FAILED_ITEMS+=("$1"); }
log_skip() { echo -e "${YELLOW}○ SKIP${NC}: $1"; SKIPPED=$((SKIPPED + 1)); }
log_info() { echo -e "  $1"; }

echo "=========================================="
echo "  项目交付验证 — $PROJECT_DIR"
echo "=========================================="
echo ""

# ============================================================
# 1. 检测项目类型
# ============================================================
echo "【1/5】项目类型检测"

PROJECT_TYPE="unknown"
HAS_NODE=false
HAS_PYTHON=false
HAS_JAVA=false
HAS_GO=false
HAS_RUST=false
HAS_PHP=false

if [ -f "package.json" ]; then
    HAS_NODE=true
    PROJECT_TYPE="node"
    log_info "检测到 Node.js 项目 (package.json)"
    # 读取 package.json 中的 scripts
    if command -v node &>/dev/null; then
        LINT_SCRIPT=$(node -e "const p=require('./package.json'); console.log(p.scripts?.lint||'')" 2>/dev/null || echo "")
        TEST_SCRIPT=$(node -e "const p=require('./package.json'); console.log(p.scripts?.test||'')" 2>/dev/null || echo "")
        BUILD_SCRIPT=$(node -e "const p=require('./package.json'); console.log(p.scripts?.build||'')" 2>/dev/null || echo "")
    fi
fi

if [ -f "requirements.txt" ] || [ -f "pyproject.toml" ] || [ -f "setup.py" ]; then
    HAS_PYTHON=true
    PROJECT_TYPE="python"
    log_info "检测到 Python 项目"
fi

if [ -f "pom.xml" ] || [ -f "build.gradle" ]; then
    HAS_JAVA=true
    PROJECT_TYPE="java"
    log_info "检测到 Java 项目"
fi

if [ -f "go.mod" ]; then
    HAS_GO=true
    PROJECT_TYPE="go"
    log_info "检测到 Go 项目"
fi

if [ -f "Cargo.toml" ]; then
    HAS_RUST=true
    PROJECT_TYPE="rust"
    log_info "检测到 Rust 项目"
fi

if [ -f "composer.json" ]; then
    HAS_PHP=true
    PROJECT_TYPE="php"
    log_info "检测到 PHP 项目"
fi

if [ "$PROJECT_TYPE" = "unknown" ]; then
    log_skip "未识别到已知项目类型，跳过自动化验证"
    echo ""
    echo "=========================================="
    echo "  结果: SKIPPED (未知项目类型)"
    echo "=========================================="
    exit 0
fi

echo ""

# ============================================================
# 2. 依赖检查
# ============================================================
echo "【2/5】依赖完整性检查"

if [ "$HAS_NODE" = true ]; then
    if [ -d "node_modules" ]; then
        log_pass "node_modules 存在"
    else
        log_fail "node_modules 不存在，请先运行 npm install"
    fi
    if [ -f "package-lock.json" ] || [ -f "yarn.lock" ] || [ -f "pnpm-lock.yaml" ]; then
        log_pass "依赖锁文件存在"
    else
        log_skip "无依赖锁文件（建议生成）"
    fi
fi

if [ "$HAS_PYTHON" = true ]; then
    if [ -d "venv" ] || [ -d ".venv" ] || command -v python3 &>/dev/null; then
        log_pass "Python 环境可用"
    else
        log_fail "未检测到 Python 虚拟环境"
    fi
fi

echo ""

# ============================================================
# 3. Lint / 静态检查
# ============================================================
echo "【3/5】Lint / 静态检查"

if [ "$HAS_NODE" = true ]; then
    if [ -n "$LINT_SCRIPT" ]; then
        log_info "运行: npm run lint"
        if npm run lint --silent 2>&1 | tail -20; then
            log_pass "ESLint/TSLint 通过"
        else
            log_fail "Lint 未通过"
        fi
    else
        log_skip "package.json 中无 lint 脚本"
    fi

    # TypeScript 类型检查
    if [ -f "tsconfig.json" ]; then
        log_info "运行: npx tsc --noEmit"
        if npx tsc --noEmit 2>&1 | tail -20; then
            log_pass "TypeScript 类型检查通过"
        else
            log_fail "TypeScript 类型错误"
        fi
    fi
fi

if [ "$HAS_PYTHON" = true ]; then
    if command -v flake8 &>/dev/null; then
        log_info "运行: flake8"
        if flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics 2>&1 | tail -10; then
            log_pass "flake8 语法检查通过"
        else
            log_fail "flake8 发现语法错误"
        fi
    elif command -v ruff &>/dev/null; then
        log_info "运行: ruff check"
        if ruff check . 2>&1 | tail -10; then
            log_pass "ruff 检查通过"
        else
            log_fail "ruff 发现问题"
        fi
    else
        log_skip "未安装 flake8/ruff，跳过 Python lint"
    fi
fi

if [ "$HAS_GO" = true ]; then
    if command -v go &>/dev/null; then
        log_info "运行: go vet"
        if go vet ./... 2>&1 | tail -10; then
            log_pass "go vet 通过"
        else
            log_fail "go vet 发现问题"
        fi
    fi
fi

echo ""

# ============================================================
# 4. 测试
# ============================================================
echo "【4/5】测试运行"

if [ "$HAS_NODE" = true ]; then
    if [ -n "$TEST_SCRIPT" ]; then
        log_info "运行: npm test"
        if npm test --silent 2>&1 | tail -30; then
            log_pass "测试全部通过"
        else
            log_fail "测试未通过"
        fi
    else
        log_skip "package.json 中无 test 脚本"
    fi
fi

if [ "$HAS_PYTHON" = true ]; then
    if command -v pytest &>/dev/null; then
        log_info "运行: pytest"
        if pytest -v --tb=short 2>&1 | tail -30; then
            log_pass "pytest 全部通过"
        else
            log_fail "pytest 有失败用例"
        fi
    elif command -v python3 &>/dev/null && python3 -m unittest discover 2>&1 | head -5 | grep -q .; then
        log_info "运行: python -m unittest"
        if python3 -m unittest discover -v 2>&1 | tail -20; then
            log_pass "unittest 全部通过"
        else
            log_fail "unittest 有失败用例"
        fi
    else
        log_skip "未安装 pytest/unittest，跳过 Python 测试"
    fi
fi

if [ "$HAS_GO" = true ]; then
    if command -v go &>/dev/null; then
        log_info "运行: go test ./..."
        if go test ./... -v 2>&1 | tail -30; then
            log_pass "Go 测试全部通过"
        else
            log_fail "Go 测试有失败"
        fi
    fi
fi

if [ "$HAS_JAVA" = true ]; then
    if [ -f "pom.xml" ] && command -v mvn &>/dev/null; then
        log_info "运行: mvn test"
        if mvn test -q 2>&1 | tail -20; then
            log_pass "Maven 测试通过"
        else
            log_fail "Maven 测试失败"
        fi
    fi
fi

echo ""

# ============================================================
# 5. 构建
# ============================================================
echo "【5/5】构建验证"

if [ "$HAS_NODE" = true ]; then
    if [ -n "$BUILD_SCRIPT" ]; then
        log_info "运行: npm run build"
        if npm run build --silent 2>&1 | tail -20; then
            log_pass "构建成功"
            # 检查构建产物
            if [ -d "dist" ] || [ -d "build" ] || [ -d ".next" ]; then
                log_pass "构建产物存在"
            else
                log_skip "未检测到构建产物目录"
            fi
        else
            log_fail "构建失败"
        fi
    else
        log_skip "package.json 中无 build 脚本"
    fi
fi

if [ "$HAS_PYTHON" = true ]; then
    if [ -f "setup.py" ] || [ -f "pyproject.toml" ]; then
        log_info "运行: python -m build"
        if python3 -m build 2>&1 | tail -10; then
            log_pass "Python 包构建成功"
        else
            log_fail "Python 包构建失败"
        fi
    else
        log_skip "Python 项目无需构建（纯脚本）"
    fi
fi

if [ "$HAS_GO" = true ]; then
    if command -v go &>/dev/null; then
        log_info "运行: go build ./..."
        if go build ./... 2>&1 | tail -10; then
            log_pass "Go 构建成功"
        else
            log_fail "Go 构建失败"
        fi
    fi
fi

if [ "$HAS_JAVA" = true ]; then
    if [ -f "pom.xml" ] && command -v mvn &>/dev/null; then
        log_info "运行: mvn package -DskipTests"
        if mvn package -DskipTests -q 2>&1 | tail -10; then
            log_pass "Maven 打包成功"
        else
            log_fail "Maven 打包失败"
        fi
    fi
fi

echo ""

# ============================================================
# 汇总
# ============================================================
echo "=========================================="
echo "  验证结果汇总"
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
    echo -e "${RED}❌ 验证未通过，有 $FAILED 项失败，请修复后重新运行。${NC}"
    exit 1
else
    echo -e "${GREEN}✅ 全部验证通过！项目可以交付。${NC}"
    exit 0
fi
