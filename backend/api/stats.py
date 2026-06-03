from fastapi import APIRouter  # FastAPI 라우터 가져오기

router = APIRouter()  # 라우터 객체 생성

# GET /api/stats 요청이 오면 이 함수 실행
# 프론트엔드 대시보드 통계 카드에 표시될 데이터
@router.get("/api/stats")
def get_stats():
    return {
        "total_events": 1024,      # 전체 탐지된 이벤트 수
        "attack_count": 683,       # 공격으로 탐지된 수
        "normal_count": 341,       # 정상으로 탐지된 수
        "high_risk": 124,          # 위험도 HIGH 개수
        "medium_risk": 302,        # 위험도 MEDIUM 개수
        "low_risk": 257,           # 위험도 LOW 개수
        "attack_types": {          # 공격 유형별 개수
            "DDoS": 200,
            "XSS": 150,
            "scanning": 133,
            "password": 100,
            "injection": 100
        }
    }