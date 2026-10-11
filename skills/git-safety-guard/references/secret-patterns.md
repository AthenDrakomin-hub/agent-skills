# Secret Pattern Reference

Extended regex patterns for detecting secrets in staged files. Use with `grep -E` or equivalent.

## Cloud Provider Keys

### AWS
```
AKIA[0-9A-Z]{16}           # Access Key ID
ASIA[0-9A-Z]{16}           # Temporary Access Key ID
aws_secret_access_key["'\s:=]+[A-Za-z0-9/+=]{40}
```

### Google Cloud
```
AIza[0-9A-Za-z\-_]{35}     # API Key
"private_key":\s*"-----BEGIN PRIVATE KEY-----[^"]+"
```

### Azure
```
DefaultEndpointsProtocol=https;AccountKey=[A-Za-z0-9+/=]{86}
```

## Version Control / API Tokens
```
gh[pousr]_[A-Za-z0-9]{36}                # GitHub PAT
glpat-[A-Za-z0-9\-_]{20}                 # GitLab PAT
xox[baprs]-[A-Za-z0-9-]{10,}            # Slack token
sk-[A-Za-z0-9]{20,}                      # OpenAI API key
rk_[A-Za-z0-9]{20,}                      # Replicate API key
```

## Private Keys & Certificates
```
-----BEGIN (RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY-----
-----BEGIN CERTIFICATE-----
```

## Database Connection Strings (with embedded credentials)
```
mysql://[^:]+:[^@]+@[^\s"']+
postgres(ql)?://[^:]+:[^@]+@[^\s"']+
mongodb(\+srv)?://[^:]+:[^@]+@[^\s"']+
redis://:[^@]+@[^\s"']+
```

## Webhooks
```
https://hooks\.slack\.com/services/[A-Za-z0-9/]+
https://discord\.com/api/webhooks/\d+/[A-Za-z0-9_-]+
```

## Generic High-Entropy Assignments
```
(api[_-]?key|secret|token|password|passwd|pwd)["'\s:=]+["'][A-Za-z0-9_\-!@#$%^&*()]{16,}["']
```

## Usage Example
```bash
# Scan all staged files for any pattern
git diff --cached --name-only | xargs grep -nE 'AKIA[0-9A-Z]{16}|-----BEGIN.*PRIVATE KEY-----|gh[pousr]_[A-Za-z0-9]{36}'
```

## False Positive Handling
- Test files with dummy keys: add `# pragma: allowlist secret` inline comment or add the file to `.gitleaksignore`.
- `.env.example` files: should only contain placeholder values like `your-api-key-here`.
