from pathlib import Path
from typing import Any

import pandas as pd
from fastapi import APIRouter, HTTPException

from RAG.report_generator import generate_security_report
from RAG.schemas import SecurityEvent

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[1]
PROCESSED_CSV_PATH = BASE_DIR / "data" / "processed_events.csv"

BENIGN_MESSAGE = "정상 트래픽입니다."


def load_event_by_id(event_id: str) -> dict[str, Any]:
    if not PROCESSED_CSV_PATH.exists():
        raise HTTPException(
            status_code=404,
            detail="processed_events.csv 파일을 찾을 수 없습니다.",
        )

    df = pd.read_csv(PROCESSED_CSV_PATH)

    if "event_id" not in df.columns:
        raise HTTPException(
            status_code=500,
            detail="processed_events.csv에 event_id 컬럼이 없습니다.",
        )

    matched = df[df["event_id"].astype(str) == str(event_id)]

    if matched.empty:
        raise HTTPException(
            status_code=404,
            detail=f"{event_id} 이벤트를 찾을 수 없습니다.",
        )

    return matched.iloc[0].to_dict()

def get_attack_label(attack_type: str) -> int:
    attack_label_map = {
        "Benign": 0,
        "Injection": 1,
        "Password": 2,
        "Reconnaissance": 3,
        "Scanning": 4,
        "XSS": 5,
    }

    return attack_label_map.get(str(attack_type).strip(), 0)

def build_security_event(event: dict[str, Any]) -> SecurityEvent:
    attack_type = str(event.get("attack_type", "Benign"))
    attack_label = get_attack_label(attack_type)

    return SecurityEvent(
        event_id=str(event.get("event_id", "")),
        timestamp=str(event.get("timestamp", "")),
        source_ip=str(event.get("source_ip", "")),
        destination_ip=str(event.get("destination_ip", "")),
        protocol=str(event.get("protocol", "")),
        attack_type=attack_type,
        attack_category=str(event.get("attack_category", "")),
        confidence=float(event.get("confidence", 0)),
        risk_level=str(event.get("risk_level", "")),
        status=str(event.get("status", "")),
        priority_score=int(event.get("priority_score", 0)),

        # RAG 모듈이 기대하는 필드
        Attack_label=attack_label,
    )


def build_benign_report(event_id: str) -> dict[str, Any]:
    return {
        "event_id": event_id,
        "report_summary": BENIGN_MESSAGE,
        "report_reason": BENIGN_MESSAGE,
        "report_impact": BENIGN_MESSAGE,
        "report_checkpoints": [BENIGN_MESSAGE],
        "report_response": [BENIGN_MESSAGE],
        "report_created_at": "",
    }


def normalize_report_response(event_id: str, rag_result: Any) -> dict[str, Any]:
    """
    RAG 결과가 dict, pydantic model, 문자열 중 어떤 형태로 와도
    프론트에서 쓰는 형태로 맞춰 반환한다.
    """

    if hasattr(rag_result, "model_dump"):
        rag_result = rag_result.model_dump()

    elif hasattr(rag_result, "dict"):
        rag_result = rag_result.dict()

    if isinstance(rag_result, dict):
        return {
            "event_id": event_id,
            "report_summary": rag_result.get("report_summary")
            or rag_result.get("summary")
            or "",
            "report_reason": rag_result.get("report_reason")
            or rag_result.get("reason")
            or "",
            "report_impact": rag_result.get("report_impact")
            or rag_result.get("impact")
            or "",
            "report_checkpoints": rag_result.get("report_checkpoints")
            or rag_result.get("checkpoints")
            or [],
            "report_response": rag_result.get("report_response")
            or rag_result.get("response")
            or rag_result.get("recommendations")
            or [],
            "report_created_at": rag_result.get("report_created_at")
            or rag_result.get("created_at")
            or "",
        }

    return {
        "event_id": event_id,
        "report_summary": str(rag_result),
        "report_reason": "",
        "report_impact": "",
        "report_checkpoints": [],
        "report_response": [],
        "report_created_at": "",
    }


@router.get("/api/report/{event_id}")
def get_report(event_id: str):
    """
    이벤트 ID로 processed_events.csv에서 이벤트를 찾고,
    해당 이벤트 정보를 RAG 모듈에 넘겨 보안 리포트를 생성한다.
    """

    event = load_event_by_id(event_id)

    if str(event.get("attack_type", "")).strip() == "Benign":
        return build_benign_report(event_id)

    security_event = build_security_event(event)

    try:
        rag_result = generate_security_report(security_event)
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"RAG 리포트 생성 실패: {error}",
        )

    return normalize_report_response(event_id, rag_result)