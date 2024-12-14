# Домашнее задание по теме "Написание примитивной ORM"
# Цель: написать простейшие CRUD функции для взаимодействия с базой данных.


from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from texts import *
from crud_functions import *

api_f = open('api.txt', 'r')
api = api_f.read()
bot = Bot(token=api)
api_f.close()
dp = Dispatcher(bot, storage=MemoryStorage())

kb = ReplyKeyboardMarkup(resize_keyboard=True)
button = KeyboardButton(text='Расчитать')
button2 = KeyboardButton(text='Информация')
button3 = KeyboardButton(text='Купить')
button4 = KeyboardButton(text='Регистрация')
kb.add(button4, button)
kb.add(button3, button2)

# Инлайн клавиатура для выбора каждого продукта
catalog_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text=get_all_products(1)[0][1], callback_data='product_buying')],
        [InlineKeyboardButton(text=get_all_products(2)[0][1], callback_data='product_buying')],
        [InlineKeyboardButton(text=get_all_products(3)[0][1], callback_data='product_buying')],
        [InlineKeyboardButton(text=get_all_products(4)[0][1], callback_data='product_buying')]
    ]
)


# Формирование надписи для описания продукта
def about_product(nomber_product):  #
    return (f'Название: {get_all_products(nomber_product)[0][1]} | '
            f'Описание: {get_all_products(nomber_product)[0][2]} '
            f'| Цена: {get_all_products(nomber_product)[0][3]}')


@dp.message_handler(text='Купить')
async def get_buying_list(message):
    await message.answer(about_product(1))
    with open('Product1.jpg', 'rb') as img1:
        await message.answer_photo(img1)

    await message.answer(about_product(2))
    with open('Product2.jpg', 'rb') as img2:
        await message.answer_photo(img2)

    await message.answer(about_product(3))
    with open('Product3.jpg', 'rb') as img3:
        await message.answer_photo(img3)

    await message.answer(about_product(4))
    with open('Product4.jpg', 'rb') as img4:
        await message.answer_photo(img4)

    await message.answer("Выберите продукт для покупки", reply_markup=catalog_kb)


ikb = InlineKeyboardMarkup(resize_keyboard=True)
ibutton1 = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
ibutton2 = InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')
ikb.add(ibutton1, ibutton2)


@dp.message_handler(text='Информация')
async def inf(message):
    with open('Info pictures.jpg', 'rb') as img:
        await message.answer_photo(img, about, reply_markup=kb)


@dp.callback_query_handler(text='product_buying')
async def send_confirm_message(call):
    await call.message.answer('Вы успешно приобрели продукт! ')
    await call.answer()


@dp.message_handler(commands=["start"])
async def start(message):
    await message.answer(hello, reply_markup=kb)


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


# Новый класс состояний
class RegistrationState(StatesGroup):
    username = State()
    email = State()
    age = State()
    balance = 1000


@dp.message_handler(text=['Регистрация'])
async def sihg_up(message):
    await message.answer('Введите имя пользователя (только латинский алфавит):')
    await RegistrationState.username.set()


# Регистрация
@dp.message_handler(state=RegistrationState.username)
async def set_username(message, state):
    if is_included(message.text):
        await state.update_data(username=message.text)
        await message.answer("Введите свой email:")
        await RegistrationState.email.set()
    else:
        await message.answer('Пользователь существует, введите другое имя')
        await RegistrationState.username.set()


# Ввод email
@dp.message_handler(state=RegistrationState.email)
async def set_email(message, state):
    await state.update_data(email=message.text)
    await message.answer("Введите свой возраст:")
    await RegistrationState.age.set()


# Ввод возраста
@dp.message_handler(state=RegistrationState.age)
async def set_age(message, state):
    await state.update_data(age=message.text)
    user_data = await state.get_data()
    add_user(user_data['username'], user_data['email'], user_data['age'])
    await message.answer(f"{user_data['username']} зарегистрирован")
    await state.finish()


@dp.message_handler(text='Расчитать')
async def main_menu(message):
    await message.answer('Выбрите опцию: ', reply_markup=ikb)


@dp.callback_query_handler(text='formulas')
async def get_formulas(call):
    await call.message.answer(calculation_formula)
    await call.answer()


@dp.callback_query_handler(text='calories')
async def set_age(call):
    await call.message.answer('Введите свой возраст (полных лет)')
    await call.answer()
    await UserState.age.set()


@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    await state.update_data(age=message.text)
    await message.answer('Введите свой рост, см')
    await UserState.growth.set()


@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    await state.update_data(growth=message.text)
    await message.answer('Введите свой вес, кг')
    await UserState.weight.set()


@dp.message_handler(state=UserState.weight)
async def send_calories(message, state):
    await state.update_data(weight=message.text)
    data = await state.get_data()
    try:
        calories = 10 * int(data['weight']) + 6.25 * int(data['growth']) - 5 * int(data['age']) + 5
        await message.answer(f'Ваши калории {calories}')
    except ValueError:
        await message.answer(
            'Данные введены некорректно. Введите числовые значения: полных лет, рост в сантиметрах, вес в килограммах')
    await state.finish()


@dp.message_handler()
async def all_message(message):
    await message.answer('Введите команду /start, чтобы начать общение.')


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
