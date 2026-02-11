#!/usr/bin/env python3
"""
Ubuntu 系统更新管理器
用于定期检查和安全更新系统
"""

import subprocess
import json
import os
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class SysUpdater:
    def __init__(self, config_file=None):
        self.update_log_file = "/home/zhangcb/.openclaw/workspace/sys-updater/update_log.json"
        self.last_check_file = "/home/zhangcb/.openclaw/workspace/sys-updater/last_check.json"
        
        # 加载配置文件
        self.config = {}
        if config_file and os.path.exists(config_file):
            with open(config_file, 'r') as f:
                self.config = json.load(f)
        
        # 通知设置
        self.notify_channels = self.config.get('notify_channels', ['DingTalk'])
        self.notify_targets = self.config.get('notify_targets', ['小张同学'])
        
    def run_command(self, command):
        """执行系统命令"""
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=300)
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Command timed out"
    
    def check_updates(self):
        """检查可用的系统更新"""
        print("正在检查系统更新...")
        
        # 更新包列表
        code, stdout, stderr = self.run_command("apt update")
        if code != 0:
            print(f"警告: 更新包列表时出现问题: {stderr}")
        
        # 检查可升级的包
        code, stdout, stderr = self.run_command("apt list --upgradable")
        
        if "Listing..." in stdout:
            packages = []
            lines = stdout.strip().split('\n')[1:]  # 跳过第一行 "Listing..."
            for line in lines:
                if line.strip() and '/' in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        package_name = parts[0].split('/')[0]
                        current_version = parts[1] if len(parts) > 1 else "unknown"
                        packages.append({
                            "name": package_name,
                            "current_version": current_version
                        })
            
            update_info = {
                "timestamp": datetime.now().isoformat(),
                "available_updates": len(packages),
                "packages": packages,
                "status": "updates_available" if packages else "up_to_date"
            }
            
            print(f"发现 {len(packages)} 个可更新的包")
            return update_info
        else:
            update_info = {
                "timestamp": datetime.now().isoformat(),
                "available_updates": 0,
                "packages": [],
                "status": "up_to_date"
            }
            print("系统已是最新版本")
            return update_info
    
    def create_update_summary(self, update_info):
        """创建更新摘要"""
        if update_info["status"] == "up_to_date":
            return "✅ 系统已是最新版本，无需更新"
        
        summary = f"🔄 发现 {update_info['available_updates']} 个系统更新:\n\n"
        for pkg in update_info["packages"]:
            summary += f"• {pkg['name']}\n"
        
        return summary
    
    def send_notification(self, message):
        """发送通知到配置的渠道和对象"""
        # 通过 OpenClaw 发送通知
        for channel, target in zip(self.notify_channels, self.notify_targets):
            try:
                cmd = [
                    "bash", "-c",
                    f'source /etc/profile && source /home/zhangcb/.nvm/nvm.sh && cd /home/zhangcb/.nvm/versions/node/v24.13.0/lib/node_modules/openclaw && openclaw message send --channel {channel.strip()} --target "{target.strip()}" --message "{message}"'
                ]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    print(f"{channel}通知发送成功")
                else:
                    print(f"{channel}通知发送失败: {result.stderr}")
            except Exception as e:
                print(f"发送{channel}通知时出错: {str(e)}")
    
    def backup_and_update(self):
        """备份并执行系统更新"""
        print("开始系统更新流程...")
        
        # 首先检查是否有更新
        update_info = self.check_updates()
        
        if update_info["status"] == "up_to_date":
            message = "✅ 系统检查完成：系统已是最新版本"
            self.send_notification(message)
            return True
        
        # 创建更新摘要
        summary = self.create_update_summary(update_info)
        message = f"🔄 系统更新通知：\n\n{summary}\n\n系统将在确认后开始更新流程。"
        self.send_notification(message)
        
        # 注意：在这个自动化脚本中，我们不会自动执行更新
        # 因为系统更新可能会影响运行中的服务
        # 实际的更新应由系统管理员确认后手动执行
        print("注意：为安全起见，此脚本不会自动执行系统更新")
        print("请在合适的时间手动执行：sudo apt upgrade")
        
        # 记录检查结果
        self.save_check_result(update_info)
        
        return True
    
    def save_check_result(self, update_info):
        """保存检查结果"""
        with open(self.last_check_file, 'w') as f:
            json.dump(update_info, f, indent=2)
    
    def get_last_check(self):
        """获取上次检查结果"""
        if os.path.exists(self.last_check_file):
            with open(self.last_check_file, 'r') as f:
                return json.load(f)
        return None
    
    def run_check_only(self):
        """只运行检查，不执行更新"""
        print("正在执行系统更新检查...")
        
        update_info = self.check_updates()
        summary = self.create_update_summary(update_info)
        
        # 发送检查结果通知
        message = f"📋 系统更新检查报告：\n\n{summary}"
        self.send_notification(message)
        
        # 保存检查结果
        self.save_check_result(update_info)
        
        return update_info


def main():
    # 使用默认配置文件路径
    config_file = os.path.expanduser("~/.sys_updater_config.json")
    updater = SysUpdater(config_file)
    # 只运行检查，不执行更新
    updater.run_check_only()


if __name__ == "__main__":
    main()