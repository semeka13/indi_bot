from datetime import datetime

from telebot import types

import config
import telebot

city = ""
place = ""
knownUsers = []
userStep = {}


def get_user_step(uid):
    if uid in userStep:
        print(userStep[uid])
        return userStep[uid]
    else:
        knownUsers.append(uid)
        userStep[uid] = 0
        print("New user detected, who hasn't used \"/start\" yet")
        return 0


def listener(messages):
    for m in messages:
        if m.content_type == 'text':
            try:
                print(str(m.from_user.username) + " [" + str(m.chat.id) + "]: " + m.text)
            except Exception:
                print("[" + str(m.chat.id) + "]: " + m.text)


bot = telebot.TeleBot(config.TOKEN)
bot.set_update_listener(listener)


@bot.message_handler(commands=["start"])
def start(message):
    cid = message.from_user.id
    knownUsers.append(cid)
    userStep[cid] = 0
    m = "Вас приветствует бот, которому Вы можете оставить сообщение, если один из биоиндикаторов показал загрязнения в воздухе.\n\nВсе сообщения абсолютно анонимны.\nДля того, чтобы сообщить о проблеме, отправьте /air_problem."
    bot.send_message(message.from_user.id, m)


@bot.message_handler(commands=["air_problem"])
def air_problem(message):
    userStep[message.from_user.id] = 1
    bot.send_message(message.from_user.id, "Напишите, в каком городе Вы заметили проблему.")


@bot.message_handler(func=lambda message: get_user_step(message.from_user.id) == 1)
def stage_one(message):
    global city
    if message.text.lower() in config.places:
        city = message.text.lower()
        m = "Выберите место, где Вы заметили проблему:"
        keyboard = types.InlineKeyboardMarkup(True)
        for place in config.places[message.text.lower()]:
            keyboard.add(types.InlineKeyboardButton(place, callback_data=place))
        bot.send_message(message.from_user.id,
                         m, reply_markup=keyboard)

    else:
        bot.send_message(message.from_user.id, "В данном городе у нас пока нет биоиндикаторов.\nПопробуйте /air_problem заново.")


@bot.callback_query_handler(func=lambda call: True)
def callback_buttons(call):
    global place
    userStep[call.from_user.id] = 2
    bot.send_message(call.from_user.id, "А теперь опишите проблему, которую Вы заметили, и пришлите её фото.")
    place = call.data


@bot.message_handler(func=lambda message: get_user_step(message.from_user.id) == 2)
def stage_two(message):
    bot.send_message(message.from_user.id, "Ваше сообщение принято, спасибо.")
    bot.send_message(787539657, f"Город: {city.capitalize()}\nМесто: {place}\nЖалоба: {message.text}")


try:
    print("BOT UP", str(datetime.now()).split(".")[0], sep="\t")
    bot.polling(none_stop=True)
except Exception as e:
    bot.stop_bot()
    print("BOT DOWN", str(datetime.now()).split(".")[0], sep="\t")

