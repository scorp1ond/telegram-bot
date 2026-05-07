import telebot
import os
import random
import string
from dotenv import load_dotenv
from telebot import types

load_dotenv()

TOKEN = os.getenv("TOKEN")

if TOKEN is None:
    print("Token is not found!")
    exit()

bot = telebot.TeleBot(TOKEN)

keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.add("8ball", "password", "rps")

rps_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
rps_kb.add("Rock", "Paper", "Scissors")

answers = ["Yes", "No", "Maybe", "Try again later"]
choices = ["Rock", "Paper", "Scissors"]

mode = {}


@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, "Choose:", reply_markup=keyboard)


@bot.message_handler(func=lambda m: m.text in ["8ball", "password", "rps"])
def set_mode(message):
    mode[message.chat.id] = message.text
    bot.send_message(message.chat.id, "OK")


@bot.message_handler(func=lambda m: True)
def handle(message):

    m = mode.get(message.chat.id)

    if m == "8ball":
        if message.text.endswith("?"):
            bot.send_message(message.chat.id, random.choice(answers))
        else:
            bot.send_message(message.chat.id, "Ask question")

    elif m == "password":
        if not message.text.isdigit():
            bot.send_message(message.chat.id, "Number only")
            return

        length = int(message.text)
        chars = string.ascii_letters + string.digits
        password = ""

        for i in range(length):
            password += random.choice(chars)

        bot.send_message(message.chat.id, password)

    elif m == "rps":

        user = message.text
        bot_choice = random.choice(choices)

        if user not in choices:
            bot.send_message(message.chat.id, "Use buttons")
            return

        if user == bot_choice:
            bot.send_message(message.chat.id, "Draw")

        elif (user == "Rock" and bot_choice == "Scissors") or \
             (user == "Scissors" and bot_choice == "Paper") or \
             (user == "Paper" and bot_choice == "Rock"):
            bot.send_message(message.chat.id, "You win")
        else:
            bot.send_message(message.chat.id, "Bot wins")


bot.infinity_polling()
