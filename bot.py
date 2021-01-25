import telebot

bot = telebot.TeleBot('TOKEN')

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    print(message)

#bot.polling(none_stop=True, interval=0)

chatId = 374113718
bot.send_message(chatId, "Тест инициативной передачи")