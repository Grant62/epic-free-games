import requests
import time
from typing import List, Dict, Optional

class SteamClient:
    """Steam Store API 客户端"""
    
    def __init__(self):
        self.timeout = 30
        self.retry_times = 3
        self.retry_delay = 2
        self.batch_size = 5  # 减少到5个
        self.rate_limit = 2.0  # 增加到2秒
        self.last_request_time = 0
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
    
    def _rate_limit_wait(self):
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit:
            time.sleep(self.rate_limit - time_since_last)
        self.last_request_time = time.time()
    
    def _request(self, url: str, params: Optional[Dict] = None) -> Optional[Dict]:
        for attempt in range(self.retry_times):
            try:
                self._rate_limit_wait()
                response = self.session.get(url, params=params, timeout=self.timeout)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                print(f"请求失败 (尝试 {attempt + 1}/{self.retry_times}): {e}")
                if attempt < self.retry_times - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                else:
                    return None
        return None
    
    def get_featured_categories(self) -> Optional[Dict]:
        print("正在获取Steam精选折扣游戏...")
        url = "https://store.steampowered.com/api/featuredcategories/"
        data = self._request(url)
        if data:
            total = 0
            for key in ["specials", "top_sellers", "new_releases", "coming_soon"]:
                if key in data and "items" in data[key]:
                    total += len(data[key]["items"])
            print(f"✅ 成功获取数据，共 {total} 个游戏")
            return data
        print("❌ 获取数据失败")
        return None
    
    def get_app_details(self, app_ids: List[int]) -> Dict[int, Dict]:
        """批量获取游戏详情 - 单个获取避免400错误"""
        if not app_ids:
            return {}
        
        results = {}
        failed = []
        
        print(f"正在逐个获取 {len(app_ids)} 个游戏详情...")
        
        for i, appid in enumerate(app_ids):
            print(f"  获取 {i+1}/{len(app_ids)}: appid={appid}")
            
            params = {
                "appids": appid,
                "cc": "CN",
                "l": "schinese",
                "filters": "basic,reviews"
            }
            
            data = self._request("https://store.steampowered.com/api/appdetails", params)
            
            if data and str(appid) in data:
                app_data = data[str(appid)]
                if app_data.get("success") and app_data.get("data"):
                    results[appid] = app_data["data"]
                else:
                    failed.append(appid)
            else:
                failed.append(appid)
            
            time.sleep(self.rate_limit)
        
        print(f"✅ 成功获取 {len(results)}/{len(app_ids)} 个游戏详情 ({len(failed)} 个失败)")
        return results
