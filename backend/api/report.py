from fastapi import APIRouter
from datetime import datetime

router = APIRouter()


def get_report_id(event_id: str) -> str:
    number = "".join(filter(str.isdigit, event_id)) or "0000"
    return f"R-{number.zfill(4)}"


def get_report_by_attack_type(event_id: str, attack_type: str = "Injection"):
    report_id = get_report_id(event_id)
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if attack_type == "Injection":
        return {
            "event_id": event_id,
            "report_id": report_id,
            "report_summary": f"{event_id} 이벤트는 Injection 공격이 의심됩니다.",
            "report_reason": "웹 입력값 또는 요청 파라미터를 통해 비정상 명령이 삽입되었을 가능성이 있습니다.",
            "report_impact": "데이터베이스 조회, 수정, 정보 노출 등의 위험이 발생할 수 있습니다.",
            "report_checkpoints": [
                "웹 요청 로그에서 비정상 파라미터 확인",
                "DB 접근 로그 확인",
                "동일 출발지 IP의 반복 요청 여부 확인",
            ],
            "report_response": [
                "입력값 검증 로직 점검",
                "Prepared Statement 또는 Parameterized Query 적용 확인",
                "웹 방화벽 정책 강화",
            ],
            "report_created_at": created_at,
        }

    if attack_type == "XSS":
        return {
            "event_id": event_id,
            "report_id": report_id,
            "report_summary": f"{event_id} 이벤트는 XSS 공격이 의심됩니다.",
            "report_reason": "사용자 입력값에 악성 스크립트가 포함되었을 가능성이 있습니다.",
            "report_impact": "사용자 세션 탈취, 악성 스크립트 실행, 웹 페이지 변조 등의 피해가 발생할 수 있습니다.",
            "report_checkpoints": [
                "입력값에 script 태그 또는 이벤트 핸들러 패턴이 있는지 확인",
                "출력 인코딩 적용 여부 확인",
                "게시판, 댓글, 검색창 등 사용자 입력 영역 점검",
            ],
            "report_response": [
                "입력값 검증 및 출력 인코딩 강화",
                "HTML Sanitization 라이브러리 적용",
                "Content Security Policy 적용 검토",
            ],
            "report_created_at": created_at,
        }

    if attack_type == "Password":
        return {
            "event_id": event_id,
            "report_id": report_id,
            "report_summary": f"{event_id} 이벤트는 인증 공격 또는 비밀번호 대입 시도로 의심됩니다.",
            "report_reason": "짧은 시간 안에 반복적인 인증 시도나 비정상 로그인 패턴이 발생했을 가능성이 있습니다.",
            "report_impact": "계정 탈취, 내부 시스템 접근, 데이터 유출 등의 보안 사고로 이어질 수 있습니다.",
            "report_checkpoints": [
                "로그인 실패 횟수와 반복 시도 간격 확인",
                "동일 출발지 IP의 다른 계정 대상 접근 여부 확인",
                "계정 잠금 정책 및 MFA 적용 여부 점검",
            ],
            "report_response": [
                "의심 IP 차단 또는 접근 제한",
                "로그인 실패 횟수 제한 및 계정 잠금 정책 강화",
                "관리자 계정 MFA 적용 검토",
            ],
            "report_created_at": created_at,
        }

    if attack_type == "Scanning":
        return {
            "event_id": event_id,
            "report_id": report_id,
            "report_summary": f"{event_id} 이벤트는 서비스 탐색 또는 포트 스캔 가능성이 있습니다.",
            "report_reason": "공격자가 활성화된 포트나 서비스를 식별하기 위해 반복 접근을 시도했을 가능성이 있습니다.",
            "report_impact": "노출된 서비스 정보가 후속 공격에 활용될 수 있으며, 취약 서비스 발견 시 침해 시도로 이어질 수 있습니다.",
            "report_checkpoints": [
                "동일 출발지 IP의 여러 포트 접근 여부 확인",
                "스캔 대상 시스템의 불필요한 포트 개방 여부 점검",
                "동일 IP의 후속 공격 이벤트 발생 여부 확인",
            ],
            "report_response": [
                "불필요한 포트 및 서비스 비활성화",
                "방화벽 또는 접근 제어 정책으로 의심 IP 제한",
                "스캔 패턴 모니터링 규칙 강화",
            ],
            "report_created_at": created_at,
        }

    if attack_type == "Reconnaissance":
        return {
            "event_id": event_id,
            "report_id": report_id,
            "report_summary": f"{event_id} 이벤트는 정찰 단계의 정보 수집 행위로 의심됩니다.",
            "report_reason": "공격자가 대상 네트워크나 서비스 정보를 파악하기 위해 DNS, WHOIS, 서비스 배너 등의 정보를 수집했을 가능성이 있습니다.",
            "report_impact": "수집된 정보는 이후 표적 공격, 취약점 악용, 피싱, 침투 시도에 활용될 수 있습니다.",
            "report_checkpoints": [
                "DNS 질의, WHOIS 조회, 서비스 배너 수집 시도 여부 확인",
                "동일 출발지 IP의 반복 접근 패턴 확인",
                "외부에 노출된 서비스와 도메인 정보 범위 점검",
            ],
            "report_response": [
                "불필요하게 노출된 서비스 정보 최소화",
                "의심 출발지 IP 접근 제한 검토",
                "정찰성 트래픽 탐지 규칙 강화",
            ],
            "report_created_at": created_at,
        }

    if attack_type == "Benign":
        return {
            "event_id": event_id,
            "report_id": report_id,
            "report_summary": f"{event_id} 이벤트는 정상 트래픽으로 분류되었습니다.",
            "report_reason": "현재 이벤트는 정상 트래픽 패턴에 가까운 것으로 판단됩니다.",
            "report_impact": "즉각적인 보안 영향은 낮지만, 동일 출발지 IP의 반복 이벤트 여부는 관찰할 수 있습니다.",
            "report_checkpoints": [
                "동일 출발지 IP의 반복 이벤트 발생 여부 확인",
                "동일 목적지로 향한 유사 트래픽 확인",
                "정상 트래픽 패턴과 비교",
            ],
            "report_response": [
                "이벤트를 정상 상태로 유지",
                "반복 발생 시 관찰 필요 상태로 재검토",
            ],
            "report_created_at": created_at,
        }

    return {
        "event_id": event_id,
        "report_id": report_id,
        "report_summary": f"{event_id} 이벤트에 대한 보안 리포트입니다.",
        "report_reason": "이벤트의 반복 발생 여부와 정상 트래픽 대비 이상 패턴 여부를 확인할 필요가 있습니다.",
        "report_impact": "단일 이벤트의 영향은 제한적일 수 있으나, 반복 발생 시 보안 위험으로 이어질 수 있습니다.",
        "report_checkpoints": [
            "동일 출발지 IP의 반복 이벤트 발생 여부 확인",
            "동일 목적지로 향한 유사 트래픽 확인",
            "정상 트래픽 패턴과 비교",
        ],
        "report_response": [
            "이벤트를 관찰 상태로 유지",
            "반복 발생 시 위험도 재평가",
        ],
        "report_created_at": created_at,
    }


@router.get("/api/report/{event_id}")
def get_report(event_id: str, attack_type: str = "Injection"):
    """
    프론트 호출 예시:
    GET /api/report/E-0001
    GET /api/report/E-0001?attack_type=Injection

    추후 RAG 모듈 연결 시:
    - event_id로 이벤트 상세 조회
    - attack_type 및 이벤트 정보를 SecurityEvent 스키마로 변환
    - generate_security_report() 호출
    - 아래 응답 구조와 동일하게 반환
    """
    return get_report_by_attack_type(event_id, attack_type)