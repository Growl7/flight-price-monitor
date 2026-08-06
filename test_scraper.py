from scraper import FlightScraper

def test_scraper():
    """测试抓取模块"""
    print("测试抓取模块...")
    
    scraper = FlightScraper()
    
    # 测试抓取单个日期
    test_date = "2026-10-30"
    print(f"测试抓取日期: {test_date}")
    
    flights = scraper.scrape_flight_prices(test_date)
    print(f"✓ 抓取到 {len(flights)} 个航班")
    
    # 显示抓取结果
    for i, flight in enumerate(flights[:5], 1):  # 只显示前5个
        print(f"  航班 {i}: {flight.get('airline', '未知')} {flight.get('flight_number', '未知')} - ¥{flight.get('price', 0)}")
    
    print("抓取模块测试完成！")

if __name__ == "__main__":
    test_scraper()