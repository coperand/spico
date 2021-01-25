import telebot

bot = telebot.TeleBot('TOKEN')

white_list = ['coperand']

def ask_platform_worker(call):
    if call.data == 'add_user':
        keyboard = telebot.types.InlineKeyboardMarkup()
        key_insta = telebot.types.InlineKeyboardButton(text='Instagram', callback_data='add_user_insta')
        keyboard.add(key_insta)
        key_vk = telebot.types.InlineKeyboardButton(text='VK', callback_data='add_user_vk')
        keyboard.add(key_vk)
        
        bot.send_message(call.message.chat.id, text="Выберите платформу, пользователя которой вы хотите добавить", reply_markup=keyboard)
    if call.data == 'del_user':
        keyboard = telebot.types.InlineKeyboardMarkup()
        key_insta = telebot.types.InlineKeyboardButton(text='Instagram', callback_data='del_user_insta')
        keyboard.add(key_insta)
        key_vk = telebot.types.InlineKeyboardButton(text='VK', callback_data='del_user_vk')
        keyboard.add(key_vk)
        
        bot.send_message(call.message.chat.id, text="Выберите платформу, пользователя которой вы хотите удалить", reply_markup=keyboard)
    if call.data == 'print_users':
        keyboard = telebot.types.InlineKeyboardMarkup()
        key_insta = telebot.types.InlineKeyboardButton(text='Instagram', callback_data='print_users_insta')
        keyboard.add(key_insta)
        key_vk = telebot.types.InlineKeyboardButton(text='VK', callback_data='print_users_vk')
        keyboard.add(key_vk)
        
        bot.send_message(call.message.chat.id, text="Выберите платформу, пользователей которой вы хотите вывести", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == 'add_user' or call.data == 'del_user' or call.data == 'print_users':
        ask_platform_worker(call)

@bot.message_handler(content_types=['text'])
def text_messages_handler(message):
    if message.from_user.username not in white_list:
        bot.send_message(message.from_user.id, "Доступ запрещен")
        return
    
    #Создаем inline-клавиатуру и наполняем кнопками
    keyboard = telebot.types.InlineKeyboardMarkup()
    key_add_user = telebot.types.InlineKeyboardButton(text='Добавить пользователя', callback_data='add_user')
    keyboard.add(key_add_user)
    key_del_user = telebot.types.InlineKeyboardButton(text='Удалить пользователя', callback_data='del_user')
    keyboard.add(key_del_user)
    key_print_users = telebot.types.InlineKeyboardButton(text='Вывести пользователей', callback_data='print_users')
    keyboard.add(key_print_users)
    
    bot.send_message(message.from_user.id, text="Бот активен. Какие действия вы бы хотели совершить?", reply_markup=keyboard)

bot.polling(none_stop=True, interval=0)

#Тестирование отправки сообщений по инициативе бота
#chatId = 374113718
#bot.send_message(chatId, "Тест инициативной передачи")