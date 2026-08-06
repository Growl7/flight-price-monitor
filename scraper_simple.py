import requests
import re
import json
from datetime import datetime
from bs4 import BeautifulSoup
from database import Database
from config import FLIGHT_CONFIG, MONITOR_DATES

class FlightScraperSimple:
    def __init__(self):
        self.db = Database()
        self.flight_config = FLIGHT_CONFIG
        self.session = requests.Session()
        
        # 设置请求头
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })
    
    def generate_url(self, date):
        """生成携程机票搜索URL"""
        departure = self.flight_config["departure"]
        arrival = self.flight_config["arrival"]
        
        # 携程机票搜索URL格式
        url = f"https://flights.ctrip.com/online/list/oneway-{departure.lower()}-{arrival.lower()}?depdate={date}&cabin=Y_S_C_F&adult=1&child=0&infant=0"
        return url
    
    def scrape_flight_prices(self, date):
        """抓取指定日期的航班价格"""
        url = self.generate_url(date)
        print(f"正在抓取日期 {date} 的航班价格...")
        print(f"URL: {url}")
        
        try:
            # 发送请求
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # 解析页面
            flights = self.extract_flight_info(response.text, date)
            
            # 保存到数据库
            for flight in flights:
                self.db.save_flight_price(flight)
            
            # 更新每日汇总
            self.db.update_daily_summary(date)
            
            print(f"成功抓取 {len(flights)} 个航班信息")
            return flights
            
        except Exception as e:
            print(f"抓取失败: {str(e)}")
            return []
    
    def extract_flight_info(self, html_content, date):
        """从HTML内容提取航班信息"""
        flights = []
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 尝试查找航班信息
            # 携程网站可能使用JavaScript动态加载，所以可能找不到数据
            # 这里我们尝试查找可能的数据结构
            
            # 方法1: 查找所有可能的价格元素
            price_elements = soup.find_all(string=re.compile(r'¥\d+'))
            for price_elem in price_elements:
                price_match = re.search(r'¥(\d+)', price_elem)
                if price_match:
                    price = float(price_match.group(1))
                    if price > 0:
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
            
            # 方法2: 尝试查找JSON数据
            script_elements = soup.find_all('script')
            for script in script_elements:
                if script.string and 'price' in script.string.lower():
                    # 尝试提取JSON数据
                    json_match = re.search(r'\{[^}]*"price"[^}]*\}', script.string)
                    if json_match:
                        try:
                            json_data = json.loads(json_match.group())
                            if 'price' in json_data:
                                flight_data = {
                                    "flight_date": date,
                                    "departure_time": "",
                                    "arrival_time": "",
                                    "airline": "",
                                    "flight_number": "",
                                    "price": float(json_data['price']),
                                    "crawl_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    "crawl_date": datetime.now().strftime("%Y-%m-%d")
                                }
                                flights.append(flight_data)
                        except json.JSONDecodeError:
                            pass
            
            print(f"从HTML中提取到 {len(flights)} 个航班信息")
            
        except Exception as e:
            print(f"解析HTML失败: {str(e)}")
        
        return flights
    
    def run_daily_scrape(self):
        """运行每日抓取任务"""
        print(f"开始每日抓取任务 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        for date in MONITOR_DATES:
            try:
                self.scrape_flight_prices(date)
            except Exception as e:
                print(f"抓取日期 {date} 失败: {str(e)}")
        
        print("每日抓取任务完成")

if __name__ == "__main__":
    scraper = FlightScraperSimple()
    scraper.run_daily_scrape()