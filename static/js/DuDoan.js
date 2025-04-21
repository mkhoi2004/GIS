function submitPredictionForm(event) {
    event.preventDefault(); // Ngăn chặn hành vi mặc định của form

    // Lấy giá trị từ các input
    const pm25Value = document.getElementById('pm25').value;
    const pm10Value = document.getElementById('pm10').value;
    const no2Value = document.getElementById('no2').value;
    const coValue = document.getElementById('co').value;
    const o3Value = document.getElementById('o3').value;
    const so2Value = document.getElementById('so2').value;
    const humidityValue = document.getElementById('humidity').value;
    const temperatureValue = document.getElementById('temperature').value;
    const windValue = document.getElementById('wind').value;

    // Lấy đơn vị từ các select (thay ID nếu cần)
    const no2Unit = document.getElementById('no2_unit').value; // Giả sử ID là 'no2_unit'
    const coUnit = document.getElementById('co_unit').value;   // Giả sử ID là 'co_unit'
    const o3Unit = document.getElementById('o3_unit').value;   // Giả sử ID là 'o3_unit'
    const so2Unit = document.getElementById('so2_unit').value; // Giả sử ID là 'so2_unit'

    const formData = {
        pm25: pm25Value,
        pm10: pm10Value,
        no2: no2Value,
        no2_unit: no2Unit, // Thêm đơn vị NO2
        co: coValue,
        co_unit: coUnit,   // Thêm đơn vị CO
        o3: o3Value,
        o3_unit: o3Unit,   // Thêm đơn vị O3
        so2: so2Value,
        so2_unit: so2Unit, // Thêm đơn vị SO2
        humidity: humidityValue,
        temperature: temperatureValue,
        wind: windValue
    };

    fetch('/api/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData) // Gửi đi formData đã bao gồm đơn vị
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => { throw new Error(err.error || `Lỗi ${response.status}`) });
        }
        return response.json();
    })
    .then(data => {
        const calculatedAqi = data.calculated_aqi;
        const aqiLevelInfo = getAqiLevelInfo(calculatedAqi);

        const aqiValueElement = document.getElementById('resultAqiValue');
        const aqiLevelElement = document.getElementById('resultAqiLevel');
        const descriptionElement = document.getElementById('resultDescription');
        const recommendationsElement = document.getElementById('resultRecommendations');
        const specificRecommendationsElement = document.getElementById('resultSpecificRecommendations');

        if (aqiValueElement) {
            aqiValueElement.textContent = calculatedAqi !== null ? calculatedAqi.toFixed(1) : 'N/A';
        }

        if (aqiLevelElement) {
            aqiLevelElement.textContent = aqiLevelInfo.name;
            aqiLevelElement.style.backgroundColor = aqiLevelInfo.color;
            aqiLevelElement.style.color = aqiLevelInfo.textColor;
            aqiLevelElement.style.padding = '2px 8px';
            aqiLevelElement.style.borderRadius = '4px';
            aqiLevelElement.style.display = 'inline-block';
        }

        if (descriptionElement) {
            descriptionElement.innerHTML = `Chất lượng không khí được coi là ${data.risk_name.toLowerCase()} và ${data.description.toLowerCase()}`;
        }

        if (recommendationsElement) {
            recommendationsElement.innerHTML = '';
            if (Array.isArray(data.recommendations)) {
                const ul = document.createElement('ul');
                data.recommendations.forEach(rec => {
                    const li = document.createElement('li');
                    li.textContent = rec;
                    ul.appendChild(li);
                });
                recommendationsElement.appendChild(ul);
            } else {
                recommendationsElement.textContent = data.recommendations;
            }
        }

        if (specificRecommendationsElement) {
            specificRecommendationsElement.innerHTML = '';
            const ul = document.createElement('ul');
            for (const group in data.specific_group_recommendations) {
                const li = document.createElement('li');
                li.innerHTML = `<strong>${group}:</strong> ${data.specific_group_recommendations[group]}`;
                ul.appendChild(li);
            }
            specificRecommendationsElement.appendChild(ul);
        }

        document.getElementById('predictionResultSection').style.display = 'block';
    })
    .catch(error => {
        console.error('Fetch Error:', error);
        const resultDiv = document.getElementById('predictionResultSection');
        if (resultDiv) {
            resultDiv.innerHTML = `<p style="color: red;">Đã xảy ra lỗi: ${error.message}</p>`;
            resultDiv.style.display = 'block';
        }
    });
}

/**
 * Xác định tên mức AQI và màu sắc dựa trên giá trị số.
 * @param {number|null} aqi - Giá trị AQI tính toán.
 * @returns {object} - Object chứa tên mức ('name') và mã màu ('color').
 */
function getAqiLevelInfo(aqi) {
    if (aqi === null || aqi === undefined) {
        return { name: "N/A", color: "#cccccc", textColor: "#000000" }; // Màu xám cho không có dữ liệu
    }
    if (aqi <= 50) {
        // Tốt (Good) - Xanh lá
        return { name: "Tốt", color: "#00e400", textColor: "#000000" };
    } else if (aqi <= 100) {
        // Trung bình (Moderate) - Vàng
        return { name: "Trung bình", color: "#ffff00", textColor: "#000000" };
    } else if (aqi <= 150) {
        // Không lành mạnh cho nhóm nhạy cảm (Unhealthy for Sensitive Groups) - Cam
        return { name: "Không lành mạnh cho nhóm nhạy cảm", color: "#ff7e00", textColor: "#ffffff" };
    } else if (aqi <= 200) {
        // Không lành mạnh (Unhealthy) - Đỏ
        return { name: "Không lành mạnh", color: "#ff0000", textColor: "#ffffff" };
    } else if (aqi <= 300) {
        // Rất không lành mạnh (Very Unhealthy) - Tím
        return { name: "Rất không lành mạnh", color: "#8f3f97", textColor: "#ffffff" };
    } else {
        // Nguy hiểm (Hazardous) - Nâu đỏ
        return { name: "Nguy hiểm", color: "#7e0023", textColor: "#ffffff" };
    }
}

// Đảm bảo DOM đã tải xong trước khi thêm event listener
document.addEventListener('DOMContentLoaded', (event) => {
    const predictionForm = document.getElementById('predictionForm'); // Thay 'predictionForm' bằng ID thực tế của form
    if (predictionForm) {
        predictionForm.addEventListener('submit', submitPredictionForm);
    } else {
        console.error("Không tìm thấy form với ID 'predictionForm'.");
        // Hoặc thử gắn vào nút nếu không dùng form submit
        const predictButton = document.getElementById('predictButton'); // Thay 'predictButton' bằng ID thực tế của nút
        if (predictButton) {
             predictButton.addEventListener('click', (clickEvent) => {
                 // Nếu nút không phải type="submit", bạn có thể cần ngăn chặn hành vi mặc định khác nếu có
                 // clickEvent.preventDefault(); // Bỏ comment nếu cần
                 submitPredictionForm(clickEvent); // Truyền sự kiện click vào hàm
             });
        } else {
             console.error("Không tìm thấy nút với ID 'predictButton'.");
        }
    }
});
