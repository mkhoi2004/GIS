function submitPredictionForm(event) {
    event.preventDefault();

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
    const no2Unit = document.getElementById('no2_unit').value; 
    const coUnit = document.getElementById('co_unit').value;   
    const o3Unit = document.getElementById('o3_unit').value;   
    const so2Unit = document.getElementById('so2_unit').value; 

    const formData = {
        pm25: pm25Value,
        pm10: pm10Value,
        no2: no2Value,
        no2_unit: no2Unit,
        co: coValue,
        co_unit: coUnit,
        o3: o3Value,
        o3_unit: o3Unit,
        so2: so2Value,
        so2_unit: so2Unit,
        humidity: humidityValue,
        temperature: temperatureValue,
        wind: windValue
    };

    fetch('/api/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
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

function getAqiLevelInfo(aqi) {
    if (aqi === null || aqi === undefined || isNaN(aqi)) {
        return { name: "N/A", color: "#cccccc", textColor: "#000000" };
    }
    aqi = Math.round(aqi);
    if (aqi <= 50) return { name: "Tốt", color: "#a8e05f", textColor: "#33691e" };
    if (aqi <= 100) return { name: "Trung bình", color: "#fdd835", textColor: "#424242" };
    if (aqi <= 150) return { name: "Không lành mạnh cho nhóm nhạy cảm", color: "#fb8c00", textColor: "white" };
    if (aqi <= 200) return { name: "Không lành mạnh", color: "#e53935", textColor: "white" };
    if (aqi <= 300) return { name: "Rất không lành mạnh", color: "#8e24aa", textColor: "white" };
    return { name: "Nguy hiểm", color: "#b71c1c", textColor: "white" };
}

document.addEventListener('DOMContentLoaded', (event) => {
    const predictionForm = document.getElementById('predictionForm');
    if (predictionForm) {
        predictionForm.addEventListener('submit', submitPredictionForm);
    } else {
        console.error("Không tìm thấy form với ID 'predictionForm'.");
        const predictButton = document.getElementById('predictButton');
        if (predictButton) {
             predictButton.addEventListener('click', (clickEvent) => {
                 submitPredictionForm(clickEvent);
             });
        } else {
             console.error("Không tìm thấy nút với ID 'predictButton'.");
        }
    }
});
