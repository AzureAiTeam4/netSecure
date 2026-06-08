"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import AiReport, { type AiReportResponse } from "../widgets/AiReport";
import type { EventRow, TabId } from "../widgets/data";
import EventList, { type EventListFilters } from "../widgets/EventList";
import ReportTargetSummary from "../widgets/ReportTargetSummary";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

function matchesFilters(row: EventRow, filters?: EventListFilters) {
  if (!filters) return true;

  const matchesKind =
    !filters.kind ||
    filters.kind === "전체" ||
    (filters.kind === "공격" && row[4] !== "Benign") ||
    (filters.kind === "정상" && row[4] === "Benign");

  const matchesRisk =
    !filters.risk || filters.risk === "전체" || row[7] === filters.risk;

  const matchesAttack =
    !filters.attack || filters.attack === "전체" || row[4] === filters.attack;

  const matchesCategory =
    !filters.category || filters.category === "전체" || row[5] === filters.category;

  const matchesStatus =
    !filters.status || filters.status === "전체" || row[8] === filters.status;

  const matchesPriority =
    !filters.priorityOnly || row[7] === "High" || row[8] === "확인 필요";

  const keyword = filters.query?.trim().toLowerCase() ?? "";

  const matchesKeyword =
    keyword.length === 0 ||
    row[0].toLowerCase().includes(keyword) ||
    row[2].toLowerCase().includes(keyword) ||
    row[3].toLowerCase().includes(keyword) ||
    row[4].toLowerCase().includes(keyword) ||
    row[5].toLowerCase().includes(keyword) ||
    row[7].toLowerCase().includes(keyword) ||
    row[8].toLowerCase().includes(keyword);

  return (
    matchesKind &&
    matchesRisk &&
    matchesAttack &&
    matchesCategory &&
    matchesStatus &&
    matchesPriority &&
    matchesKeyword
  );
}

function findInitialEvent(eventRows: EventRow[], filters?: EventListFilters) {
  if (filters?.focusEventId) {
    const focusedEvent = eventRows.find((row) => row[0] === filters.focusEventId);

    if (focusedEvent) {
      return focusedEvent;
    }
  }

  const filteredRows = eventRows.filter((row) => matchesFilters(row, filters));
  return filteredRows[0] ?? eventRows[0];
}

export default function ReportsView({
  eventRows,
  eventListFilters,
}: {
  eventRows: EventRow[];
  onMoveTab?: (tabId: TabId, filters?: EventListFilters) => void;
  eventListFilters?: EventListFilters;
}) {
  const isDirectReportMode = Boolean(
    eventListFilters?.openReport && eventListFilters?.focusEventId,
  );

  const initialEvent = useMemo(() => {
    return findInitialEvent(eventRows, eventListFilters);
  }, [eventRows, eventListFilters]);

  const [selectedEvent, setSelectedEvent] = useState<EventRow | undefined>(
    initialEvent,
  );
  const [showReport, setShowReport] = useState(isDirectReportMode);
  const [directReportMode, setDirectReportMode] = useState(isDirectReportMode);

  const [report, setReport] = useState<AiReportResponse | undefined>();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const reportRef = useRef<HTMLDivElement | null>(null);

  const fetchAiReport = useCallback(async (event: EventRow) => {
    setReport(undefined);
    setError(null);
    setIsLoading(true);

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/report/${encodeURIComponent(
          event[0],
        )}?attack_type=${encodeURIComponent(event[4])}`,
      );

      if (!response.ok) {
        throw new Error("AI 리포트를 불러오지 못했습니다.");
      }

      const data: AiReportResponse = await response.json();
      setReport(data);
    } catch {
      setError("AI 리포트 생성 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    const nextIsDirectReportMode = Boolean(
      eventListFilters?.openReport && eventListFilters?.focusEventId,
    );

    const nextEvent = findInitialEvent(eventRows, eventListFilters);

    setSelectedEvent(nextEvent);
    setShowReport(nextIsDirectReportMode);
    setDirectReportMode(nextIsDirectReportMode);

    setReport(undefined);
    setIsLoading(false);
    setError(null);

    if (nextIsDirectReportMode && nextEvent) {
      fetchAiReport(nextEvent);
    }
  }, [eventRows, eventListFilters, fetchAiReport]);

  useEffect(() => {
    if (!showReport) return;

    window.setTimeout(() => {
      reportRef.current?.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    }, 0);
  }, [showReport, selectedEvent]);

  function resetReportState() {
    setReport(undefined);
    setIsLoading(false);
    setError(null);
  }

  function handleSelectEvent(event: EventRow) {
    setSelectedEvent(event);
    setShowReport(false);
    setDirectReportMode(false);
    resetReportState();
  }

  async function handleShowReport() {
    if (!selectedEvent) return;

    setShowReport(true);
    await fetchAiReport(selectedEvent);
  }

  function handleChooseAnotherEvent() {
    setDirectReportMode(false);
    setShowReport(false);
    resetReportState();
  }

  if (directReportMode) {
    return (
      <div className="space-y-5">
        <div className="rounded-lg border border-slate-200 bg-white px-5 py-4 shadow-sm">
          <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <div>
              <p className="text-sm font-semibold text-blue-700">
                대시보드에서 선택한 우선 확인 이벤트
              </p>
              <h2 className="mt-1 text-xl font-bold text-slate-950">
                {selectedEvent?.[0] ?? "선택 이벤트"} AI 대응 리포트
              </h2>
              <p className="mt-1 text-sm text-slate-500">
                선택된 이벤트의 분석 대상 요약과 RAG 기반 대응 리포트를 바로 확인합니다.
              </p>
            </div>

            <button
              type="button"
              onClick={handleChooseAnotherEvent}
              className="h-9 rounded-md border border-slate-200 px-4 text-sm font-medium text-slate-700 transition hover:border-slate-300 hover:bg-slate-50"
            >
              다른 이벤트 선택하기
            </button>
          </div>
        </div>

        <div className="grid items-start gap-5 xl:grid-cols-[360px_minmax(0,1fr)]">
          <ReportTargetSummary
            event={selectedEvent}
            showReportButton={false}
          />

          <div ref={reportRef}>
            <AiReport
              event={selectedEvent}
              report={report}
              isLoading={isLoading}
              error={error}
              expanded
            />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-5">
      <div className="grid items-start gap-5 xl:grid-cols-[minmax(0,1fr)_390px]">
        <EventList
          expanded
          compact
          title="분석할 이벤트 선택"
          pageSize={5}
          eventRows={eventRows}
          selectedEventId={selectedEvent?.[0]}
          onSelectEvent={handleSelectEvent}
          initialFilters={eventListFilters}
        />

        <ReportTargetSummary
          event={selectedEvent}
          onShowReport={handleShowReport}
          showReportButton
        />
      </div>

      {showReport ? (
        <div ref={reportRef}>
          <AiReport
            event={selectedEvent}
            report={report}
            isLoading={isLoading}
            error={error}
            expanded
          />
        </div>
      ) : null}
    </div>
  );
}