from aiogram import types
import available_goods as nal
import emoji

def main_keyboard():
    buttons = ['💎 Товары 💎', '💼 Гарант 💼' , '📇 Мой профиль 📇', '💵 Пополнить счет 💵', '🧑🏿‍🔧 Поддержка 🧑🏿‍🔧', '📝 Правила 📝']
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    keyboard.add(*buttons)
    return keyboard

def check_pay_keyboard():
    buttons = ['Проверить оплату', 'Отменить оплату']
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    keyboard.add(*buttons)
    return keyboard

def cancel_pay_keyboard():
    buttons = 'Отменить оплату'
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    keyboard.add(buttons)
    return keyboard

def none_keyboard():
    keyboard = types.ReplyKeyboardMarkup
    return keyboard


def adm_keyboard():
    buttons = ('Пополнение баланса', 'Снять с баланса', 'Проверить балансы', 'Снять с реф.баланса', 'Рассылка')
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    keyboard.add(*buttons)
    return keyboard

def adm_cancel_keyboard():
    buttons = 'Отмена'
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    keyboard.add(buttons)
    return keyboard

def cats_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    buttons = types.InlineKeyboardButton(text=f'{emoji.emojize(":scroll:")}Ключи Steam{emoji.emojize(":scroll:")}', callback_data='keys')

    keyboard.add(buttons)
    return keyboard

def keys_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    buttons = (types.InlineKeyboardButton(text=f'Ключи CSGO | {nal.available_CSGO()} шт', callback_data='CSGO_keys'),
               types.InlineKeyboardButton(text=f'Ключи Fences 3 | {nal.available_Fences()} шт', callback_data='Fenses_keys'),
               types.InlineKeyboardButton(text='Назад', callback_data='cancelorder')
               )
    keyboard.add(*buttons)
    return keyboard

def back_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    buttons = types.InlineKeyboardButton(text='Назад', callback_data='cancelorder')
    keyboard.add(buttons)
    return keyboard

def num_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=5)
    buttons = (types.InlineKeyboardButton(text='1', callback_data='1'),
               types.InlineKeyboardButton(text='2', callback_data='2'),
               types.InlineKeyboardButton(text='3', callback_data='3'),
               types.InlineKeyboardButton(text='4', callback_data='4'),
               types.InlineKeyboardButton(text='5', callback_data='5'),
               types.InlineKeyboardButton(text='6', callback_data='6'),
               types.InlineKeyboardButton(text='7', callback_data='7'),
               types.InlineKeyboardButton(text='8', callback_data='8'),
               types.InlineKeyboardButton(text='9', callback_data='9'),
               types.InlineKeyboardButton(text='10', callback_data='10'),
               types.InlineKeyboardButton(text='Ввести вручную', callback_data='manually_input')
               )
    button1 = types.InlineKeyboardButton(text='Назад', callback_data='cancelorder')
    keyboard.add(*buttons)
    keyboard.add(button1)
    return keyboard

def err_cancel_order_keyboard():
    buttons = 'Отменить заполнение заказа'
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(buttons)
    return keyboard

def ref_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    buttons = types.InlineKeyboardButton(text='Реферальная система', callback_data='ref')
    keyboard.add(buttons)
    return keyboard

def confirmorder_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    buttons = (types.InlineKeyboardButton(text='Подтвердить', callback_data='confirm'),
               types.InlineKeyboardButton(text='Отменить заказ', callback_data='cancelorder'))
    keyboard.add(*buttons)
    return keyboard