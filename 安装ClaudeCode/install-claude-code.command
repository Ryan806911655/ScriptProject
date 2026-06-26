#!/bin/bash
# ============================================================
#  Claude Code 一键安装 (Mac 双击版)
#  双击此文件即可运行，首次可能需要右键→打开
# ============================================================

# 如果提示"无法打开"，请在终端执行: chmod +x 然后拖入此文件

# 分隔符（统一管理）
SEP1="============================================"
SEP2="--------------------------------------------"
if [ ! -x "$0" ]; then
    echo ""
    echo "$SEP1"
    echo "   首次运行需要赋予执行权限"
    echo "$SEP1"
    echo ""
    echo "   请复制下面这条命令到终端执行:"
    echo ""
    echo "   chmod +x \"$0\" && \"$0\""
    echo ""
    echo "$SEP1"
    read -p "   按回车关闭此窗口..."
    exit 1
fi

set -e

echo ""
echo "$SEP1"
echo "   Claude Code 一键安装脚本 (Mac)"
echo "   Node.js + Git + VS Code + Claude Code"
echo "$SEP1"
echo ""
echo "   本脚本将自动安装:"
echo "    1. Homebrew (macOS 包管理器,如未安装)"
echo "    2. Node.js (JavaScript 运行环境)"
echo "    3. Git    (版本管理工具)"
echo "    4. VS Code (代码编辑器)"
echo "    5. Claude Code (AI 编程助手)"
echo ""
echo "   已安装的组件会自动跳过。"
echo ""

# ============================================================
# 0. 环境检测
# ============================================================
echo "$SEP1"
echo " [环境检测]"
echo "$SEP1"

echo "   [OK] 操作系统: $(sw_vers -productName 2>/dev/null || echo 'macOS')"

echo "   正在检测网络..."
if ! ping -c 1 -W 3 8.8.8.8 > /dev/null 2>&1; then
    if ! ping -c 1 -W 3 www.baidu.com > /dev/null 2>&1; then
        echo "   [失败] 网络不可用。"
        read -p "   按回车退出"
        exit 1
    fi
fi
echo "   [OK] 网络: 正常"

# ============================================================
# 1. Homebrew
# ============================================================
echo ""
echo "$SEP1"
echo " [1/5] Homebrew - macOS 包管理器"
echo "$SEP1"

if command -v brew &> /dev/null; then
    echo "   [OK] 已安装: $(brew --version | head -1)"
else
    echo "   正在安装 Homebrew（可能需要输入密码）..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

    # Apple Silicon Mac
    if [ -f "/opt/homebrew/bin/brew" ]; then
        eval "$(/opt/homebrew/bin/brew shellenv)"
        echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> "$HOME/.zprofile"
    fi

    if command -v brew &> /dev/null; then
        echo "   [OK] Homebrew 安装成功"
    else
        echo "   [失败] Homebrew 安装失败。"
        echo "   请手动安装: https://brew.sh/"
        read -p "   按回车退出"
        exit 1
    fi
fi

# ============================================================
# 2. Node.js
# ============================================================
echo ""
echo "$SEP1"
echo " [2/5] Node.js - JavaScript 运行环境"
echo "$SEP1"

# 获取最新 LTS 版本
node_latest="v22.19.0"
node_json=$(curl -s --max-time 8 https://nodejs.org/dist/index.json 2>/dev/null)
if [ -n "$node_json" ]; then
    node_latest=$(echo "$node_json" | grep -o '"version":"v[0-9.]*"' | head -1 | cut -d'"' -f4)
fi
echo "   最新 LTS: $node_latest"

if command -v node &> /dev/null; then
    installed_node=$(node -v)
    echo "   已安装:   $installed_node"

    installed_v=$(echo "$installed_node" | sed 's/^v//')
    latest_v=$(echo "$node_latest" | sed 's/^v//')
    older=$(printf '%s
%s
' "$installed_v" "$latest_v" | sort -V | head -1)

    if [ "$older" = "$installed_v" ] && [ "$installed_v" != "$latest_v" ]; then
        echo "   ⚠ 版本过旧 ($installed_node → $node_latest)，可能影响 Claude Code 运行。"
        echo ""
        echo "   [1] 更新到 $node_latest（推荐）"
        echo "   [2] 跳过，保留当前版本"
        echo ""
        read -p "   请选择（默认 1）: " node_choice
        node_choice=${node_choice:-1}
        if [ "$node_choice" = "2" ]; then
            echo "   [OK] 已跳过更新，保留 $installed_node"
        else
            echo "   正在更新 Node.js..."
            brew upgrade node 2>/dev/null || brew install node
            if command -v node &> /dev/null; then
                echo "   [OK] Node.js $(node -v) 更新成功"
            else
                echo "   [失败] Node.js 更新失败。"
                echo "   请手动安装: https://nodejs.org/"
                read -p "   按回车退出"
                exit 1
            fi
        fi
    else
        echo "   [OK] 已是最新 LTS 版本"
    fi
else
    echo "   正在安装 Node.js..."
    brew install node

    if command -v node &> /dev/null; then
        echo "   [OK] Node.js $(node -v) 安装成功"
    else
        echo "   [失败] Node.js 安装失败。"
        echo "   请手动安装: https://nodejs.org/"
        read -p "   按回车退出"
        exit 1
    fi
fi

# ============================================================
# 配置 npm（镜像源 + 全局路径）
# ============================================================
echo ""
echo "$SEP1"
echo " [3/5] 配置 npm"
echo "$SEP1"

echo "   npm 版本: $(npm -v)"

# 修复 Mac 上 npm 全局安装的权限问题
NPM_PREFIX="$(npm config get prefix)"
if echo "$NPM_PREFIX" | grep -q "/usr/local"; then
    echo ""
    echo "   检测到 npm 全局路径需要系统权限 ($NPM_PREFIX)"
    echo "   正在迁移到用户目录..."
    NEW_PREFIX="$HOME/.npm-global"
    mkdir -p "$NEW_PREFIX"
    npm config set prefix "$NEW_PREFIX"
    # 加入 PATH
    SHELL_RC_="$HOME/.zshrc"
    [ ! -f "$SHELL_RC_" ] && SHELL_RC_="$HOME/.bashrc"
    if ! grep -q "$NEW_PREFIX/bin" "$SHELL_RC_" 2>/dev/null; then
        echo "export PATH=$NEW_PREFIX/bin:\$PATH" >> "$SHELL_RC_"
    fi
    export PATH="$NEW_PREFIX/bin:$PATH"
    echo "   [OK] npm 全局路径已迁移到 $NEW_PREFIX"
fi

echo ""
echo "   检查 npm 镜像源..."
current_registry=$(npm config get registry 2>/dev/null)
if echo "$current_registry" | grep -q "npmmirror"; then
    echo "   [OK] 当前已使用 npmmirror.com 镜像，无需切换"
else
    echo "   当前镜像: $current_registry"
    echo "   是否使用国内 npm 镜像加速?"
    echo "   中国大陆用户推荐选 Y。"
    read -p "   使用 npmmirror.com? [Y/n](直接回车=是): " mirror
    mirror=${mirror:-Y}

    if [ "$mirror" = "Y" ] || [ "$mirror" = "y" ]; then
        npm config set registry https://registry.npmmirror.com
        echo "   [OK] 镜像: npmmirror.com"
    else
        echo "   [OK] 使用 npm 官方源"
    fi
fi

# ============================================================
# 3. Git
# ============================================================
echo ""
echo "$SEP1"
echo " [4/5] Git - 版本管理工具"
echo "$SEP1"

if command -v git &> /dev/null; then
    echo "   [OK] 已安装: $(git --version)"
else
    echo "   正在安装 Git..."
    brew install git

    if command -v git &> /dev/null; then
        echo "   [OK] Git $(git --version) 安装成功"
    else
        echo "   [X] Git 安装可能失败,继续..."
    fi
fi

# ============================================================
# 4. VS Code
# ============================================================
echo ""
echo "$SEP1"
echo " [5/5] VS Code - 代码编辑器"
echo "$SEP1"

# 获取最新版本
vscode_latest=$(curl -s --max-time 8 "https://update.code.visualstudio.com/api/update/darwin/stable/latest" 2>/dev/null | grep -o '"name":"[^"]*"' | head -1 | cut -d'"' -f4)
[ -n "$vscode_latest" ] && echo "   最新稳定版: $vscode_latest"

if command -v code &> /dev/null; then
    installed_vscode=$(code --version 2>/dev/null | head -1)
    echo "   已安装:   $installed_vscode"

    if [ -n "$vscode_latest" ] && [ "$(printf '%s
%s
' "$installed_vscode" "$vscode_latest" | sort -V | head -1)" = "$installed_vscode" ] && [ "$installed_vscode" != "$vscode_latest" ]; then
        echo "   ⚠ 版本过旧 ($installed_vscode → $vscode_latest)，可能影响 Claude Code 扩展运行。"
        echo ""
        echo "   [1] 更新到最新版（推荐）"
        echo "   [2] 跳过，保留当前版本"
        echo ""
        read -p "   请选择（默认 1）: " vs_choice
        vs_choice=${vs_choice:-1}
        if [ "$vs_choice" = "2" ]; then
            echo "   [OK] 已跳过更新，保留 $installed_vscode"
        else
            echo "   正在更新 VS Code..."
            brew upgrade --cask visual-studio-code 2>/dev/null || brew install --cask visual-studio-code
            if command -v code &> /dev/null; then
                echo "   [OK] VS Code 更新成功"
            else
                echo "   [X] VS Code 更新可能失败,已跳过。"
            fi
        fi
    else
        echo "   [OK] 已是最新版本"
    fi
else
    echo "   正在安装 VS Code..."
    brew install --cask visual-studio-code

    if command -v code &> /dev/null; then
        echo "   [OK] VS Code 安装成功"
    else
        echo "   [X] VS Code 安装可能失败,已跳过。"
        echo "   可手动下载: https://code.visualstudio.com/"
    fi
fi

# ============================================================
# Claude Code
# ============================================================
echo ""
echo "$SEP1"
echo "   Claude Code - AI 编程助手"
echo "$SEP1"

# 获取 npm 上的最新版本
cc_latest=$(npm view @anthropic-ai/claude-code version 2>/dev/null)
[ -n "$cc_latest" ] && echo "   npm 最新版: $cc_latest"

# 检测是否已安装
CC_ALREADY_INSTALLED=false
if command -v claude &> /dev/null; then
    echo ""
    echo "   [检测] Claude Code 已安装: $(claude --version 2>/dev/null)"
    if [ -n "$cc_latest" ] && [ "$(claude --version 2>/dev/null)" != "$cc_latest" ]; then
        echo "   ⚠ 当前版本低于最新版 ($cc_latest)"
    fi
    echo ""
    echo "   [1] 更新到最新版（推荐）"
    echo "   [2] 重装（覆盖安装）"
    echo "   [3] 跳过安装"
    echo ""
    read -p "   请选择（默认 1）: " cc_choice
    cc_choice=${cc_choice:-1}
    if [ "$cc_choice" = "3" ]; then
        echo "   [OK] 已跳过 Claude Code 安装"
        CC_ALREADY_INSTALLED=true
    elif [ "$cc_choice" = "2" ]; then
        echo "   将覆盖安装..."
    else
        echo "   将更新到最新版..."
    fi
fi

if [ "$CC_ALREADY_INSTALLED" = false ]; then
    echo ""
    echo "   正在安装 Claude Code (约 1-3 分钟)..."
    npm install -g @anthropic-ai/claude-code

    if [ $? -ne 0 ]; then
        echo ""
        echo "   [失败] Claude Code 安装失败。"
        echo "   请手动尝试:"
        echo "     npm config set registry https://registry.npmmirror.com"
        echo "     npm install -g @anthropic-ai/claude-code"
        read -p "   按回车退出"
        exit 1
    fi

    echo "   [OK] Claude Code 安装完成"
    echo "   版本: $(claude --version 2>/dev/null || echo '请重启终端')"
fi

# ============================================================
# API 配置
# ============================================================
echo ""
echo "$SEP1"
echo " [API 配置]"
echo "$SEP1"
echo ""
echo "   请选择 API 提供商:"
echo ""
echo "   [1] DeepSeek      (国内推荐, 便宜)"
echo "   [2] Anthropic      (官方 OAuth 登录)"
echo "   [3] Anthropic      (官方 API Key)"
echo "   [4] 其他第三方      (自定义地址)"
echo "   [0] 跳过配置"
echo ""
read -p "   请输入数字 (默认 1): " choice
choice=${choice:-1}

SHELL_RC="$HOME/.zshrc"
[ ! -f "$SHELL_RC" ] && SHELL_RC="$HOME/.bashrc"
[ ! -f "$SHELL_RC" ] && SHELL_RC="$HOME/.zprofile"

case $choice in
    0) echo "   [跳过] 稍后手动配置。" ;;
    2)
        echo ""
        echo "   打开新终端,输入 claude,浏览器会弹出 OAuth 登录页面。"
        ;;
    1)
        echo ""
        echo "   获取 API Key: https://platform.deepseek.com"
        echo ""
        read -p "   请粘贴你的 DeepSeek API Key: " api_key
        if [ -z "$api_key" ]; then
            echo "   [跳过] 未输入 Key。"
        else
            cat >> "$SHELL_RC" << 'ENVEOF'

# === Claude Code with DeepSeek ===
ENVEOF
            echo "export ANTHROPIC_BASE_URL=https://api.deepseek.com/anthropic" >> "$SHELL_RC"
            echo "export ANTHROPIC_AUTH_TOKEN=$api_key" >> "$SHELL_RC"
            echo "export ANTHROPIC_DEFAULT_SONNET_MODEL=deepseek-v4-pro" >> "$SHELL_RC"
            echo "export ANTHROPIC_DEFAULT_OPUS_MODEL=deepseek-v4-pro" >> "$SHELL_RC"
            echo "export ANTHROPIC_DEFAULT_HAIKU_MODEL=deepseek-v4-flash" >> "$SHELL_RC"

            export ANTHROPIC_BASE_URL="https://api.deepseek.com/anthropic"
            export ANTHROPIC_AUTH_TOKEN="$api_key"
            export ANTHROPIC_DEFAULT_SONNET_MODEL="deepseek-v4-pro"
            export ANTHROPIC_DEFAULT_OPUS_MODEL="deepseek-v4-pro"
            export ANTHROPIC_DEFAULT_HAIKU_MODEL="deepseek-v4-flash"

            echo "   [OK] 配置已写入 $SHELL_RC"
            echo "   [OK] DeepSeek API Key + 模型映射已配置"
        fi
        ;;
    3)
        echo ""
        echo "   获取 API Key: https://console.anthropic.com/settings/keys"
        echo ""
        read -p "   请粘贴你的 Anthropic API Key: " api_key
        if [ -z "$api_key" ]; then
            echo "   [跳过] 未输入 Key。"
        else
            echo "" >> "$SHELL_RC"
            echo "# === Claude Code / Anthropic ===" >> "$SHELL_RC"
            echo "export ANTHROPIC_API_KEY=$api_key" >> "$SHELL_RC"
            export ANTHROPIC_API_KEY="$api_key"
            echo "   [OK] 配置已写入 $SHELL_RC"
        fi
        ;;
    4)
        echo ""
        echo "   第三方需要支持 Anthropic 兼容 API 端点。"
        read -p "   请输入 API Key: " api_key
        if [ -z "$api_key" ]; then
            echo "   [跳过] 未输入 Key。"
        else
            echo "" >> "$SHELL_RC"
            echo "export ANTHROPIC_AUTH_TOKEN=$api_key" >> "$SHELL_RC"
            read -p "   API 端点地址: " base_url
            [ -n "$base_url" ] && echo "export ANTHROPIC_BASE_URL=$base_url" >> "$SHELL_RC"
            read -p "   默认模型名称: " model
            if [ -n "$model" ]; then
                echo "export ANTHROPIC_DEFAULT_SONNET_MODEL=$model" >> "$SHELL_RC"
                echo "export ANTHROPIC_DEFAULT_OPUS_MODEL=$model" >> "$SHELL_RC"
            fi
            export ANTHROPIC_AUTH_TOKEN="$api_key"
            echo "   [OK] 配置已写入 $SHELL_RC"
        fi
        ;;
    *) echo "   [跳过] 无效选择。" ;;
esac

echo ""
echo "$SEP1"
echo " [ 大功告成! ]"
echo "$SEP1"
echo ""
echo "   执行以下命令使配置生效:"
echo "     source $SHELL_RC"
echo ""
echo "   然后输入 claude 开始使用!"
echo ""
echo "   常用命令:"
echo "     claude             启动交互模式"
echo '     claude "问题"       直接提问'
echo "     claude --help       查看帮助"
echo "     claude --update     更新到最新版"
echo "     code .              在当前目录打开 VS Code"
echo ""
echo "   如需清理安装文件，请运行: 清理安装文件.sh"
echo ""
echo "$SEP1"

read -p "   按回车关闭此窗口..."
