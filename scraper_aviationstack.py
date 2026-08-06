import os
import requests
import json
from datetime import datetime, timedelta

# 从环境变量获取配置
API_KEY = os.environ.get('AVIATIONSTACK_API_KEY', '')
EMAIL_SENDER = os.environ.get('EMAIL_SENDER', '')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD', '')
EMAIL_RECEIVER = os.environ.get('EMAIL_RECEIVER', '')

def get_flight_schedules(api_key, dep_iata='HGH', arr_iata='HAN', date='2026-10-30'):
    """使用Aviationstack API获取航班时刻表"""
    url = "http://api.aviationstack.com/v1/flights"
    
    params = {
        'access_key': api_key,
        'dep_iata': dep_iata,
        'arr_iata': arr_iata,
        'flight_date': date,
        'limit': 100
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        data = response.json()
        
        if 'data' in data:
            return data['data']
        else:
            print(f"API响应: {data}")
            return []
    except Exception as e:
        print(f"API请求失败: {str(e)}")
        return []

def extract_flight_info(flights, date):
    """提取航班信息"""
    result = []
    
    for flight in flights:
        try:
            # 提取价格（Aviationstack免费版可能不包含价格）
            # 这里我们使用航班时刻信息
            departure = flight.get('departure', {})
            arrival = flight.get('arrival', {})
            flight_info = flight.get('flight', {})
            airline = flight.get('airline', {})
            
            flight_data = {
                "flight_date": date,
                "departure_time": departure.get('scheduled', ''),
                "arrival_time": arrival.get('scheduled', ''),
                "airline": airline.get('name', ''),
                "flight_number": flight_info.get('iata', ''),
                "price": 0,  # 免费API不包含价格
                "crawl_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "crawl_date": datetime.now().strftime("%Y-%m-%d")
            }
            result.append(flight_data)
        except Exception as e:
            print(f"解析航班信息失败: {str(e)}")
    
    return result

def save_to_database(flights):
    """保存到数据库"""
    import sqlite3
    
    db_path = "data/flights.db"
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS flight_schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            flight_date TEXT,
            departure_time TEXT,
            arrival_time TEXT,
            airline TEXT,
            flight_number TEXT,
            crawl_time TEXT
        )
    ''')
    
    for flight in flights:
        cursor.execute('''
            INSERT INTO flight_schedules 
            (flight_date, departure_time, arrival_time, airline, flight_number, crawl_time)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            flight["flight_date"],
            flight["departure_time"],
            flight["arrival_time"],
            flight["airline"],
            flight["flight_number"],
            flight["crawl_time"]
        ))
    
    conn.commit()
    conn.close()
    print(f"已保存 {len(flights)} 条航班时刻记录")

def generate_html_report(flights_by_date):
    """生成HTML报告"""
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>杭州直飞河内航班监控</title>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1000px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }}
        h1 {{ color: #333; text-align: center; }}
        .date-section {{ margin: 20px 0; padding: 15px; background: #f9f9f9; border-radius: 8px; }}
        .date-header {{ color: #4facfe; font-size: 1.2em; font-weight: bold; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #4facfe; color: white; }}
        .info {{ color: #666; margin: 10px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>杭州 → 河内 航班监控</h1>
        <p class="info">数据来源: Aviationstack API</p>
        <p class="info">更新时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
'''
    
    for date, flights in flights_by_date.items():
        html += f'''
        <div class="date-section">
            <div class="date-header">{date}</div>
            <table>
                <thead>
                    <tr>
                        <th>航空公司</th>
                        <th>航班号</th>
                        <th>起飞时间</th>
                        <th>到达时间</th>
                    </tr>
                </thead>
                <tbody>
'''
        for flight in flights:
            html += f'''
                    <tr>
                        <td>{flight["airline"]}</td>
                        <td>{flight["flight_number"]}</td>
                        <td>{flight["departure_time"]}</td>
                        <td>{flight["arrival_time"]}</td>
                    </tr>
'''
        html += '''
                </tbody>
            </table>
        </div>
'''
    
    html += '''
    </div>
</body>
</html>'''
    
    os.makedirs("output", exist_ok=True)
    with open("output/flight_schedules.html", "w", encoding="utf-8") as f:
        f.write(html)
    
    print("HTML报告已生成: output/flight_schedules.html")

def main():
    print(f"开始航班监控 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if not API_KEY:
        print("错误: 未设置AVIATIONSTACK_API_KEY环境变量")
        print("请在GitHub仓库的Secrets中添加API Key")
        return
    
    # 监控日期
    monitor_dates = [
        "2026-10-30",
        "2026-11-06",
        "2026-11-13",
        "2026-11-20",
        "2026-11-27"
    ]
    
    all_flights_by_date = {}
    
    for date in monitor_dates:
        print(f"\n查询 {date} 的航班...")
        flights = get_flight_schedules(API_KEY, date=date)
        
        if flights:
            flight_info = extract_flight_info(flights, date)
            all_flights_by_date[date] = flight_info
            print(f"找到 {len(flight_info)} 个航班")
            
            # 保存到数据库
            save_to_database(flight_info)
        else:
            print(f"未找到 {date} 的航班数据")
            all_flights_by_date[date] = []
        
        # 避免请求过快
        import time
        time.sleep(1)
    
    # 生成报告
    generate_html_report(all_flights_by_date)
    
    print(f"\n监控完成!")

if __name__ == "__main__":
    main()