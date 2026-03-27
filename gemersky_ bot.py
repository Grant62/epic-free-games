import requests
import json
import time
from datetime import datetime
import hashlib

# ========== 在这里填你的Webhook地址 ==========
import os
WEBHOOK_URL = os.environ.get('WEBHOOK_URL', "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=你的key")
# ==========================================

class GamerskyNewsBot:
    def __init__(self, webhook):
        self.webhook = webhook
        self.sent_news = set()
        
        # 加载已推送记录
        try:
            with open('sent_history.json', 'r') as f:
                self.sent_news = set(json.load(f))
        except:
            pass
    
    def get_news(self):
        """获取游民星空新闻（过滤手游）"""
        # 游民星空RSS源
        rss_url = "https://www.gamersky.com/rss/news.xml"
        
        # 要过滤的关键词（手游相关）
        block_keywords = [
            '手游', '王者荣耀', '和平精英', '原神手游', '明日方舟', 
            '阴阳师', '崩坏', '碧蓝航线', 'FGO', '第五人格',
            '部落冲突', '皇室战争', '金铲铲', '蛋仔派对'
        ]
        
        try:
            # 获取RSS内容
            response = requests.get(rss_url, timeout=10)
            
            # 解析RSS（手动解析，不依赖feedparser）
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response.content)
            
            news_list = []
            items = root.findall('.//item')
            
            for item in items[:20]:  # 取前20条
                title = item.find('title').text
                link = item.find('link').text
                description = item.find('description').text if item.find('description') is not None else ""
                pub_date = item.find('pubDate').text if item.find('pubDate') is not None else ""
                
                # 过滤手游
                is_mobile_game = False
                for kw in block_keywords:
                    if kw in title:
                        is_mobile_game = True
                        break
                
                if is_mobile_game:
                    continue  # 跳过手游新闻
                
                # 生成唯一ID
                news_id = hashlib.md5(link.encode()).hexdigest()
                
                # 检查是否已推送
                if news_id not in self.sent_news:
                    news_list.append({
                        'id': news_id,
                        'title': title,
                        'link': link,
                        'summary': description[:150] if description else "",
                        'pub_date': pub_date
                    })
            
            return news_list
            
        except Exception as e:
            print(f"获取新闻失败: {e}")
            return []
    
    def send_message(self, content, msg_type="markdown"):
        """发送到企业微信"""
        if msg_type == "markdown":
            data = {
                "msgtype": "markdown",
                "markdown": {
                    "content": content
                }
            }
        else:
            data = {
                "msgtype": "text",
                "text": {
                    "content": content
                }
            }
        
        try:
            response = requests.post(self.webhook, json=data, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"发送失败: {e}")
            return False
    
    def format_news(self, news_list):
        """格式化新闻为Markdown"""
        if not news_list:
            return None
        
        today = datetime.now().strftime('%Y年%m月%d日')
        
        msg = f"""## 🎮 游民星空新闻速递

📅 {today}

"""
        
        for i, news in enumerate(news_list[:10], 1):
            msg += f"""### {i}. {news['title']}

📝 {news['summary'][:80]}...

🔗 [阅读全文]({news['link']})

---
"""
        
        msg += "\n> 💡 每日自动推送，已过滤手游内容"
        
        return msg
    
    def save_sent(self, news_list):
        """保存已推送记录"""
        for news in news_list:
            self.sent_news.add(news['id'])
        
        # 只保留最近500条
        if len(self.sent_news) > 500:
            self.sent_news = set(list(self.sent_news)[-500:])
        
        with open('sent_history.json', 'w') as f:
            json.dump(list(self.sent_news), f)
    
    def run(self):
        """执行推送"""
        print(f"[{datetime.now()}] 开始获取新闻...")
        
        # 获取新闻
        news_list = self.get_news()
        
        if not news_list:
            print("没有新新闻")
            # 发送一条提示消息（可选）
            # self.send_message("📭 今日暂无新游戏新闻", "text")
            return
        
        print(f"发现 {len(news_list)} 条新新闻")
        
        # 格式化并发送
        message = self.format_news(news_list)
        if message:
            if self.send_message(message):
                self.save_sent(news_list)
                print(f"推送成功！共 {len(news_list)} 条")
            else:
                print("推送失败")


# ========== 运行 ==========
if __name__ == "__main__":
    bot = GamerskyNewsBot(WEBHOOK_URL)
    bot.run()
