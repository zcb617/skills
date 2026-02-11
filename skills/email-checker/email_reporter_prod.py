#!/usr/bin/env python3
"""
邮件简报生成器 - 生产版
用于生成邮件摘要并发送通知（主要通过WhatsApp）
"""

import imaplib
import email
from email.header import decode_header
import json
import os
from datetime import datetime
import subprocess

class EmailReporter:
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
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            # 登录
            mail.login(self.username, self.password)
            return mail
        except Exception as e:
            print(f"连接邮箱失败: {str(e)}")
            return None
    
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
    
    def get_unread_emails(self):
        """获取未读邮件"""
        mail = self.connect_to_mailbox()
        if not mail:
            return []
        
        try:
            # 选择收件箱
            mail.select('INBOX')
            
            # 搜索未读邮件
            status, messages = mail.search(None, 'UNSEEN')
            
            if status != 'OK':
                print("搜索邮件失败")
                return []
            
            email_ids = messages[0].split()
            unread_emails = []
            
            for email_id in email_ids:
                # 获取邮件
                status, msg_data = mail.fetch(email_id, '(RFC822)')
                
                if status != 'OK':
                    continue
                
                # 解析邮件
                msg = email.message_from_bytes(msg_data[0][1])
                
                # 获取邮件ID
                email_uid = email_id.decode() if isinstance(email_id, bytes) else str(email_id)
                
                # 检查是否已经处理过这封邮件
                if email_uid in self.checked_emails:
                    continue
                
                # 解码邮件头部
                subject = self.decode_mime_words(msg.get("Subject", "无主题"))
                sender = self.decode_mime_words(msg.get("From", "未知发件人"))
                
                # 获取邮件正文
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))
                        
                        if content_type == "text/plain" and "attachment" not in content_disposition:
                            body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                            break
                else:
                    body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
                
                # 限制邮件正文长度
                if len(body) > 200:
                    body = body[:200] + "...（内容截断）"
                
                email_info = {
                    'id': email_uid,
                    'subject': subject,
                    'sender': sender,
                    'body': body,
                    'date': msg.get("Date", "未知日期")
                }
                
                unread_emails.append(email_info)
                self.checked_emails.add(email_uid)  # 标记为已检查
            
            return unread_emails
            
        except Exception as e:
            print(f"获取邮件失败: {str(e)}")
            return []
        finally:
            try:
                mail.close()
                mail.logout()
            except:
                pass
    
    def create_email_summary(self, emails):
        """创建邮件摘要"""
        if not emails:
            return "📭 您没有新邮件。"
        
        summary_lines = [f"📬 您有 {len(emails)} 封新邮件:"]
        
        for i, email_info in enumerate(emails, 1):
            # 清理邮件内容，避免特殊字符
            clean_subject = email_info['subject'].replace('"', "'").replace("'", "").replace('\\', '/')
            clean_sender = email_info['sender'].replace('"', "'").replace("'", "").replace('\\', '/')
            clean_body = email_info['body'][:100].replace('"', "'").replace("'", "").replace('\\', '/') if email_info['body'] else ""
            
            summary_lines.append(f"\n{i}. 📨 {clean_subject}")
            summary_lines.append(f"   📌 发件人: {clean_sender}")
            summary_lines.append(f"   📅 日期: {email_info['date']}")
            if clean_body:
                summary_lines.append(f"   📝 内容: {clean_body}...")
        
        return "\\n".join(summary_lines)
    
    def send_notification(self, message):
        """发送邮件简报通知到WhatsApp（主要渠道）"""
        print(f"准备发送邮件简报:\\n{message[:500]}...")  # 只打印前500个字符
        
        # 发送WhatsApp通知（主要通知渠道）
        try:
            cmd_whatsapp = [
                "bash", "-c",
                f'source /etc/profile && source /home/zhangcb/.nvm/nvm.sh && cd /home/zhangcb/.nvm/versions/node/v24.13.0/lib/node_modules/openclaw && openclaw message send --channel whatsapp --target "+8618605738770" --message \'{message[:2000]}\''
            ]
            result_whatsapp = subprocess.run(cmd_whatsapp, capture_output=True, text=True, timeout=30)
            if result_whatsapp.returncode == 0:
                print("✅ WhatsApp邮件简报发送成功")
            else:
                print(f"❌ WhatsApp邮件简报发送失败: {result_whatsapp.stderr}")
        except Exception as e:
            print(f"❌ 发送WhatsApp邮件简报时出错: {str(e)}")
    
    def generate_report(self):
        """生成邮件简报"""
        print(f"[{datetime.now()}] 开始生成邮件简报...")
        
        try:
            emails = self.get_unread_emails()
            
            if emails:
                print(f"发现 {len(emails)} 封新邮件!")
                
                # 创建邮件摘要
                summary = self.create_email_summary(emails)
                
                # 发送通知
                self.send_notification(summary)
                
                # 保存已检查的邮件ID
                self.save_checked_emails()
                
                return emails
            else:
                print("没有新邮件")
                # 即使没有新邮件，也发送一个通知
                no_new_msg = "📭 您没有新邮件。"
                self.send_notification(no_new_msg)
                return []
                
        except Exception as e:
            print(f"生成邮件简报过程中出错: {str(e)}")
            import traceback
            traceback.print_exc()
            return()


def main():
    """主函数"""
    try:
        reporter = EmailReporter("/home/zhangcb/.zhangchenbin@0573zzz.com")
        reporter.generate_report()
    except Exception as e:
        print(f"邮件简报生成器执行出错: {str(e)}")


if __name__ == "__main__":
    main()