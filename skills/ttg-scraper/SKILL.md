# TTG Scraper Skill for OpenClaw
# Monitors TTG website for new movie releases

name: "TTG内容监控"
description: "监控TTG网站影视音乐分类的新内容，发现新电影时发送通知"
version: "1.0.0"
author: "OpenClaw Assistant"

# 配置要求
config:
  - name: "credentials_file"
    description: "TTG网站登录凭据文件路径"
    required: true
    default: "/home/zhangcb/.totheglory"
  - name: "monitor_times"
    description: "监控时间点（24小时制）"
    required: false
    default: ["08:00", "13:00", "19:00"]

# 依赖
dependencies:
  - name: "requests"
  - name: "beautifulsoup4"
  - name: "schedule"

# 工具定义
tools:
  - name: "ttg_check_now"
    description: "立即检查TTG网站的新内容"
    parameters:
      type: "object"
      properties: {}
    handler: "ttg_scraper.TTGScraper.check_new_content"

  - name: "ttg_get_latest_movies"
    description: "获取最新的电影列表"
    parameters:
      type: "object"
      properties: {}
    handler: "ttg_scraper.TTGScraper.get_latest_movies"

  - name: "ttg_start_monitor"
    description: "启动定时监控服务"
    parameters:
      type: "object"
      properties: {}
    handler: "ttg_monitor.run_scheduler"

# 使用说明
instructions: |
  这个技能提供TTG网站内容监控服务：
  
  1. 自动监控：每天在08:00、13:00、19:00检查新电影
  2. 实时通知：发现新电影时通过钉钉和WhatsApp发送通知
  3. 手动检查：可随时手动检查新内容
  
  注意事项：
  - 需要有效的TTG网站登录凭据
  - 需要网络访问TTG网站
  - 定时任务需要保持服务运行