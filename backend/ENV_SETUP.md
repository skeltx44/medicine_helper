# 환경변수 설정 가이드

## .env 파일 생성 방법

1. `backend` 폴더에 `.env` 파일을 생성하세요.

2. `.env` 파일에 다음 내용을 추가하세요:
```
OPENAI_API_KEY=your-api-key-here
```

3. 실제 API 키로 교체하세요:
```
OPENAI_API_KEY=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
```

## 주의사항

- `.env` 파일은 절대 Git에 커밋하지 마세요!
- `.env` 파일은 이미 `.gitignore`에 포함되어 있습니다.


