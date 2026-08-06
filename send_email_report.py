import os
import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime

# 从环境变量获取配置
EMAIL_SENDER = os.environ.get('EMAIL_SENDER', '')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD', '')
EMAIL_RECEIVER = os.environ.get('EMAIL_RECEIVER', '')

def read_html_report():
    """读取HTML报告"""
    possible_paths = [
        "output/flight_prices.html",
        "output/flight_schedules.html",
        "output/flight_report.html"
    ]
    
    for report_path in possible_paths:
        if os.path.exists(report_path):
            with open(report_path, 'r', encoding='utf-8') as f:
                return f.read()
    return None

def read_flight_data():
    """读取航班数据"""
    data_path = "output/flight_prices.json"
    if os.path.exists(data_path):
        with open(data_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def send_email():
    """发送邮件"""
    if not EMAIL_SENDER or not EMAIL_PASSWORD:
        print("邮件配置未设置，跳过发送")
        return False
    
    # 读取报告
    html_content = read_html_report()
    flight_data = read_flight_data()
    
    # 创建邮件
    msg = MIMEMultipart()
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER
    msg['Subject'] = f"CA707杭州-河内直飞航班监控报告 - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    
    # 构建邮件正文
    body_lines = [
        "CA707杭州直飞河内航班监控报告",
        "=" * 60,
        f"更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "航班信息:",
        "-" * 60,
        "航班号: CA707",
        "航空公司: Air China (中国国航)",
        "航线: 杭州 (HGH) → 河内 (HAN)",
        "飞行时长: 约3小时25分钟",
        "航班类型: 直飞",
        "",
        "监控日期及价格:",
        "-" * 60
    ]
    
    if flight_data and 'results' in flight_data:
        exchange_rate = flight_data.get('exchange_rate', 7.25)
        body_lines.append(f"汇率: 1 USD = {exchange_rate} CNY")
        body_lines.append("")
        
        for result in flight_data['results']:
            if result['status'] == 'success':
                flight = result.get('flight', {})
                date = result['date']
                if flight:
                    body_lines.append(f"📅 {date}")
                    body_lines.append(f"   价格: ¥{flight.get('price_cny', 0):.0f} (${flight.get('price_usd', 0)} USD)")
                    body_lines.append(f"   航班: {flight.get('flight_no', 'CA707')}")
                    body_lines.append(f"   航空公司: {flight.get('airline', 'Air China')}")
                    body_lines.append(f"   飞行时长: {flight.get('duration', '3小时25分钟')}")
                    body_lines.append("")
                else:
                    body_lines.append(f"📅 {date}: 未找到CA707航班")
                    body_lines.append("")
            else:
                body_lines.append(f"📅 {result.get('date', '未知')}: 查询失败")
                body_lines.append("")
    else:
        body_lines.append("暂无价格数据")
    
    body_lines.extend([
        "=" * 60,
        "价格趋势:",
        "-" * 60,
        "监控所有周五的航班价格，帮助您选择最佳购票时机。",
        "",
        "请查看附件中的详细HTML报告（含价格曲线图）。",
        "",
        "---",
        "此邮件由GitHub Actions自动发送"
    ])
    
    body = "\n".join(body_lines)
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    
    # 附加HTML报告
    if html_content:
        attachment = MIMEBase('text', 'html')
        attachment.set_payload(html_content.encode('utf-8'))
        encoders.encode_base64(attachment)
        attachment.add_header('Content-Disposition', 'attachment', 
                            filename=f'flight_report_{datetime.now().strftime("%Y%m%d")}.html')
        msg.attach(attachment)
    
    # 发送邮件
    try:
        server = smtplib.SMTP_SSL('smtp.qq.com', 465)
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"邮件已发送至: {EMAIL_RECEIVER}")
        return True
    except Exception as e:
        print(f"发送邮件失败: {str(e)}")
        return False

if __name__ == "__main__":
    print(f"正在发送邮件报告 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    send_email()
