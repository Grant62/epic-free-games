from datetime import datetime
from config.settings import MAX_GAMES_PER_CATEGORY

class MessageBuilder:
    def build_message(self, free_games, premium_deals, total_checked):
        lines = []
        today = datetime.now().strftime("%m/%d")
        lines.append(f"Steam Daily Deals - {today}")
        lines.append("")
        
        if free_games:
            lines.append("=========================")
            lines.append("Free Games (High Quality)")
            lines.append("=========================")
            lines.append("")
            for i, game in enumerate(free_games[:MAX_GAMES_PER_CATEGORY], 1):
                lines.extend(self._format_free_game(game, i))
                lines.append("")
        
        if premium_deals:
            lines.append("=========================")
            lines.append("Premium Deals (Score>=80)")
            lines.append("=========================")
            lines.append("")
            for i, game in enumerate(premium_deals[:MAX_GAMES_PER_CATEGORY], 1):
                lines.extend(self._format_premium_game(game, i))
                lines.append("")
        
        if not free_games and not premium_deals:
            lines.append("No premium deals today")
            lines.append("")
            lines.append("Filter: Discount>=50% | Price>=¥50 | Review>=80% | Reviews>=10k")
            lines.append("")
        
        lines.append("=========================")
        lines.append(f"Checked: {total_checked} games -> Selected: {len(free_games) + len(premium_deals)} games")
        lines.append("More deals: https://store.steampowered.com/specials")
        
        return "
".join(lines)
    
    def _format_free_game(self, game, index):
        lines = []
        name = game["name"]
        original_price = f"¥{game['original_price'] / 100:.0f}"
        from src.game_filter import GameFilter
        expiration = GameFilter().format_expiration(game["discount_expiration"])
        appid = game["appid"]
        score = game["quality_score"]
        details = game["quality_details"]
        review_pct = details.get("review_score_pct", 0)
        total_reviews = details.get("total_reviews", 0)
        publishers = details.get("publishers", [])
        
        lines.append(f"{index}. {name}")
        if review_pct:
            lines.append(f"   Reviews: {review_pct}% | Count: {self._format_number(total_reviews)}")
        lines.append(f"   {original_price} -> FREE (-100%)")
        if publishers:
            lines.append(f"   Publisher: {publishers[0]}")
        lines.append(f"   Score: {score}")
        lines.append(f"   Expires: {expiration}")
        lines.append(f"   Link: https://store.steampowered.com/app/{appid}")
        return lines
    
    def _format_premium_game(self, game, index):
        lines = []
        name = game["name"]
        original_price = f"¥{game['original_price'] / 100:.0f}"
        final_price = f"¥{game['final_price'] / 100:.0f}"
        discount = game["discount_percent"]
        from src.game_filter import GameFilter
        expiration = GameFilter().format_expiration(game["discount_expiration"])
        appid = game["appid"]
        score = game["quality_score"]
        details = game["quality_details"]
        review_pct = details.get("review_score_pct", 0)
        total_reviews = details.get("total_reviews", 0)
        publishers = details.get("publishers", [])
        
        lines.append(f"{index}. {name}")
        if review_pct:
            lines.append(f"   Reviews: {review_pct}% | Count: {self._format_number(total_reviews)}")
        lines.append(f"   {original_price} -> {final_price} (-{discount}%)")
        if publishers:
            lines.append(f"   Publisher: {publishers[0]}")
        lines.append(f"   Score: {score}")
        lines.append(f"   Expires: {expiration}")
        lines.append(f"   Link: https://store.steampowered.com/app/{appid}")
        return lines
    
    @staticmethod
    def _format_number(num):
        if num >= 10000:
            return f"{num/10000:.0f}k"
        return str(num)
