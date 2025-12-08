"""
PushPlus 通知模块测试
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.notifier import PushPlusNotifier

# 你的 Token
TOKEN = "942e2dd537ca47f48b3974dcd8ab4dd8"

if __name__ == "__main__":
    notifier = PushPlusNotifier(TOKEN)
    
    # 发送测试消息并打印结果
    result = notifier.send_text("测试消息", "你好, 量化系统测试！")
    
    print("=" * 50)
    print(f"返回结果: {result}")
    print("=" * 50)
    
    if result.get("code") == 200:
        print("✅ API 调用成功，请检查微信公众号消息")
    else:
        print(f"❌ 失败原因: {result.get('msg')}")