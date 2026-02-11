# Ubuntu 系统更新管理配置

name: "系统更新管理"
description: "定期检查Ubuntu系统更新并在必要时通知用户"
version: "1.0.1"
author: "OpenClaw Assistant"

# 配置要求
config:
  - name: "check_frequency"
    description: "检查频率（天）"
    required: false
    default: 7
  - name: "critical_threshold"
    description: "临界更新数量阈值，超过此数量时发送紧急通知"
    required: false
    default: 10
  - name: "config_file"
    description: "配置文件路径"
    required: false
    default: "~/.sys_updater_config.json"

# 配置文件格式
config_file_format: |
  {
    "notify_channels": ["DingTalk", "WhatsApp"],
    "notify_targets": ["小张同学", "+8618605738770"]
  }

# 工具定义
tools:
  - name: "check_system_updates"
    description: "检查系统可用更新"
    parameters:
      type: "object"
      properties: {}
    handler: "sys_updater.SysUpdater.check_updates"

  - name: "get_update_summary"
    description: "获取更新摘要"
    parameters:
      type: "object"
      properties: {}
    handler: "sys_updater.SysUpdater.create_update_summary"

  - name: "send_update_notification"
    description: "发送更新通知"
    parameters:
      type: "object"
      properties:
        message:
          type: "string"
          description: "通知消息"
      required:
        - "message"
    handler: "sys_updater.SysUpdater.send_notification"

# 使用说明
instructions: |
  这个技能提供系统更新管理功能：
  
  1. 定期检查系统更新
  2. 生成更新报告
  3. 通过配置文件中指定的通知渠道和对象发送通知
  4. 记录更新历史
  
  配置文件应包含以下信息：
  - notify_channels: 通知渠道列表（如["DingTalk", "WhatsApp"]）
  - notify_targets: 通知对象列表（如["小张同学", "+8618605738770"]）
  
  安全说明：脚本不会自动执行更新，需要人工确认以避免影响运行中的服务
  注意：请确保配置文件权限设置为仅所有者可读写（chmod 600）