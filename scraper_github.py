import os
import time
import re
from datetime import datetime

# 从环境变量获取配置
EMAIL_SENDER = os.environ.get('EMAIL_SENDER', '')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD', '')
EMAIL_RECEIVER = os.environ.get('EMAIL_RECEIVER', '')

def setup_driver():
    """设置Chrome驱动"""
    import undetected_chromedriver as uc
    
    options = uc.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    driver = uc.Chrome(options=options)
    return driver

def scrape_flight_prices(driver, date):
    """抓取指定日期的航班价格"""
    url = f"https://flights.ctrip.com/online/list/oneway-hgh-han?depdate={date}&cabin=Y_S_C_F&adult=1&child=0&infant=0"
    print(f"正在抓取日期 {date} 的航班价格...")
    
    try:
        driver.get(url)
        time.sleep(5)  # 等待页面加载
        
        # 提取航班信息
        flights = extract_flight_info(driver, date)
        print(f"成功抓取 {len(flights)} 个航班信息")
        return flights
        
    except Exception as e:
        print(f"抓取失败: {str(e)}")
        return []

def extract_flight_info(driver, date):
    """从页面提取航班信息"""
    flights = []
    
    try:
        # 使用JavaScript提取数据
        data = driver.execute_script('''
            const flights = [];
            
            // 尝试获取航班列表
            const flightItems = document.querySelectorAll('.flight-item, .flight-item-v2, [class*="flight"]');
            
            flightItems.forEach(item => {
                try {
                    // 获取价格
                    const priceEl = item.querySelector('[class*="price"], .price');
                    if (priceEl) {
                        const priceText = priceEl.innerText;
                        const priceMatch = priceText.match(/[\\d,]+/);
                        if (priceMatch) {
                            const price = parseInt(priceMatch[0].replace(',', ''));
                            if (price > 0) {
                                // 获取其他信息
                                const departTime = item.querySelector('[class*="depart"]');
                                const airline = item.querySelector('[class*="airline"]');
                                const flightNo = item.querySelector('[class*="flight-no"]');
                                
                                flights.push({
                                    price: price,
                                    departure_time: departTime ? departTime.innerText.trim() : '',
                                    airline: airline ? airline.innerText.trim() : '',
                                    flight_number: flightNo ? flightNo.innerText.trim() : ''
                                });
                            }
                        }
                    }
                } catch (e) {
                    // 忽略解析错误
                }
            });
            
            return flights;
        ''')
        
        # 转换为标准格式
        for item in data:
            flight_data = {
                "flight_date": date,
                "departure_time": item.get("departure_time", ""),
                "arrival_time": "",
                "airline": item.get("airline", ""),
                "flight_number": item.get("flight_number", ""),
                "price": item.get("price", 0),
                "crawl_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "crawl_date": datetime.now().strftime("%Y-%m-%d")
            }
            flights.append(flight_data)
        
        # 如果没有找到航班，尝试其他方法
        if not flights:
            flights = extract_with_alternative_methods(driver, date)
        
    except Exception as e:
        print(f"提取航班信息失败: {str(e)}")
    
    return flights

def extract_with_alternative_methods(driver, date):
    """使用其他方法提取航班信息"""
    flights = []
    
    try:
        # 尝试查找页面中的价格数据
        page_source = driver.page_source
        
        # 查找所有价格模式 (¥数字 或 ￥数字)
        price_patterns = re.findall(r'[¥￥](\d[\d,]*)', page_source)
        
        for price_str in price_patterns:
            try:
                price = int(price_str.replace(',', ''))
                if price > 100 and price < 50000:  # 合理的价格范围
                    flight_data = {
                        "flight_date": date,
                        "departure_time": "",
                        "arrival_time": "",
                        "airline": "",
                        "flight_number": "",
                        "price": price,
                        "crawl_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "crawl_date": datetime.now().strftime("%Y-%m-%d")
                    }
                    flights.append(flight_data)
            except:
                pass
        
    except Exception as e:
        print(f"替代方法提取失败: {str(e)}")
    
    return flights

def save_to_database(flights):
    """保存到数据库"""
    import sqlite3
    
    db_path = "data/flights.db"
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 创建表（如果不存在）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS flight_prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            flight_date TEXT NOT NULL,
            departure_time TEXT,
            arrival_time TEXT,
            airline TEXT,
            flight_number TEXT,
            price REAL,
            crawl_time TEXT,
            crawl_date TEXT
        )
    ''')
    
    # 插入数据
    for flight in flights:
        cursor.execute('''
            INSERT INTO flight_prices 
            (flight_date, departure_time, arrival_time, airline, flight_number, price, crawl_time, crawl_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            flight["flight_date"],
            flight["departure_time"],
            flight["arrival_time"],
            flight["airline"],
            flight["flight_number"],
            flight["price"],
            flight["crawl_time"],
            flight["crawl_date"]
        ))
    
    conn.commit()
    conn.close()
    
    print(f"已保存 {len(flights)} 条记录到数据库")

def generate_html_report():
    """生成HTML报告"""
    import sqlite3
    from jinja2 import Environment, FileSystemLoader
    
    db_path = "data/flights.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 获取每日最低价
    cursor.execute('''
        SELECT flight_date, MIN(price) as min_price
        FROM flight_prices
        WHERE price > 0
        GROUP BY flight_date
        ORDER BY flight_date
    ''')
    
    daily_min = cursor.fetchall()
    conn.close()
    
    # 准备数据
    dates = [row[0] for row in daily_min]
    prices = [row[1] for row in daily_min]
    
    # 生成HTML
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>杭州直飞河内机票价格监控</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1000px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; text-align: center; }}
        .chart-container {{ margin: 30px 0; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #4facfe; color: white; }}
        .price {{ color: #e74c3c; font-weight: bold; }}
        .min-price {{ background: #d4edda; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>杭州直飞河内机票价格监控</h1>
        <p style="text-align: center; color: #666;">数据更新时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        
        <div class="chart-container">
            <canvas id="priceChart"></canvas>
        </div>
        
        <h2>每日最低价格</h2>
        <table>
            <thead>
                <tr>
                    <th>日期</th>
                    <th>最低价格</th>
                </tr>
            </thead>
            <tbody>
'''
    
    min_price = min(prices) if prices else 0
    for date, price in zip(dates, prices):
        row_class = ' class="min-price"' if price == min_price else ''
        html += f'                <tr{row_class}><td>{date}</td><td class="price">¥{price}</td></tr>\n'
    
    html += f'''            </tbody>
        </table>
    </div>
    
    <script>
        const ctx = document.getElementById('priceChart').getContext('2d');
        new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: {dates},
                datasets: [{{
                    label: '每日最低价格 (¥)',
                    data: {prices},
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    fill: true,
                    tension: 0.4
                }}]
            }},
            options: {{
                responsive: true,
                scales: {{
                    y: {{ beginAtZero: false }}
                }}
            }}
        }});
    </script>
</body>
</html>'''
    
    # 保存HTML文件
    os.makedirs("output", exist_ok=True)
    with open("output/flight_prices.html", "w", encoding="utf-8") as f:
        f.write(html)
    
    print("HTML报告已生成")

def send_email_notification(flights):
    """发送邮件通知"""
    if not EMAIL_SENDER or not EMAIL_PASSWORD:
        print("邮件配置未设置，跳过发送")
        return
    
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    
    # 找出最低价
    if not flights:
        return
    
    min_flight = min(flights, key=lambda x: x.get("price", float('inf')))
    min_price = min_flight.get("price", 0)
    
    # 创建邮件
    msg = MIMEMultipart()
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER
    msg['Subject'] = f"机票价格监控 - 最低价: ¥{min_price}"
    
    body = f"""
    杭州直飞河内机票价格监控报告
    
    抓取时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    
    本次抓取结果:
    - 总航班数: {len(flights)}
    - 最低价格: ¥{min_price}
    - 最低价格航班: {min_flight.get('airline', '未知')} {min_flight.get('flight_number', '未知')}
    
    详情请查看网页报告。
    """
    
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    
    try:
        server = smtplib.SMTP_SSL('smtp.qq.com', 465)
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print("邮件通知已发送")
    except Exception as e:
        print(f"发送邮件失败: {str(e)}")

def main():
    """主函数"""
    print(f"开始抓取任务 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 监控日期
    monitor_dates = [
        "2026-10-30",
        "2026-11-06",
        "2026-11-13",
        "2026-11-20",
        "2026-11-27"
    ]
    
    all_flights = []
    
    try:
        # 启动浏览器
        print("正在启动浏览器...")
        driver = setup_driver()
        print("浏览器启动成功")
        
        # 抓取每个日期的航班
        for date in monitor_dates:
            flights = scrape_flight_prices(driver, date)
            all_flights.extend(flights)
        
        # 关闭浏览器
        driver.quit()
        
    except Exception as e:
        print(f"浏览器操作失败: {str(e)}")
        print("尝试使用简单方法抓取...")
        
        # 备用方案：使用requests
        for date in monitor_dates:
            flights = scrape_with_requests(date)
            all_flights.extend(flights)
    
    if all_flights:
        # 保存到数据库
        save_to_database(all_flights)
        
        # 生成HTML报告
        generate_html_report()
        
        # 发送邮件通知
        send_email_notification(all_flights)
        
        print(f"任务完成，共抓取 {len(all_flights)} 条航班信息")
    else:
        print("未抓取到任何航班信息")

def scrape_with_requests(date):
    """使用requests抓取（备用方案）"""
    import requests
    
    url = f"https://flights.ctrip.com/online/list/oneway-hgh-han?depdate={date}&cabin=Y_S_C_F&adult=1&child=0&infant=0"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        # 携程有反爬虫机制，这里可能拿不到数据
        print(f"requests抓取 {date}: 状态码 {response.status_code}")
    except Exception as e:
        print(f"requests抓取失败: {str(e)}")
    
    return []

if __name__ == "__main__":
    main()