import sqlite3
import os
from datetime import datetime
from config import DATABASE_CONFIG

class Database:
    def __init__(self):
        self.db_path = DATABASE_CONFIG["path"]
        self.init_database()
    
    def init_database(self):
        """初始化数据库"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建航班价格表
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
        
        # 创建每日最低价汇总表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_summary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                flight_date TEXT NOT NULL,
                min_price REAL,
                min_price_time TEXT,
                min_price航班 TEXT,
                crawl_date TEXT,
                UNIQUE(flight_date, crawl_date)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_flight_price(self, flight_data):
        """保存航班价格数据"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO flight_prices 
            (flight_date, departure_time, arrival_time, airline, flight_number, price, crawl_time, crawl_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            flight_data["flight_date"],
            flight_data.get("departure_time", ""),
            flight_data.get("arrival_time", ""),
            flight_data.get("airline", ""),
            flight_data.get("flight_number", ""),
            flight_data.get("price", 0),
            flight_data.get("crawl_time", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            flight_data.get("crawl_date", datetime.now().strftime("%Y-%m-%d"))
        ))
        
        conn.commit()
        conn.close()
    
    def get_daily_min_price(self, flight_date):
        """获取某天的最低价格"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT MIN(price), departure_time, flight_number
            FROM flight_prices
            WHERE flight_date = ? AND price > 0
        ''', (flight_date,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0]:
            return {
                "min_price": result[0],
                "min_price_time": result[1],
                "flight_number": result[2]
            }
        return None
    
    def get_price_history(self, flight_date):
        """获取某天的价格历史"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT departure_time, airline, flight_number, price, crawl_time
            FROM flight_prices
            WHERE flight_date = ? AND price > 0
            ORDER BY crawl_time
        ''', (flight_date,))
        
        results = cursor.fetchall()
        conn.close()
        
        return results
    
    def update_daily_summary(self, flight_date):
        """更新每日最低价汇总"""
        min_price_data = self.get_daily_min_price(flight_date)
        if not min_price_data:
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO daily_summary 
            (flight_date, min_price, min_price_time, min_price航班, crawl_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            flight_date,
            min_price_data["min_price"],
            min_price_data["min_price_time"],
            min_price_data["flight_number"],
            datetime.now().strftime("%Y-%m-%d")
        ))
        
        conn.commit()
        conn.close()
    
    def get_all_summaries(self):
        """获取所有每日汇总"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT flight_date, min_price, min_price_time, min_price航班
            FROM daily_summary
            ORDER BY flight_date
        ''')
        
        results = cursor.fetchall()
        conn.close()
        
        return results
    
    def get_hourly_price_stats(self, flight_date=None):
        """获取按小时分组的价格统计"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if flight_date:
            # 获取特定日期的小时统计
            cursor.execute('''
                SELECT 
                    CAST(strftime('%H', crawl_time) AS INTEGER) as hour,
                    MIN(price) as min_price,
                    AVG(price) as avg_price,
                    COUNT(*) as record_count
                FROM flight_prices
                WHERE flight_date = ? AND price > 0
                GROUP BY hour
                ORDER BY hour
            ''', (flight_date,))
        else:
            # 获取所有日期的小时统计
            cursor.execute('''
                SELECT 
                    CAST(strftime('%H', crawl_time) AS INTEGER) as hour,
                    MIN(price) as min_price,
                    AVG(price) as avg_price,
                    COUNT(*) as record_count
                FROM flight_prices
                WHERE price > 0
                GROUP BY hour
                ORDER BY hour
            ''')
        
        results = cursor.fetchall()
        conn.close()
        
        return results
    
    def get_best_time_to_buy(self, flight_date=None):
        """分析最佳购买时间段"""
        hourly_stats = self.get_hourly_price_stats(flight_date)
        
        if not hourly_stats:
            return None
        
        # 找出最低价出现的时间段
        min_price_hour = None
        min_price = float('inf')
        
        for hour, min_price_val, avg_price, count in hourly_stats:
            if min_price_val < min_price:
                min_price = min_price_val
                min_price_hour = hour
        
        # 计算各时间段的平均价格
        time_periods = {
            "凌晨 (00:00-06:00)": [],
            "上午 (06:00-12:00)": [],
            "下午 (12:00-18:00)": [],
            "晚上 (18:00-24:00)": []
        }
        
        for hour, min_price_val, avg_price, count in hourly_stats:
            if 0 <= hour < 6:
                time_periods["凌晨 (00:00-06:00)"].append((hour, min_price_val, avg_price))
            elif 6 <= hour < 12:
                time_periods["上午 (06:00-12:00)"].append((hour, min_price_val, avg_price))
            elif 12 <= hour < 18:
                time_periods["下午 (12:00-18:00)"].append((hour, min_price_val, avg_price))
            else:
                time_periods["晚上 (18:00-24:00)"].append((hour, min_price_val, avg_price))
        
        # 计算每个时间段的平均最低价
        period_stats = {}
        for period, data in time_periods.items():
            if data:
                min_prices = [item[1] for item in data]
                avg_prices = [item[2] for item in data]
                period_stats[period] = {
                    "min_price": min(min_prices),
                    "avg_price": sum(avg_prices) / len(avg_prices),
                    "data_points": len(data)
                }
        
        # 找出最佳时间段
        best_period = None
        best_min_price = float('inf')
        
        for period, stats in period_stats.items():
            if stats["min_price"] < best_min_price:
                best_min_price = stats["min_price"]
                best_period = period
        
        return {
            "best_hour": min_price_hour,
            "best_min_price": min_price,
            "hourly_stats": hourly_stats,
            "period_stats": period_stats,
            "best_period": best_period
        }
    
    def get_price_trend_by_hour(self):
        """获取按小时的价格趋势（用于图表）"""
        hourly_stats = self.get_hourly_price_stats()
        
        hours = []
        min_prices = []
        avg_prices = []
        
        for hour, min_price, avg_price, count in hourly_stats:
            hours.append(f"{hour:02d}:00")
            min_prices.append(min_price)
            avg_prices.append(avg_price)
        
        return {
            "hours": hours,
            "min_prices": min_prices,
            "avg_prices": avg_prices
        }