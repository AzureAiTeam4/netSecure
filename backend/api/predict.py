from fastapi import APIRouter  # FastAPI 라우터 가져오기
from pydantic import BaseModel  # 요청 데이터 형식 정의
import requests  # Azure ML 엔드포인트 호출용
import os  # 환경변수 가져오기

router = APIRouter()

# 프론트엔드에서 보내는 트래픽 데이터 형식 정의
class TrafficData(BaseModel):
    src_ip: str          # 출발지 IP
    dst_ip: str          # 목적지 IP
    protocol: int        # 프로토콜 번호
    in_bytes: float      # 수신 바이트
    out_bytes: float     # 송신 바이트
    in_pkts: float       # 수신 패킷 수
    flow_duration: float # 연결 지속 시간

# POST /api/predict 요청이 오면 이 함수 실행
@router.post("/api/predict")
def predict(data: TrafficData):

    # Azure ML 엔드포인트 URL이랑 키 (나중에 채우면 됨)
    ENDPOINT_URL = os.getenv("AZURE_ML_ENDPOINT_URL", "")
    ENDPOINT_KEY = os.getenv("AZURE_ML_ENDPOINT_KEY", "")

    # 엔드포인트 없으면 더미 데이터 반환 (개발용)
    if not ENDPOINT_URL:
        return {
            "is_attack": True,
            "attack_type": "DDoS",
            "confidence": 0.95,
            "risk": "HIGH",
            "src_ip": data.src_ip,
            "dst_ip": data.dst_ip
        }

    # Azure ML 엔드포인트 호출 (나중에 배포 완료되면 사용)
    response = requests.post(
        url=ENDPOINT_URL,
        headers={"Authorization": f"Bearer {ENDPOINT_KEY}"},
        json={"data": [[
            data.protocol,
            data.in_bytes,
            data.out_bytes,
            data.in_pkts,
            data.flow_duration
        ]]}
    )

    return response.json()