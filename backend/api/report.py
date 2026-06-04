from fastapi import APIRouter  # FastAPI 라우터 가져오기

router = APIRouter()

# GET /api/report/{event_id} 요청이 오면 이 함수 실행
# Azure OpenAI/Search 키 받으면 RAG 연결 예정
@router.get("/api/report/{event_id}")
def get_report(event_id: int, attack_label: int = 1):
    return {
        "event_id": event_id,
        "attack_label": attack_label,
        "report_summary": "DDoS 공격이 탐지되었습니다.",
        "report_reason": "비정상적으로 높은 패킷 트래픽 감지",
        "report_impact": "서비스 가용성 저하 가능",
        "report_checkpoints": ["트래픽 로그 확인", "방화벽 설정 확인"],
        "report_response": ["해당 IP 차단", "rate limiting 적용"]
    }