#!/usr/bin/env python3
"""
邮件检查器 - 调试版
用于检查IMAP邮箱的新邮件，包含详细调试信息
"""

import imaplib
import email
from email.header import decode_header
import json
import os
from datetime import datetime
import subprocess

class EmailChecker:
    def __init__(self, config_file=None):
        # 从配置文件加载邮箱信息
        if config_file and os.path.exists(config_file):
            self.load_credentials(config_file)
        else:
            raise FileNotFoundError(f"配置文件不存在: {config_file}")
        
        # IMAP服务器信息
        self.imap_server = "imap.0573zzz.com"
        self.imap_port = 993  # SSL端口
        
        # 存储已检查的邮件ID，用于检测新邮件
        self.checked_emails_file = "/home/zhangcb/.openclaw/workspace/email-checker/checked_emails.json"
        self.checked_emails = self.load_checked_emails()
    
    def load_credentials(self, config_file):
        """从配置文件加载邮箱凭据"""
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
    
    def load_checked_emails(self):
        """加载已检查的邮件ID"""
        if os.path.exists(self.checked_emails_file):
            with open(self.checked_emails_file, 'r', encoding='utf-8') as f:
                return set(json.load(f))
        return set()
    
    def save_checked_emails(self):
        """保存已检查的邮件ID"""
        with open(self.checked_emails_file, 'w', encoding='utf-8') as f:
            json.dump(list(self.checked_emails), f, ensure_ascii=False, indent=2)
    
    def connect_to_mailbox(self):
        """连接到邮箱"""
        try:
            # 连接IMAP服务器
            print(f"正在连接到 {self.imap_server}:{self.imap_port}...")
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            print("✓ 服务器连接成功")
            
            # 尝试登录
            print(f"正在尝试登录用户: {self.username}")
            result = mail.login(self.username, self.password)
            print(f"✓ 登录成功: {result}")
            
            # 测试选择邮箱
            print("正在测试邮箱列表...")
            status, mailboxes = mail.list()
            if status == 'OK':
                print("✓ 邮箱列表获取成功")
                # 打印前几个邮箱名称
                for mb in mailboxes[:10]:  # 只打印前10个邮箱
                    print(f"  - {mb.decode('utf-8', errors='ignore')}")
            else:
                print("✗ 邮箱列表获取失败")
            
            return mail
        except Exception as e:
            print(f"✗ 连接邮箱失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def check_connection(self):
        """检查连接状态"""
        print(f"[{datetime.now()}] 开始检查邮箱连接...")
        
        try:
            mail = self.connect_to_mailbox()
            if mail:
                print("✓ 邮箱连接检查成功")
                
                # 尝试选择INBOX
                status, messages = mail.select('INBOX')
                if status == 'OK':
                    print("✓ INBOX选择成功")
                    
                    # 获取邮件数量
                    status, msg_ids = mail.search(None, 'ALL')
                    if status == 'OK':
                        emails = msg_ids[0].split()
                        print(f"✓ 找到 {len(emails)} 封邮件")
                        
                        # 搜索未读邮件
                        status, unread_msg_ids = mail.search(None, 'UNSEEN')
                        if status == 'OK':
                            unread_emails = unread_msg_ids[0].split()
                            print(f"✓ 找到 {len(unread_emails)} 封未读邮件")
                            
                            # 如果有未读邮件，获取前几封的详细信息
                            for i, email_id in enumerate(unread_emails[:3]):  # 只获取前3封
                                status, msg_data = mail.fetch(email_id, '(RFC822.HEADER)')
                                if status == 'OK':
                                    msg = email.message_from_bytes(msg_data[0][1])
                                    subject = self.decode_mime_words(msg.get("Subject", "无主题"))
                                    sender = self.decode_mime_words(msg.get("From", "未知发件人"))
                                    date = msg.get("Date", "未知日期")
                                    print(f"  - 未读邮件 {i+1}: {subject} (来自: {sender}, 日期: {date})")
                        else:
                            print("✗ 未读邮件搜索失败")
                    else:
                        print("✗ 邮件搜索失败")
                else:
                    print("✗ INBOX选择失败")
                
                # 关闭连接
                mail.close()
                mail.logout()
                print("✓ 邮箱连接已关闭")
                return True
            else:
                print("✗ 邮箱连接失败")
                return False
        except Exception as e:
            print(f"✗ 连接检查过程中出错: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def decode_mime_words(self, s):
        """解码MIME编码的字符串"""
        decoded_fragments = decode_header(s)
        decoded_string = ''
        for fragment, encoding in decoded_fragments:
            if isinstance(fragment, bytes):
                if encoding:
                    decoded_string += fragment.decode(encoding)
                else:
                    decoded_string += fragment.decode('utf-8', errors='ignore')
            else:
                decoded_string += fragment
        return decoded_string


def main():
    """主函数"""
    try:
        checker = EmailChecker("/home/zhangcb/.zhangchenbin@0573zzz.com")
        checker.check_connection()
    except Exception as e:
        print(f"邮件检查器执行出错: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()