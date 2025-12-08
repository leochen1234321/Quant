"""
数据获取模块使用示例

运行方式：
cd /Users/chenlei/Desktop/workspace/量化
python data/example.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.fetcher import DataFetcher

fetcher = DataFetcher()


def example_stock_list():
    """示例1：获取A股股票列表"""
    print("=" * 50)
    print("获取A股股票列表（新浪数据源）")
    print("=" * 50)
    
    df = fetcher.get_stock_list()
    
    if df.empty:
        print("❌ 获取失败")
        return
    
    print(f"共 {len(df)} 只股票\n")
    print("前10只股票：")
    print(df.head(10))
    print()


def example_history_data():
    """示例2：获取股票历史数据"""
    print("=" * 50)
    print("获取股票历史数据（新浪数据源）")
    print("=" * 50)
    
    df = fetcher.get_stock_history(
        symbol="000001",
        start_date="2024-01-01",
        end_date="2024-12-08",
        adjust="qfq"
    )
    
    if df.empty:
        print("❌ 获取失败")
        return
    
    print(f"\n股票代码: 000001 (平安银行)")
    print(f"数据条数: {len(df)} 条")
    print(f"时间范围: {df.index[0]} ~ {df.index[-1]}")
    print(f"\n最近5条数据:")
    print(df.tail())
    print()


def example_minute_data():
    """示例3：获取分钟数据"""
    print("=" * 50)
    print("获取分钟数据（腾讯数据源）")
    print("=" * 50)

    df = DataFetcher.get_minute_data("603122", "60")
    print(df)
    
    if df.empty:
        print("❌ 获取失败")
        return
    
    print(f"\n股票代码: 000001")
    print(f"数据周期: 5分钟")
    print(f"数据条数: {len(df)} 条")
    print(f"\n最近5条数据:")
    print(df.tail())
    print()


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("akshare 数据获取模块使用示例")
    print("=" * 50 + "\n")
    
    # example_stock_list()
    # example_history_data()
    example_minute_data()
    
    print("=" * 50)
    print("✅ 示例运行完成！")
    print("=" * 50)
