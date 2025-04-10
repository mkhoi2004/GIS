from flask import Flask, jsonify, render_template
import requests
import time
from concurrent.futures import ThreadPoolExecutor
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

# Kết nối MongoDB
client = MongoClient('mongodb://localhost:27017/')
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
        aqi = data['data']['aqi'] if data['status'] == 'ok' else 'N/A'
        pollutants = data['data']['iaqi'] if data['status'] == 'ok' and 'iaqi' in data['data'] else {}
        pm25 = pollutants.get('pm25', {}).get('v', 'N/A')
        pm10 = pollutants.get('pm10', {}).get('v', 'N/A')
        no2 = pollutants.get('no2', {}).get('v', 'N/A')
        co = pollutants.get('co', {}).get('v', 'N/A')
        o3 = pollutants.get('o3', {}).get('v', 'N/A')
        so2 = pollutants.get('so2', {}).get('v', 'N/A')
        humidity = pollutants.get('h', {}).get('v', 'N/A')
        temperature = pollutants.get('t', {}).get('v', 'N/A')
        wind = pollutants.get('w', {}).get('v', 'N/A')
        update_time = data['data']['time']['s'] if data['status'] == 'ok' and 'time' in data['data'] else 'N/A'

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
            'population': city['population'],  # Thêm population
            'area': city['area'],
            'saved_at': datetime.now().strftime('%H:%M %d/%m/%Y')
        }

        # Lưu vào cache
        cache[city['name']] = {'data': city_data, 'timestamp': current_time}
        # Lưu vào MongoDB
        collection.insert_one(city_data.copy())  # Sử dụng .copy() để tránh tham chiếu

        return city_data
    except Exception as e:
        print(f"Error fetching data for {city['name']}: {str(e)}")  # Thêm log để debug
        city_data = {
            'name': city['name'],
            'country': country,
            'aqi': 'N/A',
            'pm25': 'N/A',
            'pm10': 'N/A',
            'no2': 'N/A',
            'co': 'N/A',
            'o3': 'N/A',
            'so2': 'N/A',
            'humidity': 'N/A',
            'temperature': 'N/A',
            'wind': 'N/A',
            'update_time': 'N/A',
            'lat': city['lat'],
            'lon': city['lon'],
            'population': city['population'],  # Thêm population
            'area': city['area'],
            'saved_at': datetime.now().strftime('%H:%M %d/%m/%Y')
        }
        # Lưu vào MongoDB ngay cả khi có lỗi
        collection.insert_one(city_data.copy())  # Sử dụng .copy() để tránh tham chiếu
        return city_data

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
                    print(f"Error processing {city['name']}: {str(e)}")  # Thêm log để debug
    return jsonify(result)

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/')
def health_evaluation():
    return render_template('health_evaluation.html')

if __name__ == '__main__':
    app.run(debug=True)