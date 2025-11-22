from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import base64
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
from openai import OpenAI

# .env 파일에서 환경변수 로드 (로컬 개발용)
# Render 등 클라우드 배포 시에는 환경변수를 직접 설정하면 됩니다
load_dotenv()

app = Flask(__name__)
CORS(app)  # CORS 허용

# 디버깅: 앱이 제대로 생성되었는지 확인
print(f"[DEBUG] Flask 앱 생성됨: {app.name}")
print(f"[DEBUG] Flask 앱 파일 위치: {__file__}")

# OpenAI API 키 설정
# 환경변수 OPENAI_API_KEY에서 가져옵니다
# 
# 로컬 개발 시:
#   1. backend 폴더에 .env 파일 생성
#   2. .env 파일에 다음 내용 추가: OPENAI_API_KEY=your-api-key-here
#
# Render 배포 시:
#   1. Render 대시보드에서 프로젝트 선택
#   2. Settings > Environment Variables 메뉴로 이동
#   3. Key: OPENAI_API_KEY, Value: your-api-key-here 추가
#   4. Save Changes 후 서비스 재배포
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    print("[경고] OPENAI_API_KEY 환경변수가 설정되지 않았습니다!")
    print("[경고] 챗봇, OCR, 약 설명 변환 기능이 작동하지 않습니다.")
    print("[경고] .env 파일을 생성하거나 환경변수를 설정해주세요.")
    client = None
else:
    client = OpenAI(api_key=OPENAI_API_KEY)
    print("[INFO] OpenAI API 키가 설정되었습니다.")

# 약 데이터 저장소 (실제로는 데이터베이스를 사용해야 함)
medications_db = []
medication_history_db = []

# 사용자 데이터 저장소
users_db = []

# 이미지 저장 디렉토리
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


@app.route('/api/chat', methods=['POST'])
def chat():
    """
    GPT API를 사용한 챗봇 응답
    """
    if not client:
        return jsonify({'error': 'OpenAI API 키가 설정되지 않았습니다. 환경변수 OPENAI_API_KEY를 설정해주세요.'}), 500
    
    try:
        data = request.json
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'error': '메시지가 필요합니다.'}), 400
        
        # GPT API 호출
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # 또는 "gpt-3.5-turbo"
            messages=[
                {
                    "role": "system",
                    "content": "당신은 고령층을 위한 약 복용 도우미 챗봇입니다. 친절하고 간단한 언어로 답변해주세요. 약 복용, 복약 내역, 약 검색 등에 대해 도움을 드립니다. 마크다운 문법(** 등)을 사용하지 말고 순수 텍스트만 반환하세요."
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        bot_response = response.choices[0].message.content
        # 마크다운 문법 제거 및 줄바꿈 정리
        import re
        bot_response = bot_response.replace('**', '').replace('*', '').replace('_', '')
        bot_response = re.sub(r'\n{3,}', '\n\n', bot_response)  # 3개 이상 줄바꿈을 2개로
        
        return jsonify({
            'response': bot_response
        })
        
    except Exception as e:
        print(f"챗봇 오류: {str(e)}")
        return jsonify({'error': f'챗봇 응답 생성 중 오류가 발생했습니다: {str(e)}'}), 500


@app.route('/api/ocr', methods=['POST'])
def ocr():
    """
    약봉지 이미지 OCR 처리 및 약 정보 추출
    Vision API 사용
    """
    if not client:
        return jsonify({'error': 'OpenAI API 키가 설정되지 않았습니다. 환경변수 OPENAI_API_KEY를 설정해주세요.'}), 500
    
    try:
        data = request.json
        image_base64 = data.get('image', '')
        
        if not image_base64:
            return jsonify({'error': '이미지가 필요합니다.'}), 400
        
        # base64 데이터에서 헤더 제거 (data:image/jpeg;base64, 부분)
        if ',' in image_base64:
            image_base64 = image_base64.split(',')[1]
        
        # GPT Vision API를 사용하여 약봉지 정보 추출
        response = client.chat.completions.create(
            model="gpt-4o",  # Vision 지원 모델
            messages=[
                {
                    "role": "system",
                    "content": """당신은 약봉지 이미지를 분석하는 전문가입니다. 
                    이미지에서 다음 정보를 JSON 형식으로 추출해주세요:
                    {
                        "name": "약 이름",
                        "dosage": "1일 복용 횟수 (숫자만)",
                        "days": "총 복용 일수 (숫자만)",
                        "before_meal": true/false (식전이면 true, 식후면 false),
                        "times": ["아침", "점심", "저녁"] (복용 시간대)
                    }
                    식전/식후 판단: "식전", "식사 전", "before meal" 등이 보이면 before_meal: true
                    식후는 "식후", "식사 후", "after meal" 등이 보이면 before_meal: false
                    """
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "이 약봉지 이미지를 분석하여 약 정보를 추출해주세요."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=500
        )
        
        # 응답 파싱
        response_text = response.choices[0].message.content
        
        # JSON 추출 (코드 블록이 있을 수 있음)
        import re
        json_match = re.search(r'\{[^{}]*\}', response_text, re.DOTALL)
        if json_match:
            medication_info = json.loads(json_match.group())
        else:
            # JSON이 없으면 기본값 사용
            medication_info = {
                "name": "",
                "dosage": 1,
                "days": 7,
                "before_meal": False,
                "times": ["아침"]
            }
        
        # 약 이름에서 용량 정보 제거
        if medication_info.get("name"):
            medication_info["name"] = re.sub(r'\s+\d+[mg|ml|정|알|MG|ML].*$', '', medication_info["name"], flags=re.IGNORECASE).strip()
        
        # 약 이름이 비어있거나 너무 짧으면 저장하지 않음
        if not medication_info.get("name") or len(medication_info.get("name", "")) < 2:
            return jsonify({
                'success': False,
                'error': '약 정보를 추출할 수 없습니다. 다시 시도해주세요.'
            }), 400
        
        # 식사 시간 정의 (기본값)
        meal_times = {
            "아침": {"hour": 8, "minute": 0},
            "점심": {"hour": 12, "minute": 0},
            "저녁": {"hour": 18, "minute": 0}
        }
        
        # 알림 시간 계산 (식전 30분 전, 식후 30분 후)
        notification_times = {}
        for time in medication_info.get("times", ["아침"]):
            meal_time = meal_times.get(time, meal_times["아침"])
            if medication_info.get("before_meal", False):
                # 식전: 식사 시간 30분 전
                notification_time = datetime.now().replace(
                    hour=meal_time["hour"],
                    minute=meal_time["minute"]
                ) - timedelta(minutes=30)
            else:
                # 식후: 식사 시간 30분 후
                notification_time = datetime.now().replace(
                    hour=meal_time["hour"],
                    minute=meal_time["minute"]
                ) + timedelta(minutes=30)
            
            notification_times[time] = {
                "hour": notification_time.hour,
                "minute": notification_time.minute
            }
        
        # 약 이름이 비어있으면 저장하지 않음
        if not medication_info.get("name") or len(medication_info.get("name", "")) < 2:
            return jsonify({
                'success': False,
                'error': '약 이름을 추출할 수 없습니다. 다시 시도해주세요.'
            }), 400
        
        # 약 정보 저장
        medication_id = len(medications_db) + 1
        medication_data = {
            "id": medication_id,
            "name": medication_info.get("name", ""),
            "dosage": medication_info.get("dosage", 1),
            "days": medication_info.get("days", 7),
            "before_meal": medication_info.get("before_meal", False),
            "times": medication_info.get("times", ["아침"]),
            "notification_times": notification_times,  # 알림 시간 추가
            "registered_date": datetime.now().isoformat(),
            "image_base64": image_base64  # 나중에 필요할 수 있으므로 저장
        }
        
        medications_db.append(medication_data)
        
        return jsonify({
            'success': True,
            'medication': medication_data
        })
        
    except Exception as e:
        print(f"OCR 오류: {str(e)}")
        return jsonify({'error': f'이미지 분석 중 오류가 발생했습니다: {str(e)}'}), 500


@app.route('/api/medications', methods=['GET'])
def get_medications():
    """등록된 약 목록 조회"""
    return jsonify({
        'medications': medications_db
    })


@app.route('/api/medications', methods=['POST'])
def create_medication():
    """약 정보 저장 (프론트엔드에서 동기화용)"""
    try:
        data = request.json
        medication_id = len(medications_db) + 1
        
        medication_data = {
            "id": medication_id,
            "name": data.get("name", "알 수 없음"),
            "dosage": data.get("dosage", 1),
            "days": data.get("days", 7),
            "before_meal": data.get("before_meal", False),
            "times": data.get("times", ["아침"]),
            "notification_times": data.get("notification_times", {}),
            "registered_date": data.get("registered_date", datetime.now().isoformat()),
            "image_base64": data.get("image_base64", "")
        }
        
        medications_db.append(medication_data)
        
        return jsonify({
            'success': True,
            'medication': medication_data
        })
    except Exception as e:
        return jsonify({'error': f'약 정보 저장 중 오류가 발생했습니다: {str(e)}'}), 500


@app.route('/api/medications/<int:medication_id>', methods=['GET'])
def get_medication(medication_id):
    """특정 약 정보 조회"""
    medication = next((m for m in medications_db if m['id'] == medication_id), None)
    if not medication:
        return jsonify({'error': '약을 찾을 수 없습니다.'}), 404
    return jsonify(medication)


@app.route('/api/medications/convert', methods=['POST'])
def convert_medication_description():
    """
    약 정보를 노인 친화적인 설명으로 변환 (간단하게, 여러 약 지원)
    """
    if not client:
        return jsonify({'error': 'OpenAI API 키가 설정되지 않았습니다. 환경변수 OPENAI_API_KEY를 설정해주세요.'}), 500
    
    try:
        data = request.json
        medication_names = data.get('names', [])  # 여러 약 이름 리스트
        time_of_day = data.get('time', '아침')  # 아침, 점심, 저녁
        
        if not medication_names or len(medication_names) == 0:
            return jsonify({'error': '약 이름이 필요합니다.'}), 400
        
        # 여러 약 이름을 하나의 문자열로
        names_str = ', '.join(medication_names)
        
        # GPT API를 사용하여 노인 친화적인 설명 생성 (간단하게)
        prompt = f"""약 이름들: {names_str}

이 약들을 고령층이 이해하기 쉬운 언어로 매우 간단하게 설명해주세요.
약의 색상, 크기, 형태만 설명하세요.

약이 여러 개면 각 약을 한 줄씩 나열:
작고 둥근 노란색 약 1알
크고 캡슐 안에 들어있는 빨간색 약 1알
을 물과 함께 드세요

규칙:
- 약의 색상, 모양, 크기만 간단히 설명
- 약 이름이나 용량은 언급하지 마세요
- "지금은 아침 약 시간입니다" 같은 불필요한 설명 제거
- 형식: "[크기] [형태] [색상] 약 1알"
- 여러 약이면 각 약을 한 줄씩 나열하고, 마지막에만 "을 물과 함께 드세요" 추가
- 각 약 설명 사이에는 줄바꿈 사용
- 마크다운 문법(** 등) 절대 사용하지 말고 순수 텍스트만
"""
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "당신은 고령층을 위한 약 설명 전문가입니다. 약을 색상, 모양, 크기로 매우 간단하고 짧게 설명해주세요. 약 이름이나 용량은 언급하지 마세요. 마크다운 문법을 절대 사용하지 마세요."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=150
        )
        
        description = response.choices[0].message.content
        # 마크다운 문법 제거 및 정리
        import re
        description = description.replace('**', '').replace('*', '').replace('_', '')
        # 용량 정보 제거
        description = re.sub(r'\s*\d+\s*(mg|ml|정|알|MG|ML)\s*', '', description, flags=re.IGNORECASE)
        # 여러 공백을 하나로, 줄바꿈은 유지
        description = re.sub(r'[ \t]+', ' ', description)
        description = re.sub(r'\n{3,}', '\n\n', description)  # 3개 이상 줄바꿈을 2개로
        description = description.strip()
        
        return jsonify({
            'description': description,
            'time': time_of_day
        })
        
    except Exception as e:
        print(f"약 설명 변환 오류: {str(e)}")
        return jsonify({'error': f'약 설명 변환 중 오류가 발생했습니다: {str(e)}'}), 500


@app.route('/api/medications/today', methods=['GET'])
def get_today_medications():
    """오늘 복용해야 할 약 목록 조회"""
    today = datetime.now().date()
    today_medications = []
    
    for med in medications_db:
        registered_date = datetime.fromisoformat(med['registered_date']).date()
        days_diff = (today - registered_date).days
        
        # 등록일로부터 복용 기간 내에 있는지 확인
        if 0 <= days_diff < med['days']:
            # 오늘 복용해야 하는 시간대 확인
            for time in med['times']:
                today_medications.append({
                    'id': med['id'],
                    'name': med['name'],
                    'time': time,
                    'before_meal': med['before_meal'],
                    'description': med.get('description', '')
                })
    
    return jsonify({
        'medications': today_medications,
        'date': today.isoformat()
    })


@app.route('/api/medications/complete', methods=['POST'])
def complete_medication():
    """약 복용 완료 기록"""
    try:
        data = request.json
        medication_id = data.get('medication_id')
        time = data.get('time', '아침')  # 아침, 점심, 저녁
        
        if not medication_id:
            return jsonify({'error': '약 ID가 필요합니다.'}), 400
        
        # 복용 기록 저장
        record = {
            'medication_id': medication_id,
            'time': time,
            'completed_at': datetime.now().isoformat(),
            'date': datetime.now().date().isoformat()
        }
        
        medication_history_db.append(record)
        
        return jsonify({
            'success': True,
            'record': record
        })
        
    except Exception as e:
        print(f"복용 기록 오류: {str(e)}")
        return jsonify({'error': f'복용 기록 저장 중 오류가 발생했습니다: {str(e)}'}), 500


@app.route('/api/history', methods=['GET'])
def get_history():
    """복용 내역 조회"""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    filtered_history = medication_history_db
    
    if start_date and end_date:
        filtered_history = [
            h for h in medication_history_db
            if start_date <= h['date'] <= end_date
        ]
    
    return jsonify({
        'history': filtered_history
    })


@app.route('/api/history/month', methods=['GET'])
def get_month_history():
    """이달의 복용 내역 조회"""
    year = request.args.get('year', datetime.now().year)
    month = request.args.get('month', datetime.now().month)
    
    # 해당 월의 모든 기록 필터링
    month_history = [
        h for h in medication_history_db
        if datetime.fromisoformat(h['date']).year == int(year) and
           datetime.fromisoformat(h['date']).month == int(month)
    ]
    
    # 날짜별로 그룹화
    daily_history = {}
    for record in month_history:
        date = record['date']
        if date not in daily_history:
            daily_history[date] = []
        daily_history[date].append(record)
    
    return jsonify({
        'history': daily_history,
        'year': year,
        'month': month
    })


@app.route('/api/users', methods=['GET'])
def get_users():
    """등록된 사용자 목록 조회"""
    return jsonify({
        'users': users_db,
        'count': len(users_db)
    })


@app.route('/api/users', methods=['POST'])
def create_user():
    """사용자 정보 저장 (로그인/회원가입 시)"""
    try:
        data = request.json
        user_id = len(users_db) + 1
        
        user_data = {
            "id": user_id,
            "name": data.get("name", ""),
            "phone": data.get("phone", ""),
            "guardian_phone": data.get("guardian_phone", ""),
            "created_at": datetime.now().isoformat(),
            "type": data.get("type", "login")  # "login" or "signup"
        }
        
        users_db.append(user_data)
        
        return jsonify({
            'success': True,
            'user': user_data
        })
    except Exception as e:
        return jsonify({'error': f'사용자 정보 저장 중 오류가 발생했습니다: {str(e)}'}), 500


@app.route('/api/health', methods=['GET'])
@app.route('/api/health/', methods=['GET'])
def health_check():
    """서버 상태 확인"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/', methods=['GET'])
def root():
    """루트 경로"""
    # 등록된 모든 라우트 확인
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            'endpoint': rule.endpoint,
            'methods': list(rule.methods),
            'path': str(rule)
        })
    
    return jsonify({
        'message': '약을 먹자 API 서버',
        'status': 'running',
        'routes': routes,
        'endpoints': {
            'health': '/api/health',
            'chat': '/api/chat',
            'ocr': '/api/ocr',
            'medications': '/api/medications'
        }
    })


# 모든 경로에 대한 catch-all 핸들러 (디버깅용)
@app.errorhandler(404)
def not_found(error):
    """404 오류 처리 - 등록된 라우트 정보 반환"""
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            'endpoint': rule.endpoint,
            'methods': list(rule.methods),
            'path': str(rule)
        })
    
    return jsonify({
        'error': 'Not Found',
        'message': '요청한 URL을 찾을 수 없습니다.',
        'requested_path': request.path,
        'available_routes': routes
    }), 404


if __name__ == '__main__':
    print("백엔드 서버 시작...")
    print("주의: OPENAI_API_KEY 환경변수를 설정해주세요!")
    
    # 등록된 모든 라우트 출력
    print("\n등록된 라우트:")
    for rule in app.url_map.iter_rules():
        print(f"  {rule.rule} [{', '.join(rule.methods)}]")
    print()
    
    app.run(debug=True, host='0.0.0.0', port=5001, use_reloader=False)

