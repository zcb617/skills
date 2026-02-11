#!/usr/bin/env python3
"""
高德地图技能实现
使用高德地图API进行位置服务查询
"""

import json
import urllib.parse
import urllib.request
from typing import Dict, Any, Optional

class AMapSkill:
    """
    高德地图技能类
    提供地点搜索、导航、天气、地理编码等功能
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://restapi.amap.com/v3"
        self.web_service_base_url = "https://restapi.amap.com/v3"
    
    def keyword_search(self, keywords: str, city: Optional[str] = None) -> Dict[Any, Any]:
        """
        根据关键词搜索地点
        """
        url = f"{self.web_service_base_url}/place/text"
        params = {
            'key': self.api_key,
            'keywords': keywords
        }
        
        if city:
            params['city'] = city
            
        return self._make_request(url, params)
    
    def nearby_search(self, keywords: str, location: str, radius: int = 1000) -> Dict[Any, Any]:
        """
        搜索附近地点
        """
        url = f"{self.web_service_base_url}/place/around"
        params = {
            'key': self.api_key,
            'keywords': keywords,
            'location': location,
            'radius': radius
        }
        
        return self._make_request(url, params)
    
    def driving_route(self, origin: str, destination: str) -> Dict[Any, Any]:
        """
        驾车路径规划
        """
        url = f"{self.web_service_base_url}/direction/driving"
        params = {
            'key': self.api_key,
            'origin': origin,
            'destination': destination
        }
        
        return self._make_request(url, params)
    
    def walking_route(self, origin: str, destination: str) -> Dict[Any, Any]:
        """
        步行路径规划
        """
        url = f"{self.web_service_base_url}/direction/walking"
        params = {
            'key': self.api_key,
            'origin': origin,
            'destination': destination
        }
        
        return self._make_request(url, params)
    
    def cycling_route(self, origin: str, destination: str) -> Dict[Any, Any]:
        """
        骑行路径规划
        """
        url = f"{self.web_service_base_url}/direction/bicycling"
        params = {
            'key': self.api_key,
            'origin': origin,
            'destination': destination
        }
        
        return self._make_request(url, params)
    
    def weather_query(self, city: str) -> Dict[Any, Any]:
        """
        查询天气
        """
        url = f"{self.web_service_base_url}/weather/weatherInfo"
        params = {
            'key': self.api_key,
            'city': city,
            'extensions': 'all'
        }
        
        return self._make_request(url, params)
    
    def geo_code(self, address: str, city: Optional[str] = None) -> Dict[Any, Any]:
        """
        地址转坐标
        """
        url = f"{self.web_service_base_url}/geocode/geo"
        params = {
            'key': self.api_key,
            'address': address
        }
        
        if city:
            params['city'] = city
            
        return self._make_request(url, params)
    
    def reverse_geo_code(self, location: str) -> Dict[Any, Any]:
        """
        坐标转地址
        """
        url = f"{self.web_service_base_url}/geocode/regeo"
        params = {
            'key': self.api_key,
            'location': location
        }
        
        return self._make_request(url, params)
    
    def _make_request(self, url: str, params: Dict[str, Any]) -> Dict[Any, Any]:
        """
        发起HTTP请求
        """
        try:
            query_string = urllib.parse.urlencode(params)
            full_url = f"{url}?{query_string}"
            
            req = urllib.request.Request(full_url)
            response = urllib.request.urlopen(req)
            data = response.read().decode('utf-8')
            
            return json.loads(data)
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

# 示例用法
if __name__ == "__main__":
    # 注意：这里需要使用真实的API密钥
    # api_key = "YOUR_AMAP_API_KEY"
    # amap = AMapSkill(api_key)
    # result = amap.keyword_search("餐厅", "北京")
    # print(json.dumps(result, ensure_ascii=False, indent=2))
    pass