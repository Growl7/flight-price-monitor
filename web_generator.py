import os
import json
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from database import Database
from config import WEB_CONFIG, MONITOR_DATES, FLIGHT_CONFIG

class WebGenerator:
    def __init__(self):
        self.db = Database()
        self.output_dir = WEB_CONFIG["output_dir"]
        self.template_dir = WEB_CONFIG["template_dir"]
        
        # 确保输出目录存在
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_html(self):
        """生成HTML页面"""
        print("正在生成网页...")
        
        # 获取所有日期的汇总数据
        summaries = self.db.get_all_summaries()
        
        # 准备图表数据
        chart_data = self.prepare_chart_data(summaries)
        
        # 生成详细的航班数据
        detailed_data = self.generate_detailed_data()
        
        # 渲染HTML模板
        html_content = self.render_template(chart_data, detailed_data)
        
        # 保存HTML文件
        output_file = os.path.join(self.output_dir, "flight_prices.html")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        print(f"网页已生成: {output_file}")
        return output_file
    
    def prepare_chart_data(self, summaries):
        """准备图表数据"""
        dates = []
        prices = []
        min_price_times = []
        
        for summary in summaries:
            flight_date, min_price, min_price_time, flight_number = summary
            dates.append(flight_date)
            prices.append(min_price)
            min_price_times.append(min_price_time if min_price_time else "")
        
        return {
            "dates": dates,
            "prices": prices,
            "min_price_times": min_price_times
        }
    
    def generate_detailed_data(self):
        """生成详细数据"""
        detailed_data = []
        
        for date in MONITOR_DATES:
            # 获取该日期的价格历史
            history = self.db.get_price_history(date)
            
            # 获取最低价信息
            min_price_info = self.db.get_daily_min_price(date)
            
            detailed_data.append({
                "date": date,
                "history": history,
                "min_price_info": min_price_info
            })
        
        return detailed_data
    
    def prepare_time_analysis_data(self):
        """准备时间段分析数据"""
        # 获取最佳购买时间分析
        best_time_data = self.db.get_best_time_to_buy()
        
        # 获取按小时的价格趋势
        hourly_trend = self.db.get_price_trend_by_hour()
        
        # 获取每个日期的最佳时间
        daily_best_times = []
        for date in MONITOR_DATES:
            daily_best = self.db.get_best_time_to_buy(date)
            if daily_best:
                daily_best_times.append({
                    "date": date,
                    "best_hour": daily_best["best_hour"],
                    "best_min_price": daily_best["best_min_price"],
                    "best_period": daily_best["best_period"]
                })
        
        return {
            "best_time_data": best_time_data,
            "hourly_trend": hourly_trend,
            "daily_best_times": daily_best_times
        }
    
    def render_template(self, chart_data, detailed_data):
        """渲染HTML模板"""
        # 创建Jinja2环境
        env = Environment(loader=FileSystemLoader(self.template_dir))
        
        # 加载模板
        template = env.get_template("flight_template.html")
        
        # 准备时间段分析数据
        time_analysis = self.prepare_time_analysis_data()
        
        # 准备模板数据
        template_data = {
            "title": f"杭州直飞河内机票价格监控",
            "departure_city": FLIGHT_CONFIG["departure_city"],
            "arrival_city": FLIGHT_CONFIG["arrival_city"],
            "chart_data": chart_data,
            "detailed_data": detailed_data,
            "time_analysis": time_analysis,
            "generated_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "monitor_dates": MONITOR_DATES
        }
        
        # 渲染模板
        return template.render(**template_data)
    
    def generate_json_data(self):
        """生成JSON数据文件"""
        summaries = self.db.get_all_summaries()
        chart_data = self.prepare_chart_data(summaries)
        detailed_data = self.generate_detailed_data()
        
        json_data = {
            "chart_data": chart_data,
            "detailed_data": detailed_data,
            "generated_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        output_file = os.path.join(self.output_dir, "flight_data.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        
        print(f"JSON数据已生成: {output_file}")
        return output_file

if __name__ == "__main__":
    generator = WebGenerator()
    generator.generate_html()
    generator.generate_json_data()