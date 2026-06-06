from fastapi import APIRouter
from pydantic import BaseModel
import requests
import os
from dotenv import load_dotenv  # .env 파일 읽어오는 패키지

load_dotenv()  # .env 파일 로드

router = APIRouter()

# 프론트엔드에서 보내는 트래픽 데이터 형식
class TrafficData(BaseModel):
    src_ip: str = ""              # 출발지 IP (모델 입력 제외)
    dst_ip: str = ""              # 목적지 IP (모델 입력 제외)
    L4_SRC_PORT: float = 0       # 출발지 포트
    L4_DST_PORT: float = 0       # 목적지 포트
    PROTOCOL: float = 0          # 전송 계층 프로토콜 (TCP, UDP, ICMP)
    L7_PROTO: float = 0          # 응용 계층 프로토콜 (HTTP, DNS, FTP)
    IN_BYTES: float = 0          # 수신 바이트
    IN_PKTS: float = 0           # 수신 패킷 수
    OUT_BYTES: float = 0         # 송신 바이트
    OUT_PKTS: float = 0          # 송신 패킷 수
    FLOW_DURATION_MILLISECONDS: float = 0  # 연결 지속 시간
    DURATION_IN: float = 0       # 수신 지속 시간
    DURATION_OUT: float = 0      # 송신 지속 시간
    TCP_FLAGS: float = 0         # TCP 플래그
    CLIENT_TCP_FLAGS: float = 0  # 클라이언트 TCP 플래그
    SERVER_TCP_FLAGS: float = 0  # 서버 TCP 플래그
    TCP_WIN_MAX_IN: float = 0    # 최대 수신 윈도우 크기
    TCP_WIN_MAX_OUT: float = 0   # 최대 송신 윈도우 크기
    LONGEST_FLOW_PKT: float = 0  # 가장 긴 패킷 크기
    SHORTEST_FLOW_PKT: float = 0 # 가장 짧은 패킷 크기
    MIN_IP_PKT_LEN: float = 0    # 최소 IP 패킷 길이
    MAX_IP_PKT_LEN: float = 0    # 최대 IP 패킷 길이
    SRC_TO_DST_AVG_THROUGHPUT: float = 0  # 출발지→목적지 평균 처리량
    DST_TO_SRC_AVG_THROUGHPUT: float = 0  # 목적지→출발지 평균 처리량
    RETRANSMITTED_IN_BYTES: float = 0     # 재전송 수신 바이트
    RETRANSMITTED_IN_PKTS: float = 0      # 재전송 수신 패킷
    RETRANSMITTED_OUT_BYTES: float = 0    # 재전송 송신 바이트
    RETRANSMITTED_OUT_PKTS: float = 0     # 재전송 송신 패킷
    # TCP FLAGS 세부 (분리된 버전)
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

# POST /api/predict 요청이 오면 실행
# 이진분류 → 공격이면 다중분류 순서로 진행
@router.post("/api/predict")
def predict(data: TrafficData):

    # .env에서 URL이랑 키 가져오기
    BINARY_URL = os.getenv("AZURE_BINARY_ENDPOINT_URL")
    BINARY_KEY = os.getenv("AZURE_BINARY_ENDPOINT_KEY")
    MULTI_URL = os.getenv("AZURE_MULTI_ENDPOINT_URL")
    MULTI_KEY = os.getenv("AZURE_MULTI_ENDPOINT_KEY")

    input_data = {
        "Inputs": {
            "input1": [{
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
                "Label": 0,
                "Attack_label": 0,
                
                
            }]
        },
        "GlobalParameters": {}
    }

    # 1단계: 이진분류 (공격인지 정상인지)
    binary_response = requests.post(
        url=BINARY_URL,
        headers={"Authorization": f"Bearer {BINARY_KEY}"},
        json=input_data
    )
    binary_result = binary_response.json()
    print("이진분류 원본 결과:", binary_result)

    # 에러 체크
    if "error" in binary_result:
        return {"is_attack": False, "attack_type": "Benign", "risk": "LOW", "src_ip": data.src_ip, "dst_ip": data.dst_ip}

    scored_label = binary_result["Results"]["WebServiceOutput1"][0]["Scored Labels"]
    is_attack = str(scored_label) == "1" or float(scored_label) == 1.0  # 이렇게 수정
    '''
    binary_result = binary_response.json()
    print("이진분류 원본 결과:", binary_result)

    # Azure ML Designer 응답 형식: {"Results": {"output1": [{"Scored Labels": "0or1", ...}]}}
    scored_label = binary_result["Results"]["output1"][0]["Scored Labels"]
    is_attack = str(scored_label) == "1"
    '''

    # 정상이면 바로 반환
    if not is_attack:
        return {
            "is_attack": False,
            "attack_type": "Benign",
            "risk": "LOW",
            "src_ip": data.src_ip,
            "dst_ip": data.dst_ip
        }
    
    # 2단계: 다중분류용 데이터
    multi_input_data = {
        "Inputs": {
            "input1": [{
                **input_data["Inputs"]["input1"][0],
                "Attack": "Password",
                "Attack_label": 0
            }]
        },
        "GlobalParameters": {}
    }
    multi_input_data["Inputs"]["input1"][0].pop("Label", None)
 

    print("===== 다중분류 입력 =====")
    print(multi_input_data)

    # 2단계: 공격이면 다중분류 (공격 유형 분류)
    multi_response = requests.post(
        url=MULTI_URL,
        headers={"Authorization": f"Bearer {MULTI_KEY}"},
        json=multi_input_data  # multi_input_data 사용
    )
    multi_result = multi_response.json()
    print("===== 다중분류 결과 =====")
    print(multi_result)

    if "error" in multi_result:
        return {
            "is_attack": True,
            "attack_type": "Unknown",
            "risk": "HIGH",
            "azure_error": multi_result["error"]["message"]
        }

    attack_map = {
    1: "Injection",
    2: "Password",
    3: "Reconnaissance",
    4: "Scanning",
    5: "XSS"
}

    pred = int(float(multi_result["Results"]["WebServiceOutput0"][0]["Scored Labels"]))

    attack_type = attack_map.get(pred, "Unknown")


    return {
        "is_attack": True,
        "attack_type": attack_type,
        "risk": "HIGH",
        "src_ip": data.src_ip,
        "dst_ip": data.dst_ip
    }