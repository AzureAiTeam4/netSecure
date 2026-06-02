from typing import TypedDict, List


class SecurityEvent(TypedDict):
    # ML 모델 출력 (Attack_label: 1=injection, 2=password, 3=reconnaissance, 4=scanning, 5=xss)
    Attack_label: int

    # 네트워크 원본 (전처리 시 제거됐으나 백엔드가 보유)
    IPV4_SRC_ADDR: str
    IPV4_DST_ADDR: str

    # attack_only_dataset.csv 컬럼과 동일
    L4_SRC_PORT: int
    L4_DST_PORT: int
    PROTOCOL: int
    L7_PROTO: float
    IN_BYTES: int
    IN_PKTS: int
    OUT_BYTES: int
    OUT_PKTS: int
    FLOW_DURATION_MILLISECONDS: int
    MIN_TTL: int
    MAX_TTL: int
    TCP_FLAGS_SYN: int
    TCP_FLAGS_ACK: int
    TCP_FLAGS_RST: int
    TCP_FLAGS_FIN: int


class SecurityReport(TypedDict):
    report_summary: str             # 이벤트 한 문장 요약
    report_reason: str              # 탐지 이유
    report_impact: str              # 예상 피해
    report_checkpoints: List[str]   # 확인·점검 항목
    report_response: List[str]      # 조치·차단·수정·강화 항목
    # event_id, report_id, report_created_at 은 백엔드에서 생성
