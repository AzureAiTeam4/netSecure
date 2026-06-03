//통계 자료 3개

import { attackBars } from "./data";
import Panel from "./Panel";

export default function StatsOverview({ expanded = false }: { expanded?: boolean }) {
  return (
    <section
      className={`grid gap-5 ${
        expanded
          ? "xl:grid-cols-3"
          : "xl:grid-cols-[minmax(420px,1.4fr)_minmax(280px,1fr)_minmax(280px,1fr)]"
      }`}
    >
      <div>
        <Panel title="공격 유형별 이벤트 수">
          <div className="flex h-64 items-end gap-2 px-1 pb-3 pt-4 sm:gap-3">
            {attackBars.map(([label, value, color]) => (
              <div key={label} className="flex h-full min-w-0 flex-1 flex-col justify-end gap-2 text-center">
                <div className="text-xs font-semibold text-slate-600">{value}</div>
                <div className={`${color} mx-auto w-full max-w-10 rounded-t-md sm:max-w-12`} style={{ height: `${value / 8}px` }} />
                <div className="min-h-8 break-words text-[11px] text-slate-500 sm:text-xs">{label}</div>
              </div>
            ))}
          </div>
        </Panel>
      </div>
      <Panel title="공격 카테고리별 비율">
        <DonutChart
          gradient="#2563eb 0 37%, #10b981 37% 69%, #f59e0b 69% 100%"
          segments={[
            ["웹 공격", "37.3%", "bg-blue-500"],
            ["탐색 공격", "32.0%", "bg-emerald-500"],
            ["인증 공격", "30.7%", "bg-amber-400"],
          ]}
        />
      </Panel>
      <Panel title="위험도별 이벤트 비율">
        <DonutChart
          gradient="#ef4444 0 27%, #fb923c 27% 67%, #10b981 67% 100%"
          segments={[
            ["High", "27.3%", "bg-red-500"],
            ["Medium", "39.3%", "bg-orange-400"],
            ["Low", "33.3%", "bg-emerald-500"],
          ]}
        />
      </Panel>
    </section>
  );
}

function DonutChart({
  gradient,
  segments,
}: {
  gradient: string;
  segments: Array<[string, string, string]>;
}) {
  return (
    <div className="flex min-h-64 items-center justify-center gap-8">
      <div className="h-36 w-36 rounded-full p-8" style={{ background: `conic-gradient(${gradient})` }}>
        <div className="h-full w-full rounded-full bg-white" />
      </div>
      <div className="space-y-3 text-sm">
        {segments.map(([label, value, color]) => (
          <div key={label} className="flex items-center gap-3">
            <span className={`h-3 w-3 rounded-full ${color}`} />
            <span className="w-20 text-slate-600">{label}</span>
            <span className="font-semibold">{value}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
