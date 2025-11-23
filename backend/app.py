from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import base64
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
from openai import OpenAI
import re

# .env 파일에서 환경변수 로드 (로컬 개발용)
# Render 등 클라우드 배포 시에는 환경변수를 직접 설정하면 됩니다
load_dotenv()

app = Flask(__name__)
CORS(app)  # CORS 허용

# 디버깅: 앱이 제대로 생성되었는지 확인
print(f"[DEBUG] Flask 앱 생성됨: {app.name}")
print(f"[DEBUG] Flask 앱 파일 위치: {__file__}")

# OpenAI API 키 설정
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


def safe_int(value, default):
    """
    문자열 "1일 3회", "3회", "7일분" 등에서 숫자만 뽑아서 int로 변환.
    실패하면 default 반환.
    """
    try:
        if isinstance(value, bool):
            return default
        if isinstance(value, int):
            return value
        if isinstance(value, float):
            if value.is_integer():
                return int(value)
            return int(round(value))
        if isinstance(value, str):
            m = re.search(r'\d+', value)
            if m:
                return int(m.group())
        return default
    except Exception:
        return default


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
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "당신은 고령층을 위한 약 복용 도우미 챗봇입니다. "
                        "친절하고 간단한 언어로 짧게 답변해주세요. "
                        "약 복용, 복약 내역, 약 검색 등에 대해 도움을 드립니다. "
                        "증상 진단이나 병명 추정은 절대 하지 말고, "
                        "필요 시에는 의사·약사 상담을 권유하세요. "
                        "마크다운 문법(**, *, _, - 등)을 사용하지 말고 순수 텍스트만 반환하세요."
                    )
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
        bot_response = bot_response.replace('**', '').replace('*', '').replace('_', '')
        bot_response = re.sub(r'\n{3,}', '\n\n', bot_response)
        
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
    - 여러 약이 있으면 medications 배열로 여러 개 등록
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
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "당신은 한국 약봉투 이미지를 분석하는 전문가입니다.\n"
                        "이미지에서 다음 정보를 JSON 형식으로 매우 신중하게, 정확하게 추출해주세요.\n"
                        "반드시 아래 스키마와 키 이름을 그대로 사용하고, "
                        "JSON 외의 다른 설명 텍스트는 절대 출력하지 마세요.\n\n"
                        "{\n"
                        "  \"name\": \"약 이름 문자열\",\n"
                        "  \"dosage\": 1일 복용 횟수(정수, 예: 3),\n"
                        "  \"days\": 총 복용 일수(정수, 예: 7),\n"
                        "  \"before_meal\": true 또는 false,\n"
                        "  \"times\": [\"아침\", \"점심\", \"저녁\"] 중 일부를 요소로 갖는 배열,\n"
                        "  \"medications\": [\n"
                        "    {\n"
                        "      \"name\": \"약 이름 문자열\",\n"
                        "      \"dosage\": 1일 복용 횟수(정수),\n"
                        "      \"days\": 총 복용 일수(정수),\n"
                        "      \"before_meal\": true 또는 false,\n"
                        "      \"times\": [\"아침\", \"점심\", \"저녁\"] 중 일부\n"
                        "    }\n"
                        "  ]\n"
                        "}\n\n"
                        "위 스키마의 name, dosage, days, before_meal, times 키는 "
                        "최상위에 한 번씩 포함하고, 여러 약이 있을 경우 medications 배열에도 각 약 정보를 넣어주세요.\n\n"
                        "중요: 약봉투에 다음과 같이 적힌 경우 숫자를 정확히 해석해야 합니다.\n"
                        "- \"1일 1회\", \"하루 1번\" 등은 모두 dosage: 1 로 설정합니다.\n"
                        "- \"1일 2회\" 는 dosage: 2 로 설정합니다.\n"
                        "- \"1일 3회\" 는 dosage: 3 으로 설정합니다.\n"
                        "days도 \"3일분\", \"7일분\" 처럼 적힌 경우 안의 숫자만 사용해 정수로 설정합니다.\n\n"
                        "추가 규칙:\n"
                        "- 약봉투에 서로 다른 약이 여러 개 적혀 있다면, 각 약을 medications 배열의 별도 원소로 넣으세요.\n"
                        "- 정보가 애매하거나 잘 안 보이면 절대 추측하지 말고 해당 필드는 null로 두세요.\n"
                        "  - 예시: 복용 횟수가 잘 보이지 않으면 dosage는 null로 두세요.\n"
                        "  - 예시: 복용 일수가 안 보이면 days는 null로 두세요.\n"
                        "- \"dosage\"와 \"days\"는 반드시 정수(또는 정수로 해석 가능한 값)로 추출하세요. "
                        "\"3회\", \"3일분\"처럼 적혀 있어도 숫자 3만 남기세요.\n"
                        "- 약 이름이 명확히 안 보이면 name은 null로 두세요.\n"
                        "- 아무 약도 확실하게 읽을 수 없다면 medications는 빈 배열 []로 두세요.\n\n"
                        "주의:\n"
                        "- 정보를 추측해서 채우지 마세요. 불확실하면 해당 필드는 null로 두세요.\n"
                        "- 위 스키마의 최상위 필드(name, dosage, days, before_meal, times)는 "
                        "medications 배열과 별개로 반드시 포함해야 합니다.\n"
                        "- before_meal 값은 특별한 경우가 아니라면 false로 설정해도 됩니다.\n"
                        "- times 값은 null, 빈 배열, 또는 [\"아침\"], [\"점심\"], [\"저녁\"] 등으로 적어도 됩니다. "
                        "서버에서 dosage 값을 기준으로 실제 복용 시간대를 계산합니다.\n"
                        "- JSON 바깥에 다른 문장이나 설명을 절대 쓰지 말고, 오직 하나의 JSON 객체만 출력하세요.\n"
                        "- 답변을 출력하기 전에, 숫자(dosage, days)가 약봉투 내용과 일치하는지 한 번 더 천천히 검토한 뒤에 최종 JSON을 반환하세요."
                    )
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "이 약봉지 이미지를 분석하여 약 정보를 추출해 주세요. JSON만 반환하세요."
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
            temperature=0.1,
            max_tokens=700
        )
        
        # 응답 파싱
        response_text = response.choices[0].message.content.strip()

        # 코드블록 제거 시도
        cleaned = response_text
        if cleaned.startswith("```"):
            cleaned = re.sub(r'^```(?:json)?', '', cleaned, flags=re.IGNORECASE).strip()
            cleaned = re.sub(r'```$', '', cleaned).strip()

        medication_info = {}
        try:
            medication_info = json.loads(cleaned)
        except Exception:
            # 실패하면 예전 방식으로 백업: 첫 번째 {} 블록만 파싱
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                try:
                    medication_info = json.loads(json_match.group())
                except Exception:
                    medication_info = {}
            else:
                medication_info = {}

        # medications 배열이 있으면 그걸 사용, 없으면 단일 객체로 처리
        medications_raw = []
        if isinstance(medication_info, dict) and isinstance(medication_info.get("medications"), list) and len(medication_info["medications"]) > 0:
            medications_raw = medication_info["medications"]
        elif isinstance(medication_info, dict) and medication_info:
            medications_raw = [medication_info]
        else:
            medications_raw = []

        saved_meds = []

        for raw_med in medications_raw:
            if not isinstance(raw_med, dict):
                continue

            # 약 이름에서 용량 정보 제거
            name = raw_med.get("name", "")
            if name:
                name = re.sub(
                    r'\s+\d+[mg|ml|정|알|MG|ML].*$',
                    '',
                    name,
                    flags=re.IGNORECASE
                ).strip()

            # 이름이 비어있거나 너무 짧으면 스킵
            if not name or len(name) < 2:
                continue

            # dosage와 days를 안전하게 정수로 변환
            raw_dosage = raw_med.get("dosage", medication_info.get("dosage", 1))
            dosage_value = safe_int(raw_dosage, 1)

            raw_days = raw_med.get("days", medication_info.get("days", 7))
            days_value = safe_int(raw_days, 7)

            # 1일 복용 횟수(dosage)에 따라 복용 시간대(times) 자동 설정
            if dosage_value >= 3:
                times_list = ["아침", "점심", "저녁"]
            elif dosage_value == 2:
                times_list = ["아침", "저녁"]
            else:  # 1회 또는 그 외
                times_list = ["저녁"]

            # 식후로 통일
            before_meal = False

            # 식사 시간 정의 (기본값)
            meal_times = {
                "아침": {"hour": 8, "minute": 0},
                "점심": {"hour": 12, "minute": 0},
                "저녁": {"hour": 18, "minute": 0}
            }

            # 알림 시간 계산 (식후 30분 후로 통일)
            notification_times = {}
            now = datetime.now()
            for time_label in times_list:
                meal_time = meal_times.get(time_label, meal_times["저녁"])
                notification_time = now.replace(
                    hour=meal_time["hour"],
                    minute=meal_time["minute"],
                    second=0,
                    microsecond=0
                ) + timedelta(minutes=30)
                
                notification_times[time_label] = {
                    "hour": notification_time.hour,
                    "minute": notification_time.minute
                }

            # 약 정보 저장
            medication_id = len(medications_db) + 1
            medication_data = {
                "id": medication_id,
                "name": name,
                "dosage": dosage_value,
                "days": days_value,
                "before_meal": before_meal,
                "times": times_list,
                "notification_times": notification_times,
                "registered_date": datetime.now().isoformat(),
                "image_base64": image_base64
            }

            medications_db.append(medication_data)
            saved_meds.append(medication_data)

        # 아무 약도 저장 못 했으면 에러
        if not saved_meds:
            return jsonify({
                'success': False,
                'error': '약 정보를 추출할 수 없습니다. 다시 시도해주세요.'
            }), 400

        # 기존 호환성: 첫 번째 약은 medication 키로도 내려줌
        return jsonify({
            'success': True,
            'medication': saved_meds[0],
            'medications': saved_meds
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
        medication_names = data.get('names', [])
        time_of_day = data.get('time', '아침')
        
        if not medication_names or len(medication_names) == 0:
            return jsonify({'error': '약 이름이 필요합니다.'}), 400
        
        names_str = ', '.join(medication_names)
        num_meds = len(medication_names)
        
        prompt = f"""
약 이름들: {names_str}
약은 총 {num_meds}개입니다.

각 약을 고령층이 이해하기 쉬운 언어로 아주 간단하게 설명해 주세요.

설명 규칙:
- 약의 색상, 모양, 크기만 설명합니다.
- 약 이름, 회사 이름, 효능, 복용 시간, 복용 횟수, 용량(mg, ml 등)은 절대 언급하지 않습니다.
- 실제 색/모양 정보를 알 수 없으면, 일반적인 알약/캡슐의 모양과 색을 상상해서 사용해도 됩니다.
- 서로 다른 약은 색이나 형태를 조금씩 다르게 해서 구분되도록 해 주세요.
- "약 정보 없음", "정보 부족", "알 수 없음"과 같은 표현은 절대 사용하지 마세요.

형식 규칙(매우 중요):
- 출력은 여러 줄 텍스트입니다.
- 한 줄에는 한 가지 약만 설명합니다.
- 출력 줄 수는 최대 {num_meds}줄입니다. {num_meds}줄보다 적게 써도 괜찮지만, {num_meds}줄보다 많이 쓰면 안 됩니다.
- 설명하기 어려운 약이 있으면 그 약은 그냥 생략하고, 그 대신 "정보 없음" 같은 문장은 쓰지 마세요.
- 줄과 줄 사이는 줄바꿈(\\n)으로만 구분합니다.
- 한 설명 안에는 줄바꿈을 넣지 말고, 한 줄로만 작성하세요.
- 마크다운 문법(**, *, _, -, 번호 매기기 등)은 절대 사용하지 마세요.

예시 (약이 3개일 때):
작은 하얀색 둥근 약 1알
조금 큰 노란색 타원형 약 1알
길쭉한 파란색 캡슐 1알
"""
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "당신은 고령층을 위한 약 설명 전문가입니다. "
                        "약을 색상, 모양, 크기로만 매우 간단하고 짧게 설명해야 합니다. "
                        "약 이름, 회사명, 효능, 복용 시간, 복용 횟수, 용량(mg, ml 등)은 절대 언급하지 마세요. "
                        "여러 약이 있을 때도 새로운 약을 만들어 추가하지 말고, "
                        "입력으로 받은 약들만 설명하세요. "
                        "설명하기 어려운 약이 있더라도 "
                        "'약 정보 없음', '정보 부족', '알 수 없음' 같은 문장은 절대 쓰지 마세요. "
                        "마크다운 문법은 쓰지 마세요."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.5,
            max_tokens=200
        )
        
        description = response.choices[0].message.content
        description = description.replace('**', '').replace('*', '').replace('_', '')
        description = re.sub(r'\s*\d+\s*(mg|ml|정|알|MG|ML)\s*', '', description, flags=re.IGNORECASE)
        description = re.sub(r'[ \t]+', ' ', description)
        description = re.sub(r'\n{3,}', '\n\n', description)
        description = description.strip()

        # 줄 단위로 정리해서 "무슨 약\n무슨 약\n무슨 약" 형태 보장
        lines = [line.strip() for line in description.splitlines() if line.strip()]
        description = "\n".join(lines)
        
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
        
        if 0 <= days_diff < med['days']:
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
        time = data.get('time', '아침')
        
        if not medication_id:
            return jsonify({'error': '약 ID가 필요합니다.'}), 400

        # 해당 약 정보 조회 (여기서 이름을 쪼갬)
        medication = next((m for m in medications_db if m['id'] == medication_id), None)
        name_parts = []

        if medication and medication.get("name"):
            raw_name = medication.get("name", "")
            # 쉼표, 슬래시, 줄바꿈 기준으로 약 이름 나누기
            name_parts = [part.strip() for part in re.split(r'[,\n/]+', raw_name) if part.strip()]

        # 그래도 없으면 전체 이름 한 덩어리로
        if not name_parts:
            if medication and medication.get("name"):
                name_parts = [medication["name"]]
            else:
                name_parts = [""]

        new_records = []
        today_str = datetime.now().date().isoformat()
        now_iso = datetime.now().isoformat()

        # 약 이름을 하나씩 나눠서 각각 기록 저장
        for part_name in name_parts:
            record = {
                'medication_id': medication_id,
                'time': time,
                'completed_at': now_iso,
                'date': today_str,
                # 복약 내역 화면에서 블럭 하나에 약 하나씩 보여줄 수 있도록 개별 이름 저장
                'medication_name': part_name
            }
            medication_history_db.append(record)
            new_records.append(record)
        
        # 응답 형식은 그대로: record 한 개만 내려보내되, 첫 번째 것을 사용
        return jsonify({
            'success': True,
            'record': new_records[0]
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
    """이달의 복용 내역 조회 + 날짜별 O/X 상태"""
    year = request.args.get('year', datetime.now().year)
    month = request.args.get('month', datetime.now().month)
    # 문자열일 수도 있으니 int로 변환
    year = int(year)
    month = int(month)
    
    # 해당 월의 모든 기록 필터링 (기존 로직 그대로)
    month_history = [
        h for h in medication_history_db
        if datetime.fromisoformat(h['date']).year == year and
           datetime.fromisoformat(h['date']).month == month
    ]
    
    # 날짜별로 기록 그룹화 (기존 로직)
    daily_history = {}
    for record in month_history:
        date_str = record['date']
        if date_str not in daily_history:
            daily_history[date_str] = []
        daily_history[date_str].append(record)
    # -------- O / X 계산 (아침/점심/저녁까지 모두 고려) --------
    start_date = datetime(year, month, 1).date()
    if month == 12:
        next_month_date = datetime(year + 1, 1, 1).date()
    else:
        next_month_date = datetime(year, month + 1, 1).date()
    
    daily_status = {}  # 예: {'2025-11-03': 'O', '2025-11-04': 'X', ...}
    current = start_date
    while current < next_month_date:
        date_str = current.isoformat()
        # 1) 이 날짜에 "원래 먹어야 하는" 약들(약 + 시간대) 계산
        required_pairs = set()  # (med_id, time) 쌍
        required_meds_for_day = []
        for med in medications_db:
            registered_date = datetime.fromisoformat(med['registered_date']).date()
            days_diff = (current - registered_date).days
            if 0 <= days_diff < med['days']:
                required_meds_for_day.append(med)
                for t in med.get('times', []):
                    required_pairs.add((med['id'], t))
        # 먹어야 할 약이 하나도 없는 날 → 상태 아예 기록하지 않음 (프론트에서 표시 X)
        if not required_pairs:
            current += timedelta(days=1)
            continue
        # 2) 이 날짜의 실제 복용 기록들
        day_records = [r for r in medication_history_db if r['date'] == date_str]
        # 3) 저녁 버튼을 한 번이라도 누른 날만 O/X 평가
        has_evening_action = any(r['time'] == '저녁' for r in day_records)
        if not has_evening_action:
            # 아직 저녁 완료를 안 눌렀으면 이 날은 표시하지 않음
            current += timedelta(days=1)
            continue
        # 4) 실제로 먹은 (med_id, time) 쌍
        taken_pairs = {(r['medication_id'], r['time']) for r in day_records}
        # 5) 모든 (med_id, time)이 완료되었는지 체크
        all_taken = required_pairs.issubset(taken_pairs)
        daily_status[date_str] = 'O' if all_taken else 'X'
        current += timedelta(days=1)
    # -------- O / X 계산 끝 --------
    return jsonify({
        'history': daily_history,
        'year': year,
        'month': month,
        'daily_status': daily_status  # 달력에서 이걸로 O / X 표시
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
            "type": data.get("type", "login")
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
    
    print("\n등록된 라우트:")
    for rule in app.url_map.iter_rules():
        print(f"  {rule.rule} [{', '.join(rule.methods)}]")
    print()
    
    app.run(debug=True, host='0.0.0.0', port=5001, use_reloader=False)