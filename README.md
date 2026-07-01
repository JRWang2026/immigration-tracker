# Immigration Tracker — 自动闭环情报系统

私人本地 Agent + KOS 学术网站 + GitHub Actions 的自动闭环系统。

- **SEEK NZ 绿名单岗位扫描**：每日从 QQ Mail 拉取 SEEK 推送，按新西兰绿名单 Tier1 ICT 评分。
- **德国博士岗位扫描**：聚合 EURAXESS / academics.de 信息科学/专利分析/竞争情报方向岗位。
- **全球移民政策追踪**：监控 OECD 主要国家技术移民政策变化。
- **KOS 网站自动部署**：数据更新 → GitHub commit → GitHub Actions 构建 → GitHub Pages 上线。

## 仓库结构

```
.
├── .github/workflows/deploy.yml   # GitHub Actions：构建 KOS 并部署到 Pages
├── local_agent/                    # Python 本地 Agent
│   ├── config.yaml                 # Agent 配置
│   ├── seek_email_agent.py         # SEEK NZ 主流程
│   ├── scan_german_phd.py          # 德国博士岗位扫描
│   ├── kos_bridge.py               # KOS 数据桥接
│   ├── git_pusher.py               # 自动 commit + push
│   └── ...
├── kos/                            # Next.js 学术网站（静态导出）
│   ├── app/                        # 页面
│   ├── components/                 # 组件（含 IntelligenceDashboard）
│   ├── public/data/                # 网站运行时读取的 JSON 数据
│   └── ...
├── data/                           # Agent 生成的数据（repo 主数据源）
│   ├── seek-nz/latest.json
│   ├── reports/
│   └── raw/
├── reports/                        # Markdown 扫描报告
└── setup-github-repo.ps1           # 首次创建仓库并推送脚本
```

## 自动闭环流程

```text
Windows 任务计划程序（每日 8:00）
        │
        ▼
┌─────────────────┐
│ local_agent     │ 扫描邮件 / 网站
│ Python scripts  │
└────────┬────────┘
         │ 生成 data/seek-nz/latest.json
         │      reports/
         ▼
┌─────────────────┐
│ git_pusher.py   │ git add / commit / push
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ GitHub repo     │ main 分支更新
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ GitHub Actions  │ 同步 data -> kos/public/data
│ deploy.yml      │ npm ci && npm run build
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ GitHub Pages    │ https://jrwang2026.github.io/immigration-tracker
└─────────────────┘
```

## 首次部署步骤

1. **获取 GitHub Personal Access Token**
   - GitHub -> Settings -> Developer settings -> Personal access tokens -> Tokens (classic)
   - 勾选 `repo` 权限
   - 复制 token（以 `ghp_` 开头）

2. **运行一键部署脚本**
   ```powershell
   $env:GITHUB_TOKEN = "ghp_xxxxxxxxxxxxxxxxxxxx"
   .\setup-github-repo.ps1
   ```

3. **启用 GitHub Pages**
   - 打开 `https://github.com/JRWang2026/immigration-tracker/settings/pages`
   - Source 选择 **GitHub Actions**

4. **设置每日自动运行**
   - 确保 Windows 任务计划程序中的 `WangPrivateAgent_SEEK_NZ` 任务设置了系统环境变量 `GITHUB_TOKEN`
   - 任务每日运行后，会自动 commit + push

## 本地运行

```powershell
# 设置环境变量
$env:QQ_MAIL_USER="349376374@qq.com"
$env:QQ_MAIL_APP_PASSWORD="your_qq_app_password"

# 运行 Agent
python local_agent/seek_email_agent.py
```

## 安全说明

- 所有密码/令牌通过环境变量注入，不写入代码或配置文件。
- `setup-github-repo.ps1` 使用 HTTPS + token 的方式推送，脚本运行后 token 不会留在 remote URL（每次运行会重新配置）。
- 仓库为公开仓库，请勿提交任何包含密码、QQ 应用密码或个人隐私凭证的文件。
