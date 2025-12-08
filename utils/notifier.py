"""
PushPlus 微信通知模块

使用方法：
1. 访问 https://www.pushplus.plus/ 微信扫码登录
2. 复制 Token
3. 关注「pushplus推送加」公众号
4. 调用 send() 方法发送消息
"""
import requests
from typing import Optional
from datetime import datetime


class PushPlusNotifier:
    """PushPlus 微信通知器"""
    
    API_URL = "http://www.pushplus.plus/send"
    
    def __init__(self, token: str):
        """
        初始化通知器
        
        Args:
            token: PushPlus 的 token，从 https://www.pushplus.plus/ 获取
        """
        self.token = token
    
    def send(
        self,
        title: str,
        content: str,
        template: str = "html",
        topic: str = "",
        channel: str = "wechat"
    ) -> dict:
        """
        发送消息
        
        Args:
            title: 消息标题（必填）
            content: 消息内容（必填）
            template: 模板类型
                - html: HTML模板（默认）
                - txt: 纯文本
                - json: JSON格式
                - markdown: Markdown格式
            topic: 群组编码（可选，用于一对多推送）
            channel: 推送渠道
                - wechat: 微信公众号（默认）
                - webhook: 第三方webhook
                - cp: 企业微信
                - mail: 邮件
                
        Returns:
            dict: 返回结果 {"code": 200, "msg": "success", "data": "..."}
        """
        data = {
            "token": self.token,
            "title": title,
            "content": content,
            "template": template,
        }
        
        if topic:
            data["topic"] = topic
        if channel != "wechat":
            data["channel"] = channel
        
        try:
            response = requests.post(self.API_URL, json=data, timeout=10)
            result = response.json()
            
            if result.get("code") == 200:
                print(f"✅ 消息发送成功: {title}")
            else:
                print(f"❌ 消息发送失败: {result.get('msg')}")
            
            return result
            
        except requests.exceptions.Timeout:
            print("❌ 请求超时")
            return {"code": -1, "msg": "请求超时"}
        except Exception as e:
            print(f"❌ 发送异常: {e}")
            return {"code": -1, "msg": str(e)}
    
    def send_text(self, title: str, content: str) -> dict:
        """发送纯文本消息"""
        return self.send(title, content, template="txt")
    
    def send_markdown(self, title: str, content: str) -> dict:
        """发送 Markdown 消息"""
        return self.send(title, content, template="markdown")
    
    def send_html(self, title: str, content: str) -> dict:
        """发送 HTML 消息"""
        return self.send(title, content, template="html")
    
    def send_trade_signal(
        self,
        symbol: str,
        signal_type: str,
        price: float,
        reason: str = "",
        quantity: int = None
    ) -> dict:
        """
        发送交易信号通知
        
        Args:
            symbol: 股票代码
            signal_type: 信号类型 "buy" 或 "sell"
            price: 当前价格
            reason: 触发原因
            quantity: 交易数量（可选）
        """
        is_buy = signal_type.lower() == "buy"
        emoji = "🟢" if is_buy else "🔴"
        action = "买入" if is_buy else "卖出"
        color = "#07C160" if is_buy else "#FA5151"
        
        title = f"{emoji} {symbol} {action}信号"
        
        # 使用 HTML 模板，更美观
        content = f"""
        <div style="padding: 15px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
            <h2 style="color: {color}; margin-bottom: 20px;">{emoji} 交易信号</h2>
            <table style="width: 100%; border-collapse: collapse;">
                <tr style="border-bottom: 1px solid #eee;">
                    <td style="padding: 10px 0; color: #666;">股票代码</td>
                    <td style="padding: 10px 0; font-weight: bold;">{symbol}</td>
                </tr>
                <tr style="border-bottom: 1px solid #eee;">
                    <td style="padding: 10px 0; color: #666;">信号类型</td>
                    <td style="padding: 10px 0; font-weight: bold; color: {color};">{action}</td>
                </tr>
                <tr style="border-bottom: 1px solid #eee;">
                    <td style="padding: 10px 0; color: #666;">当前价格</td>
                    <td style="padding: 10px 0; font-weight: bold;">¥{price:.2f}</td>
                </tr>
                {"<tr style='border-bottom: 1px solid #eee;'><td style='padding: 10px 0; color: #666;'>交易数量</td><td style='padding: 10px 0;'>" + str(quantity) + " 股</td></tr>" if quantity else ""}
                <tr style="border-bottom: 1px solid #eee;">
                    <td style="padding: 10px 0; color: #666;">触发原因</td>
                    <td style="padding: 10px 0;">{reason or "策略触发"}</td>
                </tr>
                <tr>
                    <td style="padding: 10px 0; color: #666;">触发时间</td>
                    <td style="padding: 10px 0;">{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</td>
                </tr>
            </table>
            <p style="margin-top: 20px; color: #999; font-size: 12px;">
                ⚠️ 此消息由量化交易系统自动发送，仅供参考，不构成投资建议
            </p>
        </div>
        """
        
        return self.send_html(title, content)
    
    def send_daily_report(
        self,
        total_profit: float,
        today_profit: float,
        positions: list,
        trades_today: int = 0
    ) -> dict:
        """
        发送每日报告
        
        Args:
            total_profit: 总收益率
            today_profit: 今日收益率
            positions: 持仓列表 [{"symbol": "000001", "name": "平安银行", "profit": 0.05}, ...]
            trades_today: 今日交易次数
        """
        title = f"📊 每日交易报告 {datetime.now().strftime('%m-%d')}"
        
        position_rows = ""
        for pos in positions:
            profit_color = "#07C160" if pos.get("profit", 0) >= 0 else "#FA5151"
            position_rows += f"""
            <tr style="border-bottom: 1px solid #eee;">
                <td style="padding: 8px;">{pos.get('symbol', '')}</td>
                <td style="padding: 8px;">{pos.get('name', '')}</td>
                <td style="padding: 8px; color: {profit_color};">{pos.get('profit', 0):+.2%}</td>
            </tr>
            """
        
        content = f"""
        <div style="padding: 15px; font-family: -apple-system, BlinkMacSystemFont, sans-serif;">
            <h2 style="margin-bottom: 20px;">📊 每日交易报告</h2>
            
            <div style="display: flex; margin-bottom: 20px;">
                <div style="flex: 1; text-align: center; padding: 15px; background: #f5f5f5; border-radius: 8px; margin-right: 10px;">
                    <div style="color: #666; font-size: 12px;">总收益率</div>
                    <div style="font-size: 24px; font-weight: bold; color: {'#07C160' if total_profit >= 0 else '#FA5151'};">
                        {total_profit:+.2%}
                    </div>
                </div>
                <div style="flex: 1; text-align: center; padding: 15px; background: #f5f5f5; border-radius: 8px;">
                    <div style="color: #666; font-size: 12px;">今日收益</div>
                    <div style="font-size: 24px; font-weight: bold; color: {'#07C160' if today_profit >= 0 else '#FA5151'};">
                        {today_profit:+.2%}
                    </div>
                </div>
            </div>
            
            <h3 style="margin-bottom: 10px;">📈 当前持仓</h3>
            <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
                <tr style="background: #f5f5f5;">
                    <th style="padding: 8px; text-align: left;">代码</th>
                    <th style="padding: 8px; text-align: left;">名称</th>
                    <th style="padding: 8px; text-align: left;">盈亏</th>
                </tr>
                {position_rows if position_rows else "<tr><td colspan='3' style='padding: 20px; text-align: center; color: #999;'>暂无持仓</td></tr>"}
            </table>
            
            <p style="color: #666;">今日交易: {trades_today} 笔</p>
            <p style="color: #999; font-size: 12px;">报告时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </div>
        """
        
        return self.send_html(title, content)


# 便捷函数
def create_notifier(token: str) -> PushPlusNotifier:
    """创建通知器实例"""
    return PushPlusNotifier(token)
