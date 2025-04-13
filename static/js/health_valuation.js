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
