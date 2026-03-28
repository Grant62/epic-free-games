import sys
import traceback
from src.steam_client import SteamClient
from src.game_filter import GameFilter
from src.message_builder import MessageBuilder
from src.wechat_sender import WeChatSender

def main():
    print("=" * 60)
    print("Steam Daily Premium Deals Started")
    print("=" * 60)
    
    try:
        print("Initializing components...")
        steam_client = SteamClient()
        game_filter = GameFilter()
        message_builder = MessageBuilder()
        wechat_sender = WeChatSender()
        
        print("Step 1: Fetching Steam featured categories...")
        featured_data = steam_client.get_featured_categories()
        
        if not featured_data:
            error_msg = "Failed to fetch Steam data"
            print(error_msg)
            wechat_sender.send_text(f"Steam deals failed\n{error_msg}")
            sys.exit(1)
        
        print("Step 2: Extracting discounted games...")
        discount_games = game_filter.extract_discount_games(featured_data)
        
        if not discount_games:
            print("No discounted games today")
            message = message_builder.build_message([], [], 0)
            wechat_sender.send_message(message)
            print("Done (no games)")
            return
        
        print("Step 3: Fetching game details...")
        app_ids = [game["appid"] for game in discount_games]
        game_details = steam_client.get_app_details(app_ids)
        
        print("Step 4: Filtering by quality (review score>=80%, count>=1000)...")
        free_games, premium_deals = game_filter.filter_by_quality(discount_games, game_details)
        
        print("Step 5: Building message...")
        message = message_builder.build_message(free_games, premium_deals, len(discount_games))
        
        print("Step 6: Sending to WeChat...")
        success = wechat_sender.send_message(message)
        
        if success:
            print("=" * 60)
            print(f"Done! Free: {len(free_games)}, Deals: {len(premium_deals)}")
            print("=" * 60)
        else:
            print("Failed to send")
            sys.exit(1)
            
    except Exception as e:
        error_detail = traceback.format_exc()
        print(f"Error: {e}")
        print(error_detail)
        try:
            sender = WeChatSender()
            sender.send_text(f"Steam deals error: {str(e)}")
        except:
            pass
        sys.exit(1)

if __name__ == "__main__":
    main()
