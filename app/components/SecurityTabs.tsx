//메인 대시보드 화면 전체 구성

"use client";

import { useMemo, useState } from "react";
import { generateEventRows, navigation, type EventRow, type TabId } from "./dashboard/widgets/data";
import DashboardView from "./dashboard/tabs/DashboardView";
import EventsView from "./dashboard/tabs/EventsView";
import ReportsView from "./dashboard/tabs/ReportsView";
import StatsView from "./dashboard/tabs/StatsView";

type ViewProps = {
  eventRows: EventRow[];
};

const views: Record<TabId, React.ComponentType<ViewProps>> = {
  dashboard: DashboardView,
  events: EventsView,
  reports: ReportsView,
  stats: StatsView,
};

function formatDateTime(date: Date) {
  const pad = (value: number) => String(value).padStart(2, "0");

  return [
    date.getFullYear(),
    pad(date.getMonth() + 1),
    pad(date.getDate()),
  ].join("-") + ` ${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`;
}

function formatDate(date: Date) {
  const pad = (value: number) => String(value).padStart(2, "0");

  return [
    date.getFullYear(),
    pad(date.getMonth() + 1),
    pad(date.getDate()),
  ].join("-");
}

export default function SecurityTabs() {
  const [activeTab, setActiveTab] = useState<TabId>("dashboard");
  const [lastUpdated, setLastUpdated] = useState(() => new Date());
  const title = useMemo(
    () => navigation.find((item) => item.id === activeTab)?.label ?? "대시보드",
    [activeTab],
  );
  const eventRows = useMemo(() => generateEventRows(lastUpdated), [lastUpdated]);
  const rangeStart = useMemo(() => {
    const date = new Date(lastUpdated);
    date.setDate(date.getDate() - 7);
    return date;
  }, [lastUpdated]);
  const ActiveView = views[activeTab];

  const refreshData = () => {
    setLastUpdated(new Date());
  };

  return (
    <div className="flex min-h-screen flex-col bg-[#f5f7fb] text-slate-950 lg:flex-row">
      <aside className="flex w-full shrink-0 flex-col bg-[#050914] text-white shadow-2xl shadow-black/30 lg:w-64">
        <div className="border-b border-white/10 px-6 py-6">
          <div className="flex items-center gap-3">
            <div className="grid h-10 w-10 place-items-center rounded-lg border border-blue-400/50 bg-blue-500/10 text-sm font-bold">
              NS
            </div>
            <div>
              <p className="text-sm font-semibold">네트워크 보안</p>
              <p className="text-xs text-slate-400">이벤트 분석 시스템</p>
            </div>
          </div>
        </div>

        <nav className="grid flex-1 grid-cols-2 gap-2 px-4 py-5 lg:block lg:space-y-2" aria-label="보안 분석 메뉴">
          {navigation.map((item) => {
            const isActive = activeTab === item.id;

            return (
              <button
                key={item.id}
                type="button"
                onClick={() => setActiveTab(item.id)}
                className={[
                  "flex h-11 w-full items-center gap-3 rounded-md px-4 text-left text-sm font-medium transition",
                  "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-400",
                  isActive
                    ? "bg-blue-600 text-white shadow-lg shadow-blue-950/40"
                    : "text-slate-300 hover:bg-white/7 hover:text-white",
                ].join(" ")}
              >
                <span className="grid h-6 w-6 place-items-center rounded border border-white/15 text-[11px]">
                  {item.icon}
                </span>
                {item.label}
              </button>
            );
          })}
        </nav>

        <div className="m-4 rounded-lg border border-white/10 bg-[#091327] p-4 text-xs">
          <p className="text-slate-400">마지막 업데이트</p>
          <p className="mt-2 font-medium text-white">{formatDateTime(lastUpdated)}</p>
          <button
            type="button"
            onClick={refreshData}
            className="mt-4 h-9 w-full rounded-md border border-blue-400/30 bg-blue-500/10 text-blue-100"
          >
            데이터 새로고침
          </button>
        </div>
      </aside>

      <main className="min-w-0 flex-1 p-5 lg:p-8">
        <section className="mx-auto max-w-7xl">
          <header className="mb-5 flex flex-col gap-4 rounded-lg border border-slate-200 bg-white px-5 py-4 shadow-sm md:flex-row md:items-center md:justify-between">
            <div>
              <h1 className="text-2xl font-bold tracking-tight">
                네트워크 보안 이벤트 분석 {title}
              </h1>
              <p className="mt-1 text-sm text-slate-500">
                Scanning, Reconnaissance, XSS, Password, Injection 공격 유형 중심 분석
              </p>
            </div>
            <div className="flex flex-wrap gap-2 text-sm">
              <button className="h-10 rounded-md border border-slate-200 px-4 text-slate-700">
                {formatDate(rangeStart)} ~ {formatDate(lastUpdated)}
              </button>
              <button
                type="button"
                onClick={refreshData}
                className="h-10 rounded-md border border-slate-200 px-4 text-slate-700"
              >
                새로고침
              </button>
            </div>
          </header>

          <ActiveView key={lastUpdated.getTime()} eventRows={eventRows} />
        </section>
      </main>
    </div>
  );
}
