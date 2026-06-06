from fastapi import APIRouter

router = APIRouter()


@router.get("/api/stats")
def get_stats():
    return {
        "total_events": 10,
        "attack_count": 8,
        "normal_count": 2,
        "priority_count": 4,
        "risk_distribution": {
            "High": 4,
            "Medium": 4,
            "Low": 2,
        },
        "attack_types": {
            "Injection": 2,
            "XSS": 1,
            "Password": 2,
            "Scanning": 2,
            "Reconnaissance": 1,
        },
        "top_source_ips": {
            "172.16.0.45": 2,
            "203.0.113.15": 2,
            "192.168.1.100": 1,
            "192.168.1.200": 1,
            "198.51.100.22": 1,
        },
    }