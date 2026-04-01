from datetime import datetime
import re

class GameFilter:
    """游戏筛选器 - 选出最好的3款"""
    
    def extract_discount_games(self, featured_data):
        """提取所有打折游戏"""
        games = []
        if not featured_data:
            return games
        
        categories = ["specials", "top_sellers", "new_releases", "coming_soon"]
        seen_ids = set()
        
        for category in categories:
            if category not in featured_data:
                continue
            cat_data = featured_data[category]
            if "items" not in cat_data:
                continue
            
            for item in cat_data["items"]:
                appid = item.get("id")
                if not appid or appid in seen_ids:
                    continue
                
                discount_percent = item.get("discount_percent", 0)
                original_price = item.get("original_price", 0)
                
                if discount_percent > 0 and original_price > 0:
                    seen_ids.add(appid)
                    games.append({
                        "appid": appid,
                        "name": item.get("name"),
                        "discount_percent": discount_percent,
                        "original_price": original_price,
                        "final_price": item.get("final_price", 0),
                        "header_image": item.get("header_image", ""),
                        "discount_expiration": item.get("discount_expiration", 0),
                    })
        
        print(f"提取到 {len(games)} 个折扣游戏")
        return games
    
    def select_best_games(self, games, details):
        """选出最好的3款游戏"""
        if not games:
            return [], []
        
        scored_games = []
        for game in games:
            appid = game["appid"]
            game_detail = details.get(appid, {})
            
            reviews = game_detail.get("reviews", {})
            review_summary = reviews.get("review_summary", "")
            
            review_score = 0
            if review_summary:
                match = re.search(r'(\d+)%', review_summary)
                if match:
                    review_score = int(match.group(1))
            
            total_reviews = 0
            if review_summary:
                match = re.search(r'([\d,]+) user reviews', review_summary)
                if match:
                    total_reviews = int(match.group(1).replace(',', ''))
            else:
                recommendations = game_detail.get("recommendations", {})
                total_reviews = recommendations.get("total", 0)
            
            heat_score = total_reviews * (review_score / 100) if review_score > 0 else total_reviews * 0.5
            discount_bonus = game["discount_percent"] * 100
            final_score = heat_score + discount_bonus
            
            game["review_score"] = review_score if review_score > 0 else "未知"
            game["review_count"] = total_reviews
            game["final_score"] = final_score
            
            scored_games.append(game)
        
        scored_games.sort(key=lambda x: x["final_score"], reverse=True)
        top_games = scored_games[:3]
        
        free_games = [g for g in top_games if g["discount_percent"] == 100]
        paid_games = [g for g in top_games if g["discount_percent"] < 100]
        
        print(f"选出最好的 {len(top_games)} 款游戏")
        for i, g in enumerate(top_games, 1):
            print(f"  {i}. {g['name']} (评分:{g['review_score']} 评测:{g['review_count']})")
        
        return free_games, paid_games
    
    def filter_by_quality(self, games, details):
        """兼容旧代码的方法"""
        return self.select_best_games(games, details)
    
    def format_expiration(self, timestamp):
        """格式化截止时间"""
        if not timestamp:
            return "限时优惠"
        try:
            dt = datetime.fromtimestamp(timestamp)
            now = datetime.now()
            delta = dt - now
            if delta.days > 0:
                return f"剩{delta.days}天"
            elif delta.seconds > 3600:
                hours = delta.seconds // 3600
                return f"剩{hours}小时"
            else:
                return "即将截止"
        except:
            return "限时优惠"
