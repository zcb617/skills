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
response.encoding = 'utf-8'

print(f"页面长度: {len(response.text)}")

# 查找最新的资源 (792xxx) 及其周围的文本
print("\n查找最新的资源及其上下文:")
pattern = r'(?:<[^>]*>)?.{0,30}details\.php\?id=(792\d+).{0,100}'
matches = re.findall(pattern, response.text, re.IGNORECASE)
print(f"找到 {len(matches)} 个匹配")

# 查找所有 792xxx 资源的详细信息
print("\n详细分析 792xxx 资源:")
seen_ids = set()
resource_count = 0

# 使用更宽泛的模式查找资源块
for match in re.finditer(r'details\.php\?id=(792\d+)', response.text):
    torrent_id = match.group(1)
    if torrent_id in seen_ids:
        continue
    seen_ids.add(torrent_id)
    
    # 获取匹配点前后的大段文本
    start = max(0, match.start() - 200)
    end = min(len(response.text), match.end() + 300)
    context = response.text[start:end]
    
    # 从上下文中提取标题
    title_match = re.search(r'>([^<]{5,100})<', context)
    title = title_match.group(1).strip() if title_match else f"资源 #{torrent_id}"
    
    # 从上下文中提取时间
    time_match = re.search(r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})', context)
    publish_time = time_match.group(1) if time_match else "未知"
    
    print(f"资源 {torrent_id}:")
    print(f"  标题: {title[:50]}")
    print(f"  时间: {publish_time}")
    print()
    
    resource_count += 1
    if resource_count >= 5:
        break

print(f"总共找到 {len(seen_ids)} 个不同的 792xxx 资源")