import sys
import traceback
from src.steam_client import SteamClient
from src.game_filter import GameFilter
from src.message_builder import MessageBuilder
from src.wechat_sender import WeChatSender

def main():
    print("Steam 每日精品游戏推送开始")
    try:
        steam_client = SteamClient()
        game_filter = GameFilter()
        message_builder = MessageBuilder()
        wechat_sender = WeChatSender()
        
        featured_data = steam_client.get_featured_categories()
        if not featured_data:
            wechat_sender.send_text("Steam 游戏推送失败：无法获取数据")
            sys.exit(1)
        
        discount_games = game_filter.extract_discount_games(featured_data)
        if not discount_games:
            message = message_builder.build_message([], [], 0)
            wechat_sender.send_message(message)
            return
        
        app_ids = [game["appid"] for game in discount_games]
        game_details = steam_client.get_app_details(app_ids)
        free_games, premium_deals = game_filter.categorize_games(discount_games, game_details)
        message = message_builder.build_message(free_games, premium_deals, len(discount_games))
        success = wechat_sender.send_message(message)
        
        if success:
            print(f"推送完成！限时免费：{len(free_games)} 款，精品折扣：{len(premium_deals)} 款")
        else:
            sys.exit(1)
    except Exception as e:
        print(f"程序执行出错：{e}")
        try:
            WeChatSender().send_text(f"Steam 游戏推送异常：{str(e)}")
        except:
            pass
        sys.exit(1)

if __name__ == "__main__":
    main()
