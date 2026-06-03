# data_analysis — 전처리 및 EDA 모듈

네트워크 트래픽 데이터 전처리 및 탐색적 분석(EDA)

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

| 단계 | 스크립트 | 내용 |
|------|----------|------|
| 샘플링 | `sampling.ipynb` | 원본 76M → 450만 행 언더샘플링 |
| 클리닝 | `preprocess_01_cleaning.py` | 피처 제거, 클리핑, TCP_FLAGS 비트 분해, Z-score 정규화 |
| 최종 변환 | `preprocess_02_finalize.py` | Azure ML 업로드용 `final_dataset.csv` 생성 |
| 공격 추출 | `prepare_attack_data.py` | 공격 행만 분리 → `attack_only_dataset.csv` |

### 클리닝 세부 내용

| 처리 | 내용 |
|------|------|
| 피처 제거 | IP 주소, 메타정보, 중복·파생 피처 6개 제거 |
| 이상값 클리핑 | `AVG_THROUGHPUT > 1e9` → 1e9 대체 |
| TCP_FLAGS 분해 | 3개 컬럼 → 24개 비트 컬럼 (FIN·SYN·RST·PSH·ACK·URG·ECE·CWR × 3) |
| 정규화 | 수치형 전체 Z-score 정규화 후 ±3 클리핑 |
| 레이블 인코딩 | `Attack` 문자열 → 정수 매핑 (`Attack_label`) |

최종 피처 수: **55개**

## EDA

| 스크립트 | 내용 |
|----------|------|
| `eda_01_raw_distribution.py` | 원본·샘플 데이터 클래스 분포 확인 |
| `eda_02_feature_analysis.py` | 피처별 분포, 결측값, 상관관계 분석 |
| `eda_03_attack_distribution.py` | 공격 유형별 피처 분포 (정규화 값 기준) |
| `eda_04_raw_values.py` | 정규화로 패턴이 불분명한 피처 원본값 재분석 |

## 파일 구조

```
data_analysis/
├── .gitignore
├── README.md
├── sampling.ipynb                  # 샘플링
├── preprocess_01_cleaning.py       # 클리닝 및 정규화
├── preprocess_02_finalize.py       # Azure ML 업로드용 변환
├── prepare_attack_data.py          # 공격 전용 데이터 추출
├── eda_01_raw_distribution.py      # 클래스 분포 확인
├── eda_02_feature_analysis.py      # 피처 분석
├── eda_03_attack_distribution.py   # 공격 유형별 분포 (정규화)
├── eda_04_raw_values.py            # 공격 유형별 분포 (원본값)
├── archive/                        # 실험용 코드 보관 (gitignore)
├── data/                           # 데이터셋 (gitignore)
│   ├── NF-UQ-NIDS-v2.csv
│   ├── sampled_dataset.csv
│   ├── cleaned_dataset.csv
│   ├── final_dataset.csv
│   └── attack_only_dataset.csv
├── figures/                        # 시각화 결과 (gitignore)
├── logs/                           # 실행 로그 (gitignore)
└── analysis_results/               # EDA 분석 결과 (gitignore)
```
