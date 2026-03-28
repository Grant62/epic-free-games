from datetime import datetime
from config.settings import MAX_GAMES_PER_CATEGORY

class MessageBuilder:
    def build_message(self, free_games, premium_deals, total_checked):
        lines = []
        today = datetime.now().strftime("%m/%d")
        lines.append("Steam Daily Deals - " + today)
        lines.append("")
        
        if free_games:
            lines.append("=========================")
            lines.append("FREE GAMES (Score>=75%, Reviews>=500)")
            lines.append("=========================")
            lines.append("")
            for i, game in enumerate(free_games[:MAX_GAMES_PER_CATEGORY], 1):
                lines.extend(self._format_game(game, i, is_free=True))
                lines.append("")
        
        if premium_deals:
            lines.append("=========================")
            lines.append("DISCOUNTED GAMES (Score>=75%, Reviews>=500)")
            lines.append("=========================")
            lines.append("")
            for i, game in enumerate(premium_deals[:MAX_GAMES_PER_CATEGORY], 1):
                lines.extend(self._format_game(game, i, is_free=False))
                lines.append("")
        
        if not free_games and not premium_deals:
            lines.append("No games meet criteria today")
            lines.append("")
            lines.append("Criteria: Discount>=25% | Review>=75% | Reviews>=500")
            lines.append("")
        
        lines.append("=========================")
        lines.append("Checked: " + str(total_checked) + " games | Found: " + str(len(free_games) + len(premium_deals)) + " games")
        lines.append("https://store.steampowered.com/specials")
        
        return "
".join(lines)
    
    def _format_game(self, game, index, is_free=False):
        lines = []
        name = game["name"]
        original_price = game.get("original_price", 0)
        final_price = game.get("final_price", 0)
        discount = game["discount_percent"]
        review_score = game.get("review_score", 0)
        review_count = game.get("review_count", 0)
        appid = game["appid"]
        
        from src.game_filter import GameFilter
        expiration = GameFilter().format_expiration(game.get("discount_expiration", 0))
        
        if is_free:
            price_str = "$" + str(original_price / 100) + " -> FREE"
        else:
            price_str = "$" + str(original_price / 100) + " -> $" + str(final_price / 100) + " (-" + str(discount) + "%)"
        
        lines.append(str(index) + ". " + name)
        lines.append("   Reviews: " + str(review_score) + "% | Count: " + self._format_number(review_count))
        lines.append("   Price: " + price_str)
        lines.append("   Expires: " + expiration)
        lines.append("   Link: https://store.steampowered.com/app/" + str(appid))
        return lines
    
    @staticmethod
    def _format_number(num):
        if num >= 1000:
            return str(int(num/1000)) + "k"
        return str(num)
