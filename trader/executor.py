"""
实盘交易执行器 - 基于 easytrader
"""
from typing import Optional, Dict, List
from config.settings import TradingConfig, BrokerType
from strategy.base import Signal, SignalType
from utils.logger import log


class TradeExecutor:
    """交易执行器"""
    
    def __init__(self, config: TradingConfig = None):
        self.config = config or TradingConfig()
        self.trader = None
        self.is_connected = False
    
    def connect(self) -> bool:
        """连接交易客户端"""
        try:
            import easytrader
            
            broker_map = {
                BrokerType.TONGHUASHUN: "ths",
                BrokerType.DONGCAIFU: "gj"
            }
            
            broker = broker_map.get(self.config.broker, "ths")
            self.trader = easytrader.use(broker)
            
            if self.config.exe_path:
                self.trader.connect(self.config.exe_path)
            
            self.is_connected = True
            log.info(f"已连接交易客户端: {broker}")
            return True
            
        except Exception as e:
            log.error(f"连接交易客户端失败: {e}")
            return False
    
    def disconnect(self):
        """断开连接"""
        if self.trader:
            self.trader = None
            self.is_connected = False
            log.info("已断开交易客户端连接")
    
    def get_balance(self) -> Dict:
        """获取账户资金"""
        if not self.is_connected:
            log.warning("未连接交易客户端")
            return {}
        
        try:
            return self.trader.balance
        except Exception as e:
            log.error(f"获取资金失败: {e}")
            return {}
    
    def get_positions(self) -> List[Dict]:
        """获取持仓"""
        if not self.is_connected:
            return []
        
        try:
            return self.trader.position
        except Exception as e:
            log.error(f"获取持仓失败: {e}")
            return []
    
    def execute_signal(self, signal: Signal) -> bool:
        """
        执行交易信号
        
        Args:
            signal: 交易信号
        """
        if not self.is_connected:
            log.warning("未连接交易客户端，无法执行交易")
            return False
        
        if signal.signal_type == SignalType.HOLD:
            return True
        
        try:
            if signal.signal_type == SignalType.BUY:
                result = self._buy(signal.symbol, signal.price, signal.quantity)
            else:
                result = self._sell(signal.symbol, signal.price, signal.quantity)
            
            log.info(f"执行{signal.signal_type.value}: {signal.symbol}, 价格: {signal.price}, 数量: {signal.quantity}")
            return result
            
        except Exception as e:
            log.error(f"执行交易失败: {e}")
            return False
    
    def _buy(self, symbol: str, price: float, quantity: int) -> bool:
        """买入"""
        try:
            self.trader.buy(symbol, price=price, amount=quantity)
            return True
        except Exception as e:
            log.error(f"买入失败: {e}")
            return False
    
    def _sell(self, symbol: str, price: float, quantity: int) -> bool:
        """卖出"""
        try:
            self.trader.sell(symbol, price=price, amount=quantity)
            return True
        except Exception as e:
            log.error(f"卖出失败: {e}")
            return False
    
    def cancel_all_orders(self):
        """撤销所有挂单"""
        if self.is_connected:
            try:
                self.trader.cancel_entrusts()
                log.info("已撤销所有挂单")
            except Exception as e:
                log.error(f"撤单失败: {e}")
