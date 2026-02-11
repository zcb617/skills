#!/usr/bin/env python3
"""
TTG (ToTheGlory) 网站内容爬取器
用于监控影视音乐分类的新内容并发送通知
"""

import requests
from bs4 import BeautifulSoup
import re
import time
import json
import os
from datetime import datetime
import hashlib

class TTGScraper:
    def __init__(self, config_file=None):
        self.base_url = "https://totheglory.im"
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://totheglory.im/',
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
        
        # 提取所有表单字段
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
            # 如果没有action，尝试使用takelogin.php
            login_submit_url = f"{self.base_url}/takelogin.php"
        
        login_response = self.session.post(login_submit_url, data=login_data)
        
        # 检查是否登录成功
        if "logout" in login_response.text.lower() or "退出" in login_response.text or "欢迎" in login_response.text:
            print("登录成功")
            return True
        else:
            # 检查是否重定向到登录页面（可能登录失败）
            if "login" in login_response.url.lower() or "password" in login_response.text.lower():
                print("登录失败：用户名或密码错误")
                print(f"响应URL: {login_response.url}")
                return False
            else:
                print("登录可能成功，但未找到预期的登录成功标识")
                print(f"响应URL: {login_response.url}")
                return True
    
    def scrape_media_section(self):
        """爬取影视音乐分类"""
        # 分类ID为 "电影" 的板块，通常在论坛中会有特定的fid
        # 需要先访问论坛主页以找到正确的分类链接
        forum_url = f"{self.base_url}/forum.php"
        response = self.session.get(forum_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 查找"影视&音乐Media"分类
        target_category = None
        for category in soup.find_all(['td', 'div'], class_=re.compile(r'.*category.*|.*forum.*', re.I)):
            if '影视' in category.get_text() or 'Media' in category.get_text() or '音乐' in category.get_text():
                target_category = category
                break
        
        if not target_category:
            # 如果没找到特定的分类，尝试寻找包含"电影"的板块
            movies_section = None
            for forum_link in soup.find_all('a', href=re.compile(r'/forum-\d+-')):
                if 'movie' in forum_link.get_text().lower() or '电影' in forum_link.get_text():
                    movies_section = forum_link
                    break
            
            if not movies_section:
                # 作为备选方案，尝试访问常见的电影分类ID
                # 这里我们假设电影分类的ID，实际可能需要根据网站结构调整
                movies_url = f"{self.base_url}/forum-345-1"  # 假设ID为345，实际可能不同
            else:
                movies_url = self.base_url + movies_section.get('href')
        else:
            # 从分类中找到电影子版块
            movies_links = target_category.find_all('a', href=re.compile(r'/forum-\d+-'))
            movies_url = None
            for link in movies_links:
                if 'movie' in link.get_text().lower() or '电影' in link.get_text():
                    movies_url = self.base_url + link.get('href')
                    break
            
            if not movies_url:
                # 如果没找到明确的"电影"链接，就访问整个影视分类
                # 这里需要根据实际网站结构进行调整
                forums = soup.find_all('a', href=re.compile(r'/forum-\d+-'))
                for forum in forums:
                    forum_text = forum.get_text()
                    if '影视' in forum_text or 'Media' in forum_text:
                        movies_url = self.base_url + forum.get('href')
                        break
        
        if not movies_url:
            # 如果还是找不到，尝试访问首页并查找相关链接
            response = self.session.get(self.base_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            # 尝试查找包含"电影"或"movie"的链接
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                text = link.get_text()
                if ('movie' in text.lower() or '电影' in text) and '/forum-' in href:
                    movies_url = self.base_url + href
                    break
        
        if not movies_url:
            # 如果仍找不到，返回错误
            raise Exception("无法找到电影分类，请检查网站结构")
        
        # 访问电影分类页面
        response = self.session.get(movies_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 查找主题列表
        new_movies = []
        topic_links = soup.find_all('a', href=re.compile(r'/thread-\d+'))
        
        for link in topic_links:
            thread_url = self.base_url + link.get('href')
            title = link.get_text().strip()
            
            # 提取帖子ID
            thread_match = re.search(r'/thread-(\d+)', thread_url)
            if thread_match:
                thread_id = thread_match.group(1)
                
                # 检查是否为新帖子
                if thread_id not in self.known_posts:
                    new_movies.append({
                        'id': thread_id,
                        'title': title,
                        'url': thread_url
                    })
        
        return new_movies
    
    def check_new_content(self):
        """检查是否有新内容"""
        try:
            # 登录
            self.login()
            
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
            return []
    
    def get_latest_movies(self):
        """获取最新电影列表"""
        return self.check_new_content()


# 示例用法
if __name__ == "__main__":
    scraper = TTGScraper("/home/zhangcb/.totheglory")
    new_movies = scraper.get_latest_movies()
    
    if new_movies:
        print(f"发现 {len(new_movies)} 个新电影:")
        for movie in new_movies:
            print(f"- {movie['title']} - {movie['url']}")
    else:
        print("暂无新电影")