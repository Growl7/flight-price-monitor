import os

# 邮箱配置
EMAIL_CONFIG = {
    "sender": "602388619@qq.com",
    "receiver": "602388619@qq.com",
    "smtp_server": "smtp.qq.com",
    "smtp_port": 465,
    "password": "ggtgvprniytebddf"  # QQ邮箱授权码
}

# 航班配置
FLIGHT_CONFIG = {
    "departure": "HGH",  # 杭州萧山国际机场
    "arrival": "HAN",    # 河内内排国际机场
    "departure_city": "杭州",
    "arrival_city": "河内"
}

# 监控日期范围（2026年10月30日到2026年11月的每个周五）
MONITOR_DATES = [
    "2026-10-30",
    "2026-11-06",
    "2026-11-13",
    "2026-11-20",
    "2026-11-27"
]

# 数据库配置
DATABASE_CONFIG = {
    "path": "data/flights.db"
}

# 网页配置
WEB_CONFIG = {
    "output_dir": "output",
    "template_dir": "templates"
}

# 日志配置
LOG_CONFIG = {
    "level": "INFO",
    "file": "data/app.log"
}