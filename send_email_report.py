import os
import smtplib
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
    report_path = "output/flight_schedules.html"
    if os.path.exists(report_path):
        with open(report_path, 'r', encoding='utf-8') as f:
            return f.read()
    return None

def send_email():
    """发送邮件"""
    if not EMAIL_SENDER or not EMAIL_PASSWORD:
        print("邮件配置未设置，跳过发送")
        return False
    
    # 读取报告
    html_content = read_html_report()
    if not html_content:
        print("未找到报告文件")
        return False
    
    # 创建邮件
    msg = MIMEMultipart()
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER
    msg['Subject'] = f"杭州-河内航班监控报告 - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    
    # 邮件正文
    body = f"""
杭州直飞河内航班监控报告

更新时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

请查看附件中的详细报告。

---
此邮件由GitHub Actions自动发送
"""
    
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