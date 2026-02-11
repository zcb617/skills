#!/usr/bin/env python3
"""
TTG (ToTheGlory) 网站内容爬取器 - 调试版
用于检查网站结构和登录流程
"""

import requests
from bs4 import BeautifulSoup
import re
import time
import json
import os
from datetime import datetime

class TTGScraperDebug:
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
    
    def debug_login_process(self):
        """调试登录过程"""
        print("开始调试登录流程...")
        
        # 访问主页
        print("访问主页...")
        response = self.session.get(self.base_url)
        print(f"主页状态码: {response.status_code}")
        
        # 查找登录相关链接
        soup = BeautifulSoup(response.content, 'html.parser')
        login_links = []
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            text = link.get_text()
            if 'login' in href.lower() or '登录' in text or 'signin' in href.lower():
                login_links.append((href, text))
        
        print(f"找到登录相关链接: {login_links}")
        
        # 如果没有找到登录链接，尝试访问常见登录页面
        if not login_links:
            login_pages = ['/login.php', '/member.php', '/ucp.php', '/login']
            for page in login_pages:
                try:
                    test_url = f"{self.base_url}{page}"
                    test_resp = self.session.get(test_url)
                    if test_resp.status_code == 200:
                        print(f"找到可能的登录页面: {test_url}")
                        login_links.append((page, f"Possible login page: {page}"))
                        break
                except:
                    continue
        
        if login_links:
            login_path = login_links[0][0]
            if login_path.startswith('/'):
                login_url = self.base_url + login_path
            elif login_path.startswith('http'):
                login_url = login_path
            else:
                login_url = self.base_url + '/' + login_path
            
            print(f"访问登录页面: {login_url}")
            login_response = self.session.get(login_url)
            print(f"登录页面状态码: {login_response.status_code}")
            
            # 分析登录页面结构
            soup = BeautifulSoup(login_response.content, 'html.parser')
            forms = soup.find_all('form')
            print(f"在登录页面找到 {len(forms)} 个表单")
            
            for i, form in enumerate(forms):
                print(f"表单 {i+1}:")
                inputs = form.find_all('input')
                print(f"  - 输入字段数量: {len(inputs)}")
                for inp in inputs:
                    name = inp.get('name')
                    type_attr = inp.get('type')
                    placeholder = inp.get('placeholder')
                    print(f"    - {type_attr}: {name} (placeholder: {placeholder})")
                
                # 尝试找出用户名和密码字段
                username_field = None
                password_field = None
                
                for inp in inputs:
                    name = inp.get('name', '').lower()
                    placeholder = inp.get('placeholder', '').lower()
                    
                    if any(x in name or x in placeholder for x in ['user', 'name', 'email', 'login', 'uid']):
                        username_field = inp.get('name')
                    elif any(x in name or x in placeholder for x in ['pass', 'pwd', 'password']):
                        password_field = inp.get('name')
                
                print(f"  - 推测用户名字段: {username_field}")
                print(f"  - 推测密码字段: {password_field}")
        
        return True


if __name__ == "__main__":
    scraper = TTGScraperDebug("/home/zhangcb/.totheglory")
    scraper.debug_login_process()