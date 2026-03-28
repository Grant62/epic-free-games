from datetime import datetime
from config.settings import MAX_GAMES_TO_SHOW

class MessageBuilder:
    """消息构建器"""
    
    def build_message(self, free_games, premium_deals, total_checked):
        """构建推送消息"""
        lines = []
        
        # 标题
        today = datetime.now().strftime("%m月%d日")
        lines.append(f"🎮 Steam热门游戏折扣 - {today}")
        lines.append("")
        
        # 免费游戏部分
        if free_games:
            lines.append("🔥 限时免费领取")
            lines.append("━━━━━━━━━━━━━━━━━━━━━━")
            for i, game in enumerate(free_games[:MAX_GAMES_TO_SHOW], 1):
                lines.extend(self._format_game(game, i, is_free=True))
                lines.append("")
        
        # 折扣游戏部分
        if premium_deals:
            lines.append(f"💎 热门折扣游戏 (前{min(len(premium_deals), MAX_GAMES_TO_SHOW)}款)")
            lines.append("━━━━━━━━━━━━━━━━━━━━━━")
            for i, game in enumerate(premium_deals[:MAX_GAMES_TO_SHOW], 1):
                lines.extend(self._format_game(game, i, is_free=False))
                lines.append("")
        
        # 无结果提示
        if not free_games and not premium_deals:
            lines.append("😔 今日暂无符合条件的热门游戏")
            lines.append("")
            lines.append("📋 筛选条件:")
            lines.append("   • 原价 ≥ ¥30")
            lines.append("   • 好评率 ≥ 80%")
            lines.append("   • 评测数 ≥ 1000")
            lines.append("")
        
        # 统计信息
        lines.append("━━━━━━━━━━━━━━━━━━━━━━")
        lines.append(f"📊 检查 {total_checked} 个游戏 | 筛选出 {len(free_games) + len(premium_deals)} 款精品")
        lines.append(f"🎯 排序: 热度(评测数×好评率)")
        lines.append("")
        lines.append("👉 查看更多: https://store.steampowered.com/specials")
        
        return "\n".join(lines)
    
    def _format_game(self, game, index, is_free=False):
        """格式化单个游戏"""
        lines = []
        
        name = game["name"]
        original_price = game["original_price"]
        final_price = game["final_price"]
        discount = game["discount_percent"]
        review_score = game["review_score"]
        review_count = game["review_count"]
        appid = game["appid"]
        
        # 游戏标题
        if is_free:
            lines.append(f"{index}. 🎁 {name}")
            lines.append(f"   💰 ¥{int(original_price/100)} → **免费** ⭐")
        else:
            lines.append(f"{index}. 🎮 {name}")
            lines.append(f"   💰 ¥{int(original_price/100)} → ¥{int(final_price/100)} (-{discount}%)")
        
        # 评价信息
        lines.append(f"   ⭐ 好评率: {review_score}% | 评测: {self._format_number(review_count)}")
        
        # 链接
        lines.append(f"   🔗 https://store.steampowered.com/app/{appid}")
        
        return lines
    
    def _format_number(self, num):
        """格式化数字"""
        if num >= 10000:
            return f"{num/10000:.1f}万"
        return str(num)
