# 백엔드 서버

## 설치 방법

1. Python 가상환경 생성 및 활성화:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

2. 필요한 패키지 설치:
```bash
pip install -r requirements.txt
```

3. OpenAI API 키 설정:
```bash
# Windows
set OPENAI_API_KEY=your-api-key-here

# Linux/Mac
export OPENAI_API_KEY=your-api-key-here
```

## 서버 실행

```bash
python app.py
```

서버는 `http://localhost:5000`에서 실행됩니다.

## API 엔드포인트

### 1. 챗봇 (`POST /api/chat`)
- GPT API를 사용한 챗봇 응답
- 필요: OPENAI_API_KEY

### 2. 약봉지 OCR (`POST /api/ocr`)
- 약봉지 이미지 분석 및 정보 추출
- 필요: OPENAI_API_KEY (Vision API)

### 3. 약 목록 조회 (`GET /api/medications`)
- 등록된 모든 약 목록

### 4. 약 설명 변환 (`POST /api/medications/convert`)
- 약 정보를 노인 친화적 설명으로 변환
- 필요: OPENAI_API_KEY

### 5. 오늘의 약 (`GET /api/medications/today`)
- 오늘 복용해야 할 약 목록

### 6. 복용 완료 기록 (`POST /api/medications/complete`)
- 약 복용 완료 기록 저장

### 7. 복용 내역 조회 (`GET /api/history`)
- 기간별 복용 내역

### 8. 이달의 복용 내역 (`GET /api/history/month`)
- 월별 복용 내역

