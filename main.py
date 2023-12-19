# -*- coding: utf-8 -*-
import speech_recognition as sr
import telebot
from telebot import types
import requests
import os
import ffmpeg
import soundfile as sf

def checkWeather(message):
    if message.text=="q":

        bot.send_message(message.from_user.id, 'Выберите команду',reply_markup=markup)
        return
    if findweather(message.text)=="":
        print(message.text)
        message = bot.send_message(message.chat.id,
                                   'Неверный город')
        bot.register_next_step_handler(message, checkWeather)
        return
    bot.send_message(message.chat.id, findweather(message.text))
    bot.register_next_step_handler(message, checkWeather)

def findweather(city):
    s_city = f"{city}"
    appid = "b347eb2064ce298f7ff1befb93161bfa"
    strDat=""
    try:
        res = requests.get("http://api.openweathermap.org/data/2.5/weather",
                     params={'q': s_city, 'lang': 'ru', 'units':'metric', 'appid': appid})
        data = res.json()
        strDat+=f"Имя города : {data['name']}\nТемпература : {data['main']['temp']}C\nВлажность : {data['main']['humidity']}%\nДавление : {data['main']['pressure']}мм.рт.ст\nВетер : {data['wind']['speed']}м/с"

    except Exception as e:
        strDat=""
    return strDat
def voice_recogn(message):
    if message.text!="q":
        try:
            filename = str('tmpAud.ogg')
            file_info = bot.get_file(message.voice.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            with open('tmpAud.ogg', 'wb') as new_file:
                new_file.write(downloaded_file)

            data, samplerate = sf.read('tmpAud.ogg')
            sf.write('tmpAud.wav', data, samplerate, format='WAV', subtype='PCM_16')
        except Exception as ex:
            bot.send_message(message.from_user.id, 'Неверное гс')
            bot.register_next_step_handler(message, voice_recogn)
            return

        try:
            recognizer = sr.Recognizer()
            with sr.AudioFile('tmpAud.wav') as source:
                recorded_audio = recognizer.listen(source)

            text = recognizer.recognize_google(recorded_audio, language='ru-RU')
            bot.send_message(message.from_user.id, text)
            os.remove('tmpAud.ogg')
            os.remove('tmpAud.wav')
            bot.register_next_step_handler(message, voice_recogn)

        except Exception as ex:
            bot.send_message(message.from_user.id, 'Не удалось расшифровать гс')
            bot.register_next_step_handler(message, voice_recogn)
            

    else:
        bot.send_message(message.from_user.id, 'Выберите команду',reply_markup=markup)

bot = telebot.TeleBot('6782584036:AAElq7Z1u1QY7iMrDig2c1vTrWewpg3eMts')
markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn1 = types.KeyboardButton("Включить режим погоды",)
btn2 = types.KeyboardButton("Включить режим расшифровки гс")
markup.add(btn1,btn2)



@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.from_user.id, 'Выберите команду',reply_markup=markup)

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == 'Включить режим погоды':
        bot.reply_to(message, 'Введите город [введите q чтобы выйти]')
        bot.register_next_step_handler(message, checkWeather)

    elif message.text == 'Включить режим расшифровки гс':
        bot.reply_to(message, 'Введите голосовое сообщение [введите q чтобы выйти]')
        bot.register_next_step_handler(message, voice_recogn)

bot.polling(none_stop=True, interval=0)


