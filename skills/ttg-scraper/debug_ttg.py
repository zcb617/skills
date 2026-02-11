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

# 访问列表页面
response = session.get('https://totheglory.im/browse.php?c=M')
print(f"页面长度: {len(response.text)}")

# 查看包含 details.php 的片段
print("\n包含 details.php 的片段:")
count = 0
for m in re.finditer(r'.{0,60}details\.php\?id=\d+.{0,60}', response.text, re.IGNORECASE):
    print(m.group().replace('\n', ' ').replace('\r', '')[:120])
    print('---')
    count += 1
    if count > 10:
        break

# 查找 JavaScript 数据块
print("\n\n查找可能的 JavaScript 数据:")
js_patterns = [
    r'var\s+\w+\s*=\s*\[.*?\]',
    r'rt\s*:\s*\[.*?\]',
    r'torrents?\s*:\s*\[.*?\]',
    r'new\s+Array\s*\([^)]+\)',
]

for p in js_patterns:
    matches = re.findall(p, response.text, re.DOTALL | re.IGNORECASE)
    if matches:
        print(f"\n模式 {p[:50]} 找到 {len(matches)} 个")
        for m in matches[:2]:
            print(f"  长度: {len(m)}")
            print(f"  内容: {m[:200]}...")