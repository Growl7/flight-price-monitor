import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from datetime import datetime
from database import Database
from config import EMAIL_CONFIG, FLIGHT_CONFIG, MONITOR_DATES

class EmailNotifier:
    def __init__(self):
        self.db = Database()
        self.email_config = EMAIL_CONFIG
        self.flight_config = FLIGHT_CONFIG
    
    def send_notification(self):
        """发送通知邮件"""
        print("正在准备发送通知邮件...")
        
        # 获取邮件内容
        subject, body = self.generate_email_content()
        
        # 发送邮件
        try:
            self.send_email(subject, body)
            print("通知邮件发送成功")
            return True
        except Exception as e:
            print(f"发送邮件失败: {str(e)}")
            return False
    
    def generate_email_content(self):
        """生成邮件内容"""
        today = datetime.now().strftime("%Y-%m-%d")
        subject = f"杭州直飞河内机票价格监控报告 - {today}"
        
        # 获取所有日期的汇总数据
        summaries = self.db.get_all_summaries()
        
        # 生成邮件正文
        body = self.generate_email_body(summaries)
        
        return subject, body
    
    def generate_email_body(self, summaries):
        """生成邮件正文"""
        departure_city = self.flight_config["departure_city"]
        arrival_city = self.flight_config["arrival_city"]
        
        # 获取时间段分析数据
        best_time_data = self.db.get_best_time_to_buy()
        
        # 邮件头部
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .summary {{ background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .summary h2 {{ color: #667eea; margin-bottom: 15px; border-bottom: 2px solid #667eea; padding-bottom: 10px; }}
                .price-highlight {{ color: #e74c3c; font-weight: bold; font-size: 1.2em; }}
                .date-card {{ background: white; padding: 15px; border-radius: 8px; margin-bottom: 15px; border-left: 4px solid #4facfe; }}
                .date-header {{ font-weight: bold; color: #4facfe; margin-bottom: 10px; }}
                .flight-info {{ margin: 5px 0; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 0.9em; }}
                .no-data {{ color: #999; font-style: italic; }}
                .time-analysis {{ background: linear-gradient(135deg, #00b09b, #96c93d); color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
                .time-analysis h2 {{ color: white; border-bottom-color: rgba(255,255,255,0.5); }}
                .time-stat {{ background: rgba(255,255,255,0.2); padding: 10px; border-radius: 5px; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>杭州直飞河内机票价格监控报告</h1>
                    <p>{departure_city} → {arrival_city}</p>
                    <p>报告生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
                </div>
                
                <div class="content">
                    <div class="summary">
                        <h2>监控摘要</h2>
                        <p>监控日期范围: {MONITOR_DATES[0]} 至 {MONITOR_DATES[-1]}</p>
                        <p>监控天数: {len(summaries)} 天</p>
                    </div>
        """
        
        # 添加最佳购买时间分析
        if best_time_data:
            html += f"""
                    <div class="time-analysis">
                        <h2>最佳购买时间分析</h2>
                        <div class="time-stat">
                            <strong>最佳购买时间段:</strong> {best_time_data['best_period']}
                        </div>
                        <div class="time-stat">
                            <strong>最佳购买小时:</strong> {f"{best_time_data['best_hour']:02d}:00" if best_time_data['best_hour'] is not None else 'N/A'}
                        </div>
                        <div class="time-stat">
                            <strong>该时段最低价:</strong> ¥{best_time_data['best_min_price']}
                        </div>
                    </div>
            """
            
            # 添加各时间段统计
            if best_time_data.get('period_stats'):
                html += '<div class="summary"><h2>各时间段价格统计</h2>'
                html += '<table style="width: 100%; border-collapse: collapse; margin-top: 10px;">'
                html += '<tr style="background: #667eea; color: white;"><th style="padding: 10px; text-align: left;">时间段</th><th style="padding: 10px; text-align: left;">最低价</th><th style="padding: 10px; text-align: left;">平均价</th></tr>'
                
                for period, stats in best_time_data['period_stats'].items():
                    html += f"""
                    <tr style="border-bottom: 1px solid #eee;">
                        <td style="padding: 10px;"><strong>{period}</strong></td>
                        <td style="padding: 10px;" class="price-highlight">¥{stats['min_price']}</td>
                        <td style="padding: 10px;">¥{stats['avg_price']:.2f}</td>
                    </tr>
                    """
                
                html += '</table></div>'
        
        # 添加每个日期的详细信息
        if summaries:
            html += '<div class="summary"><h2>每日最低价格详情</h2>'
            
            min_price_overall = float('inf')
            min_price_date = ""
            
            for summary in summaries:
                flight_date, min_price, min_price_time, flight_number = summary
                
                # 更新整体最低价
                if min_price and min_price < min_price_overall:
                    min_price_overall = min_price
                    min_price_date = flight_date
                
                html += f"""
                <div class="date-card">
                    <div class="date-header">{flight_date}</div>
                    <div class="flight-info">
                        <strong>最低价格:</strong> <span class="price-highlight">¥{min_price}</span>
                    </div>
                """
                
                if min_price_time:
                    html += f"""
                    <div class="flight-info">
                        <strong>出现时间:</strong> {min_price_time}
                    </div>
                    """
                
                if flight_number:
                    html += f"""
                    <div class="flight-info">
                        <strong>航班号:</strong> {flight_number}
                    </div>
                    """
                
                html += '</div>'
            
            html += '</div>'
            
            # 添加整体最低价摘要
            if min_price_overall != float('inf'):
                html += f"""
                <div class="summary">
                    <h2>整体最低价</h2>
                    <p>在所有监控日期中，最低价格为 <span class="price-highlight">¥{min_price_overall}</span></p>
                    <p>出现日期: {min_price_date}</p>
                </div>
                """
        else:
            html += '<div class="summary"><h2>暂无数据</h2><p class="no-data">目前还没有收集到足够的数据。</p></div>'
        
        # 邮件尾部
        html += """
                </div>
                
                <div class="footer">
                    <p>此邮件由杭州直飞河内机票价格监控系统自动发送</p>
                    <p>如有问题，请联系系统管理员</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def send_email(self, subject, body):
        """发送邮件"""
        msg = MIMEMultipart()
        msg['From'] = self.email_config["sender"]
        msg['To'] = self.email_config["receiver"]
        msg['Subject'] = subject
        
        # 添加正文
        msg.attach(MIMEText(body, 'html', 'utf-8'))
        
        # 连接SMTP服务器
        server = smtplib.SMTP_SSL(self.email_config["smtp_server"], self.email_config["smtp_port"])
        server.login(self.email_config["sender"], self.email_config["password"])
        
        # 发送邮件
        server.send_message(msg)
        server.quit()
    
    def send_daily_report(self):
        """发送每日报告"""
        print(f"发送每日报告 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        return self.send_notification()

if __name__ == "__main__":
    notifier = EmailNotifier()
    notifier.send_daily_report()