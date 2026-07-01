"""
本地 Agent 调度器

两种运行模式：
1. schedule 模式：Python 进程常驻，按 cron 时间循环执行；
2. Windows 任务计划模式：单次运行脚本，由系统 scheduler 触发（推荐，更稳定省电）。

推荐：Windows 任务计划，因为不需要常驻 Python 进程。
"""

import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import schedule
import yaml


def run_agent(script_name: str = "seek_email_agent.py"):
    """运行指定 agent 脚本并记录输出。"""
    script = Path(__file__).resolve().parent / script_name
    print(f"[{datetime.now().isoformat()}] Running {script} ...")
    result = subprocess.run(
        [sys.executable, str(script)],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    print(f"[{datetime.now().isoformat()}] Exit code: {result.returncode}")
    return result.returncode


def main():
    cfg_path = Path(__file__).resolve().parent / "config.yaml"
    with open(cfg_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    sched_cfg = cfg.get("schedule", {})
    if not sched_cfg.get("enabled", False):
        print("Schedule 未启用（config.yaml schedule.enabled=false），单次运行 agent。")
        return run_agent()

    cron = sched_cfg.get("cron", "0 8 * * *")
    # 简单解析 cron：默认每天 HH:MM
    parts = cron.split()
    if len(parts) == 5:
        minute, hour = parts[0], parts[1]
    else:
        minute, hour = "0", "8"

    schedule.every().day.at(f"{hour.zfill(2)}:{minute.zfill(2)}").do(run_agent)
    print(f"调度器已启动，每天 {hour.zfill(2)}:{minute.zfill(2)} 运行。按 Ctrl+C 停止。")

    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    main()
