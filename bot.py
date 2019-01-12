import config
import telebot
from telebot import types
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy.orm import sessionmaker


bot = telebot.TeleBot(config.TOKEN)
# информация о боте
bot_info = bot.get_me()
#БД

engine = create_engine(config.url)
metadata = MetaData(engine)
people = Table("people", metadata,
               Column("id", Integer, primary_key = True),
               Column("name", String),
               )
Session = sessionmaker(bind = engine)
session = Session()
metadata.create_all(engine)

"""
class User(object):
    def __init__(self, id_user, name_user):
        self.id = id_user
        self.name = name_user
"""

# start и выбор режима пользователя
@bot.message_handler(commands = ['start'])
def user(message):
    start = types.ReplyKeyboardMarkup(resize_keyboard = True, one_time_keyboard = True)
    start.add("Просмотр продуктов", "/admin")
    id_user = message.from_user.id
    name_user = message.from_user.first_name, message.from_user.last_name
    in_base(id_user, name_user)
    bot.register_next_step_handler(
        bot.send_message(message.chat.id, "Здравствуйте, Вас приветствует бот {}".format(bot_info.username),
                         reply_markup=start), first_step)


def in_base(id_user, name_user):
    try:
        session.query(people).filter_by(id = id_user).first()
    except:
        one_user = people.insert().values(id = id_user, name = name_user)
        session.execute(one_user)
        session.commit()
    else:
        pass



def first_step(message):
    if message.text == "Просмотр продуктов":
        pass
    elif message.text == "/admin":
        if message.from_user.id in config.admins_id_list:
            options_for_admin(message)
        else:
            bot.send_message(message.chat.id, "Вы не обладаете правами администратора", user)
    else:
        bot.send_message(message.chat.id, "Я не знаю такой комманды, выберите, пожалуйста, из предложенных вариантов", user)


# выбор опции для админа
@bot.message_handler(content_types = ["text"])
def options_for_admin(message):
    btn_options_for_admin = types.ReplyKeyboardMarkup(resize_keyboard = True, one_time_keyboard = True)
    btn_options_for_admin.add("Продукты", "Рассылка")
    bot.register_next_step_handler(
        bot.send_message(message.chat.id, "Выберите опцию:", reply_markup = btn_options_for_admin), second_step)


def second_step(message):
    if message.text == "Продукты":
        pass
    elif message.text == "Рассылка":
        bot.send_message(message.chat.id, "Введите сообщение для рассылки:", mailing)
    else:
        bot.send_message(message.chat.id, "Я не знаю такой комманды, выберите, пожалуйста, из предложенных вариантов",
                         options_for_admin)

def mailing(message):
    for person_id in session.query(people).order_by(people.id): 
        bot.send_message(message.chat.person_id, message)
        time.sleep(1)

if __name__ == '__main__':
	bot.polling(none_stop = True)
