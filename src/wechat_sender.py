import os
import requests

class WeChatSender:
    def __init__(self):
        self.webhook_url = os.environ.get("WECHAT_WEBHOOK_URL")
        if not self.webhook_url:
            raise ValueError("环境变量 WECHAT_WEBHOOK_URL 未设置")
    
    def send_message(self, message):
        try:
            payload = {
                "msgtype": "text",
                "text": {"content": message}
            }
            response = requests.post(self.webhook_url, json=payload, timeout=30)
            result = response.json()
            if result.get("errcode") == 0:
                print("消息推送成功")
                return True
            else:
                print(f"消息推送失败：{result}")
                return False
        except Exception as e:
            print(f"消息推送异常：{e}")
            return False
    
    def send_text(self, text):
        return self.send_message(text)
