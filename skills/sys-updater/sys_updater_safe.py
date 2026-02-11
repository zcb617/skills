#!/usr/bin/env python3
"""
Ubuntu 系统更新检查器
用于定期检查系统更新状态
"""

import subprocess
import json
import os
from datetime import datetime

class SysUpdater:
    def __init__(self):
        self.update_log_file = "/home/zhangcb/.openclaw/workspace/sys-updater/update_log.json"
        self.last_check_file = "/home/zhangcb/.openclaw/workspace/sys-updater/last_check.json"
        
    def run_command(self, command):
        """执行系统命令"""
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=300)
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Command timed out"
    
    def check_updates(self):
        """检查可用的系统更新（使用非特权命令）"""
        print("正在检查系统更新...")
        
        # 使用 apt list --upgradable 来检查更新，这不需要特权
        code, stdout, stderr = self.run_command("apt list --upgradable 2>/dev/null")
        
        if "Listing..." in stdout:
            packages = []
            lines = stdout.strip().split('\n')[1:]  # 跳过第一行 "Listing..."
            for line in lines:
                if line.strip() and '/' in line:
                    # 解析包信息
                    parts = line.split()
                    if len(parts) >= 1:
                        full_name = parts[0]
                        if '/' in full_name:
                            package_name = full_name.split('/')[0]
                        else:
                            package_name = full_name
                            
                        current_version = parts[1] if len(parts) > 1 else "unknown"
                        repository = parts[2] if len(parts) > 2 else "unknown"
                        
                        packages.append({
                            "name": package_name,
                            "current_version": current_version,
                            "repository": repository
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
        for pkg in update_info["packages"][:10]:  # 只显示前10个包，避免消息过长
            summary += f"• {pkg['name']}\n"
        
        if len(update_info["packages"]) > 10:
            summary += f"... 还有 {len(update_info['packages']) - 10} 个更新\n"
        
        summary += "\n建议在合适的时间执行系统更新。"
        return summary
    
    def send_notification(self, message):
        """发送通知"""
        # 通过 OpenClaw 发送通知到钉钉和 WhatsApp
        try:
            # 发送钉钉通知
            cmd_dingtalk = [
                "bash", "-c",
                f'source /etc/profile && source /home/zhangcb/.nvm/nvm.sh && cd /home/zhangcb/.nvm/versions/node/v24.13.0/lib/node_modules/openclaw && openclaw message send --channel dingtalk --target "小张同学" --message "{message}"'
            ]
            result_dingtalk = subprocess.run(cmd_dingtalk, capture_output=True, text=True, timeout=30)
            if result_dingtalk.returncode == 0:
                print("钉钉通知发送成功")
            else:
                print(f"钉钉通知发送失败: {result_dingtalk.stderr}")
        except Exception as e:
            print(f"发送钉钉通知时出错: {str(e)}")
        
        # 发送WhatsApp通知
        try:
            cmd_whatsapp = [
                "bash", "-c",
                f'source /etc/profile && source /home/zhangcb/.nvm/nvm.sh && cd /home/zhangcb/.nvm/versions/node/v24.13.0/lib/node_modules/openclaw && openclaw message send --channel whatsapp --target "+8618605738770" --message "{message}"'
            ]
            result_whatsapp = subprocess.run(cmd_whatsapp, capture_output=True, text=True, timeout=30)
            if result_whatsapp.returncode == 0:
                print("WhatsApp通知发送成功")
            else:
                print(f"WhatsApp通知发送失败: {result_whatsapp.stderr}")
        except Exception as e:
            print(f"发送WhatsApp通知时出错: {str(e)}")
    
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


def main():
    updater = SysUpdater()
    # 只运行检查，不执行更新
    updater.run_check_only()


if __name__ == "__main__":
    main()