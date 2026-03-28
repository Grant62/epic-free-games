import re
from datetime import datetime
from config.settings import MIN_ORIGINAL_PRICE, MIN_REVIEW_COUNT, MIN_REVIEW_SCORE, MAX_GAMES_TO_SHOW

class GameFilter:
    """游戏筛选器"""
    
    def extract_discount_games(self, featured_data):
        """从Featured API提取所有折扣游戏"""
        games = []
        if not featured_data:
            return games
        
        # 从多个分类提取
        categories = ["specials", "top_sellers", "new_releases", "coming_soon"]
        seen_ids = set()
        
        for category in categories:
            if category not in featured_data:
                continue
            cat_data = featured_data[category]
            if "items" not in cat_data:
                continue
            
            print(f"  检查分类 '{category}': {len(cat_data['items'])} 个游戏")
            
            for item in cat_data["items"]:
                appid = item.get("id")
                if not appid or appid in seen_ids:
                    continue
                
                discount_percent = item.get("discount_percent", 0)
                original_price = item.get("original_price", 0)
                
                # 只要有折扣就收录（不限制折扣力度）
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
        
        print(f"✅ 共提取 {len(games)} 个折扣游戏")
        return games
    
    def filter_by_quality(self, games, details):
        """按质量筛选：好评率>=80% 且 评测数>=1000"""
        qualified = []
        
        for game in games:
            appid = game["appid"]
            original_price = game.get("original_price", 0)
            
            # 检查原价门槛（>=30元）
            if original_price < MIN_ORIGINAL_PRICE * 100:
                continue
            
            game_detail = details.get(appid, {})
            
            # 获取评价信息
            reviews = game_detail.get("reviews", {})
            review_summary = reviews.get("review_summary", "")
            
            # 解析好评率
            review_score = None
            if review_summary:
                match = re.search(r'(\d+)%', review_summary)
                if match:
                    review_score = int(match.group(1))
            
            # 解析评测数
            total_reviews = 0
            if review_summary:
                match = re.search(r'([\d,]+) user reviews', review_summary)
                if match:
                    total_reviews = int(match.group(1).replace(',', ''))
            else:
                recommendations = game_detail.get("recommendations", {})
                total_reviews = recommendations.get("total", 0)
            
            # 硬性门槛：好评率>=80% 且 评测数>=1000
            if not review_score or review_score < MIN_REVIEW_SCORE:
                continue
            if total_reviews < MIN_REVIEW_COUNT:
                continue
            
            # 计算热度分数
            heat_score = total_reviews * (review_score / 100)
            
            game["review_score"] = review_score
            game["review_count"] = total_reviews
            game["heat_score"] = heat_score
            
            qualified.append(game)
        
        print(f"✅ 通过质量筛选: {len(qualified)}/{len(games)} 个游戏")
        
        # 按热度排序（评测数 × 好评率）
        qualified.sort(key=lambda x: x["heat_score"], reverse=True)
        
        # 分离限时免费和普通折扣
        free_games = [g for g in qualified if g["discount_percent"] == 100][:MAX_GAMES_TO_SHOW]
        premium_deals = [g for g in qualified if g["discount_percent"] < 100][:MAX_GAMES_TO_SHOW]
        
        print(f"   免费游戏: {len(free_games)} 款")
        print(f"   折扣游戏: {len(premium_deals)} 款")
        
        return free_games, premium_deals
    
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
