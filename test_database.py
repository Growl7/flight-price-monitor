from database import Database
from datetime import datetime

def test_database():
    """测试数据库模块"""
    print("测试数据库模块...")
    
    db = Database()
    
    # 测试保存航班价格
    test_flight = {
        "flight_date": "2026-10-30",
        "departure_time": "08:00",
        "arrival_time": "10:30",
        "airline": "中国南方航空",
        "flight_number": "CZ8001",
        "price": 1500.0,
        "crawl_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "crawl_date": datetime.now().strftime("%Y-%m-%d")
    }
    
    db.save_flight_price(test_flight)
    print("✓ 保存航班价格成功")
    
    # 测试获取每日最低价
    min_price = db.get_daily_min_price("2026-10-30")
    print(f"✓ 获取每日最低价: {min_price}")
    
    # 测试获取价格历史
    history = db.get_price_history("2026-10-30")
    print(f"✓ 获取价格历史: {len(history)} 条记录")
    
    # 测试更新每日汇总
    db.update_daily_summary("2026-10-30")
    print("✓ 更新每日汇总成功")
    
    # 测试获取所有汇总
    summaries = db.get_all_summaries()
    print(f"✓ 获取所有汇总: {len(summaries)} 条记录")
    
    print("数据库模块测试完成！")

if __name__ == "__main__":
    test_database()