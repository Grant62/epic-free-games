import os
import requests

class WeChatSender:
    def __init__(self):
        self.webhook_url = os.environ.get("WECHAT_WEBHOOK_URL")
        if not self.webhook_url:
            raise ValueError("Environment variable WECHAT_WEBHOOK_URL not set")
    
    def send_message(self, message):
        try:
            payload = {
                "msgtype": "text",
                "text": {"content": message}
            }
            response = requests.post(self.webhook_url, json=payload, timeout=30)
            result = response.json()
            if result.get("errcode") == 0:
                print("Message sent successfully")
                return True
            else:
                print(f"Failed to send message: {result}")
                return False
        except Exception as e:
            print(f"Error sending message: {e}")
            return False
    
    def send_text(self, text):
        return self.send_message(text)
