import re

class QualityCalculator:
    """简单的质量计算器 - 只检查好评率和评测数"""
    
    @classmethod
    def calculate_total_score(cls, game_data):
        """
        返回游戏的好评率和评测数信息
        """
        # 获取评测信息
        reviews = game_data.get("reviews", {})
        review_summary = reviews.get("review_summary", "")
        
        # 解析好评率
        review_score = None
        if review_summary:
            match = re.search(r'(\d+)%', review_summary)
            if match:
                review_score = int(match.group(1))
        
        # 获取评测数量
        total_reviews = 0
        if review_score is not None:
            match = re.search(r'([\d,]+) user reviews', review_summary)
            if match:
                total_reviews = int(match.group(1).replace(',', ''))
        else:
            recommendations = game_data.get("recommendations", {})
            total_reviews = recommendations.get("total", 0)
        
        # 获取发行商信息
        publishers = game_data.get("publishers", [])
        
        return {
            "total_score": 0,  # 不再计算总分
            "breakdown": {},
            "details": {
                "review_score_pct": review_score,
                "total_reviews": total_reviews,
                "publishers": publishers
            }
        }
