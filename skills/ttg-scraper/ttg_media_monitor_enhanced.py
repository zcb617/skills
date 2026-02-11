#!/usr/bin/env python3
"""
TTG 影视音乐分类监控器 - 改进版
从列表页面直接提取标题和时间
"""

import requests
from bs4 import BeautifulSoup
import re
import time
import json
import os
from datetime import datetime
import subprocess


class TTGMediaMonitor:
    def __init__(self, config_file=None):
        self.base_url = "https://totheglory.im"
        self.media_url = "https://totheglory.im/browse.php?c=M"  # 影视音乐分类链接
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://totheglory.im/',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        self.session.headers.update(self.headers)
        
        # 从配置文件加载登录信息
        if config_file and os.path.exists(config_file):
            self.load_credentials(config_file)
        else:
            raise FileNotFoundError(f"配置文件不存在: {config_file}")
        
        # 存储已知的帖子ID，用于检测新内容
        self.known_posts_file = "/home/zhangcb/.openclaw/workspace/ttg-scraper/known_posts.json"
        self.known_posts = self.load_known_posts()
    
    def load_credentials(self, config_file):
        """从配置文件加载登录凭据"""
        with open(config_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            self.username = None
            self.password = None
            
            for line in lines:
                line = line.strip()
                if line.startswith('account='):
                    self.username = line.split('=', 1)[1]
                elif line.startswith('passwd='):
                    self.password = line.split('=', 1)[1]
    
    def load_known_posts(self):
        """加载已知的帖子ID"""
        if os.path.exists(self.known_posts_file):
            with open(self.known_posts_file, 'r', encoding='utf-8') as f:
                return set(json.load(f))
        return set()
    
    def save_known_posts(self):
        """保存已知的帖子ID"""
        with open(self.known_posts_file, 'w', encoding='utf-8') as f:
            json.dump(list(self.known_posts), f, ensure_ascii=False, indent=2)
    
    def login(self):
        """登录TTG网站"""
        # 直接提交登录（不先访问主页，避免会话问题）
        login_data = {
            'username': self.username,
            'password': self.password,
            'passan': '',
            'passid': '0',
            'lang': '0'
        }
        
        # 提交登录表单
        login_response = self.session.post(f"{self.base_url}/takelogin.php", data=login_data)
        
        # 检查登录是否成功（检查my.php）
        test_response = self.session.get(f"{self.base_url}/my.php")
        if "logout" in test_response.text.lower() and self.username in test_response.text:
            print("登录成功")
            return True
        else:
            print(f"登录失败。my.php状态: {test_response.url}")
            return False
    
    def scrape_media_section(self):
        """爬取影视音乐分类页面，直接从列表提取标题和时间"""
        # 登录
        if not self.login():
            raise Exception("登录失败，无法访问受保护的内容")
        
        # 访问影视音乐分类页面
        response = self.session.get(self.media_url)
        response.encoding = 'utf-8'  # 显式设置编码
        
        # 使用正则表达式解析资源行
        # 每个资源在 <tr class="hover_hr ..."> 标签中
        resource_pattern = r'<tr[^>]*class="[^"]*hover_hr[^"]*"[^>]*id=(\d+)[^>]*>(.*?)</tr>'
        resource_matches = re.findall(resource_pattern, response.text, re.DOTALL | re.IGNORECASE)
        
        new_movies = []
        
        for torrent_id, row_content in resource_matches:
            # 只处理新资源
            if torrent_id in self.known_posts:
                continue
            
            # 提取标题
            title = "未知标题"
            # 查找 <a href="/t/{id}/"> 标签内的文本
            title_pattern = r'<a[^>]*href="/t/' + torrent_id + r'/"[^>]*>(.*?)</a>'
            title_match = re.search(title_pattern, row_content, re.DOTALL)
            if title_match:
                # 清理HTML标签和多余空白
                title_html = title_match.group(1)
                # 移除HTML标签
                title = re.sub(r'<[^>]+>', '', title_html)
                # 清理多余空白
                title = re.sub(r'\s+', ' ', title).strip()
            
            # 提取发布时间
            publish_time = "未知"
            # 查找时间格式 YYYY-MM-DD HH:MM:SS
            time_pattern = r'<td[^>]*align=center[^>]*><nobr>(\d{4}-\d{2}-\d{2})<br\s*/?>(\d{2}:\d{2}:\d{2})</nobr></td>'
            time_match = re.search(time_pattern, row_content)
            if time_match:
                date_part = time_match.group(1)
                time_part = time_match.group(2)
                publish_time = f"{date_part} {time_part}"
            
            detail_url = f"{self.base_url}/details.php?id={torrent_id}"
            
            new_movies.append({
                'id': torrent_id,
                'title': title,
                'url': detail_url,
                'publish_time': publish_time
            })
        
        return new_movies
    
    def check_new_content(self):
        """检查是否有新内容"""
        try:
            # 爬取内容
            new_movies = self.scrape_media_section()
            
            # 更新已知帖子列表
            for movie in new_movies:
                self.known_posts.add(movie['id'])
            
            # 保存更新后的已知帖子列表
            self.save_known_posts()
            
            return new_movies
            
        except Exception as e:
            print(f"检查新内容时出错: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    def send_notifications(self, new_movies):
        """发送通知到钉钉和WhatsApp"""
        if not new_movies:
            return
        
        # 构建通知消息，包含标题、发布时间和链接
        message_lines = [f"🎬 发现 {len(new_movies)} 个新电影/音乐资源:"]
        for movie in new_movies:
            publish_info = f"[{movie['publish_time']}]" if movie.get('publish_time') not in ["未知", "获取失败"] else ""
            message_lines.append(f"• {movie['title']} {publish_info}")
            message_lines.append(f"  {movie['url']}")
        
        message = "\\n".join(message_lines)
        
        print(f"准备发送通知:\\n{message}")
        
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
    
    def run_check(self):
        """执行单次检查"""
        print(f"[{datetime.now()}] 开始检查TTG影视音乐分类新内容...")
        
        try:
            new_movies = self.check_new_content()
            
            if new_movies:
                print(f"发现 {len(new_movies)} 个新资源!")
                self.send_notifications(new_movies)
                return True
            else:
                print("暂无新资源")
                return False
                
        except Exception as e:
            print(f"检查过程中出错: {str(e)}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """主函数"""
    try:
        monitor = TTGMediaMonitor("/home/zhangcb/.totheglory")
        monitor.run_check()
    except Exception as e:
        print(f"程序执行出错: {str(e)}")


if __name__ == "__main__":
    main()