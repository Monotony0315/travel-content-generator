"""
Destinations Database
여행지 데이터베이스 (MVP)
"""

EUROPE = [
    {"name": "Paris", "country": "France", "currency": "EUR", "language": "French", "recommended_days": 5, "travel_style": "romantic", "cuisine": "french", "highlights": ["에펠탑", "루브르", "몽마르트"]},
    {"name": "Rome", "country": "Italy", "currency": "EUR", "language": "Italian", "recommended_days": 5, "travel_style": "history", "cuisine": "italian", "highlights": ["콜로세움", "바티칸", "트레비 분수"]},
    {"name": "Barcelona", "country": "Spain", "currency": "EUR", "language": "Spanish", "recommended_days": 4, "travel_style": "art", "cuisine": "spanish", "highlights": ["사그라다 파밀리아", "고딕 지구"]},
]

ASIA = [
    {"name": "Tokyo", "country": "Japan", "currency": "JPY", "language": "Japanese", "recommended_days": 5, "travel_style": "classic", "cuisine": "japanese", "highlights": ["시부야", "아사쿠사", "긴자"]},
    {"name": "Bangkok", "country": "Thailand", "currency": "THB", "language": "Thai", "recommended_days": 4, "travel_style": "foodie", "cuisine": "thai", "highlights": ["왕궁", "왓 아룬", "짜뚜짝 시장"]},
    {"name": "Singapore", "country": "Singapore", "currency": "SGD", "language": "English", "recommended_days": 3, "travel_style": "luxury", "cuisine": "singaporean", "highlights": ["마리나베이", "가든스바이더베이"]},
]

AMERICAS = [
    {"name": "New York", "country": "USA", "currency": "USD", "language": "English", "recommended_days": 5, "travel_style": "classic", "cuisine": "american", "highlights": ["타임스퀘어", "센트럴파크"]},
    {"name": "Vancouver", "country": "Canada", "currency": "CAD", "language": "English", "recommended_days": 4, "travel_style": "nature", "cuisine": "canadian", "highlights": ["스탠리 파크", "그랜빌 아일랜드"]},
]

OCEANIA = [
    {"name": "Sydney", "country": "Australia", "currency": "AUD", "language": "English", "recommended_days": 4, "travel_style": "beach", "cuisine": "australian", "highlights": ["오페라하우스", "본다이 비치"]},
]

DESTINATIONS = {
    "europe": EUROPE,
    "asia": ASIA,
    "americas": AMERICAS,
    "oceania": OCEANIA,
}
