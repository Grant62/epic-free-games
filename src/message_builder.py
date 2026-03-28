from datetime import datetime
from config.settings import MAX_GAMES_PER_CATEGORY

class MessageBuilder:
    def build_message(self, free_games, premium_deals, total_checked):
        lines = []
        today = datetime.now().strftime("%m月%d日")
        lines.append(f"Steam 每日精选 - {today}")
        lines.append("")
        
        if free_games:
            lines.append("=========================")
            lines.append("限时免费（高质量精品）")
            lines.append("=========================")
            lines.append("")
            for i, game in enumerate(free_games[:MAX_GAMES_PER_CATEGORY], 1):
                lines.extend(self._format_free_game(game, i))
                lines.append("")
        
        if premium_deals:
            lines.append("=========================")
            lines.append("今日精品折扣（精品分≥80）")
            lines.append("=========================")
            lines.append("")
            for i, game in enumerate(premium_deals[:MAX_GAMES_PER_CATEGORY], 1):
                lines.extend(self._format_premium_game(game, i))
                lines.append("")
        
        if not free_games and not premium_deals:
            lines.append("今日暂无符合条件的精品折扣")
            lines.append("")
            lines.append("筛选标准：折扣≥50% | 原价≥￥50 | 好评≥80% | 评测≥1万")
            lines.append("")
        
        lines.append("=========================")
        lines.append(f"数据：检查 {total_checked} 款 → 精选 {len(free_games) + len(premium_deals)} 款")
        lines.append("查看更多折扣：https://store.steampowered.com/specials")
        
        return "\n".join(lines)
    
    def _format_free_game(self, game, index):
        lines = []
        name = game["name"]
        original_price = f"￥{game['original_price'] / 100:.0f}"
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
            lines.append(f"   好评率：{review_pct}% | 评测：{self._format_number(total_reviews)}")
        lines.append(f"   {original_price} → 免费（-100%）")
        if publishers:
            lines.append(f"   发行商：{publishers[0]}")
        lines.append(f"   精品分：{score}")
        lines.append(f"   截止：{expiration}")
        lines.append(f"   链接：https://store.steampowered.com/app/{appid}")
        return lines
    
    def _format_premium_game(self, game, index):
        lines = []
        name = game["name"]
        original_price = f"￥{game['original_price'] / 100:.0f}"
        final_price = f"￥{game['final_price'] / 100:.0f}"
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
            lines.append(f"   好评率：{review_pct}% | 评测：{self._format_number(total_reviews)}")
        lines.append(f"   {original_price} → {final_price}（-{discount}%）")
        if publishers:
            lines.append(f"   发行商：{publishers[0]}")
        lines.append(f"   精品分：{score}")
        lines.append(f"   截止：{expiration}")
        lines.append(f"   链接：https://store.steampowered.com/app/{appid}")
        return lines
    
    @staticmethod
    def _format_number(num):
        if num >= 10000:
            return f"{num/10000:.0f}万"
        return str(num)
