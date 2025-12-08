"""
策略基类 - 所有策略需继承此类
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List, Dict
from enum import Enum
import pandas as pd


class SignalType(Enum):
    """信号类型"""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"


@dataclass
class Signal:
    """交易信号"""
    symbol: str
    signal_type: SignalType
    price: float
    quantity: Optional[int] = None
    reason: str = ""
    timestamp: Optional[str] = None


class BaseStrategy(ABC):
    """策略基类"""
    
    def __init__(self, name: str, params: Dict = None):
        self.name = name
        self.params = params or {}
        self.positions: Dict[str, int] = {}  # 当前持仓
    
    @abstractmethod
    def calculate_signals(self, data: pd.DataFrame, symbol: str) -> Signal:
        """
        计算交易信号 - 子类必须实现
        
        Args:
            data: 行情数据
            symbol: 股票代码
            
        Returns:
            Signal: 交易信号
        """
        pass
    
    def on_bar(self, data: pd.DataFrame, symbol: str) -> Signal:
        """每根K线触发"""
        return self.calculate_signals(data, symbol)
    
    def update_position(self, symbol: str, quantity: int):
        """更新持仓"""
        self.positions[symbol] = self.positions.get(symbol, 0) + quantity
        if self.positions[symbol] <= 0:
            self.positions.pop(symbol, None)
    
    def get_position(self, symbol: str) -> int:
        """获取持仓"""
        return self.positions.get(symbol, 0)