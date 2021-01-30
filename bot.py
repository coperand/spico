import sys
import time
import os
import urllib.request
from threading import Thread
import telebot
from insta.insta import InstaModule
from vk.vk import VkModule

bot = telebot.TeleBot('TOKEN')

white_list = ['coperand']
user_list = {}

def saveMedia(file_name, url):
        img = urllib.request.urlopen(url).read()
        out = open(file_name, "wb")
        out.write(img)
        out.close()

def send_data_callback(chatId, text='', images=[], videos=[]):
    if text != '':
        bot.send_message(chatId, text)
    for item in images:
        file_name = '/tmp/spico-temporary-file.jpg'
        saveMedia(file_name, item)

        img = open(file_name, "rb")
        bot.send_photo(chatId, img)
        img.close()
        os.remove(file_name)
    for item in videos:
        file_name = '/tmp/spico-temporary-file.mp4'
        saveMedia(file_name, item)

        vid = open(file_name, "rb")
        bot.send_video(chatId, vid)
        vid.close()
        os.remove(file_name)

try:
    insta = InstaModule('ingabeiko94', 'mKzkgUbYBs', send_data_callback)
    vk = VkModule('8801923291704', 'CM8Ipp69w', send_data_callback)
except Exception as e:
    print("Exception: " + str(e))
    sys.exit()

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
    if message.text == '/cancel':
        send_menu(message.from_user.id, "Бот активен. Какие действия вы бы хотели совершить?")
        return

    #Проверяем имя пользователя
    if insta.checkName(message.text) is False:
        msg = bot.send_message(message.from_user.id, text="Имя пользователя некорректно. Введите другое или /cancel для отмены")
        bot.register_next_step_handler(msg, add_insta_username)
        return

    user_dict = user_list.setdefault(message.from_user.username, {'insta': [], 'vk': [], 'id': message.from_user.id})
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

    user_dict = user_list.setdefault(message.from_user.username, {'insta': [], 'vk': [], 'id': message.from_user.id})
    if message.text not in user_dict['insta']:
        msg = bot.send_message(message.from_user.id, text="Пользователя нет в списке отслеживаемых. Введите другого или /cancel для отмены")
        bot.register_next_step_handler(msg, del_insta_username)
    else:
        user_dict['insta'].remove(message.text)
        bot.send_message(message.from_user.id, "Пользователь " + message.text + " удален из списка отслеживаемых")
        send_menu(message.from_user.id, "Какие еще действия вы бы хотели совершить?")
        insta.removeData(message.text)

def add_vk_id(message):
    if message.text == '/cancel':
        send_menu(message.from_user.id, "Бот активен. Какие действия вы бы хотели совершить?")
        return

    #Проверяем имя пользователя
    username = vk.checkId(message.text)
    if username is False:
        msg = bot.send_message(message.from_user.id, text="Идентификатор пользователя некорректен. Введите другой или /cancel для отмены")
        bot.register_next_step_handler(msg, add_vk_id)
        return

    user_dict = user_list.setdefault(message.from_user.username, {'insta': [], 'vk': [], 'id': message.from_user.id})
    if message.text not in user_dict['vk']:
        user_dict['vk'].append(message.text)
        bot.send_message(message.from_user.id, "Пользователь " + username + ' (' + message.text + ')' + " добавлен в список отслеживаемых")
        send_menu(message.from_user.id, "Какие еще действия вы бы хотели совершить?")
    else:
        msg = bot.send_message(message.from_user.id, text="Пользователь уже имеется в списке отслеживаемых. Введите другого или /cancel для отмены")
        bot.register_next_step_handler(msg, add_vk_id)

def del_vk_id(message):
    if message.text == '/cancel':
        send_menu(message.from_user.id, "Бот активен. Какие действия вы бы хотели совершить?")
        return

    user_dict = user_list.setdefault(message.from_user.username, {'insta': [], 'vk': [], 'id': message.from_user.id})
    if message.text not in user_dict['vk']:
        msg = bot.send_message(message.from_user.id, text="Пользователя нет в списке отслеживаемых. Введите другого или /cancel для отмены")
        bot.register_next_step_handler(msg, del_vk_id)
    else:
        user_dict['vk'].remove(message.text)
        bot.send_message(message.from_user.id, "Пользователь " + message.text + " удален из списка отслеживаемых. ")
        send_menu(message.from_user.id, "Какие еще действия вы бы хотели совершить?")
        vk.removeData(message.text)

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
        user_dict = user_list.setdefault(call.from_user.username, {'insta': [], 'vk': [], 'id': call.from_user.id})
        for item in user_dict['insta']:
            print_str += "\n" + item
        bot.send_message(call.message.chat.id, print_str)
        send_menu(call.message.chat.id, "Какие еще действия вы бы хотели совершить?")

    if call.data == 'del_user_insta':
        print_str = 'Введите имя пользователя, которого вы хотите удалить из следующего списка или /cancel для отмены:'
        user_dict = user_list.setdefault(call.from_user.username, {'insta': [], 'vk': [], 'id': call.from_user.id})
        for item in user_dict['insta']:
            print_str += "\n" + item
        msg = bot.send_message(call.message.chat.id, print_str)
        bot.register_next_step_handler(msg, del_insta_username)

    if call.data == 'print_users_vk':
        print_str = 'Список отслеживаемых пользователей:'
        user_dict = user_list.setdefault(call.from_user.username, {'insta': [], 'vk': [], 'id': call.from_user.id})
        for item in user_dict['vk']:
            username = vk.checkId(item)
            print_str += "\n" + username + " (" + item + ")"
        bot.send_message(call.message.chat.id, print_str)
        send_menu(call.message.chat.id, "Какие еще действия вы бы хотели совершить?")

    if call.data == 'del_user_vk':
        print_str = 'Введите идентификатор пользователя (число в скобках), которого вы хотите удалить из следующего списка (или /cancel для отмены):'
        user_dict = user_list.setdefault(call.from_user.username, {'insta': [], 'vk': [], 'id': call.from_user.id})
        for item in user_dict['vk']:
            username = vk.checkId(item)
            print_str += "\n" + username + " (" + item + ")"
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

#insta.getData("arina_weasley")
#vk.getData('78961353')

polling_thread = Thread(target=bot.polling, args=(True, 0,))
polling_thread.start()

while 1:
    print("Cycle iteration")
    for user_name in user_list:
        for item in user_list[user_name]['insta']:
            insta.getData(item, user_list[user_name]['id'])
            pass
        for item in user_list[user_name]['vk']:
            vk.getData(item, user_list[user_name]['id'])
            pass
    #TODO: Подобрать таймаут
    time.sleep(30)
