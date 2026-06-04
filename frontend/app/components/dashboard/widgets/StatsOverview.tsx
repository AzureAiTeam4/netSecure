import type { EventRow } from "./data";
import Panel from "./Panel";
import StatusBadge from "./StatusBadge";

function getCountMap(values: string[]) {
  return values.reduce<Record<string, number>>((acc, value) => {
    acc[value] = (acc[value] ?? 0) + 1;
    return acc;
  }, {});
}

function getSortedEntries(counts: Record<string, number>) {
  return Object.entries(counts).sort((a, b) => b[1] - a[1]);
}

function getAverageConfidence(eventRows: EventRow[]) {
  if (eventRows.length === 0) return "0%";

  const sum = eventRows.reduce((acc, row) => {
    const value = Number(row[6]);
    return acc + (Number.isNaN(value) ? 0 : value);
  }, 0);

  const average = sum / eventRows.length;

  if (average <= 1) {
    return `${Math.round(average * 100)}%`;
  }

  return `${Math.round(average)}%`;
}

function getMostFrequentValue(entries: Array<[string, number]>) {
  return entries[0] ?? ["없음", 0];
}

function getPercentage(count: number, total: number) {
  if (total === 0) return "0%";
  return `${Math.round((count / total) * 100)}%`;
}

function getRiskTone(value: string) {
  if (value === "High") {
    return {
      bar: "bg-rose-500",
      text: "text-rose-600",
      bg: "bg-rose-50",
      border: "border-rose-100",
    };
  }

  if (value === "Medium") {
    return {
      bar: "bg-amber-500",
      text: "text-amber-600",
      bg: "bg-amber-50",
      border: "border-amber-100",
    };
  }

  if (value === "Low") {
    return {
      bar: "bg-emerald-500",
      text: "text-emerald-600",
      bg: "bg-emerald-50",
      border: "border-emerald-100",
    };
  }

  return {
    bar: "bg-slate-400",
    text: "text-slate-700",
    bg: "bg-slate-50",
    border: "border-slate-200",
  };
}

function getAttackPriorityText(attackType: string) {
  if (attackType === "Injection" || attackType === "XSS" || attackType === "Password") {
    return "text-slate-950";
  }

  return "text-slate-700";
}

function StatCard({
  label,
  value,
  note,
  emphasis = false,
}: {
  label: string;
  value: string;
  note: string;
  emphasis?: boolean;
}) {
  return (
    <div
      className={`rounded-lg border px-4 py-4 ${
        emphasis ? "border-rose-100 bg-rose-50" : "border-slate-200 bg-slate-50"
      }`}
    >
      <p className="text-xs font-medium text-slate-500">{label}</p>
      <p className={`mt-2 text-xl font-bold ${emphasis ? "text-rose-600" : "text-slate-950"}`}>
        {value}
      </p>
      <p className="mt-2 text-xs text-slate-500">{note}</p>
    </div>
  );
}

function RankedList({
  items,
  total,
  type = "default",
}: {
  items: Array<[string, number]>;
  total: number;
  type?: "default" | "ip";
}) {
  return (
    <div className="divide-y divide-slate-100">
      {items.map(([label, count], index) => (
        <div key={label} className="flex items-center justify-between gap-4 py-3">
          <div className="flex min-w-0 items-center gap-3">
            <span className="grid h-6 w-6 shrink-0 place-items-center rounded-md bg-slate-100 text-xs font-semibold text-slate-500">
              {index + 1}
            </span>

            <div className="min-w-0">
              <p
                className={`truncate text-sm font-semibold ${
                  type === "default" ? getAttackPriorityText(label) : "font-mono text-slate-800"
                }`}
              >
                {label}
              </p>
              <p className="mt-0.5 text-xs text-slate-500">
                {getPercentage(count, total)} 비중
              </p>
            </div>
          </div>

          <p className="shrink-0 text-sm font-bold text-slate-950">
            {count.toLocaleString()}건
          </p>
        </div>
      ))}
    </div>
  );
}

function RiskDistribution({
  items,
  total,
}: {
  items: Array<[string, number]>;
  total: number;
}) {
  return (
    <div className="space-y-4">
      {items.map(([label, count]) => {
        const tone = getRiskTone(label);
        const width = total === 0 ? 0 : Math.max(4, (count / total) * 100);

        return (
          <div key={label} className={`rounded-lg border px-4 py-3 ${tone.bg} ${tone.border}`}>
            <div className="mb-3 flex items-center justify-between">
              <StatusBadge value={label} />
              <div className="text-right">
                <p className={`text-sm font-bold ${tone.text}`}>
                  {count.toLocaleString()}건
                </p>
                <p className="text-xs text-slate-500">{getPercentage(count, total)}</p>
              </div>
            </div>

            <div className="h-2 overflow-hidden rounded-full bg-white/80">
              <div
                className={`h-full rounded-full ${tone.bar}`}
                style={{ width: `${width}%` }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}

export default function StatsOverview({
  expanded = false,
  eventRows,
}: {
  expanded?: boolean;
  eventRows: EventRow[];
}) {
  const attackRows = eventRows.filter((row) => row[4] !== "Benign");
  const highRiskRows = eventRows.filter((row) => row[7] === "High");

  const attackEntries = getSortedEntries(getCountMap(attackRows.map((row) => row[4])));
  const riskEntries = getSortedEntries(getCountMap(eventRows.map((row) => row[7])));
  const highRiskAttackEntries = getSortedEntries(
    getCountMap(highRiskRows.map((row) => row[4])),
  );
  const sourceIpEntries = getSortedEntries(
    getCountMap(attackRows.map((row) => row[2])),
  ).slice(0, 5);

  const [topAttackType, topAttackCount] = getMostFrequentValue(attackEntries);
  const [topSourceIp, topSourceIpCount] = getMostFrequentValue(sourceIpEntries);

  return (
    <div className={expanded ? "space-y-5" : "grid gap-5 xl:grid-cols-3"}>
      <Panel title="통계 요약" action="현재 이벤트 데이터 기준">
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <StatCard
            label="최다 공격 유형"
            value={topAttackType}
            note={`${topAttackCount.toLocaleString()}건 발생`}
          />

          <StatCard
            label="High 위험 이벤트"
            value={`${highRiskRows.length.toLocaleString()}건`}
            note="우선 대응 검토 대상"
            emphasis
          />

          <StatCard
            label="최다 출발지 IP"
            value={topSourceIp}
            note={`${topSourceIpCount.toLocaleString()}건 반복 발생`}
          />

          <StatCard
            label="평균 예측 신뢰도"
            value={getAverageConfidence(eventRows)}
            note="모델 예측 결과 기준"
          />
        </div>
      </Panel>

      <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_380px]">
        <Panel title="공격 유형별 이벤트 수" action={`${attackRows.length.toLocaleString()}건`}>
          <RankedList
            items={attackEntries}
            total={attackRows.length}
          />
        </Panel>

        <Panel title="위험도 분포" action={`${eventRows.length.toLocaleString()}건`}>
          <RiskDistribution
            items={riskEntries}
            total={eventRows.length}
          />
        </Panel>
      </div>

      <div className="grid gap-5 xl:grid-cols-2">
        <Panel title="공격 유형별 High 위험 이벤트" action={`${highRiskRows.length.toLocaleString()}건`}>
          {highRiskAttackEntries.length > 0 ? (
            <RankedList
              items={highRiskAttackEntries}
              total={highRiskRows.length}
            />
          ) : (
            <div className="rounded-lg border border-dashed border-slate-200 bg-slate-50 px-4 py-8 text-center text-sm text-slate-500">
              High 위험도로 분류된 공격 이벤트가 없습니다.
            </div>
          )}
        </Panel>

        <Panel title="상위 출발지 IP Top 5" action="공격 이벤트 기준">
          {sourceIpEntries.length > 0 ? (
            <RankedList
              items={sourceIpEntries}
              total={attackRows.length}
              type="ip"
            />
          ) : (
            <div className="rounded-lg border border-dashed border-slate-200 bg-slate-50 px-4 py-8 text-center text-sm text-slate-500">
              공격 이벤트 기준 출발지 IP가 없습니다.
            </div>
          )}
        </Panel>
      </div>
    </div>
  );
}