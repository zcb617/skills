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

# 查找所有资源块的模式
# 看起来像是每个资源在一个<tr>标签中
pattern = r'<tr[^>]*>.*?details\.php\?id=(792\d+).*?</tr>'
matches = re.findall(pattern, response.text, re.DOTALL | re.IGNORECASE)
print(f"找到 {len(matches)} 个完整的资源行")

# 查找前几个完整的资源行
print("\n前5个完整资源行:")
for i, match in enumerate(re.finditer(pattern, response.text, re.DOTALL | re.IGNORECASE)):
    if i >= 5:
        break
    print(f"\n资源行 {i+1}:")
    row_content = match.group(0)
    print(row_content[:300] + "..." if len(row_content) > 300 else row_content)
    
    # 从这一行中提取 ID
    id_match = re.search(r'details\.php\?id=(792\d+)', row_content)
    if id_match:
        torrent_id = id_match.group(1)
        print(f"  ID: {torrent_id}")
        
        # 提取标题 (查找链接文本)
        title_match = re.search(r'<a[^>]*href=[\'"][^\'"]*details\.php\?id=' + torrent_id + r'[\'"][^>]*>([^<]+)</a>', row_content)
        if title_match:
            title = title_match.group(1).strip()
            print(f"  标题: {title}")
        else:
            print("  标题: 未找到")
            
        # 提取时间
        time_match = re.search(r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})', row_content)
        if time_match:
            publish_time = time_match.group(1)
            print(f"  时间: {publish_time}")
        else:
            print("  时间: 未找到")

# 保存页面内容用于分析
with open('/tmp/ttg_page.html', 'w', encoding='utf-8') as f:
    f.write(response.text)
print(f"\n页面已保存到 /tmp/ttg_page.html")