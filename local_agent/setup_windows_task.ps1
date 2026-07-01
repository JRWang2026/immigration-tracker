# setup_windows_task.ps1
# 创建 Windows 任务计划，每天 8:00 运行本地 SEEK NZ Agent
# 需要以管理员身份运行 PowerShell

$TaskName = "WangPrivateAgent_SEEK_NZ"
$PythonExe = "C:\Users\Mr_Wang\.workbuddy\binaries\python\envs\default\Scripts\python.exe"
$AgentScript = "C:\Users\Mr_Wang\WorkBuddy\2026-06-20-14-48-36\local_agent\seek_email_agent.py"
$WorkingDir = "C:\Users\Mr_Wang\WorkBuddy\2026-06-20-14-48-36\local_agent"

# 检查环境变量是否已设置
$User = [System.Environment]::GetEnvironmentVariable("QQ_MAIL_USER", "User")
$Pass = [System.Environment]::GetEnvironmentVariable("QQ_MAIL_APP_PASSWORD", "User")
$GitHubToken = [System.Environment]::GetEnvironmentVariable("GITHUB_TOKEN", "User")

if (-not $User -or -not $Pass) {
    Write-Host "⚠️ QQ Mail 环境变量未设置。请先运行以下命令（替换为你的真实密码）：" -ForegroundColor Yellow
    Write-Host "   [System.Environment]::SetEnvironmentVariable('QQ_MAIL_USER', '349376374@qq.com', 'User')"
    Write-Host "   [System.Environment]::SetEnvironmentVariable('QQ_MAIL_APP_PASSWORD', 'your_app_password', 'User')"
    exit 1
}

if (-not $GitHubToken) {
    Write-Host "⚠️ GITHUB_TOKEN 未设置，Agent 仍可运行但无法自动推送到 GitHub。" -ForegroundColor Yellow
    Write-Host "   如需自动闭环，请运行：" -ForegroundColor Yellow
    Write-Host "   [System.Environment]::SetEnvironmentVariable('GITHUB_TOKEN', 'ghp_xxxxxxxx', 'User')"
}

# 任务动作：运行 Python 脚本
$Action = New-ScheduledTaskAction -Execute $PythonExe -Argument "`"$AgentScript`"" -WorkingDirectory $WorkingDir

# 触发器：每天 8:00
$Trigger = New-ScheduledTaskTrigger -Daily -At "08:00"

# 设置：允许唤醒运行、错过任务尽快启动、隐藏模式
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# 主体：当前用户，登录时运行（不需要管理员）
$Principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive

# 注册任务
Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Principal $Principal -Force

Write-Host "✅ 任务 '$TaskName' 已创建。每天 8:00 运行。"
Write-Host "   查看/修改：任务计划程序 -> 任务计划程序库 -> $TaskName"
