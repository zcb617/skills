# 邮件检查器技能

name: "邮件检查器"
description: "定期检查IMAP邮箱的新邮件并发送通知"
version: "1.0.0"
author: "OpenClaw Assistant"

# 配置要求
config:
  - name: "email_config_file"
    description: "邮箱配置文件路径"
    required: true
    default: "/home/zhangcb/.zhangchenbin@0573zzz.com"
  - name: "imap_server"
    description: "IMAP服务器地址"
    required: false
    default: "imap.0573zzz.com"
  - name: "imap_port"
    description: "IMAP端口"
    required: false
    default: 993
  - name: "check_interval"
    description: "检查间隔（分钟）"
    required: false
    default: 30

# 工具定义
tools:
  - name: "check_new_emails"
    description: "检查新邮件"
    parameters:
      type: "object"
      properties: {}
    handler: "email_checker.EmailChecker.check_new_emails"

  - name: "get_unread_emails"
    description: "获取未读邮件"
    parameters:
      type: "object"
      properties: {}
    handler: "email_checker.EmailChecker.get_unread_emails"

# 使用说明
instructions: |
  这个技能提供邮件检查功能：
  
  1. 定期检查指定的IMAP邮箱
  2. 检测新邮件并提取邮件信息
  3. 通过钉钉和WhatsApp发送邮件通知
  4. 记录已检查的邮件以避免重复通知