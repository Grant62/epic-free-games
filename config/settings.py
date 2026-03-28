# Steam Game Push Configuration

# Threshold Settings
MIN_DISCOUNT_PERCENT = 25  # Discount >= 25%
MIN_REVIEW_COUNT = 500     # Reviews >= 500
MIN_REVIEW_SCORE = 75      # Review Score >= 75%

# Push Settings
MAX_GAMES_PER_CATEGORY = 10  # Max 10 games per category

# Steam API Configuration
STEAM_API = {
    "featured_url": "https://store.steampowered.com/api/featuredcategories/",
    "appdetails_url": "https://store.steampowered.com/api/appdetails",
    "timeout": 30,
    "retry_times": 3,
    "retry_delay": 2,
    "batch_size": 10,
    "rate_limit": 1.5,
}

WECHAT_WEBHOOK_ENV = "WECHAT_WEBHOOK_URL"
