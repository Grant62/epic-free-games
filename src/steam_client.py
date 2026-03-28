import requests
import time
import re
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from config.settings import STEAM_API, BATCH_SIZE, RATE_LIMIT

class SteamClient:
    """Steam全站折扣游戏爬取客户端"""
    
    def __init__(self):
        self.timeout = STEAM_API["timeout"]
        self.retry_times = STEAM_API["retry_times"]
        self.retry_delay = STEAM_API["retry_delay"]
        self.batch_size = BATCH_SIZE
        self.rate_limit = RATE_LIMIT
        self.last_request_time = 0
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Cookie": "steamCountry=CN%7Ccc64f0f3f4f5f6f7f8f9fafbfcfdfeff;"
        })
    
    def _rate_limit_wait(self):
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit:
            time.sleep(self.rate_limit - time_since_last)
        self.last_request_time = time.time()
    
    def _request(self, url: str, params: Optional[Dict] = None, is_json: bool = True) -> Optional[any]:
        for attempt in range(self.retry_times):
            try:
                self._rate_limit_wait()
                response = self.session.get(url, params=params, timeout=self.timeout)
                response.raise_for_status()
                if is_json:
                    return response.json()
                else:
                    return response.text
            except Exception as e:
                print(f"请求失败 (尝试 {attempt + 1}/{self.retry_times}): {e}")
                if attempt < self.retry_times - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                else:
                    return None
        return None
    
    def fetch_all_discounted_games(self, max_games: int = 500) -> List[Dict]:
        """
        爬取Steam全站折扣游戏
        通过解析搜索页面获取所有折扣游戏
        """
        print(f"开始爬取Steam全站折扣游戏 (最多{max_games}个)...")
        games = []
        seen_ids = set()
        
        # 获取多页数据
        for page in range(1, 11):  # 最多10页
            if len(games) >= max_games:
                break
                
            print(f"正在获取第 {page} 页...")
            params = {
                "sort_by": "Price_ASC",
                "category1": "998",  # Games
                "specials": "1",     # 只显示折扣
                "page": page
            }
            
            html = self._request(STEAM_API["search_url"], params, is_json=False)
            if not html:
                print(f"第 {page} 页获取失败，跳过")
                continue
            
            # 解析HTML提取游戏信息
            page_games = self._parse_search_page(html)
            print(f"第 {page} 页找到 {len(page_games)} 个游戏")
            
            for game in page_games:
                appid = game.get("appid")
                if appid and appid not in seen_ids:
                    seen_ids.add(appid)
                    games.append(game)
            
            if len(page_games) == 0:
                print("没有更多游戏了，停止爬取")
                break
            
            time.sleep(self.rate_limit)
        
        print(f"总共找到 {len(games)} 个折扣游戏")
        return games[:max_games]
    
    def _parse_search_page(self, html: str) -> List[Dict]:
        """解析Steam搜索页面HTML提取游戏信息"""
        games = []
        soup = BeautifulSoup(html, 'html.parser')
        
        # 查找所有游戏条目
        game_rows = soup.find_all('a', class_='search_result_row')
        
        for row in game_rows:
            try:
                # 提取AppID
                appid = row.get('data-ds-appid')
                if not appid:
                    href = row.get('href', '')
                    match = re.search(r'/app/(\d+)/', href)
                    if match:
                        appid = int(match.group(1))
                    else:
                        continue
                else:
                    appid = int(appid)
                
                # 提取游戏名称
                title_elem = row.find('span', class_='title')
                name = title_elem.text.strip() if title_elem else "Unknown"
                
                # 提取折扣信息
                discount_elem = row.find('div', class_='search_discount')
                if not discount_elem:
                    continue
                
                discount_span = discount_elem.find('span')
                if not discount_span:
                    continue
                
                discount_text = discount_span.text.strip().replace('-', '').replace('%', '')
                try:
                    discount_percent = int(discount_text)
                except:
                    continue
                
                # 提取原价和现价
                price_elem = row.find('div', class_='search_price')
                if not price_elem:
                    continue
                
                # 解析价格
                original_price = 0
                final_price = 0
                
                # 检查是否有原价划线
                strike_elem = price_elem.find('strike')
                if strike_elem:
                    # 有划线原价
                    original_text = strike_elem.text.strip()
                    original_price = self._parse_price(original_text)
                    
                    # 现价在span里
                    final_span = price_elem.find('span')
                    if final_span:
                        final_text = final_span.text.strip()
                        final_price = self._parse_price(final_text)
                else:
                    # 没有划线，可能是免费游戏或其他情况
                    continue
                
                if original_price > 0:
                    games.append({
                        "appid": appid,
                        "name": name,
                        "discount_percent": discount_percent,
                        "original_price": original_price,
                        "final_price": final_price,
                        "header_image": f"https://cdn.akamai.steamstatic.com/steam/apps/{appid}/header.jpg"
                    })
                    
            except Exception as e:
                print(f"解析游戏条目失败: {e}")
                continue
        
        return games
    
    def _parse_price(self, price_text: str) -> int:
        """解析价格文本为分"""
        try:
            # 移除货币符号和逗号
            price_text = price_text.replace('¥', '').replace(',', '').replace('$', '').strip()
            # 转换为分
            price = float(price_text)
            return int(price * 100)
        except:
            return 0
    
    def get_app_details(self, app_ids: List[int]) -> Dict[int, Dict]:
        """批量获取游戏详情（好评率、评测数等）"""
        if not app_ids:
            return {}
        
        results = {}
        total = len(app_ids)
        
        for i in range(0, total, self.batch_size):
            batch = app_ids[i:i + self.batch_size]
            appids_str = ",".join(str(appid) for appid in batch)
            
            print(f"正在获取游戏详情 ({i+1}-{min(i+self.batch_size, total)}/{total})...")
            
            params = {
                "appids": appids_str,
                "cc": "CN",
                "l": "schinese",
                "filters": "basic,reviews"
            }
            
            data = self._request(STEAM_API["appdetails_url"], params)
            
            if data:
                for appid_str, app_data in data.items():
                    appid = int(appid_str)
                    if app_data.get("success") and app_data.get("data"):
                        results[appid] = app_data["data"]
            
            if i + self.batch_size < total:
                time.sleep(self.rate_limit)
        
        print(f"✅ 成功获取 {len(results)}/{total} 个游戏详情")
        return results
