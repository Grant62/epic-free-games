from datetime import datetime
from config.settings import QUALITY_THRESHOLD, MIN_DISCOUNT_PERCENT, MIN_ORIGINAL_PRICE
from src.quality_calculator import QualityCalculator

class GameFilter:
    def __init__(self):
        self.calculator = QualityCalculator()
    
    def extract_discount_games(self, featured_data):
        games = []
        if not featured_data or "specials" not in featured_data:
            return games
        specials = featured_data["specials"]
        if "items" not in specials:
            return games
        for item in specials["items"]:
            if not item.get("discounted", False):
                continue
            discount_percent = item.get("discount_percent", 0)
            original_price = item.get("original_price", 0)
            if discount_percent >= MIN_DISCOUNT_PERCENT and original_price >= MIN_ORIGINAL_PRICE * 100:
                games.append({
                    "appid": item.get("id"),
                    "name": item.get("name"),
                    "discount_percent": discount_percent,
                    "original_price": original_price,
                    "final_price": item.get("final_price", 0),
                    "header_image": item.get("header_image", ""),
                    "discount_expiration": item.get("discount_expiration", 0),
                })
        print(f"Extracted {len(games)} discounted games from Featured API")
        return games
    
    def categorize_games(self, games, details):
        free_games = []
        premium_deals = []
        for game in games:
            appid = game["appid"]
            game_detail = details.get(appid, {})
            quality_info = self.calculator.calculate_total_score(game_detail)
            total_score = quality_info["total_score"]
            game["quality_score"] = total_score
            game["quality_breakdown"] = quality_info["breakdown"]
            game["quality_details"] = quality_info["details"]
            if game["discount_percent"] == 100:
                if total_score >= QUALITY_THRESHOLD:
                    free_games.append(game)
            else:
                if total_score >= QUALITY_THRESHOLD:
                    premium_deals.append(game)
        free_games.sort(key=lambda x: x["quality_score"], reverse=True)
        premium_deals.sort(key=lambda x: x["quality_score"], reverse=True)
        print(f"Filter result: {len(free_games)} free games, {len(premium_deals)} premium deals")
        return free_games, premium_deals
    
    def format_price(self, price_cents):
        if price_cents == 0:
            return "Free"
        return f"Y{price_cents / 100:.0f}"
    
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
