"""
全局配置管理
"""
from dataclasses import dataclass, field
from typing import Dict, List
from enum import Enum


class BrokerType(Enum):
    """券商类型"""
    TONGHUASHUN = "ths"
    DONGCAIFU = "gj"  # 国金/东财


@dataclass
class BacktestConfig:
    """回测配置"""
    start_date: str = "2023-01-01"
    end_date: str = "2023-12-10"
    initial_capital: float = 1_000_000.0
    commission_rate: float = 0.0003  # 万三佣金
    slippage: float = 0.001  # 滑点


@dataclass
class TradingConfig:
    """交易配置"""
    broker: BrokerType = BrokerType.TONGHUASHUN
    exe_path: str = ""  # 客户端路径
    max_position_pct: float = 0.3  # 单只股票最大仓位
    stock_pool: List[str] = field(default_factory=list)


@dataclass
class MonitorConfig:
    """监控配置"""
    refresh_interval: int = 3  # 行情刷新间隔（秒）
    trading_hours: tuple = (("09:30", "11:30"), ("13:00", "15:00"))


@dataclass
class Config:
    """主配置类"""
    backtest: BacktestConfig = field(default_factory=BacktestConfig)
    trading: TradingConfig = field(default_factory=TradingConfig)
    monitor: MonitorConfig = field(default_factory=MonitorConfig)


# 全局配置实例
config = Config()

