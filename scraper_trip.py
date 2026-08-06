#!/usr/bin/env python3
"""
Trip.com机票价格爬虫 - GitHub Actions版本
只监控直飞航班，价格转换为人民币，包含航班详情
"""
import requests
import re
import json
from datetime import datetime
import os

# 汇率配置 (USD to CNY)
USD_TO_CNY = 7.25

def parse_duration(duration_str):
    """解析飞行时长 (ISO 8601格式: PT3H25M)"""
    if not duration_str:
        return "未知"
    
    # 解析 PT3H25M 格式
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?', duration_str)
    if match:
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        if hours > 0 and minutes > 0:
            return f"{hours}小时{minutes}分钟"
        elif hours > 0:
            return f"{hours}小时"
        else:
            return f"{minutes}分钟"
    return duration_str

def fetch_prices(depart_date=None):
    """获取指定日期的直飞航班价格"""
    base_url = "https://www.trip.com/flights/hangzhou-to-hanoi/airfares-HGH-HAN/"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "sec-ch-ua": '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"'
    }
    
    try:
        # 构建URL
        url = base_url
        if depart_date:
            url = f"{base_url}?dcity=HGH&acity=HAN&departure={depart_date}"
        
        # 发送请求
        session = requests.Session()
        response = session.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        html = response.text
        
        # 提取航班信息
        # 查找所有价格、航班号、是否直飞、飞行时长、航空公司
        prices = re.findall(r'"price":"(\d+)"', html)
        flight_nos = re.findall(r'"flightNumber":"([^"]+)"', html)
        nonstop_flags = re.findall(r'"isNonstop":(true|false)', html)
        durations = re.findall(r'"estimatedFlightDuration":"([^"]+)"', html)
        airlines = re.findall(r'"provider":\{"@type":"Airline","name":"([^"]+)"', html)
        
        # 组合航班信息（假设它们按顺序对应）
        all_flights = []
        min_len = min(len(prices), len(flight_nos), len(nonstop_flags), len(durations), len(airlines))
        
        for i in range(min_len):
            flight = {
                'price_usd': int(prices[i]),
                'price_cny': int(prices[i]) * USD_TO_CNY,
                'flight_no': flight_nos[i],
                'is_nonstop': nonstop_flags[i].lower() == 'true',
                'duration': parse_duration(durations[i]),
                'duration_raw': durations[i],
                'airline': airlines[i],
                'departure_time': '时刻待定',
                'arrival_time': '时刻待定'
            }
            all_flights.append(flight)
        
        # 筛选直飞航班
        direct_flights = [f for f in all_flights if f["is_nonstop"]]
        
        # 提取直飞航班价格
        direct_prices_cny = [f["price_cny"] for f in direct_flights]
        
        # 计算统计数据
        if direct_prices_cny:
            stats = {
                "min_price_cny": min(direct_prices_cny),
                "max_price_cny": max(direct_prices_cny),
                "avg_price_cny": sum(direct_prices_cny) / len(direct_prices_cny),
                "min_price_usd": min(f["price_usd"] for f in direct_flights),
                "max_price_usd": max(f["price_usd"] for f in direct_flights),
                "direct_flight_count": len(direct_flights),
            }
        else:
            stats = {
                "min_price_cny": None,
                "max_price_cny": None,
                "avg_price_cny": None,
                "min_price_usd": None,
                "max_price_usd": None,
                "direct_flight_count": 0,
            }
        
        return {
            "status": "success",
            "date": depart_date or datetime.now().strftime("%Y-%m-%d"),
            "stats": stats,
            "direct_flights": direct_flights,
            "all_flights": all_flights,
            "exchange_rate": USD_TO_CNY
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "date": depart_date or datetime.now().strftime("%Y-%m-%d")
        }

def main():
    """主函数"""
    target_dates = [
        "2026-10-30",
        "2026-11-06",
        "2026-11-13",
        "2026-11-20",
        "2026-11-27"
    ]
    
    print("=" * 70)
    print("Trip.com机票价格监控（直飞航班 - 人民币）")
    print(f"汇率: 1 USD = {USD_TO_CNY} CNY")
    print("=" * 70)
    
    all_results = []
    for date in target_dates:
        print(f"\n获取 {date} 的直飞航班价格...")
        result = fetch_prices(date)
        all_results.append(result)
        
        if result["status"] == "success":
            stats = result["stats"]
            if stats["min_price_cny"]:
                print(f"   直飞航班数量: {stats['direct_flight_count']}")
                print(f"   最低价: ¥{stats['min_price_cny']:.0f} (${stats['min_price_usd']})")
                print(f"   最高价: ¥{stats['max_price_cny']:.0f} (${stats['max_price_usd']})")
                
                # 显示航班详情
                print(f"   航班详情:")
                for flight in result["direct_flights"][:5]:
                    print(f"     - {flight['flight_no']} ({flight['airline']})")
                    print(f"       价格: ¥{flight['price_cny']:.0f} | 时长: {flight['duration']}")
            else:
                print(f"   未找到直飞航班")
        else:
            print(f"   错误: {result.get('error')}")
    
    # 保存结果
    output = {
        "timestamp": datetime.now().isoformat(),
        "exchange_rate": USD_TO_CNY,
        "results": all_results
    }
    
    os.makedirs("output", exist_ok=True)
    with open("output/flight_prices.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    # 显示汇总
    print("\n" + "=" * 70)
    print("监控汇总:")
    print("=" * 70)
    for result in all_results:
        if result["status"] == "success":
            stats = result["stats"]
            if stats["min_price_cny"]:
                print(f"{result['date']}: ¥{stats['min_price_cny']:.0f} - ¥{stats['max_price_cny']:.0f}")
                for flight in result["direct_flights"][:3]:
                    print(f"    {flight['flight_no']} ({flight['airline']}) - ¥{flight['price_cny']:.0f} - {flight['duration']}")
            else:
                print(f"{result['date']}: 未找到直飞航班")
    print("=" * 70)
    print(f"结果已保存到 output/flight_prices.json")

if __name__ == "__main__":
    main()
