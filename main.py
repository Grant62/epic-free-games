import sys
import traceback
from src.steam_client import SteamClient
from src.game_filter import GameFilter
from src.message_builder import MessageBuilder
from src.wechat_sender import WeChatSender
from config.settings import MAX_GAMES_TO_FETCH

def main():
    print("=" * 70)
    print("🎮 Steam热门游戏折扣推送")
    print("=" * 70)
    
    try:
        # 初始化组件
        print("\n📦 初始化组件...")
        steam_client = SteamClient()
        game_filter = GameFilter()
        message_builder = MessageBuilder()
        wechat_sender = WeChatSender()
        
        # 步骤1: 爬取全站折扣游戏
        print("\n📥 步骤1: 爬取Steam全站折扣游戏...")
        print("(这个过程可能需要5-10分钟，请耐心等待)")
        discount_games = steam_client.fetch_all_discounted_games(MAX_GAMES_TO_FETCH)
        
        if not discount_games:
            print("❌ 未找到任何折扣游戏")
            wechat_sender.send_text("Steam折扣推送\n\n未找到符合条件的游戏")
            sys.exit(1)
        
        print(f"✅ 找到 {len(discount_games)} 个折扣游戏")
        
        # 步骤2: 批量获取游戏详情
        print("\n📊 步骤2: 获取游戏评价信息...")
        app_ids = [game["appid"] for game in discount_games]
        game_details = steam_client.get_app_details(app_ids)
        
        if not game_details:
            print("❌ 无法获取游戏详情")
            wechat_sender.send_text("Steam折扣推送\n\n获取游戏详情失败")
            sys.exit(1)
        
        # 步骤3: 筛选高质量游戏
        print("\n🔍 步骤3: 筛选热门精品游戏...")
        print(f"筛选条件: 原价≥¥40 | 折扣≥25% | 好评≥80% | 评测≥1000")
        free_games, premium_deals = game_filter.filter_games(discount_games, game_details)
        
        # 步骤4: 构建消息
        print("\n📝 步骤4: 构建推送消息...")
        message = message_builder.build_message(
            free_games, premium_deals, len(discount_games)
        )
        
        # 步骤5: 发送消息
        print("\n📤 步骤5: 推送到企业微信...")
        success = wechat_sender.send_message(message)
        
        if success:
            print("\n" + "=" * 70)
            print(f"✅ 推送成功!")
            print(f"   免费游戏: {len(free_games)} 款")
            print(f"   折扣游戏: {len(premium_deals)} 款")
            print(f"   总计: {len(free_games) + len(premium_deals)} 款精品")
            print("=" * 70)
        else:
            print("\n❌ 推送失败")
            sys.exit(1)
            
    except Exception as e:
        error_detail = traceback.format_exc()
        print(f"\n❌ 程序执行出错: {e}")
        print(error_detail)
        
        try:
            sender = WeChatSender()
            sender.send_text(f"Steam推送异常\n\n错误: {str(e)}\n\n请检查日志")
        except:
            pass
        
        sys.exit(1)

if __name__ == "__main__":
    main()
