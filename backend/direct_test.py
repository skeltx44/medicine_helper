"""
Flask 앱을 직접 로드하고 테스트하는 스크립트
"""
from app import app
import json

# 등록된 모든 라우트 확인
print("=" * 60)
print("등록된 모든 라우트:")
print("=" * 60)
for rule in app.url_map.iter_rules():
    if '/api' in rule.rule or rule.rule == '/':
        print(f"  {rule.rule:40} {', '.join(sorted(rule.methods))}")

print("\n" + "=" * 60)
print("Health 엔드포인트 테스트:")
print("=" * 60)

# Flask 테스트 클라이언트로 직접 테스트
with app.test_client() as client:
    # 루트 경로 테스트
    print("\n1. 루트 경로 (/) 테스트:")
    response = client.get('/')
    print(f"   Status Code: {response.status_code}")
    if response.status_code == 200:
        data = json.loads(response.data)
        print(f"   Response: {json.dumps(data, indent=2, ensure_ascii=False)[:200]}")
    
    # Health 엔드포인트 테스트
    print("\n2. Health 엔드포인트 (/api/health) 테스트:")
    response = client.get('/api/health')
    print(f"   Status Code: {response.status_code}")
    if response.status_code == 200:
        data = json.loads(response.data)
        print(f"   Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
    else:
        print(f"   Response: {response.data.decode('utf-8')[:200]}")
    
    # Health 엔드포인트 (trailing slash) 테스트
    print("\n3. Health 엔드포인트 (/api/health/) 테스트:")
    response = client.get('/api/health/')
    print(f"   Status Code: {response.status_code}")
    if response.status_code == 200:
        data = json.loads(response.data)
        print(f"   Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
    else:
        print(f"   Response: {response.data.decode('utf-8')[:200]}")

print("\n" + "=" * 60)

