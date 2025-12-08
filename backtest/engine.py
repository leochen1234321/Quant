"""
回测引擎 - 基于 Hikyuu
"""
from dataclasses import dataclass
from typing import Dict, List, Optional
import pandas as pd
import numpy as np
from strategy.base import BaseStrategy, SignalType
from config.settings import BacktestConfig
from utils.logger import log


@dataclass
class BacktestResult:
    """回测结果"""
    total_return: float  # 总收益率
    annual_return: float  # 年化收益率
    sharpe_ratio: float  # 夏普比率
    max_drawdown: float  # 最大回撤
    win_rate: float  # 胜率
    trade_count: int  # 交易次数
    equity_curve: pd.Series  # 净值曲线
    trades: List[Dict]  # 交易记录


class BacktestEngine:
    """
    回测引擎
    
    支持两种模式：
    1. 简易模式：使用内置回测逻辑
    2. Hikyuu模式：使用Hikyuu进行专业回测
    """
    
    def __init__(self, config: BacktestConfig = None):
        self.config = config or BacktestConfig()
        self.trades: List[Dict] = []
        self.equity_curve: List[float] = []
    
    def run(
        self,
        strategy: BaseStrategy,
        data: pd.DataFrame,
        symbol: str
    ) -> BacktestResult:
        """
        运行回测
        
        Args:
            strategy: 策略实例
            data: 历史数据
            symbol: 股票代码
        """
        log.info(f"开始回测 {strategy.name} 策略，标的: {symbol}")
        
        capital = self.config.initial_capital
        position = 0
        entry_price = 0
        self.trades = []
        equity_values = []
        
        for i in range(len(data)):
            current_data = data.iloc[:i+1]
            if len(current_data) < 2:
                equity_values.append(capital)
                continue
            
            current_price = current_data["close"].iloc[-1]
            signal = strategy.calculate_signals(current_data, symbol)
            
            # 处理买入信号
            if signal.signal_type == SignalType.BUY and position == 0:
                # 计算可买数量（考虑手续费）
                available = capital * (1 - self.config.commission_rate)
                quantity = int(available / current_price / 100) * 100
                
                if quantity > 0:
                    cost = quantity * current_price * (1 + self.config.commission_rate)
                    capital -= cost
                    position = quantity
                    entry_price = current_price
                    
                    self.trades.append({
                        "date": current_data.index[-1],
                        "action": "BUY",
                        "price": current_price,
                        "quantity": quantity,
                        "reason": signal.reason
                    })
                    log.debug(f"买入 {symbol}: {quantity}股 @ {current_price}")
            
            # 处理卖出信号
            elif signal.signal_type == SignalType.SELL and position > 0:
                revenue = position * current_price * (1 - self.config.commission_rate)
                capital += revenue
                
                profit = (current_price - entry_price) / entry_price
                self.trades.append({
                    "date": current_data.index[-1],
                    "action": "SELL",
                    "price": current_price,
                    "quantity": position,
                    "profit": profit,
                    "reason": signal.reason
                })
                log.debug(f"卖出 {symbol}: {position}股 @ {current_price}, 收益: {profit:.2%}")
                position = 0
            
            # 计算当前净值
            current_equity = capital + position * current_price
            equity_values.append(current_equity)
        
        # 计算回测指标
        equity_curve = pd.Series(equity_values, index=data.index)
        result = self._calculate_metrics(equity_curve)
        
        log.info(f"回测完成 - 总收益: {result.total_return:.2%}, 夏普: {result.sharpe_ratio:.2f}, 最大回撤: {result.max_drawdown:.2%}")
        return result
    
    def _calculate_metrics(self, equity_curve: pd.Series) -> BacktestResult:
        """计算回测指标"""
        returns = equity_curve.pct_change().dropna()
        
        # 总收益率
        total_return = (equity_curve.iloc[-1] - equity_curve.iloc[0]) / equity_curve.iloc[0]
        
        # 年化收益率
        days = (equity_curve.index[-1] - equity_curve.index[0]).days
        annual_return = (1 + total_return) ** (365 / max(days, 1)) - 1
        
        # 夏普比率 (假设无风险利率3%)
        risk_free_rate = 0.03
        excess_returns = returns - risk_free_rate / 252
        sharpe_ratio = np.sqrt(252) * excess_returns.mean() / (excess_returns.std() + 1e-10)
        
        # 最大回撤
        cummax = equity_curve.cummax()
        drawdown = (equity_curve - cummax) / cummax
        max_drawdown = abs(drawdown.min())
        
        # 胜率
        profitable_trades = [t for t in self.trades if t.get("profit", 0) > 0]
        sell_trades = [t for t in self.trades if t["action"] == "SELL"]
        win_rate = len(profitable_trades) / max(len(sell_trades), 1)
        
        return BacktestResult(
            total_return=total_return,
            annual_return=annual_return,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            win_rate=win_rate,
            trade_count=len(self.trades),
            equity_curve=equity_curve,
            trades=self.trades
        )
    
    def run_with_hikyuu(self, strategy: BaseStrategy, symbol: str) -> BacktestResult:
        """
        使用Hikyuu进行回测（需要先初始化Hikyuu）
        
        这里提供接口，具体实现需要根据Hikyuu的API进行适配
        """
        try:
            import hikyuu as hku
            # TODO: 实现Hikyuu回测逻辑
            # hku.init()
            # ...
            log.info("Hikyuu回测模式（待实现）")
        except ImportError:
            log.warning("Hikyuu未安装，使用内置回测引擎")
        
        return None
