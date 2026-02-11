# 配置 OpenClaw 以响应 TTG 监控事件

# 当接收到包含 "Check TTG for new movies" 的系统事件时，
# 执行 TTG 监控检查脚本

import sys
import os
sys.path.insert(0, '/home/zhangcb/.openclaw/workspace/ttg-scraper')

def handle_system_event(event_text):
    """处理系统事件"""
    if "Check TTG for new movies" in event_text:
        from ttg_handler import handle_ttg_check
        handle_ttg_check(event_text)
        return True
    return False

# 这个脚本会被 OpenClaw 在接收到系统事件时调用
if __name__ == "__main__":
    # 如果直接运行，可以用于测试
    if len(sys.argv) > 1:
        event_text = " ".join(sys.argv[1:])
        handle_system_event(event_text)