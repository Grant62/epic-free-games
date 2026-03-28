import re
from datetime import datetime
from config.settings import (
    MIN_ORIGINAL_PRICE, MIN_DISCOUNT_PERCENT, 
    MIN_REVIEW_COUNT, MIN_REVIEW_SCORE, MAX_GAMES_TO_SHOW
)

class GameFilter:
    """游戏筛选器 - 按热度和好评率排序"""
    
    def filter_games(self, games: list, details: dict) -> tuple:
        """
        筛选并排序游戏
        返回: (免费游戏列表, 折扣游戏列表)
        """
        qualified = []
        
        for game in games:
            appid = game["appid"]
            game_detail = details.get(appid, {})
            
            # 获取基本信息
            original_price = game.get("original_price", 0)
            discount_percent = game.get("discount_percent", 0)
            
            # 检查基本条件
            if original_price < MIN_ORIGINAL_PRICE * 100:
                continue
            if discount_percent < MIN_DISCOUNT_PERCENT:
                continue
            
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
            
            # 检查评价门槛
            if not review_score or review_score < MIN_REVIEW_SCORE:
                continue
            if total_reviews < MIN_REVIEW_COUNT:
                continue
            
            # 计算热度分数（评测数 * 好评率）
            heat_score = total_reviews * (review_score / 100)
            
            # 保存筛选结果
            game["review_score"] = review_score
            game["review_count"] = total_reviews
            game["heat_score"] = heat_score
            game["final_price"] = game.get("final_price", int(original_price * (100 - discount_percent) / 100))
            
            qualified.append(game)
        
        print(f"通过筛选: {len(qualified)}/{len(games)} 个游戏")
        
        # 按热度排序（评测数 * 好评率）
        qualified.sort(key=lambda x: (x["heat_score"], x["discount_percent"]), reverse=True)
        
        # 分离免费游戏和折扣游戏
        free_games = [g for g in qualified if g["discount_percent"] == 100][:MAX_GAMES_TO_SHOW]
        premium_deals = [g for g in qualified if g["discount_percent"] < 100][:MAX_GAMES_TO_SHOW]
        
        print(f"结果: {len(free_games)} 个免费游戏, {len(premium_deals)} 个折扣游戏")
        return free_games, premium_deals
    
    def format_price(self, price_cents: int) -> str:
        """格式化价格"""
        if price_cents == 0:
            return "免费"
        return f"¥{price_cents / 100:.0f}"
    
    def format_number(self, num: int) -> str:
        """格式化数字"""
        if num >= 10000:
            return f"{num / 10000:.1f}万"
        return str(num)
