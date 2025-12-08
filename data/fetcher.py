"""
数据获取模块 - 基于 akshare（使用新浪/腾讯数据源）
"""
import os

# 清除代理环境变量，确保直连
for key in list(os.environ.keys()):
    if 'proxy' in key.lower():
        del os.environ[key]

import akshare as ak
import pandas as pd
from typing import List
from utils.logger import log


class DataFetcher:
    """数据获取器"""
    
    @staticmethod
    def get_stock_history(
        symbol: str, 
        start_date: str,
        end_date: str,
        adjust: str = "qfq"
    ) -> pd.DataFrame:
        """
        获取股票历史数据（使用新浪数据源）
        
        Args:
            symbol: 股票代码，如 "000001"
            start_date: 开始日期 "YYYY-MM-DD" 或 "YYYYMMDD"
            end_date: 结束日期
            adjust: 复权类型 qfq-前复权, hfq-后复权, ""-不复权
        """
        try:
            # 转换代码格式：000001 -> sz000001, 600519 -> sh600519
            if symbol.startswith("6"):
                sina_symbol = f"sh{symbol}"
            else:
                sina_symbol = f"sz{symbol}"
            
            # 使用新浪数据源
            df = ak.stock_zh_a_daily(
                symbol=sina_symbol,
                start_date=start_date.replace("-", ""),
                end_date=end_date.replace("-", ""),
                adjust=adjust
            )
            
            if df.empty:
                log.warning(f"{symbol} 无数据")
                return pd.DataFrame()
            
            # 标准化列名
            df = df.rename(columns={
                "date": "date",
                "open": "open",
                "high": "high",
                "low": "low",
                "close": "close",
                "volume": "volume"
            })
            
            df["date"] = pd.to_datetime(df["date"])
            df.set_index("date", inplace=True)
            
            log.info(f"获取 {symbol} 历史数据成功，共 {len(df)} 条")
            return df
            
        except Exception as e:
            log.error(f"获取 {symbol} 历史数据失败: {e}")
            return pd.DataFrame()
    
    @staticmethod
    def get_realtime_quote(symbols: List[str]) -> pd.DataFrame:
        """
        获取实时行情（使用新浪数据源）
        
        Args:
            symbols: 股票代码列表，如 ["000001", "600519"]
        """
        try:
            # 转换代码格式
            sina_symbols = []
            for s in symbols:
                if s.startswith("6"):
                    sina_symbols.append(f"sh{s}")
                else:
                    sina_symbols.append(f"sz{s}")
            
            # 获取新浪实时行情
            df = ak.stock_zh_a_spot()
            
            # 筛选指定股票
            df = df[df["代码"].isin(symbols)]
            return df
            
        except Exception as e:
            log.error(f"获取实时行情失败: {e}")
            return pd.DataFrame()
    
    @staticmethod
    def get_stock_list() -> pd.DataFrame:
        """获取A股股票列表（使用新浪数据源）"""
        try:
            df = ak.stock_zh_a_spot()
            return df[["代码", "名称"]]
        except Exception as e:
            log.error(f"获取股票列表失败: {e}")
            return pd.DataFrame()
    
    @staticmethod
    def get_minute_data(symbol: str, period: str = "1", max_retries: int = 3) -> pd.DataFrame:
        """
        获取分钟级数据（使用东方财富数据源）
        
        Args:
            symbol: 股票代码，如 "000001"
            period: 周期，"1"-1分钟, "5"-5分钟, "15"-15分钟, "30"-30分钟, "60"-60分钟
            max_retries: 最大重试次数
        """
        import time
        
        for attempt in range(max_retries):
            try:
                df = ak.stock_zh_a_hist_min_em(
                    symbol=symbol,
                    period=period,
                    adjust=""
                )
                log.info(f"获取 {symbol} {period}分钟数据成功，共 {len(df)} 条")
                return df
            except Exception as e:
                if attempt < max_retries - 1:
                    log.warning(f"获取分钟数据失败，2秒后重试 ({attempt + 1}/{max_retries})")
                    time.sleep(2)
                else:
                    log.error(f"获取 {symbol} 分钟数据失败: {e}")
        
        return pd.DataFrame()


