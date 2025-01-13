from aiogram import Bot, Dispatcher, executor, types
import asyncio
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import API
from crud_functions import get_all_products, is_included, add_user


api = API
bot = Bot(token=api)
dp = Dispatcher(bot,storage=MemoryStorage())


kb = ReplyKeyboardMarkup(
    keyboard = [
        [
            KeyboardButton(text='Рассчитать'),
            KeyboardButton(text='Информация'),
            KeyboardButton(text='Купить'),
            KeyboardButton(text='Регистрация')
        ]
    ], resize_keyboard=True)

inline_kb = InlineKeyboardMarkup(resize_keyboard=True)
inline_button1 = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
inline_button2 = InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')
inline_kb.add(inline_button1)
inline_kb.add(inline_button2)

inline_menu = InlineKeyboardMarkup(resize_keyboard=True)
menu_button1 = InlineKeyboardButton(text = 'Product1',callback_data= 'product_buying')
menu_button2 = InlineKeyboardButton(text = 'Product2',callback_data= 'product_buying')
menu_button3 = InlineKeyboardButton(text = 'Product3',callback_data= 'product_buying')
menu_button4 = InlineKeyboardButton(text = 'Product4',callback_data= 'product_buying')
inline_menu.row(menu_button1, menu_button2, menu_button3, menu_button4)

products = get_all_products()

class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()

@dp.message_handler(commands = ['start'])
async def start_message(message):
    await message.answer("Привет! Я бот, помогающий твоему здоровью", reply_markup = kb)


@dp.message_handler(text = 'Рассчитать')
async def main_menu(message):
    await message.answer('Выберите опцию:', reply_markup = inline_kb)

@dp.message_handler(text = 'Купить')
async def get_buying_list(message):
    for products_id, title,description,price in products:
        await asyncio.sleep(1)
        with open(f'{products_id}.png', 'rb') as img:
            await message.answer(f'"Название: {title} | Описание: {description} | Цена: {price}"')
            await message.answer_photo(img)
            await asyncio.sleep(1)
    await message.answer("Выберите продукт для покупки:", reply_markup = inline_menu)

@dp.callback_query_handler(text = 'product_buying')
async def send_confirm_message(call):
    await call.message.answer("Вы успешно приобрели продукт!")

@dp.callback_query_handler(text='formulas')
async def get_formulas(call):
    await call.message.answer('10 x вес (кг) + 6,25 x рост (см) – 5 x возраст (г) – 161')


@dp.callback_query_handler(text='calories')
async def set_age(call):
    await call.message.answer('Введите свой возраст:')
    await UserState.age.set()
#
# @dp.message_handler()
# async def start_message(message):
#     await message.answer("Введите команду /start, чтобы начать общение.")

@dp.message_handler(state = UserState.age)
async def set_growth(message, state):
    await state.update_data(age_info = message.text)
    await message.answer('Введите свой рост:')
    await UserState.growth.set()

@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    await state.update_data(growth_info = message.text)
    await message.answer('Введите свой вес:')
    await UserState.weight.set()

@dp.message_handler(state=UserState.weight)
async def send_calories(message, state):
    await state.update_data(weight_info = message.text)
    data = await state.get_data()
    try:
        result = 10*int(data['weight_info']) + 6.25*int(data['growth_info']) - 5*int(data['age_info']) - 161
        await message.answer(f'Ваша норма калорий {result}')
    except:
        await message.answer(f'Пожалуйста, попробуйте заново. Для корректного расчета необходимо вводить только '
                             f'целые числа (без точек, запятых или пробелов)')
    finally:
        await state.finish()


class RegistrationState(StatesGroup):
    username = State()
    email = State()
    age = State()
    balance = 1000

@dp.message_handler(text='Регистрация')
async def sing_up(message):
    await message.answer("Введите имя пользователя (только латинский алфавит):")
    await RegistrationState.username.set()

@dp.message_handler(state=RegistrationState.username)
async def set_username(message, state):
    name = is_included(message.text)
    if name is False:
        await state.update_data(key_username=message.text)
        await message.answer("Введите свой email:" )
        await RegistrationState.email.set()
    else:
        await message.answer("Пользователь существует, введите другое имя" )
        await RegistrationState.username.set()

@dp.message_handler(state=RegistrationState.email)
async def set_email(message, state):
    await state.update_data(key_email = message.text)
    await message.answer("Введите свой возраст:")
    await RegistrationState.age.set()

@dp.message_handler(state=RegistrationState.age)
async def set_age(message, state):
    await state.update_data(key_age = message.text)
    new_user = await state.get_data()
    username = new_user['key_username']
    email = new_user['key_email']
    age = new_user['key_age']
    add_user(username, email, age)
    await message.answer(f"Регистрация пользователя прошла успешно")
    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)


