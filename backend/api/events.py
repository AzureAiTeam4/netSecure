from pathlib import Path

import pandas as pd
from fastapi import APIRouter

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[1]
PROCESSED_CSV_PATH = BASE_DIR / "data" / "processed_events.csv"


@router.get("/api/events")
def get_events():
    if not PROCESSED_CSV_PATH.exists():
        return {
            "data_range": {
                "start": "",
                "end": "",
            },
            "events": [],
        }

    df = pd.read_csv(PROCESSED_CSV_PATH)

    # 프론트 성능을 위해 일단 3000개만 반환
    # 전체 5만 개가 필요하면 이 줄을 제거하거나 숫자 변경
    df = df.head(3000)

    events = df.to_dict(orient="records")

    return {
        "data_range": {
            "start": str(events[0]["timestamp"]) if events else "",
            "end": str(events[-1]["timestamp"]) if events else "",
        },
        "events": events,
    }