import type { EventRow } from "./data";

const attackPriority: Record<string, number> = {
  Injection: 25,
  XSS: 23,
  Password: 22,
  Scanning: 14,
  Reconnaissance: 12,
  Benign: 0,
};

const riskPriority: Record<string, number> = {
  High: 50,
  Medium: 30,
  Low: 10,
};

const statusPriority: Record<string, number> = {
  "확인 필요": 30,
  "관찰 필요": 15,
  정상: 0,
};

const MAX_PRIORITY_SCORE = 115;

function parseConfidence(confidence: string) {
  const value = Number(confidence);

  if (Number.isNaN(value)) {
    return 0;
  }

  if (value <= 1) {
    return value;
  }

  return value / 100;
}

/**
 * 임시 우선순위 계산 함수
 *
 * 현재는 프론트 더미데이터 기준으로 우선 확인 이벤트를 정렬하기 위해 사용한다.
 * 위험도, 상태, 공격 유형, 신뢰도를 합산한 뒤 100점 만점으로 환산한다.
 *
 * 추후 백엔드/API에서 priority_score를 제공하면 이 함수 내부만 교체하면 된다.
 */
export function getEventPriorityScore(row: EventRow) {
  const attackType = row[4];
  const confidence = row[6];
  const risk = row[7];
  const status = row[8];

  const riskScore = riskPriority[risk] ?? 0;
  const statusScore = statusPriority[status] ?? 0;
  const attackScore = attackPriority[attackType] ?? 0;
  const confidenceScore = Math.round(parseConfidence(confidence) * 10);

  const rawScore = riskScore + statusScore + attackScore + confidenceScore;

  return Math.min(100, Math.round((rawScore / MAX_PRIORITY_SCORE) * 100));
}

export function getPriorityLabel(score: number) {
  if (score >= 85) return "최우선";
  if (score >= 65) return "우선";
  if (score >= 45) return "검토";
  return "일반";
}

export function sortEventsByPriority(eventRows: EventRow[]) {
  return [...eventRows].sort((a, b) => {
    const priorityDiff = getEventPriorityScore(b) - getEventPriorityScore(a);

    if (priorityDiff !== 0) {
      return priorityDiff;
    }

    return new Date(b[1]).getTime() - new Date(a[1]).getTime();
  });
}