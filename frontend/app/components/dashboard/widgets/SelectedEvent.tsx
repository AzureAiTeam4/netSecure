import type { EventRow } from "./data";
import Panel from "./Panel";
import StatusBadge from "./StatusBadge";

function formatConfidence(confidence: string) {
  const value = Number(confidence);

  if (Number.isNaN(value)) {
    return confidence;
  }

  if (value <= 1) {
    return `${value.toFixed(2)} · ${Math.round(value * 100)}%`;
  }

  return `${value.toFixed(0)}%`;
}

function getAttackTone(attackType: string) {
  if (attackType === "Benign") {
    return "text-emerald-700";
  }

  if (attackType === "Injection" || attackType === "XSS") {
    return "text-rose-600";
  }

  if (attackType === "Scanning" || attackType === "Reconnaissance") {
    return "text-amber-600";
  }

  if (attackType === "Password") {
    return "text-violet-600";
  }

  return "text-slate-900";
}

function InfoRow({
  label,
  value,
  valueClassName = "",
}: {
  label: string;
  value: string;
  valueClassName?: string;
}) {
  return (
    <div className="flex items-center justify-between gap-4 border-b border-slate-100 py-3 last:border-b-0">
      <span className="shrink-0 text-xs font-medium text-slate-500">{label}</span>
      <span className={`text-right text-sm font-semibold text-slate-900 ${valueClassName}`}>
        {value}
      </span>
    </div>
  );
}

export default function SelectedEvent({ event }: { event?: EventRow }) {
  if (!event) {
    return (
      <Panel title="선택한 이벤트 상세 정보" action="이벤트 선택 필요" className="h-full">
        <div className="grid min-h-[320px] place-items-center rounded-lg border border-dashed border-slate-200 bg-slate-50 text-center">
          <div>
            <p className="text-sm font-semibold text-slate-700">선택된 이벤트가 없습니다.</p>
            <p className="mt-2 text-sm text-slate-500">
              이벤트 목록에서 분석할 이벤트를 선택하세요.
            </p>
          </div>
        </div>
      </Panel>
    );
  }

  const [eventId, time, sourceIp, destinationIp, attackType, category, confidence, risk, status] =
    event;

  return (
    <Panel title="선택한 이벤트 상세 정보" className="h-full">
      <div className="flex h-full flex-col">
        <div className="rounded-lg border border-slate-200 bg-slate-50 px-4 py-4">
          <div className="flex items-start justify-between gap-3">
            <div>
              <p className="text-xs font-medium text-slate-500">선택 이벤트</p>
              <p className="mt-1 text-xl font-bold text-slate-950">{eventId}</p>
            </div>

            <div className="flex flex-col items-end gap-2">
              <StatusBadge value={risk} />
              <StatusBadge value={status} />
            </div>
          </div>
        </div>

        <div className="mt-4 rounded-lg border border-slate-200 bg-white px-4">
          <InfoRow label="시간" value={time} />
          <InfoRow label="출발지 IP" value={sourceIp} valueClassName="font-mono" />
          <InfoRow label="목적지 IP" value={destinationIp} valueClassName="font-mono" />
          <InfoRow label="프로토콜" value="TCP" />
          <InfoRow
            label="공격 유형"
            value={attackType}
            valueClassName={getAttackTone(attackType)}
          />
          <InfoRow label="카테고리" value={category} />
          <InfoRow label="신뢰도" value={formatConfidence(confidence)} />
        </div>
      </div>
    </Panel>
  );
}