#!/usr/bin/env python3
"""
机票价格监控主程序 - 使用Trip.com数据
"""
import sys
import os
from datetime import datetime

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper_trip import fetch_prices
from database import Database
from web_generator import WebGenerator
from email_notifier import EmailNotifier
from config import MONITOR_DATES, FLIGHT_CONFIG, EMAIL_CONFIG

def main():
    """主函数"""
    print("=" * 60)
    print("Trip.com机票价格监控")
    print(f"出发地: {FLIGHT_CONFIG['departure_city']}")
    print(f"目的地: {FLIGHT_CONFIG['arrival_city']}")
    print(f"监控日期: {', '.join(MONITOR_DATES)}")
    print("=" * 60)
    
    # 初始化数据库
    db = Database()
    
    # 抓取每个目标日期的价格
    print("\n1. 抓取价格数据...")
    all_results = []
    
    for date in MONITOR_DATES:
        print(f"   抓取 {date}...")
        result = fetch_prices(date)
        all_results.append(result)
        
        # 保存到数据库
        if result["status"] == "success" and result["stats"]["min_price_cny"]:
            # 获取第一个直飞航班的信息
            direct_flights = result.get("direct_flights", [])
            if direct_flights:
                flight = direct_flights[0]
                flight_data = {
                    "flight_date": date,
                    "departure_time": flight.get("departure_time", "时刻待定"),
                    "arrival_time": flight.get("arrival_time", "时刻待定"),
                    "airline": flight.get("airline", "Trip.com"),
                    "flight_number": flight.get("flight_no", "Direct"),
                    "price": result["stats"]["min_price_cny"],
                    "crawl_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "crawl_date": datetime.now().strftime("%Y-%m-%d")
                }
                db.save_flight_price(flight_data)
                # 更新每日汇总
                db.update_daily_summary(date)
                print(f"      最低价: ¥{result['stats']['min_price_cny']:.0f}")
                print(f"      航班: {flight.get('flight_no')} ({flight.get('airline')})")
                print(f"      时长: {flight.get('duration')}")
            else:
                flight_data = {
                    "flight_date": date,
                    "departure_time": "",
                    "arrival_time": "",
                    "airline": "Trip.com (直飞)",
                    "flight_number": "Direct",
                    "price": result["stats"]["min_price_cny"],
                    "crawl_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "crawl_date": datetime.now().strftime("%Y-%m-%d")
                }
                db.save_flight_price(flight_data)
                # 更新每日汇总
                db.update_daily_summary(date)
                print(f"      最低价: ¥{result['stats']['min_price_cny']:.0f}")
    
    # 生成网页报告
    print("\n2. 生成网页报告...")
    try:
        generator = WebGenerator()
        html_file = generator.generate_html()
        json_file = generator.generate_json_data()
        print(f"   HTML报告: {html_file}")
        print(f"   JSON数据: {json_file}")
    except Exception as e:
        print(f"   生成报告时出错: {e}")
    
    # 发送邮件
    print("\n3. 发送邮件报告...")
    try:
        notifier = EmailNotifier()
        notifier.send_daily_report()
        print("   邮件发送成功！")
    except Exception as e:
        print(f"   发送邮件时出错: {e}")
    
    # 显示汇总
    print("\n" + "=" * 60)
    print("监控汇总:")
    for result in all_results:
        if result["status"] == "success":
            stats = result["stats"]
            if stats["min_price_cny"]:
                print(f"   {result['date']}: ¥{stats['min_price_cny']:.0f} - ¥{stats['max_price_cny']:.0f}")
                # 显示航班详情
                for flight in result.get("direct_flights", [])[:3]:
                    print(f"     {flight['flight_no']} ({flight['airline']}) - ¥{flight['price_cny']:.0f} - {flight['duration']}")
            else:
                print(f"   {result['date']}: 未找到直飞航班")
    print("=" * 60)
    print("监控完成！")

if __name__ == "__main__":
    main()
