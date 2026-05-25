# NIDS Threat Report

네트워크 침입 탐지 시스템(NIDS) 구축을 위한 데이터 전처리 및 분류 모델링 프로젝트입니다.

## 목표

2단계 분류 모델링

1. **이진 분류** — 정상(Benign) vs 공격(Attack) 탐지
2. **다중 분류** — 5개 주요 공격 유형 식별

## 데이터셋

- **원본**: [NF-UQ-NIDS-v2](https://www.kaggle.com/datasets/aryashah2k/nfuqnidsv2-network-intrusion-detection-dataset) — 약 76M 행
- **샘플링**: 공격 유형별 60만 개 × 5 + 정상 150만 개 = **총 450만 행**

| 클래스 | 레이블 | 샘플 수 |
|--------|--------|---------|
| Benign | 0 | 1,500,000 |
| Injection | 1 | 600,000 |
| Password | 2 | 600,000 |
| Reconnaissance | 3 | 600,000 |
| Scanning | 4 | 600,000 |
| XSS | 5 | 600,000 |

## 전처리 파이프라인

| 단계 | 내용 |
|------|------|
| 불필요 피처 제거 | IP 주소, 메타정보, 중복/파생 피처 6개 제거 |
| 이상값 클리핑 | AVG_THROUGHPUT > 1e9 → 1e9으로 대체 |
| TCP_FLAGS 비트 분해 | 3개 컬럼 → 24개 비트 컬럼 |
| Z-score 정규화 | 수치형 전체 정규화 후 ±3 클리핑 |
| 레이블 인코딩 | Attack 문자열 → 정수 매핑 |

최종 피처 수: **55개**

## 파일 구조

```
├── sampling.ipynb                  # 원본 데이터 샘플링
├── eda_01_raw_distribution.py      # 원본/샘플 데이터 분포 확인
├── eda_02_feature_analysis.py      # 피처별 분포 및 결측값 분석
├── preprocess_01_cleaning.py       # 데이터 클리닝 및 전처리
├── preprocess_02_finalize.py       # Azure ML용 최종 데이터 생성
├── archive/                        # 실험용 코드 보관
├── data/                           # 데이터 (gitignore)
├── figures/                        # 시각화 결과 (gitignore)
└── logs/                           # 실행 로그 (gitignore)
```

## 모델링

Azure ML Designer에서 진행 예정
