import config
import telebot
import pytaf
from urllib import request

TOKEN = config.TOKEN
URL_METAR = config.URL_METAR
URL_TAF = config.URL_TAF

bot = telebot.TeleBot(token=TOKEN)
keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.row('/start', '/get_metar', '/get_taf')

def parse_data(code):
    code = code.replace('TAF TAF', 'TAF', 1).split('\n', 1)[1]
    return pytaf.Decoder(pytaf.TAF(code)).decode_taf()


@bot.message_handler(commands=['start', 'help'])
def start(message):
    msg = "Привет. Это бот для получения авиационного прогноза погоды " \
          "с серверов NOAA. Бот настроен на аэропорт Жуляны (UKKK)."
    bot.send_message(message.chat.id, msg, reply_markup=keyboard)

@bot.message_handler(commands=['get_metar'])
def get_metar(message):
    # Fetch info from server.
    code = request.urlopen(URL_METAR).read().decode('utf-8')
    # Send formatted answer.
    bot.send_message(message.chat.id, parse_data(code), reply_markup=keyboard)

@bot.message_handler(commands=['get_taf'])
def get_taf(message):
    # Fetch info from server.
    code = request.urlopen(URL_TAF).read().decode('utf-8')
    # Send formatted answer.
    bot.send_message(message.chat.id, parse_data(code), reply_markup=keyboard)


bot.polling(none_stop=True)
