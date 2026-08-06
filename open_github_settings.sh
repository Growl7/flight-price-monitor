#!/bin/bash
# 打开GitHub仓库设置页面

echo "正在打开GitHub仓库设置页面..."
echo ""

# 打开浏览器
open "https://github.com/Growl7/flight-price-monitor/settings/secrets/actions"

echo ""
echo "请在打开的页面中："
echo ""
echo "1. 点击 'New repository secret'"
echo ""
echo "2. 添加第一个Secret："
echo "   Name: EMAIL_SENDER"
echo "   Value: 602388619@qq.com"
echo "   点击 'Add secret'"
echo ""
echo "3. 再次点击 'New repository secret'"
echo "   Name: EMAIL_PASSWORD"
echo "   Value: ggtgvprniytebddf"
echo "   点击 'Add secret'"
echo ""
echo "4. 再次点击 'New repository secret'"
echo "   Name: EMAIL_RECEIVER"
echo "   Value: 602388619@qq.com"
echo "   点击 'Add secret'"
echo ""
echo "完成后，点击页面上方的 'Actions' 标签"
echo "然后点击 'I understand my workflows, go ahead and enable them'"
echo ""
echo "设置完成后，系统会自动开始运行！"