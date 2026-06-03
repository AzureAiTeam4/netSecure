import type { EventRow, TabId } from "./data";
import type { EventListFilters } from "./EventList";
import { toneClasses } from "./data";

type Tone = keyof typeof toneClasses;

type SummaryCard = {
  label: string;
  value: number;
  tone: Tone;
  targetTab: TabId;
  filters: EventListFilters;
  badge: string;
};

export default function SummaryGrid({
  eventRows,
  onMoveTab,
}: {
  eventRows: EventRow[];
  onMoveTab?: (tabId: TabId, filters?: EventListFilters) => void;
}) {
  const totalEvents = eventRows.length;
  const attackEvents = eventRows.filter((row) => row[4] !== "Benign").length;
  const normalEvents = eventRows.filter((row) => row[4] === "Benign").length;
  const priorityEvents = eventRows.filter(
    (row) => row[7] === "High" || row[8] === "확인 필요",
  ).length;

  const cards: SummaryCard[] = [
    {
      label: "우선 확인 이벤트",
      value: priorityEvents,
      tone: "orange",
      badge: "우선 검토",
      targetTab: "events",
      filters: {
        kind: "전체",
        risk: "전체",
        attack: "전체",
        category: "전체",
        status: "전체",
        query: "",
        priorityOnly: true,
      },
    },
    {
      label: "공격 이벤트",
      value: attackEvents,
      tone: "red",
      badge: "공격 탐지",
      targetTab: "events",
      filters: {
        kind: "공격",
        risk: "전체",
        attack: "전체",
        category: "전체",
        status: "전체",
        query: "",
      },
    },
    {
      label: "정상 이벤트",
      value: normalEvents,
      tone: "green",
      badge: "정상 분류",
      targetTab: "events",
      filters: {
        kind: "정상",
        risk: "전체",
        attack: "전체",
        category: "전체",
        status: "전체",
        query: "",
      },
    },
    {
      label: "전체 이벤트",
      value: totalEvents,
      tone: "blue",
      badge: "전체 현황",
      targetTab: "events",
      filters: {
        kind: "전체",
        risk: "전체",
        attack: "전체",
        category: "전체",
        status: "전체",
        query: "",
      },
    },
  ];

  return (
    <div className="mb-5 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      {cards.map((card) => {
        const [textTone, bgTone] = toneClasses[card.tone].split(" ");

        return (
          <button
            key={card.label}
            type="button"
            onClick={() => onMoveTab?.(card.targetTab, card.filters)}
            className="rounded-lg border border-slate-200 bg-white p-5 text-left shadow-sm transition hover:-translate-y-0.5 hover:border-slate-300 hover:shadow-md active:translate-y-0"
          >
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className={`text-sm font-semibold ${textTone}`}>
                  {card.label}
                </p>
                <p className="mt-2 text-3xl font-bold text-slate-950">
                  {card.value.toLocaleString()}
                </p>
              </div>

              <span
                className={`rounded-full border px-2.5 py-1 text-xs font-semibold ${toneClasses[card.tone]}`}
              >
                {card.badge}
              </span>
            </div>

          </button>
        );
      })}
    </div>
  );
}