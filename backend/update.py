"""
每日自动更新脚本 - 带重试机制的 git push
"""

import subprocess
import sys
import time
import logging
from pathlib import Path
from datetime import datetime

# ============ 配置 ============
PROJECT_DIR = Path("/home/eric/00works/astro-reveal/backend")  # 改成你的项目路径
PDIR = PROJECT_DIR.parent
LOG_FILE = Path.home() / "daily_update.log"
MAX_RETRIES = 5
RETRY_DELAY_BASE = 5  # 基础延迟秒数，会递增
# ==============================

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def run_cmd(cmd: list, cwd: Path = None, check: bool = False) -> tuple:
    """执行命令，返回 (成功与否, 输出)"""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=check
        )
        output = result.stdout + result.stderr
        return result.returncode == 0, output.strip()
    except subprocess.CalledProcessError as e:
        return False, e.stderr.strip()


def git_add(cwd: Path) -> bool:
    """git add ."""
    logger.info("▶️  git add .")
    success, output = run_cmd(["git", "add", "."], cwd)
    if not success:
        logger.error(f"❌ git add 失败: {output}")
    return success


def git_commit(cwd: Path, message: str = "daily update") -> tuple:
    """git commit，返回 (是否有变更, 是否成功)"""
    # 先检查是否有变更
    success, output = run_cmd(["git", "diff", "--cached", "--quiet"], cwd)
    if success:
        logger.info("⏭️  没有变更需要提交，跳过")
        return False, True  # 无变更，视为成功

    logger.info("▶️  git commit")
    success, output = run_cmd(["git", "commit", "-m", message], cwd)
    if not success:
        logger.error(f"❌ git commit 失败: {output}")
        return True, False
    logger.info("✅ git commit 成功")
    return True, True


def git_push_with_retry(cwd: Path) -> bool:
    """带重试的 git push"""
    logger.info("▶️  git push (带重试)")

    for attempt in range(1, MAX_RETRIES + 1):
        delay = RETRY_DELAY_BASE * attempt  # 5, 10, 15, 20, 25 秒
        logger.info(f"  尝试 push {attempt}/{MAX_RETRIES}...")

        success, output = run_cmd(["git", "push"], cwd)
        if success:
            logger.info("✅ git push 成功")
            return True

        # 判断是否是网络相关错误
        error_lower = output.lower()
        is_network_error = any(keyword in error_lower for keyword in [
            "connection", "timeout", "reset", "refused",
            "network", "unreachable", "could not read", "ssl"
        ])

        if attempt < MAX_RETRIES:
            if is_network_error:
                logger.warning(f"  ⚠️ 网络错误，{delay}秒后重试...")
            else:
                logger.warning(f"  ⚠️ push 失败 (非网络错误)，{delay}秒后重试...")
                logger.debug(f"  错误信息: {output}")
            time.sleep(delay)
        else:
            logger.error(f"💀 push 重试 {MAX_RETRIES} 次后仍然失败")
            logger.error(f"  最后错误: {output}")

    return False


def send_notification(message: str, webhook_url: str = None):
    """发送通知（可选）"""
    if webhook_url:
        try:
            import requests
            requests.post(
                webhook_url,
                json={"msgtype": "text", "text": {"content": message}},
                timeout=5
            )
        except Exception as e:
            logger.warning(f"发送通知失败: {e}")

    # 也可以发邮件
    # import smtplib
    # from email.mime.text import MIMEText
    # ...


def main():
    logger.info("=" * 50)
    logger.info("🚀 开始每日更新任务")

    # 1. 检查项目目录
    if not PROJECT_DIR.exists():
        logger.error(f"❌ 项目目录不存在: {PROJECT_DIR}")
        sys.exit(1)

    # 2. 执行 update.py
    logger.info("▶️  执行 qieman.py...")
    success, output = run_cmd(["uv", "run",  "qieman.py"], cwd=PROJECT_DIR)
    if not success:
        logger.error(f"❌ update.py 执行失败: {output}")
        sys.exit(1)
    logger.info("✅ qieman.py 执行成功")

    # 3. git add
    if not git_add(PDIR):
        sys.exit(1)

    # 4. git commit
    has_changes, success = git_commit(PDIR)
    if not success:
        sys.exit(1)
    if not has_changes:
        logger.info("🎉 无变更，任务结束")
        return

    # 5. git push (带重试)
    if not git_push_with_retry(PDIR):
        # 失败通知
        send_notification(
            f"⚠️ 每日更新 push 失败\n目录: {PDIR}\n请手动处理"
        )
        sys.exit(1)

    logger.info("🎉 全部完成")


if __name__ == "__main__":
    main()
