"""
Flask 앱의 라우트를 테스트하는 스크립트
"""
import requests
import json

def test_routes():
    base_url = "http://localhost:5000"
    
    print("=" * 50)
    print("Flask 앱 라우트 테스트")
    print("=" * 50)
    
    # 루트 경로 테스트
    print("\n1. 루트 경로 (/) 테스트:")
    try:
        response = requests.get(f"{base_url}/")
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        else:
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"   오류: {e}")
    
    # Health 엔드포인트 테스트
    print("\n2. Health 엔드포인트 (/api/health) 테스트:")
    try:
        response = requests.get(f"{base_url}/api/health")
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        else:
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"   오류: {e}")
    
    # 존재하지 않는 경로 테스트 (404 핸들러 확인)
    print("\n3. 존재하지 않는 경로 (/test) 테스트 (404 핸들러):")
    try:
        response = requests.get(f"{base_url}/test")
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 404:
            data = response.json()
            print(f"   Error: {data.get('error')}")
            print(f"   Requested Path: {data.get('requested_path')}")
            print(f"   Available Routes:")
            for route in data.get('available_routes', [])[:10]:  # 처음 10개만
                print(f"     - {route.get('path')} [{', '.join(route.get('methods', []))}]")
        else:
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"   오류: {e}")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    test_routes()

