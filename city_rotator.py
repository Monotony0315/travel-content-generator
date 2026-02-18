"""
Daily City Rotator for Travel Blog
매일 다른 도시를 자동으로 선택하여 블로그 생성
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# 사용 가능한 도시 목록 (60개) - 한국 제외, 다양한 휴양지 포함
AVAILABLE_CITIES: List[Dict] = [
    # ========== 유럽 (20개) ==========
    {"name": "Paris", "country": "France", "region": "유럽", "blog_links": [
        "https://www.theguardian.com/travel/paris",
        "https://www.timeout.com/paris",
        "https://www.lonelyplanet.com/france/paris",
        "https://www.tripadvisor.com/Tourism-g187147-Paris_Ile_de_France-Vacations.html",
    ]},
    {"name": "Rome", "country": "Italy", "region": "유럽", "blog_links": [
        "https://www.theguardian.com/travel/rome",
        "https://www.timeout.com/rome",
        "https://www.lonelyplanet.com/italy/rome",
        "https://www.tripadvisor.com/Tourism-g187791-Rome_Lazio-Vacations.html",
    ]},
    {"name": "Barcelona", "country": "Spain", "region": "유럽", "blog_links": [
        "https://www.theguardian.com/travel/barcelona",
        "https://www.timeout.com/barcelona",
        "https://www.lonelyplanet.com/spain/barcelona",
        "https://www.tripadvisor.com/Tourism-g187497-Barcelona_Catalonia-Vacations.html",
    ]},
    {"name": "London", "country": "UK", "region": "유럽", "blog_links": [
        "https://www.theguardian.com/travel/london",
        "https://www.timeout.com/london",
        "https://www.lonelyplanet.com/great-britain/london",
        "https://www.tripadvisor.com/Tourism-g186338-London_England-Vacations.html",
    ]},
    {"name": "Amsterdam", "country": "Netherlands", "region": "유럽", "blog_links": [
        "https://www.theguardian.com/travel/amsterdam",
        "https://www.timeout.com/amsterdam",
        "https://www.lonelyplanet.com/the-netherlands/amsterdam",
        "https://www.tripadvisor.com/Tourism-g188590-Amsterdam_North_Holland_Province-Vacations.html",
    ]},
    {"name": "Prague", "country": "Czech Republic", "region": "유럽", "blog_links": [
        "https://www.theguardian.com/travel/prague",
        "https://www.timeout.com/prague",
        "https://www.lonelyplanet.com/czech-republic/prague",
        "https://www.tripadvisor.com/Tourism-g274707-Prague_Bohemia-Vacations.html",
    ]},
    {"name": "Vienna", "country": "Austria", "region": "유럽", "blog_links": [
        "https://www.theguardian.com/travel/vienna",
        "https://www.timeout.com/vienna",
        "https://www.lonelyplanet.com/austria/vienna",
        "https://www.tripadvisor.com/Tourism-g190454-Vienna-Vacations.html",
    ]},
    {"name": "Budapest", "country": "Hungary", "region": "유럽", "blog_links": [
        "https://www.theguardian.com/travel/budapest",
        "https://www.timeout.com/budapest",
        "https://www.lonelyplanet.com/hungary/budapest",
        "https://www.tripadvisor.com/Tourism-g274887-Budapest_Central_Hungary-Vacations.html",
    ]},
    {"name": "Lisbon", "country": "Portugal", "region": "유럽", "blog_links": [
        "https://www.theguardian.com/travel/lisbon",
        "https://www.timeout.com/lisbon",
        "https://www.lonelyplanet.com/portugal/lisbon",
        "https://www.tripadvisor.com/Tourism-g189158-Lisbon_Lisbon_District_Central_Portugal-Vacations.html",
    ]},
    {"name": "Berlin", "country": "Germany", "region": "유럽", "blog_links": [
        "https://www.theguardian.com/travel/berlin",
        "https://www.timeout.com/berlin",
        "https://www.lonelyplanet.com/germany/berlin",
        "https://www.tripadvisor.com/Tourism-g187323-Berlin-Vacations.html",
    ]},
    {"name": "Florence", "country": "Italy", "region": "유럽", "blog_links": [
        "https://www.theguardian.com/travel/florence",
        "https://www.timeout.com/florence",
        "https://www.lonelyplanet.com/italy/florence",
        "https://www.tripadvisor.com/Tourism-g187895-Florence_Tuscany-Vacations.html",
    ]},
    {"name": "Venice", "country": "Italy", "region": "유럽", "blog_links": [
        "https://www.theguardian.com/travel/venice",
        "https://www.timeout.com/venice",
        "https://www.lonelyplanet.com/italy/venice",
        "https://www.tripadvisor.com/Tourism-g187870-Venice_Veneto-Vacations.html",
    ]},
    {"name": "Milan", "country": "Italy", "region": "유럽", "blog_links": [
        "https://www.theguardian.com/travel/milan",
        "https://www.timeout.com/milan",
        "https://www.lonelyplanet.com/italy/milan",
        "https://www.tripadvisor.com/Tourism-g187849-Milan_Lombardy-Vacations.html",
    ]},
    {"name": "Madrid", "country": "Spain", "region": "유럽", "blog_links": [
        "https://www.theguardian.com/travel/madrid",
        "https://www.timeout.com/madrid",
        "https://www.lonelyplanet.com/spain/madrid",
        "https://www.tripadvisor.com/Tourism-g187514-Madrid-Vacations.html",
    ]},
    {"name": "Athens", "country": "Greece", "region": "유럽", "blog_links": [
        "https://www.theguardian.com/travel/athens",
        "https://www.timeout.com/athens",
        "https://www.lonelyplanet.com/greece/athens",
        "https://www.tripadvisor.com/Tourism-g189400-Athens_Attica-Vacations.html",
    ]},
    {"name": "Edinburgh", "country": "Scotland", "region": "유럽", "blog_links": [
        "https://www.theguardian.com/travel/edinburgh",
        "https://www.timeout.com/edinburgh",
        "https://www.lonelyplanet.com/scotland/edinburgh",
        "https://www.tripadvisor.com/Tourism-g186525-Edinburgh_Scotland-Vacations.html",
    ]},
    {"name": "Copenhagen", "country": "Denmark", "region": "유럽", "blog_links": [
        "https://www.theguardian.com/travel/copenhagen",
        "https://www.timeout.com/copenhagen",
        "https://www.lonelyplanet.com/denmark/copenhagen",
        "https://www.tripadvisor.com/Tourism-g189541-Copenhagen_Zealand-Vacations.html",
    ]},
    {"name": "Stockholm", "country": "Sweden", "region": "유럽", "blog_links": [
        "https://www.theguardian.com/travel/stockholm",
        "https://www.timeout.com/stockholm",
        "https://www.lonelyplanet.com/sweden/stockholm",
        "https://www.tripadvisor.com/Tourism-g189852-Stockholm-Vacations.html",
    ]},
    {"name": "Dubrovnik", "country": "Croatia", "region": "유럽", "blog_links": [
        "https://www.theguardian.com/travel/dubrovnik",
        "https://www.timeout.com/dubrovnik",
        "https://www.lonelyplanet.com/croatia/dubrovnik",
        "https://www.tripadvisor.com/Tourism-g295371-Dubrovnik_Dubrovnik_Neretva_County_Dalmatia-Vacations.html",
    ]},
    {"name": "Santorini", "country": "Greece", "region": "유럽", "blog_links": [
        "https://www.theguardian.com/travel/santorini",
        "https://www.timeout.com/santorini",
        "https://www.lonelyplanet.com/greece/cyclades/santorini",
        "https://www.tripadvisor.com/Tourism-g189433-Santorini_Cyclades_South_Aegean-Vacations.html",
    ]},
    
    # ========== 동남아시아 (15개) ==========
    {"name": "Bangkok", "country": "Thailand", "region": "동남아", "blog_links": [
        "https://www.theguardian.com/travel/bangkok",
        "https://www.timeout.com/bangkok",
        "https://www.lonelyplanet.com/thailand/bangkok",
        "https://www.tripadvisor.com/Tourism-g293916-Bangkok-Vacations.html",
    ]},
    {"name": "Singapore", "country": "Singapore", "region": "동남아", "blog_links": [
        "https://www.theguardian.com/travel/singapore",
        "https://www.timeout.com/singapore",
        "https://www.lonelyplanet.com/singapore",
        "https://www.tripadvisor.com/Tourism-g294265-Singapore-Vacations.html",
    ]},
    {"name": "Kuala Lumpur", "country": "Malaysia", "region": "동남아", "blog_links": [
        "https://www.theguardian.com/travel/kuala-lumpur",
        "https://www.timeout.com/kuala-lumpur",
        "https://www.lonelyplanet.com/malaysia/kuala-lumpur",
        "https://www.tripadvisor.com/Tourism-g298570-Kuala_Lumpur_Wilayah_Persekutuan-Vacations.html",
    ]},
    {"name": "Jakarta", "country": "Indonesia", "region": "동남아", "blog_links": [
        "https://www.theguardian.com/travel/jakarta",
        "https://www.timeout.com/jakarta",
        "https://www.lonelyplanet.com/indonesia/jakarta",
        "https://www.tripadvisor.com/Tourism-g294229-Jakarta_Java-Vacations.html",
    ]},
    {"name": "Ho Chi Minh City", "country": "Vietnam", "region": "동남아", "blog_links": [
        "https://www.theguardian.com/travel/ho-chi-minh-city",
        "https://www.timeout.com/ho-chi-minh-city",
        "https://www.lonelyplanet.com/vietnam/ho-chi-minh-city",
        "https://www.tripadvisor.com/Tourism-g293925-Ho_Chi_Minh_City-Vacations.html",
    ]},
    {"name": "Hanoi", "country": "Vietnam", "region": "동남아", "blog_links": [
        "https://www.theguardian.com/travel/hanoi",
        "https://www.timeout.com/hanoi",
        "https://www.lonelyplanet.com/vietnam/hanoi",
        "https://www.tripadvisor.com/Tourism-g293924-Hanoi-Vacations.html",
    ]},
    {"name": "Manila", "country": "Philippines", "region": "동남아", "blog_links": [
        "https://www.theguardian.com/travel/manila",
        "https://www.timeout.com/manila",
        "https://www.lonelyplanet.com/philippines/manila",
        "https://www.tripadvisor.com/Tourism-g298573-Manila_Metro_Manila_Luzon-Vacations.html",
    ]},
    {"name": "Phnom Penh", "country": "Cambodia", "region": "동남아", "blog_links": [
        "https://www.theguardian.com/travel/phnom-penh",
        "https://www.timeout.com/phnom-penh",
        "https://www.lonelyplanet.com/cambodia/phnom-penh",
        "https://www.tripadvisor.com/Tourism-g293940-Phnom_Penh-Vacations.html",
    ]},
    {"name": "Siem Reap", "country": "Cambodia", "region": "동남아", "blog_links": [
        "https://www.theguardian.com/travel/siem-reap",
        "https://www.timeout.com/siem-reap",
        "https://www.lonelyplanet.com/cambodia/siem-reap",
        "https://www.tripadvisor.com/Tourism-g297390-Siem_Reap_Siem_Reap_Province-Vacations.html",
    ]},
    {"name": "Yangon", "country": "Myanmar", "region": "동남아", "blog_links": [
        "https://www.theguardian.com/travel/yangon",
        "https://www.timeout.com/yangon",
        "https://www.lonelyplanet.com/myanmar-burma/yangon",
        "https://www.tripadvisor.com/Tourism-g295408-Yangon_Rangoon_Yangon_Region-Vacations.html",
    ]},
    {"name": "Chiang Mai", "country": "Thailand", "region": "동남아", "blog_links": [
        "https://www.theguardian.com/travel/chiang-mai",
        "https://www.timeout.com/chiang-mai",
        "https://www.lonelyplanet.com/thailand/chiang-mai",
        "https://www.tripadvisor.com/Tourism-g293917-Chiang_Mai-Vacations.html",
    ]},
    {"name": "Phuket", "country": "Thailand", "region": "동남아", "blog_links": [
        "https://www.theguardian.com/travel/phuket",
        "https://www.timeout.com/phuket",
        "https://www.lonelyplanet.com/thailand/phuket",
        "https://www.tripadvisor.com/Tourism-g293920-Phuket-Vacations.html",
    ]},
    {"name": "Penang", "country": "Malaysia", "region": "동남아", "blog_links": [
        "https://www.theguardian.com/travel/penang",
        "https://www.timeout.com/penang",
        "https://www.lonelyplanet.com/malaysia/penang",
        "https://www.tripadvisor.com/Tourism-g298303-Penang_Penang_Island-Vacations.html",
    ]},
    {"name": "Da Nang", "country": "Vietnam", "region": "동남아", "blog_links": [
        "https://www.theguardian.com/travel/da-nang",
        "https://www.lonelyplanet.com/vietnam/da-nang",
        "https://www.tripadvisor.com/Tourism-g298085-Da_Nang-Vacations.html",
    ]},
    {"name": "Luang Prabang", "country": "Laos", "region": "동남아", "blog_links": [
        "https://www.theguardian.com/travel/luang-prabang",
        "https://www.lonelyplanet.com/laos/luang-prabang",
        "https://www.tripadvisor.com/Tourism-g295411-Luang_Prabang_Luang_Prabang_Province-Vacations.html",
    ]},
    
    # ========== 휴양지 섬 (10개) ==========
    {"name": "Bali", "country": "Indonesia", "region": "휴양지", "blog_links": [
        "https://www.theguardian.com/travel/bali",
        "https://www.timeout.com/bali",
        "https://www.lonelyplanet.com/indonesia/bali",
        "https://www.tripadvisor.com/Tourism-g294226-Bali-Vacations.html",
    ]},
    {"name": "Maldives", "country": "Maldives", "region": "휴양지", "blog_links": [
        "https://www.theguardian.com/travel/maldives",
        "https://www.timeout.com/maldives",
        "https://www.lonelyplanet.com/maldives",
        "https://www.tripadvisor.com/Tourism-g293953-Maldives-Vacations.html",
    ]},
    {"name": "Phuket", "country": "Thailand", "region": "휴양지", "blog_links": [
        "https://www.theguardian.com/travel/phuket",
        "https://www.timeout.com/phuket",
        "https://www.lonelyplanet.com/thailand/phuket",
        "https://www.tripadvisor.com/Tourism-g293920-Phuket-Vacations.html",
    ]},
    {"name": "Boracay", "country": "Philippines", "region": "휴양지", "blog_links": [
        "https://www.theguardian.com/travel/boracay",
        "https://www.lonelyplanet.com/philippines/boracay",
        "https://www.tripadvisor.com/Tourism-g294260-Boracay_Malay_Aklan_Province_Panay_Island_Visayas-Vacations.html",
    ]},
    {"name": "Bora Bora", "country": "French Polynesia", "region": "휴양지", "blog_links": [
        "https://www.theguardian.com/travel/bora-bora",
        "https://www.lonelyplanet.com/french-polynesia/bora-bora",
        "https://www.tripadvisor.com/Tourism-g309685-Bora_Bora-Society_Islands-Vacations.html",
    ]},
    {"name": "Cancun", "country": "Mexico", "region": "휴양지", "blog_links": [
        "https://www.theguardian.com/travel/cancun",
        "https://www.lonelyplanet.com/mexico/cancun",
        "https://www.tripadvisor.com/Tourism-g150807-Cancun_Yucatan_Peninsula-Vacations.html",
    ]},
    {"name": "Santorini", "country": "Greece", "region": "휴양지", "blog_links": [
        "https://www.theguardian.com/travel/santorini",
        "https://www.lonelyplanet.com/greece/cyclades/santorini",
        "https://www.tripadvisor.com/Tourism-g189433-Santorini_Cyclades_South_Aegean-Vacations.html",
    ]},
    {"name": "Mykonos", "country": "Greece", "region": "휴양지", "blog_links": [
        "https://www.theguardian.com/travel/mykonos",
        "https://www.lonelyplanet.com/greece/cyclades/mykonos",
        "https://www.tripadvisor.com/Tourism-g189430-Mykonos_Cyclades_South_Aegean-Vacations.html",
    ]},
    {"name": "Zanzibar", "country": "Tanzania", "region": "휴양지", "blog_links": [
        "https://www.theguardian.com/travel/zanzibar",
        "https://www.lonelyplanet.com/tanzania/zanzibar",
        "https://www.tripadvisor.com/Tourism-g488117-Zanzibar_Island_Zanzibar_Archipelago-Vacations.html",
    ]},
    {"name": "Costa Rica", "country": "Costa Rica", "region": "휴양지", "blog_links": [
        "https://www.theguardian.com/travel/costa-rica",
        "https://www.lonelyplanet.com/costa-rica",
        "https://www.tripadvisor.com/Tourism-g291982-Costa_Rica-Vacations.html",
    ]},
    {"name": "Bali", "country": "Indonesia", "region": "휴양지", "blog_links": [
        "https://www.theguardian.com/travel/bali",
        "https://www.timeout.com/bali",
        "https://www.lonelyplanet.com/indonesia/bali",
        "https://www.tripadvisor.com/Tourism-g294226-Bali-Vacations.html",
    ]},
    {"name": "Maldives", "country": "Maldives", "region": "휴양지", "blog_links": [
        "https://www.theguardian.com/travel/maldives",
        "https://www.timeout.com/maldives",
        "https://www.lonelyplanet.com/maldives",
        "https://www.tripadvisor.com/Tourism-g293953-Maldives-Vacations.html",
    ]},
    {"name": "Phuket", "country": "Thailand", "region": "휴양지", "blog_links": [
        "https://www.theguardian.com/travel/phuket",
        "https://www.timeout.com/phuket",
        "https://www.lonelyplanet.com/thailand/phuket",
        "https://www.tripadvisor.com/Tourism-g293920-Phuket-Vacations.html",
    ]},
    {"name": "Boracay", "country": "Philippines", "region": "휴양지", "blog_links": [
        "https://www.theguardian.com/travel/boracay",
        "https://www.lonelyplanet.com/philippines/boracay",
        "https://www.tripadvisor.com/Tourism-g294260-Boracay_Malay_Aklan_Province_Panay_Island_Visayas-Vacations.html",
    ]},
    {"name": "Fiji", "country": "Fiji", "region": "휴양지", "blog_links": [
        "https://www.theguardian.com/travel/fiji",
        "https://www.lonelyplanet.com/fiji",
        "https://www.tripadvisor.com/Tourism-g294331-Fiji-South_Pacific-Vacations.html",
    ]},
    {"name": "Seychelles", "country": "Seychelles", "region": "휴양지", "blog_links": [
        "https://www.theguardian.com/travel/seychelles",
        "https://www.lonelyplanet.com/seychelles",
        "https://www.tripadvisor.com/Tourism-g293737-Seychelles-Vacations.html",
    ]},
    {"name": "Mauritius", "country": "Mauritius", "region": "휴양지", "blog_links": [
        "https://www.theguardian.com/travel/mauritius",
        "https://www.lonelyplanet.com/mauritius",
        "https://www.tripadvisor.com/Tourism-g293816-Mauritius-Vacations.html",
    ]},
    {"name": "Palawan", "country": "Philippines", "region": "휴양지", "blog_links": [
        "https://www.theguardian.com/travel/palawan",
        "https://www.lonelyplanet.com/philippines/palawan",
        "https://www.tripadvisor.com/Tourism-g294257-Palawan_Island_Palawan_Province_Mimaropa-Vacations.html",
    ]},
    {"name": "Koh Samui", "country": "Thailand", "region": "휴양지", "blog_links": [
        "https://www.theguardian.com/travel/koh-samui",
        "https://www.lonelyplanet.com/thailand/ko-samui",
        "https://www.tripadvisor.com/Tourism-g293918-Ko_Samui_Surat_Thani_Province-Vacations.html",
    ]},
    {"name": "Langkawi", "country": "Malaysia", "region": "휴양지", "blog_links": [
        "https://www.theguardian.com/travel/langkawi",
        "https://www.lonelyplanet.com/malaysia/langkawi",
        "https://www.tripadvisor.com/Tourism-g298283-Langkawi_Langkawi_District_Kedah-Vacations.html",
    ]},
    {"name": "Gili Islands", "country": "Indonesia", "region": "휴양지", "blog_links": [
        "https://www.theguardian.com/travel/gili-islands",
        "https://www.lonelyplanet.com/indonesia/gili-islands",
        "https://www.tripadvisor.com/Tourism-g297711-Gili_Islands_Lombok_West_Nusa_Tenggara-Vacations.html",
    ]},
    {"name": "Phi Phi Islands", "country": "Thailand", "region": "휴양지", "blog_links": [
        "https://www.theguardian.com/travel/phi-phi",
        "https://www.lonelyplanet.com/thailand/ko-phi-phi",
        "https://www.tripadvisor.com/Tourism-g303901-Ko_Phi_Phi_Don_Krabi_Province-Vacations.html",
    ]},
    {"name": "Raja Ampat", "country": "Indonesia", "region": "휴양지", "blog_links": [
        "https://www.theguardian.com/travel/raja-ampat",
        "https://www.lonelyplanet.com/indonesia/raja-ampat",
        "https://www.tripadvisor.com/Tourism-g1584592-Raja_Ampat_West_Papua_Papua-Vacations.html",
    ]},
    {"name": "Azores", "country": "Portugal", "region": "휴양지", "blog_links": [
        "https://www.theguardian.com/travel/azores",
        "https://www.lonelyplanet.com/portugal/the-azores",
        "https://www.tripadvisor.com/Tourism-g189167-Azores-Vacations.html",
    ]},
    {"name": "Fiji", "country": "Fiji", "region": "휴양지", "blog_links": [
        "https://www.theguardian.com/travel/fiji",
        "https://www.lonelyplanet.com/fiji",
        "https://www.tripadvisor.com/Tourism-g294331-Fiji-South_Pacific-Vacations.html",
    ]},
    {"name": "Seychelles", "country": "Seychelles", "region": "휴양지", "blog_links": [
        "https://www.theguardian.com/travel/seychelles",
        "https://www.lonelyplanet.com/seychelles",
        "https://www.tripadvisor.com/Tourism-g293737-Seychelles-Vacations.html",
    ]},
    {"name": "Mauritius", "country": "Mauritius", "region": "휴양지", "blog_links": [
        "https://www.theguardian.com/travel/mauritius",
        "https://www.lonelyplanet.com/mauritius",
        "https://www.tripadvisor.com/Tourism-g293816-Mauritius-Vacations.html",
    ]},
    {"name": "Palawan", "country": "Philippines", "region": "휴양지", "blog_links": [
        "https://www.theguardian.com/travel/palawan",
        "https://www.lonelyplanet.com/philippines/palawan",
        "https://www.tripadvisor.com/Tourism-g294257-Palawan_Island_Palawan_Province_Mimaropa-Vacations.html",
    ]},
    {"name": "Koh Samui", "country": "Thailand", "region": "휴양지", "blog_links": [
        "https://www.theguardian.com/travel/koh-samui",
        "https://www.lonelyplanet.com/thailand/ko-samui",
        "https://www.tripadvisor.com/Tourism-g293918-Ko_Samui_Surat_Thani_Province-Vacations.html",
    ]},
    
    # ========== 동아시아 (6개) - 한국 제외 ==========
    {"name": "Tokyo", "country": "Japan", "region": "동아시아", "blog_links": [
        "https://www.theguardian.com/travel/tokyo",
        "https://www.timeout.com/tokyo",
        "https://www.lonelyplanet.com/japan/tokyo",
        "https://www.tripadvisor.com/Tourism-g298184-Tokyo_Tokyo_Prefecture_Kanto-Vacations.html",
    ]},
    {"name": "Kyoto", "country": "Japan", "region": "동아시아", "blog_links": [
        "https://www.theguardian.com/travel/kyoto",
        "https://www.timeout.com/kyoto",
        "https://www.lonelyplanet.com/japan/kyoto",
        "https://www.tripadvisor.com/Tourism-g298564-Kyoto_Kyoto_Prefecture_Kinki-Vacations.html",
    ]},
    {"name": "Osaka", "country": "Japan", "region": "동아시아", "blog_links": [
        "https://www.theguardian.com/travel/osaka",
        "https://www.timeout.com/osaka",
        "https://www.lonelyplanet.com/japan/osaka",
        "https://www.tripadvisor.com/Tourism-g298566-Osaka_Osaka_Prefecture_Kinki-Vacations.html",
    ]},
    {"name": "Okinawa", "country": "Japan", "region": "동아시아", "blog_links": [
        "https://www.theguardian.com/travel/okinawa",
        "https://www.lonelyplanet.com/japan/okinawa",
        "https://www.tripadvisor.com/Tourism-g298223-Okinawa_Prefecture_Kyushu-Okinawa-Vacations.html",
    ]},
    {"name": "Taipei", "country": "Taiwan", "region": "동아시아", "blog_links": [
        "https://www.theguardian.com/travel/taipei",
        "https://www.timeout.com/taipei",
        "https://www.lonelyplanet.com/taiwan/taipei",
        "https://www.tripadvisor.com/Tourism-g293913-Taipei-Vacations.html",
    ]},
    {"name": "Hong Kong", "country": "Hong Kong", "region": "동아시아", "blog_links": [
        "https://www.theguardian.com/travel/hong-kong",
        "https://www.timeout.com/hong-kong",
        "https://www.lonelyplanet.com/china/hong-kong",
        "https://www.tripadvisor.com/Tourism-g294217-Hong_Kong-Vacations.html",
    ]},
    {"name": "Shanghai", "country": "China", "region": "동아시아", "blog_links": [
        "https://www.theguardian.com/travel/shanghai",
        "https://www.timeout.com/shanghai",
        "https://www.lonelyplanet.com/china/shanghai",
        "https://www.tripadvisor.com/Tourism-g308272-Shanghai-Vacations.html",
    ]},
    {"name": "Beijing", "country": "China", "region": "동아시아", "blog_links": [
        "https://www.theguardian.com/travel/beijing",
        "https://www.timeout.com/beijing",
        "https://www.lonelyplanet.com/china/beijing",
        "https://www.tripadvisor.com/Tourism-g294212-Beijing-Vacations.html",
    ]},
    
    # ========== 미주/기타 (5개) ==========
    {"name": "New York", "country": "USA", "region": "미주", "blog_links": [
        "https://www.theguardian.com/travel/new-york",
        "https://www.timeout.com/newyork",
        "https://www.lonelyplanet.com/usa/new-york-city",
        "https://www.tripadvisor.com/Tourism-g60763-New_York_City_New_York-Vacations.html",
    ]},
    {"name": "Los Angeles", "country": "USA", "region": "미주", "blog_links": [
        "https://www.theguardian.com/travel/los-angeles",
        "https://www.timeout.com/los-angeles",
        "https://www.lonelyplanet.com/usa/los-angeles",
        "https://www.tripadvisor.com/Tourism-g32655-Los_Angeles_California-Vacations.html",
    ]},
    {"name": "San Francisco", "country": "USA", "region": "미주", "blog_links": [
        "https://www.theguardian.com/travel/san-francisco",
        "https://www.timeout.com/san-francisco",
        "https://www.lonelyplanet.com/usa/san-francisco",
        "https://www.tripadvisor.com/Tourism-g60713-San_Francisco_California-Vacations.html",
    ]},
    {"name": "Vancouver", "country": "Canada", "region": "미주", "blog_links": [
        "https://www.theguardian.com/travel/vancouver",
        "https://www.timeout.com/vancouver",
        "https://www.lonelyplanet.com/canada/vancouver",
        "https://www.tripadvisor.com/Tourism-g154943-Vancouver_British_Columbia-Vacations.html",
    ]},
    {"name": "Sydney", "country": "Australia", "region": "오세아니아", "blog_links": [
        "https://www.theguardian.com/travel/sydney",
        "https://www.timeout.com/sydney",
        "https://www.lonelyplanet.com/australia/sydney",
        "https://www.tripadvisor.com/Tourism-g255060-Sydney_New_South_Wales-Vacations.html",
    ]},
    
    # ========== 중동 (3개) ==========
    {"name": "Dubai", "country": "UAE", "region": "중동", "blog_links": [
        "https://www.theguardian.com/travel/dubai",
        "https://www.timeout.com/dubai",
        "https://www.lonelyplanet.com/uae/dubai",
        "https://www.tripadvisor.com/Tourism-g295424-Dubai_Emirate_of_Dubai-Vacations.html",
    ]},
    {"name": "Istanbul", "country": "Turkey", "region": "중동", "blog_links": [
        "https://www.theguardian.com/travel/istanbul",
        "https://www.timeout.com/istanbul",
        "https://www.lonelyplanet.com/turkey/istanbul",
        "https://www.tripadvisor.com/Tourism-g293974-Istanbul-Vacations.html",
    ]},
    {"name": "Abu Dhabi", "country": "UAE", "region": "중동", "blog_links": [
        "https://www.theguardian.com/travel/abu-dhabi",
        "https://www.timeout.com/abu-dhabi",
        "https://www.lonelyplanet.com/uae/abu-dhabi",
        "https://www.tripadvisor.com/Tourism-g294013-Abu_Dhabi_Emirate_of_Abu_Dhabi-Vacations.html",
    ]},
]

STATE_FILE = Path(__file__).resolve().parent / "data" / "city_rotation.json"

def get_next_city() -> Dict:
    """다음에 생성할 도시를 순환하여 반환"""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    # 상태 파일 로드
    if STATE_FILE.exists():
        try:
            state = json.loads(STATE_FILE.read_text(encoding="utf-8"))
            last_index = state.get("last_index", -1)
        except:
            last_index = -1
    else:
        last_index = -1
    
    # 다음 도시 인덱스 계산
    next_index = (last_index + 1) % len(AVAILABLE_CITIES)
    next_city = AVAILABLE_CITIES[next_index]
    
    # 상태 저장
    state = {
        "last_index": next_index,
        "last_city": next_city["name"],
        "last_country": next_city["country"],
        "last_region": next_city["region"],
        "last_run": datetime.now().isoformat(),
        "total_cities": len(AVAILABLE_CITIES),
    }
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    
    return next_city

def get_current_city() -> Dict:
    """현재 설정된 도시 반환 (기본값: Paris)"""
    if STATE_FILE.exists():
        try:
            state = json.loads(STATE_FILE.read_text(encoding="utf-8"))
            city_name = state.get("last_city", "Paris")
            for city in AVAILABLE_CITIES:
                if city["name"] == city_name:
                    return city
        except:
            pass
    return AVAILABLE_CITIES[0]

def get_city_by_name(name: str) -> Dict:
    """도시 이름으로 도시 정보 반환"""
    for city in AVAILABLE_CITIES:
        if city["name"].lower() == name.lower():
            return city
    return None

if __name__ == "__main__":
    city = get_next_city()
    print(f"Next city for travel blog: {city['name']}, {city['country']} ({city['region']})")
    print(f"Travel blog links: {city['blog_links']}")
