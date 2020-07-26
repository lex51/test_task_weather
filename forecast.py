#!/usr/bin/env python3

import telebot
import requests
from bs4 import BeautifulSoup as bs
import datetime
from dateutil.parser import parse 
import config
import re

tele_token = config.token
bot = telebot.TeleBot(tele_token)

@bot.message_handler(commands=['start', 'help'])
def help_response(message):

    bot.send_message(message.chat.id, 'Доброго времени суток ;)\nДанный бот является результатом выполнения тестового задания и показывает погоду на следущие 30 дней в славном городе Ярославль.\n')

@bot.message_handler(content_types=['text'])
def get_aud_messages(message):

    day_date = ''
    if re.match('сегодня', message.text.lower()):
        day_date = datetime.datetime.now()
    elif re.match('завтра', message.text.lower()):
        day_date = (datetime.date.today() + datetime.timedelta(days=1))
    elif re.match('послезавтра', message.text.lower()):
        day_date = (datetime.date.today() + datetime.timedelta(days=2))
    else:
        try:
            day_date = parse(message.text)
        except BaseException:
            pass
    if day_date:
        forecast = get_forecast_by_date(str(day_date.day))
        bot.send_message(message.chat.id, \
            f'Погода в Ярославле на {day_date.day}.{day_date.month}.{day_date.year}:\n{forecast["rain_percent"]}\n{forecast["water"]}\nТемпература воздуха {forecast["temp"]} \u00b0 C')


def get_forecast_by_date(day_date):

    url = 'https://pogodnik.com/11135-pogoda-v-yaroslavle-rossiya/month'
    headers = requests.utils.default_headers()
    headers.update({ 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/69.0'})
    resp = requests.get(url, headers)
    soup = bs(resp.text, 'lxml')

    d = {}
    for i in soup.find_all(class_='item'): 
        date = i.find(class_='date')
        if date:
            d[date.text.strip().lstrip('0')]= \
            { 
                'rain_percent': i.find('i', class_='icon').get('title').split('\n')[1],
                'water': i.find('i', class_='icon').get('title').split('\n')[0],
                'temp': i.find_all('span')[1].text
            }

    return d.get(day_date, None)



bot.polling(none_stop=True, interval=0)