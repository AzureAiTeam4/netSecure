# NIDS Threat Report

네트워크 침입 탐지 시스템(NIDS) 기반 위협 분석 및 보고서 생성 프로젝트

## 전체 구조

| 폴더 | 역할 |
|------|------|
| `frontend/` | 대시보드 UI — Next.js |
| `backend/` | API 서버 — FastAPI, Azure ML 추론 연동, RAG 리포트 모듈 포함(`backend/RAG/`) |
| `data_analysis/` | 데이터 전처리 및 EDA |
| `ML_results/` | Azure ML Designer 모델 학습 결과 |

## 시스템 구성

| 단계 | 담당 |
|------|------|
| UI / 대시보드 | `frontend/` — Next.js |
| 데이터 전처리 / EDA | `data_analysis/` |
| 모델 학습 | Azure ML Designer |
| 추론 API | Azure ML 엔드포인트 (백엔드 연동) |
| 위협 분석 / 보고서 생성 | `backend/RAG/` — Azure OpenAI + Azure AI Search (모듈 구현 완료, `/api/report` 연동 예정) |
