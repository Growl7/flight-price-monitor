#!/bin/bash
# 初始化Git仓库并推送到GitHub的脚本

echo "=== 机票价格监控系统 - GitHub设置向导 ==="
echo ""

# 检查是否已安装git
if ! command -v git &> /dev/null; then
    echo "错误: 请先安装Git"
    echo "访问 https://git-scm.com/downloads 下载安装"
    exit 1
fi

# 获取GitHub用户名
read -p "请输入您的GitHub用户名: " GITHUB_USERNAME

if [ -z "$GITHUB_USERNAME" ]; then
    echo "错误: 用户名不能为空"
    exit 1
fi

echo ""
echo "正在初始化Git仓库..."

# 初始化Git仓库
git init
git add .
git commit -m "初始化机票价格监控系统"

# 添加远程仓库
git remote add origin "https://github.com/$GITHUB_USERNAME/flight-price-monitor.git"

# 推送代码
echo ""
echo "正在推送代码到GitHub..."
git branch -M main
git push -u origin main

echo ""
echo "=== 完成！==="
echo ""
echo "接下来请："
echo "1. 访问 https://github.com/$GITHUB_USERNAME/flight-price-monitor"
echo "2. 点击 Settings → Secrets and variables → Actions"
echo "3. 添加以下Secrets:"
echo "   - EMAIL_SENDER: 602388619@qq.com"
echo "   - EMAIL_PASSWORD: ggtgvprniytebddf"
echo "   - EMAIL_RECEIVER: 602388619@qq.com"
echo "4. 点击 Actions 标签，启用工作流"
echo ""
echo "详细说明请查看 GITHUB_SETUP.md"