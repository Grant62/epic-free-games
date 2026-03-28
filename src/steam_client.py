import requests
import time
from typing import List, Dict, Optional

class SteamClient:
    """Steam Store API 客户端"""
    
    def __init__(self):
        self.timeout = 30
        self.retry_times = 3
        self.retry_delay = 2
        self.batch_size = 10
        self.rate_limit = 1.0
        self.last_request_time = 0
    
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
                response = requests.get(
                    url, 
                    params=params, 
                    timeout=self.timeout,
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                    }
                )
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
        """获取Steam精选分类数据（包含折扣游戏）"""
        print("正在获取Steam精选折扣游戏...")
        url = "https://store.steampowered.com/api/featuredcategories/"
        data = self._request(url)
        if data:
            # 计算总共有多少个游戏
            total_games = 0
            for key in ["specials", "top_sellers", "new_releases", "coming_soon"]:
                if key in data and "items" in data[key]:
                    total_games += len(data[key]["items"])
            print(f"✅ 成功获取数据，共 {total_games} 个游戏")
            return data
        else:
            print("❌ 获取数据失败")
            return None
    
    def get_app_details(self, app_ids: List[int]) -> Dict[int, Dict]:
        """批量获取游戏详情"""
        if not app_ids:
            return {}
        
        results = {}
        failed_count = 0
        
        for i in range(0, len(app_ids), self.batch_size):
            batch = app_ids[i:i + self.batch_size]
            appids_str = ",".join(str(appid) for appid in batch)
            
            print(f"正在获取游戏详情 ({i+1}-{min(i+self.batch_size, len(app_ids))}/{len(app_ids)})...")
            
            params = {
                "appids": appids_str,
                "cc": "CN",
                "l": "schinese",
                "filters": "basic,reviews"
            }
            
            data = self._request("https://store.steampowered.com/api/appdetails", params)
            
            if data:
                for appid_str, app_data in data.items():
                    appid = int(appid_str)
                    if app_data.get("success") and app_data.get("data"):
                        results[appid] = app_data["data"]
                    else:
                        failed_count += 1
            else:
                failed_count += len(batch)
                print(f"⚠️ 批次获取失败，跳过 {len(batch)} 个游戏")
            
            if i + self.batch_size < len(app_ids):
                time.sleep(self.rate_limit)
        
        print(f"✅ 成功获取 {len(results)}/{len(app_ids)} 个游戏详情 ({failed_count} 个失败)")
        return results
