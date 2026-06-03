from fastapi import APIRouter  # FastAPI에서 라우터(경로 묶음) 기능 가져오기
from datetime import datetime  # 현재 시간 사용하기 위해 가져오기

router = APIRouter()  # 라우터 객체 생성 (main.py에 연결할 거예요)

# GET /api/events 요청이 오면 이 함수 실행
# 프론트엔드에서 이벤트 목록 요청할 때 사용
@router.get("/api/events")
def get_events():
    return {
        "events": [
            {
                "id": 1,  # 이벤트 고유 번호
                "time": datetime.now().isoformat(),  # 탐지 시간
                "src_ip": "192.168.1.100",  # 공격 출발지 IP
                "attack_type": "DDoS",  # 공격 유형
                "risk": "HIGH",  # 위험도
                "status": "탐지됨"  # 현재 상태
            },
            {
                "id": 2,
                "time": datetime.now().isoformat(),
                "src_ip": "192.168.1.200",
                "attack_type": "XSS",
                "risk": "MEDIUM",
                "status": "탐지됨"
            }
        ]
    }