#!/usr/bin/env python3
"""
TTG 网站结构探测器 - 简化版
用于找到正确的电影分类ID
"""

import requests
from bs4 import BeautifulSoup
import re

def get_forum_structure():
    # 从配置文件加载登录凭据
    config_file = "/home/zhangcb/.totheglory"
    with open(config_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        username = None
        password = None
        
        for line in lines:
            line = line.strip()
            if line.startswith('account='):
                username = line.split('=', 1)[1]
            elif line.startswith('passwd='):
                password = line.split('=', 1)[1]
    
    # 创建会话
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })
    
    # 登录
    login_response = session.post('https://totheglory.im/takelogin.php', data={
        'username': username,
        'password': password,
        'login': 'Login'
    })
    
    if not ("logout" in login_response.text.lower() or "退出" in login_response.text):
        print("登录失败")
        return
    
    print("登录成功")
    
    # 访问论坛页面
    response = session.get("https://totheglory.im/forum.php")
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # 查找所有论坛链接并提取ID
    forum_links = soup.find_all('a', href=re.compile(r'forum-\d+'))
    
    print(f'找到 {len(forum_links)} 个论坛链接:')
    
    media_related = []
    for link in forum_links:
        href = link.get('href')
        text = link.get_text().strip()
        
        # 提取论坛ID
        forum_id_match = re.search(r'forum-(\d+)', href)
        if forum_id_match:
            forum_id = forum_id_match.group(1)
            print(f'  ID: {forum_id} - {text} - {href}')
            
            # 检查是否是媒体相关论坛
            if any(keyword in text.lower() for keyword in ['media', 'movie', 'music', '影视', '电影', '音乐', 'media']):
                media_related.append((forum_id, text, href))
    
    print(f'\\n找到 {len(media_related)} 个媒体相关论坛:')
    for fid, text, href in media_related:
        print(f'  ID: {fid} - {text} - {href}')
    
    if not media_related:
        print('\\n未找到明确标记为媒体的论坛，以下是所有论坛:')
        for link in forum_links[:10]:  # 只显示前10个
            href = link.get('href')
            text = link.get_text().strip()
            forum_id_match = re.search(r'forum-(\d+)', href)
            if forum_id_match:
                forum_id = forum_id_match.group(1)
                print(f'  ID: {forum_id} - {text}')

if __name__ == "__main__":
    get_forum_structure()