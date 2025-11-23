// API 설정 파일
// 백엔드 서버 URL을 여기서 설정합니다
const API_CONFIG = {
    BASE_URL: 'https://sibaljom.onrender.com/api',
    // 로컬 개발 시에는 아래 주석을 해제하고 위를 주석 처리하세요
    // BASE_URL: 'http://localhost:5001/api'
};

// 식사 시간 설정 (알림 시간 계산용)
const MEAL_TIMES = {
    아침: { hour: 8, minute: 0 },
    점심: { hour: 12, minute: 0 },
    저녁: { hour: 18, minute: 0 }
};

