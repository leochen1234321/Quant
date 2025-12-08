"""
日志管理模块
"""
import os

# 清除代理环境变量
for key in list(os.environ.keys()):
    if 'proxy' in key.lower():
        del os.environ[key]

from loguru import logger
import sys
from pathlib import Path


def setup_logger(log_dir: str = "logs"):
    """配置日志"""
    Path(log_dir).mkdir(exist_ok=True)
    
    # 移除默认handler
    logger.remove()
    
    # 控制台输出
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO"
    )
    
    # 文件输出
    logger.add(
        f"{log_dir}/trading_{{time:YYYY-MM-DD}}.log",
        rotation="00:00",
        retention="30 days",
        level="DEBUG"
    )
    
    return logger


log = setup_logger()
