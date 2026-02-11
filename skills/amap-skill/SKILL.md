# AMap Skill for OpenClaw
# Provides location services using AMap (Gaode Maps) API

name: "高德地图服务"
description: "使用高德地图API提供地点搜索、路径规划、天气查询和地理编码服务"
version: "1.0.0"
author: "OpenClaw Assistant"

# 配置要求
config:
  - name: "api_key"
    description: "高德地图API密钥"
    required: true
    env: "AMAP_API_KEY"

# 工具定义
tools:
  - name: "amap_search_places"
    description: "根据关键词搜索地点"
    parameters:
      type: "object"
      properties:
        keywords:
          type: "string"
          description: "搜索关键词，如餐厅、咖啡厅、景点等"
        city:
          type: "string"
          description: "城市名称，可选参数"
      required:
        - "keywords"
    handler: "amap_service.search_places"

  - name: "amap_search_nearby"
    description: "搜索指定位置附近的地点"
    parameters:
      type: "object"
      properties:
        keywords:
          type: "string"
          description: "搜索关键词"
        location:
          type: "string"
          description: "中心位置坐标，格式：经度,纬度"
        radius:
          type: "integer"
          description: "搜索半径，单位米，默认1000"
          default: 1000
      required:
        - "keywords"
        - "location"
    handler: "amap_service.search_nearby_places"

  - name: "amap_get_driving_route"
    description: "获取驾车路线规划"
    parameters:
      type: "object"
      properties:
        origin:
          type: "string"
          description: "起点坐标，格式：经度,纬度"
        destination:
          type: "string"
          description: "终点坐标，格式：经度,纬度"
      required:
        - "origin"
        - "destination"
    handler: "amap_service.get_driving_route"

  - name: "amap_get_walking_route"
    description: "获取步行路线规划"
    parameters:
      type: "object"
      properties:
        origin:
          type: "string"
          description: "起点坐标，格式：经度,纬度"
        destination:
          type: "string"
          description: "终点坐标，格式：经度,纬度"
      required:
        - "origin"
        - "destination"
    handler: "amap_service.get_walking_route"

  - name: "amap_get_cycling_route"
    description: "获取骑行路线规划"
    parameters:
      type: "object"
      properties:
        origin:
          type: "string"
          description: "起点坐标，格式：经度,纬度"
        destination:
          type: "string"
          description: "终点坐标，格式：经度,纬度"
      required:
        - "origin"
        - "destination"
    handler: "amap_service.get_cycling_route"

  - name: "amap_get_weather"
    description: "查询指定城市的天气"
    parameters:
      type: "object"
      properties:
        city:
          type: "string"
          description: "城市名称或城市adcode"
      required:
        - "city"
    handler: "amap_service.get_weather"

  - name: "amap_geocode"
    description: "将地址转换为坐标"
    parameters:
      type: "object"
      properties:
        address:
          type: "string"
          description: "详细地址"
        city:
          type: "string"
          description: "城市名称，可选"
      required:
        - "address"
    handler: "amap_service.geocode_address"

  - name: "amap_reverse_geocode"
    description: "将坐标转换为地址"
    parameters:
      type: "object"
      properties:
        location:
          type: "string"
          description: "坐标，格式：经度,纬度"
      required:
        - "location"
    handler: "amap_service.reverse_geocode"

# 使用说明
instructions: |
  这个技能提供了高德地图的各种服务：
  
  1. 地点搜索：可以搜索城市内的各种地点
  2. 附近搜索：可以搜索指定位置附近的地点
  3. 路径规划：提供驾车、步行、骑行路线规划
  4. 天气查询：查询城市天气信息
  5. 地理编码：地址与坐标的相互转换
  
  注意：使用前需要配置高德地图API密钥