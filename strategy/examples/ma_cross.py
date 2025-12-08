"""
均线交叉策略示例
"""
import pandas as pd
from strategy.base import BaseStrategy, Signal, SignalType


class MACrossStrategy(BaseStrategy):
    """
    双均线交叉策略
    - 短期均线上穿长期均线：买入
    - 短期均线下穿长期均线：卖出
    """
    
    def __init__(self, short_period: int = 5, long_period: int = 20):
        super().__init__(
            name="MA_Cross",
            params={"short": short_period, "long": long_period}
        )
        self.short_period = short_period
        self.long_period = long_period
    
    def calculate_signals(self, data: pd.DataFrame, symbol: str) -> Signal:
        if len(data) < self.long_period + 1:
            return Signal(symbol=symbol, signal_type=SignalType.HOLD, price=0)
        
        # 计算均线
        data = data.copy()
        data["ma_short"] = data["close"].rolling(self.short_period).mean()
        data["ma_long"] = data["close"].rolling(self.long_period).mean()
        
        # 获取最近两根K线的均线值
        curr_short = data["ma_short"].iloc[-1]
        curr_long = data["ma_long"].iloc[-1]
        prev_short = data["ma_short"].iloc[-2]
        prev_long = data["ma_long"].iloc[-2]
        
        current_price = data["close"].iloc[-1]
        
        # 金叉买入
        if prev_short <= prev_long and curr_short > curr_long:
            return Signal(
                symbol=symbol,
                signal_type=SignalType.BUY,
                price=current_price,
                reason=f"MA{self.short_period}上穿MA{self.long_period}"
            )
        
        # 死叉卖出
        if prev_short >= prev_long and curr_short < curr_long:
            return Signal(
                symbol=symbol,
                signal_type=SignalType.SELL,
                price=current_price,
                reason=f"MA{self.short_period}下穿MA{self.long_period}"
            )
        
        return Signal(symbol=symbol, signal_type=SignalType.HOLD, price=current_price)
