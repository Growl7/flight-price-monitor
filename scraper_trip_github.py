#!/usr/bin/env python3
"""
CA707航班价格监控 - 杭州直飞河内
专门监控国航CA707航班，价格转换为人民币
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
        return "3小时25分钟"
    
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

def fetch_ca707_price(depart_date=None):
    """获取CA707航班价格"""
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
        
        # 查找CA707航班信息
        # 查找 CA707 及其附近的价格
        ca707_pos = html.find('CA707')
        if ca707_pos == -1:
            return {
                "status": "error",
                "error": "未找到CA707航班",
                "date": depart_date or datetime.now().strftime("%Y-%m-%d")
            }
        
        # 向前搜索最近的价格
        search_area = html[max(0, ca707_pos-500):ca707_pos]
        price_matches = re.findall(r'"price":"(\d+)"', search_area)
        
        if not price_matches:
            return {
                "status": "error",
                "error": "未找到CA707航班价格",
                "date": depart_date or datetime.now().strftime("%Y-%m-%d")
            }
        
        price_usd = int(price_matches[-1])
        price_cny = price_usd * USD_TO_CNY
        
        # 查找飞行时长
        duration_match = re.search(r'"estimatedFlightDuration":"([^"]+)"', html[ca707_pos:ca707_pos+500])
        duration_raw = duration_match.group(1) if duration_match else "PT3H25M"
        duration = parse_duration(duration_raw)
        
        return {
            "status": "success",
            "date": depart_date or datetime.now().strftime("%Y-%m-%d"),
            "flight": {
                "flight_no": "CA707",
                "airline": "Air China (中国国航)",
                "departure_city": "杭州 (HGH)",
                "arrival_city": "河内 (HAN)",
                "price_usd": price_usd,
                "price_cny": price_cny,
                "duration": duration,
                "duration_raw": duration_raw,
                "is_nonstop": True
            },
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
    print("CA707航班价格监控（杭州直飞河内）")
    print(f"汇率: 1 USD = {USD_TO_CNY} CNY")
    print("=" * 70)
    
    all_results = []
    for date in target_dates:
        print(f"\n获取 {date} 的CA707航班价格...")
        result = fetch_ca707_price(date)
        all_results.append(result)
        
        if result["status"] == "success":
            flight = result["flight"]
            print(f"   航班: {flight['flight_no']} ({flight['airline']})")
            print(f"   价格: ¥{flight['price_cny']:.0f} (${flight['price_usd']} USD)")
            print(f"   时长: {flight['duration']}")
        else:
            print(f"   错误: {result.get('error')}")
    
    # 保存结果
    output = {
        "timestamp": datetime.now().isoformat(),
        "exchange_rate": USD_TO_CNY,
        "flight_info": {
            "flight_no": "CA707",
            "airline": "Air China (中国国航)",
            "route": "杭州 (HGH) → 河内 (HAN)",
            "duration": "约3小时25分钟",
            "type": "直飞"
        },
        "results": all_results
    }
    
    os.makedirs("output", exist_ok=True)
    with open("output/flight_prices.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    # 显示汇总
    print("\n" + "=" * 70)
    print("监控汇总:")
    print("=" * 70)
    print("航班: CA707 (Air China 中国国航)")
    print("航线: 杭州 (HGH) → 河内 (HAN)")
    print("类型: 直飞 | 时长: 约3小时25分钟")
    print("-" * 70)
    
    for result in all_results:
        if result["status"] == "success":
            flight = result["flight"]
            print(f"{result['date']}: ¥{flight['price_cny']:.0f} (${flight['price_usd']} USD)")
        else:
            print(f"{result['date']}: 查询失败")
    
    print("=" * 70)
    print(f"结果已保存到 output/flight_prices.json")

if __name__ == "__main__":
    main()
