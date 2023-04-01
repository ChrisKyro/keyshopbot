from aiogram import Bot, Dispatcher, executor, types, exceptions
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import aiogram.utils.markdown as fmt
import logging
import requests
import random

from botdb import botdb
import keyboards as kb
import available_goods as av


def summ_isdigit(summa):
    return summa.isdigit()


def payment_history_last(my_login, api_access_token, rows_num, next_TxnId, next_TxnDate):
    s = requests.Session()
    s.headers['authorization'] = 'Bearer ' + api_access_token
    parameters = {'rows': rows_num, 'nextTxnId': next_TxnId, 'nextTxnDate': next_TxnDate}
    h = s.get('https://edge.qiwi.com/payment-history/v2/persons/' + my_login + '/payments', params = parameters)
    return h.json()

def check_opl(summa, comment):
    global mylogin
    global api_access_token
    lastPayments = payment_history_last(mylogin, api_access_token, '5', '', '')
    datalist = lastPayments['data']
    for payment in datalist:
        if payment['status'] == 'SUCCESS' and payment['type'] == 'IN' and payment['sum']['amount'] == summa and payment['comment'] == comment:
            return True

def makeorder(number, comment, filename):
    with open(f'./goods/{filename}.txt', 'r+') as f:
        lines = f.readlines()
        f.close()
    with open(f'./orders/order{comment}.txt', 'w') as o:
        o.writelines(lines[0:number])
        o.close()
    with open(f'./goods/{filename}.txt', 'w') as f:
        f.writelines(lines[number:])
        f.close()


mylogin = ''
api_access_token = ''


botdb = botdb(f'./database/keyshopdb.db')


bot_token = ''

bot = Bot(token=bot_token)
dp = Dispatcher(bot, storage=MemoryStorage())
logging.basicConfig(level=logging.INFO)

class summbalance(StatesGroup):
    waiting_for_payment = State()
    check_payment = State()

class admbalance(StatesGroup):
    mention = State()
    value = State()

class admmailing(StatesGroup):
    wait_for_message = State()

class admbalancemin(StatesGroup):
    mention = State()
    value = State()

class admrefbalancemin(StatesGroup):
    mention = State()
    value = State()

class admcheckbalance(StatesGroup):
    id = State()

class order(StatesGroup):
    wait_for_good = State()
    wait_for_num = State()
    wait_for_manually = State()
    confirm_order = State()

'''ГЛАВНОЕ МЕНЮ, ПОПОЛНЕНИЕ БАЛАНСА'''

@dp.message_handler(commands='start')
async def welcome(message: types.message):
    if message.get_args() == '':
        ref_code = 0
    else:
        ref_code = int(message.get_args())
    await message.answer(
        fmt.text(
            fmt.text('Привет, друг!✋'),
            fmt.text('Сейчас ты пользуешься демо-версией нашего нового шопа'),
            fmt.text('Если ты нашёл баг, или у тебя есть предложения по доработке шопа, пиши сюда - @GodDotCom'),
            fmt.text(),
            fmt.text('По нашей рефке ты можешь заработать 10% с каждого пополнения, так что дерзай помогать развитию шопа 👇'),
        sep='\n'),
    parse_mode='HTML', reply_markup=kb.ref_keyboard())
    if (not botdb.user_exists(message.from_user.id)):
        botdb.new_user(message.from_user.id, message.from_user.mention, ref_code)

@dp.message_handler(lambda message: message.text == '📇 Мой профиль 📇')
async def prifile(message: types.message):
    await message.answer(
        fmt.text(
            fmt.text(f'Провиль пользователя {message.from_user.mention}'),
            fmt.text(),
            fmt.text(f'Привет, {message.from_user.full_name}!'),
            fmt.text(f'Ты с нами с {botdb.get_regdate(message.from_user.id)}'),
            fmt.text(f'Твой ID: <code>{message.from_user.id}</code>'),
            fmt.text(),
            fmt.text(f'Баланс {botdb.check_balance(message.from_user.id)} рублей'),
            fmt.text(),
            fmt.text(f'Если ты ещё не знаком с нашей <b>реферальной системой</b>, то скорей сделай это. Денги за рефералов можно вывести на Qiwi 💵'),
            sep='\n'),
        parse_mode = 'HTML', reply_markup = kb.ref_keyboard())

@dp.message_handler(lambda message: message.text == '💼 Гарант 💼')
async def gatant(message: types.message):
    await message.answer(
        fmt.text(
            fmt.text('Гарант с комиссией всего 2%'),
            fmt.text(),
            fmt.text('По поводу услуг гаранта писать NONE'),
            sep='\n'),
        parse_mode = 'HTML')

@dp.message_handler(lambda message: message.text == '💵 Пополнить счет 💵')
async def addbalance(message: types.message):
    await message.answer('В демо-версии магазина нет пополнения счёта. На вашем балансе уже есть 1000р по умолчанию')

@dp.message_handler(state=summbalance.waiting_for_payment)
async def process_pay(message: types.message, state: FSMContext):
    if message.text == 'Отменить оплату':
        await message.answer('Оплата отменена', reply_markup=kb.main_keyboard())
        await state.finish()
    else:
        comment = random.randint(0, 1000000)
        if summ_isdigit(message.text) == True:
            async with state.proxy() as data:
                data['summa'] = message.text
                data['comment'] = comment
            await message.answer(
                fmt.text(
                    fmt.text('Пополните кошелёк на указанную сумму'),
                    fmt.text('Сумма и комментарий должны <b>полностью</b> совпадать'),
                    fmt.text('Номер, сумму и комментарий можно скопировать'),
                    fmt.text(),
                    fmt.text('Перевод по номеру на киви кошелёк'),
                    fmt.text('Номер: <code>79878020873</code>'),
                    fmt.text(f'Сумма: <code>{message.text}</code>'),
                    fmt.text(f'Комментарий: <code>{comment}</code>'),
                    sep='\n'),
                parse_mode='HTML', reply_markup=kb.check_pay_keyboard())
            await summbalance.next()
        else:
            await message.answer('Сумма пополнения должна быть целым числом. Введите значение повторно.')

@dp.message_handler(state = summbalance.check_payment)
async def check_pay(message: types.message, state: FSMContext):
    if message.text == 'Отменить оплату':
        await message.answer('Оплата отменена', reply_markup=kb.main_keyboard())
        await state.finish()
    elif message.text == 'Проверить оплату':
        async with state.proxy() as data:
            summa = int(data['summa'])
            comment = str(data['comment'])
        if check_opl(summa, comment) == True:
            await message.answer('Ура, оплата прошла 💵', reply_markup = kb.main_keyboard())
            botdb.change_balance(message.from_user.id, summa)
            botdb.new_payment(message.from_user.id, summa)
            await state.finish()
            ref_id = botdb.get_ref(message.from_user.id)
            if ref_id != 0:
                ref_summa = int(summa/100)*10
                botdb.change_balance(ref_id, ref_summa)
                botdb.change_ref_balance(ref_id, ref_summa)
        else:
            await message.answer('Оплата не прошла 😕')
    else:
        await  message.answer('Я вас не понимаю, используйте кнопки')

'''РЕФЕРАЛЬНАЯ СИСТЕМА'''

@dp.callback_query_handler(text = 'ref')
async def ref(callback: types.CallbackQuery):
    await callback.message.answer(
        fmt.text(
            fmt.text('По нашей реферальной системе ты можешь заработать 10% с каждого пополнения реферала 💵'),
            fmt.text('Вывод от <b>200 рублей</b> на киви'),
            fmt.text('По поводу вывода писать @GodDotCom'),
            fmt.text(),
            fmt.text(f'Твоя реферальная ссылка: t.me/DotComShopBot?start={callback.from_user.id}'),
            fmt.text(f'У тебя {botdb.ref_num(callback.from_user.id)} рефералов'),
            fmt.text(f'Они принесли вам {botdb.check_ref_balance(callback.from_user.id)} рублей'),
            sep='\n'),
        parse_mode='HTML', reply_markup=kb.main_keyboard())
    await callback.answer()

"""ПОДДЕРЖКА"""

@dp.message_handler(lambda message: message.text == '🧑🏿‍🔧 Поддержка 🧑🏿‍🔧')
async def support(message: types.message):
    await message.answer(
        fmt.text(
            fmt.text('Если у вас возникли проблемы, вопросы или предложения, мы всегда готовы ответить вам ☺️'),
            fmt.text(),
            fmt.text('Тех. поддержка, по любым вопросам: @GodDotCom'),
            sep='\n'),
        parse_mode='HTML')

'''ПРАВИЛА'''

@dp.message_handler(lambda message: message.text == '📝 Правила 📝')
async def rules(message: types.message):
    await message.answer('''Данный раздел временно недоступен''')

'''АДМИН ПАНЕЛЬ'''

@dp.message_handler(commands='adm')
async def adm(message: types.message):
    if botdb.check_admin(message.from_user.id) == True:
        await message.answer('Админ панель', reply_markup=kb.adm_keyboard())
    else:
        await message.answer('У вас нет прав админа', reply_markup=kb.main_keyboard())

@dp.message_handler(lambda message: message.text == 'Пополнение баланса')
async def addbalancef(message: types.message):
    if botdb.check_admin(message.from_user.id) == True:
        await message.answer('Введите id пользователя')
        await admbalance.mention.set()
    else:
        await message.answer('У вас нет прав админа', reply_markup=kb.main_keyboard())

@dp.message_handler(state = admbalance.mention)
async def admbalsumm(message: types.message, state: FSMContext):
    if botdb.check_admin(message.from_user.id) == True:
        async with state.proxy() as data:
            data['id'] = message.text
        await message.answer('Введите сумму')
        await admbalance.next()
    else:
        await message.answer('У вас нет прав админа', reply_markup=kb.main_keyboard())

@dp.message_handler(state = admbalance.value)
async def admbalsuccess(message: types.message, state: FSMContext):
    if botdb.check_admin(message.from_user.id) == True:
        async with state.proxy() as data:
            id = str(data['id'])
        value = int(message.text)
        await message.answer('Деньги зачислены на баланс', reply_markup=kb.main_keyboard())
        botdb.adm_change_balance(id, value)
        await state.finish()
    else:
        await message.answer('У вас нет прав админа', reply_markup=kb.main_keyboard())

@dp.message_handler(lambda message: message.text == 'Снять с баланса')
async def addbalancefmin(message: types.message):
    if botdb.check_admin(message.from_user.id) == True:
        await message.answer('Введите id пользователя')
        await admbalancemin.mention.set()
    else:
        await message.answer('У вас нет прав админа', reply_markup=kb.main_keyboard())

@dp.message_handler(state = admbalancemin.mention)
async def admbalsummmin(message: types.message, state: FSMContext):
    if botdb.check_admin(message.from_user.id) == True:
        async with state.proxy() as data:
            data['id'] = message.text
        await message.answer('Введите сумму')
        await admbalancemin.next()
    else:
        await message.answer('У вас нет прав админа', reply_markup=kb.main_keyboard())

@dp.message_handler(state = admbalancemin.value)
async def admbalsuccessmin(message: types.message, state: FSMContext):
    if botdb.check_admin(message.from_user.id) == True:
        async with state.proxy() as data:
            id = str(data['id'])
        value = int(message.text)
        await message.answer('Деньги сняты с баланса', reply_markup=kb.main_keyboard())
        botdb.change_balance_min(id, value)
        await state.finish()
    else:
        await message.answer('У вас нет прав админа', reply_markup=kb.main_keyboard())

@dp.message_handler(lambda message: message.text == 'Проверить балансы')
async def checkbalid(message: types.message):
    if botdb.check_admin(message.from_user.id) == True:
        await message.answer('Введите id пользователя')
        await admcheckbalance.id.set()
    else:
        await message.answer('У вас нет прав админа', reply_markup=kb.main_keyboard())

@dp.message_handler(state = admcheckbalance.id)
async def admcheckbal(message: types.message, state: FSMContext):
    if botdb.check_admin(message.from_user.id) == True:
        await message.answer(f'На балансе шопа: {botdb.check_balance(int(message.text))}. На реф балансе: {botdb.check_ref_balance(int(message.text))}', reply_markup=kb.main_keyboard())
        await state.finish()
    else:
        await message.answer('У вас нет прав админа', reply_markup=kb.main_keyboard())

@dp.message_handler(lambda message: message.text == 'Снять с реф.баланса')
async def addbalanceref(message: types.message):
    if botdb.check_admin(message.from_user.id) == True:
        await message.answer('Введите id пользователя')
        await admrefbalancemin.mention.set()
    else:
        await message.answer('У вас нет прав админа', reply_markup=kb.main_keyboard())

@dp.message_handler(state = admrefbalancemin.mention)
async def admbalsummref(message: types.message, state: FSMContext):
    if botdb.check_admin(message.from_user.id) == True:
        async with state.proxy() as data:
            data['id'] = message.text
        await message.answer('Введите сумму')
        await admrefbalancemin.next()
    else:
        await message.answer('У вас нет прав админа', reply_markup=kb.main_keyboard())

@dp.message_handler(state = admrefbalancemin.value)
async def admbalsuccessref(message: types.message, state: FSMContext):
    if botdb.check_admin(message.from_user.id) == True:
        async with state.proxy() as data:
            id = str(data['id'])
        value = int(message.text)
        await message.answer('Деньги сняты с реф. баланса', reply_markup=kb.main_keyboard())
        botdb.adm_minus_ref(id, value)
        await state.finish()
    else:
        await message.answer('У вас нет прав админа', reply_markup=kb.main_keyboard())

@dp.message_handler(lambda message: message.text == 'Рассылка')
async def admmessage(message: types.message):
    if botdb.check_admin(message.from_user.id) == True:
        await message.answer('Введите сообщение', reply_markup = kb.adm_cancel_keyboard())
        await admmailing.wait_for_message.set()
    else:
        await message.answer('У вас нет прав админа', reply_markup=kb.main_keyboard())

@dp.message_handler(state=admmailing.wait_for_message)
async def admsending(message: types.message, state: FSMContext):
    if botdb.check_admin(message.from_user.id) == True:
        if message.text == 'Отмена':
            await message.answer('Действие отменено', reply_markup = kb.main_keyboard())
            await state.finish()
        else:
            for person in botdb.get_all_userid():
                try:
                    await bot.send_message(chat_id=int(person[0]), text=message.text)
                except exceptions.ChatNotFound and exceptions.BotBlocked:
                    print('Такого чата нет, возможно его удалили')
            await message.answer('Рассылка прошла успешно', reply_markup=kb.main_keyboard())
            await state.finish()
    else:
        await message.answer('У вас нет прав админа', reply_markup=kb.main_keyboard())
        await state.finish()

"""ТОВАРЫ"""

@dp.message_handler(lambda message: message.text == '💎 Товары 💎')
async def cats(message: types.message):
    await message.answer('Выберите категорию', reply_markup = kb.cats_keyboard())

@dp.message_handler(state=order.wait_for_good)
async def error(message: types.message):
    await message.answer('Извините, но я вас не понимаю. Для начала закончите заполнение заказа или нажмите на кнопку "Назад"')

@dp.message_handler(state=order.wait_for_num)
async def error(message: types.message):
    await message.answer('Извините, но я вас не понимаю. Для начала закончите заполнение заказа или нажмите на кнопку "Назад"')

@dp.callback_query_handler(text = 'keys')
async def cat_str(callback: types.CallbackQuery):
    await callback.message.edit_text('Выберите товар', reply_markup=kb.keys_keyboard())
    await order.wait_for_good.set()
    await callback.answer()

@dp.callback_query_handler(state = order.wait_for_good, text = 'cancelorder')
async def back(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text('Выберите категорию', reply_markup=kb.cats_keyboard())
    await callback.answer()
    await state.finish()

@dp.callback_query_handler(state = order.wait_for_good, text = 'CSGO_keys')
async def bk_str(callback: types.CallbackQuery, state: FSMContext):
    if av.available_CSGO() <= 0:
        await callback.message.edit_text('К сожалению, данный товар закончился. Вы можете выбрать другой товар или дождаться пополнения', reply_markup = kb.cats_keyboard())
        await callback.answer()
        await state.finish()
    else:
        await order.next()
        await callback.message.edit_text(
            fmt.text(
                fmt.text('📇 Ключи CSGO 📇'),
                fmt.text('👌 Вы получите ключ с Prime 👌'),
                fmt.text(),
                fmt.text('Цена: 200 рублей за шт'),
                fmt.text(),
                fmt.text('Выберите количество:'),
                sep='\n'),
            parse_mode='HTML', reply_markup=kb.num_keyboard())
        await callback.answer()
        async with state.proxy() as data:
            data['good'] = 'Ключи CSGO'
            data['available'] = av.available_CSGO()

@dp.callback_query_handler(state = order.wait_for_good, text = 'Fenses_keys')
async def psk_str(callback: types.CallbackQuery, state: FSMContext):
    if av.available_Fences() <= 0:
        await callback.message.edit_text('К сожалению, данный товар закончился. Вы можете выбрать другой товар или дождаться пополнения', reply_markup = kb.cats_keyboard())
        await callback.answer()
        await state.finish()
    else:
        await order.next()
        await callback.message.edit_text('Вы получите ключ Fences 3\nВыберите количество', reply_markup=kb.num_keyboard())
        await callback.answer()
        async with state.proxy() as data:
            data['good'] = 'Ключи Fences'
            data['available'] = av.available_Fences()

@dp.callback_query_handler(state = order.wait_for_good)
async def inputerror(callback: types.CallbackQuery, state: FSMContext):
    if callback.data not in ('CSGO_keys', 'Fenses_keys'):
        await state.finish()
        await callback.message.edit_text(
            'Произошла ошибка ввода данных. Нам пришлось отменить составление формы заказа. Чтобы избежать подобных ошибок, не используйте два диалоговых окна для составления заказа одновременно',
            reply_markup=kb.cats_keyboard())
        await callback.answer()

@dp.callback_query_handler(state = order.wait_for_num)
async def wait_for_num(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == 'cancelorder':
        await callback.message.edit_text('Выберите категорию', reply_markup=kb.cats_keyboard())
        await callback.answer()
        await state.finish()
    elif callback.data == 'manually_input':
        await callback.message.edit_text('Введите количество')
        await callback.answer()
        await order.next()
    elif summ_isdigit(callback.data) == True:
        async with state.proxy() as data:
            data['num'] = str(callback.data)
            good = data['good']
            available = data['available']
        if int(available) >= int(callback.data):
            summ = int(callback.data)*botdb.get_price(good)
            async with state.proxy() as data:
                data['summ'] = summ
            await callback.message.edit_text(fmt.text(
                    fmt.text('<b>Заказ</b>'),
                    fmt.text(),
                    fmt.text(f'Товар: {good}'),
                    fmt.text(f'Количество: {str(callback.data)}'),
                    fmt.text(f'Общая стоимость: {summ} рублей'),
                    fmt.text(),
                    fmt.text('Если все данные верны, то просто подтвердите покупку'),
                    sep='\n'),
                parse_mode='HTML', reply_markup=kb.confirmorder_keyboard())
            await callback.answer()
            await order.confirm_order.set()
        else:
            await callback.message.edit_text(f'Вы ввели количество больше, чем есть у нас в наличии. Введите значение не более {str(available)}', reply_markup=kb.num_keyboard())
            await callback.answer()
    else:
        await state.finish()
        await callback.message.edit_text('Произошла ошибка ввода данных. Нам пришлось отменить составление формы заказа. Чтобы избежать подобных ошибок, не используйте два диалоговых окна для составления заказа одновременно', reply_markup=kb.cats_keyboard())
        await callback.answer()

@dp.message_handler(state=order.wait_for_manually)
async def wait_for_manually(message: types.message, state: FSMContext):
    if summ_isdigit(message.text) == True:
        async with state.proxy() as data:
            data['num'] = message.text
            good = data['good']
            available = data['available']
        if int(available) >= int(message.text):
            summ = int(message.text)*botdb.get_price(good)
            async with state.proxy() as data:
                data['summ'] = summ
            await message.answer(
                fmt.text(
                    fmt.text('<b>Заказ</b>'),
                    fmt.text(),
                    fmt.text(f'Товар: {good}'),
                    fmt.text(f'Количество: {message.text}'),
                    fmt.text(f'Общая стоимость: {summ} рублей'),
                    fmt.text(),
                    fmt.text('Если все данные верны, то просто подтвердите покупку'),
                    sep='\n'),
                parse_mode='HTML', reply_markup=kb.confirmorder_keyboard())
            await order.confirm_order.set()
        else:
            await message.answer(f'Вы ввели количество больше, чем есть у нас в наличии. Введите значение не более {str(available)}', reply_markup=kb.num_keyboard())
            await order.wait_for_num.set()
    else:
        await message.answer('Данные введены неверно. Введите целое число')

@dp.callback_query_handler(state = order.confirm_order)
async def confirm_order(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == 'cancelorder':
        await callback.message.edit_text('Выберите категорию', reply_markup=kb.cats_keyboard())
        await callback.answer()
        await state.finish()
    elif callback.data == 'confirm':
        async with state.proxy() as data:
            num = int(data['num'])
            good = str(data['good'])
            summ = data['summ']
        if summ > botdb.check_balance(callback.from_user.id):
            await callback.message.edit_text(f'Вам не хватает {summ - botdb.check_balance(callback.from_user.id)} рублей для оплаты заказа. Пополните баланс и повторите попытку', reply_markup=kb.cats_keyboard())
            await state.finish()
        else:
            await callback.message.edit_text('Подождите пару секунд, мы собираем ваш заказ ⏰')
            await callback.answer()
            botdb.change_balance_min(callback.from_user.id, summ)
            makeorder(num, str(callback.from_user.id), good)
            await callback.message.answer_document(types.InputFile(f'./orders/order{str(callback.from_user.id)}.txt'))
            await callback.message.answer('Спасибо за поддержку нашего магазина ❤')
            await state.finish()
    else:
        await state.finish()
        await callback.message.edit_text(
            'Произошла ошибка ввода данных. Нам пришлось отменить составление формы заказа. Чтобы избежать подобных ошибок, не используйте два диалоговых окна для составления заказа одновременно',
            reply_markup=kb.cats_keyboard())
        await callback.answer()

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)