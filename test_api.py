# 간단한 API 테스트 스크립트
# 백엔드 서버가 정상 작동하는지 확인하는 테스트

import requests
import json

BASE_URL = 'http://localhost:5000/api'

def test_health():
    """서버 상태 확인"""
    try:
        response = requests.get(f'{BASE_URL}/health')
        print(f"✅ 서버 상태: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ 서버 연결 실패: {e}")
        return False

def test_chat():
    """챗봇 API 테스트"""
    try:
        response = requests.post(
            f'{BASE_URL}/chat',
            json={'message': '안녕하세요'}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 챗봇 응답: {data.get('response', '')[:50]}...")
            return True
        else:
            print(f"❌ 챗봇 API 오류: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 챗봇 API 오류: {e}")
        return False

def test_medications():
    """약 목록 조회 테스트"""
    try:
        response = requests.get(f'{BASE_URL}/medications')
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 등록된 약 개수: {len(data.get('medications', []))}")
            return True
        else:
            print(f"❌ 약 목록 조회 오류: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 약 목록 조회 오류: {e}")
        return False

if __name__ == '__main__':
    print("=" * 50)
    print("API 테스트 시작")
    print("=" * 50)
    
    if not test_health():
        print("\n⚠️ 백엔드 서버가 실행되지 않았습니다.")
        print("백엔드 서버를 먼저 실행해주세요: python backend/app.py")
        exit(1)
    
    print("\n" + "-" * 50)
    test_chat()
    print("-" * 50)
    test_medications()
    print("=" * 50)
    print("테스트 완료")

