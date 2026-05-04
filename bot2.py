import telebot
import os
import re
from dotenv import load_dotenv
from telebot import types
from telebot import custom_filters
from telebot.storage import StateMemoryStorage
from telebot.handler_backends import State, StatesGroup

load_dotenv()

TOKEN = os.getenv('TOKEN')

if TOKEN is None:
    print('Token is not found!')
    exit()

state_storage = StateMemoryStorage()
bot = telebot.TeleBot(TOKEN, state_storage=state_storage)

bot.add_custom_filter(custom_filters.StateFilter(bot))


class RegistrationStates(StatesGroup):
    waiting_for_email = State()
    waiting_for_phone = State()


registration_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
registration_btn = types.KeyboardButton('Registration 🪪')
registration_kb.add(registration_btn)

cancel_kb = types.InlineKeyboardMarkup()
cancel_btn = types.InlineKeyboardButton('Cancel 🚫', callback_data='cancel')
cancel_kb.add(cancel_btn)

remove_kb = types.ReplyKeyboardRemove()


@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.send_message(
        message.chat.id,
        'Hello! Press "Registration" to start.',
        reply_markup=registration_kb
    )


@bot.message_handler(func=lambda message: message.text.startswith('Registration'))
def registration_start(message):

    temp_msg = bot.send_message(
        message.chat.id,
        'Loading interface...',
        reply_markup=remove_kb
    )

    bot.delete_message(message.chat.id, temp_msg.message_id)

    bot.set_state(
        message.from_user.id,
        RegistrationStates.waiting_for_email,
        message.chat.id
    )

    bot.send_message(
        message.chat.id,
        'Great! Send your email address.',
        reply_markup=cancel_kb
    )


@bot.message_handler(state=RegistrationStates.waiting_for_email)
def process_email(message):
    email = message.text
    email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'

    print(f'New email: {email}')

    if re.match(email_pattern, email):

        with open('emails.txt', 'a') as f:
            f.write(email + '\n')

        bot.set_state(
            message.from_user.id,
            RegistrationStates.waiting_for_phone,
            message.chat.id
        )

        bot.send_message(
            message.chat.id,
            'Now send your phone number'
        )

    else:
        bot.send_message(
            message.chat.id,
            'Invalid email. Try again.'
        )


@bot.message_handler(state=RegistrationStates.waiting_for_phone)
def process_phone(message):
    phone = message.text

    phone_pattern = r'^\+?\d{7,15}$'

    print(f'New phone: {phone}')

    if re.match(phone_pattern, phone):

        with open('phones.txt', 'a') as f:
            f.write(phone + '\n')

        bot.send_message(
            message.chat.id,
            'Registration complete!',
            reply_markup=registration_kb
        )

        bot.delete_state(message.from_user.id, message.chat.id)

    else:
        bot.send_message(
            message.chat.id,
            'Invalid phone number. Try again'
        )


@bot.callback_query_handler(lambda call: call.data == 'cancel')
def cancel_handler(call):

    bot.delete_state(call.from_user.id, call.message.chat.id)

    bot.send_message(
        call.message.chat.id,
        'Cancelled. Press "Registration" to start again.',
        reply_markup=registration_kb
    )

    bot.answer_callback_query(call.id)


if __name__ == "__main__":
    print('Bot is running...')
    bot.infinity_polling()