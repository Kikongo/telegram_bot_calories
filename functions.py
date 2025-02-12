# Пример поиска калорийности продукта. Работает так себе и ищет не то что нужно, но для нашего задания пойдет
import requests
from config import API_TOKEN
import json

def get_food_info(product_name):
    url = f"https://world.openfoodfacts.org/cgi/search.pl?action=process&search_terms={product_name}&json=true"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        products = data.get('products', [])
        if products:  # Проверяем, есть ли найденные продукты
            first_product = products[0]
            return {
                'name': first_product.get('product_name', 'Неизвестно'),
                'calories': first_product.get('nutriments', {}).get('energy-kcal_100g', 0)
            }
        return None
    print(f"Ошибка: {response.status_code}")
    return None

def calculate_calories(user):

    # MET (Metabolic Equivalent of Task) values for different intensities
    met_values = {
        "light": 3.0,      # Light walking, casual cycling, stretching
        "moderate": 5.0,   # Brisk walking, easy jogging, swimming
        "very active": 8.0    # Running, HIIT workouts, competitive sports
    }

    # Mifflin-St Jeor Equation for BMR
    if user['gender'].lower() == "male":
        bmr = 10 * int(user['weight']) + 6.25 * int(user['height']) - 5 * int(user['age']) + 5
    elif user['gender'].lower() == "female":
        bmr = 10 * int(user['weight']) + 6.25 * int(user['height']) - 5 * int(user['age']) - 161
    else:
        raise ValueError("Gender must be 'male' or 'female'")
    
    # Convert minutes to hours
    activity_hours = int(user['activity']) / 60.0

    # Calories burned from activity: MET × weight (kg) × time (hours)
    activity_calories = met_values[user['activity_type']] * int(user['weight']) * activity_hours

    calories = bmr + activity_calories
    return round(calories, 2)

def get_temperature(city):
    URL_temp = "https://api.openweathermap.org/data/2.5/weather"
    URL_geocode = "http://api.openweathermap.org/geo/1.0/direct"

    data_geo = {
    "q": city,
    "appid": API_TOKEN
    }
    
    r_geocode = requests.get(URL_geocode, params=data_geo)
    resp_geo = json.loads(r_geocode.text)
    lat = resp_geo[0]['lat']
    lon = resp_geo[0]['lon']

    data_temp = {
        "lat": lat,
        "lon": lon,
        "appid": API_TOKEN
    }

    r_temp = requests.get(URL_temp, params=data_temp)
    resp_temp = json.loads(r_temp.text)
    temp = resp_temp['main']['temp']
    temp_celsius = round(temp - 273.15, 2)
    
    return temp_celsius

def calculate_water(user):
    water_norm = int(user['weight']) * 30
    activity_multiplier = 0

    if int(user['activity']) > 30:
        activity_multiplier = round(int(user['activity']) / 30)
    
    temperature = get_temperature(user['city'])

    if temperature > 25:
        water_norm += 1000

    water_total = water_norm + 500 * activity_multiplier
    
    return water_total
