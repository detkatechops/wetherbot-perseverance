import telebot
import pytaf
from urllib import request
from googletrans import Translator
from config import TOKEN, URL_METAR, URL_TAF


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
    code = request.urlopen(URL_METAR).read().decode('utf-8')
    # Send formatted answer.
    bot.send_message(message.chat.id, parse_data(code), reply_markup=keyboard)


@bot.message_handler(commands=['get_taf'])
def get_taf(message):
    # Fetch info from server.
    code = request.urlopen(URL_TAF).read().decode('utf-8')
    # Send formatted answer.
    bot.send_message(message.chat.id, parse_data(code), reply_markup=keyboard)


# Запускаем бота, чтобы работал 24/7
if __name__ == '__main__':
    bot.polling(none_stop=True, interval=5, timeout=40)
