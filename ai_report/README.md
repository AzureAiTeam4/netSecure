# ai_report — 보안 리포트 생성 모듈

보안 이벤트를 입력받아 Azure AI Search(RAG) + Azure OpenAI(GPT-4o)로 대응 리포트 JSON을 생성합니다.

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
ai_report/
├── .env                  # Azure 키 및 엔드포인트 (gitignore)
├── requirements.txt
├── config.py             # 환경변수 로드
├── schemas.py            # SecurityEvent, SecurityReport 타입 정의
├── search_client.py      # Azure AI Search 검색
├── prompt_builder.py     # 검색 쿼리 및 프롬프트 생성
├── report_generator.py   # 전체 파이프라인 + JSON 파싱
└── test_report.py        # 5가지 공격 유형 샘플 테스트
```

## 사용법

```python
from ai_report.report_generator import generate_security_report

event = {
    "Attack_label":               1,             # ML 모델 출력 (1=injection, 2=password, 3=reconnaissance, 4=scanning, 5=xss)
    "IPV4_SRC_ADDR":              "203.0.113.10",
    "IPV4_DST_ADDR":              "10.0.0.5",
    "L4_SRC_PORT":                54321,
    "L4_DST_PORT":                3306,
    "PROTOCOL":                   6,
    "L7_PROTO":                   7.0,
    "IN_BYTES":                   511,
    "IN_PKTS":                    5,
    "OUT_BYTES":                  2163,
    "OUT_PKTS":                   5,
    "FLOW_DURATION_MILLISECONDS": 320,
    "MIN_TTL":                    64,
    "MAX_TTL":                    64,
    "TCP_FLAGS_SYN":              1,
    "TCP_FLAGS_ACK":              1,
    "TCP_FLAGS_RST":              0,
    "TCP_FLAGS_FIN":              1,
}

report = generate_security_report(event)
```

> `event_id`, `report_id`, `report_created_at`은 백엔드에서 생성 후 추가합니다.
