# 약을 먹자 - 설정 가이드

## 🚀 시작하기

### 1. 백엔드 서버 설정

1. **Python 가상환경 생성 및 활성화**
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

2. **필요한 패키지 설치**
```bash
pip install -r requirements.txt
```

3. **OpenAI API 키 설정**
   - OpenAI 웹사이트(https://platform.openai.com/api-keys)에서 API 키 발급
   - 환경변수로 설정:
   
   **Windows (PowerShell):**
   ```powershell
   $env:OPENAI_API_KEY="your-api-key-here"
   ```
   
   **Windows (CMD):**
   ```cmd
   set OPENAI_API_KEY=your-api-key-here
   ```
   
   **Linux/Mac:**
   ```bash
   export OPENAI_API_KEY=your-api-key-here
   ```

4. **백엔드 서버 실행**
```bash
python app.py
```

서버가 `http://localhost:5000`에서 실행됩니다.

### 2. 프론트엔드 설정

1. **config.js 파일 확인**
   - `config.js` 파일에서 API URL이 올바르게 설정되어 있는지 확인
   - 기본값: `http://localhost:5000/api`
   - 프로덕션 환경에서는 실제 서버 URL로 변경

2. **웹 서버 실행**
   - Python의 간단한 HTTP 서버 사용:
   ```bash
   # Python 3
   python -m http.server 8080
   ```
   
   - 또는 다른 웹 서버 사용 (Apache, Nginx 등)
   
   - 브라우저에서 `http://localhost:8080` 접속

### 3. 기능 테스트

#### ✅ 챗봇 기능
1. 메인 화면에서 "챗봇" 버튼 클릭
2. 메시지 입력 후 전송
3. GPT API를 통한 응답 확인

#### ✅ 약봉지 인식
1. 메인 화면에서 "검색" 버튼 클릭
2. 약봉지 사진 촬영
3. 이미지 분석 및 약 정보 추출 확인

#### ✅ 오늘의 약
1. 메인 화면에서 "오늘의 약" 버튼 클릭
2. 아침/점심/저녁 시간대별 약 확인
3. 노인 친화적 설명 및 음성 안내 확인
4. 복용 완료 버튼 클릭하여 기록 저장

#### ✅ 복약 내역
1. 메인 화면에서 "복약 내역" 버튼 클릭
2. 기간 선택 후 "조회" 버튼 클릭
3. 해당 기간의 복용 내역 확인

#### ✅ 이달의 약
1. 메인 화면에서 "이달의 약" 버튼 클릭
2. 달력에서 복용한 날짜에 알약 아이콘 표시 확인
3. 이번 달 복약률 확인

## ⚠️ 주의사항

1. **OpenAI API 키 필요**
   - 챗봇, OCR, 약 설명 변환 기능은 모두 OpenAI API를 사용합니다
   - API 키가 없으면 해당 기능이 작동하지 않습니다
   - API 사용량에 따라 비용이 발생할 수 있습니다

2. **CORS 설정**
   - 백엔드 서버에서 CORS가 활성화되어 있습니다
   - 다른 도메인에서 접근할 경우 추가 설정이 필요할 수 있습니다

3. **데이터 저장**
   - 현재는 메모리와 localStorage를 사용하여 데이터를 저장합니다
   - 실제 운영 환경에서는 데이터베이스(MySQL, PostgreSQL 등)를 사용해야 합니다

4. **알림 기능**
   - 브라우저 알림 권한이 필요합니다
   - 모바일 앱으로 변환할 경우 푸시 알림을 사용해야 합니다

## 🔧 문제 해결

### 백엔드 서버가 시작되지 않을 때
- Python 버전 확인 (Python 3.7 이상 필요)
- 필요한 패키지가 모두 설치되었는지 확인
- 포트 5000이 이미 사용 중인지 확인

### API 호출 오류
- 백엔드 서버가 실행 중인지 확인
- `config.js`의 API URL이 올바른지 확인
- 브라우저 콘솔에서 오류 메시지 확인

### OpenAI API 오류
- API 키가 올바르게 설정되었는지 확인
- API 사용량 한도 확인
- 네트워크 연결 확인

