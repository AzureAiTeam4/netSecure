# backend — FastAPI 서버

## 엔드포인트

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/api/events` | 더미 트래픽 데이터를 Azure ML 모델로 추론한 탐지 이벤트 목록 반환 (날짜별 층화 샘플링) |
| GET | `/api/stats` | 대시보드 통계 반환 |
| POST | `/api/predict` | Azure ML 엔드포인트 호출 → 공격 분류 (이진 → 다중 2단계) |
| GET | `/api/report/{event_id}` | `processed_events.csv`에서 이벤트를 조회해 RAG 모듈(Azure AI Search + GPT-4o)로 보안 리포트 생성 |

## 파일 구조

```
backend/
├── main.py                      # FastAPI 앱 진입점, 라우터 등록
├── .env                         # Azure ML 키 (gitignore)
├── generate_processed_events.py # 더미 트래픽 데이터를 Azure ML로 추론 → processed_events.csv 생성
├── data/
│   ├── dummy_final_with_date.csv  # 추론 입력용 더미 트래픽 데이터
│   └── processed_events.csv       # 추론 결과가 포함된 이벤트 데이터 (events.py가 서빙)
├── RAG/                         # 보안 리포트 생성 모듈 (Azure AI Search + GPT-4o, report.py에 연동 완료)
└── api/
    ├── predict.py   # POST /api/predict — Azure ML 분류 (이진 → 다중)
    ├── report.py    # GET  /api/report/{id} — RAG 모듈 호출해 보안 리포트 실시간 생성
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

RAG 모듈(`/api/report`)은 별도로 `RAG/.env`에 Azure OpenAI·Azure AI Search 키를 둔다 (자세한 내용은 [`RAG/README.md`](RAG/README.md) 참고).
```
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_DEPLOYMENT=
AZURE_SEARCH_ENDPOINT=
AZURE_SEARCH_KEY=
AZURE_SEARCH_INDEX_NAME=
AZURE_SEARCH_SEMANTIC_CONFIG=
```
