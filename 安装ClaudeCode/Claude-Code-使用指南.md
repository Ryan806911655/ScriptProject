# Claude Code 使用指南

> 适用于 Windows / Mac 新手用户 · 安装完成后阅读本文即可上手

---

## 目录

1. [Claude Code 是什么](#1-claude-code-是什么)
2. [第一次启动](#2-第一次启动)
3. [基础使用](#3-基础使用)
4. [进阶功能](#4-进阶功能)
5. [VS Code 中使用](#5-vs-code-中使用)
6. [常用命令速查](#6-常用命令速查)
7. [常见问题](#7-常见问题)
8. [省钱技巧](#8-省钱技巧)

---

## 1. Claude Code 是什么

Claude Code 是一个**运行在终端里的 AI 编程助手**。它可以：

| 能做什么 | 举个例子 |
|----------|----------|
| 写代码 | "帮我写一个 Python 爬虫" |
| 改代码 | "把这个函数改成异步的" |
| 修 Bug | "这段代码报错了，帮我看看" |
| 解释代码 | "这段代码是什么意思" |
| 创建项目 | "帮我创建一个 Vue 项目" |
| 操作文件 | "把所有 .txt 文件转成 .md" |

简单理解：**一个能直接操作你电脑文件的 ChatGPT**，而且更懂编程。

---

## 2. 第一次启动

### 打开终端

| 系统 | 方法 |
|------|------|
| **Windows** | 按 `Win + R`，输入 `cmd`，回车 |
| **Mac** | 按 `Cmd + 空格`，输入 `终端`，回车 |

### 启动 Claude Code

```bash
claude
```

第一次运行会问你几个问题（用↑↓键选择，回车确认），按默认选择即可。

### 检查是否正常

```bash
claude --version
```

显示版本号就是正常的。

---

## 3. 基础使用

### 3.1 交互模式（推荐）

直接在终端输入 `claude` 进入对话：

```bash
claude
```

进去后就像聊天一样打字，Claude 会回答你的问题、帮你写代码、操作文件。

#### 常用快捷键

| 快捷键 | 作用 |
|--------|------|
| `Ctrl + C` | 退出当前对话 / 回到主菜单 |
| `Ctrl + D` | 退出 Claude Code |
| `↑ / ↓` | 浏览历史消息 |
| `Enter` | 发送消息 |
| `Shift + Enter` | 换行（消息太长时分段） |

### 3.2 单次提问（不进入对话模式）

```bash
claude "帮我写一个批量重命名文件的脚本"
```

适合简单的一次性任务，用完就走。

### 3.3 指定文件操作

```bash
claude "帮我把 app.js 里的 main 函数改成 async"
```

Claude 会自动读取文件、修改、保存。

### 3.4 从文件读取任务

把需求写在一个文件里，让 Claude 读：

```bash
claude < 需求.txt
```

---

## 4. 进阶功能

### 4.1 让 Claude 了解你的项目

在项目根目录创建一个 `CLAUDE.md` 文件：

```markdown
# 项目说明
这是一个用 React + TypeScript 写的后台管理系统。
主要功能是用户管理、订单管理。

# 技术栈
- 前端: React 18 + TypeScript
- 样式: Tailwind CSS
- 后端: Node.js + Express

# 编码规范
- 函数名用驼峰命名
- 组件文件用 PascalCase
```

Claude Code 每次进入这个项目都会先读 `CLAUDE.md`，理解你的项目背景。

### 4.2 拖拽文件

直接把文件或文件夹**拖到终端窗口**，Claude 会自动读取：

```bash
claude
# 进入对话后，把文件拖进来，Claude 就能读到
```

### 4.3 多轮迭代

Claude 可以持续改代码直到你满意：

```
你: 帮我写一个登录页面
Claude: [创建 login.html]
你: 背景改成深色
Claude: [修改]
你: 再加一个注册链接
Claude: [修改]
你: 好的，就这样
```

### 4.4 解决报错

直接把报错信息贴给 Claude：

```
你: npm run build 报错了:
    Error: Cannot find module './utils'
    帮我看看怎么修
```

Claude 会读代码、定位问题、修好。

---

## 5. VS Code 中使用

### 安装扩展

1. 打开 VS Code
2. 点击左侧扩展图标（或按 `Ctrl + Shift + X`）
3. 搜索 **"Claude Code"**
4. 点击安装

### 使用方式

安装后，在 VS Code 里按 `Ctrl + Shift + P`，输入 `Claude`，选择命令即可。

也可以用快捷键：
- **`Ctrl + Shift + I`** — 打开 Claude Code 侧边栏

在 VS Code 里使用的好处是：**可以直接看到代码、选中代码让 Claude 改、实时预览效果**。

---

## 6. 常用命令速查

| 命令 | 说明 |
|------|------|
| `claude` | 进入交互对话模式 |
| `claude "问题"` | 单次提问 |
| `claude --help` | 查看所有命令 |
| `claude --version` | 查看版本 |
| `claude --update` | 更新到最新版 |
| `claude config` | 修改配置 |
| `claude mcp` | 管理 MCP 插件 |
| `/status` | （对话中）查看当前状态 |
| `/model` | （对话中）切换模型 |
| `/clear` | （对话中）清空对话历史 |

---

## 7. 常见问题

### Q: 提示 `claude: command not found`

**原因**：安装后没重启终端。

**解决**：关闭当前终端，重新打开一个，再试。

---

### Q: 提示 `API Key` 相关错误

**原因**：Key 没配或过期。

**解决**：
- DeepSeek：去 [platform.deepseek.com](https://platform.deepseek.com) 检查余额
- Anthropic：去 [console.anthropic.com](https://console.anthropic.com) 检查 Key 状态

确认后重新设置：
```bash
# Windows
setx ANTHROPIC_AUTH_TOKEN "你的新Key"

# Mac
echo 'export ANTHROPIC_AUTH_TOKEN="你的新Key"' >> ~/.zshrc
source ~/.zshrc
```

---

### Q: 提示 `You don't have access to this model` 或模型报错

**原因**：模型名写错了。

**解决**：确认使用的模型名称：
- DeepSeek：`deepseek-v4-pro` 或 `deepseek-v4-flash`
- Anthropic 官方：不需要配置模型名

---

### Q: Claude 改错了我的代码怎么办

**别怕**，两种方法恢复：

#### 方法 1：撤回
Ctrl + Z 就能撤回 Claude 的修改。

#### 方法 2：告诉它改回来
```
你: 刚才的修改不对，帮我改回原来的
```

#### 方法 3（推荐）：用 Git
```bash
git checkout .    # 恢复到上次 commit 的状态
```

建议在让 Claude 改代码前先 commit 一下。

---

### Q: 响应很慢

1. 检查网络
2. 切换模型：`/model` 选择更快更便宜的模型
3. 用 DeepSeek 的话，高峰期可能慢，换个时段

---

### Q: 每次都要输入 Key 吗

不需要。安装脚本已经把 Key 保存到了系统环境变量，永久有效，直到 Key 过期。

---

### Q: 我的 Key 安全吗

Key 存储在系统环境变量中，只会存在你的电脑上。**不要把你的 Key 发给任何人。**

如果 Key 泄露了，马上去官网删除并重新生成一个新的。

---

## 8. 省钱技巧

### 8.1 简单任务用便宜模型

```bash
# 对话中输入 /model
# 选择 cheaper 或 fastest 的模型
```

| 任务 | 推荐模型 | 价格参考 |
|------|----------|----------|
| 写代码 / 改项目 | 主力模型 (Pro) | ~$0.44/百万字 |
| 简单问答 / 翻译 | 快速模型 (Flash) | ~$0.14/百万字 |

### 8.2 不要反复问同一个问题

如果第一次答案不满意，**告诉它哪里不对让它改**，而不是重新问一遍。重复提问会重复扣费。

### 8.3 一个任务一次说完

```
# ❌ 浪费
你: 帮我写一个按钮
Claude: [写了]
你: 改成红色
Claude: [改了]
你: 再放大一点

# ✅ 省
你: 帮我写一个红色的大按钮，圆角，带阴影
```

### 8.4 用项目说明文件

创建 `CLAUDE.md`（见 4.1 节），让 Claude 一次性了解项目背景，不用每次都重新解释。

### 8.5 估算花费

```bash
# 对话中输入
/status
```

能看到当前会话花了多少钱。

---

## 附录: 推荐工作流

```
1. 打开终端 → 进入项目文件夹
     cd my-project

2. 用 Git 保存当前状态
     git add . && git commit -m "修改前保存"

3. 启动 Claude Code
     claude

4. 描述你的需求
     帮我把用户列表接口改成支持分页和搜索

5. Claude 改完后，测试一下
     npm run dev      # 运行项目验证

6. 满意就提交，不满意就告诉它继续改或 git checkout 恢复
```

---

> 📧 如有问题，联系帮你安装的技术支持。
>
> 🔗 官方文档: [https://docs.anthropic.com/zh-CN/docs/claude-code/overview](https://docs.anthropic.com/zh-CN/docs/claude-code/overview)
