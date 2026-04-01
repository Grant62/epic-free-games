# Steam热门游戏折扣推送配置

# 推送设置  
MAX_GAMES_TO_SHOW = 12       # 最多显示12款
MAX_GAMES_PER_CATEGORY = 12  # 推送12款

# Steam API配置
STEAM_API = {
    "featured_url": "https://store.steampowered.com/api/featuredcategories/",
    "appdetails_url": "https://store.steampowered.com/api/appdetails",
    "timeout": 30,
    "retry_times": 3,
    "retry_delay": 2,
}

WECHAT_WEBHOOK_ENV = "WECHAT_WEBHOOK_URL"
