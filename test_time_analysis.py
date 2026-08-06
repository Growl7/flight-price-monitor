from database import Database
from datetime import datetime

def test_time_analysis():
    """测试时间段分析功能"""
    print("测试时间段分析功能...")
    
    db = Database()
    
    # 添加一些测试数据（不同时间点）
    test_flights = [
        {
            "flight_date": "2026-10-30",
            "departure_time": "08:00",
            "arrival_time": "10:30",
            "airline": "中国南方航空",
            "flight_number": "CZ8001",
            "price": 1500.0,
            "crawl_time": "2026-10-30 08:00:00",
            "crawl_date": "2026-10-30"
        },
        {
            "flight_date": "2026-10-30",
            "departure_time": "14:00",
            "arrival_time": "16:30",
            "airline": "中国东方航空",
            "flight_number": "MU5001",
            "price": 1200.0,
            "crawl_time": "2026-10-30 14:00:00",
            "crawl_date": "2026-10-30"
        },
        {
            "flight_date": "2026-10-30",
            "departure_time": "20:00",
            "arrival_time": "22:30",
            "airline": "越南航空",
            "flight_number": "VN8001",
            "price": 1800.0,
            "crawl_time": "2026-10-30 20:00:00",
            "crawl_date": "2026-10-30"
        },
        {
            "flight_date": "2026-11-06",
            "departure_time": "10:00",
            "arrival_time": "12:30",
            "airline": "中国南方航空",
            "flight_number": "CZ8002",
            "price": 1100.0,
            "crawl_time": "2026-11-06 10:00:00",
            "crawl_date": "2026-11-06"
        },
        {
            "flight_date": "2026-11-06",
            "departure_time": "16:00",
            "arrival_time": "18:30",
            "airline": "中国东方航空",
            "flight_number": "MU5002",
            "price": 1300.0,
            "crawl_time": "2026-11-06 16:00:00",
            "crawl_date": "2026-11-06"
        }
    ]
    
    # 保存测试数据
    for flight in test_flights:
        db.save_flight_price(flight)
    
    print("✓ 保存测试数据成功")
    
    # 测试获取小时统计
    hourly_stats = db.get_hourly_price_stats()
    print(f"✓ 获取小时统计: {len(hourly_stats)} 个小时段")
    
    # 测试获取特定日期的小时统计
    hourly_stats_date = db.get_hourly_price_stats("2026-10-30")
    print(f"✓ 获取特定日期小时统计: {len(hourly_stats_date)} 个小时段")
    
    # 测试获取最佳购买时间
    best_time = db.get_best_time_to_buy()
    if best_time:
        print(f"✓ 获取最佳购买时间:")
        print(f"  - 最佳时间段: {best_time['best_period']}")
        print(f"  - 最佳小时: {best_time['best_hour']}:00")
        print(f"  - 最低价: ¥{best_time['best_min_price']}")
    
    # 测试获取特定日期的最佳购买时间
    best_time_date = db.get_best_time_to_buy("2026-10-30")
    if best_time_date:
        print(f"✓ 获取特定日期最佳购买时间:")
        print(f"  - 最佳时间段: {best_time_date['best_period']}")
        print(f"  - 最佳小时: {best_time_date['best_hour']}:00")
        print(f"  - 最低价: ¥{best_time_date['best_min_price']}")
    
    # 测试获取价格趋势
    price_trend = db.get_price_trend_by_hour()
    print(f"✓ 获取价格趋势: {len(price_trend['hours'])} 个小时段")
    
    print("时间段分析功能测试完成！")

if __name__ == "__main__":
    test_time_analysis()