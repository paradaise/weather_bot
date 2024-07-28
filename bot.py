from api_tokens import TG_API_TOKEN
from api_tokens import WEATHER_API_TOKEN
import telebot
from telebot import types
import requests
import json

bot = telebot.TeleBot(TG_API_TOKEN)

main_menu = ('Погода сейчас', 'Погода на завтра', 'Погода на 5 дней', 'Установить/Поменять город', '📑Контакты', '💸Поддержать')
donation_menu = ('🫰Юмани', '💰СБП', '↩️Назад')
user_city = None

def keyboard(menu):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i in range(0, len(menu), 2):
        markup.add(*[types.KeyboardButton(item)
                      for item in menu[i:i+2]])
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    username = message.from_user.username
    name = message.from_user.first_name
    bot.reply_to(message, 
                f'<i>Привет,<b>{name} AKA {username}</b>!Я бот-погодник, чтобы получить актуальную погоду напиши название своего города!</i>', 
                reply_markup=keyboard(main_menu), parse_mode="html")

@bot.message_handler(content_types=['text'])
def get_information(message):
    global user_city
    if message.chat.type == 'private':
        if message.text == '📑Контакты':
            bot.send_message(message.chat.id, 'У вас что-то не работает?Или есть предложения о сотрудничестве?Напишите мне!')
            bot.send_message(message.chat.id, 'Гоголев Виктор:n📱Telegram: t.me/wa55upn🌐Вконтакте: vk.com/yowa55upn🐙GitHub: github.com/paradaisen')
        elif message.text == '💸Поддержать':
            bot.send_message(message.chat.id, '💵Вы можете поддержать наш проект,нажав кнопку ниже:', reply_markup=keyboard(donation_menu))
        elif message.text == '🫰Юмани':
            bot.send_message(message.chat.id, '🫰Вы можете поддержать Юмани по ссылке:nhttps://yoomoney.ru/to/410013032669115')
        elif message.text == '💰СБП':
            bot.send_message(message.chat.id, '💰Вы можете поддержать CБП по ссылке:')
        elif message.text == '↩️Назад':
            bot.send_message(message.chat.id, '↩️Возвращаемся к основному меню', reply_markup=keyboard(main_menu))
        elif message.text == 'Установить/Поменять город':
            bot.send_message(message.chat.id, 'Введите название города:', reply_markup=keyboard(main_menu))
            bot.register_next_step_handler(message, set_city)
        elif message.text == 'Погода сейчас' and user_city:
            get_weather(message, user_city,0)
        elif message.text == 'Погода на завтра' and user_city:
            get_weather(message, user_city,1)
        elif message.text == 'Погода на 5 дней' and user_city:
            get_weather(message, user_city,5)


        else:
            bot.send_message(message.chat.id, 'Нажмите кнопку "Установить/Поменять город", чтобы получить прогноз погоды', reply_markup=keyboard(main_menu))

def set_city(message):
    global user_city
    user_city = message.text
    data = get_weather_data(user_city)
    if data is None:
        bot.send_message(message.chat.id, f'Города <b>{user_city}</b> нет в базе', parse_mode="html",reply_markup=keyboard(main_menu))
    else:
        bot.send_message(message.chat.id, f'Город <b>{data["location"]["name"]},{data["location"]["region"]},{data["location"]["country"]}</b> установлен!', parse_mode="html")
        bot.send_message(message.chat.id, 'Выберите действие:', reply_markup=keyboard(main_menu))

def get_weather_data(city):
    uri = f'http://api.weatherapi.com/v1/forecast.json?days=5&hour=24&aqi=no&lang=ru&q={city}&key={WEATHER_API_TOKEN}'
    r = requests.get(uri)
    if r.status_code == 200:
        return json.loads(r.text)
    else:
        return None

def get_weather(message, city, count):
    data = get_weather_data(city)
    
    def format_weather_info(day_data, date_template, prefix):
        header = f'{prefix} <b>{data["location"]["name"]}</b>: <i>{day_data["day"]["condition"]["text"]}</i>\n'
        avg_temp = f'🌡Средняя температура воздуха: <b>{day_data["day"]["avgtemp_c"]} ℃</b>\n'
        min_temp = f'📉Минимальная температура: <b>{day_data["day"]["mintemp_c"]} ℃</b>\n'
        max_temp = f'📈Максмальная температура: <b>{day_data["day"]["maxtemp_c"]} ℃</b>\n'
        max_wind = f'💨Максимальная скорость ветра: <b>{day_data["day"]["maxwind_kph"]} км/ч</b>\n'
        avg_vlaga = f'💦Влажность: <b>{day_data["day"]["avghumidity"]} %</b>\n'
        rain_probability = f'🌧Вероятность дождя: <b>{day_data["day"]["daily_chance_of_rain"]} %</b>\n'
        sunrise = f'🌅Восход: <b>{day_data["astro"]["sunrise"]}</b>\n'
        sunset = f'🌆Закат: <b>{day_data["astro"]["sunset"]}</b>'
        
        return f'{header}{avg_temp}{min_temp}{max_temp}{max_wind}{avg_vlaga}{rain_probability}{sunrise}{sunset}'
    
    if count == 5:
        for i in range(count):
            date_template = data["forecast"]["forecastday"][i]["date"]
            prefix = f'Прогноз на {i+1} день ({date_template}) в '
            weather_info = format_weather_info(data["forecast"]["forecastday"][i], date_template, prefix)
            bot.send_message(message.chat.id, weather_info, parse_mode="html", reply_markup=keyboard(main_menu))
    else:
        date_template = data["forecast"]["forecastday"][count]["date"]
        if count == 0:
            prefix = f'Сегодня ({date_template}) в '
        elif count == 1:
            prefix = f'Завтра ({date_template}) в '
        
        weather_info = format_weather_info(data["forecast"]["forecastday"][count], date_template, prefix)
        bot.send_message(message.chat.id, weather_info, parse_mode="html", reply_markup=keyboard(main_menu))

    

bot.polling()

