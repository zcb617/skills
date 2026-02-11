#!/usr/bin/env python3
"""
TTG 影视音乐分类监控器 - 使用准确的分类链接
用于监控TTG网站影视音乐分类的新内容并发送通知
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
        # 先访问主页获取一些可能需要的cookies
        self.session.get(self.base_url)
        
        # 访问登录页面
        login_url = f"{self.base_url}/login.php"
        response = self.session.get(login_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 查找登录表单（选择第一个包含用户名和密码字段的表单）
        form = None
        for potential_form in soup.find_all('form'):
            inputs = potential_form.find_all('input')
            has_username = any(inp.get('name') == 'username' for inp in inputs)
            has_password = any(inp.get('name') == 'password' for inp in inputs)
            if has_username and has_password:
                form = potential_form
                break
        
        if not form:
            raise Exception("无法找到包含用户名和密码字段的登录表单")
        
        # 提取所有表单字段，包括隐藏字段
        inputs = form.find_all('input')
        login_data = {}
        
        for inp in inputs:
            name = inp.get('name')
            value = inp.get('value', '')
            if name:
                login_data[name] = value
        
        # 设置用户名和密码
        login_data['username'] = self.username
        login_data['password'] = self.password
        
        # 查找提交按钮
        submit_button = form.find('input', {'type': 'submit'})
        if submit_button:
            btn_name = submit_button.get('name')
            btn_value = submit_button.get('value', 'Login')
            if btn_name:
                login_data[btn_name] = btn_value
            else:
                login_data['login'] = btn_value
        else:
            # 如果没有显式的提交按钮，添加常见的登录标识
            login_data['login'] = 'Login'
        
        # 提交登录表单
        login_action = form.get('action')
        if login_action:
            if login_action.startswith('http'):
                login_submit_url = login_action
            elif login_action.startswith('/'):
                login_submit_url = self.base_url + login_action
            else:
                # 如果是相对路径，需要构造完整URL
                login_submit_url = self.base_url + '/' + login_action
        else:
            # 如果没有action，使用takelogin.php
            login_submit_url = f"{self.base_url}/takelogin.php"
        
        # 尝试登录
        login_response = self.session.post(login_submit_url, data=login_data)
        
        # 检查登录是否成功
        success_indicators = [
            "logout" in login_response.text.lower(),
            "退出" in login_response.text,
            "欢迎" in login_response.text,
            "profile" in login_response.url.lower(),
            "my.php" in login_response.url.lower()
        ]
        
        if any(success_indicators):
            print("登录成功")
            return True
        else:
            # 尝试访问一个需要登录的页面来确认登录状态
            test_response = self.session.get(f"{self.base_url}/my.php")
            if "logout" in test_response.text.lower() or "退出" in test_response.text:
                print("登录成功（通过访问my.php确认）")
                return True
            else:
                print(f"登录可能失败。响应URL: {login_response.url}")
                print(f"状态码: {login_response.status_code}")
                return False
    
    def scrape_media_section(self):
        """爬取影视音乐分类页面第一页"""
        # 登录
        if not self.login():
            raise Exception("登录失败，无法访问受保护的内容")
        
        # 访问影视音乐分类页面第一页
        response = self.session.get(self.media_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 查找种子列表
        new_movies = []
        
        # 查找所有详情页链接（只处理当前页面的链接）
        detail_links = soup.find_all('a', href=re.compile(r'/details\.php\?id=\d+'))
        
        for link in detail_links:
            title = link.get_text().strip()
            id_match = re.search(r'id=(\d+)', link.get('href', ''))
            
            if id_match:
                torrent_id = id_match.group(1)
                
                if torrent_id not in self.known_posts:
                    detail_url = f"{self.base_url}/details.php?id={torrent_id}"
                    
                    new_movies.append({
                        'id': torrent_id,
                        'title': title,
                        'url': detail_url
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
        
        # 构建通知消息
        message_lines = [f"🎬 发现 {len(new_movies)} 个新电影/音乐资源:"]
        for movie in new_movies:
            message_lines.append(f"• {movie['title']}")
            message_lines.append(f"  {movie['url']}")
        
        message = "\\n".join(message_lines)
        
        print(f"准备发送通知: {message[:100]}...")  # 打印消息前100个字符
        
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