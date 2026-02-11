# 邮件检查器技能

name: "邮件检查器"
description: "定期检查IMAP邮箱的新邮件并发送通知"
version: "1.0.1"
author: "OpenClaw Assistant"

# 配置要求
config:
  - name: "email_config_file"
    description: "邮箱配置文件路径"
    required: true
    default: "~/.email_checker_config"
  - name: "check_interval"
    description: "检查间隔（分钟）"
    required: false
    default: 30

# 配置文件格式
config_file_format: |
  account=your_email@example.com
  passwd=your_password
  imap_server=imap.example.com
  imap_port=993
  notify_channels=WhatsApp,DingTalk
  notify_targets=+8618605738770,小张同学

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
  3. 通过配置文件中指定的通知渠道和对象发送邮件通知
  4. 记录已检查的邮件以避免重复通知
  
  配置文件应包含以下信息：
  - account: 邮箱账户
  - passwd: 邮箱密码
  - imap_server: IMAP服务器地址
  - imap_port: IMAP端口
  - notify_channels: 通知渠道列表（如WhatsApp,DingTalk）
  - notify_targets: 通知对象列表（如+8618605738770,小张同学）
  
  注意：请确保配置文件权限设置为仅所有者可读写（chmod 600）