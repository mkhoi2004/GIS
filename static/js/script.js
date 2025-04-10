document.addEventListener('DOMContentLoaded', function () {
    const map = L.map('map').setView([20, 100], 3);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    const searchInput = document.getElementById('search-input');
    const searchResults = document.getElementById('search-results');
    let locations = [];

    // Danh sách ánh xạ URL tùy chỉnh
    const customUrls = {
        "Cần Thơ": "https://aqicn.org/city/vietnam/can-tho/ninh-kieu-kttv-tram-cam-bien/",
        "Trà Vinh": "https://aqicn.org/city/vietnam/tra-vinh/xa-dan-thanh--tx-duyen-hai/",
        "Vũng Tàu": "https://aqicn.org/city/vietnam/vung-tau/nga-tu-gieng-nuoc-tp.vung-tau/",
        "Long An": "https://aqicn.org/station/vietnam-long-an%3A-ubnd-tp-t%C3%A2n-an-76-h%C3%B9ng-v%C6%B0%C6%A1ng-p.2-kk/",
        "Tp Hồ Chí Minh": "https://aqicn.org/city/vietnam/tp-ho-chi-minh/duong-nguyen-van-tao--ap-3--nha-be-kttv-tram-cam-bien/",
        "Bình Dương": "https://aqicn.org/station/vietnam-thu-dau-mot-city-p.-hi%E1%BB%87p-th%C3%A0nh-kk-b%C3%ACnh-d%C6%B0%C6%A1ng%3A-s%E1%BB%91-593-%C4%91%E1%BA%A1i-l%E1%BB%99-b%C3%ACnh-d%C6%B0%C6%A1ng/",
        "Bình Phước": "https://aqicn.org/station/@469792/",
        "Lâm Đồng": "https://aqicn.org/station/vietnam-da-lat-city-l%C3%A2m-%C4%91%E1%BB%93ng%3A-v%C6%B0%E1%BB%9Dn-hoa-%C4%91%E1%BB%91i-di%E1%BB%87n-thcs-lam-s%C6%A1n-ph%C6%B0%E1%BB%9Dng-6-tp-%C4%91%C3%A0-l%E1%BA%A1t-kk/",
        "Ninh Thuận": "https://aqicn.org/station/vietnam-phan-rang%E2%80%93th%C3%A1p-ch%C3%A0m-city-ninh-thu%E1%BA%ADn%3A-c%C3%B4ng-vi%C3%AAn-b%E1%BA%BFn-xe-c%C5%A9-%C4%91.-th%E1%BB%91ng-nh%E1%BA%A5t-p.-thanh-s%C6%A1n-tp-phan-rang-kk/",
        "Nha Trang": "https://aqicn.org/city/vietnam/nha-trang/",
        "Khánh Hòa": "https://aqicn.org/station/vietnam-x%C3%A3-ninh-an-kh%C3%A1nh-h%C3%B2a%3A-tr%E1%BA%A1m-kh%C3%B4ng-kh%C3%AD-xung-quanh-ninh-an-kk/",
        "Bình Định": "https://aqicn.org/station/vietnam-quy-nh%C6%A1n-b%C3%ACnh-%C4%91%E1%BB%8Bnh%3A-huy%E1%BB%87n-tuy-ph%C6%B0%E1%BB%9Bc-kk/",
        "Gia Lai": "https://aqicn.org/city/vietnam/gia-lai/phu-dong--thanh-pho-pleiku-kttv-tram-cam-bien/",
        "Quảng Nam": "https://aqicn.org/station/vietnam-tam-k%E1%BB%B3-qu%E1%BA%A3ng-nam%3A-ti%E1%BA%BFp-gi%C3%A1p-%C4%91.-h%C3%B9ng-v%C6%B0%C6%A1ng-kdc-%C4%91.-h%E1%BB%93-xu%C3%A2n-h%C6%B0%C6%A1ng-kk/",
        "Đà Nẵng": "https://aqicn.org/station/vietnam-%C4%91%C3%A0-n%E1%BA%B5ng%3A-khu%C3%B4n-vi%C3%AAn-tr%C6%B0%E1%BB%9Dng-%C4%91h-s%C6%B0-ph%E1%BA%A1m-%C4%91%C3%A0-n%E1%BA%B5ng-kk/",
        "Thừa Thiên Huế": "https://aqicn.org/city/vietnam/thua-thien-hue/83-hung-vuong/",
        "Quảng Bình": "https://aqicn.org/city/vietnam/quang-binh/khu-kinh-te-hon-la/",
        "Nghệ An": "https://aqicn.org/city/vietnam/nghe-an/truong-thi--thanh-pho-vinh-kttv-tram-cam-bien/",
        "Thanh Hoá": "https://aqicn.org/city/vietnam/thanh-hoa/ubnd-p.-lam-son--tx.-bim-son/",
        "Ninh Bình": "https://aqicn.org/city/vietnam/ninh-binh/cuc-phuong--dong-phong--nho-quan-kttv-tram-cam-bien/",
        "Thái Bình": "https://aqicn.org/station/vietnam-th%C3%A1i-b%C3%ACnh%3A-c%E1%BA%A7u-th%C3%A1i-b%C3%ACnh-%C4%91.-tr%E1%BA%A7n-th%C3%A1i-t%C3%B4ng-p.-b%E1%BB%93-xuy%C3%AAn-tp-th%C3%A1i-b%C3%ACnh-kk/",
        "Hưng Yên": "https://aqicn.org/station/vietnam-hung-yen-city-h%C6%B0ng-y%C3%AAn%3A-s%E1%BB%91-437-nguy%E1%BB%85n-v%C4%83n-linh-tp-h%C6%B0ng-y%C3%AAn-kk/",
        "Bắc Giang": "https://aqicn.org/station/vietnam-l%E1%BA%A1ng-giang-district-b%E1%BA%AFc-giang%3A-khu-li%C3%AAn-c%C6%A1-quan-t%E1%BB%89nh-b%E1%BA%AFc-giang-p.-ng%C3%B4-quy%E1%BB%81n-tp.-b%E1%BA%AFc-giang-kk/",
        "Quảng Ninh": "https://aqicn.org/city/vietnam/quang-ninh/ubnd-tp-uong-bi/",
        "Việt Trì": "https://aqicn.org/city/vietnam/viet-tri/",
        "Sơn La": "https://aqicn.org/city/vietnam/son-la/p.-to-hieu-kttv-tram-cam-bien/",
        "Thái Nguyên": "https://aqicn.org/city/vietnam/thai-nguyen/duong-hung-vuong-tp-thai-nguyen/",
        "Lạng Sơn": "https://aqicn.org/city/vietnam/lang-son/xa-hong-phong-cao-loc/",
        "Hà Nội": "https://aqicn.org/station/vietnam-h%C3%A0-n%E1%BB%99i:-%C4%91hbk-c%E1%BB%95ng-parabol-%C4%91%C6%B0%E1%BB%9Dng-gi%E1%BA%A3i-ph%C3%B3ng-kk/",
        "H.C. Ørsted Institutet": "https://aqicn.org/city/denmark/copenhagen/h.c.-orsted-institutet/",
        "Risø": "https://aqicn.org/city/denmark/riso/",
        "Hedevej, Frederiks": "https://aqicn.org/station/denmark-frederiks-hedevej/",
        "H.C.Andersens Boulevard": "https://aqicn.org/city/denmark/copenhagen/h.c.andersens-boulevard/",
        "Møllebjergvej, Rudkøbing": "https://aqicn.org/station/denmark-rudk%C3%B8bing-m%C3%B8llebjergvej/",
        "Udsigten, Morud": "https://aqicn.org/station/denmark-morud-udsigten/",
        "Vardevej, Tarm": "https://aqicn.org/station/denmark-tarm-vardevej/",
        "Midtvej, Hobro": "https://aqicn.org/station/denmark-hobro-midtvej/",
        "Kjærslund, Aarhus": "https://aqicn.org/station/denmark-aarhus-kj%C3%A6rslund/",
        "Møllen, Skanderborg": "https://aqicn.org/station/denmark-skanderborg-m%C3%B8llen/",
        "Bøgehegnet, Greve Strand": "https://aqicn.org/station/denmark-greve-strand-b%C3%B8gehegnet/",
        "Rådhus, Odense": "https://aqicn.org/station/@503839/",
        "Østerbro, Aalborg": "https://aqicn.org/station/@503833/"  
    };
    const blogUrls = {
        "Cần Thơ": "https://www.evn.com.vn/d6/news/Thanh-pho-Xanh-Quoc-gia-Can-Tho-2024-thanh-qua-cua-nhung-no-luc-khong-ngung-nghi-100-635-126012.aspx",
        "Trà Vinh": "https://tapchitaichinh.vn/tra-vinh-nang-cao-y-thuc-cua-cong-dong-ve-bao-ve-rung-bao-ve-moi-truong.html",
        "Vũng Tàu": "https://truongchinhtri.baria-vungtau.gov.vn/article?item=1ef308b5fb154242e4dc19bac2656212",
        "Long An": "https://baolongan.vn/dong-bo-cac-giai-phap-bao-ve-moi-truong-a191044.html",
        "Tp Hồ Chí Minh": "https://thanhtin.net/van-de-moi-truong-o-tphcm-va-phuong-huong-giai-quyet/",
        "Bình Dương": "https://baoxaydung.com.vn/binh-duong-988-chat-thai-ran-sinh-hoat-duoc-xu-ly-trong-nam-2024-392890.html",
        "Bình Phước": "https://binhphuoc.gov.vn/vi/news/tin-tuc-su-kien-421/binh-phuoc-duy-tri-tot-hoat-dong-giam-sat-bao-ve-moi-truong-37146.html",
        "Lâm Đồng": "https://thiennhienmoitruong.vn/lam-dong-kiem-soat-cac-nguon-thai-nguy-co-gay-o-nhiem-moi-truong.html",
        "Ninh Thuận": "https://ninhthuan.gov.vn/portal/Pages/2024-4-25/Quy-hoach-phat-trien-do-thi-theo-huong-xanh-hien-dvv348x.aspx",
        "Nha Trang": "https://tapchicongthuong.vn/o-nhiem-moi-truong-bien-tai-vinh-nha-trang--danh-gia--nguyen-nhan-va-giai-phap-xanh-huong-den-phat-trien-ben-vung-132784.htm",
        "Khánh Hòa": "https://thiennhienmoitruong.vn/khanh-hoa-quan-ly-cac-nguon-thai-nguy-co-gay-o-nhiem-moi-truong.html",
        "Bình Định": "https://baotainguyenmoitruong.vn/binh-dinh-phat-huy-vai-tro-cua-quy-bao-ve-moi-truong-384142.html",
        "Gia Lai": "https://baotainguyenmoitruong.vn/gia-lai-den-2025-100-chu-nguon-thai-duoc-tuyen-truyen-kien-thuc-ve-phan-loai-rac-381335.html",
        "Quảng Nam": "https://baoquangnam.vn/quang-nam-quyet-liet-cai-thien-moi-truong-dau-tu-kinh-doanh-3149144.html",
        "Đà Nẵng": "https://danangfantasticity.com/du-lich-viet-nam/phat-dong-giai-bao-chi-xay-dung-da-nang-thanh-pho-moi-truong-nam-2024.html",
        "Thừa Thiên Huế": "https://baotainguyenmoitruong.vn/thua-thien-hue-huong-ung-ngay-moi-truong-the-gioi-2024-374963.html",
        "Quảng Bình": "https://www.baoquangbinh.vn/kinh-te/202503/cung-chung-tay-bao-ve-moi-truong-va-ung-pho-voi-bien-doi-khi-hau-2225092/",
        "Nghệ An": "https://laodong.vn/moi-truong/nghe-an-co-6-co-so-o-nhiem-nghiem-trong-chua-duoc-xu-ly-1428299.ldo",
        "Thanh Hoá": "https://baotainguyenmoitruong.vn/thanh-hoa-phat-trien-ben-vung-nganh-tai-nguyen-va-moi-truong-385203.html",
        "Ninh Bình": "https://bvhttdl.gov.vn/ninh-binh-bao-ve-moi-truong-di-san-quan-the-danh-thang-trang-an-20240919144949241.htm",
        "Thái Bình": "https://danviet.vn/thai-binh-tang-cuong-co-che-chinh-sach-ho-tro-bao-ve-moi-truong-cap-nuoc-sach-nong-thon-2024101510420898-d846163.html",
        "Hưng Yên": "https://baohungyen.vn/bao-ve-moi-truong-trong-san-xuat-cong-nghiep-3179574.html",
        "Bắc Giang": "https://atgt.bacgiang.gov.vn/chi-tiet-tin-tuc/-/asset_publisher/9DJTiagaQTlH/content/tong-hop-tin-tuc-ve-bac-giang-tren-bao-chi-ngay-22-23-3-2025/20181?inheritRedirect=false&redirect=https%3A%2F%2Fatgt.bacgiang.gov.vn%2Fchi-tiet-tin-tuc%2F-%2Fasset_publisher%2F9DJTiagaQTlH%2Fcontent%2Ftong-hop-tin-tuc-ve-bac-giang-tren-bao-chi-ngay-15-16-3-2025%2F20181",
        "Quảng Ninh": "https://baoquangninh.vn/bao-ve-moi-truong-song-hanh-cung-phat-trien-kinh-te-3317584.html",
        "Việt Trì": "https://microbelift.vn/thuc-trang-o-nhiem-moi-truong-o-viet-nam-nam-2024/",
        "Sơn La": "https://baoxaydung.com.vn/son-la-nang-cao-tieu-chi-moi-truong-trong-xay-dung-nong-thon-moi-390452.html",
        "Thái Nguyên": "https://sotp.thainguyen.gov.vn/web/guest/tin-tuc-hoat-dong-bao-ve-moi-truong",
        "Lạng Sơn": "https://thanhpho.langson.gov.vn/thong-tin-theo-linh-vuc/van-hoa-xa-hoi/thanh-pho-lang-son-ra-quan-tong-ve-sinh-moi-truong-huong-ung-ngay-moi-truong-the-gioi-5-6-va-thang-hanh-dong-vi-moi-truo.html",
        "Hà Nội": "https://baotainguyenmoitruong.vn/ha-noi-lai-dung-dau-the-gioi-ve-o-nhiem-khong-khi-385409.html",
        "H.C. Ørsted Institutet": "https://insideclimatenews.org/news/10122023/denmark-global-climate-policy-leader-high-ambitions/",
        "Risø": "https://www.riso.co.jp/english/company/eco/index.html",
        "Hedevej, Frederiks": "/blog/hedevej-frederiks",
        "H.C.Andersens Boulevard": "https://ccpi.org/country/dnk/",
        "Møllebjergvej, Rudkøbing": "/blog/mollebjergvej-rudkobing",
        "Udsigten, Morud": "/blog/udsigten-morud",
        "Vardevej, Tarm": "/blog/vardevej-tarm",
        "Midtvej, Hobro": "/blog/midtvej-hobro",
        "Kjærslund, Aarhus": "/blog/kjaerslund-aarhus",
        "Møllen, Skanderborg": "/blog/mollen-skanderborg",
        "Bøgehegnet, Greve Strand": "/blog/bogehegnet-greve-strand",
        "Rådhus, Odense": "/blog/radhus-odense",
        "Østerbro, Aalborg": "/blog/osterbro-aalborg"
    };
    const historyUrls = {
        "Cần Thơ": "https://lichsuvn.net/lich-su-can-tho",
        "Trà Vinh": "https://lichsuvn.net/lich-su-tra-vinh",
        "Vũng Tàu": "https://lichsuvn.net/lich-su-vung-tau",
        "Long An": "https://lichsuvn.net/lich-su-long-an",
        "Tp Hồ Chí Minh": "https://lichsuvn.net/lich-su-tp-ho-chi-minh",
        "Bình Dương": "https://lichsuvn.net/lich-su-binh-duong",
        "Bình Phước": "https://lichsuvn.net/lich-su-binh-phuoc",
        "Lâm Đồng": "https://lichsuvn.net/lich-su-lam-dong",
        "Ninh Thuận": "https://lichsuvn.net/lich-su-ninh-thuan",
        "Nha Trang": "https://lichsuvn.net/lich-su-nha-trang",
        "Khánh Hòa": "https://lichsuvn.net/lich-su-khanh-hoa",
        "Bình Định": "https://lichsuvn.net/lich-su-binh-dinh",
        "Gia Lai": "https://lichsuvn.net/lich-su-gia-lai",
        "Quảng Nam": "https://lichsuvn.net/lich-su-quang-nam",
        "Đà Nẵng": "https://lichsuvn.net/lich-su-da-nang",
        "Thừa Thiên Huế": "https://lichsuvn.net/lich-su-thua-thien-hue",
        "Quảng Bình": "https://lichsuvn.net/lich-su-quang-binh",
        "Nghệ An": "https://lichsuvn.net/lich-su-nghe-an",
        "Thanh Hoá": "https://lichsuvn.net/lich-su-thanh-hoa",
        "Ninh Bình": "https://lichsuvn.net/lich-su-ninh-binh",
        "Thái Bình": "https://lichsuvn.net/lich-su-thai-binh",
        "Hưng Yên": "https://lichsuvn.net/lich-su-hung-yen",
        "Bắc Giang": "https://lichsuvn.net/lich-su-bac-giang",
        "Quảng Ninh": "https://lichsuvn.net/lich-su-quang-ninh",
        "Việt Trì": "https://lichsuvn.net/lich-su-viet-tri",
        "Sơn La": "https://lichsuvn.net/lich-su-son-la",
        "Thái Nguyên": "https://lichsuvn.net/lich-su-thai-nguyen",
        "Lạng Sơn": "https://lichsuvn.net/lich-su-lang-son",
        "Hà Nội": "https://lichsuvn.net/lich-su-ha-noi",
        "H.C. Ørsted Institutet": "https://history.denmark.dk/hc-orsted-institutet",
        "Risø": "https://history.denmark.dk/riso",
        "Hedevej, Frederiks": "/history/hedevej-frederiks",
        "H.C.Andersens Boulevard": "https://history.denmark.dk/hc-andersens-boulevard",
        "Møllebjergvej, Rudkøbing": "/history/mollebjergvej-rudkobing",
        "Udsigten, Morud": "/history/udsigten-morud",
        "Vardevej, Tarm": "/history/vardevej-tarm",
        "Midtvej, Hobro": "/history/midtvej-hobro",
        "Kjærslund, Aarhus": "/history/kjaerslund-aarhus",
        "Møllen, Skanderborg": "/history/mollen-skanderborg",
        "Bøgehegnet, Greve Strand": "/history/bogehegnet-greve-strand",
        "Rådhus, Odense": "/history/radhus-odense",
        "Østerbro, Aalborg": "/history/osterbro-aalborg"
    };

    // Hàm xác định màu sắc dựa trên giá trị AQI
    function getColor(aqi) {
        if (aqi === 'N/A') return '#gray';
        aqi = parseInt(aqi);
        if (aqi <= 50) return '#00e400'; // Tốt
        if (aqi <= 100) return '#ffff00'; // Trung bình
        if (aqi <= 150) return '#ff7e00'; // Không lành mạnh cho nhóm nhạy cảm
        if (aqi <= 200) return '#ff0000'; // Không lành mạnh
        if (aqi <= 300) return '#8f3f97'; // Rất không lành mạnh
        return '#7e0023'; // Nguy hiểm
    }

    // Hàm đánh giá sức khỏe dựa trên AQI
    function getHealthImpact(aqi) {
        if (aqi === 'N/A') return 'Không có dữ liệu để đánh giá.';
        aqi = parseInt(aqi);
        if (aqi <= 50) return 'Tốt: Không ảnh hưởng đến sức khỏe hô hấp.';
        if (aqi <= 100) return 'Trung bình: Có thể gây lo ngại nhẹ cho người nhạy cảm (hen suyễn, bệnh phổi).';
        if (aqi <= 150) return 'Không lành mạnh cho nhóm nhạy cảm: Người già, trẻ em, người có bệnh hô hấp có thể gặp khó thở.';
        if (aqi <= 200) return 'Không lành mạnh: Mọi người có thể cảm thấy khó thở, ho. Nhóm nhạy cảm bị ảnh hưởng nghiêm trọng.';
        if (aqi <= 300) return 'Rất không lành mạnh: Nguy cơ cao gặp vấn đề hô hấp nghiêm trọng (khó thở, kích ứng phổi).';
        return 'Nguy hiểm: Toàn bộ dân số có nguy cơ cao gặp vấn đề hô hấp nghiêm trọng, có thể gây tổn thương phổi.';
    }

    // Hàm tính thời gian "updated X hours ago"
    function getTimeAgo(updateTime) {
        if (updateTime === 'N/A') return 'Không có dữ liệu';
        const updateDate = new Date(updateTime);
        const now = new Date();
        const diffInMs = now - updateDate;
        const diffInHours = Math.floor(diffInMs / (1000 * 60 * 60));
        if (diffInHours < 1) return `updated just now (${updateTime})`;
        return `updated ${diffInHours} hours ago (${updateTime})`;
    }

    // Hàm lấy dữ liệu AQI từ backend
    function fetchAQIData() {
        fetch('/aqi')
            .then(response => response.json())
            .then(data => {
                locations = data; // Lưu danh sách địa điểm để tìm kiếm
                data.forEach(location => {
                    const marker = L.circleMarker([location.lat, location.lon], {
                        radius: 8,
                        fillColor: getColor(location.aqi),
                        color: '#000',
                        weight: 1,
                        opacity: 1,
                        fillOpacity: 0.8
                    }).addTo(map);

                    // Xác định URL tùy chỉnh cho "Xem chi tiết"
                    let moreInfoUrl = customUrls[location.name] || 
                                     `https://aqicn.org/city/${location.name.toLowerCase().replace(/\s+/g, '-')}`;

                    // Xác định URL tùy chỉnh cho "Xem blog"
                    let blogUrl = blogUrls[location.name] || 
                                  `/blog/${location.name.toLowerCase().replace(/\s+/g, '-')}`;

                    // Xác định URL tùy chỉnh cho "Xem khu vực lịch sử"
                    let historyUrl = historyUrls[location.name] || 
                                    `/history/${location.name.toLowerCase().replace(/\s+/g, '-')}`;

                    // Tạo nội dung popup
                    marker.bindPopup(`
                        <div class="popup-content">
                            <h3>${location.name} (${location.country})</h3>
                            <div class="aqi-header">
                                <span class="aqi-value">${location.aqi === 'N/A' ? 'N/A' : location.aqi}</span>
                                <span class="aqi-status">${getHealthImpact(location.aqi).split(':')[0]}</span>
                            </div>
                            <p class="update-time">${getTimeAgo(location.update_time)}</p>
                            <div class="pollutants">
                                <div class="pollutant"><span>PM2.5:</span><span>${location.pm25 === 'N/A' ? 'N/A' : location.pm25}</span></div>
                                <div class="pollutant"><span>PM10:</span><span>${location.pm10 === 'N/A' ? 'N/A' : location.pm10}</span></div>
                                <div class="pollutant"><span>NO2:</span><span>${location.no2 === 'N/A' ? 'N/A' : location.no2}</span></div>
                                <div class="pollutant"><span>CO:</span><span>${location.co === 'N/A' ? 'N/A' : location.co}</span></div>
                                <div class="pollutant"><span>O3:</span><span>${location.o3 === 'N/A' ? 'N/A' : location.o3}</span></div>
                                <div class="pollutant"><span>SO2:</span><span>${location.so2 === 'N/A' ? 'N/A' : location.so2}</span></div>
                                <div class="pollutant"><span>Humidity (R.H.):</span><span>${location.humidity === 'N/A' ? 'N/A' : location.humidity}%</span></div>
                                <div class="pollutant"><span>Temperature:</span><span>${location.temperature === 'N/A' ? 'N/A' : location.temperature}°C</span></div>
                                <div class="pollutant"><span>Wind Speed:</span><span>${location.wind === 'N/A' ? 'N/A' : location.wind} m/s</span></div>
                            </div>
                            <div class="more-info">
                                <a href="${moreInfoUrl}" target="_blank">Xem chi tiết</a>
                                <a href="${blogUrl}" target="_blank">Xem blog</a>
                                <a href="${historyUrl}" target="_blank">Xem khu du lịch</a>
                            </div>
                        </div>
                    `);
                });
            })
            .catch(error => console.error('Error fetching AQI data:', error));
    }

    // Xử lý tìm kiếm
    searchInput.addEventListener('input', function () {
        const query = searchInput.value.toLowerCase();
        searchResults.innerHTML = '';

        if (query) {
            const filteredLocations = locations.filter(location =>
                location.name.toLowerCase().includes(query)
            );

            filteredLocations.forEach(location => {
                const li = document.createElement('li');
                li.textContent = `${location.name} (${location.country})`;
                li.addEventListener('click', function () {
                    map.setView([location.lat, location.lon], 10); // Zoom đến vị trí thành phố
                    searchResults.innerHTML = '';
                    searchInput.value = '';
                });
                searchResults.appendChild(li);
            });
        }
    });

    // Gọi hàm lấy dữ liệu khi trang tải
    fetchAQIData();

    // Cập nhật dữ liệu mỗi 1 giờ
    setInterval(fetchAQIData, 3600000);
});