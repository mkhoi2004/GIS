import pandas as pd

#Sử dụng mô hình để đưa ra dự đoán và khuyến nghị


def get_health_recommendations(risk_level):
    recommendations = {
        0: {
            "risk_name": "Tốt (Good)",
            "color": "Xanh lá",
            "description": "Chất lượng không khí được coi là tốt và ô nhiễm không khí gây ra ít hoặc không có rủi ro.",
            "health_effects": "Không có nguy cơ sức khỏe. Phù hợp cho mọi hoạt động ngoài trời.",
            "recommendations": [
                "Bạn có thể tham gia các hoạt động ngoài trời bình thường.",
                "Không cần có biện pháp phòng ngừa đặc biệt."
            ],
            "specific_recommendations": {
                "Người khỏe mạnh": "An toàn cho mọi hoạt động ngoài trời.",
                "Người già (>65 tuổi)": "An toàn cho các hoạt động ngoài trời.",
                "Trẻ em (<18 tuổi)": "An toàn cho mọi hoạt động ngoài trời.",
                "Người mắc bệnh hô hấp": "An toàn, nhưng nên mang theo thuốc (ống hít) nếu có bệnh hen suyễn."
            }
        },
        1: {
            "risk_name": "Trung bình (Moderate)",
            "color": "Vàng",
            "description": "Chất lượng không khí ở mức chấp nhận được, tuy nhiên có thể gây ra một số lo ngại cho những người cực kỳ nhạy cảm.",
            "health_effects": "Chất lượng không khí chấp nhận được, nhưng một số người nhạy cảm (như người mắc hen suyễn) có thể gặp vấn đề nhẹ.",
            "recommendations": [
                "Những người nhạy cảm đặc biệt nên xem xét giảm các hoạt động kéo dài hoặc nặng nề ngoài trời.",
                "Người bình thường có thể hoạt động ngoài trời bình thường."
            ],
            "specific_recommendations": {
                "Người khỏe mạnh": "Có thể hoạt động ngoài trời bình thường.",
                "Người già (>65 tuổi)": "Theo dõi sức khỏe, hạn chế tiếp xúc kéo dài nếu có bệnh nền (tim mạch, hô hấp).",
                "Trẻ em (<18 tuổi)": "Giảm thời gian chơi ngoài trời nếu nhạy cảm với khói bụi.",
                "Người mắc bệnh hô hấp": "Theo dõi triệu chứng, mang theo thuốc (ống hít)."
            }
        },
        2: {
            "risk_name": "Không lành mạnh cho nhóm nhạy cảm (Unhealthy for Sensitive Groups)",
            "color": "Cam",
            "description": "Những người thuộc nhóm nhạy cảm có thể bị ảnh hưởng sức khỏe. Người bình thường ít bị ảnh hưởng.",
            "health_effects": "Trẻ em, người già, và người mắc bệnh hô hấp (hen suyễn, COPD) có thể gặp triệu chứng như khó thở, ho. Người khỏe mạnh ít bị ảnh hưởng.",
            "recommendations": [
                "Trẻ em, người già và người có bệnh hô hấp nên hạn chế các hoạt động ngoài trời kéo dài.",
                "Nên đóng cửa sổ và sử dụng máy lọc không khí nếu có.",
                "Cân nhắc đeo khẩu trang N95 khi ra ngoài."
            ],
            "specific_recommendations": {
                "Người khỏe mạnh": "Hạn chế hoạt động ngoài trời kéo dài, đặc biệt nếu có triệu chứng như ho, khó thở.",
                "Người già (>65 tuổi)": "Ở trong nhà, sử dụng máy lọc không khí nếu có.",
                "Trẻ em (<18 tuổi)": "Tránh hoạt động ngoài trời, đặc biệt nếu mắc hen suyễn.",
                "Người mắc bệnh hô hấp": "Tránh ra ngoài, sử dụng thuốc theo chỉ định, liên hệ bác sĩ nếu triệu chứng nặng."
            }
        },
        3: {
            "risk_name": "Không lành mạnh (Unhealthy)",
            "color": "Đỏ",
            "description": "Mọi người có thể bắt đầu cảm thấy ảnh hưởng đến sức khỏe. Những người nhạy cảm có thể gặp tác động nghiêm trọng hơn.",
            "health_effects": "Mọi người bắt đầu gặp vấn đề sức khỏe, đặc biệt là khó thở, ho. Nhóm nhạy cảm bị ảnh hưởng nghiêm trọng hơn.",
            "recommendations": [ 
                "Mọi người nên hạn chế các hoạt động ngoài trời, đặc biệt là hoạt động nặng.",
                "Trẻ em, người già và người có bệnh hô hấp nên ở trong nhà.",
                "Đeo khẩu trang N95 khi ra ngoài và sử dụng máy lọc không khí trong nhà."
            ],
            "specific_recommendations": {
                "Người khỏe mạnh": "Tránh vận động mạnh ngoài trời, theo dõi triệu chứng.",
                "Người già (>65 tuổi)": "Ở trong nhà, hạn chế tối đa hoạt động ngoài trời, sử dụng máy lọc không khí.",
                "Trẻ em (<18 tuổi)": "Giữ trẻ trong nhà, đảm bảo môi trường trong nhà sạch sẽ.",
                "Người mắc bệnh hô hấp": "Ở trong nhà hoàn toàn, tăng cường sử dụng thuốc dự phòng, chuẩn bị sẵn thuốc cấp cứu."
            }
        },
        4: {
            "risk_name": "Rất không lành mạnh (Very Unhealthy)",
            "color": "Tím",
            "description": "Cảnh báo sức khỏe về điều kiện khẩn cấp. Toàn bộ dân số có nhiều khả năng bị ảnh hưởng.",
            "health_effects": "Cảnh báo sức khỏe: Mọi người có nguy cơ gặp triệu chứng nghiêm trọng (khó thở, đau ngực). Nhóm nhạy cảm cần tránh ra ngoài.",
            "recommendations": [
                "Tránh tất cả các hoạt động thể chất ngoài trời.",
                "Nên ở trong nhà và đóng cửa sổ, sử dụng máy lọc không khí.",
                "Đeo khẩu trang N95 khi buộc phải ra ngoài.",
                "Người có bệnh hô hấp nên liên hệ với bác sĩ nếu có triệu chứng."
            ],
            "specific_recommendations": {
                "Người khỏe mạnh": "Ở trong nhà, đóng cửa sổ, sử dụng máy lọc không khí, đeo khẩu trang N95 khi buộc phải ra ngoài.",
                "Người già (>65 tuổi)": "Không ra ngoài, sử dụng máy lọc không khí, liên hệ y tế ngay nếu có triệu chứng khó thở.",
                "Trẻ em (<18 tuổi)": "Giữ trẻ trong nhà, đảm bảo không khí trong phòng được lọc, đặc biệt trong phòng ngủ.",
                "Người mắc bệnh hô hấp": "Cần được giám sát y tế, chuẩn bị kế hoạch điều trị khẩn cấp, liên hệ bác sĩ ngay khi có triệu chứng."
            }
        },
        5: {
            "risk_name": "Nguy hiểm (Hazardous)",
            "color": "Nâu",
            "description": "Cảnh báo sức khỏe: tất cả mọi người có thể gặp phải các tác động sức khỏe nghiêm trọng hơn.",
            "health_effects": "Tình trạng khẩn cấp: Toàn bộ dân số bị ảnh hưởng nghiêm trọng, có thể dẫn đến nhập viện hoặc tử vong nếu tiếp xúc kéo dài.",
            "recommendations": [
                "Tất cả mọi người nên tránh mọi hoạt động ngoài trời.",
                "Ở trong nhà, đóng cửa sổ và chạy máy lọc không khí.",
                "Người bị bệnh hô hấp nên được theo dõi y tế chặt chẽ.",
                "Cân nhắc di chuyển tạm thời đến khu vực có chất lượng không khí tốt hơn."
            ],
            "specific_recommendations": {
                "Người khỏe mạnh": "Ở trong nhà hoàn toàn, sử dụng khẩu trang N95 ngay cả trong nhà nếu không có máy lọc không khí.",
                "Người già (>65 tuổi)": "Cần được giám sát y tế, cân nhắc di chuyển đến khu vực an toàn hơn nếu có thể.",
                "Trẻ em (<18 tuổi)": "Không cho trẻ ra ngoài trong mọi trường hợp, cân nhắc di chuyển đến nơi an toàn hơn.",
                "Người mắc bệnh hô hấp": "Cần hỗ trợ y tế ngay lập tức, sẵn sàng phương án nhập viện nếu triệu chứng nặng."
            }
        }
    }
    
    return recommendations.get(risk_level, {"risk_name": "Không xác định", "description": "Không có dữ liệu", "recommendations": []})

# Hàm lấy khuyến nghị cụ thể cho từng nhóm đối tượng dựa trên mức AQI
def get_specific_group_recommendations(aqi_value):
    # Kiểm tra đầu vào, trả về thông báo nếu không hợp lệ
    if pd.isna(aqi_value) or isinstance(aqi_value, str) and not aqi_value.replace('.', '', 1).isdigit():
        # Trả về dict rỗng hoặc thông báo lỗi cho từng nhóm nếu AQI không hợp lệ
        default_message = "Không có dữ liệu AQI hợp lệ để đưa ra khuyến nghị."
        return {
            "Người khỏe mạnh": default_message,
            "Người già (>65 tuổi)": default_message,
            "Trẻ em (<18 tuổi)": default_message,
            "Người mắc bệnh hô hấp": default_message
        }

    try:
        aqi = float(aqi_value)
    except (ValueError, TypeError):
        # Xử lý trường hợp không thể chuyển đổi sang float
        default_message = "Giá trị AQI không hợp lệ."
        return {
            "Người khỏe mạnh": default_message,
            "Người già (>65 tuổi)": default_message,
            "Trẻ em (<18 tuổi)": default_message,
            "Người mắc bệnh hô hấp": default_message
        }


    recommendations = {
        "Người khỏe mạnh": {
            "advice": {
                "0-50": "An toàn cho mọi hoạt động ngoài trời.",
                "51-100": "An toàn cho mọi hoạt động ngoài trời.",
                "101-150": "Hạn chế hoạt động ngoài trời kéo dài, đặc biệt nếu có triệu chứng như ho, khó thở.",
                "151+": "Tránh vận động mạnh ngoài trời, theo dõi triệu chứng."
            }
        },
        "Người già (>65 tuổi)": {
            "advice": {
                "0-50": "An toàn cho các hoạt động ngoài trời.",
                "51-100": "Theo dõi sức khỏe, hạn chế tiếp xúc kéo dài nếu có bệnh nền (tim mạch, hô hấp).",
                "101+": "Ở trong nhà, sử dụng máy lọc không khí nếu có."
            }
        },
        "Trẻ em (<18 tuổi)": {
            "advice": {
                "0-50": "An toàn cho mọi hoạt động ngoài trời.",
                "51-100": "Giảm thời gian chơi ngoài trời nếu nhạy cảm với khói bụi.",
                "101+": "Tránh hoạt động ngoài trời, đặc biệt nếu mắc hen suyễn."
            }
        },
        "Người mắc bệnh hô hấp": {
            "advice": {
                "0-50": "Theo dõi triệu chứng, mang theo thuốc (ống hít).",
                "51-100": "Theo dõi triệu chứng, mang theo thuốc (ống hít).",
                "101+": "Tránh ra ngoài, sử dụng thuốc theo chỉ định, liên hệ bác sĩ nếu triệu chứng nặng."
            }
        }
    }

    result = {}
    default_advice = "Không có khuyến nghị cụ thể cho mức AQI này."

    for group, info in recommendations.items():
        advice_dict = info.get("advice", {})
        selected_advice = default_advice

        try:
            if aqi <= 50:
                selected_advice = advice_dict.get("0-50", default_advice)
            elif aqi <= 100:
                selected_advice = advice_dict.get("51-100", default_advice)
            elif aqi <= 150 and group == "Người khỏe mạnh":
                selected_advice = advice_dict.get("101-150", default_advice)
            else:
                key_to_use = "151+" if group == "Người khỏe mạnh" else "101+"
                selected_advice = advice_dict.get(key_to_use, default_advice)

            result[group] = selected_advice

        except Exception as e:
            print(f"Unexpected error processing group '{group}': {str(e)}")
            result[group] = "Đã xảy ra lỗi khi lấy khuyến nghị."

    return result
