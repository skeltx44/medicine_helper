# 💊 약을 먹자

AI 기반 고령층 복약 도우미 서비스

## 📋 프로젝트 개요

시중에 나와 있는 많은 건강관리 앱들은 젊은 층 기준의 UI/UX여서 노인들이 직접 사용하기에는 진입장벽이 높습니다. 따라서 노인분들의 약물 오용 위험 감축을 위한 단순성 및 가독성, 정보 접근성, 알림 서비스 등 노인들에게 필요한 모든 기능을 종합한 서비스를 기획하였습니다.

## 🚩 주요 기능

### 1. 약 봉투 인식
- 약봉지 사진 촬영 시 AI OCR 기술로 약 정보 자동 추출
- 약 이름, 복용 횟수, 복용 기간, 식전/식후 판단
- 식전 약은 식사 시간 30분 전, 식후 약은 식사 시간 30분 후 알림 설정

### 2. 챗봇 안내
- GPT API를 활용한 지능형 챗봇
- 고령층 친화적인 간단한 대화 UI
- 약 복용, 복약 내역, 약 검색 등 질문에 답변

### 3. 오늘의 약
- 약 정보를 노인 친화적 언어로 변환
- 예: "타이레놀 1정" → "작은 하얀색 동그란 약 1알"
- 색상, 모양, 크기를 이용한 직관적 설명
- 음성 안내 기능 제공
- 아침/점심/저녁 시간대별 복용 안내

### 4. 복약 내역
- 기간별 복용 내역 조회
- 년/월/일 단위로 복용 기록 확인

### 5. 이달의 약
- 달력 형태로 복약 이행 현황 시각화
- 복용한 날은 알약 아이콘 표시
- 이번 달 전체 복약률 퍼센트 표시

## 🛠️ 기술 스택

### Frontend
- HTML, CSS, JavaScript
- Web Speech API (음성 안내)
- Web Notification API (알림)

### Backend
- Python Flask
- OpenAI API (GPT-4, GPT Vision)
- Flask-CORS

## 📁 프로젝트 구조

```
final/
├── backend/
│   ├── app.py              # Flask 백엔드 서버
│   ├── requirements.txt    # Python 패키지 목록
│   └── README.md           # 백엔드 설정 가이드
├── pages/                  # HTML 파일들
│   ├── index.html
│   ├── main.html
│   ├── capture.html
│   ├── chatbot.html
│   ├── today_med.html
│   ├── medlist.html
│   └── thismonth.html
├── css/                    # CSS 파일들
├── js/                     # JavaScript 파일들
│   ├── chatbot.js
│   └── notification.js
├── config.js              # API 설정 파일
├── SETUP.md               # 설정 가이드
└── README.md              # 이 파일
```

## 🚀 시작하기

> **⚠️ 중요:** 백엔드는 Render에 배포되어 있습니다 (`https://sibaljom.onrender.com`)
> 프론트엔드는 로컬에서 실행하지만, API는 Render 서버를 호출합니다.

### 프론트엔드 실행

```bash
# Python HTTP 서버 사용
python -m http.server 8080

# 브라우저에서 http://localhost:8080 접속
```

### 로컬 백엔드 개발 (선택사항)

로컬에서 백엔드를 개발하고 싶다면:

자세한 설정 방법은 `SETUP.md` 파일을 참고하세요.

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# .env 파일 생성 (OPENAI_API_KEY 설정)
# backend/.env 파일에 다음 내용 추가:
# OPENAI_API_KEY=your-api-key-here

python app.py
```

로컬 백엔드를 사용하려면 `config.js`에서 API URL을 변경하세요:
```javascript
BASE_URL: 'http://localhost:5001/api'
```

## ⚙️ API 엔드포인트

### 챗봇
- `POST /api/chat` - GPT API를 사용한 챗봇 응답

### 약봉지 인식
- `POST /api/ocr` - 약봉지 이미지 OCR 처리 및 약 정보 추출

### 약 관리
- `GET /api/medications` - 등록된 약 목록 조회
- `POST /api/medications` - 약 정보 저장
- `GET /api/medications/today` - 오늘 복용해야 할 약 목록
- `POST /api/medications/complete` - 약 복용 완료 기록
- `POST /api/medications/convert` - 약 정보를 노인 친화적 설명으로 변환

### 복용 내역
- `GET /api/history` - 기간별 복용 내역 조회
- `GET /api/history/month` - 월별 복용 내역 조회

## ⚠️ 주의사항

1. **OpenAI API 키 필요**
   - 챗봇, OCR, 약 설명 변환 기능은 모두 OpenAI API를 사용합니다
   - API 키가 없으면 해당 기능이 작동하지 않습니다
   - API 사용량에 따라 비용이 발생할 수 있습니다

2. **데이터 저장**
   - 현재는 메모리와 localStorage를 사용하여 데이터를 저장합니다
   - 실제 운영 환경에서는 데이터베이스를 사용해야 합니다

3. **알림 기능**
   - 브라우저 알림 권한이 필요합니다
   - 모바일 앱으로 변환할 경우 푸시 알림을 사용해야 합니다

## 👥 팀

- 남상혁: 팀 리더 & 백엔드 개발
- 신지원: 프론트엔드 개발
- 우효정: 프론트엔드 개발
- 황선인: 웹 투 앱 개발

## 📝 라이선스

이 프로젝트는 해커톤 프로젝트입니다.

