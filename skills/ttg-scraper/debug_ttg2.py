#!/usr/bin/env python3
import requests
import re

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://totheglory.im/',
})

# 读取登录信息
with open('/home/zhangcb/.totheglory', 'r') as f:
    for line in f:
        if line.startswith('account='):
            username = line.split('=', 1)[1].strip()
        elif line.startswith('passwd='):
            password = line.split('=', 1)[1].strip()

# 登录
login_data = {'username': username, 'password': password, 'passan': '', 'passid': '0', 'lang': '0'}
session.post('https://totheglory.im/takelogin.php', data=login_data)

# 访问列表页面，显式设置编码
response = session.get('https://totheglory.im/browse.php?c=M')
response.encoding = 'utf-8'  # 显式设置编码

print(f"页面长度: {len(response.text)}")

# 查找最新的资源 (792xxx)
print("\n查找最新的资源 (792xxx):")
latest_pattern = r'details\.php\?id=(792\d+)'
latest_matches = re.findall(latest_pattern, response.text)
print(f"找到 {len(latest_matches)} 个最新资源 ID")
if latest_matches:
    print(f"前10个: {latest_matches[:10]}")

# 查找包含最新资源的完整链接和标题
print("\n查找完整链接和标题:")
full_pattern = r'<a[^>]*href=[\'"](?:/)?details\.php\?id=792\d+[\'"][^>]*>([^<]+)</a>'
full_matches = re.findall(full_pattern, response.text)
print(f"找到 {len(full_matches)} 个完整匹配")
for i, title in enumerate(full_matches[:5]):
    print(f"  标题 {i+1}: {title}")

# 查找时间
print("\n查找时间:")
time_pattern = r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})'
time_matches = re.findall(time_pattern, response.text)
print(f"找到 {len(time_matches)} 个时间")
for i, t in enumerate(time_matches[:10]):
    print(f"  时间 {i+1}: {t}")

# 查找 JavaScript 数据
print("\n查找 JavaScript 数据:")
js_pattern = r'var\s+(\w+)\s*=\s*(\[.*?\]);'
js_matches = re.findall(js_pattern, response.text, re.DOTALL)
print(f"找到 {len(js_matches)} 个 JavaScript 变量")
for var_name, data in js_matches:
    if 'details' in data or '792' in data:
        print(f"  变量 {var_name}: 长度 {len(data)}")
        print(f"    数据片段: {data[:200]}...")