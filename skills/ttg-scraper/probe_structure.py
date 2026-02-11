#!/usr/bin/env python3
"""
TTG 网站结构探测器
用于找到正确的电影分类ID
"""

import requests
from bs4 import BeautifulSoup
import re
import sys
import os

def probe_ttg_structure():
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
    
    # 首先登录
    login_page_url = "https://totheglory.im/login.php"
    response = session.get(login_page_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # 查找登录表单
    form = None
    for potential_form in soup.find_all('form'):
        inputs = potential_form.find_all('input')
        has_username = any(inp.get('name') == 'username' for inp in inputs)
        has_password = any(inp.get('name') == 'password' for inp in inputs)
        if has_username and has_password:
            form = potential_form
            break
    
    if not form:
        print("无法找到登录表单")
        return
    
    # 提取所有表单字段
    inputs = form.find_all('input')
    login_data = {}
    
    for inp in inputs:
        name = inp.get('name')
        value = inp.get('value', '')
        if name:
            login_data[name] = value
    
    # 设置用户名和密码
    login_data['username'] = username
    login_data['password'] = password
    
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
        login_data['login'] = 'Login'
    
    # 提交登录表单
    login_action = form.get('action')
    if login_action:
        if login_action.startswith('/'):
            login_submit_url = "https://totheglory.im" + login_action
        else:
            login_submit_url = login_action
    else:
        login_submit_url = login_page_url
    
    login_response = session.post(login_submit_url, data=login_data)
    
    # 检查登录是否成功
    if not ("logout" in login_response.text.lower() or "退出" in login_response.text or "欢迎" in login_response.text):
        print("登录失败")
        return
    
    print("登录成功，开始探测网站结构...")
    
    # 访问论坛页面
    forum_response = session.get("https://totheglory.im/forum.php")
    forum_soup = BeautifulSoup(forum_response.content, 'html.parser')
    
    # 查找所有链接
    all_links = forum_soup.find_all('a', href=True)
    
    # 查找可能的媒体分类
    media_categories = []
    for link in all_links:
        href = link.get('href')
        text = link.get_text().strip()
        
        # 查找包含媒体相关关键词的链接
        if any(keyword in text.lower() for keyword in ['media', 'movie', 'film', 'music', '影视', '电影', '音乐']):
            media_categories.append((href, text))
        
        # 查找论坛链接
        if 'forum' in href and any(keyword in text.lower() for keyword in ['media', 'movie', 'film', 'music', '影视', '电影', '音乐']):
            media_categories.append((href, text))
    
    print(f"找到 {len(media_categories)} 个媒体相关分类:")
    for href, text in media_categories:
        print(f"  - {href}: {text}")
    
    # 如果没找到特定的媒体分类，列出所有论坛链接
    if not media_categories:
        print("\\n列出所有论坛链接:")
        forum_links = [(link.get('href'), link.get_text().strip()) for link in all_links if 'forum' in link.get('href', '')]
        for href, text in forum_links:
            print(f"  - {href}: {text}")
    
    # 也尝试访问主页
    main_response = session.get("https://totheglory.im/")
    main_soup = BeautifulSoup(main_response.content, 'html.parser')
    
    # 在主页上查找媒体相关链接
    main_media_links = []
    main_all_links = main_soup.find_all('a', href=True)
    for link in main_all_links:
        href = link.get('href')
        text = link.get_text().strip()
        
        if any(keyword in text.lower() for keyword in ['media', 'movie', 'film', 'music', '影视', '电影', '音乐']):
            main_media_links.append((href, text))
    
    print(f"\\n主页上找到 {len(main_media_links)} 个媒体相关链接:")
    for href, text in main_media_links:
        print(f"  - {href}: {text}")

if __name__ == "__main__":
    probe_ttg_structure()