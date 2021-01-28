import time
from threading import Thread
import telebot
from insta.insta import InstaModule
from vk.vk import VkModule

bot = telebot.TeleBot('TOKEN')

white_list = ['coperand']
user_list = {}

def send_menu(user_id, message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    key_add_user = telebot.types.InlineKeyboardButton(text='Добавить пользователя', callback_data='add_user')
    keyboard.add(key_add_user)
    key_del_user = telebot.types.InlineKeyboardButton(text='Удалить пользователя', callback_data='del_user')
    keyboard.add(key_del_user)
    key_print_users = telebot.types.InlineKeyboardButton(text='Вывести пользователей', callback_data='print_users')
    keyboard.add(key_print_users)

    bot.send_message(user_id, text=message, reply_markup=keyboard)

def add_insta_username(message):
    #TODO: Проверить имя пользователя

    if message.text == '/cancel':
        send_menu(message.from_user.id, "Бот активен. Какие действия вы бы хотели совершить?")
        return

    user_dict = user_list.setdefault(message.from_user.username, {'insta': [], 'vk': []})
    if message.text not in user_dict['insta']:
        user_dict['insta'].append(message.text)
        bot.send_message(message.from_user.id, "Пользователь " + message.text + " добавлен в список отслеживаемых")
        send_menu(message.from_user.id, "Какие еще действия вы бы хотели совершить?")
    else:
        msg = bot.send_message(message.from_user.id, text="Пользователь уже имеется в списке отслеживаемых. Введите другого или /cancel для отмены")
        bot.register_next_step_handler(msg, add_insta_username)

def del_insta_username(message):
    if message.text == '/cancel':
        send_menu(message.from_user.id, "Бот активен. Какие действия вы бы хотели совершить?")
        return

    user_dict = user_list.setdefault(message.from_user.username, {'insta': [], 'vk': []})
    if message.text not in user_dict['insta']:
        msg = bot.send_message(message.from_user.id, text="Пользователя нет в списке отслеживаемых. Введите другого или /cancel для отмены")
        bot.register_next_step_handler(msg, del_insta_username)
    else:
        user_dict['insta'].remove(message.text)
        bot.send_message(message.from_user.id, "Пользователь " + message.text + " удален из списка отслеживаемых")
        send_menu(message.from_user.id, "Какие еще действия вы бы хотели совершить?")
        #TODO: Удалить медиа из бд

def add_vk_id(message):
    #TODO: Проверить имя пользователя

    if message.text == '/cancel':
        send_menu(message.from_user.id, "Бот активен. Какие действия вы бы хотели совершить?")
        return

    user_dict = user_list.setdefault(message.from_user.username, {'insta': [], 'vk': []})
    if message.text not in user_dict['vk']:
        user_dict['vk'].append(message.text)
        bot.send_message(message.from_user.id, "Пользователь " + message.text + " добавлен в список отслеживаемых")
        send_menu(message.from_user.id, "Какие еще действия вы бы хотели совершить?")
    else:
        msg = bot.send_message(message.from_user.id, text="Пользователь уже имеется в списке отслеживаемых. Введите другого или /cancel для отмены")
        bot.register_next_step_handler(msg, add_vk_id)

def del_vk_id(message):
    if message.text == '/cancel':
        send_menu(message.from_user.id, "Бот активен. Какие действия вы бы хотели совершить?")
        return

    user_dict = user_list.setdefault(message.from_user.username, {'insta': [], 'vk': []})
    if message.text not in user_dict['vk']:
        msg = bot.send_message(message.from_user.id, text="Пользователя нет в списке отслеживаемых. Введите другого или /cancel для отмены")
        bot.register_next_step_handler(msg, del_vk_id)
    else:
        user_dict['vk'].remove(message.text)
        bot.send_message(message.from_user.id, "Пользователь " + message.text + " удален из списка отслеживаемых. ")
        send_menu(message.from_user.id, "Какие еще действия вы бы хотели совершить?")
        #TODO: Удалить медиа из бд

def ask_platform_worker(call):
    if call.data == 'add_user':
        keyboard = telebot.types.InlineKeyboardMarkup()
        key_insta = telebot.types.InlineKeyboardButton(text='Instagram', callback_data='add_user_insta')
        keyboard.add(key_insta)
        key_vk = telebot.types.InlineKeyboardButton(text='VK', callback_data='add_user_vk')
        keyboard.add(key_vk)
        key_return = telebot.types.InlineKeyboardButton(text='Вернуться', callback_data='return')
        keyboard.add(key_return)

        bot.send_message(call.message.chat.id, text="Выберите платформу, пользователя которой вы хотите добавить", reply_markup=keyboard)
    if call.data == 'del_user':
        keyboard = telebot.types.InlineKeyboardMarkup()
        key_insta = telebot.types.InlineKeyboardButton(text='Instagram', callback_data='del_user_insta')
        keyboard.add(key_insta)
        key_vk = telebot.types.InlineKeyboardButton(text='VK', callback_data='del_user_vk')
        keyboard.add(key_vk)
        key_return = telebot.types.InlineKeyboardButton(text='Вернуться', callback_data='return')
        keyboard.add(key_return)

        bot.send_message(call.message.chat.id, text="Выберите платформу, пользователя которой вы хотите удалить", reply_markup=keyboard)
    if call.data == 'print_users':
        keyboard = telebot.types.InlineKeyboardMarkup()
        key_insta = telebot.types.InlineKeyboardButton(text='Instagram', callback_data='print_users_insta')
        keyboard.add(key_insta)
        key_vk = telebot.types.InlineKeyboardButton(text='VK', callback_data='print_users_vk')
        keyboard.add(key_vk)
        key_return = telebot.types.InlineKeyboardButton(text='Вернуться', callback_data='return')
        keyboard.add(key_return)

        bot.send_message(call.message.chat.id, text="Выберите платформу, пользователей которой вы хотите вывести", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == 'add_user' or call.data == 'del_user' or call.data == 'print_users':
        ask_platform_worker(call)

    if call.data == 'add_user_insta':
        msg = bot.send_message(call.message.chat.id, text="Введите имя пользователя или /cancel для отмены")
        bot.register_next_step_handler(msg, add_insta_username)

    if call.data == 'add_user_vk':
        msg = bot.send_message(call.message.chat.id, text="Введите id пользователя (или /cancel для отмены)")
        bot.register_next_step_handler(msg, add_vk_id)

    if call.data == 'print_users_insta':
        print_str = 'Список отслеживаемых пользователей:'
        user_dict = user_list.setdefault(call.from_user.username, {'insta': [], 'vk': []})
        for item in user_dict['insta']:
            print_str += "\n" + item
        bot.send_message(call.message.chat.id, print_str)
        send_menu(call.message.chat.id, "Какие еще действия вы бы хотели совершить?")

    if call.data == 'del_user_insta':
        print_str = 'Введите имя пользователя, которого вы хотите удалить из следующего списка или /cancel для отмены:'
        user_dict = user_list.setdefault(call.from_user.username, {'insta': [], 'vk': []})
        for item in user_dict['insta']:
            print_str += "\n" + item
        msg = bot.send_message(call.message.chat.id, print_str)
        bot.register_next_step_handler(msg, del_insta_username)

    if call.data == 'print_users_vk':
        print_str = 'Список отслеживаемых пользователей:'
        user_dict = user_list.setdefault(call.from_user.username, {'insta': [], 'vk': []})
        for item in user_dict['vk']:
            print_str += "\n" + item
        bot.send_message(call.message.chat.id, print_str)
        send_menu(call.message.chat.id, "Какие еще действия вы бы хотели совершить?")
        #TODO: Вывод имен?

    if call.data == 'del_user_vk':
        print_str = 'Введите идентификатор пользователя, которого вы хотите удалить из следующего списка (или /cancel для отмены):'
        user_dict = user_list.setdefault(call.from_user.username, {'insta': [], 'vk': []})
        for item in user_dict['vk']:
            print_str += "\n" + item
        #TODO: Вывод имен?
        msg = bot.send_message(call.message.chat.id, print_str)
        bot.register_next_step_handler(msg, del_vk_id)

    if call.data == 'return':
        send_menu(call.message.chat.id, "Бот активен. Какие действия вы бы хотели совершить?")

    bot.answer_callback_query(call.id)

@bot.message_handler(content_types=['text'])
def text_messages_handler(message):
    if message.from_user.username not in white_list:
        bot.send_message(message.from_user.id, "Доступ запрещен")
        return

    send_menu(message.from_user.id, "Бот активен. Какие действия вы бы хотели совершить?")

insta = InstaModule('ingabeiko94', 'mKzkgUbYBs')
#insta.getData("arina_weasley")
vk = VkModule('8801923291704', 'CM8Ipp69w')
#vk.getData('78961353')

polling_thread = Thread(target=bot.polling, args=(True, 0,))
polling_thread.start()

#Тестирование отправки сообщений по инициативе бота
#chatId = 374113718
#while 1:
#    time.sleep(3)
#    bot.send_message(chatId, "Тест инициативной передачи")
