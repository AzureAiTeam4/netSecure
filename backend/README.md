# backend — FastAPI 서버

## 엔드포인트

| 메서드 | 경로 | 설명 | 상태 |
|--------|------|------|------|
| GET | `/api/events` | 탐지 이벤트 목록 반환 | 더미 데이터 |
| GET | `/api/stats` | 대시보드 통계 반환 | 더미 데이터 |
| POST | `/api/predict` | Azure ML 엔드포인트 호출 → 공격 분류 | 구현 완료 |
| GET | `/api/report/{event_id}` | RAG 모듈 호출 → 보안 리포트 생성 | 구현 완료 |

## 구현 상태

**완료**
- FastAPI 기본 구조 및 CORS 설정
- Azure ML 엔드포인트 연동 (`predict.py`) — 키 없을 시 더미 응답 반환
- RAG 모듈 연동 (`report.py`) — 실패 시 더미 응답 반환

**미완**
- DB 연동 (`events.py`, `stats.py` 현재 하드코딩)

## 파일 구조

```
backend/
├── main.py          # FastAPI 앱 진입점, 라우터 등록
├── .env             # Azure ML 키 (gitignore)
└── api/
    ├── predict.py   # POST /api/predict — Azure ML 분류
    ├── report.py    # GET  /api/report/{id} — RAG 리포트 생성
    ├── events.py    # GET  /api/events — 이벤트 목록 (더미)
    └── stats.py     # GET  /api/stats — 통계 (더미)
```

## 환경변수 (.env)

```
AZURE_BINARY_ENDPOINT_URL=   # 이진 분류 엔드포인트
AZURE_BINARY_ENDPOINT_KEY=
AZURE_MULTI_ENDPOINT_URL=    # 다중 분류 엔드포인트
AZURE_MULTI_ENDPOINT_KEY=
```
