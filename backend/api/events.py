from pathlib import Path
import random

import pandas as pd
from fastapi import APIRouter

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[1]
PROCESSED_CSV_PATH = BASE_DIR / "data" / "processed_events.csv"


def sample_events_by_date(
    df: pd.DataFrame,
    min_count: int = 4000,
    max_count: int = 5000,
) -> pd.DataFrame:
    """
    날짜별로 4,000~5,000개 사이의 이벤트를 샘플링한다.
    같은 날짜는 새로고침해도 같은 개수/샘플이 나오도록 seed를 날짜 기준으로 고정한다.
    attack_type 비율이 크게 무너지지 않도록 attack_type별 층화 샘플링을 적용한다.
    """
    if "timestamp" not in df.columns:
        return df

    sampled_parts = []

    working_df = df.copy()
    working_df["event_date"] = working_df["timestamp"].astype(str).str.slice(0, 10)

    for event_date, date_df in working_df.groupby("event_date", sort=True):
        date_seed = int(event_date.replace("-", ""))
        rng = random.Random(date_seed)

        target_count = rng.randint(min_count, max_count)
        target_count = min(target_count, len(date_df))

        if target_count <= 0:
            continue

        if "attack_type" not in date_df.columns:
            sampled = date_df.sample(
                n=target_count,
                random_state=date_seed,
            )
            sampled_parts.append(sampled)
            continue

        sampled_groups = []
        total_count = len(date_df)
        type_counts = date_df["attack_type"].value_counts()

        for attack_type, group_count in type_counts.items():
            group_df = date_df[date_df["attack_type"] == attack_type]

            ratio = group_count / total_count
            sample_count = round(target_count * ratio)
            sample_count = min(sample_count, len(group_df))

            if sample_count > 0:
                sampled_group = group_df.sample(
                    n=sample_count,
                    random_state=date_seed + abs(hash(str(attack_type))) % 10000,
                )
                sampled_groups.append(sampled_group)

        if sampled_groups:
            sampled = pd.concat(sampled_groups)
        else:
            sampled = pd.DataFrame(columns=date_df.columns)

        # 반올림 때문에 목표 개수보다 적게 뽑힌 경우 남은 개수 보충
        remaining_count = target_count - len(sampled)

        if remaining_count > 0:
            remaining_df = date_df.drop(index=sampled.index, errors="ignore")

            if len(remaining_df) > 0:
                extra = remaining_df.sample(
                    n=min(remaining_count, len(remaining_df)),
                    random_state=date_seed + 999,
                )
                sampled = pd.concat([sampled, extra])

        # 혹시 목표보다 많이 뽑힌 경우 잘라내기
        if len(sampled) > target_count:
            sampled = sampled.sample(
                n=target_count,
                random_state=date_seed + 555,
            )

        sampled_parts.append(sampled)

    if not sampled_parts:
        return working_df.drop(columns=["event_date"], errors="ignore")

    result = pd.concat(sampled_parts)
    result = result.drop(columns=["event_date"], errors="ignore")

    # 시간순 정렬
    if "timestamp" in result.columns:
        result = result.sort_values("timestamp", ascending=False)

    return result.reset_index(drop=True)


@router.get("/api/events")
def get_events():
    if not PROCESSED_CSV_PATH.exists():
        return {
            "total": 0,
            "data_range": {
                "start": "",
                "end": "",
            },
            "events": [],
            "error": "processed_events.csv 파일을 찾을 수 없습니다.",
        }

    df = pd.read_csv(PROCESSED_CSV_PATH)

    if df.empty:
        return {
            "total": 0,
            "data_range": {
                "start": "",
                "end": "",
            },
            "events": [],
        }

    # 전체 원본 데이터 기준 날짜 범위
    if "timestamp" in df.columns:
        date_values = df["timestamp"].astype(str).str.slice(0, 10)
        data_range = {
            "start": str(date_values.min()),
            "end": str(date_values.max()),
        }
    else:
        data_range = {
            "start": "",
            "end": "",
        }

    # 날짜별 4,000~5,000개 샘플링
    sampled_df = sample_events_by_date(
        df,
        min_count=4000,
        max_count=5000,
    )

    events = sampled_df.to_dict(orient="records")

    return {
        "total": len(events),
        "data_range": data_range,
        "events": events,
    }