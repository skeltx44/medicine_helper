// API 설정 파일
// 백엔드 서버 URL을 여기서 설정합니다
const API_CONFIG = {
    BASE_URL: 'http://localhost:5001/api',
    // 프로덕션 환경에서는 실제 서버 URL로 변경
    // BASE_URL: 'https://your-server.com/api'
};

// 식사 시간 설정 (알림 시간 계산용)
const MEAL_TIMES = {
    아침: { hour: 8, minute: 0 },
    점심: { hour: 12, minute: 0 },
    저녁: { hour: 18, minute: 0 }
};

