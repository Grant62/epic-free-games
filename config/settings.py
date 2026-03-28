# Steam游戏推送配置

# 门槛设置
MIN_DISCOUNT_PERCENT = 25  # 折扣>=25%
MIN_REVIEW_COUNT = 1000  # 评测数>=1000
MIN_REVIEW_SCORE = 80  # 好评率>=80%

# 推送设置
MAX_GAMES_PER_CATEGORY = 10  # 最多推送10个

# Steam API配置
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
