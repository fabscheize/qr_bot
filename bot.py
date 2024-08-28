import telebot
from telebot import types
import qrcode
from token import token


bot = telebot.TeleBot(token)
FILE_NAME = 'qr_code.png'
CONTENT_TYPES = ["audio", "document", "photo", "sticker", "video", "video_note", "voice",
                 "location", "contact", "new_chat_members", "left_chat_member", "new_chat_title",
                 "new_chat_photo", "delete_chat_photo", "group_chat_created", "pinned_message",
                 "supergroup_chat_created", "channel_chat_created", "migrate_to_chat_id",
                 "migrate_from_chat_id"]

one_more_message = None


def create_qr(data):
    qr = qrcode.QRCode(box_size=20)
    qr.add_data(data)
    qr.make()
    img = qr.make_image()
    img.save(FILE_NAME)


@bot.message_handler(commands=['start'])
def bot_start(message):
    bot.send_message(
        message.chat.id, f'Привет, {message.from_user.username} 👋\n\
Пришли мне ссылку или текст, и я сгенерирую тебе QR-код 🤖')


@bot.message_handler(commands=['help'])
def bot_help(message):
    bot.send_message(
        message.chat.id, 'Просто пришли мне ссылку или текст, и я сгенерирую тебе QR-код 👇')


@bot.message_handler(content_types=['text'])
def get_message(message):
    global one_more_message
    create_qr(message.text)

    keyboard = types.InlineKeyboardMarkup(row_width=1)
    button = types.InlineKeyboardButton(
        text='Получить файл 📄', callback_data=FILE_NAME)
    keyboard.add(button)

    with open(FILE_NAME, 'rb') as photo:
        bot.send_photo(message.chat.id, photo, reply_markup=keyboard, caption='Готово 🎉\n\
Если хочешь получить QR-код в виде файла, нажми кнопку ниже ⬇️')
    one_more_message = bot.send_message(
        message.chat.id, 'Чтобы сгенерировать новый QR-код просто снова введи свой текст 👨🏻‍💻')


@bot.callback_query_handler(func=lambda callback: callback.data)
def check_callback(callback):
    global one_more_message
    if callback.data == FILE_NAME and one_more_message is not None:
        bot.delete_message(callback.message.chat.id, one_more_message.id)
        one_more_message = None

        with open(FILE_NAME, 'rb') as file:
            bot.send_document(callback.message.chat.id, file,
                              caption='Вот твой файл 💾')

        bot.send_message(callback.message.chat.id,
                         'Чтобы сгенерировать новый QR-код просто снова введи свой текст 👨🏻‍💻')


@bot.message_handler(func=lambda message: True, content_types=CONTENT_TYPES)
def default_command(message):
    bot.send_message(message.chat.id, 'Я не могу сделать из этого QR-код 😔')


bot.infinity_polling()
