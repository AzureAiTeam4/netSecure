import type { EventRow, TabId } from "./data";
import type { EventListFilters } from "./EventList";
import Panel from "./Panel";
import StatusBadge from "./StatusBadge";

function getMostFrequentAttack(eventRows: EventRow[]) {
  const attackRows = eventRows.filter((row) => row[4] !== "Benign");

  const counts = attackRows.reduce<Record<string, number>>((acc, row) => {
    const attackType = row[4] || "Unknown";
    acc[attackType] = (acc[attackType] ?? 0) + 1;
    return acc;
  }, {});

  const [attackType = "없음", count = 0] =
    Object.entries(counts).sort((a, b) => b[1] - a[1])[0] ?? [];

  return { attackType, count };
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

export default function OperationSummary({
  eventRows,
  onMoveTab,
}: {
  eventRows: EventRow[];
  onMoveTab?: (tabId: TabId, filters?: EventListFilters) => void;
}) {
  const needCheckEvents = eventRows.filter((row) => row[8] === "확인 필요").length;
  const highRiskEvents = eventRows.filter((row) => row[7] === "High").length;
  const { attackType, count } = getMostFrequentAttack(eventRows);
  const averageConfidence = getAverageConfidence(eventRows);

  const hasPriorityEvents = highRiskEvents > 0 || needCheckEvents > 0;

  const highRiskFilters: EventListFilters = {
    kind: "전체",
    risk: "High",
    attack: "전체",
    category: "전체",
    status: "전체",
    query: "",
  };

  const needCheckFilters: EventListFilters = {
    kind: "전체",
    risk: "전체",
    attack: "전체",
    category: "전체",
    status: "확인 필요",
    query: "",
  };

  return (
    <Panel title="현재 보안 상태 판단">
      <div className="grid gap-4 lg:grid-cols-[minmax(0,1.2fr)_minmax(320px,0.8fr)]">
        <div className="rounded-lg border border-slate-200 bg-slate-50 px-5 py-5">
          <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
            <div>
              <p className="text-sm font-semibold text-slate-800">
                {hasPriorityEvents
                  ? "우선 확인 대상이 존재합니다."
                  : "현재 우선 확인 대상은 제한적입니다."}
              </p>

              <p className="mt-2 text-sm leading-6 text-slate-600">
                High 위험도와 확인 필요 상태의 이벤트를 먼저 검토한 뒤,
                AI 리포트 탭에서 개별 이벤트의 위험 원인과 대응 방안을 확인하는 흐름이 적합합니다.
              </p>
            </div>

            <div className="flex shrink-0 flex-wrap gap-2">
              <StatusBadge value={hasPriorityEvents ? "High" : "Low"} />
              <StatusBadge value={needCheckEvents > 0 ? "확인 필요" : "정상"} />
            </div>
          </div>

          <div className="mt-5 grid gap-3 md:grid-cols-3">
            <div className="rounded-md border border-slate-200 bg-white px-4 py-3">
              <p className="text-xs font-medium text-slate-500">최다 공격 유형</p>
              <p className="mt-1 text-lg font-bold text-slate-950">{attackType}</p>
              <p className="mt-1 text-xs text-slate-500">{count.toLocaleString()}건 발생</p>
            </div>

            <div className="rounded-md border border-slate-200 bg-white px-4 py-3">
              <p className="text-xs font-medium text-slate-500">평균 예측 신뢰도</p>
              <p className="mt-1 text-lg font-bold text-slate-950">{averageConfidence}</p>
              <p className="mt-1 text-xs text-slate-500">모델 예측 결과 기준</p>
            </div>

            <div className="rounded-md border border-slate-200 bg-white px-4 py-3">
              <p className="text-xs font-medium text-slate-500">우선 대응 권장 유형</p>
              <p className="mt-1 text-lg font-bold text-slate-950">Injection / XSS / Password</p>
              <p className="mt-1 text-xs text-slate-500">직접 피해 가능성 우선</p>
            </div>
          </div>
        </div>

        <div className="rounded-lg border border-blue-100 bg-blue-50/50 px-5 py-5">
          <p className="text-sm font-semibold text-blue-700">다음 행동</p>

          <div className="mt-4 space-y-2 text-sm leading-6 text-slate-700">
            <p>1. 우선 확인 이벤트에서 위험도와 공격 유형을 확인합니다.</p>
            <p>2. 필요한 이벤트를 선택해 AI 대응 리포트를 확인합니다.</p>
            <p>3. 대응 방안에 따라 로그 점검, 차단, 추가 모니터링을 진행합니다.</p>
          </div>

          <div className="mt-5 flex flex-col gap-2">
            <button
              type="button"
              onClick={() => onMoveTab?.("events", highRiskFilters)}
              className="h-10 rounded-md border border-rose-200 bg-white px-4 text-sm font-medium text-rose-600 transition hover:border-rose-300 hover:bg-rose-50"
            >
              High 위험 이벤트 보기
            </button>

            <button
              type="button"
              onClick={() => onMoveTab?.("events", needCheckFilters)}
              className="h-10 rounded-md border border-slate-200 bg-white px-4 text-sm font-medium text-slate-700 transition hover:border-slate-300 hover:bg-slate-50"
            >
              확인 필요 이벤트 보기
            </button>

            <button
              type="button"
              onClick={() => onMoveTab?.("reports", highRiskFilters)}
              className="h-10 rounded-md bg-blue-600 px-4 text-sm font-semibold text-white shadow-sm shadow-blue-200 transition hover:bg-blue-700 active:scale-[0.99]"
            >
              AI 리포트에서 분석하기
            </button>
          </div>
        </div>
      </div>
    </Panel>
  );
}