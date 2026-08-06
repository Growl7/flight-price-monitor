import sys
import os

def test_system():
    """测试系统完整性"""
    print("测试系统完整性...")
    
    # 检查必要的文件
    required_files = [
        "config.py",
        "database.py",
        "scraper.py",
        "web_generator.py",
        "email_notifier.py",
        "main.py",
        "requirements.txt",
        "README.md"
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✓ {file} 存在")
        else:
            print(f"✗ {file} 不存在")
            return False
    
    # 检查目录
    required_dirs = ["data", "templates", "output"]
    for dir_name in required_dirs:
        if os.path.exists(dir_name):
            print(f"✓ {dir_name}/ 目录存在")
        else:
            print(f"✗ {dir_name}/ 目录不存在")
            return False
    
    # 检查模板文件
    template_file = "templates/flight_template.html"
    if os.path.exists(template_file):
        print(f"✓ {template_file} 存在")
    else:
        print(f"✗ {template_file} 不存在")
        return False
    
    print("系统完整性测试通过！")
    return True

if __name__ == "__main__":
    success = test_system()
    sys.exit(0 if success else 1)