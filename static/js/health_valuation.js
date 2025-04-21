const W1 = 0.6;
const W2 = 0.25;
const W3 = 0.15;
const RESPIRATORY_RATE = 7.5;

document.addEventListener('DOMContentLoaded', function () {
    fetch('/aqi')
        .then(response => response.json())
        .then(data => {
            const citySelect = document.getElementById('citySelect');
            data.forEach(location => {
                const option = document.createElement('option');
                option.value = location.name;
                option.textContent = `${location.name} (${location.country})`;
                option.dataset.population = location.population;
                option.dataset.area = location.area;
                option.dataset.aqi = location.aqi;
                citySelect.appendChild(option);
            });
        })
        .catch(error => console.error('Error fetching city data:', error));
});

function calculateHRI() {
    let citySelect = document.getElementById('citySelect');
    let selectedCity = citySelect.options[citySelect.selectedIndex];
    let resultDiv = document.getElementById('hriResult');

    if (!selectedCity.value) {
        resultDiv.innerHTML = "Vui lòng chọn một thành phố.";
        resultDiv.style.display = "block";
        return;
    }

    let aqi = parseFloat(selectedCity.dataset.aqi) || 0;
    let population = parseFloat(selectedCity.dataset.population) || 0;
    let area = parseFloat(selectedCity.dataset.area) || 1;
    let populationDensity = population / area;

    let hri = (aqi * W1) + (RESPIRATORY_RATE * W2) + (populationDensity * W3);

    let aqiMessage = "";
    if (aqi >= 0 && aqi <= 50) {
        aqiMessage = "<b>Mức độ ô nhiễm:</b> Tốt<br><b>Ý nghĩa:</b> Chất lượng không khí đạt yêu cầu, ít rủi ro.";
    } else if (aqi <= 100) {
        aqiMessage = "<b>Mức độ ô nhiễm:</b> Vừa phải<br><b>Ý nghĩa:</b> Chất lượng không khí chấp nhận được, có thể ảnh hưởng nhẹ đến nhóm nhạy cảm.";
    } else if (aqi <= 150) {
        aqiMessage = "<b>Mức độ ô nhiễm:</b> Không lành mạnh cho nhóm nhạy cảm<br><b>Ý nghĩa:</b> Nhóm nhạy cảm có thể bị ảnh hưởng.";
    } else if (aqi <= 200) {
        aqiMessage = "<b>Mức độ ô nhiễm:</b> Không lành mạnh<br><b>Ý nghĩa:</b> Mọi người có thể gặp vấn đề sức khỏe.";
    } else if (aqi <= 300) {
        aqiMessage = "<b>Mức độ ô nhiễm:</b> Rất không lành mạnh<br><b>Ý nghĩa:</b> Nguy cơ cao gặp vấn đề hô hấp nghiêm trọng.";
    } else {
        aqiMessage = "<b>Mức độ ô nhiễm:</b> Nguy hiểm<br><b>Ý nghĩa:</b> Nguy cơ nghiêm trọng đến sức khỏe toàn dân.";
    }

    let hriMessage = "";
    if (hri <= 100) {
        hriMessage = "<b>Mức độ HRI:</b> Tốt (0-100)<br><b>Lời khuyên:</b> Không khí an toàn, bạn có thể thoải mái hoạt động ngoài trời mà không cần lo lắng.";
    } else if (hri <= 250) {
        hriMessage = "<b>Mức độ HRI:</b> Trung bình (101-250)<br><b>Lời khuyên:</b> Chất lượng không khí ở mức chấp nhận được, nhưng nhóm nhạy cảm (trẻ em, người già, người có bệnh hô hấp) nên hạn chế thời gian ngoài trời.";
    } else if (hri <= 400) {
        hriMessage = "<b>Mức độ HRI:</b> Không tốt cho nhóm nhạy cảm (251-400)<br><b>Lời khuyên:</b> Nhóm nhạy cảm nên ở trong nhà, đeo khẩu trang nếu ra ngoài, và tránh các hoạt động gắng sức.";
    } else if (hri <= 600) {
        hriMessage = "<b>Mức độ HRI:</b> Không tốt (401-600)<br><b>Lời khuyên:</b> Mọi người nên ở trong nhà, đóng cửa sổ, sử dụng máy lọc không khí, và hạn chế tối đa tiếp xúc với không khí bên ngoài.";
    } else if (hri <= 1000) {
        hriMessage = "<b>Mức độ HRI:</b> Rất không tốt (601-1000)<br><b>Lời khuyên:</b> Nguy cơ hô hấp nghiêm trọng, ở trong nhà, sử dụng khẩu trang N95 và máy lọc không khí, tránh mọi hoạt động ngoài trời.";
    } else {
        hriMessage = "<b>Mức độ HRI:</b> Nguy hiểm (>1000)<br><b>Lời khuyên:</b> Tình trạng khẩn cấp, ở trong nhà với hệ thống lọc không khí, đeo khẩu trang chuyên dụng nếu phải ra ngoài, liên hệ cơ quan y tế nếu có triệu chứng bất thường.";
    }

    resultDiv.innerHTML = `
        <b>AQI:</b> ${aqi}<br>
        ${aqiMessage}<br>
        ${hriMessage}<br>
        <b>Thành phố:</b> ${selectedCity.textContent}<br>
        <b>Dân số:</b> ${population.toLocaleString()} người<br>
        <b>Diện tích:</b> ${area.toLocaleString()} km²<br>
        <b>Mật độ dân số:</b> ${populationDensity.toFixed(2)} người/km²<br>
        <b>Tỷ lệ bệnh hô hấp:</b> ${RESPIRATORY_RATE}% (giá trị cố định toàn cầu)<br>
        <b>HRI (Chỉ số rủi ro hô hấp):</b> ${hri.toFixed(2)}
    `;
    resultDiv.style.display = "block";
}

function sendMessage() {
    let userMessage = document.getElementById("userMessage").value;
    if (!userMessage.trim()) {
        alert("Vui lòng nhập câu hỏi!");
        return;
    }

    let chatboxBody = document.getElementById("chatboxBody");
    const userMsgDiv = document.createElement('div');
    userMsgDiv.classList.add('user-message');
    userMsgDiv.textContent = userMessage;
    chatboxBody.appendChild(userMsgDiv);

    document.getElementById("userMessage").value = "";
    chatboxBody.scrollTop = chatboxBody.scrollHeight;

    const thinkingDiv = document.createElement('div');
    thinkingDiv.classList.add('ai-response');
    thinkingDiv.innerHTML = '<i>Đang trả lời...</i>';
    chatboxBody.appendChild(thinkingDiv);
    chatboxBody.scrollTop = chatboxBody.scrollHeight;

    fetch('/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: userMessage })
    })
    .then(response => {
        if (!response.ok) {
             return response.json().then(err => {
                 throw new Error(err.error || `Lỗi ${response.status}`);
             }).catch(() => {
                 throw new Error(`Lỗi ${response.status}: ${response.statusText}`);
             });
        }
        return response.json();
    })
    .then(data => {
        chatboxBody.removeChild(thinkingDiv);

        if (data.response) {
            const aiMsgDiv = document.createElement('div');
            aiMsgDiv.classList.add('ai-response');
            aiMsgDiv.innerHTML = data.response.replace(/\n/g, '<br>'); 
            chatboxBody.appendChild(aiMsgDiv);
        } else {
            const errorDiv = document.createElement('div');
            errorDiv.classList.add('ai-response');
            errorDiv.style.color = 'red';
            errorDiv.textContent = data.error || 'Không nhận được phản hồi hợp lệ.';
            chatboxBody.appendChild(errorDiv);
        }
        chatboxBody.scrollTop = chatboxBody.scrollHeight;
    })
    .catch(error => {
        console.error("Error:", error);
         if (chatboxBody.contains(thinkingDiv)) {
             chatboxBody.removeChild(thinkingDiv);
         }
        const errorDiv = document.createElement('div');
        errorDiv.classList.add('ai-response');
        errorDiv.style.color = 'red';
        errorDiv.textContent = `Lỗi: ${error.message}`;
        chatboxBody.appendChild(errorDiv);
        chatboxBody.scrollTop = chatboxBody.scrollHeight;
    });
}

let healthRiskChart;

function updateChart(probabilities) {
    const ctx = document.getElementById('healthRiskChart').getContext('2d');

    const chartLabels = ['Tốt', 'Trung bình', 'Không lành mạnh cho nhóm nhạy cảm', 'Không lành mạnh'];

    if (!probabilities || !Array.isArray(probabilities) || probabilities.length === 0) {
        console.error("Dữ liệu xác suất không hợp lệ hoặc rỗng:", probabilities);
        if (healthRiskChart) {
            healthRiskChart.data.datasets[0].data = [];
            healthRiskChart.update();
        }
        return;
    }

    const chartData = probabilities.map(p => (p * 100).toFixed(1));

    const backgroundColors = [
        'rgba(0, 228, 0, 0.6)',
        'rgba(255, 255, 0, 0.6)',
        'rgba(255, 126, 0, 0.6)',
        'rgba(255, 0, 0, 0.6)',
        'rgba(143, 63, 151, 0.6)',
        'rgba(126, 0, 35, 0.6)'
    ];
    const borderColors = [
        'rgba(0, 228, 0, 1)',
        'rgba(255, 255, 0, 1)',
        'rgba(255, 126, 0, 1)',
        'rgba(255, 0, 0, 1)',
        'rgba(143, 63, 151, 1)',
        'rgba(126, 0, 35, 1)'
    ];

    const labelsToShow = chartLabels.slice(0, probabilities.length);
    const bgColorsToShow = backgroundColors.slice(0, probabilities.length);
    const bdColorsToShow = borderColors.slice(0, probabilities.length);

    if (healthRiskChart) {
        healthRiskChart.data.labels = labelsToShow;
        healthRiskChart.data.datasets[0].data = chartData;
        healthRiskChart.data.datasets[0].backgroundColor = bgColorsToShow;
        healthRiskChart.data.datasets[0].borderColor = bdColorsToShow;
        healthRiskChart.update();
    } else {
        healthRiskChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labelsToShow,
                datasets: [{
                    label: 'Xác suất rủi ro sức khỏe (%)',
                    data: chartData,
                    backgroundColor: bgColorsToShow,
                    borderColor: bdColorsToShow,
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        title: {
                             display: true,
                             text: 'Xác suất (%)'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                let label = context.dataset.label || '';
                                if (label) {
                                    label += ': ';
                                }
                                if (context.parsed.y !== null) {
                                    label += context.parsed.y + '%';
                                }
                                return label;
                            }
                        }
                    }
                }
            }
        });
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const chatWidget = document.querySelector('.chat-widget');
    const chatToggleButton = document.getElementById('chatToggleButton');
    const chatCloseButton = document.getElementById('chatCloseButton');
    const chatboxContainer = document.getElementById('chatboxContainer');

    if (chatToggleButton && chatWidget && chatCloseButton && chatboxContainer) {
        chatToggleButton.addEventListener('click', function() {
            chatWidget.classList.add('open');
        });

        chatCloseButton.addEventListener('click', function() {
            chatWidget.classList.remove('open');
        });
    } else {
        console.error("Không tìm thấy các phần tử cần thiết cho chat widget.");
    }

    fetchCityData();
});

async function submitPredictionForm() {
    const pm25 = document.getElementById('pm25Input').value;
    const pm10 = document.getElementById('pm10Input').value;
    const no2 = document.getElementById('no2Input').value;
    const o3 = document.getElementById('o3Input').value;
    const co = document.getElementById('coInput').value;
    const so2 = document.getElementById('so2Input').value;
    const humidity = document.getElementById('humidityInput').value;
    const temperature = document.getElementById('temperatureInput').value;
    const wind = document.getElementById('windInput').value;

    const inputData = {
        pm25: parseFloat(pm25) || 0,
        pm10: parseFloat(pm10) || 0,
        no2: parseFloat(no2) || 0,
        o3: parseFloat(o3) || 0,
        co: parseFloat(co) || 0,
        so2: parseFloat(so2) || 0,
        humidity: parseFloat(humidity) || 0,
        temperature: parseFloat(temperature) || 0,
        wind: parseFloat(wind) || 0
    };

    const submitButton = document.getElementById('predictButton');
    const resultDiv = document.getElementById('predictionResult');
    if (submitButton) submitButton.disabled = true;
    if (resultDiv) resultDiv.innerHTML = 'Đang xử lý...';

    try {
        const response = await fetch('/api/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(inputData)
        });

        if (!response.ok) {
            throw new Error(`Lỗi HTTP: ${response.status}`);
        }

        const data = await response.json();

        if (data.error) {
            console.error("Lỗi API dự đoán:", data.error);
            if (resultDiv) resultDiv.innerHTML = `Lỗi: ${data.error}`;
             if (healthRiskChart) {
                updateChart([]);
             }
        } else {
            console.log("Kết quả dự đoán:", data);
            document.getElementById('aqiValueDisplay').innerText = data.calculated_aqi !== undefined ? data.calculated_aqi.toFixed(1) : 'N/A';
            document.getElementById('aqiLevelDisplay').innerText = data.aqi_level || '';
            document.getElementById('healthDescription').innerText = data.health_description || '';

             if (resultDiv) {
                 resultDiv.style.display = 'block';
             }

            updateChart(data.risk_probabilities);
        }

    } catch (error) {
        console.error('Lỗi gọi API dự đoán:', error);
        if (resultDiv) resultDiv.innerHTML = `Đã xảy ra lỗi khi kết nối đến máy chủ: ${error.message}`;
         if (healthRiskChart) {
             updateChart([]);
         }
    } finally {
         if (submitButton) submitButton.disabled = false;
    }
}
