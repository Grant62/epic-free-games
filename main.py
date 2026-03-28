import sys
import traceback
from src.steam_client import SteamClient
from src.game_filter import GameFilter
from src.message_builder import MessageBuilder
from src.wechat_sender import WeChatSender

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
        
        # 步骤1: 获取Steam精选数据
        print("\n📥 步骤1: 获取Steam精选折扣游戏...")
        featured_data = steam_client.get_featured_categories()
        
        if not featured_data:
            error_msg = "无法获取Steam数据"
            print(f"❌ {error_msg}")
            wechat_sender.send_text(f"Steam折扣推送失败\n\n{error_msg}")
            sys.exit(1)
        
        # 步骤2: 提取折扣游戏
        print("\n📋 步骤2: 提取折扣游戏...")
        discount_games = game_filter.extract_discount_games(featured_data)
        
        if not discount_games:
            print("⚠️ 今日暂无折扣游戏")
            message = message_builder.build_message([], [], 0)
            wechat_sender.send_message(message)
            print("\n✅ 已发送空结果通知")
            return
        
        print(f"✅ 找到 {len(discount_games)} 个折扣游戏")
        
        # 步骤3: 获取游戏详情
        print("\n📊 步骤3: 获取游戏评价信息...")
        app_ids = [game["appid"] for game in discount_games]
        game_details = steam_client.get_app_details(app_ids)
        
        if not game_details:
            print("⚠️ 无法获取游戏详情，使用基础信息推送")
            game_details = {}
        
        # 步骤4: 筛选高质量游戏
        print("\n🔍 步骤4: 筛选热门精品...")
        print("筛选条件: 原价≥¥30 | 折扣任意 | 好评≥80% | 评测≥1000")
        free_games, premium_deals = game_filter.filter_by_quality(discount_games, game_details)
        
        # 步骤5: 构建消息
        print("\n📝 步骤5: 构建推送消息...")
        message = message_builder.build_message(
            free_games, premium_deals, len(discount_games)
        )
        
        # 步骤6: 发送消息
        print("\n📤 步骤6: 推送到企业微信...")
        success = wechat_sender.send_message(message)
        
        if success:
            print("\n" + "=" * 70)
            print("✅ 推送成功!")
            print(f"   免费游戏: {len(free_games)} 款")
            print(f"   折扣游戏: {len(premium_deals)} 款")
            print(f"   总计: {len(free_games) + len(premium_deals)} 款")
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
