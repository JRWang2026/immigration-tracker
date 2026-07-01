# 王工私人本地 Agent（Wang Private Local Agent）

> 追求极致自由、绝对把控的私人自动化系统。所有代码跑在自己机器上，凭据自己管，数据自己存。

---

## 1. 架构总览

```text
┌────────────────────────────────────────────────────────────────────┐
│                        王工私人本地 Agent                            │
├────────────────────────────────────────────────────────────────────┤
│  seek_email_agent.py  │  scan_german_phd_agent.py  │  policy_tracker │
│        (SEEK NZ)      │       (EURAXESS)           │   (全球移民政策) │
├────────────────────────────────────────────────────────────────────┤
│              email_client.py  +  IMAP/SMTP 安全凭据管理              │
├────────────────────────────────────────────────────────────────────┤
│              kos_bridge.py  →  local_agent_output/kos/*.json         │
├────────────────────────────────────────────────────────────────────┤
│              KOS 学术网站 / GitHub Pages 静态展示                     │
└────────────────────────────────────────────────────────────────────┘
```

### 核心原则

1. **本地优先**：所有代码、数据、凭据都在你自己的电脑上。
2. **密码安全**：不硬编码密码，优先环境变量，可选 Windows Credential Manager。
3. **可扩展**：一个 agent 一个文件，新增功能复制模板即可。
4. **KOS 集成**：所有输出标准化为 JSON/Markdown，可直接喂给 KOS 网站。

---

## 2. 文件结构

```text
local_agent/
├── config.yaml                 # 全局配置（无密码）
├── requirements.txt            # Python 依赖
├── email_client.py             # IMAP 客户端 + 凭据加载
├── seek_parser.py              # SEEK 邮件 HTML 解析
├── green_list_scorer.py        # NZ 绿名单 Tier1 ICT 评分
├── seek_email_agent.py         # SEEK NZ 扫描主程序
├── kos_bridge.py               # KOS 数据桥接
├── scheduler.py                # Python 内置调度（可选）
├── setup_windows_task.ps1      # Windows 任务计划创建脚本
└── README.md                   # 本文件
```

---

## 3. 快速开始

### 3.1 安装依赖

```powershell
C:\Users\Mr_Wang\.workbuddy\binaries\python\envs\default\Scripts\python.exe -m pip install -r requirements.txt
```

### 3.2 配置 QQ Mail 应用专用密码

1. 登录 [QQ邮箱网页版](https://mail.qq.com)
2. 设置 → 账户 → 开启 **IMAP/SMTP服务**
3. 生成 **应用专用密码**（16位，不含空格）
4. 设置环境变量：

```powershell
# 在 PowerShell 中运行（永久生效）
[System.Environment]::SetEnvironmentVariable("QQ_MAIL_USER", "349376374@qq.com", "User")
[System.Environment]::SetEnvironmentVariable("QQ_MAIL_APP_PASSWORD", "你的16位应用专用密码", "User")
```

### 3.3 运行 SEEK NZ 扫描

```powershell
cd C:\Users\Mr_Wang\WorkBuddy\2026-06-20-14-48-36\local_agent
C:\Users\Mr_Wang\.workbuddy\binaries\python\envs\default\Scripts\python.exe seek_email_agent.py
```

输出：
- `../local_agent_output/reports/SEEK_NZ_Job_Report_YYYY-MM-DD.md`
- `../local_agent_output/data/seek_nz_YYYY-MM-DD.json`
- `../local_agent_output/kos/seek-nz_latest.json`

### 3.4 设置每日自动运行

推荐用 Windows 任务计划（省电、稳定）：

```powershell
# 以管理员身份运行 PowerShell
.\setup_windows_task.ps1
```

之后可在 任务计划程序 中查看、编辑、手动触发。

---

## 4. 与 KOS 学术网站集成

### 4.1 数据流

```text
Agent 运行 → local_agent_output/kos/*.json
                ↓
         手动或 GitHub Actions 同步
                ↓
         KOS 仓库 public/data/*.json
                ↓
         Next.js SSG / ISR 渲染页面
```

### 4.2 KOS 页面（已部署）

已完成集成：

- **中文页面**：`/intelligence`
- **英文页面**：`/en/intelligence`
- **组件**：`kos/components/IntelligenceDashboard.tsx`
- **数据文件**：`kos/public/data/seek-nz/latest.json`

页面功能：
1. 客户端拉取 `/data/seek-nz/latest.json` 并展示
2. 显示扫描邮件数、去重岗位数、Tier1 匹配数
3. 绿名单 Tier1 匹配岗位表格（岗位/公司/地点/薪资/匹配度/ANZSCO/移民路径）
4. 建议补强技能清单
5. 自动化说明（可写进 CV/申博作品集）

每次 Agent 运行后，执行以下命令同步数据到 KOS：

```powershell
cp C:\Users\Mr_Wang\WorkBuddy\2026-06-20-14-48-36\local_agent_output\kos\seek-nz_latest.json `
   C:\Users\Mr_Wang\WorkBuddy\2026-06-03-14-49-17\kos\public\data\seek-nz\latest.json

cd C:\Users\Mr_Wang\WorkBuddy\2026-06-03-14-49-17\kos
npm run build
```

（长期可用 GitHub Actions 自动完成。）

### 4.3 GitHub Actions 自动同步（可选）

在主仓库 `.github/workflows/sync-agent-data.yml`：

```yaml
name: Sync Agent Data
on:
  schedule:
    - cron: "0 9 * * *"  # 每天北京时间 9:00
  workflow_dispatch:

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Download from your NAS/cloud
        run: |
          # 把 local_agent_output/kos 同步到 public/data
          echo "implement your sync here"
      - name: Commit and push
        run: |
          git config user.name "Agent Bot"
          git config user.email "agent@kos.local"
          git add public/data
          git commit -m "chore: update agent data $(date -I)" || true
          git push
```

---

## 5. 技能提升价值

这个本地 Agent 本身就是一个**高质量的练手项目**，对以下能力有直接提升：

| 能力维度 | 具体锻炼点 |
|----------|-----------|
| **Python 工程化** | 模块化设计、配置管理、日志、异常处理、类型提示 |
| **IMAP/邮件协议** | 真实协议交互、MIME 解码、HTML 邮件解析 |
| **数据工程** | ETL、去重、结构化、JSON/Markdown 输出 |
| **自动化运维** | Windows 任务计划、cron、GitHub Actions |
| **安全实践** | 凭据管理、环境变量、最小权限原则 |
| **前端/全栈** | KOS 数据消费、Next.js SSG/ISR、API 设计 |
| **学术研究** | 数据集维护、可复现研究、开源项目治理 |
| **移民政策研究** | 多源信息聚合、变化检测、政策分析 |

**可写进 CV 的成果**：

> **Wang Private Local Agent** — A self-hosted Python automation system that monitors SEEK NZ job alerts, EURAXESS PhD positions, and skilled immigration policy changes across 10+ OECD countries. Integrates with my personal academic website (KOS) for real-time research intelligence display.

---

## 6. 安全与责任

- **密码**：永远不要把 QQ 主密码写进代码。用应用专用密码 + 环境变量。
- **网络**：QQ IMAP 在国内通常可直接连接；如遇问题可配置代理。
- **频率**：不要高频拉取邮件，建议每天 1-2 次，避免触发服务商限制。
- **数据**：邮件内容可能含个人隐私，输出文件不要公开到不可信的云。

---

## 7. 后续扩展计划

- [ ] `scan_german_phd_agent.py`：把现有 `scan_german_phd.py` 接入本地 agent 架构
- [ ] `policy_tracker_agent.py`：把 `global_policy_tracker.py` 接入本地 agent 架构
- [ ] Web UI：用 Streamlit / Gradio 做一个本地看板
- [ ] 告警通知：变化时发送邮件/企业微信/Slack
- [ ] 数据库存储：SQLite → PostgreSQL（长期）
- [x] KOS 页面：新增 `/intelligence` 实时展示 agent 结果

---

**一句话总结**：这就是你自己的数字劳工，24小时帮你扫邮件、盯政策、找博士岗位，产出还能直接挂到 KOS 上当学术成果展示。
