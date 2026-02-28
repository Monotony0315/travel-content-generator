"""Travel blog style enforcer.

This version treats the generated schedule as data and rewrites the narrative
into a practical blogger-like flow.

Design goal:
- Keep schema-compatible structure (content / days_plan / blog_cards / etc.)
- Improve readability by rewriting intro + per-day copy with AI (if available).
- Fallback to deterministic copy when AI is unavailable.
"""

from __future__ import annotations

from typing import Dict, List
import re

from content.narrative_writer import generate_narrative


class TravelBlogStyleEnforcer:
    def __init__(self, cfg: Dict):
        self.cfg = cfg or {}
        self.req = self.cfg.get("requirements", {})
        self.runtime = self.cfg.get("runtime_fallback", {})

    def enforce(self, city: str, country: str, region: str, content: Dict, day_count: int = 4) -> Dict:
        if not content:
            return content

        # Always ensure destination fields exist for downstream renderers
        destination = content.get("destination", {}) if isinstance(content.get("destination"), dict) else {}
        content["destination"] = {
            "name": city,
            "country": country,
            **({"region": region} if region else {}),
            **(destination or {}),
        }

        # Prefer AI-generated narrative that mimics user's preferred tone
        narrative = generate_narrative(content, city, country, region)

        intro_text = narrative.get("intro") if isinstance(narrative, dict) else None
        if intro_text and intro_text.strip():
            content["intro"] = intro_text.strip()
        else:
            content.setdefault("intro", self._fallback_intro(city, country, region))
        closing_text = narrative.get("closing") if isinstance(narrative, dict) else None
        if closing_text and isinstance(closing_text, str):
            content["closing"] = closing_text.strip()
        else:
            content["closing"] = self._fallback_closing(city, country, region)

        hotel_section = narrative.get("hotel_section") if isinstance(narrative, dict) else ""
        if isinstance(hotel_section, str) and hotel_section.strip():
            content["hotel_section"] = hotel_section

        # Add scenario bullets in intro-style section if present
        scenarios = narrative.get("scenarios") if isinstance(narrative, dict) else []
        if isinstance(scenarios, list) and scenarios:
            # keep old key stable while adding a readable prefix
            content["travel_scenarios"] = scenarios
            scenario_section = "\n".join(f"- {s}" for s in scenarios)
            if isinstance(narrative.get("scenario_section"), str) and narrative["scenario_section"].strip():
                content["scenario_section"] = narrative.get("scenario_section")
            else:
                content["scenario_section"] = scenario_section
            # merge into intro if there not explicit section
            if "3가지 방문 시나리오" not in content.get("intro", ""):
                pass

        season_section = narrative.get("season_section")
        if isinstance(season_section, str) and season_section.strip():
            content["season_section"] = season_section

        total_estimate = content.get("total_estimate") or {}
        if total_estimate:
            content["total_estimate"] = total_estimate

        # overwrite day writing for all days, keep fields schema-compatible
        day_writings = narrative.get("day_writings") if isinstance(narrative, dict) else []
        day_map = {d.get("day", idx + 1): d for idx, d in enumerate(day_writings or []) if isinstance(d, dict)}

        for idx, day in enumerate(content.get("days_plan", []), 1):
            nw = day_map.get(idx, {}) if isinstance(day_map, dict) else {}
            title = day.get("title") or f"Day {idx}"

            # Preserve raw structured fields
            day.setdefault("spots", day.get("spots", []))
            day.setdefault("restaurants", day.get("restaurants", []))
            day.setdefault("estimated_cost", day.get("estimated_cost", {}))

            day_content = day.get("content", "")
            base_content = str(day_content or "").strip()
            should_overwrite = bool(self.runtime.get("force_day_content", True)) and len(base_content) < 500
            if (not base_content) or should_overwrite:
                if isinstance(nw, dict) and (nw.get("content") and str(nw.get("content")).strip()):
                    candidate = str(nw.get("content") or "").strip()
                    if len(candidate) >= 500:
                        day["content"] = candidate
                    else:
                        seed = candidate if candidate else base_content
                        day["content"] = self._fallback_day_content(
                            city,
                            title,
                            day.get("theme", ""),
                            idx,
                            day.get("spots") or [],
                            day.get("restaurants") or [],
                            seed_text=seed,
                        ).strip()
                elif isinstance(nw, dict) and (nw.get("morning") or nw.get("afternoon") or nw.get("evening")):
                    parts = []
                    if nw.get("opening_line"):
                        parts.append(nw.get("opening_line"))
                    if nw.get("morning"):
                        parts.append(f"오전\n{nw.get('morning')}")
                    if nw.get("afternoon"):
                        parts.append(f"오후\n{nw.get('afternoon')}")
                    if nw.get("evening"):
                        parts.append(f"저녁\n{nw.get('evening')}")
                    if nw.get("restaurant_markdown"):
                        parts.append(str(nw.get("restaurant_markdown")))
                    if nw.get("closing_sentence"):
                        parts.append(str(nw.get("closing_sentence")))
                    content_text = "\n\n".join([str(x).strip() for x in parts if str(x).strip()])
                    cleaned = self._strip_daily_cost_lines(content_text)
                    if len(cleaned) >= 500:
                        day["content"] = cleaned
                    else:
                        day["content"] = self._fallback_day_content(
                            city,
                            title,
                            day.get("theme", ""),
                            idx,
                            day.get("spots") or [],
                            day.get("restaurants") or [],
                            seed_text=cleaned,
                        ).strip()
                else:
                    day["content"] = self._fallback_day_content(
                        city,
                        title,
                        day.get("theme", ""),
                        idx,
                        day.get("spots") or [],
                        day.get("restaurants") or [],
                        seed_text=base_content,
                    ).strip()
            else:
                day["content"] = self._strip_daily_cost_lines(base_content)
            day["content"] = self._ensure_time_labels(
                day.get("content", ""),
                city=city,
                spots=day.get("spots") or [],
            )

            day["opening_line"] = nw.get("opening_line") or f"{title}: 오전/오후/저녁으로 분할해 체력 관리하며 움직이기"

            hints = nw.get("scene_hints")
            if not isinstance(hints, list):
                hints = [
                    "오전/오후/저녁 3구간으로 분할하면 동선이 지쳐도 다시 돌아올 수 있어요.",
                    "카메라는 빛이 좋은 구간에서 한 번, 휴식 구간에서 한 번으로 나눠 잡으세요.",
                ]
            day["scene_hints"] = hints[:3]

            cards = nw.get("cards")
            if not isinstance(cards, list):
                cards = self._fallback_cards(city, day.get("spots") or [], idx)
            day["blog_cards"] = [self._normalize_card(c) for c in cards if self._is_card(c)]
            if not day["blog_cards"]:
                day["blog_cards"] = self._fallback_cards(city, day.get("spots") or [], idx)

            # optional: reservation banner stays
            day.setdefault("reservation_notice", day.get("reservation_notice", ""))
        self._ensure_cost_key(content)
        self._ensure_tier_lists(content)
        self._ensure_reservation_links(content)
        return content

    @staticmethod
    def _strip_daily_cost_lines(text: str) -> str:
        if not isinstance(text, str):
            return text or ""
        import re
        cleaned = re.sub(r"\n?일일 비용 가이드\n(?:- .*\n?)*", "\n", text)
        return cleaned.strip()

    def _fallback_intro(self, city: str, country: str, region: str) -> str:
        return (
            f"{city}는 지도에 찍힌 동선보다, 한 번에 오래 머무를 수 있는 리듬이 더 중요해요. "
            f"{country} 기준으로도 {region} 특성에 맞춰 움직임/휴식이 분명해야 피로는 줄고 기억은 커져요."
        )


    @staticmethod
    def _fallback_closing(city: str, country: str, region: str) -> str:
        return (
            f"{city}의 리듬은 급하게 만들지 않으면 더 오래 남아요.\n"
            f"일정에서 가장 좋은 순간은, 계획을 잠깐 비웠을 때 찾아옵니다.\n"
            f"오늘의 장면 한두 개면 충분해요.\n"
            f"무리한 채우기는 오히려 피로로 바뀌기 쉽기 때문에 천천히 나누는 흐름이 훨씬 좋아요.\n"
            f"돌아보면 {region or country}에서의 한 날은 더 큰 수확이 됐을 거예요."
        )

    def _fallback_day_content(
        self,
        city: str,
        title: str,
        theme: str,
        idx: int,
        spots: List[Dict],
        restaurants: List[Dict],
        seed_text: str = "",
    ) -> str:
        morning = spots[0] if len(spots) >= 1 else {"name": f"{city} 중심가", "desc": "", "tip": ""}
        afternoon = spots[1] if len(spots) >= 2 else morning
        evening = spots[2] if len(spots) >= 3 else afternoon

        budget_rest = next((r for r in restaurants if (r.get("price_tier") or "") == "budget"), None)
        mid_rest = next((r for r in restaurants if (r.get("price_tier") or "") == "mid"), None)
        lux_rest = next((r for r in restaurants if (r.get("price_tier") or "") == "luxury"), None)

        budget_label = (budget_rest or {}).get("name") or f"{city} 가성비 식당"
        mid_label = (mid_rest or {}).get("name") or f"{city} 일반 다이닝"
        lux_label = (lux_rest or {}).get("name") or f"{city} 고급 다이닝"

        seed_line = seed_text.strip()
        seed_intro = ""
        if seed_line:
            first_sentence = re.split(r"[.!?]\s+", seed_line)[0].strip()
            if first_sentence:
                seed_intro = f"{first_sentence}. "

        return (
            f"{title}은(는) {theme or '도시의 기본 리듬'}을 중심으로 정리해요. "
            f"{seed_intro}체크리스트를 늘리는 대신, 구간별 체류 시간을 분명히 잡으면 피로가 확실히 줄어요.\n\n"
            f"오전에는 {morning.get('name', city)}부터 시작해 도시의 결을 먼저 파악하세요. "
            f"{(morning.get('desc') or '첫 구간에서 페이스를 조절하면 하루 전체가 훨씬 안정적입니다.')} "
            f"{(morning.get('tip') or '오픈 직후 시간대를 쓰면 대기 스트레스를 크게 줄일 수 있어요.')}\n\n"
            f"오후는 {afternoon.get('name', city)}을(를) 중심으로 깊이를 주는 시간이에요. "
            f"{(afternoon.get('desc') or '여러 곳을 얕게 돌기보다 핵심 한 곳 체류 시간을 늘리는 편이 만족도가 높아요.')} "
            "중간에 20~30분 버퍼를 넣어 체력과 날씨 변수를 흡수해 주세요.\n\n"
            f"저녁엔 {evening.get('name', city)} 한 구간으로 압축해 마무리하면 좋아요. "
            f"{(evening.get('desc') or '야간 전환 시간대의 분위기를 짧게 집중해서 즐기고, 귀가 동선은 단순하게 잡으세요.')} "
            "내일 일정을 위해 이동 욕심을 줄이는 게 결과적으로 더 좋은 선택입니다.\n\n"
            f"식사는 동선 기준으로 가성비({budget_label}) → 일반({mid_label}) → 고급({lux_label}) 순으로 선택지를 두면 결정이 빨라져요. "
            "기대치를 과하게 올리기보다 여유를 남기면, 같은 도시도 훨씬 오래 기억에 남습니다."
        )

    @staticmethod
    def _is_card(card) -> bool:
        return isinstance(card, dict) and (card.get("label") or "").strip() and (card.get("value") is not None)

    @staticmethod
    def _normalize_card(card: Dict) -> Dict:
        return {"label": str(card.get("label") or "메모").strip() or "메모", "value": str(card.get("value") or "").strip() or "-"}

    def _fallback_cards(self, city: str, spots: List[Dict], idx: int) -> List[Dict[str, str]]:
        first = (spots[0].get("name") if spots else city) or city
        return [
            {"label": "촬영 포인트", "value": f"{first}은(는) 해가 정점 가기 전 1~2시간이 가장 안정적으로 잘 나옵니다. 첫 컷은 넓고, 끝 컷은 근접하게."},
            {"label": "동선 리듬", "value": "오전: 시작 정렬 / 오후: 핵심 집중 / 저녁: 마무리 루트 1개만."},
            {"label": "실수 포인트", "value": "점심 전후 1시간은 무리하게 움직이지 말고 버퍼 20분 확보."},
            {"label": "체크리스트", "value": "지도 공유 링크, 교통권, 예약확인서, 비상연락처를 한 곳에 보관하면 좋아요."},
        ]

    @staticmethod
    def _ensure_tier_lists(content: Dict) -> None:
        hotels = content.get("hotels")
        if isinstance(hotels, dict):
            hotels.setdefault("budget", hotels.get("budget") or [])
            hotels.setdefault("mid", hotels.get("mid") or [])
            hotels.setdefault("luxury", hotels.get("luxury") or [])

    @staticmethod
    def _ensure_reservation_links(content: Dict) -> None:
        must_reserve = content.get("must_reserve")
        if not isinstance(must_reserve, list):
            content["must_reserve"] = []
            must_reserve = content["must_reserve"]

        for row in must_reserve:
            if isinstance(row, dict) and row.get("url") and not str(row["url"]).startswith("http"):
                row["url"] = ""

    @staticmethod
    def _ensure_cost_key(content: Dict) -> None:
        for day in content.get("days_plan", []):
            summary = day.get("summary_cost")
            if isinstance(summary, dict):
                continue

            # keep estimated_cost first
            day_cost = day.get("estimated_cost")
            if not isinstance(day_cost, dict):
                day_cost = {}
                day["estimated_cost"] = day_cost
            if not isinstance(day.get("summary_cost"), dict):
                day["summary_cost"] = day_cost

    @staticmethod
    def _ensure_time_labels(text: str, city: str, spots: List[Dict]) -> str:
        body = (text or "").strip()
        if not body:
            body = f"{city} 일정 본문입니다."

        labels = ["오전", "오후", "저녁"]
        missing = [label for label in labels if label not in body]
        if not missing:
            return body

        morning_name = spots[0].get("name") if len(spots) >= 1 and isinstance(spots[0], dict) else f"{city} 중심 구간"
        afternoon_name = spots[1].get("name") if len(spots) >= 2 and isinstance(spots[1], dict) else f"{city} 주요 동선"
        evening_name = spots[2].get("name") if len(spots) >= 3 and isinstance(spots[2], dict) else f"{city} 야간 구간"
        fallback_map = {
            "오전": f"오전\n{morning_name}에서 하루 리듬을 천천히 시작해요.",
            "오후": f"오후\n{afternoon_name} 중심으로 이동 간격을 조절해요.",
            "저녁": f"저녁\n{evening_name} 한 구간에 집중하고 일정을 마무리해요.",
        }
        additions = [fallback_map[label] for label in labels if label in missing]
        return f"{body}\n\n" + "\n\n".join(additions)


def apply_style_guard(content: Dict, city: str, country: str, region: str, cfg: Dict, day_count: int = 4) -> Dict:
    return TravelBlogStyleEnforcer(cfg).enforce(city, country, region, content, day_count=day_count)
