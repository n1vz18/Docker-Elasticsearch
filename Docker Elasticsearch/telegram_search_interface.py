from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext
from elasticsearch import Elasticsearch
from search_engine import SearchEngine



def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("Начать поиск слова", callback_data='search')],
        [InlineKeyboardButton("Помощь", callback_data='help')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(f'Приветствую, {user.first_name}! \nДобро пожаловать в главное меню поисковика Docker Elasticsearch. \nВыберите команду для работы с ботом:', reply_markup=reply_markup)

def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Это раздел помощи. Используйте /search для поиска слов.")

def search(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    # Кнопка возврата в главное меню
    buttons = [
        [InlineKeyboardButton("Назад", callback_data='back_to_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    query.edit_message_text(text="Введите слово для поиска или используйте /start для возврата в главное меню.", reply_markup=reply_markup)

def handle_message(update: Update, context: CallbackContext) -> None:
    if update.message:
        # Проверка ввода слова
        if context.user_data.get('awaiting_search_term'):
            # Пользователь находится в меню поиска и ввел поисковый запрос.
            text = update.message.text
            search_engine = SearchEngine()
            results = search_engine.search_phrase(text)
            
            context.user_data['awaiting_search_term'] = False
            
            if results:
                # Сохранённые результаты поиска для дальнейшего использования
                context.user_data['last_search_results'] = results
                
                message_text = "Выберите статью:\n"
                buttons = []
                for index, result in enumerate(results):
                    truncated_result = (result[:300] + '...') if len(result) > 300 else result
                    message_text += f"{index + 1}. {truncated_result}\n\n"
                    buttons.append([InlineKeyboardButton(f"Читать статью {index + 1}", callback_data=str(index))])
                
                # Добавление кнопки
                buttons.append([InlineKeyboardButton("Главное меню", callback_data='back_to_menu')])
                reply_markup = InlineKeyboardMarkup(buttons)
                
                update.message.reply_text(message_text, reply_markup=reply_markup)
            else:
                buttons = [
                    [InlineKeyboardButton("Начать новый поиск", callback_data='search')],
                    [InlineKeyboardButton("Отмена", callback_data='back_to_menu')]
                ]
                reply_markup = InlineKeyboardMarkup(buttons)
                update.message.reply_text("Статьи по запросу не найдены.", reply_markup=reply_markup)
        else:
            update.message.reply_text("Пожалуйста, введите /search для начала поиска, или /start для возврата в главное меню.") 

def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    data = query.data

    # Возврат в гланое меню
    if data == 'back_to_menu':
        # Удаление прошлого сообщения + выбор команды
        context.user_data['awaiting_search_term'] = False
        query.delete_message()
        update.effective_chat.send_message(text="Выберите команду:", reply_markup=main_menu_keyboard())

    # Кнопка поиска
    elif data == 'search':
        context.user_data['awaiting_search_term'] = True
        query.delete_message()
        update.effective_chat.send_message(text="Введите слово для поиска:")

    # Кнопка Помощи
    elif data == 'help':
        context.user_data['awaiting_search_term'] = False  # Reset the flag
        help_message = "Вы можете использовать команду /search для поиска слова или /start для возврата в главное меню."
        query.edit_message_text(text=help_message)

    # Возвращение к списку результатов поиска
    elif data == 'back_to_results':
        if 'last_search_results' in context.user_data:
            message_text = "Выберите статью:\n"
            buttons = []
            for index, result in enumerate(context.user_data['last_search_results']):
                truncated_result = (result[:300] + '...') if len(result) > 300 else result
                message_text += f"{index + 1}. {truncated_result}\n\n"
                buttons.append([InlineKeyboardButton(f"Читать статью {index + 1}", callback_data=str(index))])
            buttons.append([InlineKeyboardButton("Главное меню", callback_data='back_to_menu')])
            reply_markup = InlineKeyboardMarkup(buttons)
            query.edit_message_text(text=message_text, reply_markup=reply_markup)
        else:
            query.edit_message_text(text="Список результатов не найден. Пожалуйста, начните новый поиск.")

    # Отображение полного текста выбранной статьи
    elif data.isdigit():
        index = int(data)
        if 'last_search_results' in context.user_data:
            selected_article = context.user_data['last_search_results'][index]
            buttons = [
                [InlineKeyboardButton("Назад к результатам", callback_data='back_to_results')],
                [InlineKeyboardButton("Главное меню", callback_data='back_to_menu')]
            ]
            reply_markup = InlineKeyboardMarkup(buttons)
            query.edit_message_text(text=selected_article, reply_markup=reply_markup)
        else:
            query.edit_message_text(text="Произошла ошибка, повторите поиск.")

    # Обработка неожиданных данных обратного вызова
    else:
        query.edit_message_text(text="Произошла ошибка с данными кнопки, повторите поиск.")
        

def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("Начать поиск слова", callback_data='search')],
        [InlineKeyboardButton("Помощь", callback_data='help')]
    ]
    return InlineKeyboardMarkup(keyboard)

def main() -> None:

    updater = Updater("TOKEN_TG_BOT", use_context=True)

    dp = updater.dispatcher

    # Рабочии команды TG бота ... pass
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))

    # не корректрый ввод
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    
    dp.add_handler(CallbackQueryHandler(button))

    # Start the Bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()