import telebot
import pytaf
import os
import flask
from urllib import request
from googletrans import Translator


TOKEN = os.getenv('API_BOT_TOKEN')

# Создание бота
bot = telebot.TeleBot(token=TOKEN)
# создать объект класса Translator
translator = Translator()
keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.row('/start', '/get_metar', '/get_taf')


def parse_data(code):
    # заменяте таф таф на таф один раз, один раз режет строку на \n и берет второй элемент по счету, бо первый это 0
    code = code.replace('TAF TAF', 'TAF', 1).split('\n', 1)[1]
    # взятый из переменной code  код подается в обьект конвертирования кода сводки аэропорта
    content = pytaf.Decoder(pytaf.TAF(code)).decode_taf()
    # в обьект перевода подается погода не английском
    translation = translator.translate(content, src='en', dest='ru')
    return translation.text

@bot.message_handler(commands=['start', 'help'])
def start(message):
    msg = "Привет. Это бот для получения авиационного прогноза погоды " \
          "с серверов NOAA. Бот настроен на аэропорт Жуляны (UKKK)."
    bot.send_message(message.chat.id, msg, reply_markup=keyboard)


@bot.message_handler(commands=['get_metar'])
def get_metar(message):
    # Fetch info from server.
    code = request.urlopen(os.getenv('URL_METAR')).read().decode('utf-8')
    # Send formatted answer.
    bot.send_message(message.chat.id, parse_data(code), reply_markup=keyboard)


@bot.message_handler(commands=['get_taf'])
def get_taf(message):
    # Fetch info from server.
    code = request.urlopen(os.getenv('URL_TAF')).read().decode('utf-8')
    # Send formatted answer.
    bot.send_message(message.chat.id, parse_data(code), reply_markup=keyboard)


# set web hook
server = flask.Flask(__name__)


@server.route('/' + TOKEN, methods=['POST'])
def get_messages():
    bot.process_new_updates([telebot.types.Update.de_json(flask.request.stream.read().decode('utf-8'))])
    return '!', 200


@server.route('/', methods=["GET"])
def web_hook():
    bot.remove_webhook()
    bot.set_webhook(url=os.getenv('HEROKU_URL') + TOKEN)
    return '!', 200

# Запускаем бота, чтобы работал 24/7
if __name__ == '__main__':
    # bot.polling(none_stop=True, interval=15, timeout=60)
    server.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
