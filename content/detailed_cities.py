"""
Detailed City Content Database
도시별 상세 콘텐츠 데이터베이스 - 블로거 스타일
"""

# 국가별 비상 연락처 (정확한 정보)
COUNTRY_EMERGENCY = {
    "France": {"police": "17", "ambulance": "15", "fire": "18", "general": "112", "korean_embassy": "+33-1-47-53-01-01"},
    "Italy": {"police": "113", "ambulance": "118", "fire": "115", "general": "112", "korean_embassy": "+39-06-802-461"},
    "Spain": {"police": "091", "ambulance": "061", "fire": "080", "general": "112", "korean_embassy": "+34-91-353-2000"},
    "UK": {"police": "999", "ambulance": "999", "fire": "999", "general": "999", "korean_embassy": "+44-20-7227-5500"},
    "Germany": {"police": "110", "ambulance": "112", "fire": "112", "general": "112", "korean_embassy": "+49-30-203-610"},
    "Netherlands": {"police": "112", "ambulance": "112", "fire": "112", "general": "112", "korean_embassy": "+31-70-311-8700"},
    "Austria": {"police": "133", "ambulance": "144", "fire": "122", "general": "112", "korean_embassy": "+43-1-533-8681"},
    "Greece": {"police": "100", "ambulance": "166", "fire": "199", "general": "112", "korean_embassy": "+30-210-698-5800"},
    "Portugal": {"police": "112", "ambulance": "112", "fire": "112", "general": "112", "korean_embassy": "+351-21-390-4300"},
    "Czech Republic": {"police": "158", "ambulance": "155", "fire": "150", "general": "112", "korean_embassy": "+420-2-5732-1355"},
    "Hungary": {"police": "107", "ambulance": "104", "fire": "105", "general": "112", "korean_embassy": "+36-1-462-9700"},
    "Thailand": {"police": "191", "ambulance": "1669", "fire": "199", "general": "1155", "korean_embassy": "+66-2-247-7530"},
    "Singapore": {"police": "999", "ambulance": "995", "fire": "995", "general": "999", "korean_embassy": "+65-6256-1188"},
    "Malaysia": {"police": "999", "ambulance": "999", "fire": "994", "general": "999", "korean_embassy": "+60-3-4251-2336"},
    "Indonesia": {"police": "110", "ambulance": "118", "fire": "113", "general": "112", "korean_embassy": "+62-21-2939-1710"},
    "Vietnam": {"police": "113", "ambulance": "115", "fire": "114", "general": "112", "korean_embassy": "+84-24-3831-5116"},
    "Philippines": {"police": "117", "ambulance": "911", "fire": "911", "general": "911", "korean_embassy": "+63-2-8856-9210"},
    "Japan": {"police": "110", "ambulance": "119", "fire": "119", "general": "110", "korean_embassy": "+81-3-3452-7611"},
    "USA": {"police": "911", "ambulance": "911", "fire": "911", "general": "911", "korean_embassy": "+1-202-939-5600"},
    "Australia": {"police": "000", "ambulance": "000", "fire": "000", "general": "000", "korean_embassy": "+61-2-6270-4100"},
    "UAE": {"police": "999", "ambulance": "998", "fire": "997", "general": "999", "korean_embassy": "+971-2-443-4536"},
    "Turkey": {"police": "155", "ambulance": "112", "fire": "110", "general": "112", "korean_embassy": "+90-312-468-4825"},
}

# 도시별 상세 콘텐츠 - 파리
PARIS_DETAILED = {
    "day1": {
        "title": "도착 & 마레 지구에서 파리 감성 익히기",
        "theme": "느긋한 첫날, 17세기 귀족 거리를 걷다",
        "content": """📍 예약 필요: 없음

✈️ 공항에서 시내 이동
샤를 드 골 공항(CDG)에서 시내로는 공항 리무진 버스 'Le Bus Direct'(16유로, 45분)가 가장 편해요. 짐이 많거나 처음 오신다면 이걸 추천드려요. RER B선(10.3유로, 35분)은 더 빠르지만 계단이 많아서 짐 옮기기가 힘들어요.

🏨 숙소 체크인 후 첫 산책
숙소는 마레(Le Marais, 3·4구)나 생제륧망데프레(Saint-Germain-des-Prés, 6구) 중심으로 잡는 것이 좋아요. 오늘은 마레 지구를 둘러볼 거예요.

📍 Place des Vosges (보즈 광장)
파리에서 가장 오래된 광장으로, 1605년부터 이어진 400년 역사를 자랑해요. 빨간 벽돌 건축물이 사각형으로 둘러싸고 있어서 사진 찍기 딱 좋아요. 빅토르 위고의 집이 있던 곳으로, 여기 벤치에 앉아 있으면 마치 영화 'Before Sunset'에 나오는 것 같은 기분이 들어요.

🚶 이동: 메트로 1호선 'Saint-Paul'역에서 도보 5분

🛍️ Rue des Rosiers (로시에 거리)
마레 지구의 메인 거리예요. 과거 유대인 거주지였던 이곳은 지금 빈티지 샵과 트렌디한 카페가 가득한 핫플레이스로 변했어요. Kilo Shop에서는 빈티지 옷을 무게로 팔아요(kg당 20-40유로). 득템하면 평생 입을 수 있는 물건을 찾을 수 있어요.

🚶 이동: 보즈 광장에서 도보 3분

🍽️ 점심: L'As du Fallafel
로시에 거리에서 가장 유명한 팔라펠 전문점이에요. 줄이 30미터 이상 길게 늘어서 있지만 10-15분이면 받을 수 있어요. 팔라펠 샌드위치(8유로)는 반으로 잘라서 두 명이 나눠 먹을 만큼 커요. 타히니 소스와 신선한 채소가 들어가서 중동의 맛을 제대로 느낄 수 있어요. 여기는 레오나르도 디카프리오도 방문한 곳이라는 소문이 있어요.

📍 주소: 34 Rue des Rosiers, 75004 Paris
⏰ 영업: 일-목 11:00-22:00, 금 11:00-15:00 (유대인 안식일)

🌅 저녁 산책: 세느강변
일몰 시간대(19:00-20:00)에 세느강변을 걸어보세요. 일몰빛이 에펠탑에 비치는 모습이 정말 환상적이에요. 다리 위에서 사진을 찍으면 인생샷을 건질 수 있어요.

💡 꿀팁: 첫날은 무리하지 말고 일찍 쉬세요. 시차 적응을 위해서 22시 전에는 잠자리에 드는 것을 추천드려요.""",
        "spots": [
            {"name": "Place des Vosges (보즈 광장)", "desc": "파리 최초의 왕립 광장, 빨간 벽돌 건축물", "maps": "https://goo.gl/maps/xyz123", "reservation": False},
            {"name": "Rue des Rosiers (로시에 거리)", "desc": "마레 지구 중심가, 빈티지 쇼핑 거리", "maps": "https://goo.gl/maps/xyz124", "reservation": False},
        ],
        "restaurants": [
            {"name": "L'As du Fallafel", "type": "점심", "price": "8유로", "tip": "팔라펠 샌드위치, 줄 서도 10분이면", "maps": "https://goo.gl/maps/xyz125", "reservation": False},
        ],
    },
    "day2": {
        "title": "에펠탑 아침 & 생제륧망데프레 감성",
        "theme": "파리의 상징과 현지인 동네",
        "content": """🎫 예약 필요: 에펠탑 (2-4주 전 예약 필수)

오늘은 파리의 심장, 에펠탑을 아침 일찍 방문할 거예요. 무턱대고 가면 2시간 줄을 서야 해서 꼭 미리 예약하세요!

📍 에펠탑 (Tour Eiffel)
1889년 세워진 파리의 랜드마크로, 330미터 높이의 철탑이에요. 꼭대기까지 갈 필요 없이 2층까지만 가도 충분해요(16.3유로). 여기서 찍은 사진은 인생샷이 될 거예요.

예약 방법:
1. https://www.toureiffel.paris 접속
2. 'Tickets' → 'To the Top' 또는 '2nd Floor'
3. 날짜와 시간 선택 (9:00-10:30 추천)
4. 이메일로 받은 QR코드 출력 또는 모바일 저장

💡 꿀팁: 9시 오픈런을 하면 사람이 가장 적어요. 아침 8시 50분까지 도착하세요.

🚶 이동: 메트로 6호선 'Bir-Hakeim'역

📸 트로카데로 (Trocadéro) 광장
에펠탑에서 도보로 10분 거리예요. 에펠탑과 정면으로 마주 보는 위치라 프레임이 완벽해요. 아침 9시 전에 가면 사람도 적고 사진도 잘 나와요. 'Emily in Paris' 드라마에서도 나왔던 장소예요.

🥐 점심: Café de Flore
생제륧망데프레 지구로 넘어가서 역사적인 문학 카페에서 브런치를 즐기세요. 사르트르와 시몬 드 볼장이 단골이었던 1887년 창업의 카페예요. 크루아상(6유로)과 카페 오 레(5.5유로)를 주문하고 창가 자리에 앉으세요. 비싸지만 '파리에 왔다'는 감성을 제대로 느낄 수 있어요.

📍 주소: 172 Bd Saint-Germain, 75006 Paris
⏰ 영업: 7:30-01:30

🚶 이동: 메트로 4호선 'Saint-Germain-des-Prés'역

🌳 오후: 룩셈부르크 정원 (Jardin du Luxembourg)
파리 현지인들이 가장 좋아하는 공원이에요. 1612년 마리 드 메디치스가 만든 프랑스식 정원으로, 녹색 의자에 앉아 책 읽는 사람들, 배드민턴 치는 아이들, 산책하는 연인들을 보며 파리의 일상을 느낄 수 있어요.

메디치스 분수(Fontaine Médicis) 옆 의자에 앉아서 1시간만 멍 때리세요. 여기서 파리지엥의 여유로움을 제대로 느낄 수 있어요.

🚶 이동: 카페에서 도보 10분

🍽️ 저녁: Le Comptoir du Relais
생제륧망데프레에서 가장 인기 있는 브라세리예요. 셰프 이브 캉드보레가 운영하는 곳으로, 까수레(cassoulet, 소시지와 콩의 스튜, 24유로)가 시그니처예요. 예약 없이 19시 전에 가면 웨이팅 없이 들어갈 수 있어요. 현지인들이 가득한 분위기가 정말 좋아요.

📍 주소: 9 Carrefour de l'Odéon, 75006 Paris
⏰ 영업: 12:00-23:00 (예약 불가, 현장 웨이팅만 가능)""",
        "spots": [
            {"name": "에펠탑 (Eiffel Tower)", "desc": "파리의 상징, 1889년 건립", "maps": "https://goo.gl/maps/xyz126", "reservation": True, "reservation_url": "https://www.toureiffel.paris", "reservation_note": "2-4주 전 예약 필수"},
            {"name": "트로카데로 광장", "desc": "에펠탑 전망 사진 명소", "maps": "https://goo.gl/maps/xyz127", "reservation": False},
            {"name": "룩셈부르크 정원", "desc": "파리 현지인 최애 공원", "maps": "https://goo.gl/maps/xyz128", "reservation": False},
        ],
        "restaurants": [
            {"name": "Café de Flore", "type": "브런치", "price": "15유로", "tip": "역사적 문학 카페, 크루아상 필수", "maps": "https://goo.gl/maps/xyz129", "reservation": False},
            {"name": "Le Comptoir du Relais", "type": "저녁", "price": "35유로", "tip": "까수레 시그니처, 7시 전 도착 권장", "maps": "https://goo.gl/maps/xyz130", "reservation": False},
        ],
    },
    "day3": {
        "title": "루브르 아침 & 생트샤펠 오후",
        "theme": "세계 최고의 미술관과 중세 보석",
        "content": """🎫 예약 필요: 루브르 박물관 (최소 1주일 전 예약 필수)

오늘은 세계 최고의 미술관, 루브르에서 하루를 보낼 거예요. 3만 5천 점의 작품이 있는 곳이라 하루 종일 봐도 모자라요.

📍 루브르 박물관 (Musée du Louvre)
원래 왕궁이었던 곳으로, 1793년 프랑스 혁명 이후 박물관으로 바뀌었어요. 피라미드 입구가 유명하지만 지하 쇼핑센터 '카루젤 뒤 루브르'에서도 들어갈 수 있어 줄이 더 짧아요.

예약 방법:
1. https://www.louvre.fr 접속
2. 'Visit' → 'Tickets'
3. 날짜와 시간대 선택 (9:00-11:00 추천)
4. 성인 티켓: 17유로

📸 꼭 봐야 할 작품들:
1. 모나리자 (Denon Wing 1층) - 레오나르도 다 빈치
2. 미로의 비너스 (Sully Wing 0층)
3. 승리의 여신 (Denon Wing 1층)
4. 나폴레옹 3세 아파트 (Richelieu Wing 2층)
5. 이집트 유물관 (Sully Wing 0층)

💡 꿀팁: 모나리자는 사람이 많아서 30초만 보고 나오세요. 오히려 다른 작품들이 더 감동적이에요.

⏰ 관람 시간: 최소 4시간 필요

🍽️ 점심: 루브르 안 카페
박물관 안에 카페가 여러 개 있어요. Cafe Mollien(2층)이 가장 넓고 한가로워서 추천드려요. 샌드위치(12유로)와 커피(4유로)로 간단히 해결하세요.

🎨 오후: 생트샤펠 (Sainte-Chapelle)
루브르에서 도보로 15분 거리에 있는 13세기 성당이에요. 15개의 거대한 스테인드글라스 창문이 천장까지 둘러싸고 있어서 햇빛이 들어오면 무지개빛으로 빛나요. 특히 낮 12시-2시 사이에 가면 빛이 가장 아름다워요.

예약: https://www.sainte-chapelle.fr (11.5유로, 온라인 예매 권장)

🚶 이동: 루브르에서 도보 15분

🌉 저녁: 퐁 데자르 (Pont des Arts)
생트샤펠에서 센강을 따라 걸으면 나오는 다리예요. '예술의 다리'로 불리는 이곳은 연인들이 자물쇠를 걸던 곳으로 유명했어요(지금은 자물쇠 금지). 일몰 시간대에 강을 바라보며 산책하는 것이 파리 여행의 하이라이트예요.""",
        "spots": [
            {"name": "루브르 박물관", "desc": "세계 최대 미술관, 모나리자 전시", "maps": "https://goo.gl/maps/xyz131", "reservation": True, "reservation_url": "https://www.louvre.fr", "reservation_note": "1주일 전 예약 필수"},
            {"name": "생트샤펠", "desc": "스테인드글라스 예술의 정수", "maps": "https://goo.gl/maps/xyz132", "reservation": True, "reservation_url": "https://www.sainte-chapelle.fr", "reservation_note": "온라인 예매 시 할인"},
            {"name": "퐁 데자르", "desc": "예술의 다리, 일몰 명소", "maps": "https://goo.gl/maps/xyz133", "reservation": False},
        ],
        "restaurants": [
            {"name": "Cafe Mollien (루브르 내)", "type": "점심", "price": "20유로", "tip": "박물관 안에서 간단히", "maps": "https://goo.gl/maps/xyz134", "reservation": False},
        ],
    },
    "day4": {
        "title": "몽마르트 예술가 거리 & 에펠탑 야경",
        "theme": "예술의 언덕과 반짝이는 밤",
        "content": """🎫 예약 필요: 없음 (예술가 거리는 자유 방문)

오늘은 파리에서 가장 예술적인 동네 몽마르트(Montmartre)를 탐험하고, 밤에는 에펠탑 조명쇼로 마무리할 거예요.

📍 사크레쾨르 성당 (Sacré-Cœur)
흰 돔이 특징인 이 성당은 파리에서 가장 높은 언덕 위에 있어요. 메트로 'Abbesses'역에서 내려서 300계단을 걸어 올라가는 것이 포인트예요(편한 신발 필수!). 올라가면서 파리 시내가 점점 작아지는 게 보여요.

성당 안은 무료로 들어갈 수 있고, 돔 올라가는 것은 7유로예요. 9시 전에 가면 관광객이 적어서 사진 찍기 좋아요.

🎨 플라스 듀 테르트르 (Place du Tertre)
성당에서 도보 5분 거리에 있는 예술가들의 광장이에요. 피카소, 르누아르, 반 고흐가 모두 이 동네에서 살고 작업했어요. 지금도 거리 작가들이 초상화를 그려주고 있어요. 20-30분 앉아서 그림을 그려주면 30-50유로예요. 시간이 되시면 여기서 그림을 하나 그려보세요. 파리 여행의 특별한 추억이 될 거예요.

☕ 카페: La Maison Rose
몽마르트에서 가장 인스타그램 핫플인 분홍색 집 카페예요. 로제 와인(8유로) 한 잔하면서 경치를 즐기세요. 여기는 영화 '아멜리에'에도 나왔던 곳이에요.

🍽️ 점심: Le Moulin de la Galette
1800년대부터 영업한 풍차 모양 레스토랑이에요. 몽마르트 전통 요리인 라타투이(Ratatouille, 채소 스튜, 18유로)를 맛볼 수 있어요. 테라스 자리에서 몽마르트 거리를 내려다보며 식사하세요.

📍 주소: 83 Rue Lepic, 75018 Paris

🌃 저녁: 에펠탑 조명쇼
밤 9시가 넘으면 에펠탑으로 가세요. 매시간 정각부터 5분간 반짝이는 조명쇼가 펼쳐져요(21:00, 22:00, 23:00). 어두운 밤하늘에 반짝이는 에펠탑을 보면 정말 황홀해요. 트로카데로 광장이나 샹드마르스 공원에서 보면 가장 좋아요.

💡 꿀팁: 담요나 가벼운 외투를 챙가세요. 밤에는 꽤 추워요.""",
        "spots": [
            {"name": "사크레쾨르 성당", "desc": "흰 돔 성당, 파리 전망", "maps": "https://goo.gl/maps/xyz135", "reservation": False},
            {"name": "Place du Tertre", "desc": "예술가들의 광장, 초상화", "maps": "https://goo.gl/maps/xyz136", "reservation": False},
            {"name": "에펠탑 야경", "desc": "매시간 5분간 반짝이는 조명쇼", "maps": "https://goo.gl/maps/xyz137", "reservation": False},
        ],
        "restaurants": [
            {"name": "La Maison Rose", "type": "카페", "price": "15유로", "tip": "분홍색 집 카페, 로제 와인", "maps": "https://goo.gl/maps/xyz138", "reservation": False},
            {"name": "Le Moulin de la Galette", "type": "점심", "price": "30유로", "tip": "1800년대 풍차 레스토랑", "maps": "https://goo.gl/maps/xyz139", "reservation": False},
        ],
    },
    "day5": {
        "title": "마무리 쇼핑 & 귀국",
        "theme": "여유로운 마지막 날",
        "content": """📍 예약 필요: 없음

마지막 날이에요. 늦잠을 자고 천천히 일어나 마지막 브런치를 즐기세요.

🛍️ 오전: 갤러리 라파예트 (Galeries Lafayette)
파리를 대표하는 명품 백화점이에요. 하우스 브랜드부터 럭셔리 브랜드까지 다 있지만, 쇼핑을 안 해도 꼭 가봐야 할 곳이에요. 7층 테라스(무료)에서 보는 파리 전망이 정말 멋져요. 오페라 하우스 지붕과 에펠탑이 한 화면에 잡혀요.

🚶 이동: 메트로 7호선 'Chaussée d'Antin'역

🍽️ 점심: Bouillon Chartier
1896년부터 영업한 전통 브라세리예요. 1900년대 초반 분위기 그대로라 인테리어도 볼거리예요. 에스카르고(Escargot, 달팽이 요리, 8유로), 코코뱅(Coq au Vin, 닭고기 와인 스튜, 14유로) 같은 클래식 프랑스 요리를 저렴한 가격에 맛볼 수 있어요. 웨이팅이 있지만 15-20분이면 들어갈 수 있어요.

📍 주소: 7 Rue du Faubourg Montmartre, 75009 Paris
⏰ 영업: 11:30-00:00

✈️ 공항 이동
짐을 챙겨서 샤를 드 골 공항으로 이동하세요. 테륵미니역에서 레오나륵도 익스프레스(14유로, 35분)를 타세요. 비행기는 3시간 전에 도착하는 것이 안전해요.

5일간의 파리 여행이 끝났어요. 느긋하게 카페에서 보낸 시간, 골목길을 걸으며 발견한 멋진 가게들, 감동적이었던 미술관과 야경... 이 모든 것이 추억으로 남으실 거예요. 다음에는 또 다른 동네를 탐험해보세요. À bientôt, Paris! (또 만나요, 파리!)""",
        "spots": [
            {"name": "갤러리 라파예트", "desc": "파리 명품 백화점, 7층 전망대", "maps": "https://goo.gl/maps/xyz140", "reservation": False},
            {"name": "샤를 드 골 공항", "desc": "귀국", "maps": "https://goo.gl/maps/xyz141", "reservation": False},
        ],
        "restaurants": [
            {"name": "Bouillon Chartier", "type": "점심", "price": "20유로", "tip": "1896년 전통 브라세리, 에스카르고 추천", "maps": "https://goo.gl/maps/xyz142", "reservation": False},
        ],
    },
}

# 파리 외 다른 도시들도 같은 형식으로 추가 가능
CITY_DATABASE = {
    "Paris": PARIS_DETAILED,
}

# 예약 필수 목록
RESERVATION_REQUIRED = {
    "Paris": [
        {"name": "에펠탑", "when": "2-4주 전", "url": "https://www.toureiffel.paris", "note": "아침 9시 오픈런 추천"},
        {"name": "루브르 박물관", "when": "최소 1주일 전", "url": "https://www.louvre.fr", "note": "9-11시 타임 예약 추천"},
        {"name": "생트샤펠", "when": "3-4일 전", "url": "https://www.sainte-chapelle.fr", "note": "오후 12-14시 빛이 가장 아름다움"},
        {"name": "Septime 레스토랑", "when": "최소 1개월 전", "url": "https://www.septimorestaurant.com", "note": "미슐랭 1성, 매우 인기"},
        {"name": "Le Comptoir du Relais", "when": "당일 웨이팅", "url": "https://www.comptoidurelais.com", "note": "7시 전 도착 권장"},
    ],
}
