"""
实时行情监控模块
"""
import time
import schedule
from typing import List, Callable
from datetime import datetime
from data.fetcher import DataFetcher
from strategy.base import BaseStrategy, SignalType
from trader.executor import TradeExecutor
from config.settings import MonitorConfig
from utils.logger import log


class RealtimeMonitor:
    """实时行情监控器"""
    
    def __init__(
        self,
        strategy: BaseStrategy,
        executor: TradeExecutor,
        symbols: List[str],
        config: MonitorConfig = None
    ):
        self.strategy = strategy
        self.executor = executor
        self.symbols = symbols
        self.config = config or MonitorConfig()
        self.fetcher = DataFetcher()
        self.is_running = False
        self._history_cache = {}
    
    def is_trading_time(self) -> bool:
        """判断是否在交易时间"""
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        
        for start, end in self.config.trading_hours:
            if start <= current_time <= end:
                return True
        return False
    
    def _load_history(self, symbol: str, days: int = 60):
        """加载历史数据用于策略计算"""
        if symbol not in self._history_cache:
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - pd.Timedelta(days=days)).strftime("%Y-%m-%d")
            self._history_cache[symbol] = self.fetcher.get_stock_history(
                symbol, start_date, end_date
            )
        return self._history_cache[symbol]
    
    def check_signals(self):
        """检查所有标的的信号"""
        if not self.is_trading_time():
            log.debug("非交易时间，跳过信号检查")
            return
        
        log.info("开始检查交易信号...")
        quotes = self.fetcher.get_realtime_quote(self.symbols)
        
        for symbol in self.symbols:
            try:
                # 获取历史数据
                history = self._load_history(symbol)
                if history.empty:
                    continue
                
                # 获取实时价格并更新
                quote = quotes[quotes["代码"] == symbol]
                if not quote.empty:
                    current_price = float(quote["最新价"].values[0])
                    # 将实时价格追加到历史数据
                    import pandas as pd
                    new_row = pd.DataFrame({
                        "open": [current_price],
                        "high": [current_price],
                        "low": [current_price],
                        "close": [current_price],
                        "volume": [0]
                    }, index=[pd.Timestamp.now()])
                    history = pd.concat([history, new_row])
                
                # 计算信号
                signal = self.strategy.calculate_signals(history, symbol)
                
                if signal.signal_type != SignalType.HOLD:
                    log.info(f"检测到信号: {symbol} - {signal.signal_type.value}, 原因: {signal.reason}")
                    
                    # 计算交易数量
                    if signal.signal_type == SignalType.BUY:
                        balance = self.executor.get_balance()
                        available = balance.get("可用金额", 0)
                        max_amount = available * self.executor.config.max_position_pct
                        signal.quantity = int(max_amount / current_price / 100) * 100
                    else:
                        positions = self.executor.get_positions()
                        for pos in positions:
                            if pos.get("证券代码") == symbol:
                                signal.quantity = int(pos.get("可用余额", 0))
                                break
                    
                    # 执行交易
                    if signal.quantity and signal.quantity > 0:
                        self.executor.execute_signal(signal)
                        
            except Exception as e:
                log.error(f"处理 {symbol} 信号时出错: {e}")
    
    def start(self):
        """启动监控"""
        log.info(f"启动实时监控，标的: {self.symbols}")
        self.is_running = True
        
        # 设置定时任务
        schedule.every(self.config.refresh_interval).seconds.do(self.check_signals)
        
        try:
            while self.is_running:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """停止监控"""
        self.is_running = False
        schedule.clear()
        log.info("实时监控已停止")
