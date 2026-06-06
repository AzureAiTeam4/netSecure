from typing import TypedDict, List


class SecurityEvent(TypedDict, total=False):
    # 예시 확정 필드: ML 모델 출력
    # (1=injection, 2=password, 3=reconnaissance, 4=scanning, 5=xss)
    Attack_label: int   # required

    # 나머지 필드는 백엔드 스키마 확정 후 추가 필요


class SecurityReport(TypedDict):
    report_summary: str             # 이벤트 한 문장 요약
    report_reason: str              # 탐지 이유
    report_impact: str              # 예상 피해
    report_checkpoints: List[str]   # 확인·점검 항목
    report_response: List[str]      # 조치·차단·수정·강화 항목
    # event_id, report_id, report_created_at 은 백엔드에서 생성
