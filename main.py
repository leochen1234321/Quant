"""
A股量化交易系统 - 主程序入口

工作流程：
1. 使用Hikyuu进行历史数据快速回测
2. 验证策略有效性（收益率、夏普比率等）
3. 策略通过后，使用easytrader连接同花顺/东方财富
4. 实时监控行情（akshare获取）
5. 根据策略信号自动执行买卖
"""
import argparse
from config.settings import config, BrokerType
from data.fetcher import DataFetcher
from backtest.engine import BacktestEngine
from strategy.examples.ma_cross import MACrossStrategy
from trader.executor import TradeExecutor
from monitor.realtime import RealtimeMonitor
from utils.logger import log


def run_backtest(symbols: list, strategy=None):
    """运行回测"""
    log.info("=" * 50)
    log.info("开始回测模式")
    log.info("=" * 50)
    
    fetcher = DataFetcher()
    engine = BacktestEngine(config.backtest)
    strategy = strategy or MACrossStrategy(short_period=5, long_period=20)
    
    results = {}
    for symbol in symbols:
        log.info(f"\n回测标的: {symbol}")
        
        # 获取历史数据
        data = fetcher.get_stock_history(
            symbol,
            config.backtest.start_date,
            config.backtest.end_date
        )
        
        if data.empty:
            log.warning(f"无法获取 {symbol} 的历史数据")
            continue
        
        # 运行回测
        result = engine.run(strategy, data, symbol)
        results[symbol] = result
        
        # 打印结果
        print(f"\n{'='*40}")
        print(f"回测结果 - {symbol}")
        print(f"{'='*40}")
        print(f"总收益率:   {result.total_return:>10.2%}")
        print(f"年化收益率: {result.annual_return:>10.2%}")
        print(f"夏普比率:   {result.sharpe_ratio:>10.2f}")
        print(f"最大回撤:   {result.max_drawdown:>10.2%}")
        print(f"胜率:       {result.win_rate:>10.2%}")
        print(f"交易次数:   {result.trade_count:>10d}")
        print(f"{'='*40}")
    
    return results


def run_live_trading(symbols: list, strategy=None):
    """运行实盘交易"""
    log.info("=" * 50)
    log.info("开始实盘交易模式")
    log.info("=" * 50)
    
    strategy = strategy or MACrossStrategy(short_period=5, long_period=20)
    
    # 初始化交易执行器
    executor = TradeExecutor(config.trading)
    
    if not executor.connect():
        log.error("无法连接交易客户端，退出")
        return
    
    try:
        # 显示账户信息
        balance = executor.get_balance()
        log.info(f"账户资金: {balance}")
        
        positions = executor.get_positions()
        log.info(f"当前持仓: {positions}")
        
        # 启动实时监控
        monitor = RealtimeMonitor(
            strategy=strategy,
            executor=executor,
            symbols=symbols,
            config=config.monitor
        )
        
        monitor.start()
        
    except KeyboardInterrupt:
        log.info("收到中断信号")
    finally:
        executor.disconnect()


def main():
    parser = argparse.ArgumentParser(description="A股量化交易系统")
    parser.add_argument(
        "--mode", 
        choices=["backtest", "live"], 
        default="backtest",
        help="运行模式: backtest(回测) 或 live(实盘)"
    )
    parser.add_argument(
        "--symbols",
        nargs="+",
        default=["000001", "600519"],
        help="股票代码列表"
    )
    parser.add_argument(
        "--broker",
        choices=["ths", "gj"],
        default="ths",
        help="券商类型: ths(同花顺) 或 gj(国金/东财)"
    )
    
    args = parser.parse_args()
    
    # 更新配置
    if args.broker == "gj":
        config.trading.broker = BrokerType.DONGCAIFU
    
    log.info(f"运行模式: {args.mode}")
    log.info(f"交易标的: {args.symbols}")
    
    if args.mode == "backtest":
        run_backtest(args.symbols)
    else:
        run_live_trading(args.symbols)


if __name__ == "__main__":
    main()
