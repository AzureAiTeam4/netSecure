# NIDS Threat Report

네트워크 침입 탐지 시스템(NIDS) 기반 위협 분석 및 보고서 생성 프로젝트

## 전체 구조

| 폴더 | 역할 |
|------|------|
| `frontend/` | |
| `backend/` | |
| `data_analysis/` | |
| `RAG/` | |

## 시스템 구성

| 단계 | 담당 |
|------|------|
| 데이터 전처리 / EDA | `data_analysis/` |
| 모델 학습 | Azure ML Designer |
| 추론 API | Azure ML 엔드포인트 (백엔드 연동) |
| 위협 분석 / 보고서 생성 | `RAG/` — Azure OpenAI + Azure AI Search |
