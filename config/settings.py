# Steam热门游戏折扣推送配置

# 筛选条件
MIN_ORIGINAL_PRICE = 30      # 原价 >= ¥30（无门槛）
MIN_REVIEW_COUNT = 1000      # 评测数 >= 1000
MIN_REVIEW_SCORE = 80        # 好评率 >= 80%

# 推送设置  
MAX_GAMES_TO_SHOW = 20       # 最多显示20款

# Steam API配置
STEAM_API = {
    "featured_url": "https://store.steampowered.com/api/featuredcategories/",
    "appdetails_url": "https://store.steampowered.com/api/appdetails",
    "timeout": 30,
    "retry_times": 3,
    "retry_delay": 2,
}

WECHAT_WEBHOOK_ENV = "WECHAT_WEBHOOK_URL"
