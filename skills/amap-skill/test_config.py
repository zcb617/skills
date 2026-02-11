#!/usr/bin/env python3
"""
高德地图技能测试脚本
"""

import os
import sys
sys.path.append('/home/zhangcb/.openclaw/workspace/amap-skill')

def test_amap_config():
    """测试高德地图API配置"""
    api_key = os.getenv('AMAP_API_KEY')
    
    if not api_key:
        print("❌ 高德地图API密钥未设置")
        print("请设置环境变量 AMAP_API_KEY")
        print("例如: export AMAP_API_KEY='your_api_key_here'")
        return False
    else:
        print(f"✅ 高德地图API密钥已设置")
        print(f"API密钥前缀: {api_key[:6]}...")
        return True

def test_dependencies():
    """测试依赖项"""
    try:
        import requests
        print("✅ requests 库已安装")
        return True
    except ImportError:
        print("❌ requests 库未安装")
        print("请运行: pip3 install --break-system-packages requests")
        return False

def show_usage_examples():
    """显示使用示例"""
    print("\n📝 使用示例:")
    print("1. 地点搜索: 搜索附近的餐厅")
    print("2. 路径规划: 获取驾车/步行/骑行路线")
    print("3. 天气查询: 查询指定城市天气")
    print("4. 地理编码: 地址与坐标的相互转换")

if __name__ == "__main__":
    print("🔍 高德地图技能配置检查")
    print("="*40)
    
    config_ok = test_amap_config()
    deps_ok = test_dependencies()
    
    print()
    if config_ok and deps_ok:
        print("✅ 高德地图技能配置完成，可以使用")
    else:
        print("❌ 高德地图技能配置不完整")
    
    show_usage_examples()