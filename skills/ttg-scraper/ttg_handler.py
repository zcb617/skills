#!/usr/bin/env python3
"""
TTG 监控处理器
处理 OpenClaw cron 事件并执行 TTG 网站监控
"""

import os
import sys
import subprocess
from datetime import datetime

def handle_ttg_check(event_text):
    """处理TTG检查事件"""
    print(f"[{datetime.now()}] 处理TTG检查事件: {event_text}")
    
    # 导入TTG媒体监控模块并执行检查
    try:
        # 临时添加工作目录到Python路径
        sys.path.insert(0, '/home/zhangcb/.openclaw/workspace/ttg-scraper')
        
        from ttg_media_monitor_enhanced import TTGMediaMonitor
        
        # 创建监控实例
        monitor = TTGMediaMonitor("/home/zhangcb/.totheglory")
        
        # 执行检查
        new_movies = monitor.check_new_content()
        
        if new_movies:
            print(f"发现 {len(new_movies)} 个新电影/音乐资源!")
            
            # 构建消息
            message_lines = [f"🎬 发现 {len(new_movies)} 个新电影/音乐资源:"]
            for movie in new_movies:
                message_lines.append(f"• {movie['title']}")
                message_lines.append(f"  {movie['url']}")
            
            message = "\\n".join(message_lines)
            
            # 发送钉钉通知
            try:
                cmd_dingtalk = [
                    "bash", "-c",
                    f'source /etc/profile && source /home/zhangcb/.nvm/nvm.sh && cd /home/zhangcb/.nvm/versions/node/v24.13.0/lib/node_modules/openclaw && openclaw message send --channel dingtalk --target "小张同学" --message "{message}"'
                ]
                result_dingtalk = subprocess.run(cmd_dingtalk, capture_output=True, text=True, timeout=30)
                if result_dingtalk.returncode == 0:
                    print("钉钉通知发送成功")
                else:
                    print(f"钉钉通知发送失败: {result_dingtalk.stderr}")
            except Exception as e:
                print(f"发送钉钉通知时出错: {str(e)}")
            
            # 发送WhatsApp通知
            try:
                cmd_whatsapp = [
                    "bash", "-c",
                    f'source /etc/profile && source /home/zhangcb/.nvm/nvm.sh && cd /home/zhangcb/.nvm/versions/node/v24.13.0/lib/node_modules/openclaw && openclaw message send --channel whatsapp --target +8618605738770 --message "{message}"'
                ]
                result_whatsapp = subprocess.run(cmd_whatsapp, capture_output=True, text=True, timeout=30)
                if result_whatsapp.returncode == 0:
                    print("WhatsApp通知发送成功")
                else:
                    print(f"WhatsApp通知发送失败: {result_whatsapp.stderr}")
            except Exception as e:
                print(f"发送WhatsApp通知时出错: {str(e)}")
        else:
            print("暂无新资源")
        
        return True
        
    except Exception as e:
        print(f"处理TTG检查时出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # 从命令行参数获取事件文本
    if len(sys.argv) > 1:
        event_text = sys.argv[1]
        handle_ttg_check(event_text)
    else:
        print("需要提供事件文本作为参数")