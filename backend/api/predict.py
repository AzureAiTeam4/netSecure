from fastapi import APIRouter
from pydantic import BaseModel
import requests
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

# 학습 데이터 기준 평균/표준편차 (Z-score 정규화용)
MEANS = {
    'L4_SRC_PORT': 46237.490587333334, 'L4_DST_PORT': 6601.894119555555,
    'PROTOCOL': 8.125692, 'L7_PROTO': 8.447087715111113,
    'IN_BYTES': 901.1828886666667, 'IN_PKTS': 6.060202888888889,
    'OUT_BYTES': 3874.0776255555556, 'OUT_PKTS': 6.346302,
    'FLOW_DURATION_MILLISECONDS': 840916.4904826666,
    'DURATION_IN': 76.00220622222223, 'DURATION_OUT': 36.664164444444445,
    'MIN_TTL': 41.02751222222222, 'MAX_TTL': 41.086209555555556,
    'LONGEST_FLOW_PKT': 495.61374177777776, 'SHORTEST_FLOW_PKT': 50.31534,
    'MIN_IP_PKT_LEN': 41.36580511111111,
    'RETRANSMITTED_IN_BYTES': 66.0259588888889, 'RETRANSMITTED_IN_PKTS': 0.33080133333333334,
    'RETRANSMITTED_OUT_BYTES': 556.1787695555555, 'RETRANSMITTED_OUT_PKTS': 0.5384028888888889,
    'SRC_TO_DST_AVG_THROUGHPUT': 4058099.2132266667, 'DST_TO_SRC_AVG_THROUGHPUT': 10729510.099783111,
    'NUM_PKTS_UP_TO_128_BYTES': 25.96614111111111, 'NUM_PKTS_128_TO_256_BYTES': 0.6052486666666667,
    'NUM_PKTS_256_TO_512_BYTES': 0.5157546666666667, 'NUM_PKTS_512_TO_1024_BYTES': 0.4935366666666667,
    'NUM_PKTS_1024_TO_1514_BYTES': 2.513063333333333,
    'TCP_WIN_MAX_IN': 12445.618085777778, 'TCP_WIN_MAX_OUT': 18608.61968822222
}

STDS = {
    'L4_SRC_PORT': 13329.889110085007, 'L4_DST_PORT': 14908.549853418806,
    'PROTOCOL': 4.5465046773639886, 'L7_PROTO': 22.040122388469328,
    'IN_BYTES': 63049.542488826184, 'IN_PKTS': 158.29421684692352,
    'OUT_BYTES': 285468.5603674523, 'OUT_PKTS': 272.1291332292352,
    'FLOW_DURATION_MILLISECONDS': 1704181.0959953917,
    'DURATION_IN': 326.75058461157977, 'DURATION_OUT': 160.3270778474292,
    'MIN_TTL': 41.812558270716686, 'MAX_TTL': 41.86872319151952,
    'LONGEST_FLOW_PKT': 595.7529921436056, 'SHORTEST_FLOW_PKT': 23.159700523162254,
    'MIN_IP_PKT_LEN': 21.544857427000295,
    'RETRANSMITTED_IN_BYTES': 2443.0097966651933, 'RETRANSMITTED_IN_PKTS': 6.292493248058237,
    'RETRANSMITTED_OUT_BYTES': 13518.81006638243, 'RETRANSMITTED_OUT_PKTS': 9.710640575942145,
    'SRC_TO_DST_AVG_THROUGHPUT': 13328464.304241989, 'DST_TO_SRC_AVG_THROUGHPUT': 45759013.100663185,
    'NUM_PKTS_UP_TO_128_BYTES': 1466.335847545234, 'NUM_PKTS_128_TO_256_BYTES': 14.77146534841889,
    'NUM_PKTS_256_TO_512_BYTES': 11.425325996761421, 'NUM_PKTS_512_TO_1024_BYTES': 43.10836630927331,
    'NUM_PKTS_1024_TO_1514_BYTES': 191.99690357739456,
    'TCP_WIN_MAX_IN': 14370.172201370167, 'TCP_WIN_MAX_OUT': 23413.554601480195
}

def scale_record(record: dict) -> dict:
    scaled = record.copy()
    for col, mean in MEANS.items():
        if col in scaled:
            std = STDS[col]
            val = (scaled[col] - mean) / std
            # ±3 클리핑
            val = max(-3, min(3, val))
            scaled[col] = val
    return scaled


class TrafficData(BaseModel):
    src_ip: str = ""
    dst_ip: str = ""

    L4_SRC_PORT: float = 0
    L4_DST_PORT: float = 0
    PROTOCOL: float = 0
    L7_PROTO: float = 0
    IN_BYTES: float = 0
    IN_PKTS: float = 0
    OUT_BYTES: float = 0
    OUT_PKTS: float = 0
    FLOW_DURATION_MILLISECONDS: float = 0
    DURATION_IN: float = 0
    DURATION_OUT: float = 0

    TCP_FLAGS: float = 0
    CLIENT_TCP_FLAGS: float = 0
    SERVER_TCP_FLAGS: float = 0

    TCP_WIN_MAX_IN: float = 0
    TCP_WIN_MAX_OUT: float = 0
    LONGEST_FLOW_PKT: float = 0
    SHORTEST_FLOW_PKT: float = 0
    MIN_IP_PKT_LEN: float = 0
    MAX_IP_PKT_LEN: float = 0
    SRC_TO_DST_AVG_THROUGHPUT: float = 0
    DST_TO_SRC_AVG_THROUGHPUT: float = 0
    RETRANSMITTED_IN_BYTES: float = 0
    RETRANSMITTED_IN_PKTS: float = 0
    RETRANSMITTED_OUT_BYTES: float = 0
    RETRANSMITTED_OUT_PKTS: float = 0

    TCP_FLAGS_FIN: float = 0
    TCP_FLAGS_SYN: float = 0
    TCP_FLAGS_RST: float = 0
    TCP_FLAGS_PSH: float = 0
    TCP_FLAGS_ACK: float = 0
    TCP_FLAGS_URG: float = 0
    TCP_FLAGS_ECE: float = 0
    TCP_FLAGS_CWR: float = 0

    CLIENT_TCP_FLAGS_FIN: float = 0
    CLIENT_TCP_FLAGS_SYN: float = 0
    CLIENT_TCP_FLAGS_RST: float = 0
    CLIENT_TCP_FLAGS_PSH: float = 0
    CLIENT_TCP_FLAGS_ACK: float = 0
    CLIENT_TCP_FLAGS_URG: float = 0
    CLIENT_TCP_FLAGS_ECE: float = 0
    CLIENT_TCP_FLAGS_CWR: float = 0

    SERVER_TCP_FLAGS_FIN: float = 0
    SERVER_TCP_FLAGS_SYN: float = 0
    SERVER_TCP_FLAGS_RST: float = 0
    SERVER_TCP_FLAGS_PSH: float = 0
    SERVER_TCP_FLAGS_ACK: float = 0
    SERVER_TCP_FLAGS_URG: float = 0
    SERVER_TCP_FLAGS_ECE: float = 0
    SERVER_TCP_FLAGS_CWR: float = 0

    MIN_TTL: float = 0
    MAX_TTL: float = 0
    NUM_PKTS_UP_TO_128_BYTES: float = 0
    NUM_PKTS_128_TO_256_BYTES: float = 0
    NUM_PKTS_256_TO_512_BYTES: float = 0
    NUM_PKTS_512_TO_1024_BYTES: float = 0
    NUM_PKTS_1024_TO_1514_BYTES: float = 0


def get_first_output(result: dict) -> dict:
    results = result.get("Results", {})

    if "WebServiceOutput1" in results:
        return results["WebServiceOutput1"][0]

    if "WebServiceOutput0" in results:
        return results["WebServiceOutput0"][0]

    if "output1" in results:
        return results["output1"][0]

    first_key = next(iter(results))
    return results[first_key][0]


def is_attack_label(label) -> bool:
    return str(label).strip() in ["1", "1.0", "True", "true"]


def normalize_attack_type(label) -> str:
    attack_map = {
        "1": "Injection",
        "1.0": "Injection",
        "2": "Password",
        "2.0": "Password",
        "3": "Reconnaissance",
        "3.0": "Reconnaissance",
        "4": "Scanning",
        "4.0": "Scanning",
        "5": "XSS",
        "5.0": "XSS",
        "Injection": "Injection",
        "Password": "Password",
        "Reconnaissance": "Reconnaissance",
        "Scanning": "Scanning",
        "XSS": "XSS",
    }

    return attack_map.get(str(label).strip(), "Unknown")


def build_model_record(data: TrafficData) -> dict:
    return {
        "L4_SRC_PORT": data.L4_SRC_PORT,
        "L4_DST_PORT": data.L4_DST_PORT,
        "PROTOCOL": data.PROTOCOL,
        "L7_PROTO": data.L7_PROTO,
        "IN_BYTES": data.IN_BYTES,
        "IN_PKTS": data.IN_PKTS,
        "OUT_BYTES": data.OUT_BYTES,
        "OUT_PKTS": data.OUT_PKTS,
        "FLOW_DURATION_MILLISECONDS": data.FLOW_DURATION_MILLISECONDS,
        "DURATION_IN": data.DURATION_IN,
        "DURATION_OUT": data.DURATION_OUT,
        "TCP_WIN_MAX_IN": data.TCP_WIN_MAX_IN,
        "TCP_WIN_MAX_OUT": data.TCP_WIN_MAX_OUT,
        "LONGEST_FLOW_PKT": data.LONGEST_FLOW_PKT,
        "SHORTEST_FLOW_PKT": data.SHORTEST_FLOW_PKT,
        "MIN_IP_PKT_LEN": data.MIN_IP_PKT_LEN,
        "SRC_TO_DST_AVG_THROUGHPUT": data.SRC_TO_DST_AVG_THROUGHPUT,
        "DST_TO_SRC_AVG_THROUGHPUT": data.DST_TO_SRC_AVG_THROUGHPUT,
        "RETRANSMITTED_IN_BYTES": data.RETRANSMITTED_IN_BYTES,
        "RETRANSMITTED_IN_PKTS": data.RETRANSMITTED_IN_PKTS,
        "RETRANSMITTED_OUT_BYTES": data.RETRANSMITTED_OUT_BYTES,
        "RETRANSMITTED_OUT_PKTS": data.RETRANSMITTED_OUT_PKTS,
        "TCP_FLAGS_FIN": data.TCP_FLAGS_FIN,
        "TCP_FLAGS_SYN": data.TCP_FLAGS_SYN,
        "TCP_FLAGS_RST": data.TCP_FLAGS_RST,
        "TCP_FLAGS_PSH": data.TCP_FLAGS_PSH,
        "TCP_FLAGS_ACK": data.TCP_FLAGS_ACK,
        "TCP_FLAGS_URG": data.TCP_FLAGS_URG,
        "TCP_FLAGS_ECE": data.TCP_FLAGS_ECE,
        "TCP_FLAGS_CWR": data.TCP_FLAGS_CWR,
        "CLIENT_TCP_FLAGS_FIN": data.CLIENT_TCP_FLAGS_FIN,
        "CLIENT_TCP_FLAGS_SYN": data.CLIENT_TCP_FLAGS_SYN,
        "CLIENT_TCP_FLAGS_RST": data.CLIENT_TCP_FLAGS_RST,
        "CLIENT_TCP_FLAGS_PSH": data.CLIENT_TCP_FLAGS_PSH,
        "CLIENT_TCP_FLAGS_ACK": data.CLIENT_TCP_FLAGS_ACK,
        "CLIENT_TCP_FLAGS_URG": data.CLIENT_TCP_FLAGS_URG,
        "CLIENT_TCP_FLAGS_ECE": data.CLIENT_TCP_FLAGS_ECE,
        "CLIENT_TCP_FLAGS_CWR": data.CLIENT_TCP_FLAGS_CWR,
        "SERVER_TCP_FLAGS_FIN": data.SERVER_TCP_FLAGS_FIN,
        "SERVER_TCP_FLAGS_SYN": data.SERVER_TCP_FLAGS_SYN,
        "SERVER_TCP_FLAGS_RST": data.SERVER_TCP_FLAGS_RST,
        "SERVER_TCP_FLAGS_PSH": data.SERVER_TCP_FLAGS_PSH,
        "SERVER_TCP_FLAGS_ACK": data.SERVER_TCP_FLAGS_ACK,
        "SERVER_TCP_FLAGS_URG": data.SERVER_TCP_FLAGS_URG,
        "SERVER_TCP_FLAGS_ECE": data.SERVER_TCP_FLAGS_ECE,
        "SERVER_TCP_FLAGS_CWR": data.SERVER_TCP_FLAGS_CWR,
        "MIN_TTL": data.MIN_TTL,
        "MAX_TTL": data.MAX_TTL,
        "NUM_PKTS_UP_TO_128_BYTES": data.NUM_PKTS_UP_TO_128_BYTES,
        "NUM_PKTS_128_TO_256_BYTES": data.NUM_PKTS_128_TO_256_BYTES,
        "NUM_PKTS_256_TO_512_BYTES": data.NUM_PKTS_256_TO_512_BYTES,
        "NUM_PKTS_512_TO_1024_BYTES": data.NUM_PKTS_512_TO_1024_BYTES,
        "NUM_PKTS_1024_TO_1514_BYTES": data.NUM_PKTS_1024_TO_1514_BYTES,
    }


def call_azure_endpoint(url: str, key: str, record: dict) -> dict:
    payload = {
        "Inputs": {
            "input1": [record],
        },
        "GlobalParameters": {},
    }

    response = requests.post(
        url=url,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        json=payload,
        timeout=120,
    )

    result = response.json()

    if "error" in result:
        raise RuntimeError(result["error"].get("message", "Azure ML endpoint error"))

    return get_first_output(result)


@router.post("/api/predict")
def predict(data: TrafficData):
    binary_url = os.getenv("AZURE_BINARY_ENDPOINT_URL")
    binary_key = os.getenv("AZURE_BINARY_ENDPOINT_KEY")
    multi_url = os.getenv("AZURE_MULTI_ENDPOINT_URL")
    multi_key = os.getenv("AZURE_MULTI_ENDPOINT_KEY")

    if not binary_url or not binary_key or not multi_url or not multi_key:
        return {
            "is_attack": False,
            "attack_type": "Benign",
            "risk": "LOW",
            "src_ip": data.src_ip,
            "dst_ip": data.dst_ip,
            "error": "Azure ML 환경변수가 설정되지 않았습니다.",
        }

    base_record = build_model_record(data)
    scaled_record = scale_record(base_record)  # 스케일링 적용

    binary_record = {
        **scaled_record,
        "Label": 0,
        "Attack_label": 0,
    }

    try:
        binary_result = call_azure_endpoint(binary_url, binary_key, binary_record)
        print("이진분류 원본 결과:", binary_result) 
        scored_label = binary_result.get("Scored Labels")
        binary_probability = float(binary_result.get("Scored Probabilities", 0))
        is_attack = is_attack_label(scored_label)

        if not is_attack:
            return {
                "is_attack": False,
                "attack_type": "Benign",
                "risk": "LOW",
                "confidence": round(1 - binary_probability, 4),
                "attack_probability": round(binary_probability, 4),
                "src_ip": data.src_ip,
                "dst_ip": data.dst_ip,
            }

        multi_record = {
            **scaled_record,
            "Attack": 0,
            "Attack_label": 0,
        }

        multi_result = call_azure_endpoint(multi_url, multi_key, multi_record)
        multi_label = multi_result.get("Scored Labels")
        multi_probability = float(multi_result.get("Scored Probabilities", binary_probability))

        attack_type = normalize_attack_type(multi_label)

        return {
            "is_attack": True,
            "attack_type": attack_type,
            "risk": "HIGH",
            "confidence": round(multi_probability, 4),
            "attack_probability": round(binary_probability, 4),
            "src_ip": data.src_ip,
            "dst_ip": data.dst_ip,
        }

    except Exception as error:
        return {
            "is_attack": False,
            "attack_type": "Benign",
            "risk": "LOW",
            "src_ip": data.src_ip,
            "dst_ip": data.dst_ip,
            "error": str(error),
        }