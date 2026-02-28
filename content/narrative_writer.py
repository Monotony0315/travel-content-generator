"""LLM-assisted narrative writer for travel blog content.

This module generates the final prose in a practical, conversational style.
By default it prefers Gemini API and falls back to local codex or deterministic
formatting when unavailable.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Tuple


SYSTEM_STYLE = """당신은 실제로 해당 도시를 다녀온 한국어 여행 블로거다.
톤:
- 실전형 + 담백한 감성, 존댓말 중심(~좋아요/~하세요)
- 과장/홍보 문장 금지, 여행자 입장에서 바로 써먹을 문장으로 작성

핵심 규칙:
- 단순 정보 나열 대신 "오전-오후-저녁" 이동 흐름으로 스토리텔링
- 각 구간마다 장면 1개(빛/소리/분위기), 실전 팁 1개(대기/교통/체력), 주의 포인트 1개를 자연스럽게 녹임
- 문단은 3~4문장 단위로 쪼개 읽기 쉽게 유지
- 식당은 가성비/일반/고급 3티어만 제시, 동선과 어울리는 이유를 짧게 덧붙임
- 결론은 "기대치보다 여유를 남기는 여행" 톤으로 마무리

금지:
- 뻔한 상투어 반복("환상적", "잊지 못할" 연속 사용)
- 같은 문장 패턴 반복
- 근거 없는 수치/과장
"""


# reference-like output skeleton for deterministic rendering
MARKDOWN_BRIEF_TEMPLATE = """# 🇫🇷 {city} 5일 완벽 가이드 | 통계적 최적 기간 + 3티어 예산 비교
# {city} 5일 여행, 첫 방문이라면 이렇게 가는 게 좋아요

{intro}

---

## 📊 {city} 통계적 최적 방문 시기
{season_section}

### 🎯 3가지 방문 시나리오 추천
{scenario_section}

## 🗓️ Day {day_no} — {title}
{day_body}

## 🏨 호텔 추천 (3티어 비교)
{hotel_section}

## 💰 5일 총 예산 비교표
{budget_section}

## 🚨 비상연락처 & 유용 정보
{emergency_section}

## 📝 마무리
{closing}
"""


def _normalize_days(days: List[Dict]) -> List[Dict]:
    out = []
    for d in days or []:
        spots = d.get("spots") or []
        restaurants = d.get("restaurants") or []
        out.append(
            {
                "day": d.get("day", 1),
                "title": d.get("title", ""),
                "theme": d.get("theme", ""),
                "spots": [
                    {
                        "name": s.get("name", ""),
                        "time": s.get("time", ""),
                        "desc": s.get("description") or s.get("desc", ""),
                        "tip": s.get("tip", ""),
                        "name_with_time": f"{s.get('time', '').strip()} {s.get('name', '')}".strip(),
                        "maps_url": s.get("maps_url", ""),
                    }
                    for s in spots[:6]
                ],
                "restaurants": [
                    {
                        "name": r.get("name", ""),
                        "type": r.get("type", r.get("cuisine", "")),
                        "price": r.get("price", ""),
                        "tip": r.get("tip", ""),
                        "price_tier": r.get("price_tier", ""),
                        "maps_url": r.get("maps_url", ""),
                    }
                    for r in restaurants[:6]
                ],
                "reservation_notice": d.get("reservation_notice", ""),
                "content": d.get("content", ""),
            }
        )
    return out


def _split_spots_by_time(spots: List[Dict]) -> Dict[str, List[Dict]]:
    buckets = {"morning": [], "afternoon": [], "evening": []}
    for row in spots:
        t = (row.get("time") or "").lower()
        n = row.get("name", "")
        if any(k in t for k in ["오전", "아침", "morning", "am"]):
            buckets["morning"].append(row)
        elif any(k in t for k in ["오후", "저녁", "evening", "pm"]):
            buckets["evening"].append(row)
        else:
            buckets["afternoon"].append(row)

    # guarantee at least one sample per section
    if not buckets["morning"] and spots:
        buckets["morning"].append(spots[0])
    if not buckets["afternoon"] and len(spots) > 1:
        buckets["afternoon"].append(spots[1])
    if not buckets["evening"] and len(spots) > 2:
        buckets["evening"].append(spots[2])
    return buckets


def _section_from_markdown_table(lines: List[str]) -> str:
    # keep markdown table formatting and compact if needed.
    if not lines:
        return ""
    return "\n".join(lines)


def _build_prompt(city: str, country: str, region: str, days: List[Dict], intro_text: str) -> str:
    day_chunks = []
    for d in days:
        buckets = _split_spots_by_time(d.get("spots", []))
        day_chunks.append(
            f"DAY {d['day']}: {d.get('title')}\n"
            f"theme={d.get('theme')}\n"
            f"morning={json.dumps(buckets['morning'], ensure_ascii=False)}\n"
            f"afternoon={json.dumps(buckets['afternoon'], ensure_ascii=False)}\n"
            f"evening={json.dumps(buckets['evening'], ensure_ascii=False)}\n"
            f"restaurants={json.dumps(d.get('restaurants', [])[:6], ensure_ascii=False)}\n"
            f"notice={d.get('reservation_notice')}\n"
            f"old_content={d.get('content', '')[:900]}\n"
        )

    return (
        "도시: " + city + " (" + country + "), 지역: " + region + "\n\n"
        "기준 intro 원본:\n"
        + intro_text + "\n\n"
        "요청 형식(JSON)으로 정확히 하나의 객체만 출력(JSON outside text 금지):\n"
        + '{\n'
        + '  "intro": "intro 5줄(문장 위주)",\n'
        + '  "closing": "마무리 5줄(실전형 멘트)",\n'
        + '  "scenarios": ["베스트 ...", "균형 ...", "가성비 ..."],\n'
        + '  "scenario_section": "### ...\\n- ...",\n'
        + '  "season_section": "| 월 | ... 표 ...",\n'
        + '  "day_writings": [\n'
        + '    {\n'
        + '      "day": 1,\n'
        + '      "title": "Day 1 — ...",\n'
        + '      "opening_line": "...",\n'
        + '      "morning": "... 마크다운 문장 ...",\n'
        + '      "afternoon": "... 마크다운 문장 ...",\n'
        + '      "evening": "... 마크다운 문장 ...",\n'
        + '      "content": "Day 1 본문(마크다운). 오전/오후/저녁을 각각 1개 문단(각 3~4문장)으로 구성하고 전체 700~1100자",\n'
        + '      "cards": [\n'
        + '        {"label": "촬영 포인트", "value": "..."},\n'
        + '        {"label": "동선 리듬", "value": "..."},\n'
        + '        {"label": "실수 포인트", "value": "..."},\n'
        + '        {"label": "체크리스트", "value": "..."}\n'
        + '      ],\n'
        + '      "restaurant_markdown": "Day 1 식당 추천 (동선 기준, 3티어)\\n- ...\\n- ...",\n'
        + '      "closing_sentence": "..."\n'
        + '    }\n'
        + '  ]\n'
        + '}\n\n'
        + '톤/형식 규칙:\n'
        + '- intro는 5개 줄, closing도 5개 줄(문장 단위).\n'
        + '- 오프닝은 "한 번에 많이 넣기보다" 느낌.\n'
        + '- Day는 오전/오후/저녁을 “자연스러운 문단”으로 풀어 써주세요. 각 섹션은 문단 1개 정도면 충분해요.\n'
        + '- 식당은 3티어(가성비/일반/고급)로 한곳씩 우선 제시.\n'
        + '- 교통/대기/우천 대안처럼 실제 여행자가 바로 적용할 팁을 각 Day에 최소 2개 포함.\n'
        + '- 동일 표현 반복을 피하고, 장면 묘사는 구체 명칭 기반으로 작성.\n'
        + '- 문장 내부에 [명칭](URL) 형태 마크다운 링크가 있으면 더 좋음.\n'
        + '- JSON만 반환하고 추가 주석/코드블록 없이.\n\n'
        + 'Day inputs:\n'
        + "\n".join(day_chunks)
    )

def _trim_to_json(text: str) -> str:
    if not text:
        return text
    text = text.strip()
    if text.startswith("```"):
        text = text.strip('`')
    # extract first JSON block
    m = re.search(r"\{[\s\S]*\}$", text)
    if m:
        return m.group(0).strip()
    return text


def _try_gemini_payload(city: str, country: str, region: str, days: List[Dict], intro_text: str) -> Tuple[Dict | None, str]:
    if os.getenv("TRAVEL_BLOG_USE_GEMINI", "0") != "1":
        return None, "disabled"

    key = os.getenv("GEMINI_API_KEY", "")
    if not key:
        return None, "no_key"

    model = os.getenv("TRAVEL_BLOG_MODEL", os.getenv("TRAVEL_BLOG_MODEL_GEMINI", "gemini-2.5-flash"))
    candidates = [m for m in [model, "gemini-2.5-flash", "gemini-flash-latest", "gemini-2.0-flash", "gemini-2.5-pro"] if isinstance(m, str)]
    last_err = None
    txt = ""

    try:
        from google import genai as ga
        client = ga.Client(api_key=key)
        prompt = f"{SYSTEM_STYLE}\n\n{_build_prompt(city, country, region, days, intro_text)}"

        for m in candidates:
            try:
                out = client.models.generate_content(
                    model=m,
                    contents=prompt,
                    config={"response_mime_type": "application/json", "temperature": 0.6, "max_output_tokens": 4096},
                )
                txt = (getattr(out, "text", "") or "").strip()
                if txt:
                    break
            except Exception as e:
                last_err = e
                txt = ""
                continue

        if not txt:
            # keep compact reason for diagnostics
            if last_err is not None:
                return None, f"gemini_failed:{type(last_err).__name__}"
            return None, "empty"

        txt = _trim_to_json(txt)
        if not txt:
            return None, "empty"
        try:
            return json.loads(txt), "ok"
        except Exception:
            return None, "json_parse"
    except Exception:
        return None, "exception"

def _try_codex_payload(city: str, country: str, region: str, days: List[Dict], intro_text: str) -> Tuple[Dict | None, str]:
    # Fallback path for environments without GEMINI usage.
    model = os.getenv("TRAVEL_BLOG_MODEL_CLAUDE", "gpt-5.2-codex")
    if not (os.getenv("TRAVEL_BLOG_USE_CLAUDE", "1") == "1"):
        return None, "disabled"

    prompt = (
        _build_prompt(city, country, region, days, intro_text)
        + "\n\nIMPORTANT: Output must be ONLY a valid JSON object, no markdown/code fences."
    )
    with tempfile.NamedTemporaryFile(delete=False, mode="w", encoding="utf-8", suffix=".json") as f:
        out_path = f.name

    cmd = ["codex", "exec", "--json", "-m", model, "-o", out_path, prompt]

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=75)
        p = Path(out_path)
        txt = p.read_text(encoding="utf-8") if p.exists() else ""
        p.unlink(missing_ok=True)

        if not txt:
            return None, "empty"

        agent_text = ""
        for line in txt.splitlines()[::-1]:
            ln = line.strip()
            if not ln:
                continue
            try:
                obj = json.loads(ln)
            except Exception:
                continue
            if isinstance(obj, dict) and obj.get("type") == "agent_message" and isinstance(obj.get("text"), str):
                agent_text = obj.get("text", "").strip()
                break

        candidates = []
        if agent_text:
            candidates.append(agent_text)
        candidates.append(txt)

        for cand in candidates:
            s = cand.find("{")
            e = cand.rfind("}")
            if s != -1 and e != -1 and e > s:
                body = cand[s : e + 1]
                try:
                    return json.loads(body), "agent_json"
                except Exception:
                    pass

        return None, "parse_error"
    except subprocess.TimeoutExpired:
        return None, "timeout"
    except Exception:
        return None, "exception"


def _build_fallback(city: str, country: str, region: str, days: List[Dict], base_intro: str, content: Dict | None = None) -> Dict:
    scenario_section = (
        "- 베스트 시즌: 5월 중순~6월 초, 9~10월 초 - 날씨/분위기 우선\n"
        "- 균형형: 4월 하순~5월 초, 10월 중순~11월 초 - 가격+혼잡 균형\n"
        "- 가성비형: 1~2월, 11월~12월 - 숙박 절약/한적함\n"
    )

    season_section = (
        "| 월 | 평균기온 | 강수량 | 관광객 밀도 | 숙박비 지수 | 추천도 | 특징 |\n"
        "|---|---------|--------|------------|------------|--------|------|\n"
        "| 4~6월 | 13~21°C | 낮음 | 중간~높음 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 꽃/햇빛 균형\n"
        "| 7~8월 | 24°C | 낮음 | 매우 높음 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | 더위·인파 주의\n"
        "| 9~10월 | 15~20°C | 낮음 | 중간 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 가을 단풍, 여유\n"
    )

    writings = []
    for idx, d in enumerate(days, 1):
        buckets = _split_spots_by_time(d.get("spots", []))
        am_spot = buckets["morning"][0] if buckets["morning"] else {"name": f"{city} 핵심 코스", "desc": "", "tip": ""}
        pm_spot = buckets["afternoon"][0] if buckets["afternoon"] else {"name": f"{city} 산책 코스", "desc": "", "tip": ""}
        ev_spot = buckets["evening"][0] if buckets["evening"] else {"name": f"{city} 야경 구간", "desc": "", "tip": ""}
        s_am = am_spot.get("name") or f"{city} 핵심 코스"
        s_pm = pm_spot.get("name") or f"{city} 산책 코스"
        s_ev = ev_spot.get("name") or f"{city} 야경 구간"
        rest = d.get("restaurants", []) or []
        r_budget = next((r.get("name") for r in rest if (r.get("price_tier") or "budget") == "budget"), f"{city} 로컬 가성비 식당")
        r_mid = next((r.get("name") for r in rest if (r.get("price_tier") or "mid") == "mid"), f"{city} 일반 다이닝")
        r_lux = next((r.get("name") for r in rest if (r.get("price_tier") or "luxury") == "luxury"), f"{city} 고급 다이닝")
        r_budget_price = next((r.get("price") for r in rest if (r.get("price_tier") or "budget") == "budget" and r.get("price")), "합리적")
        r_mid_price = next((r.get("price") for r in rest if (r.get("price_tier") or "mid") == "mid" and r.get("price")), "중간대")
        r_lux_price = next((r.get("price") for r in rest if (r.get("price_tier") or "luxury") == "luxury" and r.get("price")), "프리미엄")

        am_desc = (am_spot.get("desc") or "").strip()
        pm_desc = (pm_spot.get("desc") or "").strip()
        ev_desc = (ev_spot.get("desc") or "").strip()
        am_tip = (am_spot.get("tip") or "").strip()
        pm_tip = (pm_spot.get("tip") or "").strip()
        ev_tip = (ev_spot.get("tip") or "").strip()

        writing = {
            "day": idx,
            "title": d.get("title", f"Day {idx}"),
            "opening_line": (
                f"{d.get('title', f'Day {idx}')}은(는) 체크리스트보다 걸음의 속도를 맞추는 날이에요. "
                "많이 보기보다, 남는 장면을 분명히 가져가면 충분해요."
            ),
            "scene_hints": [
                "오전은 핵심 1~2곳만 잡고, 줄 대기 전 도착이 핵심이에요.",
                "오후는 이동 사이 버퍼 20분을 넣으면 체력 소모가 확 줄어요.",
                "저녁은 한 구간만 길게 보고, 다음 날 컨디션을 남겨두세요.",
            ],
            "morning": (
                f"오전에는 {s_am}부터 시작해요. {am_desc or '첫 구간에서 도시의 결을 읽는 데 시간을 쓰면 이후 동선이 훨씬 안정적이에요.'} "
                f"{am_tip or '입장 대기가 생기기 전, 오픈 직후 1시간 안에 도착하면 체감 피로가 크게 줄어요.'}"
            ),
            "afternoon": (
                f"오후에는 {s_pm}으로 흐름을 옮겨요. {pm_desc or '점심 직후엔 무리하게 여러 곳을 붙이기보다 핵심 한 곳을 깊게 보는 편이 만족도가 높아요.'} "
                f"{pm_tip or '이동 거리가 길어지기 쉬운 시간대라, 카페/실내 휴식 30분을 미리 넣어두면 일정이 무너지지 않아요.'}"
            ),
            "evening": (
                f"저녁은 {s_ev} 한 구간에 집중해 마무리해요. {ev_desc or '해 질 무렵부터 야간 조명 전환 사이가 가장 분위기가 좋은 시간이에요.'} "
                f"{ev_tip or '귀가 동선은 단순하게 잡고, 늦은 시간 무리한 이동은 피하는 게 다음 날 컨디션에 유리해요.'}"
            ),
            "cards": [
                {"label": "촬영 포인트", "value": f"{s_am}은(는) 오픈 직후, {s_ev}은(는) 블루아워 전후가 가장 안정적으로 예쁜 컷이 나와요."},
                {"label": "동선 리듬", "value": "오전 집중-오후 완급조절-저녁 압축 루프를 유지하면 지치지 않아요."},
                {"label": "실수 포인트", "value": "오후 이동을 촘촘하게 넣으면 저녁 만족도가 급격히 떨어집니다."},
                {"label": "체크리스트", "value": "예약 캡처, 지도 오프라인 저장, 귀가 루트, 우천 대안 1개를 먼저 준비하세요."},
            ],
            "restaurant_markdown": (
                "Day {0} 식당 추천 (동선 기준, 3티어)\n"
                "- 가성비: {budget} ({budget_price}) — 이동 중간에 짧게 들러도 만족도가 높은 선택\n"
                "- 일반: {mid} ({mid_price}) — 동선이 길어지는 날 중심을 잡아주는 선택\n"
                "- 고급: {lux} ({lux_price}) — 하루를 기분 좋게 마감하고 싶을 때 가장 좋은 선택\n"
            ).format(
                idx,
                budget=r_budget,
                mid=r_mid,
                lux=r_lux,
                budget_price=r_budget_price,
                mid_price=r_mid_price,
                lux_price=r_lux_price,
            ),
            "closing_sentence": "오늘 다 보지 못해도 괜찮아요. 여유를 남긴 일정이 결국 더 오래, 더 선명하게 기억에 남아요.",
        }
        writing["content"] = (
            f"오전은 {s_am}, 오후는 {s_pm}, 저녁은 {s_ev} 한 구간씩 잡아 리듬을 만드는 날입니다. "
            "이 도시에서는 많이 찍는 것보다, 좋은 타이밍에 머무는 게 훨씬 중요해요.\n\n"
            f"{writing['morning']}\n\n"
            f"{writing['afternoon']}\n\n"
            f"{writing['evening']}\n\n"
            "실전 운영 팁: 일정이 밀리면 저녁 코스 하나를 과감히 비우고, 귀가 동선을 먼저 확보하세요. "
            "이 원칙 하나로 여행 피로도가 확실히 줄어듭니다.\n\n"
            f"{writing['restaurant_markdown']}\n\n"
            f"{writing['closing_sentence']}"
        )
        writing["content_md"] = (
            f"{writing['morning']}\n\n{writing['afternoon']}\n\n{writing['evening']}\n\n"
        )
        writings.append(writing)

    # optional hotel hint from structured data
    hotels = {}
    if isinstance(content, dict):
        hotels = content.get("hotels") or {}
    budget_h = hotels.get("budget") or []
    mid_h = hotels.get("mid") or []
    luxury_h = hotels.get("luxury") or []
    hotel_lines = []
    if budget_h:
        hotel_lines.append(f"가성비: {budget_h[0].get('name', '미정')} - {budget_h[0].get('price_per_night', '')}")
    if mid_h:
        hotel_lines.append(f"일반: {mid_h[0].get('name', '미정')} - {mid_h[0].get('price_per_night', '')}")
    if luxury_h:
        hotel_lines.append(f"고급: {luxury_h[0].get('name', '미정')} - {luxury_h[0].get('price_per_night', '')}")
    hotel_section = "\n".join(f"- {row}" for row in hotel_lines) if hotel_lines else ""

    return {
        "intro": (
            f"{base_intro}\n"
            f"{city}는 '많이 보기'보다 '어떻게 걸었는가'가 더 오래 남아요.\n"
            f"아침엔 동선의 밀도를 낮추고, 오후엔 이동보다 체류를 늘리는 쪽으로 가시면 좋아요.\n"
            f"한 번에 몰아넣기보다 포인트를 하나씩 정리하면 피로가 덜하고 품질이 더 좋아져요.\n"
            f"예약이 필요한 구간만 미리 잡고, 여유 구간은 즉흥으로 채우면 훨씬 안정적이에요.\n"
            f"도시의 하이라이트는 결국 ‘완주’보다 ‘기억에 남는 장면’에서 나옵니다."
        ),
        "closing": (
            f"기대보다 여유가 먼저면 일정은 훨씬 부드러워져요.\n"
            f"오늘은 다 담지 못했더라도 내일이 있으니까 포인트를 분할하세요.\n"
            f"동선은 완성보다 반복 가능한 리듬이 중요합니다.\n"
            f"오후가 지나기 전에 이동 버퍼 20분을 남겨두면 당황 확률이 크게 줄어요.\n"
            f"결국 남는 건, 지친 발걸음이 아닌 남긴 장면입니다."
        ),
        "scenarios": [
            "베스트 시즌: 날씨+분위기 우선, 4~6월 / 9~10월",
            "균형형: 4월 하순~5월 초, 10월 중순~11월 초",
            "가성비형: 1월~2월, 11월 하순~12월 초",
        ],
        "season_section": season_section,
        "scenario_section": scenario_section,
        "hotel_section": hotel_section,
        "day_writings": writings,
    }


def _to_gemini_narrative(payload: Dict) -> str:
    # optional compact final markdown output
    if not isinstance(payload, dict):
        return ""
    snippets = [
        payload.get("intro", ""),
        payload.get("season_section", ""),
        "\n".join(payload.get("scenarios", []) or []),
    ]
    return "\n\n".join(s for s in snippets if s)


def _try_openai_payload(city: str, country: str, region: str, days: List[Dict], intro_text: str) -> Dict | None:
    if os.getenv("TRAVEL_BLOG_TRY_OPENAI", "0") != "1":
        return None
    key = os.getenv("OPENAI_API_KEY", "")
    if not key:
        return None

    try:
        from openai import OpenAI

        client = OpenAI(api_key=key)
        model = os.getenv("TRAVEL_BLOG_OPENAI_MODEL", "gpt-4o-mini")
        response = client.chat.completions.create(
            model=model,
            temperature=0.55,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_STYLE},
                {"role": "user", "content": _build_prompt(city, country, region, days, intro_text)},
            ],
            timeout=30,
        )
        content = response.choices[0].message.content or "{}"
        return json.loads(content)
    except Exception:
        return None


def _get_provider_payload(city: str, country: str, region: str, days: List[Dict], base_intro: str) -> Dict | None:
    provider = os.getenv("TRAVEL_BLOG_PROVIDER", "gemini").lower().strip()

    if provider == "gemini":
        payload, status = _try_gemini_payload(city, country, region, days, base_intro)
        if isinstance(payload, dict):
            return payload

        # fallback order for reliability
        payload, status = _try_codex_payload(city, country, region, days, base_intro)
        if isinstance(payload, dict):
            return payload

    elif provider == "codex":
        payload, status = _try_codex_payload(city, country, region, days, base_intro)
        if isinstance(payload, dict):
            return payload

    elif provider == "openai":
        payload = _try_openai_payload(city, country, region, days, base_intro)
        if isinstance(payload, dict):
            return payload

    # fallback chain when provider fails
    payload = _try_openai_payload(city, country, region, days, base_intro)
    if isinstance(payload, dict):
        return payload
    payload, status = _try_codex_payload(city, country, region, days, base_intro)
    if isinstance(payload, dict):
        return payload

    return None


def generate_narrative(content: Dict, city: str, country: str, region: str) -> Dict:
    """Return writer output; fallback to deterministic composer when model fails."""
    if not isinstance(content, dict):
        return {"intro": "", "scenarios": [], "day_writings": []}

    base_intro = (content.get("intro") or "").strip() or f"{city}의 1일을 리듬 있게 정리한 5일 여행입니다."
    raw_days = _normalize_days(content.get("days_plan") or [])

    payload = _get_provider_payload(city, country, region, raw_days, base_intro)
    if isinstance(payload, dict) and payload.get("day_writings"):
        # normalize legacy fields
        return payload

    payload = _build_fallback(city, country, region, raw_days, base_intro, content)
    payload["provider"] = "fallback"
    return payload
