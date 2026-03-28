# Steam热门游戏推送配置

# 筛选门槛
MIN_ORIGINAL_PRICE = 40      # 原价 >= ¥40
MIN_DISCOUNT_PERCENT = 25    # 折扣 >= 25%
MIN_REVIEW_COUNT = 1000      # 评测数 >= 1000
MIN_REVIEW_SCORE = 80        # 好评率 >= 80%

# 推送设置
MAX_GAMES_TO_SHOW = 20       # 最多显示20条
SORT_BY_HEAT = True          # 按热度排序

# 爬取设置
MAX_GAMES_TO_FETCH = 500     # 最多爬取500个游戏
BATCH_SIZE = 10              # 每批查询10个
RATE_LIMIT = 1.0             # 请求间隔1秒

# Steam API配置
STEAM_API = {
    "featured_url": "https://store.steampowered.com/api/featuredcategories/",
    "search_url": "https://store.steampowered.com/search/results/",
    "appdetails_url": "https://store.steampowered.com/api/appdetails",
    "timeout": 30,
    "retry_times": 3,
    "retry_delay": 2,
}

WECHAT_WEBHOOK_ENV = "WECHAT_WEBHOOK_URL"
