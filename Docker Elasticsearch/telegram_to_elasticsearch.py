from telegram.ext import Updater, MessageHandler, Filters, CallbackContext
from telegram import Update
from search_engine import SearchEngine  
from bot_logger import configure_logging  

logger = configure_logging()

TELEGRAM_BOT_TOKEN = 'TOKEN_TG_BOT'

search_engine = SearchEngine()

def channel_post(update: Update, context: CallbackContext):
    text = update.channel_post.text or update.channel_post.caption
    if text:
        search_engine.index_text(text)
        logger.info(f"Indexed text: {text[:50]}...")  

def main():
    updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.update.channel_posts, channel_post))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()