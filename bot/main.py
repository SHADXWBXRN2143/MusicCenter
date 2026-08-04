"""
===========================================================
 MusicCenter
-----------------------------------------------------------
 Telegram Bot Entry Point

 Run with: python -m bot.main

 Version : 0.1
===========================================================
"""

from telegram.ext import Application, CallbackQueryHandler, CommandHandler

from bot import handlers
from bot.config import ALLOWED_USER_IDS, BOT_TOKEN


def main():
    if not BOT_TOKEN:
        raise SystemExit("TELEGRAM_BOT_TOKEN is not set")

    if not ALLOWED_USER_IDS:
        print("Warning: TELEGRAM_ALLOWED_IDS is empty - nobody will be able to use this bot")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", handlers.start))
    app.add_handler(CommandHandler("now", handlers.now_playing))
    app.add_handler(CommandHandler("search", handlers.search))
    app.add_handler(CallbackQueryHandler(handlers.button_callback))

    print("MusicCenter bot starting (polling)...")
    app.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    main()
