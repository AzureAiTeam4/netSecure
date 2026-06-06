from .schemas import SecurityEvent

import json
from datetime import datetime

# Attack_label → 표시명 매핑 (preprocess_01_cleaning.py 기준)
LABEL_MAP = {
    1: "SQL Injection",
    2: "Brute Force",
    3: "Reconnaissance",
    4: "Scanning",
    5: "XSS",
}

QUERY_HINTS = {
    "SQL Injection":  "SQL Injection 대응 방안 입력값 검증 Prepared Statement DB 권한 제한",
    "XSS":            "XSS 예방 방법 output encoding sanitization safe sinks script tag",
    "Brute Force":    "Brute Force 탐지 방법 로그인 실패 계정 잠금 MFA password spraying credential stuffing",
    "Scanning":       "Network Service Discovery Scanning 탐지 완화 포트 스캔 다중 연결",
    "Reconnaissance": "Reconnaissance Active Scanning 탐지 완화 정찰 행위 정보 수집",
}


def build_event_message(event: SecurityEvent) -> str:
    # raw 피처 값을 조합해 이벤트 설명 문자열 생성
    return (
        f"src_port={event.get('L4_SRC_PORT', '')} → dst_port={event.get('L4_DST_PORT', '')}, "
        f"IN={event.get('IN_BYTES', 0)}B/{event.get('IN_PKTS', 0)}pkts "
        f"OUT={event.get('OUT_BYTES', 0)}B/{event.get('OUT_PKTS', 0)}pkts "
        f"FLOW={event.get('FLOW_DURATION_MILLISECONDS', 0)}ms "
        f"FLAGS SYN={event.get('TCP_FLAGS_SYN', 0)} ACK={event.get('TCP_FLAGS_ACK', 0)} "
        f"RST={event.get('TCP_FLAGS_RST', 0)} FIN={event.get('TCP_FLAGS_FIN', 0)} "
        f"TTL={event.get('MIN_TTL', 0)}~{event.get('MAX_TTL', 0)}"
    )


def build_search_query(event: SecurityEvent) -> str:
    # Attack_label → 공격명 변환 후 보안 키워드 합쳐 Azure AI Search 쿼리 생성
    attack_name = LABEL_MAP.get(event["Attack_label"], "Unknown")
    hint = QUERY_HINTS.get(attack_name, "")
    return f"{attack_name} {hint}".strip()


def build_system_prompt() -> str:
    return """
너는 네트워크 보안 이벤트를 분석하고 대응 리포트를 생성하는 보안 관제 AI이다.

사용자가 제공한 보안 이벤트 정보와 RAG 검색 문서 근거를 바탕으로 리포트를 생성한다.
반드시 제공된 문서 근거를 우선 사용한다.
문서 근거에 없는 내용은 과도하게 추측하지 말고, 필요한 경우 "추가 확인 필요"라고 작성한다.

출력은 반드시 JSON 객체만 사용한다.
마크다운, 코드블록, 설명 문장, 주석은 출력하지 않는다.

생성해야 하는 필드는 다음과 같다.

- report_summary:
  이벤트를 한 문장으로 요약한다.

- report_reason:
  탐지된 이벤트가 왜 위험한지 또는 어떤 공격으로 볼 수 있는지 설명한다.

- report_impact:
  해당 이벤트가 실제 침해로 이어질 경우 예상되는 피해나 영향을 설명한다.

- report_checkpoints:
  보안 담당자가 추가로 확인해야 할 로그, 지표, 설정, 시스템 점검 항목을 배열로 작성한다.

- report_response:
  즉시 수행할 수 있는 대응 조치와 재발 방지 조치를 배열로 작성한다.

작성 규칙:
1. 모든 문장은 보안 관제 리포트에 들어갈 수 있는 공식적이고 간결한 문체로 작성한다.
2. report_checkpoints와 report_response는 실무자가 바로 확인하거나 조치할 수 있는 문장으로 작성한다.
3. report_checkpoints에는 "확인", "점검", "분석", "검토" 중심의 항목을 작성한다.
4. report_response에는 "차단", "제한", "수정", "적용", "강화", "비활성화", "모니터링" 중심의 조치를 작성한다.
5. 공격 유형이 SQL Injection 또는 XSS인 경우 입력값 검증, 인코딩, Prepared Statement, 권한 최소화 등 개발 보안 조치를 우선 고려한다.
6. 공격 유형이 Brute Force 또는 Password 관련 이벤트인 경우 로그인 실패 로그, 계정 잠금, MFA, 비밀번호 정책, 출발지 IP 제한을 우선 고려한다.
7. 공격 유형이 Scanning 또는 Reconnaissance인 경우 포트/서비스 접근 로그, 짧은 시간 내 다수 연결, 네트워크 세분화, 불필요한 서비스 비활성화를 우선 고려한다.
8. 동일한 의미의 항목을 반복하지 않는다.
9. JSON 값에는 줄바꿈 문자를 과도하게 포함하지 않는다.
10. 근거 문서와 이벤트 정보가 충돌하면 이벤트 정보를 우선하되, 문서 근거가 부족한 부분은 "추가 확인 필요"라고 작성한다.
""".strip()


def build_user_prompt(event: dict, retrieved_docs: list[dict]) -> str:

    context_blocks = []

    for idx, doc in enumerate(retrieved_docs, start=1):
        title = doc.get("title", "unknown source")
        chunk = doc.get("chunk", "")
        score = doc.get("score", doc.get("@search.score", ""))

        context_blocks.append(
            f"""
        [문서 {idx}]
        source_title: {title}
        search_score: {score}
        content:
        {chunk}
        """.strip()
        )

    retrieved_context = "\n\n".join(context_blocks) if context_blocks else "검색된 문서 근거 없음"

    attack_name = LABEL_MAP.get(event.get("Attack_label"), "Unknown")
    output_schema = {
        "report_summary": f"해당 이벤트는 {attack_name} 공격이 의심됩니다.",
        "report_reason": "",
        "report_impact": "",
        "report_checkpoints": [],
        "report_response": [],
    }

    event_message = build_event_message(event)

    return f"""
[보안 이벤트]
attack_type: {attack_name}
event_message: {event_message}

[RAG 문서 근거]
{retrieved_context}

[요청]
위 보안 이벤트와 RAG 문서 근거를 바탕으로 보안 대응 리포트를 생성하라.
반드시 아래 JSON 형식만 출력하라.

{json.dumps(output_schema, ensure_ascii=False, indent=2)}
""".strip()
