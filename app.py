from flask import Flask, request, render_template, redirect, url_for, session, jsonify
from pymongo import MongoClient
import bcrypt
import os
from dotenv import load_dotenv
import requests
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import pandas as pd
import joblib
import math
import numpy as np
from health_recommendations import get_health_recommendations, get_specific_group_recommendations


# Tải biến môi trường từ file .env
load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key')

# Kết nối tới MongoDB
client = MongoClient(os.getenv('MONGO_URI', 'mongodb+srv://Khoi:Minhkhoi2204%40%40@khoi.jqf2h.mongodb.net/'))
db = client['GIS']
collection = db['DataAQI']
account_collection = db['Account']


# --- ĐĂNG NHẬP/ĐĂNG KÝ ---
@app.route('/index_admin')
def index_admin():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('index_admin.html')

@app.route('/index_user')
def index_user():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('health_evaluation.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        role = request.form['role']

        if not name or not password or not role:
            return render_template('register.html', error="Vui lòng điền đầy đủ thông tin")

        if account_collection.find_one({'name': name}):
            return render_template('register.html', error="Người dùng đã tồn tại")

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        account_collection.insert_one({'name': name, 'password': hashed_password, 'role': role})
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']

        user = account_collection.find_one({'name': name})
        if not user or not bcrypt.checkpw(password.encode('utf-8'), user['password']):
            return render_template('login.html', error="Tên đăng nhập hoặc mật khẩu không đúng")

        session['username'] = name
        if user['role'] == 'admin':
            return redirect(url_for('index_admin'))
        return redirect(url_for('index_user'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# Khối lượng mol của các chất ô nhiễm (g/mol)
MW = {
    'co': 28.01,
    'no2': 46.01,
    'o3': 48.00,
    'so2': 64.07
}

# Thể tích mol chuẩn (L/mol) ở điều kiện tiêu chuẩn (25°C, 1 atm)
MOLAR_VOLUME = 24.45

# Chuyển đổi đơn vị từ ug/m3 sang ppm và ppb
def ugm3_to_ppm(value_ugm3, mw):
    if value_ugm3 is None or mw is None or mw == 0:
        return None
    try:
        value_ppm = (float(value_ugm3) * MOLAR_VOLUME) / (mw * 1000)
        if math.isnan(value_ppm) or math.isinf(value_ppm):
            return None
        return value_ppm
    except (ValueError, TypeError):
        return None

def ugm3_to_ppb(value_ugm3, mw):
    value_ppm = ugm3_to_ppm(value_ugm3, mw)
    if value_ppm is None:
        return None
    try:
        value_ppb = value_ppm * 1000
        if math.isnan(value_ppb) or math.isinf(value_ppb):
            return None
        return value_ppb
    except (ValueError, TypeError):
        return None

# Danh sách các địa điểm và URL API tương ứng để lấy dữ liệu AQI
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

# Bộ nhớ đệm để lưu trữ dữ liệu AQI đã lấy
cache = {}
CACHE_DURATION = 3600

# Hàm lấy dữ liệu AQI cho một thành phố
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
            'population': city.get('population'),
            'area': city.get('area'),
            'saved_at': datetime.now().strftime('%H:%M %d/%m/%Y')
        }

        cache[city['name']] = {'data': city_data, 'timestamp': current_time}
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
            'population': city.get('population'),
            'area': city.get('area'),
            'saved_at': datetime.now().strftime('%H:%M %d/%m/%Y')
        }
        return city_data

API_KEY = os.getenv('API_KEY')
# URL của API Gemini
api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}" if API_KEY else None

# Route xử lý yêu cầu chat với Gemini API
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
            if 'candidates' in chat_response and len(chat_response['candidates']) > 0 and \
               'content' in chat_response['candidates'][0] and \
               'parts' in chat_response['candidates'][0]['content'] and len(chat_response['candidates'][0]['content']['parts']) > 0:
                return jsonify({"response": chat_response['candidates'][0]['content']['parts'][0]['text']})
            else:
                return jsonify({'error': 'Unexpected API response structure'}), 500
        else:
            return jsonify({'error': f"API error: {response.status_code} - {response.text}"}), 500
    except Exception as e:
        print(f"Chat error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Route lấy dữ liệu AQI cho tất cả các địa điểm
@app.route('/aqi', methods=['GET'])
def get_aqi_data():
    result = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures_map = {}
        for country, cities in locations.items():
            for city in cities:
                future = executor.submit(fetch_city_data, city, country)
                futures_map[future] = city['name']

        for future in futures_map:
            city_name = futures_map[future]
            try:
                aqi_data = future.result()
                if aqi_data and aqi_data.get('aqi') is not None:
                     result.append(aqi_data)
            except Exception as e:
                print(f"Error processing future for {city_name}: {str(e)}")
    return jsonify(result)

# Route hiển thị trang bản đồ chính
@app.route('/index')
def index():
    return render_template('index.html')

# Route hiển thị trang đánh giá sức khỏe (trang chủ mặc định)
@app.route('/')
def health_evaluation():
    return render_template('health_evaluation.html')

# Tải pipeline mô hình dự đoán đã được huấn luyện
pipeline = None
pipeline_features = []
try:
    pipeline = joblib.load('health_risk_pipeline.pkl')
    print("Đã tải thành công health_risk_pipeline.pkl")

    try:
        preprocessor_step = pipeline.named_steps.get('preprocessor')
        if preprocessor_step and hasattr(preprocessor_step, 'transformers_'):
            pipeline_features = preprocessor_step.transformers_[0][2]
            print(f"Pipeline mong đợi các features: {pipeline_features}")
        else:
            pipeline_features = ['pm25', 'pm10', 'no2', 'co', 'o3', 'so2', 'humidity', 'temperature', 'wind']
            print(f"Không lấy được features từ pipeline, sử dụng mặc định: {pipeline_features}")
    except Exception as e:
        pipeline_features = ['pm25', 'pm10', 'no2', 'co', 'o3', 'so2', 'humidity', 'temperature', 'wind']
        print(f"Lỗi khi lấy features từ pipeline ({e}), sử dụng mặc định: {pipeline_features}")

except FileNotFoundError:
    print("Lỗi: Không tìm thấy file 'health_risk_pipeline.pkl'.")
    pipeline = None
except Exception as e:
    print(f"Lỗi khi tải pipeline: {e}")
    pipeline = None

# Route API để dự đoán mức độ rủi ro sức khỏe
@app.route('/api/predict', methods=['POST'])
def predict():
    if pipeline is None:
        return jsonify({'error': 'Model pipeline is not loaded.'}), 500
    if not pipeline_features:
         return jsonify({'error': 'Pipeline features not determined.'}), 500

    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No input data provided'}), 400

        input_values_raw = {}
        input_units = {}
        pollutants_with_units = ['no2', 'co', 'o3', 'so2']
        other_features = ['pm25', 'pm10', 'humidity', 'temperature', 'wind']

        for feature in pollutants_with_units:
            val_str = data.get(feature)
            unit = data.get(f"{feature}_unit")
            valid_units = (['ppb', 'ugm3'] if feature != 'co' else ['ppm', 'ugm3'])
            input_units[feature] = unit if unit in valid_units else None
            try:
                input_values_raw[feature] = float(val_str) if val_str not in (None, '') else None
            except (ValueError, TypeError):
                input_values_raw[feature] = None

        for feature in other_features:
            val_str = data.get(feature)
            try:
                input_values_raw[feature] = float(val_str) if val_str not in (None, '') else None
            except (ValueError, TypeError):
                input_values_raw[feature] = None

        wind_unit = data.get('wind_unit')
        input_units['wind'] = wind_unit if wind_unit in ['ms', 'kmh'] else None

        aqi_input = {}
        aqi_input['pm25'] = input_values_raw.get('pm25')
        aqi_input['pm10'] = input_values_raw.get('pm10')

        co_raw = input_values_raw.get('co')
        co_unit = input_units.get('co')
        if co_raw is not None and co_unit == 'ugm3':
            aqi_input['co_ppm'] = ugm3_to_ppm(co_raw, MW.get('co'))
        elif co_raw is not None and co_unit == 'ppm':
            aqi_input['co_ppm'] = co_raw
        else:
            aqi_input['co_ppm'] = None

        for gas in ['no2', 'o3', 'so2']:
            raw_val = input_values_raw.get(gas)
            unit = input_units.get(gas)
            if raw_val is not None and unit == 'ugm3':
                aqi_input[f'{gas}_ppb'] = ugm3_to_ppb(raw_val, MW.get(gas))
            elif raw_val is not None and unit == 'ppb':
                aqi_input[f'{gas}_ppb'] = raw_val
            else:
                aqi_input[f'{gas}_ppb'] = None

        model_input_values = {}
        model_input_values['pm25'] = input_values_raw.get('pm25')
        model_input_values['pm10'] = input_values_raw.get('pm10')
        model_input_values['humidity'] = input_values_raw.get('humidity')
        model_input_values['temperature'] = input_values_raw.get('temperature')

        if co_raw is not None and co_unit == 'ugm3':
             model_input_values['co'] = ugm3_to_ppm(co_raw, MW.get('co'))
        elif co_raw is not None and co_unit == 'ppm':
             model_input_values['co'] = co_raw
        else:
             model_input_values['co'] = None

        for gas in ['no2', 'o3', 'so2']:
            raw_val = input_values_raw.get(gas)
            unit = input_units.get(gas)
            if raw_val is not None and unit == 'ugm3':
                model_input_values[gas] = ugm3_to_ppb(raw_val, MW.get(gas))
            elif raw_val is not None and unit == 'ppb':
                model_input_values[gas] = raw_val
            else:
                model_input_values[gas] = None

        wind_raw = input_values_raw.get('wind')
        wind_unit_local = input_units.get('wind')
        if wind_raw is not None:
            if wind_unit_local == 'kmh':
                model_input_values['wind'] = wind_raw / 3.6
            elif wind_unit_local == 'ms':
                model_input_values['wind'] = wind_raw
            else:
                 model_input_values['wind'] = None
        else:
            model_input_values['wind'] = None

        input_for_pipeline_list = []
        for f in pipeline_features:
            val = model_input_values.get(f)
            input_for_pipeline_list.append(float(val) if val is not None else np.nan)

        print("-" * 20)
        print(f"Received JSON data: {data}")
        print(f"Raw input values: {input_values_raw}")
        print(f"Input units: {input_units}")
        print(f"Values passed to calculate_aqi: pm25={aqi_input['pm25']}, pm10={aqi_input['pm10']}, no2_ppb={aqi_input['no2_ppb']}, co_ppm={aqi_input['co_ppm']}, o3_ppb={aqi_input['o3_ppb']}, so2_ppb={aqi_input['so2_ppb']}")
        print(f"Values for pipeline prediction (ordered by {pipeline_features}, NaN for missing): {input_for_pipeline_list}")

        pollutants_for_aqi_check = [aqi_input['pm25'], aqi_input['pm10'], aqi_input['no2_ppb'], aqi_input['co_ppm'], aqi_input['o3_ppb'], aqi_input['so2_ppb']]
        if not any(p is not None and not math.isnan(p) and not math.isinf(p) for p in pollutants_for_aqi_check):
             calculated_aqi = None
             print("    [predict] Not enough valid pollutant data to calculate AQI.")
        else:
            calculated_aqi = calculate_aqi(
                aqi_input['pm25'], aqi_input['pm10'], aqi_input['no2_ppb'],
                aqi_input['co_ppm'], aqi_input['o3_ppb'], aqi_input['so2_ppb']
            )
        print(f"Calculated AQI result: {calculated_aqi}")

        input_df = pd.DataFrame([input_for_pipeline_list], columns=pipeline_features)

        try:
            predicted_risk_level = int(pipeline.predict(input_df)[0])
            risk_probs_learned = pipeline.predict_proba(input_df)[0]
            risk_probs_full = np.zeros(6)
            learned_classes = pipeline.classes_
            for i, cls_label in enumerate(learned_classes):
                 if 0 <= cls_label < 6:
                     risk_probs_full[int(cls_label)] = risk_probs_learned[i]

            print(f"Predicted Risk Level (from model): {predicted_risk_level}")
            print(f"Predicted Probabilities (learned classes {learned_classes}): {risk_probs_learned}")
            print(f"Full Probabilities (0-5): {risk_probs_full.tolist()}")

        except Exception as model_err:
             print(f"Pipeline prediction error: {str(model_err)}")
             import traceback
             print(traceback.format_exc())
             return jsonify({'error': f'Lỗi trong quá trình dự đoán của pipeline: {str(model_err)}'}), 500

        print("-" * 20)

        model_recommendations = get_health_recommendations(predicted_risk_level)
        aqi_for_specific_groups = calculated_aqi if calculated_aqi is not None and not math.isnan(calculated_aqi) else 0
        specific_group_recommendations = get_specific_group_recommendations(aqi_for_specific_groups)

        response_data = {
            'predicted_risk_level': predicted_risk_level,
            'risk_name': model_recommendations['risk_name'],
            'description': model_recommendations['description'],
            'health_effects': model_recommendations['health_effects'],
            'recommendations': model_recommendations['recommendations'],
            'specific_recommendations': model_recommendations['specific_recommendations'],
            'calculated_aqi': round(calculated_aqi, 1) if calculated_aqi is not None else None,
            'risk_probabilities': risk_probs_full.tolist(),
            'specific_group_recommendations': specific_group_recommendations
        }

        return jsonify(response_data)

    except ValueError as e:
        print(f"Prediction error (ValueError): {str(e)}")
        return jsonify({'error': f'Dữ liệu đầu vào không hợp lệ: {str(e)}'}), 400
    except KeyError as e:
         print(f"Prediction error (KeyError): Missing key {str(e)}")
         return jsonify({'error': f'Thiếu dữ liệu đầu vào cần thiết: {str(e)}'}), 400
    except Exception as e:
        import traceback
        print(f"Prediction error (Exception): {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': f'Lỗi dự đoán không xác định: {str(e)}'}), 500

# Hàm tính toán chỉ số AQI tổng hợp từ các chỉ số thành phần
# Dựa trên công thức tính AQI của EPA Hoa Kỳ
def calculate_aqi(pm25, pm10, no2_ppb, co_ppm, o3_ppb, so2_ppb):
    aqi_values = []
    print(f"  [calculate_aqi] Inputs: pm25={pm25}, pm10={pm10}, no2_ppb={no2_ppb}, co_ppm={co_ppm}, o3_ppb={o3_ppb}, so2_ppb={so2_ppb}")

    def is_valid(value):
        return value is not None and not math.isnan(value) and not math.isinf(value)

    if is_valid(pm25):
        try:
            pm25_f = float(pm25)
            if pm25_f <= 12: aqi = (50 / 12) * pm25_f
            elif pm25_f <= 35.4: aqi = 50 + (50 / (35.4 - 12)) * (pm25_f - 12)
            elif pm25_f <= 55.4: aqi = 100 + (50 / (55.4 - 35.4)) * (pm25_f - 35.4)
            elif pm25_f <= 150.4: aqi = 150 + (50 / (150.4 - 55.4)) * (pm25_f - 55.4)
            elif pm25_f <= 250.4: aqi = 200 + (100 / (250.4 - 150.4)) * (pm25_f - 150.4)
            else: aqi = 300 + (200 / (500.4 - 250.4)) * min(pm25_f - 250.4, 250)
            aqi_values.append(aqi)
            print(f"    [calculate_aqi] PM2.5 AQI = {aqi}")
        except (ValueError, TypeError):
            print(f"    [calculate_aqi] Invalid PM2.5 value: {pm25}")

    if is_valid(pm10):
        try:
            pm10_f = float(pm10)
            if pm10_f <= 54: aqi = (50 / 54) * pm10_f
            elif pm10_f <= 154: aqi = 50 + (50 / (154 - 54)) * (pm10_f - 54)
            elif pm10_f <= 254: aqi = 100 + (50 / (254 - 154)) * (pm10_f - 154)
            elif pm10_f <= 354: aqi = 150 + (50 / (354 - 254)) * (pm10_f - 254)
            elif pm10_f <= 424: aqi = 200 + (100 / (424 - 354)) * (pm10_f - 354)
            else: aqi = 300 + (200 / (604 - 424)) * min(pm10_f - 424, 180)
            aqi_values.append(aqi)
            print(f"    [calculate_aqi] PM10 AQI = {aqi}")
        except (ValueError, TypeError):
            print(f"    [calculate_aqi] Invalid PM10 value: {pm10}")

    if is_valid(no2_ppb):
        try:
            no2 = float(no2_ppb)
            if no2 <= 53: aqi = (50 / 53) * no2
            elif no2 <= 100: aqi = 50 + (50 / (100 - 53)) * (no2 - 53)
            elif no2 <= 360: aqi = 100 + (50 / (360 - 100)) * (no2 - 100)
            elif no2 <= 649: aqi = 150 + (50 / (649 - 360)) * (no2 - 360)
            elif no2 <= 1249: aqi = 200 + (100 / (1249 - 649)) * (no2 - 649)
            else: aqi = 300 + (200 / (2049 - 1249)) * min(no2 - 1249, 800)
            aqi_values.append(aqi)
            print(f"    [calculate_aqi] NO2 AQI = {aqi}")
        except (ValueError, TypeError):
            print(f"    [calculate_aqi] Invalid NO2 value: {no2_ppb}")

    if is_valid(co_ppm):
        try:
            co = float(co_ppm)
            if co <= 4.4: aqi = (50 / 4.4) * co
            elif co <= 9.4: aqi = 50 + (50 / (9.4 - 4.4)) * (co - 4.4)
            elif co <= 12.4: aqi = 100 + (50 / (12.4 - 9.4)) * (co - 9.4)
            elif co <= 15.4: aqi = 150 + (50 / (15.4 - 12.4)) * (co - 12.4)
            elif co <= 30.4: aqi = 200 + (100 / (30.4 - 15.4)) * (co - 15.4)
            else: aqi = 300 + (200 / (50.4 - 30.4)) * min(co - 30.4, 20)
            aqi_values.append(aqi)
            print(f"    [calculate_aqi] CO AQI = {aqi}")
        except (ValueError, TypeError):
            print(f"    [calculate_aqi] Invalid CO value: {co_ppm}")

    if is_valid(o3_ppb):
        try:
            o3 = float(o3_ppb)
            if o3 <= 54: aqi = (50 / 54) * o3
            elif o3 <= 70: aqi = 50 + (50 / (70 - 54)) * (o3 - 54)
            elif o3 <= 85: aqi = 100 + (50 / (85 - 70)) * (o3 - 70)
            elif o3 <= 105: aqi = 150 + (50 / (105 - 85)) * (o3 - 85)
            elif o3 <= 200: aqi = 200 + (100 / (200 - 105)) * (o3 - 105)
            else: aqi = 300 + (200 / (300 - 200)) * min(o3 - 200, 100)
            aqi_values.append(aqi)
            print(f"    [calculate_aqi] O3 AQI = {aqi}")
        except (ValueError, TypeError):
            print(f"    [calculate_aqi] Invalid O3 value: {o3_ppb}")

    if is_valid(so2_ppb):
        try:
            so2 = float(so2_ppb)
            if so2 <= 35: aqi = (50 / 35) * so2
            elif so2 <= 75: aqi = 50 + (50 / (75 - 35)) * (so2 - 35)
            elif so2 <= 185: aqi = 100 + (50 / (185 - 75)) * (so2 - 75)
            elif so2 <= 304: aqi = 150 + (50 / (304 - 185)) * (so2 - 185)
            elif so2 <= 604: aqi = 200 + (100 / (604 - 304)) * (so2 - 304)
            else: aqi = 300 + (200 / (1004 - 604)) * min(so2 - 604, 400)
            aqi_values.append(aqi)
            print(f"    [calculate_aqi] SO2 AQI = {aqi}")
        except (ValueError, TypeError):
            print(f"    [calculate_aqi] Invalid SO2 value: {so2_ppb}")

    print(f"  [calculate_aqi] All individual valid AQIs calculated: {aqi_values}")
    valid_aqi_values = [aqi for aqi in aqi_values if is_valid(aqi)]

    if not valid_aqi_values:
        print("  [calculate_aqi] No valid individual AQIs to calculate final AQI.")
        return None

    final_aqi = max(valid_aqi_values)
    print(f"  [calculate_aqi] Final Max AQI: {final_aqi}")
    return final_aqi

# Route hiển thị trang dự đoán
@app.route('/DuDoan')
def DuDoan():
    return render_template('DuDoan.html')

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        print(f"Error during application startup: {str(e)}")
