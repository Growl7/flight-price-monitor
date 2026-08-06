import schedule
import time
from datetime import datetime
from scraper import FlightScraper
from web_generator import WebGenerator
from email_notifier import EmailNotifier
from config import MONITOR_DATES

class FlightMonitor:
    def __init__(self):
        self.scraper = FlightScraper()
        self.web_generator = WebGenerator()
        self.email_notifier = EmailNotifier()
    
    def run_scrape_task(self):
        """运行抓取任务"""
        print(f"开始抓取任务 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # 运行抓取
            self.scraper.run_daily_scrape()
            
            # 生成网页
            self.web_generator.generate_html()
            self.web_generator.generate_json_data()
            
            # 发送邮件通知
            self.email_notifier.send_daily_report()
            
            print(f"抓取任务完成 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
        except Exception as e:
            print(f"抓取任务失败: {str(e)}")
    
    def run_web_update_only(self):
        """仅更新网页"""
        print(f"开始更新网页 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # 生成网页
            self.web_generator.generate_html()
            self.web_generator.generate_json_data()
            
            print(f"网页更新完成 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
        except Exception as e:
            print(f"网页更新失败: {str(e)}")
    
    def start_scheduler(self):
        """启动定时任务调度器"""
        print("启动定时任务调度器...")
        print(f"监控日期: {', '.join(MONITOR_DATES)}")
        
        # 每小时运行一次抓取任务
        schedule.every(1).hours.do(self.run_scrape_task)
        
        # 每天发送一次汇总报告（晚上8点）
        schedule.every().day.at("20:00").do(self.email_notifier.send_daily_report)
        
        print("定时任务已配置:")
        print("- 每小时: 抓取航班价格并更新网页")
        print("- 每天20:00: 发送每日汇总报告")
        
        # 运行第一次任务
        self.run_scrape_task()
        
        # 开始调度循环
        while True:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次
    
    def run_single_scrape(self, date=None):
        """运行单次抓取"""
        if date:
            print(f"抓取指定日期: {date}")
            import asyncio
            asyncio.run(self.scraper.scrape_flight_prices(date))
        else:
            print("抓取所有监控日期")
            self.scraper.run_daily_scrape()
        
        # 更新网页
        self.web_generator.generate_html()
        self.web_generator.generate_json_data()
    
    def generate_report(self):
        """生成报告"""
        print("生成报告...")
        self.web_generator.generate_html()
        self.web_generator.generate_json_data()
        self.email_notifier.send_daily_report()
        print("报告生成完成")

def main():
    """主函数"""
    monitor = FlightMonitor()
    
    print("杭州直飞河内机票价格监控系统")
    print("=" * 50)
    print("1. 启动定时监控 (每小时自动运行)")
    print("2. 运行单次抓取")
    print("3. 仅生成网页报告")
    print("4. 发送邮件通知")
    print("5. 退出")
    print("=" * 50)
    
    while True:
        choice = input("请选择操作 (1-5): ").strip()
        
        if choice == '1':
            print("启动定时监控...")
            monitor.start_scheduler()
            break
        
        elif choice == '2':
            date = input("请输入要抓取的日期 (格式: YYYY-MM-DD，或留空抓取所有日期): ").strip()
            if date:
                monitor.run_single_scrape(date)
            else:
                monitor.run_single_scrape()
            print("抓取完成!")
        
        elif choice == '3':
            monitor.generate_report()
            print("报告生成完成!")
        
        elif choice == '4':
            monitor.email_notifier.send_daily_report()
            print("邮件发送完成!")
        
        elif choice == '5':
            print("退出程序")
            break
        
        else:
            print("无效选择，请重新输入")

if __name__ == "__main__":
    main()