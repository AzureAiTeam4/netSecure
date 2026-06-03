from fastapi import APIRouter, HTTPException  # FastAPI 라우터 가져오기
import sys
import os

# RAG 폴더를 import 경로에 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '../../RAG'))

from report_generator import generate_security_report  # RAG 리포트 생성 함수
from schemas import SecurityEvent  # RAG 입력 데이터 형식

router = APIRouter()

# GET /api/report/{event_id} 요청이 오면 이 함수 실행
@router.get("/api/report/{event_id}")
def get_report(event_id: int, attack_label: int = 1):  
    # attack_label: 1=injection, 2=password, 3=reconnaissance, 4=scanning, 5=xss
    
    # SecurityEvent 형식으로 데이터 만들기
    event: SecurityEvent = {
        "Attack_label": attack_label
    }
    
    try:
        # RAG 리포트 생성
        report = generate_security_report(event)
        return {
            "event_id": event_id,
            "attack_label": attack_label,
            **report  # report_summary, report_reason 등 포함
        }
    except Exception as e:
        # RAG 실패하면 더미 데이터 반환 (개발용)
        return {
            "event_id": event_id,
            "report_summary": "DDoS 공격이 탐지되었습니다.",
            "report_reason": "비정상적으로 높은 패킷 트래픽 감지",
            "report_impact": "서비스 가용성 저하 가능",
            "report_checkpoints": ["트래픽 로그 확인", "방화벽 설정 확인"],
            "report_response": ["해당 IP 차단", "rate limiting 적용"]
        }