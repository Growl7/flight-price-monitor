#!/usr/bin/env python3
"""
机票价格监控主程序 - 使用Trip.com数据
"""
import sys
import os
import time
import random
from datetime import datetime

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper_trip import fetch_ca707_price
from database import Database
from web_generator import WebGenerator
from email_notifier import EmailNotifier
from config import MONITOR_DATES, FLIGHT_CONFIG, EMAIL_CONFIG

def main():
    """主函数"""
    print("=" * 60)
    print("CA707航班价格监控")
    print(f"航线: {FLIGHT_CONFIG['departure_city']} → {FLIGHT_CONFIG['arrival_city']}")
    print(f"监控日期: {', '.join(MONITOR_DATES)}")
    print("=" * 60)
    
    # 初始化数据库
    db = Database()
    
    # 抓取每个目标日期的价格
    print("\n1. 抓取价格数据...")
    all_results = []
    
    for i, date in enumerate(MONITOR_DATES):
        print(f"\n   抓取 {date}...")
        result = fetch_ca707_price(date, max_retries=2)
        all_results.append(result)
        
        # 保存到数据库
        if result["status"] == "success":
            flight = result.get("flight", {})
            if flight:
                flight_data = {
                    "flight_date": date,
                    "departure_time": flight.get("departure_time", "时刻待定"),
                    "arrival_time": flight.get("arrival_time", "时刻待定"),
                    "airline": flight.get("airline", "Air China"),
                    "flight_number": flight.get("flight_no", "CA707"),
                    "price": flight.get("price_cny", 0),
                    "crawl_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "crawl_date": datetime.now().strftime("%Y-%m-%d")
                }
                db.save_flight_price(flight_data)
                # 更新每日汇总
                db.update_daily_summary(date)
                
                print(f"      ✅ 航班: {flight.get('flight_no')} ({flight.get('airline')})")
                print(f"      💰 价格: ¥{flight.get('price_cny', 0):.0f}")
                print(f"      ⏱️ 时长: {flight.get('duration')}")
            else:
                print(f"      ⚠️ 未找到航班详情")
        else:
            print(f"      ❌ 查询失败: {result.get('error')}")
        
        # 每次请求后等待
        if i < len(MONITOR_DATES) - 1:
            wait_time = random.randint(15, 25)
            print(f"      ⏳ 等待{wait_time}秒...")
            time.sleep(wait_time)
    
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
    print("=" * 60)
    success_count = 0
    for result in all_results:
        if result["status"] == "success":
            flight = result.get("flight", {})
            if flight:
                success_count += 1
                print(f"   ✅ {result['date']}: ¥{flight.get('price_cny', 0):.0f}")
                print(f"      {flight.get('flight_no')} ({flight.get('airline')}) - {flight.get('duration')}")
        else:
            print(f"   ❌ {result['date']}: 查询失败")
    
    print("-" * 60)
    print(f"   成功: {success_count}/{len(all_results)} 个日期")
    print("=" * 60)
    print("监控完成！")

if __name__ == "__main__":
    main()
