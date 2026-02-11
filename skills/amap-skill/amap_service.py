# 高德地图技能
# 提供地点搜索、导航、天气、地理编码等功能

import os
import requests
from typing import Dict, Any, Optional

class AMapService:
    """
    高德地图服务类
    """
    def __init__(self):
        # 从环境变量或配置获取API密钥
        self.api_key = os.getenv('AMAP_API_KEY', '')
        if not self.api_key:
            raise ValueError("请设置高德地图API密钥 (AMAP_API_KEY)")
        
        self.base_url = "https://restapi.amap.com/v3"
        self.web_service_base_url = "https://restapi.amap.com/v3"

    def keyword_search(self, keywords: str, city: Optional[str] = None) -> Dict[Any, Any]:
        """
        关键词搜索地点
        """
        url = f"{self.web_service_base_url}/place/text"
        params = {
            'key': self.api_key,
            'keywords': keywords
        }
        
        if city:
            params['city'] = city
        
        response = requests.get(url, params=params)
        return response.json()

    def nearby_search(self, keywords: str, location: str, radius: int = 1000) -> Dict[Any, Any]:
        """
        附近搜索
        """
        url = f"{self.web_service_base_url}/place/around"
        params = {
            'key': self.api_key,
            'keywords': keywords,
            'location': location,
            'radius': radius
        }
        
        response = requests.get(url, params=params)
        return response.json()

    def driving_route(self, origin: str, destination: str) -> Dict[Any, Any]:
        """
        驾车路线规划
        """
        url = f"{self.web_service_base_url}/direction/driving"
        params = {
            'key': self.api_key,
            'origin': origin,
            'destination': destination
        }
        
        response = requests.get(url, params=params)
        return response.json()

    def walking_route(self, origin: str, destination: str) -> Dict[Any, Any]:
        """
        步行路线规划
        """
        url = f"{self.web_service_base_url}/direction/walking"
        params = {
            'key': self.api_key,
            'origin': origin,
            'destination': destination
        }
        
        response = requests.get(url, params=params)
        return response.json()

    def cycling_route(self, origin: str, destination: str) -> Dict[Any, Any]:
        """
        骑行路线规划
        """
        url = f"{self.web_service_base_url}/direction/bicycling"
        params = {
            'key': self.api_key,
            'origin': origin,
            'destination': destination
        }
        
        response = requests.get(url, params=params)
        return response.json()

    def weather_query(self, city: str) -> Dict[Any, Any]:
        """
        天气查询
        """
        url = f"{self.web_service_base_url}/weather/weatherInfo"
        params = {
            'key': self.api_key,
            'city': city,
            'extensions': 'all'
        }
        
        response = requests.get(url, params=params)
        return response.json()

    def geo_code(self, address: str, city: Optional[str] = None) -> Dict[Any, Any]:
        """
        地理编码（地址转坐标）
        """
        url = f"{self.web_service_base_url}/geocode/geo"
        params = {
            'key': self.api_key,
            'address': address
        }
        
        if city:
            params['city'] = city
        
        response = requests.get(url, params=params)
        return response.json()

    def reverse_geo_code(self, location: str) -> Dict[Any, Any]:
        """
        逆地理编码（坐标转地址）
        """
        url = f"{self.web_service_base_url}/geocode/regeo"
        params = {
            'key': self.api_key,
            'location': location
        }
        
        response = requests.get(url, params=params)
        return response.json()

# 初始化服务
amap_service = AMapService()

def search_places(keywords: str, city: Optional[str] = None):
    """
    搜索地点
    """
    return amap_service.keyword_search(keywords, city)

def search_nearby_places(keywords: str, location: str, radius: int = 1000):
    """
    搜索附近地点
    """
    return amap_service.nearby_search(keywords, location, radius)

def get_driving_route(origin: str, destination: str):
    """
    获取驾车路线
    """
    return amap_service.driving_route(origin, destination)

def get_walking_route(origin: str, destination: str):
    """
    获取步行路线
    """
    return amap_service.walking_route(origin, destination)

def get_cycling_route(origin: str, destination: str):
    """
    获取骑行路线
    """
    return amap_service.cycling_route(origin, destination)

def get_weather(city: str):
    """
    获取天气
    """
    return amap_service.weather_query(city)

def geocode_address(address: str, city: Optional[str] = None):
    """
    地址转坐标
    """
    return amap_service.geo_code(address, city)

def reverse_geocode(location: str):
    """
    坐标转地址
    """
    return amap_service.reverse_geo_code(location)