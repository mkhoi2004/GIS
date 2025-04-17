
function submitForm(event) {
    event.preventDefault(); // Ngăn chặn hành vi mặc định của form
    fetch("{{ url_for('predict') }}", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            pm25: document.getElementById('pm25').value,
            pm10: document.getElementById('pm10').value,
            no2: document.getElementById('no2').value,
            co: document.getElementById('co').value,
            o3: document.getElementById('o3').value,
            so2: document.getElementById('so2').value,
            humidity: document.getElementById('humidity').value,
            temperature: document.getElementById('temperature').value,
            wind: document.getElementById('wind').value
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            console.error('Error:', data.error);
            document.getElementById('result').innerText = `Lỗi: ${data.error}`;
        } else {
            document.getElementById('result').innerText = `Mức độ rủi ro: ${data.risk_level}`;
        }
    })
    .catch(error => console.error('Error:', error));
}
