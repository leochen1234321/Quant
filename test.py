import os
import requests
import akshare as ak

# 彻底清除代理
for key in list(os.environ.keys()):
    if 'proxy' in key.lower():
        print(f"删除环境变量: {key}={os.environ[key]}")
        del os.environ[key]

os.environ['NO_PROXY'] = '*'

# 使用不信任环境的 session
session = requests.Session()
session.trust_env = False

print("\n测试直连...")
try:
    resp = session.get(
        "https://push2his.eastmoney.com/api/qt/stock/kline/get",
        params={
            "secid": "0.000001",
            "fields1": "f1,f2,f3",
            "fields2": "f51,f52,f53,f54,f55,f56,f57",
            "klt": "101",
            "fqt": "1",
            "beg": "20241201",
            "end": "20241206"
        },
        timeout=10
    )
    print(f"✅ 成功！状态码: {resp.status_code}")
    print(resp.text[:200])
except Exception as e:
    print(f"❌ 失败: {type(e).__name__}: {e}")

print("测试1: 新浪数据源 - 指数行情")
try:
    df = ak.stock_zh_index_spot_sina()
    print("✅ 新浪数据源成功！")
    print(df.head())
except Exception as e:
    print(f"❌ 失败: {e}")

print("\n测试2: 新浪数据源 - 股票历史")
try:
    df = ak.stock_zh_a_daily(symbol="sz000001", start_date="20241201", end_date="20251208")
    print("✅ 新浪历史数据成功！")
    print(df)
except Exception as e:
    print(f"❌ 失败: {e}")

print("\n测试3: 腾讯数据源")
try:
    df = ak.stock_zh_a_hist_min_em(symbol="000001", period="1", adjust="")
    print("✅ 腾讯分钟数据成功！")
    print(df.tail())
except Exception as e:
    print(f"❌ 失败: {e}")