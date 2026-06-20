web: gunicorn "api.app:create_app()" --bind 0.0.0.0:$PORT --workers 2
bot: python notifier/telegram_bot.py
