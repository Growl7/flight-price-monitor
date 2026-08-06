# 杭州直飞河内机票价格监控系统

这是一个用于监控杭州直飞河内机票价格的自动化系统。系统会定期抓取携程网站上的机票价格数据，并生成可视化报告。

## 功能特点

- 自动抓取携程网站上的机票价格
- 存储历史价格数据到SQLite数据库
- 生成静态HTML页面展示价格趋势
- 发送邮件通知每日最低价信息
- 支持定时任务自动运行

## 系统要求

- Python 3.8+
- 现代浏览器（Chrome、Firefox等）
- 网络连接

## 安装步骤

1. 克隆或下载此项目
2. 安装依赖包：
   ```bash
   pip install -r requirements.txt
   ```
3. 安装Playwright浏览器：
   ```bash
   playwright install
   ```

## 配置说明

编辑 `config.py` 文件进行配置：

### 邮箱配置
```python
EMAIL_CONFIG = {
    "sender": "your_email@qq.com",
    "receiver": "your_email@qq.com",
    "smtp_server": "smtp.qq.com",
    "smtp_port": 465,
    "password": "your_smtp_authorization_code"
}
```

### 航班配置
```python
FLIGHT_CONFIG = {
    "departure": "HGH",  # 杭州萧山国际机场
    "arrival": "HAN",    # 河内内排国际机场
    "departure_city": "杭州",
    "arrival_city": "河内"
}
```

### 监控日期
```python
MONITOR_DATES = [
    "2026-10-30",
    "2026-11-06",
    "2026-11-13",
    "2026-11-20",
    "2026-11-27"
]
```

## 使用方法

### 1. 启动定时监控
```bash
python main.py
```
选择选项1，系统将每小时自动抓取数据并更新网页。

### 2. 运行单次抓取
```bash
python main.py
```
选择选项2，可以抓取指定日期或所有监控日期的数据。

### 3. 生成网页报告
```bash
python main.py
```
选择选项3，生成静态HTML页面和JSON数据文件。

### 4. 发送邮件通知
```bash
python main.py
```
选择选项4，手动发送邮件通知。

## 文件结构

```
机票价格监控/
├── config.py           # 配置文件
├── database.py         # 数据库操作模块
├── scraper.py          # 网页抓取模块
├── web_generator.py    # 网页生成模块
├── email_notifier.py   # 邮件通知模块
├── main.py             # 主程序
├── requirements.txt    # 依赖包列表
├── README.md           # 说明文档
├── data/               # 数据目录
│   ├── flights.db      # SQLite数据库
│   └── app.log         # 日志文件
├── templates/          # HTML模板目录
│   └── flight_template.html
└── output/             # 输出目录
    ├── flight_prices.html  # 生成的HTML页面
    └── flight_data.json    # 生成的JSON数据
```

## 输出文件

### HTML页面
生成的 `output/flight_prices.html` 文件可以在浏览器中直接打开，包含：
- 每日最低价格趋势图
- 价格统计摘要
- 详细航班数据表格

### JSON数据
生成的 `output/flight_data.json` 文件包含所有价格数据，可供其他程序使用。

### 邮件通知
系统会自动发送包含以下内容的邮件：
- 监控摘要
- 每日最低价格详情
- 整体最低价统计

## 注意事项

1. **反爬虫机制**：携程网站有反爬虫机制，如果抓取失败，请稍后重试或调整抓取频率。

2. **网络要求**：需要稳定的网络连接才能正常访问携程网站。

3. **浏览器要求**：Playwright需要安装浏览器，首次运行时会自动下载。

4. **邮箱配置**：QQ邮箱需要开启SMTP服务并获取授权码。

5. **运行时间**：定时任务模式下需要保持程序运行，建议在服务器上部署。

## 故障排除

### 抓取失败
- 检查网络连接
- 确认携程网站是否可访问
- 查看日志文件 `data/app.log`

### 邮件发送失败
- 检查邮箱配置是否正确
- 确认SMTP授权码是否有效
- 检查网络连接

### 网页生成失败
- 确认 `templates` 目录存在
- 检查模板文件是否完整
- 查看错误日志

## 扩展功能

可以通过修改代码添加以下功能：
- 支持更多航空公司
- 添加价格提醒功能
- 支持多条航线监控
- 添加数据导出功能
- 集成其他通知方式（微信、Telegram等）

## 许可证

MIT License