# netSecure — 네트워크 보안 이벤트 분석 대시보드

인공지능산업체특강 4조 프로젝트 프론트엔드 (Next.js + TypeScript + Tailwind CSS)

백엔드(`/api/events`, `/api/stats`, `/api/predict`, `/api/report`)에서 받은 탐지 이벤트를 대시보드로 시각화하고, 이벤트별 AI 보안 리포트를 보여준다.

## 구성

| 영역 | 설명 |
|------|------|
| `app/components/SecurityTabs.tsx` | 대시보드 전체 화면 구성, 탭 전환, 백엔드 `/api/events` 연동 |
| `app/components/dashboard/tabs/` | 탭별 화면 — `DashboardView`, `EventsView`, `ReportsView`, `StatsView` |
| `app/components/dashboard/widgets/` | 공용 위젯 — 이벤트 목록, 통계 카드, AI 리포트(`AiReport`), 위험 이벤트 등 |

## 실행

```bash
npm install
npm run dev
```
