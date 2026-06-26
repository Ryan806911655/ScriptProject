#!/bin/bash
set -e

# 分隔符（统一管理）
SEP1="============================================"
SEP2="--------------------------------------------"

echo ""
echo "$SEP1"
echo "   Claude Code 一键安装脚本 (Mac/Linux)"
echo "   Node.js + Git + VS Code + Claude Code"
echo "$SEP1"
echo ""
echo "   本脚本将自动安装:"
echo "    1. Homebrew (macOS 包管理器,如未安装)"
echo "    2. Node.js (JavaScript 运行环境)"
echo "    3. Git    (版本管理工具)"
echo "    4. VS Code (代码编辑器,仅 macOS)"
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

OS="$(uname -s)"
echo "   [OK] 操作系统: $OS"

# 网络检测
echo "   正在检测网络..."
if ! ping -c 1 -W 3 8.8.8.8 > /dev/null 2>&1; then
    if ! ping -c 1 -W 3 www.baidu.com > /dev/null 2>&1; then
        echo "   [失败] 网络不可用。"
        exit 1
    fi
fi
echo "   [OK] 网络: 正常"

# ============================================================
# macOS: 安装 Homebrew
# ============================================================
if [ "$OS" = "Darwin" ]; then
    echo ""
    echo "$SEP1"
    echo " [0/5] Homebrew - macOS 包管理器"
    echo "$SEP1"

    if command -v brew &> /dev/null; then
        echo "   [OK] Homebrew 已安装: $(brew --version | head -1)"
    else
        echo "   正在安装 Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

        # Apple Silicon Mac 需要额外设置 PATH
        if [ -f "/opt/homebrew/bin/brew" ]; then
            eval "$(/opt/homebrew/bin/brew shellenv)"
        fi

        if command -v brew &> /dev/null; then
            echo "   [OK] Homebrew 安装成功"
        else
            echo "   [失败] Homebrew 安装失败。"
            echo "   请手动安装: https://brew.sh/"
            exit 1
        fi
    fi
fi

# ============================================================
# 1. Node.js
# ============================================================
echo ""
echo "$SEP1"
echo " [1/5] Node.js - JavaScript 运行环境"
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

    # 版本比较
    installed_v=$(echo "$installed_node" | sed 's/^v//')
    latest_v=$(echo "$node_latest" | sed 's/^v//')
    older=$(printf '%s\n%s\n' "$installed_v" "$latest_v" | sort -V | head -1)

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
            echo "   正在安装/更新 Node.js..."
            if [ "$OS" = "Darwin" ]; then
                brew upgrade node 2>/dev/null || brew install node
            else
                curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
                sudo apt-get install -y nodejs
            fi
            if command -v node &> /dev/null; then
                echo "   [OK] Node.js $(node -v) 安装成功"
            else
                echo "   [失败] Node.js 安装失败。"
                echo "   请手动安装: https://nodejs.org/"
                exit 1
            fi
        fi
    else
        echo "   [OK] 已是最新 LTS 版本"
    fi
else
    echo "   正在安装 Node.js ($node_latest)..."

    if [ "$OS" = "Darwin" ]; then
        brew install node
    else
        # Linux: 使用 NodeSource
        curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
        sudo apt-get install -y nodejs
    fi

    if command -v node &> /dev/null; then
        echo "   [OK] Node.js $(node -v) 安装成功"
    else
        echo "   [失败] Node.js 安装失败。"
        echo "   请手动安装: https://nodejs.org/"
        exit 1
    fi
fi

# ============================================================
# 2. 配置 npm
# ============================================================
echo ""
echo "$SEP1"
echo " [2/5] 配置 npm"
echo "$SEP1"

echo "   npm 版本: $(npm -v)"

echo ""
echo "   检查 npm 镜像源..."
current_registry=$(npm config get registry 2>/dev/null)
if echo "$current_registry" | grep -q "npmmirror"; then
    echo "   [OK] 当前已使用 npmmirror.com 镜像，无需切换"
else
    echo "   当前镜像: $current_registry"
    echo "   是否使用国内 npm 镜像加速下载?"
    echo "   中国大陆用户推荐选 Y。"
    read -p "   使用 npmmirror.com? [Y/N] (推荐 Y): " mirror_choice
    mirror_choice=${mirror_choice:-Y}

    if [ "$mirror_choice" = "Y" ] || [ "$mirror_choice" = "y" ]; then
        npm config set registry https://registry.npmmirror.com
        echo "   [OK] 镜像已设置: npmmirror.com"
    else
        echo "   [OK] 使用 npm 官方源"
    fi
fi

# ============================================================
# 3. Git
# ============================================================
echo ""
echo "$SEP1"
echo " [3/5] Git - 版本管理工具"
echo "$SEP1"

if command -v git &> /dev/null; then
    echo "   [OK] 已安装: $(git --version)"
else
    echo "   正在安装 Git..."

    if [ "$OS" = "Darwin" ]; then
        brew install git
    else
        sudo apt-get install -y git
    fi

    if command -v git &> /dev/null; then
        echo "   [OK] Git $(git --version) 安装成功"
    else
        echo "   [X] Git 安装可能失败,继续..."
    fi
fi

# ============================================================
# 4. VS Code (仅 macOS)
# ============================================================
if [ "$OS" = "Darwin" ]; then
    echo ""
    echo "$SEP1"
    echo " [4/5] VS Code - 代码编辑器"
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
else
    echo ""
    echo "$SEP1"
    echo " [4/5] VS Code - 请手动安装"
    echo "$SEP1"
    echo "   请从 https://code.visualstudio.com/ 下载安装"
fi

# ============================================================
# 5. Claude Code
# ============================================================
echo ""
echo "$SEP1"
echo " [5/5] Claude Code - AI 编程助手"
echo "$SEP1"

# 获取 npm 上的最新版本
cc_latest=$(npm view @anthropic-ai/claude-code version 2>/dev/null)
[ -n "$cc_latest" ] && echo "   npm 最新版: $cc_latest"

# 检测是否已安装
CC_ALREADY_INSTALLED=false
if command -v claude &> /dev/null; then
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
        echo ""
        echo "   请手动尝试:"
        echo "     npm config set registry https://registry.npmmirror.com"
        echo "     npm install -g @anthropic-ai/claude-code"
        exit 1
    fi

    echo "   [OK] Claude Code 安装完成"
    echo "   Claude Code 版本: $(claude --version 2>/dev/null || echo '请重启终端')"
fi

echo ""
echo "$SEP1"
echo " [安装完成!]"
echo "$SEP1"
echo "   Claude Code 版本: $(claude --version 2>/dev/null || echo '请重启终端')"

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

case $choice in
    0)
        echo "   [跳过] 稍后手动配置。"
        ;;
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
            SHELL_RC=""
            if [ -f "$HOME/.zshrc" ]; then SHELL_RC="$HOME/.zshrc"; else SHELL_RC="$HOME/.bashrc"; fi
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
            echo "   [OK] DeepSeek API Key 和端点已保存到 $SHELL_RC"
            echo "   [OK] 模型映射已配置 (deepseek-v4-pro + deepseek-v4-flash)"
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
            SHELL_RC=""
            if [ -f "$HOME/.zshrc" ]; then SHELL_RC="$HOME/.zshrc"; else SHELL_RC="$HOME/.bashrc"; fi
            echo "export ANTHROPIC_API_KEY=$api_key" >> "$SHELL_RC"
            export ANTHROPIC_API_KEY="$api_key"
            echo "   [OK] Anthropic API Key 已保存到 $SHELL_RC"
        fi
        ;;
    4)
        echo ""
        echo "   第三方需要支持 Anthropic 兼容 API 端点。"
        read -p "   请输入 API Key: " api_key
        if [ -z "$api_key" ]; then
            echo "   [跳过] 未输入 Key。"
        else
            SHELL_RC=""
            if [ -f "$HOME/.zshrc" ]; then SHELL_RC="$HOME/.zshrc"; else SHELL_RC="$HOME/.bashrc"; fi
            echo "export ANTHROPIC_AUTH_TOKEN=$api_key" >> "$SHELL_RC"
            read -p "   API 端点地址: " base_url
            if [ -n "$base_url" ]; then echo "export ANTHROPIC_BASE_URL=$base_url" >> "$SHELL_RC"; fi
            read -p "   默认模型名称: " model
            if [ -n "$model" ]; then
                echo "export ANTHROPIC_DEFAULT_SONNET_MODEL=$model" >> "$SHELL_RC"
                echo "export ANTHROPIC_DEFAULT_OPUS_MODEL=$model" >> "$SHELL_RC"
            fi
            export ANTHROPIC_AUTH_TOKEN="$api_key"
            echo "   [OK] 第三方提供商已配置到 $SHELL_RC"
        fi
        ;;
    *)
        echo "   [跳过] 无效选择。"
        ;;
esac

echo ""
echo "$SEP1"
echo " [大功告成!]"
echo "$SEP1"
echo ""
echo "   source ~/.zshrc (或 ~/.bashrc) 使配置生效"
echo "   然后输入 claude 开始使用!"
echo ""
echo "   常用命令:"
echo "     claude             启动交互模式"
echo '     claude "问题"       直接提问'
echo "     claude --help       查看帮助"
echo "     claude --update     更新到最新版"
echo "     code .              在当前目录打开 VS Code"
echo ""
echo "   VS Code 用户:"
echo '     在扩展市场搜索 Claude Code 安装官方扩展'
echo ""
echo "   如需清理安装文件，请运行: 清理安装文件.sh"
echo ""
echo "$SEP1"