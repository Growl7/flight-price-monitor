import time
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from database import Database
from config import FLIGHT_CONFIG, MONITOR_DATES

class FlightScraper:
    def __init__(self):
        self.db = Database()
        self.flight_config = FLIGHT_CONFIG
    
    def generate_url(self, date):
        """生成携程机票搜索URL"""
        departure = self.flight_config["departure"]
        arrival = self.flight_config["arrival"]
        
        # 携程机票搜索URL格式
        url = f"https://flights.ctrip.com/online/list/oneway-{departure.lower()}-{arrival.lower()}?depdate={date}&cabin=Y_S_C_F&adult=1&child=0&infant=0"
        return url
    
    def setup_driver(self):
        """设置Chrome驱动"""
        options = Options()
        options.add_argument('--headless')  # 无头模式
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # 使用Selenium Manager自动管理ChromeDriver
        try:
            driver = webdriver.Chrome(options=options)
            return driver
        except Exception as e:
            print(f"Chrome浏览器启动失败: {str(e)}")
            raise
    
    def scrape_flight_prices(self, date):
        """抓取指定日期的航班价格"""
        url = self.generate_url(date)
        print(f"正在抓取日期 {date} 的航班价格...")
        print(f"URL: {url}")
        
        driver = self.setup_driver()
        
        try:
            # 访问页面
            driver.get(url)
            
            # 等待页面加载
            time.sleep(5)
            
            # 尝试获取航班信息
            flights = self.extract_flight_info(driver, date)
            
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
        finally:
            driver.quit()
    
    def extract_flight_info(self, driver, date):
        """从页面提取航班信息"""
        flights = []
        
        try:
            # 等待航班列表加载
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".flight-item, .flight-item-v2, [class*='flight']"))
            )
            
            # 尝试多种选择器
            selectors = [
                ".flight-item",
                ".flight-item-v2",
                ".flight-list-item",
                "[class*='flight']",
                ".list-item"
            ]
            
            for selector in selectors:
                try:
                    flight_items = driver.find_elements(By.CSS_SELECTOR, selector)
                    if flight_items:
                        print(f"使用选择器 {selector} 找到 {len(flight_items)} 个航班")
                        for item in flight_items:
                            try:
                                flight_data = self.parse_flight_item(item, date)
                                if flight_data and flight_data.get("price", 0) > 0:
                                    flights.append(flight_data)
                            except Exception as e:
                                print(f"解析航班项失败: {str(e)}")
                                continue
                        if flights:
                            break
                except Exception:
                    continue
            
            # 如果没有找到航班，尝试使用JavaScript
            if not flights:
                flights = self.extract_with_javascript(driver, date)
            
        except Exception as e:
            print(f"提取航班信息失败: {str(e)}")
            # 尝试使用JavaScript提取
            flights = self.extract_with_javascript(driver, date)
        
        return flights
    
    def parse_flight_item(self, item, date):
        """解析单个航班项"""
        try:
            # 获取航班信息
            departure_time = self.safe_find_element(item, ".depart-time, .depart-time-text, [class*='depart']")
            arrival_time = self.safe_find_element(item, ".arrival-time, .arrival-time-text, [class*='arrival']")
            airline = self.safe_find_element(item, ".airline-name, .airline-text, [class*='airline']")
            flight_number = self.safe_find_element(item, ".flight-number, .flight-no, [class*='flight-no']")
            price = self.safe_find_element(item, ".price, .price-text, [class*='price']")
            
            departure_time_text = departure_time.text if departure_time else ""
            arrival_time_text = arrival_time.text if arrival_time else ""
            airline_text = airline.text if airline else ""
            flight_number_text = flight_number.text if flight_number else ""
            price_text = price.text if price else "0"
            
            # 清理价格文本
            price_value = re.sub(r'[^\d.]', '', price_text)
            try:
                price_value = float(price_value)
            except ValueError:
                price_value = 0
            
            return {
                "flight_date": date,
                "departure_time": departure_time_text.strip(),
                "arrival_time": arrival_time_text.strip(),
                "airline": airline_text.strip(),
                "flight_number": flight_number_text.strip(),
                "price": price_value,
                "crawl_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "crawl_date": datetime.now().strftime("%Y-%m-%d")
            }
        except Exception as e:
            print(f"解析航班项失败: {str(e)}")
            return None
    
    def safe_find_element(self, parent, selector):
        """安全查找元素"""
        try:
            elements = parent.find_elements(By.CSS_SELECTOR, selector)
            return elements[0] if elements else None
        except Exception:
            return None
    
    def extract_with_javascript(self, driver, date):
        """使用JavaScript提取航班信息"""
        try:
            # 执行JavaScript获取页面数据
            data = driver.execute_script('''
                const flights = [];
                
                // 尝试获取所有可能的价格元素
                const priceElements = document.querySelectorAll('[class*="price"], [class*="Price"]');
                priceElements.forEach(el => {
                    const priceText = el.innerText;
                    const priceMatch = priceText.match(/[\\d,]+/);
                    if (priceMatch) {
                        const price = parseInt(priceMatch[0].replace(',', ''));
                        if (price > 0) {
                            flights.push({
                                price: price,
                                text: priceText
                            });
                        }
                    }
                });
                
                return flights;
            ''')
            
            # 将提取的数据转换为标准格式
            flights = []
            for item in data:
                flight_data = {
                    "flight_date": date,
                    "departure_time": "",
                    "arrival_time": "",
                    "airline": "",
                    "flight_number": "",
                    "price": item.get("price", 0),
                    "crawl_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "crawl_date": datetime.now().strftime("%Y-%m-%d")
                }
                flights.append(flight_data)
            
            return flights
            
        except Exception as e:
            print(f"JavaScript提取失败: {str(e)}")
            return []
    
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
    scraper = FlightScraper()
    scraper.run_daily_scrape()