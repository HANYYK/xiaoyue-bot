# XiaoYue - WeCom AI Girlfriend Bot

AI girlfriend bot via WeCom (企业微信) official API. Zero ban risk.

## Quick Start

```bash
# 1. Install
pip install -r requirements.txt

# 2. Configure
cp .env.example .env
# Fill in DEEPSEEK_API_KEY + WeCom settings

# 3. Run
python main.py
```

## WeCom Setup (one-time, ~5 min)

1. Go to https://work.weixin.qq.com/ → Register free
2. App Management → Create App
3. Note: Corp ID, Agent ID, Secret
4. Set Callback URL: `https://your-domain/callback`
5. Generate Token + AES Key (random strings)
6. Fill all into `.env`

## Deploy to Railway

1. Push to GitHub
2. Railway → New → Deploy from GitHub
3. Add env vars from `.env`
4. Done! Update WeCom callback URL to Railway domain

## Commands (send to bot)

- `#清除` - Clear conversation memory
- `#帮助` - Show help
- `#状态` - Bot status

## Features

- Girlfriend persona with 7 rotating moods
- Human-like reply delays
- Session persistence
- Anti-ban behavior simulation
- 24/7 cloud deployment ready
