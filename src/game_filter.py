from datetime import datetime
from config.settings import MIN_REVIEW_COUNT, MIN_REVIEW_SCORE
from src.quality_calculator import QualityCalculator

class GameFilter:
    def __init__(self):
        self.calculator = QualityCalculator()
    
    def extract_discount_games(self, featured_data):
        """提取所有打折的游戏，不限制折扣力度"""
        games = []
        if not featured_data:
            return games
        
        # 从所有分类中提取
        categories = ["specials", "top_sellers", "new_releases", "coming_soon"]
        seen_ids = set()
        
        for category in categories:
            if category not in featured_data:
                continue
            cat_data = featured_data[category]
            if "items" not in cat_data:
                continue
            
            print(f"Checking category '{category}': {len(cat_data['items'])} items")
            
            for item in cat_data["items"]:
                appid = item.get("id")
                if not appid or appid in seen_ids:
                    continue
                
                discount_percent = item.get("discount_percent", 0)
                original_price = item.get("original_price", 0)
                
                # 只要有折扣就提取（不限制折扣力度）
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
        
        print(f"Total extracted: {len(games)} discounted games from all categories")
        return games
    
    def filter_by_quality(self, games, details):
        """按质量筛选：好评率>=75%且评测数>=500"""
        qualified = []
        for game in games:
            appid = game["appid"]
            game_detail = details.get(appid, {})
            quality_info = self.calculator.calculate_total_score(game_detail)
            
            review_score = quality_info["details"]["review_score_pct"]
            review_count = quality_info["details"]["total_reviews"]
            
            # 硬性门槛：好评率>=75% 且 评测数>=500
            if review_score and review_score >= MIN_REVIEW_SCORE and review_count >= MIN_REVIEW_COUNT:
                game["review_score"] = review_score
                game["review_count"] = review_count
                game["quality_info"] = quality_info
                qualified.append(game)
        
        # 按折扣力度排序（折扣大的在前）
        qualified.sort(key=lambda x: x["discount_percent"], reverse=True)
        
        # 分离限时免费和普通折扣
        free_games = [g for g in qualified if g["discount_percent"] == 100]
        premium_deals = [g for g in qualified if g["discount_percent"] < 100]
        
        print(f"Quality filter: {len(free_games)} free, {len(premium_deals)} deals (total {len(qualified)})")
        return free_games, premium_deals
    
    def format_price(self, price_cents):
        if price_cents == 0:
            return "Free"
        return f"${price_cents / 100:.2f}"
    
    def format_expiration(self, timestamp):
        if not timestamp:
            return "Limited time"
        try:
            dt = datetime.fromtimestamp(timestamp)
            now = datetime.now()
            delta = dt - now
            if delta.days > 0:
                return f"{delta.days} days left"
            elif delta.seconds > 3600:
                hours = delta.seconds // 3600
                return f"{hours} hours left"
            else:
                return "Ending soon"
        except:
            return "Limited time"
