from web_generator import WebGenerator

def test_web_generator():
    """测试网页生成模块"""
    print("测试网页生成模块...")
    
    generator = WebGenerator()
    
    # 生成HTML页面
    html_file = generator.generate_html()
    print(f"✓ 生成HTML页面: {html_file}")
    
    # 生成JSON数据
    json_file = generator.generate_json_data()
    print(f"✓ 生成JSON数据: {json_file}")
    
    print("网页生成模块测试完成！")

if __name__ == "__main__":
    test_web_generator()