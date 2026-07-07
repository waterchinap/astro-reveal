"""
使用 curl 执行批量下载脚本
读取 TOML 配置文件，依次执行 curl 命令下载文件
"""

import subprocess
import time
import random
import shlex
import tomllib
from pathlib import Path
from typing import Annotated
from datetime import datetime

import typer
from loguru import logger
from pydantic import BaseModel, Field, ValidationError

app = typer.Typer()


class DownloadTask(BaseModel):
    """单个下载任务"""
    filename: str = Field(..., description="保存的文件名")
    curl_command: str = Field(..., description="完整的 curl 命令")


class DownloadConfig(BaseModel):
    """下载配置"""
    tasks: list[DownloadTask] = Field(..., description="下载任务列表")
    output_dir: str = Field("./downloads", description="输出目录")
    delay_min: float = Field(1.0, description="最小延迟秒数")
    delay_max: float = Field(3.0, description="最大延迟秒数")
    retry_times: int = Field(2, description="失败重试次数")


def load_config(config_path: Path) -> DownloadConfig:
    """加载并验证 TOML 配置文件"""
    if not config_path.exists():
        logger.error(f"配置文件不存在: {config_path}")
        raise typer.Exit(code=1)

    with open(config_path, 'rb') as f:
        data = tomllib.load(f)

    try:
        config = DownloadConfig(**data)
    except ValidationError as e:
        logger.error(f"配置文件格式错误:\n{e}")
        raise typer.Exit(code=1)

    return config

def execute_curl(curl_command: str, output_path: Path) -> bool:
    """执行 curl 命令下载文件"""
    # 替换输出路径占位符
    command = curl_command.replace("{output}", str(output_path))

    # 2. 使用 shlex.split 将命令字符串分割成列表
    # 这可以正确处理带引号的参数和空格
    try:
        command_list = shlex.split(command)
    except ValueError as e:
        logger.error(f"命令解析失败: {e}")
        return False

    logger.debug(f"执行命令: {' '.join(command_list[:10])}...") # 只打印前几个参数用于调试

    try:
        # 3. 传入命令列表，而不是字符串
        # 注意：这里不需要 shell=True
        result = subprocess.run(
            command_list,
            capture_output=True,
            text=True,
            timeout=300,
        )

        if result.returncode == 0:
            return True
        else:
            logger.error(f"curl 执行失败 (返回码: {result.returncode})")
            if result.stderr:
                logger.error(f"错误信息: {result.stderr[:500]}")
            return False

    except subprocess.TimeoutExpired:
        logger.error("命令执行超时")
        return False
    except Exception as e:
        logger.error(f"执行异常: {e}")
        return False

def download_with_retry(task: DownloadTask, output_path: Path, retry_times: int) -> bool:
    """带重试的下载"""
    for attempt in range(1, retry_times + 2):  # 初始 + retry_times 次重试
        if attempt > 1:
            wait_time = attempt * 5  # 递增等待
            logger.warning(f"第 {attempt-1} 次重试，等待 {wait_time} 秒...")
            time.sleep(wait_time)

        logger.info(f"下载尝试 {attempt}/{retry_times + 1}: {task.filename}")
        if execute_curl(task.curl_command, output_path):
            # 验证文件是否真的下载成功
            if output_path.exists() and output_path.stat().st_size > 0:
                size_kb = output_path.stat().st_size / 1024
                logger.success(f"下载成功: {output_path} ({size_kb:.1f} KB)")
                return True
            else:
                logger.warning("文件大小为0或不存在，视为失败")
        else:
            logger.warning("下载失败")

    return False


@app.command()
def run(
    config_file: Annotated[str, typer.Argument(..., help="TOML 配置文件路径")],
    output_dir: Annotated[str | None, typer.Option("--output", "-o", help="覆盖输出目录")] = None,
    dry_run: Annotated[bool, typer.Option("--dry-run", help="只打印不执行")] = False,
):
    """根据 TOML 配置文件执行批量下载"""
    config_path = Path(config_file)
    config = load_config(config_path)

    # 确定输出目录
    out_dir = Path(output_dir) if output_dir else Path(config.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"加载配置: {config_path}")
    logger.info(f"共 {len(config.tasks)} 个下载任务")
    logger.info(f"输出目录: {out_dir.resolve()}")

    success_count = 0
    fail_count = 0

    for i, task in enumerate(config.tasks, 1):
        logger.info(f"\n[{i}/{len(config.tasks)}] 处理: {task.filename}")

        date_prefix = datetime.now().strftime("%Y%m%d")  # 生成类似 "20260706" 的日期前缀
        output_path = out_dir / f"{date_prefix}_{task.filename}"
        if dry_run:
            logger.info(f"[DRY RUN] 将下载到: {output_path}")
            logger.info(f"[DRY RUN] 命令: {task.curl_command[:300]}...")
            success_count += 1
            continue

        # 检查文件是否已存在
        if output_path.exists() and output_path.stat().st_size > 0:
            logger.info(f"文件已存在，跳过: {output_path}")
            success_count += 1
            continue

        # 执行下载
        if download_with_retry(task, output_path, config.retry_times):
            success_count += 1
        else:
            fail_count += 1
            logger.error(f"下载失败: {task.filename}")

        # 任务间延迟
        if i < len(config.tasks):
            delay = random.uniform(config.delay_min, config.delay_max)
            logger.debug(f"等待 {delay:.1f} 秒...")
            time.sleep(delay)

    # 汇总报告
    logger.info("\n" + "=" * 50)
    logger.info(f"下载完成: 成功 {success_count}, 失败 {fail_count}, 总计 {len(config.tasks)}")
    if fail_count > 0:
        logger.warning("部分文件下载失败，请检查网络或重试")
        raise typer.Exit(code=1)


@app.command()
def validate(
    config_file: Annotated[str, typer.Argument(..., help="TOML 配置文件路径")],
):
    """验证 TOML 配置文件格式"""
    config_path = Path(config_file)
    try:
        config = load_config(config_path)
        logger.success(f"配置文件验证通过")
        logger.info(f"任务数量: {len(config.tasks)}")
        for task in config.tasks:
            logger.info(f"  - {task.filename}")
    except Exception as e:
        logger.error(f"配置文件验证失败: {e}")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
