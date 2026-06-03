//모든 탭 상단에 들어가는 요약카드 묶음 컨포넌트

import { summaryCards, toneClasses } from "./data";

export default function SummaryGrid() {
  return (
    <div className="mb-5 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      {summaryCards.map((card) => (
        <article key={card.label} className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <div className="flex items-start justify-between gap-3">
            <div>
              <p className={`text-sm font-semibold ${toneClasses[card.tone].split(" ")[0]}`}>
                {card.label}
              </p>
              <p className="mt-2 text-3xl font-bold">{card.value}</p>
            </div>
            <span className={`grid h-11 w-11 place-items-center rounded-full border text-sm font-bold ${toneClasses[card.tone]}`}>
              {card.label.slice(0, 1)}
            </span>
          </div>
          <div className="mt-4 flex items-center gap-2 text-xs">
            <span className={card.change.startsWith("+") ? "text-red-500" : "text-emerald-600"}>
              {card.change}
            </span>
            <span className="text-slate-500">{card.note}</span>
          </div>
          <div className="mt-4 flex h-8 items-end gap-1">
            {[20, 26, 18, 30, 24, 35, 28, 38].map((height, index) => (
              <span
                key={index}
                className={`w-full rounded-sm ${toneClasses[card.tone].split(" ")[1]}`}
                style={{ height }}
              />
            ))}
          </div>
        </article>
      ))}
    </div>
  );
}
