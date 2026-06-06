from pathlib import Path
import os
import time
from unittest import result
from urllib import response

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
INPUT_CSV = BASE_DIR / "data" / "dummy_final_with_date.csv"
OUTPUT_CSV = BASE_DIR / "data" / "processed_events.csv"

BINARY_URL = os.getenv("AZURE_BINARY_ENDPOINT_URL")
BINARY_KEY = os.getenv("AZURE_BINARY_ENDPOINT_KEY")
MULTI_URL = os.getenv("AZURE_MULTI_ENDPOINT_URL")
MULTI_KEY = os.getenv("AZURE_MULTI_ENDPOINT_KEY")

# 처음에는 300개 정도만 테스트하고, 성공하면 None으로 바꿔서 전체 5만 개 처리
ROW_LIMIT = 300

BATCH_SIZE = 1

ATTACK_LABEL_MAP = {
    "0": "Benign",
    "1": "Injection",
    "2": "Password",
    "3": "Reconnaissance",
    "4": "Scanning",
    "5": "XSS",
    "Benign": "Benign",
    "Injection": "Injection",
    "Password": "Password",
    "Reconnaissance": "Reconnaissance",
    "Scanning": "Scanning",
    "XSS": "XSS",
}

ATTACK_CATEGORY_MAP = {
    "Injection": "웹 공격",
    "XSS": "웹 공격",
    "Password": "인증 공격",
    "Scanning": "탐색형 공격",
    "Reconnaissance": "탐색형 공격",
    "Benign": "정상 트래픽",
}


MODEL_COLUMNS = [
    "L4_SRC_PORT",
    "L4_DST_PORT",
    "PROTOCOL",
    "L7_PROTO",
    "IN_BYTES",
    "IN_PKTS",
    "OUT_BYTES",
    "OUT_PKTS",
    "FLOW_DURATION_MILLISECONDS",
    "DURATION_IN",
    "DURATION_OUT",
    "TCP_WIN_MAX_IN",
    "TCP_WIN_MAX_OUT",
    "LONGEST_FLOW_PKT",
    "SHORTEST_FLOW_PKT",
    "MIN_IP_PKT_LEN",
    "SRC_TO_DST_AVG_THROUGHPUT",
    "DST_TO_SRC_AVG_THROUGHPUT",
    "RETRANSMITTED_IN_BYTES",
    "RETRANSMITTED_IN_PKTS",
    "RETRANSMITTED_OUT_BYTES",
    "RETRANSMITTED_OUT_PKTS",
    "TCP_FLAGS_FIN",
    "TCP_FLAGS_SYN",
    "TCP_FLAGS_RST",
    "TCP_FLAGS_PSH",
    "TCP_FLAGS_ACK",
    "TCP_FLAGS_URG",
    "TCP_FLAGS_ECE",
    "TCP_FLAGS_CWR",
    "CLIENT_TCP_FLAGS_FIN",
    "CLIENT_TCP_FLAGS_SYN",
    "CLIENT_TCP_FLAGS_RST",
    "CLIENT_TCP_FLAGS_PSH",
    "CLIENT_TCP_FLAGS_ACK",
    "CLIENT_TCP_FLAGS_URG",
    "CLIENT_TCP_FLAGS_ECE",
    "CLIENT_TCP_FLAGS_CWR",
    "SERVER_TCP_FLAGS_FIN",
    "SERVER_TCP_FLAGS_SYN",
    "SERVER_TCP_FLAGS_RST",
    "SERVER_TCP_FLAGS_PSH",
    "SERVER_TCP_FLAGS_ACK",
    "SERVER_TCP_FLAGS_URG",
    "SERVER_TCP_FLAGS_ECE",
    "SERVER_TCP_FLAGS_CWR",
    "MIN_TTL",
    "MAX_TTL",
    "NUM_PKTS_UP_TO_128_BYTES",
    "NUM_PKTS_128_TO_256_BYTES",
    "NUM_PKTS_256_TO_512_BYTES",
    "NUM_PKTS_512_TO_1024_BYTES",
    "NUM_PKTS_1024_TO_1514_BYTES",
]


def validate_env():
    missing = []

    for name, value in {
        "AZURE_BINARY_ENDPOINT_URL": BINARY_URL,
        "AZURE_BINARY_ENDPOINT_KEY": BINARY_KEY,
        "AZURE_MULTI_ENDPOINT_URL": MULTI_URL,
        "AZURE_MULTI_ENDPOINT_KEY": MULTI_KEY,
    }.items():
        if not value:
            missing.append(name)

    if missing:
        raise RuntimeError(
            "Azure ML 환경변수가 비어 있습니다: "
            + ", ".join(missing)
            + "\nbackend/.env 값을 먼저 확인하세요."
        )


def build_input_records(df: pd.DataFrame) -> list[dict]:
    records = []

    for _, row in df.iterrows():
        record = {}

        for column in MODEL_COLUMNS:
            value = row[column] if column in row and pd.notna(row[column]) else 0
            record[column] = float(value)

        # Azure ML Designer 배포 모델의 입력 스키마에 Label, Attack_label이 포함되어 있어서
        # 예측 요청 시에도 해당 컬럼을 더미값으로 포함해야 함
        record["Label"] = 0.0
        record["Attack_label"] = 0.0

        records.append(record)

    return records


def call_azure_ml(url: str, key: str, records: list[dict]) -> list[dict]:
    payload = {
        "Inputs": {
            "input1": records,
        },
        "GlobalParameters": {},
    }

    response = requests.post(
        url=url,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=120,
    )

    if not response.ok:
        print("Azure ML 요청 실패")
        print("Status Code:", response.status_code)
        print("Response Text:", response.text)
        response.raise_for_status()

    result = response.json()

    results = result.get("Results", {})

    if "WebServiceOutput1" in results:
        return results["WebServiceOutput1"]

    if "output1" in results:
        return results["output1"]

    if "WebServiceOutput0" in results:
        return results["WebServiceOutput0"]

    first_key = next(iter(results))
    return results[first_key]


def get_scored_label(result_row: dict):
    for key in ["Scored Labels", "Scored Label", "scored_label", "label"]:
        if key in result_row:
            return result_row[key]

    return None


def get_confidence(result_row: dict, default: float = 0.9) -> float:
    for key in [
        "Scored Probabilities",
        "Scored Probability",
        "Probability",
        "probability",
        "confidence",
    ]:
        if key in result_row:
            try:
                return float(result_row[key])
            except Exception:
                return default

    return default


def normalize_attack_type(label) -> str:
    if label is None:
        return "Benign"

    label_text = str(label).strip()
    return ATTACK_LABEL_MAP.get(label_text, label_text)


def get_risk_level(attack_type: str, confidence: float) -> str:
    if attack_type in ["Injection", "XSS", "Password"]:
        return "High"

    if attack_type in ["Scanning", "Reconnaissance"]:
        return "Medium"

    return "Low"


def get_status(risk_level: str) -> str:
    if risk_level == "High":
        return "확인 필요"

    if risk_level == "Medium":
        return "관찰 필요"

    return "정상"


def get_priority_score(risk_level: str, confidence: float) -> int:
    confidence_score = round(confidence * 100) if confidence <= 1 else round(confidence)

    if risk_level == "High":
        return min(100, max(85, confidence_score))

    if risk_level == "Medium":
        return min(84, max(55, confidence_score))

    return min(40, max(5, confidence_score // 2))


def main():
    validate_env()

    if not INPUT_CSV.exists():
        raise FileNotFoundError(f"원본 CSV를 찾을 수 없습니다: {INPUT_CSV}")

    df = pd.read_csv(INPUT_CSV)

    if ROW_LIMIT is not None:
        df = df.head(ROW_LIMIT)

    processed_rows = []

    total = len(df)
    print(f"총 {total}개 행 처리 시작")

    for start in range(0, total, BATCH_SIZE):
        end = min(start + BATCH_SIZE, total)
        batch_df = df.iloc[start:end]

        print(f"{start + 1} ~ {end}행 이진분류 요청 중...")

        records = build_input_records(batch_df)
        binary_results = call_azure_ml(BINARY_URL, BINARY_KEY, records)

        attack_records = []
        attack_original_indexes = []
        row_predictions = []

        for local_index, result_row in enumerate(binary_results):
            scored_label = get_scored_label(result_row)
            is_attack = str(scored_label) == "1"

            binary_confidence = get_confidence(result_row, default=0.9)

            row_predictions.append(
                {
                    "is_attack": is_attack,
                    "attack_type": "Benign",
                    "confidence": binary_confidence,
                }
            )

            if is_attack:
                attack_records.append(records[local_index])
                attack_original_indexes.append(local_index)

        if attack_records:
            print(f"{start + 1} ~ {end}행 중 공격 {len(attack_records)}건 다중분류 요청 중...")
            multi_results = call_azure_ml(MULTI_URL, MULTI_KEY, attack_records)

            for result_index, result_row in enumerate(multi_results):
                original_local_index = attack_original_indexes[result_index]
                multi_label = get_scored_label(result_row)
                attack_type = normalize_attack_type(multi_label)
                confidence = get_confidence(
                    result_row,
                    default=row_predictions[original_local_index]["confidence"],
                )

                row_predictions[original_local_index] = {
                    "is_attack": True,
                    "attack_type": attack_type,
                    "confidence": confidence,
                }

        for local_index, (_, row) in enumerate(batch_df.iterrows()):
            global_index = start + local_index
            prediction = row_predictions[local_index]

            attack_type = prediction["attack_type"]
            confidence = prediction["confidence"]
            risk_level = get_risk_level(attack_type, confidence)
            status = get_status(risk_level)

            processed_rows.append(
                {
                    "event_id": f"E-{global_index + 1:05d}",
                    "timestamp": row.get("Date", "2026-06-03"),
                    "source_ip": f"192.168.1.{100 + (global_index % 100)}",
                    "destination_ip": f"10.0.0.{10 + (global_index % 50)}",
                    "protocol": "TCP",
                    "attack_type": attack_type,
                    "attack_category": ATTACK_CATEGORY_MAP.get(attack_type, "기타"),
                    "confidence": round(float(confidence), 4),
                    "risk_level": risk_level,
                    "status": status,
                    "priority_score": get_priority_score(risk_level, float(confidence)),
                }
            )

        time.sleep(0.2)

    processed_df = pd.DataFrame(processed_rows)
    processed_df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")

    print(f"processed_events.csv 생성 완료: {OUTPUT_CSV}")
    print(f"총 {len(processed_df)}개 이벤트 생성")


if __name__ == "__main__":
    main()