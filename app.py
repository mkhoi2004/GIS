from flask import Flask, jsonify, render_template, request
import requests
import time
from concurrent.futures import ThreadPoolExecutor
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv
import pandas as pd
import joblib
import os
from health_recommendations import get_health_recommendations, get_specific_group_recommendations

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key')  # Lấy từ .env hoặc mặc định
# Loại bỏ CSRFProtect vì endpoint /api/predict nhận JSON, không cần CSRF

# Kết nối MongoDB
client = MongoClient(os.getenv('MONGO_URI', 'mongodb+srv://Khoi:Minhkhoi2204%40%40@khoi.jqf2h.mongodb.net/'))
db = client['GIS']
collection = db['DataAQI']

locations = {
    "Vietnam": [
        {"name": "Hà Nội", "url": "https://api.waqi.info/feed/A476341/?token=e31f457d039504a9b5e5c087c41ce3bf604b755a", "lat": 21.0044, "lon": 105.8432, "population": 8500000, "area": 3358.6},
        {"name": "Vũng Tàu", "url": "https://api.waqi.info/feed/@14642/?token=e31f457d039504a9b5e5c087c41ce3bf604b755a", "lat": 10.346, "lon": 107.0843, "population": 570000, "area": 141.1},
        {"name": "Trà Vinh", "url": "https://api.waqi.info/feed/@13662/?token=e31f457d039504a9b5e5c087c41ce3bf604b755a", "lat": 9.9472, "lon": 106.342, "population": 160000, "area": 68.035},
        {"name": "Nha Trang", "url": "https://api.waqi.info/feed/@1585/?token=e31f457d039504a9b5e5c087c41ce3bf604b755a", "lat": 12.2388, "lon": 109.1967, "population": 450000, "area": 251},
        {"name": "Quảng Bình", "url": "https://api.waqi.info/feed/@14640/?token=e31f457d039504a9b5e5c087c41ce3bf604b755a", "lat": 17.4656, "lon": 106.6222, "population": 200000, "area": 155.54},
        {"name": "Thanh Hoá", "url": "https://api.waqi.info/feed/@14927/?token=e31f457d039504a9b5e5c087c41ce3bf604b755a", "lat": 19.807, "lon": 105.776, "population": 450000, "area": 149.5},
        {"name": "Lạng Sơn", "url": "https://api.waqi.info/feed/@13667/?token=e31f457d039504a9b5e5c087c41ce3bf604b755a", "lat": 21.8549, "lon": 106.7615, "population": 200000, "area": 79},
        {"name": "Cần Thơ", "url": "https://api.waqi.info/feed/@13687/?token=e31f457d039504a9b5e5c087c41ce3bf604b755a", "lat": 10.0452, "lon": 105.7469, "population": 1250000, "area": 1408.9},
        {"name": "Long An", "url": "https://api.waqi.info/feed/A476272/?token=e31f457d039504a9b5e5c087c41ce3bf604b755a", "lat": 10.5333, "lon": 106.4167, "population": 250000, "area": 81.95},
        {"name": "Bình Dương", "url": "https://api.waqi.info/feed/A476137/?token=e31f457d039504a9b5e5c087c41ce3bf604b755a", "lat": 11.3254, "lon": 106.477, "population": 2600000, "area": 118.9},
        {"name": "Tp Hồ Chí Minh", "url": "https://api.waqi.info/feed/@13756/?token=e31f457d039504a9b5e5c087c41ce3bf604b755a", "lat": 10.7769, "lon": 106.7009, "population": 9300000, "area": 2061.4},
        {"name": "Gia Lai", "url": "https://api.waqi.info/feed/@13762/?token=e31f457d039504a9b5e5c087c41ce3bf604b755a", "lat": 13.9833, "lon": 108.0000, "population": 300000, "area": 260.7},
        {"name": "Thừa Thiên Huế", "url": "https://api.waqi.info/feed/@12488/?token=e31f457d039504a9b5e5c087c41ce3bf604b755a", "lat": 16.4667, "lon": 107.5833, "population": 400000, "area": 70.67},
        {"name": "Nghệ An", "url": "https://api.waqi.info/feed/@13666/?token=e31f457d039504a9b5e5c087c41ce3bf604b755a", "lat": 18.6667, "lon": 105.6667, "population": 350000, "area": 104.97},
        {"name": "Ninh Bình", "url": "https://api.waqi.info/feed/@13763/?token=e31f457d039504a9b5e5c087c41ce3bf604b755a", "lat": 20.2500, "lon": 105.9667, "population": 200000, "area": 48.4},
        {"name": "Sơn La", "url": "https://api.waqi.info/feed/@13663/?token=e31f457d039504a9b5e5c087c41ce3bf604b755a", "lat": 21.3167, "lon": 103.9167, "population": 150000, "area": 324.9},
        {"name": "Hưng Yên", "url": "https://api.waqi.info/feed/A476158/?token=e31f457d039504a9b5e5c087c41ce3bf604b755a", "lat": 20.6464, "lon": 106.0511, "population": 250000, "area": 76.5},
        {"name": "Việt Trì", "url": "https://api.waqi.info/feed/@5506/?token=e31f457d039504a9b5e5c087c41ce3bf604b755a", "lat": 21.3010, "lon": 105.4010, "population": 300000, "area": 111.2},
        {"name": "Thái Nguyên", "url": "https://api.waqi.info/feed/@13027/?token=e31f457d039504a9b5e5c087c41ce3bf604b755a", "lat": 21.5928, "lon": 105.8442, "population": 350000, "area": 189.9},
        {"name": "Quảng Ninh", "url": "https://api.waqi.info/feed/@13445/?token=e31f457d039504a9b5e5c087c41ce3bf604b755a", "lat": 20.9511, "lon": 107.0789, "population": 650000, "area": 1119.1},
        {"name": "Bắc Giang", "url": "https://api.waqi.info/feed/A476293/?token=e31f457d039504a9b5e5c087c41ce3bf604b755a", "lat": 21.2732, "lon": 106.1947, "population": 300000, "area": 67.8},
        {"name": "Thái Bình", "url": "https://api.waqi.info/feed/A476842/?token=e31f457d039504a9b5e5c087c41ce3bf604b755a", "lat": 20.4467, "lon": 106.3366, "population": 250000, "area": 78.7},
        {"name": "Đà Nẵng", "url": "https://api.waqi.info/feed/@13658/?token=e31f457d039504a9b5e5c087c41ce3bf604b755a", "lat": 16.0600, "lon": 108.2208, "population": 1200000, "area": 1285.4},
        {"name": "Quảng Nam", "url": "https://api.waqi.info/feed/A476308/?token=e31f457d039504a9b5e5c087c41ce3bf604b755a", "lat": 15.5678, "lon": 108.4792, "population": 300000, "area": 92.8},
        {"name": "Bình Định", "url": "https://api.waqi.info/feed/A520996/?token=e31f457d039504a9b5e5c087c41ce3bf604b755a", "lat": 13.7765, "lon": 109.2237, "population": 350000, "area": 284.3},
        {"name": "Khánh Hòa", "url": "https://api.waqi.info/feed/A521008/?token=e31f457d039504a9b5e5c087c41ce3bf604b755a", "lat": 12.2500, "lon": 109.1833, "population": 450000, "area": 251},
        {"name": "Lâm Đồng", "url": "https://api.waqi.info/feed/A476452/?token=e31f457d039504a9b5e5c087c41ce3bf604b755a", "lat": 11.9404, "lon": 108.4585, "population": 300000, "area": 394.3},
        {"name": "Bình Phước", "url": "https://api.waqi.info/feed/A469792/?token=e31f457d039504a9b5e5c087c41ce3bf604b755a", "lat": 11.4833, "lon": 106.9167, "population": 250000, "area": 167.5},
        {"name": "Ninh Thuận", "url": "https://api.waqi.info/feed/A476314/?token=e31f457d039504a9b5e5c087c41ce3bf604b755a", "lat": 11.5667, "lon": 108.9833, "population": 200000, "area": 79.2}
    ],
    "Denmark": [
        {"name": "H.C. Ørsted Institutet", "url": "https://api.waqi.info/feed/@8568/?token=e31f457d039504a9b5e5c087c41ce3bf604b755a", "lat": 55.6969, "lon": 12.5596, "population": 650000, "area": 243.6},
        {"name": "Risø", "url": "https://api.waqi.info/feed/@3318/?token=e31f457d039504a9b5e5c087c41ce3bf604b755a", "lat": 55.6931, "lon": 12.099, "population": 90000, "area": 66.2},
        {"name": "Hedevej, Frederiks", "url": "https://api.waqi.info/feed/A412219/?token=e31f457d039504a9b5e5c087c41ce3bf604b755a", "lat": 55.5667, "lon": 11.4167, "population": 45000, "area": 78.9},
        {"name": "H.C.Andersens Boulevard", "url": "https://api.waqi.info/feed/@3317/?token=e31f457d039504a9b5e5c087c41ce3bf604b755a", "lat": 55.6759, "lon": 12.5727, "population": 650000, "area": 243.6},
        {"name": "Møllebjergvej, Rudkøbing", "url": "https://api.waqi.info/feed/A513088/?token=e31f457d039504a9b5e5c087c41ce3bf604b755a", "lat": 54.9404, "lon": 10.7096, "population": 4500, "area": 290.5},
        {"name": "Udsigten, Morud", "url": "https://api.waqi.info/feed/A247267/?token=e31f457d039504a9b5e5c087c41ce3bf604b755a", "lat": 55.2667, "lon": 10.5167, "population": 1500, "area": 324.3},
        {"name": "Vardevej, Tarm", "url": "https://api.waqi.info/feed/A102532/?token=e31f457d039504a9b5e5c087c41ce3bf604b755a", "lat": 55.9083, "lon": 8.5194, "population": 4000, "area": 1474},
        {"name": "Midtvej, Hobro", "url": "https://api.waqi.info/feed/A422296/?token=e31f457d039504a9b5e5c087c41ce3bf604b755a", "lat": 56.6431, "lon": 9.7939, "population": 12000, "area": 795},
        {"name": "Kjærslund, Aarhus", "url": "https://api.waqi.info/feed/A532795/?token=e31f457d039504a9b5e5c087c41ce3bf604b755a", "lat": 56.1567, "lon": 10.2108, "population": 360000, "area": 468},
        {"name": "Møllen, Skanderborg", "url": "https://api.waqi.info/feed/A529471/?token=e31f457d039504a9b5e5c087c41ce3bf604b755a", "lat": 56.0349, "lon": 9.9272, "population": 20000, "area": 416.6},
        {"name": "Bøgehegnet, Greve Strand", "url": "https://api.waqi.info/feed/A74383/?token=e31f457d039504a9b5e5c087c41ce3bf604b755a", "lat": 55.5833, "lon": 12.3000, "population": 50000, "area": 64.7},
        {"name": "Rådhus, Odense", "url": "https://api.waqi.info/feed/A503839/?token=e31f457d039504a9b5e5c087c41ce3bf604b755a", "lat": 55.3962, "lon": 10.3883, "population": 205000, "area": 324.3},
        {"name": "Østerbro, Aalborg", "url": "https://api.waqi.info/feed/A503833/?token=e31f457d039504a9b5e5c087c41ce3bf604b755a", "lat": 57.0488, "lon": 9.9217, "population": 220000, "area": 294.5}
    ]
}

# Cache để giảm tải API
cache = {}
CACHE_DURATION = 3600  # 1 giờ

def fetch_city_data(city, country):
    current_time = time.time()
    if city['name'] in cache and (current_time - cache[city['name']]['timestamp']) < CACHE_DURATION:
        return cache[city['name']]['data']
    try:
        response = requests.get(city['url'], timeout=10)
        response.raise_for_status()
        data = response.json()
        aqi = data['data']['aqi'] if data['status'] == 'ok' else None
        pollutants = data['data']['iaqi'] if data['status'] == 'ok' and 'iaqi' in data['data'] else {}
        pm25 = pollutants.get('pm25', {}).get('v', None)
        pm10 = pollutants.get('pm10', {}).get('v', None)
        no2 = pollutants.get('no2', {}).get('v', None)
        co = pollutants.get('co', {}).get('v', None)
        o3 = pollutants.get('o3', {}).get('v', None)
        so2 = pollutants.get('so2', {}).get('v', None)
        humidity = pollutants.get('h', {}).get('v', None)
        temperature = pollutants.get('t', {}).get('v', None)
        wind = pollutants.get('w', {}).get('v', None)
        update_time = data['data']['time']['s'] if data['status'] == 'ok' and 'time' in data['data'] else None

        city_data = {
            'name': city['name'],
            'country': country,
            'aqi': aqi,
            'pm25': pm25,
            'pm10': pm10,
            'no2': no2,
            'co': co,
            'o3': o3,
            'so2': so2,
            'humidity': humidity,
            'temperature': temperature,
            'wind': wind,
            'update_time': update_time,
            'lat': city['lat'],
            'lon': city['lon'],
            'population': city['population'],
            'area': city['area'],
            'saved_at': datetime.now().strftime('%H:%M %d/%m/%Y')
        }

        # Lưu vào cache
        cache[city['name']] = {'data': city_data, 'timestamp': current_time}
        # Lưu vào MongoDB
        collection.insert_one(city_data.copy())
        return city_data
    except Exception as e:
        print(f"Error fetching data for {city['name']}: {str(e)}")
        city_data = {
            'name': city['name'],
            'country': country,
            'aqi': None,
            'pm25': None,
            'pm10': None,
            'no2': None,
            'co': None,
            'o3': None,
            'so2': None,
            'humidity': None,
            'temperature': None,
            'wind': None,
            'update_time': None,
            'lat': city['lat'],
            'lon': city['lon'],
            'population': city['population'],
            'area': city['area'],
            'saved_at': datetime.now().strftime('%H:%M %d/%m/%Y')
        }
        collection.insert_one(city_data.copy())
        return city_data

API_KEY = os.getenv('API_KEY')
api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}" if API_KEY else None

@app.route('/chat', methods=['POST'])
def chat():
    if not API_KEY:
        return jsonify({'error': 'API key not configured'}), 500
    try:
        user_message = request.json.get("message")
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400

        data = {"contents": [{"parts": [{"text": user_message}]}]}
        headers = {"Content-Type": "application/json"}
        response = requests.post(api_url, headers=headers, json=data)

        if response.status_code == 200:
            chat_response = response.json()
            return jsonify({"response": chat_response['candidates'][0]['content']['parts'][0]['text']})
        else:
            return jsonify({'error': f"API error: {response.status_code} - {response.text}"}), 500
    except Exception as e:
        print(f"Chat error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/aqi', methods=['GET'])
def get_aqi_data():
    result = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        for country, cities in locations.items():
            futures = [executor.submit(fetch_city_data, city, country) for city in cities]
            for city, future in zip(cities, futures):
                try:
                    aqi_data = future.result()
                    result.append(aqi_data)
                except Exception as e:
                    print(f"Error processing {city['name']}: {str(e)}")
    return jsonify(result)

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/')
def health_evaluation():
    return render_template('health_evaluation.html')

# Tải mô hình và bộ tiền xử lý
try:
    model = joblib.load('health_risk_model.pkl')
    preprocessor = joblib.load('preprocessor.pkl')
except FileNotFoundError as e:
    print(f"Model loading error: {str(e)}")
    model = None
    preprocessor = None

@app.route('/api/predict', methods=['POST'])
def predict():
    if model is None or preprocessor is None:
        return jsonify({'error': 'Model or preprocessor not loaded'}), 500

    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No input data provided'}), 400

        # Lấy dữ liệu từ request
        features = ['pm25', 'pm10', 'no2', 'co', 'o3', 'so2', 'humidity', 'temperature', 'wind']
        input_values = [
            float(data.get(feature)) if data.get(feature) not in (None, '') else None
            for feature in features
        ]

        # Kiểm tra xem có ít nhất một giá trị hợp lệ
        if all(val is None for val in input_values):
            return jsonify({'error': 'At least one input value must be provided'}), 400

        # Tạo DataFrame
        input_data = pd.DataFrame([input_values], columns=features)

        # Tiền xử lý và dự đoán
        input_processed = preprocessor.transform(input_data)
        risk_level = int(model.predict(input_processed)[0])
        risk_probs = model.predict_proba(input_processed)[0].tolist()

        # Tính AQI
        calculated_aqi = calculate_aqi(
            input_values[0], input_values[1], input_values[2],
            input_values[3], input_values[4], input_values[5]
        )

        # Lấy khuyến nghị
        recommendations = get_health_recommendations(risk_level)
        specific_recommendations = get_specific_group_recommendations(calculated_aqi if calculated_aqi is not None else 0)

        response = {
            'risk_level': risk_level,
            'risk_name': recommendations['risk_name'],
            'color': recommendations['color'],
            'description': recommendations['description'],
            'health_effects': recommendations['health_effects'],
            'recommendations': recommendations['recommendations'],
            'specific_recommendations': recommendations['specific_recommendations'],
            'specific_group_recommendations': specific_recommendations,
            'risk_probabilities': risk_probs,
            'calculated_aqi': round(calculated_aqi, 1) if calculated_aqi is not None else None
        }

        return jsonify(response)

    except ValueError as e:
        print(f"Prediction error: {str(e)}")
        return jsonify({'error': f'Invalid input data: {str(e)}'}), 400
    except Exception as e:
        print(f"Prediction error: {str(e)}")
        return jsonify({'error': f'Prediction failed: {str(e)}'}), 500

def calculate_aqi(pm25, pm10, no2, co, o3, so2):
    """Tính AQI dựa trên các chất ô nhiễm, lấy giá trị cao nhất."""
    aqi_values = []

    # PM2.5
    if pm25 is not None:
        if pm25 <= 12:
            aqi = (50 / 12) * pm25
        elif pm25 <= 35.4:
            aqi = 50 + (50 / (35.4 - 12)) * (pm25 - 12)
        elif pm25 <= 55.4:
            aqi = 100 + (50 / (55.4 - 35.4)) * (pm25 - 35.4)
        elif pm25 <= 150.4:
            aqi = 150 + (50 / (150.4 - 55.4)) * (pm25 - 55.4)
        elif pm25 <= 250.4:
            aqi = 200 + (100 / (250.4 - 150.4)) * (pm25 - 150.4)
        else:
            aqi = 300 + (200 / (500.4 - 250.4)) * min(pm25 - 250.4, 250)
        aqi_values.append(aqi)

    # PM10 - FIX: Sửa lại công thức tính
    if pm10 is not None:
        if pm10 <= 54:
            aqi = (50 / 54) * pm10
        elif pm10 <= 154:
            aqi = 50 + (50 / (154 - 54)) * (pm10 - 54)
        elif pm10 <= 254:
            aqi = 100 + (50 / (254 - 154)) * (pm10 - 154)
        elif pm10 <= 354:
            aqi = 150 + (50 / (354 - 254)) * (pm10 - 254)  # FIX: Sửa từ (pm10 - 154)
        elif pm10 <= 424:
            aqi = 200 + (100 / (424 - 354)) * (pm10 - 354)
        else:
            aqi = 300 + (200 / (604 - 424)) * min(pm10 - 424, 180)
        aqi_values.append(aqi)

    # NO2
    if no2 is not None:
        if no2 <= 53:
            aqi = (50 / 53) * no2
        elif no2 <= 100:
            aqi = 50 + (50 / (100 - 53)) * (no2 - 53)
        elif no2 <= 360:
            aqi = 100 + (50 / (360 - 100)) * (no2 - 100)
        elif no2 <= 649:
            aqi = 150 + (50 / (649 - 360)) * (no2 - 360)
        elif no2 <= 1249:
            aqi = 200 + (100 / (1249 - 649)) * (no2 - 649)
        else:
            aqi = 300 + (200 / (2049 - 1249)) * min(no2 - 1249, 800)
        aqi_values.append(aqi)

    # CO
    if co is not None:
        if co <= 4.4:
            aqi = (50 / 4.4) * co
        elif co <= 9.4:
            aqi = 50 + (50 / (9.4 - 4.4)) * (co - 4.4)
        elif co <= 12.4:
            aqi = 100 + (50 / (12.4 - 9.4)) * (co - 9.4)
        elif co <= 15.4:
            aqi = 150 + (50 / (15.4 - 12.4)) * (co - 12.4)
        elif co <= 30.4:
            aqi = 200 + (100 / (30.4 - 15.4)) * (co - 15.4)
        else:
            aqi = 300 + (200 / (50.4 - 30.4)) * min(co - 30.4, 20)
        aqi_values.append(aqi)

    # O3
    if o3 is not None:
        if o3 <= 54:
            aqi = (50 / 54) * o3
        elif o3 <= 70:
            aqi = 50 + (50 / (70 - 54)) * (o3 - 54)
        elif o3 <= 85:
            aqi = 100 + (50 / (85 - 70)) * (o3 - 70)
        elif o3 <= 105:
            aqi = 150 + (50 / (105 - 85)) * (o3 - 85)
        elif o3 <= 200:
            aqi = 200 + (100 / (200 - 105)) * (o3 - 105)
        else:
            aqi = 300 + (200 / (300 - 200)) * min(o3 - 200, 100)
        aqi_values.append(aqi)

    # SO2
    if so2 is not None:
        if so2 <= 35:
            aqi = (50 / 35) * so2
        elif so2 <= 75:
            aqi = 50 + (50 / (75 - 35)) * (so2 - 35)
        elif so2 <= 185:
            aqi = 100 + (50 / (185 - 75)) * (so2 - 75)
        elif so2 <= 304:
            aqi = 150 + (50 / (304 - 185)) * (so2 - 185)
        elif so2 <= 604:
            aqi = 200 + (100 / (604 - 304)) * (so2 - 304)
        else:
            aqi = 300 + (200 / (1004 - 604)) * min(so2 - 604, 400)
        aqi_values.append(aqi)

    return max(aqi_values) if aqi_values else None

@app.route('/')
@app.route('/DuDoan')
def DuDoan():
    return render_template('DuDoan.html')

if __name__ == '__main__':
    try:
        app.run(debug=True)
    except Exception as e:
        print(f"Error during application startup: {str(e)}")