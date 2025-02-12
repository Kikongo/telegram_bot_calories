from aiogram import Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from states import Form, FoodForm
import aiohttp
from functions import *

router = Router()

users = {
    "user_id": {
        "weight": 80,
        "height": 184,
        "age": 26,
        "gender": "Male",
        "activity": 45,
        "activity_type": "light",
        "city": "Paris",
        "water_goal": 0,
        "calorie_goal": 0,
        "logged_water": 0,
        "logged_calories": 0,
        "burned_calories": 0
    }
}

# Обработчик команды /start
@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.reply("Добро пожаловать! Я ваш бот.\nВведите /help для списка команд.")

# Обработчик команды /help
@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.reply(
        "Доступные команды:\n"
        "/start - Начало работы\n"
        "/set_profile - Данные пользователя\n"
        "/log_water - Логирование воды\n"
        "/log_food - Логирование еды\n"
        "/log_training - Логирование тренировок\n"
        "/check_progress - Прогресс пользователя\n"
        "/joke - Получить случайную шутку"
    )

# Обработчик команды /keyboard с инлайн-кнопками
@router.message(Command("keyboard"))
async def show_keyboard(message: Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Кнопка 1", callback_data="btn1")],
            [InlineKeyboardButton(text="Кнопка 2", callback_data="btn2")],
        ]
    )
    await message.reply("Выберите опцию:", reply_markup=keyboard)

@router.callback_query()
async def handle_callback(callback_query, state: FSMContext):
    if callback_query.data == "btn1":
        await callback_query.message.reply("Вы нажали Кнопка 1")
    elif callback_query.data == "btn2":
        await callback_query.message.reply("Вы нажали Кнопка 2")

    elif callback_query.data == "male_btn":
        await state.update_data(gender="Male")
        await process_gender(callback_query.message, state)
    elif callback_query.data == "female_btn":
        await state.update_data(gender="Female")
        await process_gender(callback_query.message, state)

    elif callback_query.data == "light_btn":
        await state.update_data(activity_type="light")
        await process_activity_type(callback_query.message, state)
    elif callback_query.data == "moderate_btn":
        await state.update_data(activity_type="moderate")
        await process_activity_type(callback_query.message, state)
    elif callback_query.data == "active_btn":
        await state.update_data(activity_type="very active")
        await process_activity_type(callback_query.message, state)

# FSM: диалог с пользователем
@router.message(Command("set_profile"))
async def set_profile(message: Message, state: FSMContext):
    await message.reply("Ваш вес (в кг)?")
    await state.set_state(Form.weight)

@router.message(Form.weight)
async def process_weight(message: Message, state: FSMContext):
    await state.update_data(weight=message.text)
    await message.reply("Какой у вас рост (в см)?")
    await state.set_state(Form.height)

@router.message(Form.height)
async def process_height(message: Message, state: FSMContext):
    await state.update_data(height=message.text)
    await message.reply("Какой у вас возраст?")
    await state.set_state(Form.age)

@router.message(Form.age)
async def process_age(message: Message, state: FSMContext):
    await state.update_data(age=message.text)
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Male", callback_data="male_btn")],
            [InlineKeyboardButton(text="Female", callback_data="female_btn")],
        ]
    )
    await message.reply("Выберите пол:", reply_markup=keyboard)

@router.message(Form.gender)
async def process_gender(message: Message, state: FSMContext):
    # await state.update_data(gender=message.text)
    await message.reply("Ваша активность в минутах?")
    await state.set_state(Form.activity)

@router.message(Form.activity)
async def process_activity(message: Message, state: FSMContext):
    await state.update_data(activity=message.text)
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="light", callback_data="light_btn")],
            [InlineKeyboardButton(text="moderate", callback_data="moderate_btn")],
            [InlineKeyboardButton(text="very active", callback_data="active_btn")],
        ]
    )
    await message.reply("Ваш тип активности:", reply_markup=keyboard)

@router.message(Form.activity_type)
async def process_activity_type(message: Message, state: FSMContext):
    # await state.update_data(activity_type=message.text)
    await message.reply("Ваш город?")
    await state.set_state(Form.city)

@router.message(Form.city)
async def process_city(message: Message, state: FSMContext):
    data = await state.get_data()
    weight = data.get("weight")
    height = data.get("height")
    age = data.get("age")
    gender = data.get("gender")
    activity = data.get("activity")
    activity_type = data.get("activity_type")
    city = message.text

    users['user_id']['weight'] = weight
    users['user_id']['height'] = height
    users['user_id']['age'] = age
    users['user_id']['gender'] = gender
    users['user_id']['activity'] = activity
    users['user_id']['activity_type'] = activity_type
    users['user_id']['city'] = city

    await state.update_data(city=city) # Сохраняем город
    await message.reply(f"Вес, {weight} кг! Рост {height} см. Пол {gender}. Активность {activity}. Город {city}")
    await state.clear()

# Получение шутки из API
@router.message(Command("joke"))
async def get_joke(message: Message):
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.chucknorris.io/jokes/random") as response:
            joke = await response.json()
            await message.reply(joke["value"])

# Логирование воды
@router.message(Command("log_water"))
async def log_water(message: Message):
    water_consumed = message.text.split(" ")[1]
    water_norm = calculate_water(users["user_id"])

    await message.reply(
        "Вода: \n"
        f"- Выпито: {water_consumed} мл из {water_norm} мл. \n"
        f"- Осталось: {int(water_norm) - int(water_consumed)} мл."
    )

    users["user_id"]['logged_water'] = water_consumed
    users["user_id"]['water_goal'] = water_consumed


# Логирование еды
@router.message(Command("log_food"))
async def log_food(message: Message, state: FSMContext):
    food = message.text.split(" ")[1]
    food_info = get_food_info(food)
    calories = food_info['calories']

    await message.reply(f"{food} - {calories} ккал на 100 гр. Сколько грамм вы съели?")

    await state.set_state(FoodForm.food_calories)
    await state.update_data(food_calories = calories)

@router.message(FoodForm.food_calories)
async def process_food(message: Message, state: FSMContext):
    data = await state.get_data()
    food_calories = data.get('food_calories')
    food_consumed = message.text

    calories = food_calories / 100 * int(food_consumed)
    calories = round(calories, 0)

    await message.reply(f"Записано: {calories} ккал.")

    users["user_id"]['logged_calories'] = calories
    await state.clear()

# Логирование тренировок
@router.message(Command("log_training"))
async def log_training(message: Message, command: CommandObject):
    training = command.args.split(" ")[0]
    minutes = command.args.split(" ")[1]
    burned_calories = 0
    rec_water = 0
    if int(minutes) > 10:    
        burned_calories = round(int(minutes) / 10) * 100
    
    if int(minutes) > 30:
        rec_water = round(int(minutes) / 30) * 200
    await message.reply(f"{training} {minutes} минут - {burned_calories} калорий. Дополнительно выпейте {rec_water} мл воды")

    users["user_id"]["burned_calories"] = burned_calories

# Прогресс по воде и калориям
@router.message(Command("check_progress"))
async def check_progress(message: Message):
    water_consumed = users["user_id"]["logged_water"]
    water_norm = calculate_water(users["user_id"])

    calories_consumed = users["user_id"]["logged_calories"]
    calories_burned = users["user_id"]["burned_calories"]
    calories_norm = calculate_calories(users["user_id"])
    
    await message.reply(
        "Прогресс: \n"
        "Вода: \n"
        f"- Выпито: {water_consumed} мл из {water_norm} мл. \n"
        f"- Осталось: {int(water_norm) - int(water_consumed)} мл. \n"
        "Калории: \n"
        f"- Потреблено: {calories_consumed} ккал из {calories_norm} ккал. \n"
        f"- Сожжено: {calories_burned} ккал. \n"
        f"- Баланс: {int(calories_norm) - int(calories_burned)} ккал. \n"
       
    )

    users["user_id"]["calorie_goal"] = calories_norm

# Функция для подключения обработчиков
def setup_handlers(dp):
    dp.include_router(router)
