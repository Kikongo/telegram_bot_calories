from aiogram.fsm.state import State, StatesGroup

class Form(StatesGroup):
    weight = State()
    height = State()
    age = State()
    gender = State()
    activity = State()
    activity_type = State()
    city = State()

class FoodForm(StatesGroup):
    food_calories = State()
    food_consumed = State()