#!/bin/bash
# 推送代码到GitHub的脚本

echo "=== 推送代码到GitHub ==="
echo ""
echo "请按以下步骤操作："
echo ""
echo "1. 打开浏览器访问: https://github.com/settings/tokens/new"
echo "2. 填写信息："
echo "   - Note: flight-monitor"
echo "   - Expiration: 90 days"
echo "   - 勾选: repo"
echo "3. 点击 'Generate token'"
echo "4. 复制生成的Token"
echo ""

read -p "请粘贴您的GitHub Token: " GITHUB_TOKEN

if [ -z "$GITHUB_TOKEN" ]; then
    echo "错误: Token不能为空"
    exit 1
fi

echo ""
echo "正在配置..."

# 设置远程仓库地址
git remote set-url origin "https://$GITHUB_TOKEN@github.com/Growl7/flight-price-monitor.git"

# 推送代码
echo "正在推送代码..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "=== 推送成功！==="
    echo ""
    echo "接下来请："
    echo "1. 访问 https://github.com/Growl7/flight-price-monitor"
    echo "2. 点击 Settings → Secrets and variables → Actions"
    echo "3. 添加以下Secrets："
    echo "   - EMAIL_SENDER: 602388619@qq.com"
    echo "   - EMAIL_PASSWORD: ggtgvprniytebddf"
    echo "   - EMAIL_RECEIVER: 602388619@qq.com"
    echo "4. 点击 Actions 标签，启用工作流"
else
    echo ""
    echo "推送失败，请检查Token是否正确"
fi