# Lean 模式命令速查表

零依赖逆向分析，用系统原生命令完成。按目标类型路由，批量探测合并调用。

## 通用探测（一次调用拿全局信息）

### Linux/macOS
```bash
# 类型 + 大小 + 字符串数 + 导入表
file target; ls -lh target; strings target | wc -l; objdump -p target 2>/dev/null | grep NEEDED || otool -L target
```

### Windows PowerShell
```powershell
# 类型 + 大小 + 字符串（需 Sysinternals strings.exe）
Get-Item target | Select-Object Name,Length; & strings.exe -accepteula target | Measure-Object -Line
```

## 文件头魔数识别

```bash
# 前 4 字节十六进制
xxd -l 4 target
# 或 Python（跨平台）
python3 -c "print(open('target','rb').read(4).hex())"
```

| 魔数 | 类型 |
|---|---|
| `4d5a` | PE (Windows) |
| `7f454c46` | ELF (Linux) |
| `cffaedfe` / `feedfacf` | Mach-O (macOS) |
| `0061736d` | WASM |
| `53514c69` | SQLite |
| `504b0304` | ZIP/APK/JAR |
| `1f8b` | gzip |

## Electron / ASAR

```bash
# 解压 ASAR
npx asar extract app.asar ./extracted

# 搜索 IPC 通道和 preload（-uu 搜索点开头目录）
rg -uu "ipcMain\.(handle|on)|ipcRenderer\.(invoke|send)|contextBridge|preload" ./extracted/

# 看 package.json 的 main 入口
cat ./extracted/package.json | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('main'), d.get('version'))"

# 找 fuses 配置
rg -uu "onlyLoadAppFromAsar|nodeIntegration|contextIsolation" ./extracted/
```

## Mach-O (macOS)

```bash
# 加载命令和依赖库
otool -l target | head -60
otool -L target

# 字面量池（字符串）
otool -v -s __TEXT __cstring target | head -100

# 目标文件所有符号
nm -j target | head -50

# 反汇编指定函数（先找地址）
otool -ov target | grep -A10 "函数名"
objdump -d --start-address=0x1000 --stop-address=0x2000 target
```

## ELF (Linux)

```bash
# 程序头和节
readelf -h target
readelf -S target

# 动态符号和导入
readelf -d target | grep NEEDED
readelf --dyn-syms target | head -50

# 字符串
strings -n 4 target | head -100

# 反汇编
objdump -d target | head -200
objdump -d --start-address=0x401000 --stop-address=0x402000 target
```

## PE (Windows)

```bash
# 导入表（需 Visual Studio dumpbin 或 mingw objdump）
dumpbin /imports target.exe
objdump -p target.exe | grep "DLL Name"

# 字符串（Sysinternals）
strings.exe -accepteula -n 4 target.exe | head -100

# 节信息
dumpbin /headers target.exe
```

## Go 二进制

```bash
# 构建信息和依赖版本
go version -m target

# 找 runtime 符号确认是 Go
strings target | grep "runtime\." | head -5
strings target | grep "go.buildinfo"

# Go 函数名（通常带包路径）
nm target | grep "main\." | head -30
```

## Rust 二进制

```bash
# cargo auditable 嵌入的依赖清单（如果有）
strings target | grep "cargo auditable" | head -5

# Rust panic 消息和符号
strings target | grep "panicked at" | head -10
nm target | grep "_ZN" | head -30  # Rust 符号修饰
```

## .NET 程序集

```bash
# ilspycmd 反编译（需 dotnet tool install -g ilspycmd）
ilspycmd -p -o ./decompiled assembly.dll

# monodis（Mono）
monodis assembly.dll | head -100

# 查看引用的程序集
strings assembly.dll | grep -i "\.dll" | sort -u | head -30
```

## Android APK

```bash
# JADX 反编译（推荐，需 JDK 17+）
jadx --no-res --output-dir ./jadx-out app.apk

# apktool 解包（资源+smali）
apktool d app.apk -o ./apk-out

# 先看 Manifest
cat ./jadx-out/resources/AndroidManifest.xml | head -80

# 搜关键词（-uu 搜所有目录）
rg -uu "login|api|http|secret|key|token|encrypt" ./jadx-out/sources/ | head -30

# 权限列表
rg -o 'android:name="[^"]*"' ./jadx-out/resources/AndroidManifest.xml | grep permission | sort -u
```

## Flutter

```bash
# 找 libflutter.so 和 snapshot
find ./extracted -name "libflutter.so" -o -name "*snapshot*"

# snapshot hash（用于匹配 Dart SDK 版本）
strings libflutter.so | grep -i "snapshot" | head -5

# Dart 字符串（AOT 编译后字符串仍可见）
strings libapp.so | grep -i "http\|api\|login" | head -20
```

## WASM

```bash
# wasm-objdump（需 wabt）
wasm-objdump -x target.wasm | head -50
wasm-objdump -d target.wasm | head -100

# 字符串（WASM 中字符串在 data 段）
strings target.wasm | head -50

# 导入和导出
wasm-objdump -j Import -x target.wasm
wasm-objdump -j Export -x target.wasm
```

## SQLite

```bash
# 完整 dump
sqlite3 target.db .dump > dump.sql

# 表清单
sqlite3 target.db .tables

# 表结构
sqlite3 target.db ".schema"

# 敏感数据搜索
sqlite3 target.db "SELECT * FROM users LIMIT 5;"
```

## 固件

```bash
# Binwalk 提取（Linux only）
binwalk -e firmware.bin
binwalk -y filesystem firmware.bin  # 只提取文件系统

# 识别文件系统类型
file extracted/*

# 提取后对二进制做原生分析
strings extracted/sbin/busybox | head -50
```

## 网站

```bash
# 获取页面和 JS
curl -sL https://example.com -o page.html
curl -sL https://example.com/app.js -o app.js

# 搜 API 端点和密钥
rg -n "api|fetch|axios|token|secret|key|password" app.js | head -30

# 看 Network 请求（需浏览器 DevTools）
# 在 DevTools Console 执行：performance.getEntriesByType('resource').map(r=>r.name)
```

## HAR / PCAP

```bash
# HAR 解析
jq '.log.entries[] | {url: .request.url, method: .request.method, status: .response.status}' target.har

# PCAP 分析（需 tshark）
tshark -r target.pcap -Y http -T fields -e http.request.uri | head -30
tshark -r target.pcap -Y "tcp.port==443" -c 20
```

## 搜索技巧

```bash
# rg -uu 搜索所有文件（包括点开头目录和隐藏文件）
rg -uu "关键词" ./directory/

# 只搜特定扩展名
rg -uu "关键词" -g "*.js" ./directory/

# 搜二进制中的字符串
rg -uu --text "关键词" binary_file

# 排除大文件
rg -uu "关键词" --max-filesize 1M ./directory/
```

## 证据等级标注规范

每个分析结论必须标注：

- `confirmed`：工具输出直接证明，附原始输出片段
- `inferred`：基于证据的合理推断，说明推理链
- `unknown`：无法确定，说明需要什么额外信息才能确认

示例：
```
- API 端点：https://api.example.com/v1/login [confirmed]
  证据：strings 输出第 1234 行 "https://api.example.com/v1/login"
- 使用 AES 加密 [inferred]
  证据：导入了 libcrypto.so，且字符串中出现 "AES-256"，但未确认具体模式
- 登录失败次数限制 [unknown]
  证据：反编译伪代码中未找到相关逻辑，可能在服务端实现
```
