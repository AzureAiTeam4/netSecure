import json
from report_generator import generate_security_report
from prompt_builder import LABEL_MAP

SAMPLE_EVENTS = [
    {
        "Attack_label":                  1,  # injection
        "IPV4_SRC_ADDR":           "203.0.113.10",
        "IPV4_DST_ADDR":           "10.0.0.5",
        "L4_SRC_PORT":             54321,
        "L4_DST_PORT":             3306,
        "PROTOCOL":                6,
        "L7_PROTO":                7.0,
        "IN_BYTES":                511,
        "OUT_BYTES":               2163,
        "IN_PKTS":                 5,
        "OUT_PKTS":                5,
        "FLOW_DURATION_MILLISECONDS": 320,
        "MIN_TTL":                 64,
        "MAX_TTL":                 64,
        "TCP_FLAGS_SYN":           1,
        "TCP_FLAGS_ACK":           1,
        "TCP_FLAGS_RST":           0,
        "TCP_FLAGS_FIN":           1,
    },
    {
        "Attack_label":                  5,  # xss
        "IPV4_SRC_ADDR":           "198.51.100.22",
        "IPV4_DST_ADDR":           "10.0.0.5",
        "L4_SRC_PORT":             61234,
        "L4_DST_PORT":             80,
        "PROTOCOL":                6,
        "L7_PROTO":                7.0,
        "IN_BYTES":                68,
        "OUT_BYTES":               100,
        "IN_PKTS":                 1,
        "OUT_PKTS":                1,
        "FLOW_DURATION_MILLISECONDS": 120,
        "MIN_TTL":                 64,
        "MAX_TTL":                 64,
        "TCP_FLAGS_SYN":           0,
        "TCP_FLAGS_ACK":           1,
        "TCP_FLAGS_RST":           0,
        "TCP_FLAGS_FIN":           1,
    },
    {
        "Attack_label":                  2,  # password
        "IPV4_SRC_ADDR":           "192.0.2.55",
        "IPV4_DST_ADDR":           "10.0.0.10",
        "L4_SRC_PORT":             49152,
        "L4_DST_PORT":             22,
        "PROTOCOL":                6,
        "L7_PROTO":                7.0,
        "IN_BYTES":                466,
        "OUT_BYTES":               2142,
        "IN_PKTS":                 6,
        "OUT_PKTS":                6,
        "FLOW_DURATION_MILLISECONDS": 150,
        "MIN_TTL":                 64,
        "MAX_TTL":                 64,
        "TCP_FLAGS_SYN":           1,
        "TCP_FLAGS_ACK":           1,
        "TCP_FLAGS_RST":           0,
        "TCP_FLAGS_FIN":           1,
    },
    {
        "Attack_label":                  4,  # scanning
        "IPV4_SRC_ADDR":           "172.16.0.99",
        "IPV4_DST_ADDR":           "10.0.0.5",
        "L4_SRC_PORT":             43210,
        "L4_DST_PORT":             445,
        "PROTOCOL":                6,
        "L7_PROTO":                0.0,
        "IN_BYTES":                48,
        "OUT_BYTES":               0,
        "IN_PKTS":                 1,
        "OUT_PKTS":                0,
        "FLOW_DURATION_MILLISECONDS": 10,
        "MIN_TTL":                 32,
        "MAX_TTL":                 32,
        "TCP_FLAGS_SYN":           1,
        "TCP_FLAGS_ACK":           0,
        "TCP_FLAGS_RST":           0,
        "TCP_FLAGS_FIN":           0,
    },
    {
        "Attack_label":                  3,  # reconnaissance
        "IPV4_SRC_ADDR":           "10.10.10.5",
        "IPV4_DST_ADDR":           "10.0.0.5",
        "L4_SRC_PORT":             52000,
        "L4_DST_PORT":             443,
        "PROTOCOL":                6,
        "L7_PROTO":                7.0,
        "IN_BYTES":                44,
        "OUT_BYTES":               40,
        "IN_PKTS":                 1,
        "OUT_PKTS":                1,
        "FLOW_DURATION_MILLISECONDS": 50,
        "MIN_TTL":                 32,
        "MAX_TTL":                 32,
        "TCP_FLAGS_SYN":           1,
        "TCP_FLAGS_ACK":           1,
        "TCP_FLAGS_RST":           1,
        "TCP_FLAGS_FIN":           0,
    },
]


def main():
    for event in SAMPLE_EVENTS:
        print(f"\n{'='*60}")
        print(f"[{LABEL_MAP.get(event['Attack_label'])}] {event['IPV4_SRC_ADDR']} → {event['IPV4_DST_ADDR']}:{event['L4_DST_PORT']}")
        print("=" * 60)
        try:
            report = generate_security_report(event)
            print(json.dumps(report, ensure_ascii=False, indent=2))
        except Exception as e:
            print(f"오류 발생: {e}")


if __name__ == "__main__":
    main()
