# GitHub认证配置指南

由于网络原因，GitHub CLI安装失败。请按以下步骤使用Personal Access Token：

## 步骤1: 生成Personal Access Token

1. 登录 https://github.com
2. 点击右上角头像 → "Settings"
3. 左侧菜单最底部 → "Developer settings"
4. 左侧菜单 → "Personal access tokens" → "Tokens (classic)"
5. 点击 "Generate new token" → "Generate new token (classic)"
6. 填写信息：
   - Note: `flight-monitor`
   - Expiration: 选择 "90 days" 或 "No expiration"
   - 勾选权限：**repo** (完整勾选)
7. 点击 "Generate token"
8. **复制生成的Token**（只显示一次！）

## 步骤2: 使用Token推送代码

在终端运行以下命令（将 `YOUR_TOKEN` 替换为上面生成的Token）：

```bash
cd /Users/z11/Desktop/ai_manager/机票价格监控

# 设置远程仓库地址（包含Token）
git remote set-url origin https://YOUR_TOKEN@github.com/Growl7/flight-price-monitor.git

# 推送代码
git push -u origin main
```

## 示例

假设Token是 `ghp_ABCDEFGHIJKLMNOP123456`，则命令为：

```bash
git remote set-url origin https://ghp_ABCDEFGHIJKLMNOP123456@github.com/Growl7/flight-price-monitor.git
git push -u origin main
```

## 注意事项

- Token只在设置URL时需要，之后Git会记住认证信息
- 不要把Token分享给别人或提交到代码仓库
- 如果Token过期，需要重新生成并更新URL