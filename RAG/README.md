# RAG — 보안 리포트 생성 모듈

보안 이벤트를 입력받아 Azure AI Search(RAG) + Azure OpenAI(GPT-4o)로 대응 리포트 JSON 생성

## 흐름

```
event(dict)
  → 공격 유형별 검색 쿼리 생성 (prompt_builder)
  → Azure AI Search에서 관련 문서 검색 (search_client)
  → system/user 프롬프트 조합 (prompt_builder)
  → GPT-4o 호출 → JSON 파싱 (report_generator)
  → report(dict) 반환
```

## 출력 형식

```json
{
  "report_summary": "해당 이벤트는 SQL Injection 공격이 의심됩니다.",
  "report_reason": "...",
  "report_impact": "...",
  "report_checkpoints": ["..."],
  "report_response": ["..."]
}
```

> `event_id`, `report_id`, `report_created_at`은 백엔드에서 생성 후 추가합니다.

## 파일 구조

```
RAG/
├── .env                  # Azure 키 및 엔드포인트 (gitignore)
├── requirements.txt
├── config.py             # 환경변수 로드
├── schemas.py            # SecurityEvent, SecurityReport 타입 정의
├── search_client.py      # Azure AI Search 검색
├── prompt_builder.py     # LABEL_MAP, 검색 쿼리, 프롬프트 생성
├── report_generator.py   # 전체 파이프라인 + JSON 파싱
└── test_report.py        # 5가지 공격 유형 샘플 테스트
```

## 백엔드 연동 시 필요한 작업

| 항목 | 내용 |
|------|------|
| 패키지 설치 | `requirements.txt` 의존성을 FastAPI 가상환경에 설치 |
| 환경변수 | `.env`의 Azure 키·엔드포인트를 FastAPI 서버 환경변수로 등록 |
| 스키마 확정 | `schemas.py`의 `SecurityEvent`에 백엔드 DB 필드 반영 |
| ID 처리 | 반환된 `report`에 `event_id`, `report_id`, `report_created_at` 추가 후 DB 저장 |

```python
# FastAPI 라우터에서 직접 import해서 사용 (예시)
from RAG.report_generator import generate_security_report

@router.post("/report")
async def create_report(event: dict):
    report = generate_security_report(event)  # event는 최소 Attack_label 포함
    report["event_id"] = ...
    report["report_id"] = ...
    report["report_created_at"] = ...
    return report
```
