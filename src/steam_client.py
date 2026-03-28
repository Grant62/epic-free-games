import requests
import time

class SteamClient:
    def __init__(self):
        self.timeout = 30
        self.retry_times = 3
        self.retry_delay = 2
        self.batch_size = 10  # 减少到10个，避免400错误
        self.rate_limit = 1.5
        self.last_request_time = 0
    
    def _rate_limit_wait(self):
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit:
            time.sleep(self.rate_limit - time_since_last)
        self.last_request_time = time.time()
    
    def _request(self, url, params=None):
        for attempt in range(self.retry_times):
            try:
                self._rate_limit_wait()
                response = requests.get(url, params=params, timeout=self.timeout,
                    headers={"User-Agent": "Mozilla/5.0"})
                response.raise_for_status()
                return response.json()
            except Exception as e:
                print(f"Request failed (attempt {attempt + 1}/{self.retry_times}): {e}")
                if attempt < self.retry_times - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
        return None
    
    def get_featured_categories(self):
        print("Fetching Steam featured categories...")
        url = "https://store.steampowered.com/api/featuredcategories/"
        data = self._request(url)
        if data:
            print("Successfully fetched data")
            return data
        print("Failed to fetch featured categories")
        return None
    
    def get_app_details(self, app_ids):
        if not app_ids:
            return {}
        results = {}
        failed_count = 0
        
        for i in range(0, len(app_ids), self.batch_size):
            batch = app_ids[i:i + self.batch_size]
            appids_str = ",".join(str(appid) for appid in batch)
            print(f"Fetching game details batch {i//self.batch_size + 1}: {len(batch)} games...")
            
            params = {
                "appids": appids_str,
                "cc": "CN",
                "l": "schinese",
                "filters": "basic,reviews,publishers"
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
                print(f"Warning: Failed to fetch batch, skipping {len(batch)} games")
            
            if i + self.batch_size < len(app_ids):
                time.sleep(self.rate_limit)
        
        print(f"Successfully fetched {len(results)}/{len(app_ids)} game details ({failed_count} failed)")
        return results
