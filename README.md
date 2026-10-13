# Telegram Bot - Railway uchun tayyor

## Qanday ishlatish

### 1. Telegram bot yaratish
1. Telegramda @BotFather ga boring
2. `/newbot` yuboring
3. Tokenni oling

### 2. GitHub ga joylash
```bash
git init
git add .
git commit -m "Telegram bot"
git branch -M main
git remote add origin https://github.com/SIZNING_USERNAME/REPO_NOMI.git
git push -u origin main
```

### 3. Railway ga deploy
1. https://railway.app ga kiring
2. New Project → Deploy from GitHub repo
3. Variables bo'limiga qo'shing:
   - Name: `TELEGRAM_BOT_TOKEN`
   - Value: BotFatherdan olgan token
4. Start Command: `python bot.py`

Tayyor! Bot 24/7 ishlaydi.
