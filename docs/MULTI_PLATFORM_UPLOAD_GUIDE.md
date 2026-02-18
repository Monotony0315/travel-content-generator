# 여행 블로그 멀티 플랫폼 업로드 가이드
## Notion → 티스토리 & 네이버 블로그 이전 메뉴얼

---

## 📋 개요

이 문서는 Notion에 생성된 여행 가이드를 티스토리와 네이버 블로그에 오류 없이 업로드하는 방법을 설명합니다.

---

## 1️⃣ Notion 콘텐츠 남기기

### 방법 A: Notion Export 기능 사용

1. Notion 페이지 우측 상단 `···` (더보기) 클릭
2. `Export` 선택
3. Export format: **Markdown & CSV** 선택
4. Include subpages: ✓ 체크
5. `Export` 버튼 클릭
6. 다운로드된 `.zip` 파일 압축 해제
7. `.md` 파일 확인

### 방법 B: 수동 복사 (권장)

1. Notion 페이지에서 `Ctrl+A` (전체 선택)
2. `Ctrl+C` (복사)
3. 메모장 또는 마크다운 에디터에 붙여넣기
4. 이미지는 우클릭 → `이미지 주소 복사` 로 개별 저장

---

## 2️⃣ 티스토리 업로드

### 이미지 준비

티스토리는 외부 이미지 URL을 자동으로 가져오지 못하는 경우가 많습니다.

```
❌ 외부 URL 직접 사용
https://images.unsplash.com/photo-xxx...

✅ 티스토리 서버에 업로드
- 이미지를 먼저 다운로드
- 티스토리 에디터에서 직접 업로드
```

### 업로드 절차

1. **티스토리 관리자 페이지 접속**
   - https://www.tistory.com/admin

2. **새 글 작성**
   - `글` → `글 작성` 클릭

3. **에디터 선택**
   - **Markdown 에디터** 사용 권장
   - 또는 HTML 모드로 전환

4. **콘텐츠 붙여넣기**
   - Markdown 파일 내용 복사
   - 에디터에 붙여넣기

5. **이미지 처리**
   ```
   방법 1: 드래그 앤 드롭
   - 로컬에 저장된 이미지를 에디터로 드래그
   
   방법 2: URL 삽입
   - ![대체텍스트](이미지URL)
   - 단, 티스토리는 일부 외부 URL 차단 가능
   ```

6. **서식 조정**
   - 헤딩 (H1, H2, H3) 확인
   - 인용구 (>) 스타일 적용
   - 구분선 (---) 추가

7. **미리보기 & 발행**
   - `미리보기`로 확인
   - `발행` 클릭

### 주의사항

| 문제 | 해결방법 |
|------|---------|
| 외부 이미지 안보임 | 이미지 다운로드 후 재업로드 |
| 링크 깨짐 | 하이퍼링크 재설정 |
| 폰트 깨짐 | 티스토리 기본 폰트 사용 |
| 표 깨짐 | HTML 테이블로 변환 |

---

## 3️⃣ 네이버 블로그 업로드

### 네이버 블로그 특성

네이버 블로그는 HTML/Markdown 직접 입력이 제한적입니다. **스마트에디터 3.0** 사용 권장.

### 업로드 절차

1. **네이버 블로그 접속**
   - https://blog.naver.com

2. **새 글 작성**
   - `글쓰기` 클릭

3. **에디터 모드 선택**
   - **스마트에디터 3.0** 선택
   - HTML 모드 (상단 메뉴에서 선택)

4. **Markdown → HTML 변환**
   
   온라인 변환기 사용:
   - https://www.markdowntohtml.com/
   - https://markdowntohtml.com/
   
   또는 VS Code 확장 프로그램:
   - Markdown Preview Enhanced 설치
   - HTML로 남기기

5. **HTML 붙여넣기**
   - 에디터를 HTML 모드로 전환
   - 변환된 HTML 코드 붙여넣기

6. **이미지 처리**
   ```
   방법 1: 멀티업로더 사용
   - '사진' 버튼 클릭
   - 이미지 일괄 업로드
   
   방법 2: 본문 삽입
   - 이미지 위치에 커서 배치
   - 개별 이미지 업로드
   ```

7. **스타일 조정**
   - 글자 크기: 기본 12pt 권장
   - 줄 간격: 1.5~1.8 설정
   - 본문 색상: #333333 (어두운 회색)

8. **미리보기 & 발행**
   - `미리보기` 확인
   - `발행` 클릭

### 네이버 블로그 꿀팁

```
✅ 효과적인 포맷팅
- 소제목: 크기 16pt, 굵게, 색상 #1a1a1a
- 본문: 크기 12pt, 색상 #333333
- 강조: 색상 #ff6b6b (빨강) 또는 #4ecdc4 (청록)

✅ 이미지 크기
- 가로폭: 800px 권장 (모바일 최적화)
- 파일 크기: 1MB 이하 (로딩 속도)
- 포맷: JPG (사진), PNG (그래픽)

✅ 링크 처리
- 외부 링크: 새 창에서 열기 설정
- 남기 링크: # 기호 사용
```

---

## 4️⃣ 자동화 도구 (선택사항)

### Python 스크립트로 이미지 다운로드

```python
# images_downloader.py
import requests
import os
from urllib.parse import urlparse

def download_image(url, folder="images"):
    """이미지 다운로드"""
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            # 파일명 생성
            parsed = urlparse(url)
            filename = os.path.basename(parsed.path)
            if not filename:
                filename = "image.jpg"
            
            filepath = os.path.join(folder, filename)
            with open(filepath, 'wb') as f:
                f.write(response.content)
            print(f"✅ 다운로드 완료: {filename}")
            return filepath
    except Exception as e:
        print(f"❌ 다운로드 실패: {url} - {e}")
    return None

# 사용 예시
image_urls = [
    "https://images.unsplash.com/photo-xxx...",
    "https://images.pexels.com/photos/xxx...",
]

for url in image_urls:
    download_image(url)
```

### 실행
```bash
python3 images_downloader.py
```

---

## 5️⃣ SEO 최적화 체크리스트

### 공통 적용사항

- [ ] **제목**: 도시명 + 여행 기간 + "완벽 가이드" 포함
- [ ] **메타설명**: 150자 이내로 요약
- [ ] **키워드**: 도시명, 국가명, 여행, 맛집, 호텔
- [ ] **이미지 ALT 텍스트**: 설명적인 텍스트 추가
- [ ] **내부 링크**: 관련 여행 가이드 연결

### 플랫폼별 추가사항

**티스토리**
- [ ] 카테고리 설정 (여행 > 해외여행)
- [ ] 태그 5~10개 추가
- [ ] 공개 범위: 전체공개
- [ ] 댓글 허용: ✓

**네이버 블로그**
- [ ] 주제 선택: 여행 > 해외여행
- [ ] 키워드 3개 등록
- [ ] 공개 설정: 전체공개
- [ ] 이웃공개 설정 (선택)

---

## 6️⃣ 업로드 후 확인사항

### 크로스 브라우징 테스트

1. **PC 브라우저**
   - Chrome, Safari, Edge에서 확인
   
2. **모바일**
   - 스마트폰에서 실제 접속
   - 반응형 디자인 확인

3. **이미지 로딩**
   - 모든 이미지 정상 표시 확인
   - 로딩 속도 체크

### 링크 점검

```
✅ 확인해야 할 링크
- 구글맵 링크 (호텔, 식당, 관광지)
- 예약 사이트 링크
- 공식 홈페이지 링크
- 대사관 웹사이트 링크
```

---

## 7️⃣ 문제 해결

### 자주 발생하는 문제

**Q: 이미지가 깨져서 보입니다**
A: 
- 외부 URL 대신 직접 업로드
- 이미지 크기 800px 이하로 조정
- JPG 포맷 사용

**Q: 표가 깨집니다**
A:
- Markdown 표 → HTML 테이블로 변환
- 또는 이미지로 캡처 후 삽입

**Q: 링크가 작동하지 않습니다**
A:
- 전체 URL 사용 (https:// 포함)
- 새 창에서 열기 설정

**Q: 폰트가 다릅니다**
A:
- 플랫폼 기본 폰트 사용
- 사용자 설정 폰트 무시

---

## 📞 지원

문제 발생 시:
1. 이 문서의 "문제 해결" 섹션 확인
2. 프로젝트 GitHub Issues 등록
3. 담당자에게 문의

---

**마지막 업데이트**: 2026-02-18
**버전**: 1.0
**작성자**: Travel Content Generator Team
