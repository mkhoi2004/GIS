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

    // Hiển thị tin nhắn của người dùng trong chatbox
    let chatboxBody = document.getElementById("chatboxBody");
    chatboxBody.innerHTML += `<div class="user-message">${userMessage}</div>`;

    // Gửi yêu cầu tới backend (Flask)
    fetch('/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: userMessage })
    })
    .then(response => response.json())
    .then(data => {
        // Log phản hồi từ backend
        console.log("Response from backend:", data);

        if (data.response) {
            // Hiển thị phản hồi từ AI (Gemini)
            let aiResponse = data.response;
            chatboxBody.innerHTML += `<div class="ai-response">${aiResponse}</div>`;
            document.getElementById("userMessage").value = ""; // Xóa ô nhập liệu

            // Cuộn xuống dưới để hiển thị tin nhắn mới nhất
            chatboxBody.scrollTop = chatboxBody.scrollHeight;
        } else {
            console.log("Không có phản hồi từ API Gemini");
        }
    })
    .catch(error => {
        console.error("Error:", error);  // Log lỗi nếu có sự cố
    });
}

// Biến toàn cục hoặc trong scope phù hợp để lưu trữ biểu đồ
let healthRiskChart;

/**
 * Cập nhật biểu đồ xác suất rủi ro sức khỏe.
 * @param {Array<number>} probabilities Mảng chứa xác suất cho từng mức rủi ro,
 *                                     ví dụ: [prob_tot, prob_trung_binh, prob_knl_nhay_cam, prob_khong_lanh_manh, ...]
 *                                     Thứ tự PHẢI khớp với thứ tự lớp của mô hình ML.
 */
function updateChart(probabilities) {
    const ctx = document.getElementById('healthRiskChart').getContext('2d'); // Đảm bảo ID này đúng với thẻ canvas của bạn

    // --- QUAN TRỌNG: Đảm bảo thứ tự nhãn này khớp với thứ tự xác suất trả về từ model ---
    // Giả sử thứ tự là: Tốt, Trung bình, Không lành mạnh cho nhóm nhạy cảm, Không lành mạnh
    const chartLabels = ['Tốt', 'Trung bình', 'Không lành mạnh cho nhóm nhạy cảm', 'Không lành mạnh'];
    // Nếu model trả về nhiều hơn 4 xác suất, bạn cần thêm nhãn tương ứng vào đây
    // Ví dụ: ['Tốt', 'Trung bình', 'KNL Nhạy cảm', 'Không lành mạnh', 'Rất KNL', 'Nguy hại']

    // Kiểm tra dữ liệu probabilities
    if (!probabilities || !Array.isArray(probabilities) || probabilities.length === 0) {
        console.error("Dữ liệu xác suất không hợp lệ hoặc rỗng:", probabilities);
        // Có thể ẩn hoặc xóa dữ liệu biểu đồ cũ nếu muốn
        if (healthRiskChart) {
            healthRiskChart.data.datasets[0].data = [];
            healthRiskChart.update();
        }
        return;
    }

    // Chuyển đổi xác suất thành phần trăm
    const chartData = probabilities.map(p => (p * 100).toFixed(1)); // Làm tròn đến 1 chữ số thập phân

    // Màu sắc tương ứng cho từng mức (điều chỉnh nếu cần)
    const backgroundColors = [
        'rgba(0, 228, 0, 0.6)',    // Green - Tốt
        'rgba(255, 255, 0, 0.6)',  // Yellow - Trung bình
        'rgba(255, 126, 0, 0.6)', // Orange - KNL cho nhóm nhạy cảm
        'rgba(255, 0, 0, 0.6)',    // Red - Không lành mạnh
        'rgba(143, 63, 151, 0.6)', // Purple - Rất không lành mạnh (Nếu có)
        'rgba(126, 0, 35, 0.6)'    // Maroon - Nguy hại (Nếu có)
    ];
    const borderColors = [
        'rgba(0, 228, 0, 1)',
        'rgba(255, 255, 0, 1)',
        'rgba(255, 126, 0, 1)',
        'rgba(255, 0, 0, 1)',
        'rgba(143, 63, 151, 1)',
        'rgba(126, 0, 35, 1)'
    ];

    // Chỉ lấy số lượng nhãn và màu sắc tương ứng với số lượng xác suất nhận được
    const labelsToShow = chartLabels.slice(0, probabilities.length);
    const bgColorsToShow = backgroundColors.slice(0, probabilities.length);
    const bdColorsToShow = borderColors.slice(0, probabilities.length);


    if (healthRiskChart) {
        // Nếu biểu đồ đã tồn tại, cập nhật dữ liệu
        healthRiskChart.data.labels = labelsToShow;
        healthRiskChart.data.datasets[0].data = chartData;
        healthRiskChart.data.datasets[0].backgroundColor = bgColorsToShow;
        healthRiskChart.data.datasets[0].borderColor = bdColorsToShow;
        healthRiskChart.update();
    } else {
        // Nếu biểu đồ chưa tồn tại, tạo mới
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
                        max: 100, // Đảm bảo trục Y đi đến 100%
                        title: {
                             display: true,
                             text: 'Xác suất (%)'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false // Ẩn legend nếu không cần thiết
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                let label = context.dataset.label || '';
                                if (label) {
                                    label += ': ';
                                }
                                if (context.parsed.y !== null) {
                                    label += context.parsed.y + '%'; // Hiển thị % trong tooltip
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

// Hàm này được gọi khi người dùng nhấn nút "Đánh giá rủi ro"
// Bạn cần đảm bảo nút này có sự kiện onclick="submitPredictionForm()" hoặc thêm event listener
async function submitPredictionForm() {
    // 1. Lấy giá trị từ các input fields (thay ID bằng ID thực tế của bạn)
    const pm25 = document.getElementById('pm25Input').value;
    const pm10 = document.getElementById('pm10Input').value;
    const no2 = document.getElementById('no2Input').value;
    const o3 = document.getElementById('o3Input').value;
    const co = document.getElementById('coInput').value;
    const so2 = document.getElementById('so2Input').value;
    const humidity = document.getElementById('humidityInput').value;
    const temperature = document.getElementById('temperatureInput').value;
    const wind = document.getElementById('windInput').value;

    // Có thể thêm kiểm tra dữ liệu đầu vào ở đây

    // Chuẩn bị dữ liệu gửi đi
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
        // Đảm bảo tên các trường khớp với những gì backend /api/predict mong đợi
    };

    // Hiển thị loading hoặc vô hiệu hóa nút trong khi chờ
    const submitButton = document.getElementById('predictButton'); // Thay ID nút nếu cần
    const resultDiv = document.getElementById('predictionResult'); // Thay ID div kết quả nếu cần
    if (submitButton) submitButton.disabled = true;
    if (resultDiv) resultDiv.innerHTML = 'Đang xử lý...';


    try {
        // 2. Gửi yêu cầu đến /api/predict
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

        // 3. Xử lý kết quả trả về
        if (data.error) {
            console.error("Lỗi API dự đoán:", data.error);
            if (resultDiv) resultDiv.innerHTML = `Lỗi: ${data.error}`;
            // Xóa hoặc ẩn biểu đồ nếu có lỗi
             if (healthRiskChart) {
                updateChart([]); // Gọi với mảng rỗng để xóa dữ liệu cũ
             }
        } else {
            console.log("Kết quả dự đoán:", data);
            // Cập nhật các phần khác của giao diện (AQI, khuyến nghị, ...)
            // Ví dụ: (thay ID bằng ID thực tế)
            document.getElementById('aqiValueDisplay').innerText = data.calculated_aqi !== undefined ? data.calculated_aqi.toFixed(1) : 'N/A';
            document.getElementById('aqiLevelDisplay').innerText = data.aqi_level || '';
            document.getElementById('healthDescription').innerText = data.health_description || '';
            // Cập nhật các khuyến nghị...

            // Hiển thị phần kết quả
             if (resultDiv) {
                 resultDiv.style.display = 'block'; // Hoặc cách bạn dùng để hiển thị kết quả
                 // Cập nhật nội dung chi tiết vào resultDiv nếu cần
             }


            // --- GỌI HÀM CẬP NHẬT BIỂU ĐỒ ---
            updateChart(data.risk_probabilities); // Quan trọng!
        }

    } catch (error) {
        console.error('Lỗi gọi API dự đoán:', error);
        if (resultDiv) resultDiv.innerHTML = `Đã xảy ra lỗi khi kết nối đến máy chủ: ${error.message}`;
         // Xóa hoặc ẩn biểu đồ nếu có lỗi
         if (healthRiskChart) {
             updateChart([]);
         }
    } finally {
         // Kích hoạt lại nút sau khi hoàn tất
         if (submitButton) submitButton.disabled = false;
    }
}

// --- QUAN TRỌNG ---
// Đảm bảo bạn có một nút trong HTML (`DuDoan.html` hoặc `health_evaluation.html`)
// có id="predictButton" (hoặc ID khác) và gọi hàm submitPredictionForm() khi click.
// Ví dụ: <button id="predictButton" onclick="submitPredictionForm()">Đánh giá rủi ro</button>
// Hoặc thêm Event Listener trong JavaScript:
// document.getElementById('predictButton').addEventListener('click', submitPredictionForm);
