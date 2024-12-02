from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio

api = ''
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())
kb = InlineKeyboardMarkup()
button1 = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
button2 = InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')
kb.add(button1, button2)


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


@dp.message_handler(commands='start')
async def start(message):
    await message.answer('Привет! Я бот помогающий твоему здоровью.')


@dp.message_handler(text='Рассчитать')
async def main_menu(message):
    await message.answer('Выберите опцию:', reply_markup=kb)


@dp.callback_query_handler(text='formulas')
async def get_formulas(call):
    await call.message.answer('10 х вес (кг) + 6,25 x рост (см) – 5 х возраст (г) + 5')


@dp.callback_query_handler(text='calories')
async def set_age(call):
    await call.message.answer('Введите свой возраст:')
    await UserState.age.set()


@dp.message_handler()
async def all_message(message):
    await message.answer('Введите команду /start, чтобы начать общение.')


@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    if not message.text.isdigit() or int(message.text) == 0:
        await message.answer('Введите положительное целое число!')
        return None
    await state.update_data(age=message.text)
    await message.answer('Введите свой рост, см:')
    await UserState.growth.set()


@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    if not message.text.isdigit() or int(message.text) == 0:
        await message.answer('Введите положительное целое число!')
        return None
    await state.update_data(growth=message.text)
    await message.answer('Введите свой вес, кг:')
    await UserState.weight.set()


@dp.message_handler(state=UserState.weight)
async def set_calories(message, state):
    if not message.text.isdigit() or int(message.text) == 0:
        await message.answer('Введите положительное целое число!')
        return None
    await state.update_data(weight=message.text)
    data = await state.get_data()
    calories = int(data['growth']) * 6.25 + int(data['weight']) * 10 - int(data['age']) * 5 + 5
    await message.answer(f'Ваша калорийность равна {calories} кал')
    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
