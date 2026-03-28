import re
from config.publishers import is_premium_publisher
from config.settings import REVIEW_SCORE_LEVELS, REVIEW_COUNT_LEVELS, PRICE_LEVELS

class QualityCalculator:
    @staticmethod
    def calculate_review_score_score(review_score):
        if not review_score:
            return 0
        for threshold, score in sorted(REVIEW_SCORE_LEVELS.items(), reverse=True):
            if review_score >= threshold:
                return score
        return 0
    
    @staticmethod
    def calculate_review_count_score(total_reviews):
        if not total_reviews:
            return 0
        for threshold, score in sorted(REVIEW_COUNT_LEVELS.items(), reverse=True):
            if total_reviews >= threshold:
                return score
        return 0
    
    @staticmethod
    def calculate_price_score(original_price):
        if not original_price:
            return 0
        price_yuan = original_price / 100
        for threshold, score in sorted(PRICE_LEVELS.items(), reverse=True):
            if price_yuan >= threshold:
                return score
        return 0
    
    @classmethod
    def calculate_total_score(cls, game_data):
        reviews = game_data.get("reviews", {})
        review_summary = reviews.get("review_summary", "")
        review_score = None
        if review_summary:
            match = re.search(r'(\d+)%', review_summary)
            if match:
                review_score = int(match.group(1))
        
        total_reviews = 0
        if review_score is not None:
            match = re.search(r'([\d,]+) user reviews', review_summary)
            if match:
                total_reviews = int(match.group(1).replace(',', ''))
        else:
            recommendations = game_data.get("recommendations", {})
            total_reviews = recommendations.get("total", 0)
        
        price_overview = game_data.get("price_overview", {})
        original_price = price_overview.get("initial", 0)
        publishers = game_data.get("publishers", [])
        
        review_score_score = cls.calculate_review_score_score(review_score)
        review_count_score = cls.calculate_review_count_score(total_reviews)
        price_score = cls.calculate_price_score(original_price)
        publisher_score = 10 if any(is_premium_publisher(p) for p in publishers) else 0
        
        total = review_score_score + review_count_score + price_score + publisher_score
        
        return {
            "total_score": total,
            "breakdown": {
                "review_score": review_score_score,
                "review_count": review_count_score,
                "price": price_score,
                "publisher": publisher_score
            },
            "details": {
                "review_score_pct": review_score,
                "total_reviews": total_reviews,
                "original_price_yuan": original_price / 100 if original_price else 0,
                "publishers": publishers
            }
        }
