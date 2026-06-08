# backend — FastAPI 서버

## 엔드포인트

| 메서드 | 경로 | 설명 | 상태 |
|--------|------|------|------|
| GET | `/api/events` | 탐지 이벤트 목록 반환 | 더미 트래픽 데이터를 Azure ML 모델로 추론한 결과 (사전 계산) |
| GET | `/api/stats` | 대시보드 통계 반환 | 더미 데이터 |
| POST | `/api/predict` | Azure ML 엔드포인트 호출 → 공격 분류 (이진 → 다중 2단계) | 구현 완료 |
| GET | `/api/report/{event_id}` | 공격 유형별 보안 리포트 생성 | 공격 유형별 템플릿 응답 (RAG 연동 안됨) |

## 구현 상태

**완료**
- FastAPI 기본 구조 및 CORS 설정
- Azure ML 엔드포인트 연동 (`predict.py`) — 이진분류 후 공격으로 판정되면 다중분류까지 호출하는 2단계 흐름, 키 없을 시 더미 응답 반환
- 더미 트래픽 데이터(`dummy_final_with_date.csv`)를 Azure ML 모델로 추론해 이벤트 데이터셋 생성 (`generate_processed_events.py` → `data/processed_events.csv`)
- `events.py`에서 날짜별 4,000~5,000개 층화 샘플링으로 이벤트 목록 제공

**미완**
- DB 연동 (`stats.py` 현재 하드코딩)
- `/api/report` ↔ RAG 모듈 연동 — 현재 `report.py`는 공격 유형별 템플릿 응답만 반환하며, RAG 모듈(`backend/RAG/`)은 아직 호출되지 않음
- `generate_processed_events.py`의 `ROW_LIMIT`(현재 300건 테스트용)을 늘려 전체 데이터 생성

## 파일 구조

```
backend/
├── main.py                      # FastAPI 앱 진입점, 라우터 등록
├── .env                         # Azure ML 키 (gitignore)
├── generate_processed_events.py # 더미 트래픽 데이터를 Azure ML로 추론 → processed_events.csv 생성
├── data/
│   ├── dummy_final_with_date.csv  # 추론 입력용 더미 트래픽 데이터
│   └── processed_events.csv       # 추론 결과가 포함된 이벤트 데이터 (events.py가 서빙)
├── RAG/                         # 보안 리포트 생성 모듈 (Azure AI Search + GPT-4o, report.py 연동 필요)
└── api/
    ├── predict.py   # POST /api/predict — Azure ML 분류 (이진 → 다중)
    ├── report.py    # GET  /api/report/{id} — 공격 유형별 템플릿 리포트 (RAG 연동 필요)
    ├── events.py    # GET  /api/events — 추론된 이벤트 목록 + 날짜별 샘플링
    └── stats.py     # GET  /api/stats — 통계 (더미)
```

## 환경변수 (.env)

```
AZURE_BINARY_ENDPOINT_URL=   # 이진 분류 엔드포인트
AZURE_BINARY_ENDPOINT_KEY=
AZURE_MULTI_ENDPOINT_URL=    # 다중 분류 엔드포인트
AZURE_MULTI_ENDPOINT_KEY=
```
