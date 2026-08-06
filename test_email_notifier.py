from email_notifier import EmailNotifier

def test_email_notifier():
    """测试邮件通知模块"""
    print("测试邮件通知模块...")
    
    notifier = EmailNotifier()
    
    # 发送测试邮件
    success = notifier.send_notification()
    
    if success:
        print("✓ 邮件发送成功")
    else:
        print("✗ 邮件发送失败")
    
    print("邮件通知模块测试完成！")

if __name__ == "__main__":
    test_email_notifier()