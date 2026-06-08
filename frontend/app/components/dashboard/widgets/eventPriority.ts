import type { EventRow } from "./data";

function getRiskScore(riskLevel: string) {
  if (riskLevel === "High") return 30;
  if (riskLevel === "Medium") return 18;
  if (riskLevel === "Low") return 5;
  return 0;
}

function getAttackTypeScore(attackType: string) {
  const scores: Record<string, number> = {
    Injection: 25,
    XSS: 22,
    Password: 20,
    Reconnaissance: 14,
    Scanning: 12,
    Benign: 0,
  };

  return scores[attackType] ?? 8;
}

function getStatusScore(status: string) {
  if (status === "확인 필요") return 20;
  if (status === "관찰 필요") return 10;
  if (status === "정상") return 0;
  if (status === "조치 완료") return -10;
  return 0;
}

function getConfidenceScore(confidenceText: string) {
  const confidence = Number(confidenceText);

  if (Number.isNaN(confidence)) {
    return 0;
  }

  return Math.round(Math.min(confidence, 1) * 15);
}

function getRecencyScore(timestamp: string, latestTimestamp?: string) {
  if (!timestamp || !latestTimestamp) {
    return 0;
  }

  const eventTime = new Date(timestamp).getTime();
  const latestTime = new Date(latestTimestamp).getTime();

  if (Number.isNaN(eventTime) || Number.isNaN(latestTime)) {
    return 0;
  }

  const diffHours = Math.max(0, (latestTime - eventTime) / (1000 * 60 * 60));

  if (diffHours <= 1) return 10;
  if (diffHours <= 6) return 8;
  if (diffHours <= 24) return 6;
  if (diffHours <= 72) return 4;
  return 1;
}

export function getEventPriorityScore(
  row: EventRow,
  latestTimestamp?: string,
) {
  const attackType = row[4];
  const confidence = row[6];
  const riskLevel = row[7];
  const status = row[8];
  const timestamp = row[1];

  const score =
    getRiskScore(riskLevel) +
    getAttackTypeScore(attackType) +
    getStatusScore(status) +
    getConfidenceScore(confidence) +
    getRecencyScore(timestamp, latestTimestamp);

  // 정상 이벤트는 우선 확인 대상이 아니므로 점수 상한 제한
  if (attackType === "Benign") {
    return Math.min(score, 15);
  }

  return Math.max(0, Math.min(100, Math.round(score)));
}

export function getPriorityLabel(score: number) {
  if (score >= 85) return "최우선";
  if (score >= 65) return "우선";
  if (score >= 40) return "검토";
  return "일반";
}

export function sortEventsByPriority(eventRows: EventRow[]) {
  const latestTimestamp = eventRows
    .map((row) => row[1])
    .sort()
    .at(-1);

  return [...eventRows].sort((a, b) => {
    const scoreA = getEventPriorityScore(a, latestTimestamp);
    const scoreB = getEventPriorityScore(b, latestTimestamp);

    return scoreB - scoreA;
  });
}