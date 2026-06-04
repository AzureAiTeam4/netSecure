import type { EventRow } from "./data";
import { getEventPriorityScore, getPriorityLabel } from "./eventPriority";
import Panel from "./Panel";
import StatusBadge from "./StatusBadge";

function formatConfidence(confidence: string) {
  const value = Number(confidence);

  if (Number.isNaN(value)) return confidence;
  if (value <= 1) return `${Math.round(value * 100)}%`;

  return `${value.toFixed(0)}%`;
}

function getAttackReason(attackType: string) {
  if (attackType === "Injection") {
    return "데이터 변조나 정보 노출 위험을 우선 확인해야 합니다.";
  }

  if (attackType === "XSS") {
    return "세션 탈취나 악성 스크립트 실행 여부를 확인해야 합니다.";
  }

  if (attackType === "Password") {
    return "인증 로그와 반복 로그인 시도 여부를 확인해야 합니다.";
  }

  if (attackType === "Scanning") {
    return "동일 IP의 반복 접근과 후속 공격 가능성을 확인해야 합니다.";
  }

  if (attackType === "Reconnaissance") {
    return "노출된 서비스와 접근 패턴을 확인해야 합니다.";
  }

  if (attackType === "Benign") {
    return "정상 트래픽이나 반복 패턴 여부를 확인할 수 있습니다.";
  }

  return "추가 검토가 필요한 이벤트입니다.";
}

function getPriorityBadgeClass(label: string) {
  if (label === "최우선") return "border-rose-200 bg-rose-50 text-rose-600";
  if (label === "우선") return "border-amber-200 bg-amber-50 text-amber-700";
  if (label === "검토") return "border-blue-200 bg-blue-50 text-blue-700";

  return "border-slate-200 bg-slate-50 text-slate-600";
}

function MiniMetric({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div className="rounded-md border border-slate-200 bg-white px-3 py-2">
      <p className="text-[11px] font-medium text-slate-500">{label}</p>
      <p className="mt-1 truncate text-sm font-bold text-slate-950">{value}</p>
    </div>
  );
}

export default function ReportTargetSummary({
  event,
  onShowReport,
  showReportButton = true,
}: {
  event?: EventRow;
  onShowReport?: () => void;
  showReportButton?: boolean;
}) {
  if (!event) {
    return (
      <Panel title="분석 대상 요약">
        <div className="grid min-h-[220px] place-items-center rounded-lg border border-dashed border-slate-200 bg-slate-50 text-center">
          <div>
            <p className="text-sm font-semibold text-slate-700">
              분석 대상이 선택되지 않았습니다.
            </p>
            <p className="mt-2 text-xs text-slate-500">
              이벤트 목록에서 AI 리포트를 생성할 이벤트를 선택하세요.
            </p>
          </div>
        </div>
      </Panel>
    );
  }

  const [eventId, , , , attackType, category, confidence, risk, status] = event;

  const priorityScore = getEventPriorityScore(event);
  const priorityLabel = getPriorityLabel(priorityScore);

  return (
    <Panel title="분석 대상 요약">
      <div className="space-y-3">
        <div className="rounded-lg border border-slate-200 bg-slate-50 px-4 py-3">
          <div className="flex items-start justify-between gap-3">
            <div className="min-w-0">
              <p className="text-xs font-medium text-slate-500">선택 이벤트</p>
              <p className="mt-1 truncate text-2xl font-bold text-slate-950">{eventId}</p>
            </div>

            <span
              className={`shrink-0 rounded-full border px-2.5 py-1 text-xs font-semibold ${getPriorityBadgeClass(
                priorityLabel,
              )}`}
            >
              {priorityLabel}
            </span>
          </div>

          <div className="mt-3 flex flex-wrap gap-2">
            <StatusBadge value={risk} />
            <StatusBadge value={status} />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-2">
          <MiniMetric label="공격 유형" value={attackType} />
          <MiniMetric label="카테고리" value={category} />
          <MiniMetric label="신뢰도" value={formatConfidence(confidence)} />
          <MiniMetric label="우선순위" value={`${priorityScore}점`} />
        </div>

        <div className="rounded-md border border-blue-100 bg-blue-50/50 px-3 py-2">
          <p className="text-[11px] font-semibold text-blue-700">우선 검토 이유</p>
          <p className="mt-1 text-xs leading-5 text-slate-600">
            {getAttackReason(attackType)}
          </p>
        </div>

        {showReportButton ? (
          <button
            type="button"
            onClick={onShowReport}
            className="h-10 w-full rounded-md bg-blue-600 text-sm font-semibold text-white shadow-sm shadow-blue-200 transition hover:bg-blue-700 active:scale-[0.99]"
          >
            AI 대응 리포트 확인하기
          </button>
        ) : null}
      </div>
    </Panel>
  );
}