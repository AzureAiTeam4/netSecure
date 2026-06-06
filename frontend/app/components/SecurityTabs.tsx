//메인 대시보드 화면 전체 구성

"use client";

import {
  type ComponentType,
  useEffect,
  useMemo,
  useState,
} from "react";
import { navigation, type EventRow, type TabId } from "./dashboard/widgets/data";
import type { EventListFilters } from "./dashboard/widgets/EventList";
import DashboardView from "./dashboard/tabs/DashboardView";
import EventsView from "./dashboard/tabs/EventsView";
import ReportsView from "./dashboard/tabs/ReportsView";
import StatsView from "./dashboard/tabs/StatsView";

type ViewProps = {
  eventRows: EventRow[];
  onMoveTab?: (tabId: TabId, filters?: EventListFilters) => void;
  eventListFilters?: EventListFilters;
};

type ApiEvent = {
  event_id: string;
  timestamp: string;
  source_ip: string;
  destination_ip: string;
  attack_type: string;
  attack_category: string;
  confidence: number | string;
  risk_level: string;
  status: string;
};

type ApiEventsResponse = {
  data_range?: {
    start?: string;
    end?: string;
  };
  events: ApiEvent[];
};

type DataRange = {
  start: string;
  end: string;
};

const views: Record<TabId, ComponentType<ViewProps>> = {
  dashboard: DashboardView,
  events: EventsView,
  reports: ReportsView,
  stats: StatsView,
};

const defaultEventListFilters: EventListFilters = {
  kind: "전체",
  risk: "전체",
  attack: "전체",
  category: "전체",
  status: "전체",
  query: "",
};

function toDateInputValue(value?: string) {
  if (!value) {
    return "";
  }

  return String(value).slice(0, 10);
}

function formatDateLabel(value?: string) {
  const dateValue = toDateInputValue(value);

  return dateValue || "-";
}

function formatDateTimeLabel(value?: string) {
  if (!value) {
    return "-";
  }

  return String(value).replace("T", " ");
}

function formatCurrentTime(date: Date) {
  const pad = (value: number) => String(value).padStart(2, "0");

  return (
    [
      date.getFullYear(),
      pad(date.getMonth() + 1),
      pad(date.getDate()),
    ].join("-") + ` ${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`
  );
}

function addDays(dateString: string, amount: number) {
  const [year, month, day] = dateString.split("-").map(Number);

  if (!year || !month || !day) {
    return "";
  }

  const date = new Date(year, month - 1, day);
  date.setDate(date.getDate() + amount);

  const pad = (value: number) => String(value).padStart(2, "0");

  return [
    date.getFullYear(),
    pad(date.getMonth() + 1),
    pad(date.getDate()),
  ].join("-");
}

function isDateInRange(timestamp: string, startDate: string, endDate: string) {
  const eventDate = toDateInputValue(timestamp);

  if (!eventDate) {
    return false;
  }

  if (startDate && eventDate < startDate) {
    return false;
  }

  if (endDate && eventDate > endDate) {
    return false;
  }

  return true;
}

function convertApiEventToEventRow(event: ApiEvent): EventRow {
  return [
    String(event.event_id),
    String(event.timestamp),
    String(event.source_ip),
    String(event.destination_ip),
    String(event.attack_type),
    String(event.attack_category),
    Number(event.confidence).toFixed(4),
    String(event.risk_level),
    String(event.status),
  ];
}

export default function SecurityTabs() {
  const [activeTab, setActiveTab] = useState<TabId>("dashboard");
  const [eventListFilters, setEventListFilters] = useState<EventListFilters>(defaultEventListFilters);

  const [allEventRows, setAllEventRows] = useState<EventRow[]>([]);
  const [dataRange, setDataRange] = useState<DataRange | null>(null);

  const [selectedStartDate, setSelectedStartDate] = useState("");
  const [selectedEndDate, setSelectedEndDate] = useState("");

  const [currentRefreshTime, setCurrentRefreshTime] = useState(() => new Date());
  const [isLoadingEvents, setIsLoadingEvents] = useState(true);
  const [eventsError, setEventsError] = useState<string | null>(null);
  const [fetchKey, setFetchKey] = useState(0);

  const title = useMemo(
    () => navigation.find((item) => item.id === activeTab)?.label ?? "대시보드",
    [activeTab],
  );

  const ActiveView = views[activeTab];

  useEffect(() => {
    const API_BASE_URL =
      process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

    async function fetchEvents() {
      try {
        setIsLoadingEvents(true);
        setEventsError(null);

        const response = await fetch(`${API_BASE_URL}/api/events`);

        if (!response.ok) {
          throw new Error("이벤트 데이터를 불러오지 못했습니다.");
        }

        const data: ApiEventsResponse = await response.json();
        const convertedRows = data.events.map(convertApiEventToEventRow);

        const apiStart = data.data_range?.start ?? convertedRows[0]?.[1] ?? "";
        const apiEnd = data.data_range?.end ?? convertedRows[convertedRows.length - 1]?.[1] ?? "";

        const nextDataRange = {
          start: apiStart,
          end: apiEnd,
        };

        setAllEventRows(convertedRows);
        setDataRange(nextDataRange);

        const endDate = toDateInputValue(apiEnd);
        const startDate = endDate ? addDays(endDate, -6) : toDateInputValue(apiStart);

        setSelectedStartDate(startDate);
        setSelectedEndDate(endDate);
      } catch (error) {
        console.error(error);
        setEventsError("이벤트 데이터를 불러오지 못했습니다.");
      } finally {
        setIsLoadingEvents(false);
      }
    }

    fetchEvents();
  }, [fetchKey]);

  const filteredEventRows = useMemo(() => {
    if (!selectedStartDate && !selectedEndDate) {
      return allEventRows;
    }

    return allEventRows.filter((eventRow) =>
      isDateInRange(eventRow[1], selectedStartDate, selectedEndDate),
    );
  }, [allEventRows, selectedStartDate, selectedEndDate]);

  const refreshCurrentTime = () => {
    setCurrentRefreshTime(new Date());
  };

  const resetToRecentWeek = () => {
    const dataEndDate = toDateInputValue(dataRange?.end);

    if (!dataEndDate) {
      setFetchKey((current) => current + 1);
      return;
    }

    setSelectedEndDate(dataEndDate);
    setSelectedStartDate(addDays(dataEndDate, -6));
    setCurrentRefreshTime(new Date());
  };

  function moveTab(tabId: TabId, filters?: EventListFilters) {
    if (filters) {
      setEventListFilters(filters);
    }

    setActiveTab(tabId);
  }

  function handleNavigationClick(tabId: TabId) {
    if (tabId === "events") {
      setEventListFilters(defaultEventListFilters);
    }

    setActiveTab(tabId);
  }

  return (
    <div className="flex h-screen flex-col overflow-hidden bg-[#f5f7fb] text-slate-950 lg:flex-row">
      <aside className="flex w-full shrink-0 flex-col bg-[#050914] text-white shadow-2xl shadow-black/30 lg:h-screen lg:w-64">
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
                onClick={() => handleNavigationClick(item.id)}
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
          <p className="text-slate-400">마지막 새로고침</p>
          <p className="mt-2 font-medium text-white">
            {formatCurrentTime(currentRefreshTime)}
          </p>
          <button
            type="button"
            onClick={refreshCurrentTime}
            className="mt-4 h-9 w-full rounded-md border border-blue-400/30 bg-blue-500/10 text-blue-100 transition hover:border-blue-300/50 hover:bg-blue-500/20 hover:text-white active:bg-blue-500/30"
          >
            현재 시간 새로고침
          </button>
        </div>
      </aside>

      <main className="min-h-0 min-w-0 flex-1 overflow-y-auto p-5 lg:h-screen lg:p-8">
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

            <div className="flex flex-wrap items-center gap-2 text-sm">
              <label className="flex min-h-10 items-center gap-2 rounded-md border border-slate-200 px-3 text-slate-700">
                <span className="text-xs font-medium text-slate-500">조회 시작일</span>
                <input
                  type="date"
                  value={selectedStartDate}
                  min={formatDateLabel(dataRange?.start)}
                  max={selectedEndDate || formatDateLabel(dataRange?.end)}
                  onChange={(event) => setSelectedStartDate(event.target.value)}
                  className="h-8 bg-transparent text-sm font-medium text-slate-800 outline-none"
                />
              </label>

              <label className="flex min-h-10 items-center gap-2 rounded-md border border-slate-200 px-3 text-slate-700">
                <span className="text-xs font-medium text-slate-500">조회 종료일</span>
                <input
                  type="date"
                  value={selectedEndDate}
                  min={selectedStartDate || formatDateLabel(dataRange?.start)}
                  max={formatDateLabel(dataRange?.end)}
                  onChange={(event) => setSelectedEndDate(event.target.value)}
                  className="h-8 bg-transparent text-sm font-medium text-slate-800 outline-none"
                />
              </label>

              <div className="flex h-10 items-center rounded-md border border-slate-200 px-4 text-slate-700">
                {selectedStartDate || "-"} ~ {selectedEndDate || "-"}
              </div>

              <button
                type="button"
                onClick={resetToRecentWeek}
                className="h-10 rounded-md border border-slate-200 px-4 text-slate-700 transition hover:border-slate-300 hover:bg-slate-50 hover:text-slate-900 active:bg-slate-100"
              >
                최근 1주일
              </button>
            </div>
          </header>

          {isLoadingEvents ? (
            <div className="rounded-lg border border-slate-200 bg-white p-6 text-sm text-slate-500 shadow-sm">
              이벤트 데이터를 불러오는 중입니다.
            </div>
          ) : eventsError ? (
            <div className="rounded-lg border border-red-200 bg-red-50 p-6 text-sm text-red-600 shadow-sm">
              {eventsError}
            </div>
          ) : (
            <ActiveView
              key={`${activeTab}-${selectedStartDate}-${selectedEndDate}`}
              eventRows={filteredEventRows}
              onMoveTab={moveTab}
              eventListFilters={eventListFilters}
            />
          )}
        </section>
      </main>
    </div>
  );
}