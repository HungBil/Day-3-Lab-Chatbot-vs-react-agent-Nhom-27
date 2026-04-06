"""
Travel Planner Tools for ReAct Agent — Lab 3.
Scenario: Smart Travel Planner that helps users plan trips with
destination info, weather, hotel pricing, food costs, attractions, and budget checking.

All data is mock/simulated for lab purposes.
Each function takes string arguments and returns a string result.
"""

# ============================================================
# MOCK DATABASES
# ============================================================

DESTINATIONS = {
    "da nang": {
        "name": "Đà Nẵng",
        "region": "Miền Trung",
        "description": "Thành phố biển nổi tiếng với bãi biển Mỹ Khê, cầu Rồng, và Bà Nà Hills.",
        "specialties": "Mì Quảng, bánh tráng cuốn thịt heo, bún chả cá",
        "best_season": "Tháng 3 - 8",
    },
    "phu quoc": {
        "name": "Phú Quốc",
        "region": "Miền Nam",
        "description": "Đảo ngọc với biển trong xanh, hoàng hôn đẹp, và nước mắm nổi tiếng.",
        "specialties": "Bún quậy, gỏi cá trích, nước mắm Phú Quốc",
        "best_season": "Tháng 11 - 4",
    },
    "sapa": {
        "name": "Sa Pa",
        "region": "Tây Bắc",
        "description": "Vùng núi có ruộng bậc thang, đỉnh Fansipan, và văn hóa dân tộc H'Mông.",
        "specialties": "Thắng cố, cá suối nướng, rượu táo mèo",
        "best_season": "Tháng 9 - 11 (mùa lúa chín), Tháng 12 - 2 (tuyết)",
    },
    "hoi an": {
        "name": "Hội An",
        "region": "Miền Trung",
        "description": "Phố cổ di sản UNESCO, đèn lồng, và ẩm thực đường phố hấp dẫn.",
        "specialties": "Cao lầu, bánh mì Phượng, cơm gà Hội An",
        "best_season": "Tháng 2 - 5",
    },
    "nha trang": {
        "name": "Nha Trang",
        "region": "Miền Trung",
        "description": "Thành phố biển với Vinpearl, tháp Bà Ponagar, và hải sản tươi ngon.",
        "specialties": "Bún chả cá, bánh căn, nem nướng Ninh Hòa",
        "best_season": "Tháng 1 - 8",
    },
    "ha long": {
        "name": "Hạ Long",
        "region": "Miền Bắc",
        "description": "Vịnh di sản UNESCO với hàng nghìn hòn đảo đá vôi, du thuyền qua đêm.",
        "specialties": "Chả mực, sá sùng, hàu nướng",
        "best_season": "Tháng 3 - 5, Tháng 9 - 11",
    },
    "da lat": {
        "name": "Đà Lạt",
        "region": "Tây Nguyên",
        "description": "Thành phố ngàn hoa, khí hậu mát mẻ quanh năm, kiến trúc Pháp.",
        "specialties": "Bánh tráng nướng, kem bơ, atiso",
        "best_season": "Tháng 11 - 3",
    },
}

WEATHER_DATA = {
    # (city, month) -> weather info
    ("da nang", "1"):  {"temp": "20-25°C", "condition": "Mưa nhẹ, se lạnh", "advice": "Mang áo khoác mỏng."},
    ("da nang", "2"):  {"temp": "21-26°C", "condition": "Ít mưa, trời dịu mát", "advice": "Thời tiết dễ chịu cho tham quan."},
    ("da nang", "3"):  {"temp": "23-28°C", "condition": "Nắng nhẹ, ít mưa", "advice": "Bắt đầu mùa đẹp, lý tưởng du lịch."},
    ("da nang", "4"):  {"temp": "25-30°C", "condition": "Nắng ấm", "advice": "Thời tiết tốt cho hoạt động biển."},
    ("da nang", "5"):  {"temp": "27-33°C", "condition": "Nắng nóng", "advice": "Thoa kem chống nắng, uống nhiều nước."},
    ("da nang", "6"):  {"temp": "28-35°C", "condition": "Nắng nóng, ít mưa", "advice": "Lý tưởng cho tắm biển. Tránh nắng 11h-14h."},
    ("da nang", "7"):  {"temp": "27-34°C", "condition": "Nắng, có mưa rào chiều", "advice": "Mang ô phòng mưa chiều."},
    ("da nang", "8"):  {"temp": "26-33°C", "condition": "Nắng xen mưa", "advice": "Vẫn đẹp nhưng lưu ý mưa bất chợt."},
    ("da nang", "9"):  {"temp": "24-30°C", "condition": "Mưa nhiều, có bão", "advice": "Cân nhắc kỹ, mùa bão miền Trung."},
    ("da nang", "10"): {"temp": "23-28°C", "condition": "Mưa lớn kéo dài", "advice": "Không khuyến khích du lịch biển."},
    ("da nang", "11"): {"temp": "22-27°C", "condition": "Mưa nhiều", "advice": "Mùa mưa, nên chọn thời điểm khác."},
    ("da nang", "12"): {"temp": "20-25°C", "condition": "Mưa, se lạnh", "advice": "Mang áo ấm, chuẩn bị ô."},
    ("sapa", "1"):  {"temp": "3-10°C", "condition": "Rất lạnh, có sương muối", "advice": "Mang áo ấm dày. Có thể có tuyết."},
    ("sapa", "6"):  {"temp": "18-25°C", "condition": "Mưa nhiều, mát mẻ", "advice": "Mùa mưa, đường trơn."},
    ("sapa", "10"): {"temp": "12-20°C", "condition": "Lúa chín vàng, mát", "advice": "Mùa đẹp nhất! Ruộng bậc thang vàng rực."},
    ("sapa", "12"): {"temp": "2-8°C", "condition": "Rất lạnh, có thể có tuyết", "advice": "Mang áo phao/áo lông. Cơ hội ngắm tuyết."},
    ("phu quoc", "1"):  {"temp": "25-30°C", "condition": "Nắng đẹp, khô ráo", "advice": "Mùa cao điểm, rất lý tưởng."},
    ("phu quoc", "6"):  {"temp": "27-32°C", "condition": "Mưa nhiều", "advice": "Mùa thấp điểm, giá rẻ nhưng mưa."},
    ("phu quoc", "12"): {"temp": "25-30°C", "condition": "Nắng, mát mẻ", "advice": "Thời điểm tuyệt vời, nên đặt sớm."},
    ("hoi an", "1"):  {"temp": "20-24°C", "condition": "Ít mưa, mát", "advice": "Dễ chịu cho dạo phố cổ."},
    ("hoi an", "3"):  {"temp": "23-28°C", "condition": "Nắng nhẹ", "advice": "Tuyệt vời cho tham quan và chụp ảnh."},
    ("hoi an", "8"):  {"temp": "26-33°C", "condition": "Nắng nóng", "advice": "Nóng, nên đi sớm hoặc chiều tối."},
    ("nha trang", "1"):  {"temp": "22-27°C", "condition": "Ít mưa, biển đẹp", "advice": "Mùa lý tưởng, nước trong xanh."},
    ("nha trang", "6"):  {"temp": "27-33°C", "condition": "Nắng nóng", "advice": "Tốt cho biển, thoa kem chống nắng."},
    ("nha trang", "10"): {"temp": "24-28°C", "condition": "Mưa lớn, biển động", "advice": "Không nên đi biển, nguy hiểm."},
    ("ha long", "3"):  {"temp": "18-22°C", "condition": "Sương mù lãng mạn", "advice": "Cảnh đẹp huyền ảo, hơi lạnh."},
    ("ha long", "6"):  {"temp": "28-33°C", "condition": "Nắng nóng, biển đẹp", "advice": "Mùa đẹp, nên đi du thuyền."},
    ("ha long", "11"): {"temp": "20-25°C", "condition": "Se lạnh, ít mưa", "advice": "Thời tiết dễ chịu, ít đông đúc."},
    ("da lat", "1"):  {"temp": "12-22°C", "condition": "Se lạnh, nắng nhẹ", "advice": "Mát mẻ, lý tưởng cho dạo phố."},
    ("da lat", "6"):  {"temp": "17-25°C", "condition": "Mưa chiều, mát", "advice": "Mang áo khoác và ô."},
    ("da lat", "12"): {"temp": "10-20°C", "condition": "Lạnh, sương mù sáng", "advice": "Mùa đẹp nhất, hoa nở rộ."},
}

HOTEL_PRICES = {
    # (city, star_level) -> price_per_night (VND)
    ("da nang", "3"):   500000,
    ("da nang", "4"):   800000,
    ("da nang", "5"):   1500000,
    ("phu quoc", "3"):  600000,
    ("phu quoc", "4"):  1000000,
    ("phu quoc", "5"):  2500000,
    ("sapa", "3"):      400000,
    ("sapa", "4"):      700000,
    ("sapa", "5"):      1200000,
    ("hoi an", "3"):    450000,
    ("hoi an", "4"):    750000,
    ("hoi an", "5"):    1800000,
    ("nha trang", "3"): 500000,
    ("nha trang", "4"): 900000,
    ("nha trang", "5"): 2000000,
    ("ha long", "3"):   550000,
    ("ha long", "4"):   950000,
    ("ha long", "5"):   2200000,
    ("da lat", "3"):    400000,
    ("da lat", "4"):    650000,
    ("da lat", "5"):    1100000,
}

HOTEL_SUGGESTIONS = {
    ("da nang", "3"):   "Gợi ý: Zen Diamond, Fivitel",
    ("da nang", "4"):   "Gợi ý: Mường Thanh, Novotel",
    ("da nang", "5"):   "Gợi ý: InterContinental, Hyatt Regency",
    ("phu quoc", "3"):  "Gợi ý: Sea Star, Bamboo Resort",
    ("phu quoc", "4"):  "Gợi ý: Dusit Princess, Sol by Meliá",
    ("phu quoc", "5"):  "Gợi ý: JW Marriott, InterContinental",
    ("sapa", "3"):      "Gợi ý: Sapa Panorama, Bamboo Sapa",
    ("sapa", "4"):      "Gợi ý: Hotel de la Coupole, Pao's Sapa",
    ("sapa", "5"):      "Gợi ý: Silk Path Grand, BB Sapa Resort",
    ("hoi an", "3"):    "Gợi ý: Hoi An Historic, Pho Hoi Riverside",
    ("hoi an", "4"):    "Gợi ý: Allegro Hoi An, Little Hoi An",
    ("hoi an", "5"):    "Gợi ý: Four Seasons Nam Hai, Anantara",
    ("nha trang", "3"): "Gợi ý: Dendro Gold, The Light",
    ("nha trang", "4"): "Gợi ý: Havana, StarCity",
    ("nha trang", "5"): "Gợi ý: Vinpearl Resort, Sheraton",
    ("ha long", "3"):   "Gợi ý: BMC Thăng Long, Hạ Long Park",
    ("ha long", "4"):   "Gợi ý: Wyndham, Novotel Hạ Long",
    ("ha long", "5"):   "Gợi ý: FLC Grand, Vinpearl Resort",
    ("da lat", "3"):    "Gợi ý: Sao Băng, Tulip Hotel",
    ("da lat", "4"):    "Gợi ý: Terracotta, Swiss-Bel Đà Lạt",
    ("da lat", "5"):    "Gợi ý: Ana Mandara Villas, DaLat Palace",
}

FOOD_COSTS = {
    # (city, budget_level) -> cost_per_day (VND)
    ("da nang", "low"):     150000,
    ("da nang", "mid"):     300000,
    ("da nang", "high"):    600000,
    ("phu quoc", "low"):    200000,
    ("phu quoc", "mid"):    400000,
    ("phu quoc", "high"):   800000,
    ("sapa", "low"):        120000,
    ("sapa", "mid"):        250000,
    ("sapa", "high"):       500000,
    ("hoi an", "low"):      130000,
    ("hoi an", "mid"):      280000,
    ("hoi an", "high"):     550000,
    ("nha trang", "low"):   150000,
    ("nha trang", "mid"):   350000,
    ("nha trang", "high"):  700000,
    ("ha long", "low"):     180000,
    ("ha long", "mid"):     350000,
    ("ha long", "high"):    700000,
    ("da lat", "low"):      120000,
    ("da lat", "mid"):      250000,
    ("da lat", "high"):     500000,
}

ATTRACTIONS = {
    ("da nang", "beach"): [
        ("Biển Mỹ Khê", "Miễn phí", "Bãi biển đẹp nhất Việt Nam theo Forbes"),
        ("Bán đảo Sơn Trà", "Miễn phí", "Ngắm voọc và cảnh biển từ trên cao"),
        ("Bà Nà Hills", "900,000 VNĐ", "Cầu Vàng, khu vui chơi Fantasy Park"),
    ],
    ("da nang", "culture"): [
        ("Ngũ Hành Sơn", "40,000 VNĐ", "Núi đá cẩm thạch, chùa cổ"),
        ("Bảo tàng Chăm", "60,000 VNĐ", "Di sản điêu khắc Chăm Pa"),
        ("Chùa Linh Ứng", "Miễn phí", "Tượng Phật Quan Thế Âm lớn nhất VN"),
    ],
    ("da nang", "adventure"): [
        ("Leo Bà Nà từ chân núi", "Miễn phí", "Trekking 3-4 giờ qua rừng"),
        ("Lặn biển Sơn Trà", "500,000 VNĐ", "Ngắm san hô, tour nửa ngày"),
        ("Chèo SUP sông Hàn", "200,000 VNĐ", "Hoạt động buổi chiều thú vị"),
    ],
    ("da nang", "food"): [
        ("Mì Quảng Bà Mua", "35,000 VNĐ", "Quán nổi tiếng nhất Đà Nẵng"),
        ("Bánh tráng Bà Hường", "50,000 VNĐ", "Trải nghiệm đặc sản miền Trung"),
        ("Chợ Hàn", "Miễn phí vào", "Khu ẩm thực đường phố phong phú"),
    ],
    ("phu quoc", "beach"): [
        ("Bãi Sao", "Miễn phí", "Bãi biển cát trắng đẹp nhất đảo"),
        ("Hòn Thơm", "500,000 VNĐ", "Cáp treo vượt biển + công viên nước"),
        ("Lặn ngắm san hô", "350,000 VNĐ", "Tour nửa ngày, ngắm cá nhiệt đới"),
    ],
    ("phu quoc", "culture"): [
        ("Nhà tù Phú Quốc", "Miễn phí", "Di tích lịch sử chiến tranh"),
        ("Dinh Cậu", "Miễn phí", "Ngôi đền linh thiêng trên mỏm đá"),
        ("Làng chài Hàm Ninh", "Miễn phí", "Hải sản tươi, vibe hoang sơ"),
    ],
    ("sapa", "culture"): [
        ("Bản Cát Cát", "70,000 VNĐ", "Bản dân tộc H'Mông, thác nước"),
        ("Nhà thờ Sa Pa", "Miễn phí", "Kiến trúc Pháp, chợ tình cuối tuần"),
        ("Bảo tàng Sa Pa", "30,000 VNĐ", "Văn hóa các dân tộc Tây Bắc"),
    ],
    ("sapa", "adventure"): [
        ("Chinh phục Fansipan", "800,000 VNĐ", "Nóc nhà Đông Dương, cáp treo hoặc leo bộ 2 ngày"),
        ("Trekking Tả Phìn", "Miễn phí", "Đi bộ qua ruộng bậc thang"),
        ("Đèo Ô Quy Hồ", "Miễn phí", "Cung đường đèo đẹp nhất Tây Bắc"),
    ],
    ("hoi an", "culture"): [
        ("Phố cổ Hội An", "120,000 VNĐ", "Vé tham quan 5 điểm di tích"),
        ("Chùa Cầu", "Có trong vé phố cổ", "Biểu tượng Hội An 400 năm"),
        ("Làng rau Trà Quế", "50,000 VNĐ", "Trải nghiệm làm nông dân"),
    ],
    ("hoi an", "beach"): [
        ("Biển An Bàng", "Miễn phí", "Bãi biển đẹp, yên tĩnh"),
        ("Cù Lao Chàm", "500,000 VNĐ", "Tour 1 ngày lặn biển + làng chài"),
    ],
    ("nha trang", "beach"): [
        ("Vinpearl Land", "880,000 VNĐ", "Cáp treo + khu vui chơi cả ngày"),
        ("Hòn Mun", "350,000 VNĐ", "Lặn ngắm san hô đẹp nhất VN"),
        ("Biển Trần Phú", "Miễn phí", "Bãi biển trung tâm, sóng êm"),
    ],
    ("nha trang", "culture"): [
        ("Tháp Bà Ponagar", "22,000 VNĐ", "Di tích Chăm Pa ngàn năm tuổi"),
        ("Long Sơn Tự", "Miễn phí", "Chùa có tượng Phật trắng lớn"),
    ],
    ("ha long", "adventure"): [
        ("Du thuyền qua đêm", "1,500,000 VNĐ", "Ngắm vịnh, kayak, hang Sửng Sốt"),
        ("Kayak trên vịnh", "200,000 VNĐ", "Chèo kayak qua hang luồn"),
        ("Leo núi Bài Thơ", "Miễn phí", "View toàn cảnh vịnh Hạ Long"),
    ],
    ("da lat", "culture"): [
        ("Dinh Bảo Đại", "30,000 VNĐ", "Dinh thự vua cũ, kiến trúc Pháp"),
        ("Thiền viện Trúc Lâm", "Miễn phí", "Cáp treo + chùa giữa rừng thông"),
        ("Chợ Đà Lạt", "Miễn phí", "Chợ đêm, street food nổi tiếng"),
    ],
    ("da lat", "adventure"): [
        ("Canyoning Datanla", "1,200,000 VNĐ", "Abseiling thác nước, mạo hiểm"),
        ("Đồi chè Cầu Đất", "Miễn phí", "Cảnh đẹp cho chụp ảnh"),
        ("Langbiang", "80,000 VNĐ", "Đỉnh núi ngắm toàn cảnh Đà Lạt"),
    ],
}


# ============================================================
# TOOL FUNCTIONS
# ============================================================

def search_destination(city: str) -> str:
    """
    Search for basic information about a travel destination in Vietnam.

    Input: city (string) - name of the city, e.g. "Đà Nẵng" or "Da Nang".
    Returns: city name, region, description, local specialties, and best travel season.
    Example: search_destination("Đà Nẵng") -> "Đà Nẵng (Miền Trung): Thành phố biển..."
    """
    key = _normalize_city(city)
    if key in DESTINATIONS:
        d = DESTINATIONS[key]
        return (
            f"{d['name']} ({d['region']}): {d['description']} "
            f"Đặc sản: {d['specialties']}. "
            f"Mùa đẹp nhất: {d['best_season']}."
        )
    available = ", ".join(DESTINATIONS[k]["name"] for k in DESTINATIONS)
    return f"Không tìm thấy thông tin về '{city}'. Các điểm đến có sẵn: {available}."


def get_weather(city: str, month: str) -> str:
    """
    Get weather information for a city in a specific month.

    Input: city (string) - city name, e.g. "Đà Nẵng". month (string) - month number 1-12, e.g. "6".
    Returns: temperature range, weather condition, and travel advice for that month.
    Example: get_weather("Đà Nẵng", "6") -> "Tháng 6 tại Đà Nẵng: 28-35°C, Nắng nóng..."
    """
    key = _normalize_city(city)
    m = str(month).strip()

    weather = WEATHER_DATA.get((key, m))
    if weather:
        city_name = DESTINATIONS.get(key, {}).get("name", city)
        return (
            f"Tháng {m} tại {city_name}: {weather['temp']}, "
            f"{weather['condition']}. "
            f"Lời khuyên: {weather['advice']}"
        )

    # Check if city exists but month data not available
    if key in DESTINATIONS:
        city_name = DESTINATIONS[key]["name"]
        return (
            f"Không có dữ liệu thời tiết chi tiết cho {city_name} tháng {m}. "
            f"Mùa đẹp nhất: {DESTINATIONS[key]['best_season']}."
        )

    available = ", ".join(DESTINATIONS[k]["name"] for k in DESTINATIONS)
    return f"Không tìm thấy thông tin thời tiết cho '{city}'. Các điểm đến có sẵn: {available}."


def get_hotel_price(city: str, star_level: str, nights: str) -> str:
    """
    Get estimated hotel price for a city based on star level and number of nights.

    Input: city (string) - city name. star_level (string) - hotel star rating "3", "4", or "5". nights (string) - number of nights.
    Returns: price per night, total cost, and hotel suggestions.
    Example: get_hotel_price("Đà Nẵng", "3", "3") -> "Khách sạn 3 sao tại Đà Nẵng: 500,000 VNĐ/đêm × 3 đêm = 1,500,000 VNĐ."
    """
    key = _normalize_city(city)
    stars = str(star_level).strip()
    try:
        num_nights = int(nights)
    except (ValueError, TypeError):
        return f"Lỗi: Số đêm '{nights}' không hợp lệ. Vui lòng nhập số nguyên (vd: 3)."

    if num_nights <= 0:
        return "Lỗi: Số đêm phải lớn hơn 0."

    if stars not in ("3", "4", "5"):
        return f"Lỗi: Hạng sao '{star_level}' không hợp lệ. Chỉ hỗ trợ: 3, 4, 5 sao."

    price = HOTEL_PRICES.get((key, stars))
    if price:
        total = price * num_nights
        city_name = DESTINATIONS.get(key, {}).get("name", city)
        suggestion = HOTEL_SUGGESTIONS.get((key, stars), "")
        return (
            f"Khách sạn {stars} sao tại {city_name}: "
            f"{price:,.0f} VNĐ/đêm × {num_nights} đêm = {total:,.0f} VNĐ. "
            f"{suggestion}"
        )

    if key in DESTINATIONS:
        city_name = DESTINATIONS[key]["name"]
        return f"Không có dữ liệu giá khách sạn {stars} sao tại {city_name}."

    available = ", ".join(DESTINATIONS[k]["name"] for k in DESTINATIONS)
    return f"Không tìm thấy thông tin khách sạn cho '{city}'. Các điểm đến có sẵn: {available}."


def estimate_food_cost(city: str, days: str, budget_level: str) -> str:
    """
    Estimate daily and total food cost for a trip.

    Input: city (string) - city name. days (string) - number of days. budget_level (string) - one of "low", "mid", or "high".
    - "low": street food, local eateries.
    - "mid": mix of local restaurants and nice cafes.
    - "high": upscale restaurants and seafood.
    Returns: cost per day and total food budget.
    Example: estimate_food_cost("Đà Nẵng", "3", "mid") -> "Ăn uống mức trung bình tại Đà Nẵng: 300,000 VNĐ/ngày × 3 ngày = 900,000 VNĐ."
    """
    key = _normalize_city(city)
    level = str(budget_level).strip().lower()
    try:
        num_days = int(days)
    except (ValueError, TypeError):
        return f"Lỗi: Số ngày '{days}' không hợp lệ. Vui lòng nhập số nguyên (vd: 3)."

    if num_days <= 0:
        return "Lỗi: Số ngày phải lớn hơn 0."

    level_labels = {"low": "tiết kiệm", "mid": "trung bình", "high": "cao cấp"}
    if level not in level_labels:
        return f"Lỗi: Mức ngân sách '{budget_level}' không hợp lệ. Chỉ hỗ trợ: low, mid, high."

    cost = FOOD_COSTS.get((key, level))
    if cost:
        total = cost * num_days
        city_name = DESTINATIONS.get(key, {}).get("name", city)
        return (
            f"Ăn uống mức {level_labels[level]} tại {city_name}: "
            f"{cost:,.0f} VNĐ/ngày × {num_days} ngày = {total:,.0f} VNĐ."
        )

    if key in DESTINATIONS:
        city_name = DESTINATIONS[key]["name"]
        return f"Không có dữ liệu chi phí ăn uống tại {city_name}."

    available = ", ".join(DESTINATIONS[k]["name"] for k in DESTINATIONS)
    return f"Không tìm thấy thông tin cho '{city}'. Các điểm đến có sẵn: {available}."


def search_attraction(city: str, interest: str) -> str:
    """
    Search for tourist attractions based on city and interest category.

    Input: city (string) - city name. interest (string) - one of "beach", "culture", "adventure", or "food".
    Returns: list of top attractions with entry fees and short descriptions.
    Example: search_attraction("Đà Nẵng", "beach") -> "1. Biển Mỹ Khê (Miễn phí) - Bãi biển đẹp nhất VN..."
    """
    key = _normalize_city(city)
    cat = str(interest).strip().lower()

    valid_interests = ["beach", "culture", "adventure", "food"]
    if cat not in valid_interests:
        return (
            f"Lỗi: Loại sở thích '{interest}' không hợp lệ. "
            f"Chỉ hỗ trợ: {', '.join(valid_interests)}."
        )

    attractions = ATTRACTIONS.get((key, cat))
    if attractions:
        city_name = DESTINATIONS.get(key, {}).get("name", city)
        lines = [f"Địa điểm {cat} tại {city_name}:"]
        total_cost = 0
        for i, (name, fee, desc) in enumerate(attractions, 1):
            lines.append(f"  {i}. {name} (Vé: {fee}) — {desc}")
            # Extract numeric cost for total estimate
            try:
                cost_num = int(fee.replace(",", "").replace(".", "").split()[0])
                total_cost += cost_num
            except (ValueError, IndexError):
                pass
        if total_cost > 0:
            lines.append(f"Tổng chi phí vé tham quan ước tính: {total_cost:,} VNĐ")
        return "\n".join(lines)

    if key in DESTINATIONS:
        city_name = DESTINATIONS[key]["name"]
        available_cats = [cat for (c, cat) in ATTRACTIONS.keys() if c == key]
        return (
            f"Không có dữ liệu địa điểm '{interest}' tại {city_name}. "
            f"Các loại có sẵn: {', '.join(available_cats)}."
        )

    available = ", ".join(DESTINATIONS[k]["name"] for k in DESTINATIONS)
    return f"Không tìm thấy thông tin cho '{city}'. Các điểm đến có sẵn: {available}."


def check_budget(total_cost: str, budget: str) -> str:
    """
    Compare total estimated cost against the user's budget.

    Input: total_cost (string) - total estimated trip cost in VND, e.g. "3800000". budget (string) - user's budget in VND, e.g. "5000000".
    Returns: comparison result with recommendation (within budget, over budget, or plenty of room).
    Example: check_budget("3800000", "5000000") -> "Tổng chi phí: 3,800,000 VNĐ | Ngân sách: 5,000,000 VNĐ | Còn dư: 1,200,000 VNĐ ✅"
    """
    try:
        cost = float(total_cost)
    except (ValueError, TypeError):
        return f"Lỗi: Tổng chi phí '{total_cost}' không hợp lệ. Nhập số (vd: 3800000)."

    try:
        bgt = float(budget)
    except (ValueError, TypeError):
        return f"Lỗi: Ngân sách '{budget}' không hợp lệ. Nhập số (vd: 5000000)."

    diff = bgt - cost
    result = (
        f"Tổng chi phí: {cost:,.0f} VNĐ | "
        f"Ngân sách: {bgt:,.0f} VNĐ | "
    )

    if diff > 0:
        percent_remaining = (diff / bgt) * 100
        if percent_remaining > 30:
            result += f"Còn dư: {diff:,.0f} VNĐ ({percent_remaining:.0f}%) ✅ Rất thoải mái! Có thể nâng hạng khách sạn hoặc thêm hoạt động."
        else:
            result += f"Còn dư: {diff:,.0f} VNĐ ({percent_remaining:.0f}%) ✅ Vừa đủ."
    elif diff == 0:
        result += "Vừa khít ngân sách! ⚠️ Nên dự phòng thêm 10-15%."
    else:
        result += f"VƯỢT ngân sách: {abs(diff):,.0f} VNĐ ❌ Gợi ý: giảm hạng khách sạn, ăn tiết kiệm hơn, hoặc giảm ngày."

    return result


# ============================================================
# HELPER
# ============================================================

def _normalize_city(city: str) -> str:
    """
    Normalize city input to match our database keys.
    Handles Vietnamese diacritics and common variations.
    """
    mapping = {
        # Da Nang variants
        "đà nẵng": "da nang", "da nang": "da nang", "danang": "da nang",
        "đà nẵng city": "da nang",
        # Phu Quoc variants
        "phú quốc": "phu quoc", "phu quoc": "phu quoc", "phuquoc": "phu quoc",
        # Sa Pa variants
        "sa pa": "sapa", "sapa": "sapa", "sả pa": "sapa", "lào cai": "sapa",
        # Hoi An variants
        "hội an": "hoi an", "hoi an": "hoi an", "hoian": "hoi an",
        # Nha Trang variants
        "nha trang": "nha trang", "nhatrang": "nha trang",
        # Ha Long variants
        "hạ long": "ha long", "ha long": "ha long", "halong": "ha long",
        "vịnh hạ long": "ha long",
        # Da Lat variants
        "đà lạt": "da lat", "da lat": "da lat", "dalat": "da lat",
    }
    normalized = city.strip().lower()
    return mapping.get(normalized, normalized)
