#Requires -Version 5.1
<#
.SYNOPSIS
    一键创建 GitHub 仓库并完成首次推送，建立本地 Agent -> GitHub -> KOS Pages 的自动闭环。

.DESCRIPTION
    1. 读取环境变量 GITHUB_TOKEN（classic PAT，需要 repo 权限）。
    2. 在 GitHub 上创建公开仓库 immigration-tracker。
    3. 初始化本地 git（如尚未初始化）。
    4. 添加 remote 并推送 main 分支。
    5. 提示用户到仓库 Settings -> Pages 启用 GitHub Actions 部署源。

.PARAMETER RepoName
    仓库名，默认 immigration-tracker。

.PARAMETER Owner
    GitHub 用户名，默认 JRWang2026。

.EXAMPLE
    $env:GITHUB_TOKEN = "ghp_xxxxxxxxxxxxxxxxxxxx"
    .\setup-github-repo.ps1
#>
param(
    [string]$RepoName = "immigration-tracker",
    [string]$Owner = "JRWang2026"
)

$ErrorActionPreference = "Stop"

$token = $env:GITHUB_TOKEN
if (-not $token) {
    Write-Error "请先在环境变量中设置 GITHUB_TOKEN。获取方式：GitHub -> Settings -> Developer settings -> Personal access tokens -> Tokens (classic)，勾选 repo 权限。"
    exit 1
}

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Resolve-Path $repoRoot

# 1. 创建 GitHub 仓库
$headers = @{
    "Authorization" = "token $token"
    "Accept"        = "application/vnd.github.v3+json"
}
$body = @{
    name        = $RepoName
    description = "Private local agent + KOS website for NZ Green List job tracking, German PhD scanning, and global immigration policy monitoring."
    private     = $false
    auto_init   = $false
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "https://api.github.com/user/repos" -Method POST -Headers $headers -Body $body
    Write-Host "✅ GitHub 仓库已创建：$($response.html_url)" -ForegroundColor Green
}
catch {
    if ($_.Exception.Response.StatusCode -eq 422) {
        Write-Host "⚠️ 仓库 $RepoName 可能已存在，跳过创建。" -ForegroundColor Yellow
    }
    else {
        throw
    }
}

# 2. 初始化本地 git
Set-Location $repoRoot
if (-not (Test-Path ".git")) {
    git init
    git branch -M main
}

# 3. 配置 user（如未配置）
$email = git config user.email
if (-not $email) { git config user.email "WJR2026@hotmail.com" }
$name = git config user.name
if (-not $name) { git config user.name "Wang Private Agent" }

# 4. 配置带 token 的 remote
$remoteUrl = "https://$token@github.com/$Owner/$RepoName.git"
git remote remove origin 2>$null
git remote add origin $remoteUrl

# 5. 提交并推送
git add .
$hasChanges = git status --porcelain
if ($hasChanges) {
    git commit -m "Initial commit: local agent + KOS + data feeds"
}
else {
    Write-Host "ℹ️ 没有待提交变更。" -ForegroundColor Cyan
}

git pull origin main --rebase 2>$null
git push -u origin main

Write-Host "`n🚀 首次推送完成！`n" -ForegroundColor Green
Write-Host "下一步（只需做一次）：" -ForegroundColor Cyan
Write-Host "1. 打开 https://github.com/$Owner/$RepoName/settings/pages"
Write-Host "2. Source 选择 'GitHub Actions'"
Write-Host "3. 回到仓库主页，点击 Actions 标签查看部署状态"
Write-Host "4. 设置环境变量 GITHUB_TOKEN 到 Windows 系统环境变量，并重启任务计划程序，实现每日自动推送。"
