# 26-1 인공지능산업체특강 프로젝트

[![code](https://img.shields.io/badge/Code-Python%20%7C%20TypeScript-blue)]()
[![data](https://img.shields.io/badge/Data-NF--UQ--NIDS--v2-blueviolet)](https://www.kaggle.com/datasets/aryashah2k/nfuqnidsv2-network-intrusion-detection-dataset)
[![cloud](https://img.shields.io/badge/Cloud-Azure-0078D4)]()
[![member](https://img.shields.io/badge/Project-Member-brightgreen)](#-developer)

> **NIDS Threat Report** — 네트워크 침입 탐지 시스템(NIDS) 기반 위협 분석 및 보고서 생성 프로젝트

![NIDS Threat Report](https://github.com/user-attachments/assets/d99cebcf-0d1a-4900-bf29-4c5a678cb173)

## 📖 Description

네트워크 트래픽을 분석해 침입을 탐지하고, 탐지된 위협에 대해 AI가 작성한 보안 리포트를 제공하는 프로젝트

NF-UQ-NIDS-v2 데이터셋을 전처리·학습하여 Azure ML 기반 분류 모델을 구축하고, 탐지된 공격 이벤트는 RAG(Azure AI Search + GPT-4o)를 통해 원인·영향·대응 방안을 포함한 리포트로 자동 생성됩니다.

## ⭐ Main Feature

### 침입 탐지 (이진 → 다중 2단계 분류)
- Azure ML Designer로 학습한 이진 분류 모델로 정상/공격 1차 판별
- 공격으로 판별된 트래픽은 다중 분류 모델로 5종 공격 유형(Injection, Password, Reconnaissance, Scanning, XSS) 분류

### 위협 탐지 대시보드
- 탐지 이벤트 목록, 통계, 위험 이벤트를 한눈에 확인하는 대시보드
- 날짜별 이벤트 샘플링 및 위험도(Risk) 기반 우선순위 표시

### AI 보안 리포트 자동 생성
- Azure AI Search + GPT-4o 기반 RAG로 공격 유형별 원인/영향/대응 방안 리포트 생성
- 정상(Benign) 트래픽은 RAG 호출 없이 고정 응답 반환

### 데이터 전처리 및 EDA
- 원본 76M 행(NF-UQ-NIDS-v2) → 클래스 균형 샘플링, 클리닝, Z-score 정규화
- 인접 플로우(과거1/과거2) 결합을 통한 시계열 정보 보완 실험

## 💻 Getting Started

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Backend
```bash
cd backend
pip install fastapi uvicorn pandas python-dotenv requests
pip install -r RAG/requirements.txt
uvicorn main:app --reload
```

## 📁 Project Structure

```
network_detection
├── frontend/        # 대시보드 UI (Next.js + TypeScript + Tailwind CSS)
├── backend/         # API 서버 (FastAPI) + RAG 보안 리포트 모듈
│   └── RAG/         # Azure AI Search + GPT-4o 기반 리포트 생성
├── data_analysis/   # 데이터 전처리 및 EDA (NF-UQ-NIDS-v2)
└── ML_results/      # Azure ML Designer 모델 학습 결과
```

## 👨‍💻 Role & Contribution

**AI** (@miji0, @yeonjaeae)
- 데이터 전처리 및 EDA (NF-UQ-NIDS-v2)
- Azure ML Designer 모델 학습 (이진 / 다중 분류)
- RAG 기반 보안 리포트 생성 모듈 구축 (Azure AI Search + GPT-4o)

**Backend** (@yeonjaeae)
- FastAPI 서버 구축 및 전체 API 연동 (`/api/events`, `/api/stats`, `/api/predict`, `/api/report`)
- Azure ML 추론 모델 및 RAG 모듈을 API로 연결

**Frontend** (@jiwonnee, @nonopenah)
- 대시보드 UI 개발 (Next.js + TypeScript + Tailwind CSS)
- 탐지 이벤트 시각화 및 AI 보안 리포트 화면 구현

## 👨‍👩‍👧‍👦 Developer
* **김나희** ([nonopenah](https://github.com/nonopenah))
* **김미지** ([miji0](https://github.com/miji0))
* **김연재** ([yeonjaeae](https://github.com/yeonjaeae))
* **신지원** ([jiwonnee](https://github.com/jiwonnee))
