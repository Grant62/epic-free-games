QUALITY_THRESHOLD = 80
MIN_DISCOUNT_PERCENT = 50
MIN_ORIGINAL_PRICE = 50
MAX_GAMES_PER_CATEGORY = 5

REVIEW_SCORE_LEVELS = {95: 40, 90: 35, 85: 30, 80: 20}
REVIEW_COUNT_LEVELS = {500000: 30, 200000: 25, 100000: 20, 50000: 15, 10000: 10, 1000: 5}
PRICE_LEVELS = {200: 20, 150: 15, 100: 10, 50: 5}

STEAM_API = {
    "featured_url": "https://store.steampowered.com/api/featuredcategories/",
    "appdetails_url": "https://store.steampowered.com/api/appdetails",
    "timeout": 30,
    "retry_times": 3,
    "retry_delay": 2,
    "batch_size": 50,
    "rate_limit": 1.5,
}

WECHAT_WEBHOOK_ENV = "WECHAT_WEBHOOK_URL"
