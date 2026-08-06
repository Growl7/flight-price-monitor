# GitHub Actions 配置指南

## 步骤1: 创建GitHub仓库

1. 登录 GitHub (https://github.com)
2. 点击右上角 "+" → "New repository"
3. 仓库名称: `flight-price-monitor`
4. 选择 "Public"（免费）
5. 点击 "Create repository"

## 步骤2: 上传代码到GitHub

在终端中运行以下命令：

```bash
cd /Users/z11/Desktop/ai_manager/机票价格监控

# 初始化Git仓库
git init
git add .
git commit -m "初始化机票价格监控系统"

# 添加远程仓库（替换为您的GitHub用户名）
git remote add origin https://github.com/YOUR_USERNAME/flight-price-monitor.git

# 推送代码
git branch -M main
git push -u origin main
```

## 步骤3: 设置GitHub Secrets（重要！）

1. 在GitHub仓库页面，点击 "Settings"
2. 左侧菜单选择 "Secrets and variables" → "Actions"
3. 点击 "New repository secret"
4. 添加以下三个Secrets：

| Name | Value | 说明 |
|------|-------|------|
| `EMAIL_SENDER` | 602388619@qq.com | 发送邮箱 |
| `EMAIL_PASSWORD` | ggtgvprniytebddf | QQ邮箱授权码 |
| `EMAIL_RECEIVER` | 602388619@qq.com | 接收邮箱 |

## 步骤4: 启用GitHub Pages（可选，用于查看网页）

1. 在仓库页面，点击 "Settings"
2. 左侧菜单选择 "Pages"
3. Source 选择 "Deploy from a branch"
4. Branch 选择 "main" 和 "/ (root)"
5. 点击 "Save"

## 步骤5: 启用Actions

1. 在仓库页面，点击 "Actions" 标签
2. 如果看到提示，点击 "I understand my workflows, go ahead and enable them"
3. 系统会自动开始运行

## 步骤6: 手动测试运行

1. 点击 "Actions" 标签
2. 选择 "机票价格监控" 工作流
3. 点击 "Run workflow"
4. 等待运行完成

## 查看运行结果

### 查看网页报告
访问: `https://YOUR_USERNAME.github.io/flight-price-monitor/output/flight_prices.html`

### 查看运行日志
1. 点击 "Actions" 标签
2. 点击最新的运行记录
3. 展开 "scrape" 步骤查看详细日志

### 下载报告文件
1. 点击最新的运行记录
2. 在 "Artifacts" 部分下载报告文件

## 自定义监控日期

编辑 `scraper_github.py` 文件中的 `monitor_dates` 变量：

```python
monitor_dates = [
    "2026-10-30",
    "2026-11-06",
    "2026-11-13",
    "2026-11-20",
    "2026-11-27"
]
```

## 修改运行频率

编辑 `.github/workflows/monitor.yml` 文件中的 cron 表达式：

```yaml
schedule:
  # 每小时运行一次
  - cron: '0 * * * *'
  
  # 其他频率示例：
  # 每6小时运行一次: '0 */6 * * *'
  # 每天运行一次: '0 8 * * *' (每天8点)
  # 每周一运行: '0 8 * * 1'
```

## 常见问题

### Q: 为什么没有抓取到数据？
A: 携程网站有反爬虫机制，可能需要：
- 增加等待时间
- 使用代理IP
- 尝试不同的User-Agent

### Q: 邮件没有收到？
A: 检查：
- QQ邮箱授权码是否正确
- 是否开启了SMTP服务
- 垃圾邮件文件夹

### Q: GitHub Actions运行失败？
A: 检查：
- Secrets是否正确设置
- 查看运行日志中的错误信息

### Q: 如何停止定时任务？
A: 在Actions页面，点击工作流，选择 "Disable workflow"

## 免费额度说明

GitHub Actions 每月提供 2000 分钟免费运行时间：
- 每小时运行一次 = 24次/天 × 30天 = 720次/月
- 每次运行约2-5分钟
- 总计约 1440-3600 分钟/月

对于公开仓库，额度是无限的！