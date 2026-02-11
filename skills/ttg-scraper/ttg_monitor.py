#!/usr/bin/env python3
"""
TTG 监控任务调度器
每天在指定时间检查新内容并发送通知
"""

import schedule
import time
import threading
from ttg_scraper import TTGScraper
import subprocess
import json
import os
from datetime import datetime

class TTGMonitor:
    def __init__(self):
        self.scraper = TTGScraper("/home/zhangcb/.totheglory")
        self.setup_schedule()
    
    def setup_schedule(self):
        """设置定时任务"""
        # 每天早上8点、下午1点、晚上7点执行
        schedule.every().day.at("08:00").do(self.check_and_notify)
        schedule.every().day.at("13:00").do(self.check_and_notify)
        schedule.every().day.at("19:00").do(self.check_and_notify)
    
    def send_notification(self, new_movies):
        """发送通知到钉钉和WhatsApp"""
        if not new_movies:
            return
        
        # 构建通知消息
        message_lines = [f"🎬 发现 {len(new_movies)} 个新电影:"]
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
    
    def check_and_notify(self):
        """检查新内容并发送通知"""
        print(f"[{datetime.now()}] 开始检查TTG新内容...")
        
        try:
            new_movies = self.scraper.get_latest_movies()
            
            if new_movies:
                print(f"发现 {len(new_movies)} 个新电影!")
                self.send_notification(new_movies)
            else:
                print("暂无新电影")
                
        except Exception as e:
            print(f"检查过程中出错: {str(e)}")
    
    def start_monitoring(self):
        """开始监控"""
        print("TTG监控服务已启动...")
        print("定时任务: 每天 08:00, 13:00, 19:00 检查新内容")
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次任务队列


def run_scheduler():
    """运行调度器的独立函数"""
    monitor = TTGMonitor()
    monitor.start_monitoring()


if __name__ == "__main__":
    # 启动监控服务
    run_scheduler()