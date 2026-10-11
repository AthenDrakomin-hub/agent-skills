#!/usr/bin/env bash
# Git pre-commit hook: scan staged files for secrets and sensitive patterns.
# Install: cp scripts/pre-commit-hook.sh .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

BLOCKED=0

# Get list of staged files (excluding deleted files)
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM)

if [ -z "$STAGED_FILES" ]; then
    exit 0
fi

echo -e "${YELLOW}[git-safety-guard] Scanning staged files for secrets...${NC}"

# 1. Blocked file extensions / names
BLOCKED_PATTERNS=(
    '\.env$' '\.env\.' '\.key$' '\.pem$' '\.p12$' '\.pfx$' '\.jks$'
    'id_rsa' 'id_ed25519' '\.cer$' '\.crt$' 'credentials\.json'
    'service-account\.json' '\.secret$' '\.secrets$'
)

for file in $STAGED_FILES; do
    for pattern in "${BLOCKED_PATTERNS[@]}"; do
        if echo "$file" | grep -qE "$pattern"; then
            # Allow .env.example
            if echo "$file" | grep -q '\.env\.example'; then
                continue
            fi
            echo -e "${RED}  BLOCKED (sensitive file): $file${NC}"
            BLOCKED=1
        fi
    done
done

# 2. Content pattern scan
SECRET_PATTERNS=(
    'AKIA[0-9A-Z]{16}'
    'gh[pousr]_[A-Za-z0-9]{36}'
    '-----BEGIN.*PRIVATE KEY-----'
    'sk-[A-Za-z0-9]{20,}'
    'xox[baprs]-[A-Za-z0-9-]{10,}'
    'AIza[0-9A-Za-z\-_]{35}'
    'hooks\.slack\.com/services/'
)

for file in $STAGED_FILES; do
    # Skip binary files
    if git diff --cached --numstat | grep -q "^-\s*-.*$file"; then
        continue
    fi
    for pattern in "${SECRET_PATTERNS[@]}"; do
        MATCH=$(git diff --cached -- "$file" | grep -E "^\+.*$pattern" || true)
        if [ -n "$MATCH" ]; then
            echo -e "${RED}  BLOCKED (secret pattern in $file):${NC}"
            echo "$MATCH" | head -3 | sed 's/^/    /'
            BLOCKED=1
        fi
    done
done

# 3. .gitignore existence check
if [ ! -f ".gitignore" ]; then
    echo -e "${YELLOW}  WARNING: No .gitignore found in repository root${NC}"
fi

if [ "$BLOCKED" -eq 1 ]; then
    echo ""
    echo -e "${RED}[git-safety-guard] Commit blocked. Remove secrets or use git update-index --assume-unchanged for specific files.${NC}"
    echo -e "${YELLOW}  If this is a false positive, add '# pragma: allowlist secret' inline or skip with: git commit --no-verify${NC}"
    exit 1
fi

echo -e "${GREEN}[git-safety-guard] Scan passed. No secrets detected.${NC}"
exit 0
