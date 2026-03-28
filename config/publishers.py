PREMIUM_PUBLISHERS = {
    "Valve", "CD PROJEKT RED", "Rockstar Games", "Bethesda", "FromSoftware",
    "Capcom", "Square Enix", "Bandai Namco", "Sega", "Ubisoft",
    "Electronic Arts", "2K", "Activision", "Blizzard", "Naughty Dog",
    "Santa Monica Studio", "Larian Studios", "Mojang", "Paradox Interactive",
    "Game Science", "miHoYo", "Tencent Games", "NetEase Games"
}

def is_premium_publisher(name):
    if not name:
        return False
    return any(p.lower() in name.lower() for p in PREMIUM_PUBLISHERS)
