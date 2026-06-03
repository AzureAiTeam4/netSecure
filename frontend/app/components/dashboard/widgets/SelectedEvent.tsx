import type { EventRow } from "./data";
import Panel from "./Panel";

export default function SelectedEvent({ event }: { event?: EventRow }) {
  const selectedEvent = event ?? ["E-0001", "-", "-", "-", "-", "-", "-", "-", "-"];

  return (
    <Panel title="선택한 이벤트 상세 정보" action={selectedEvent[0]}>
      <dl className="grid grid-cols-2 gap-px overflow-hidden rounded-md border border-slate-200 bg-slate-200 text-xs">
        {[
          ["시간", selectedEvent[1]],
          ["출발지 IP", selectedEvent[2]],
          ["목적지 IP", selectedEvent[3]],
          ["프로토콜", "TCP"],
          ["공격 유형", selectedEvent[4]],
          ["신뢰도", `${selectedEvent[6]} (${Math.round(Number(selectedEvent[6]) * 100)}%)`],
          ["위험도", selectedEvent[7]],
          ["상태", selectedEvent[8]],
        ].map(([key, value]) => (
          <div key={key} className="bg-white p-3">
            <dt className="text-slate-500">{key}</dt>
            <dd className="mt-1 font-semibold text-slate-900">{value}</dd>
          </div>
        ))}
      </dl>
    </Panel>
  );
}
