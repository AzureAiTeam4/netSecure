"use client";

import { useEffect, useMemo, useState } from "react";
import type { EventRow, TabId } from "./data";
import type { EventListFilters } from "./EventList";
import {
  getEventPriorityScore,
  getPriorityLabel,
  sortEventsByPriority,
} from "./eventPriority";
import Panel from "./Panel";
import StatusBadge from "./StatusBadge";

function getPriorityBadgeClass(label: string) {
  if (label === "최우선") {
    return "border-rose-200 bg-rose-50 text-rose-600";
  }

  if (label === "우선") {
    return "border-amber-200 bg-amber-50 text-amber-700";
  }

  if (label === "검토") {
    return "border-blue-200 bg-blue-50 text-blue-700";
  }

  return "border-slate-200 bg-slate-50 text-slate-600";
}

function getAttackEmphasisClass(attackType: string) {
  if (attackType === "Injection" || attackType === "XSS" || attackType === "Password") {
    return "text-rose-600";
  }

  if (attackType === "Scanning" || attackType === "Reconnaissance") {
    return "text-amber-600";
  }

  return "text-slate-900";
}

function getReportFilters(event: EventRow): EventListFilters {
  return {
    kind: "전체",
    risk: "전체",
    attack: "전체",
    category: "전체",
    status: "전체",
    query: "",
    focusEventId: event[0],
    openReport: true,
  };
}

export default function RecentRiskEvents({
  eventRows,
  onMoveTab,
}: {
  eventRows: EventRow[];
  onMoveTab?: (tabId: TabId, filters?: EventListFilters) => void;
}) {
  const previewRows = useMemo(() => {
    return sortEventsByPriority(eventRows)
      .filter((row) => row[7] === "High" || row[8] === "확인 필요")
      .slice(0, 6);
  }, [eventRows]);

  const [selectedEvent, setSelectedEvent] = useState<EventRow | undefined>(previewRows[0]);

  useEffect(() => {
    setSelectedEvent(previewRows[0]);
  }, [previewRows]);

  const selectedPriorityScore = selectedEvent ? getEventPriorityScore(selectedEvent) : 0;
  const selectedPriorityLabel = selectedEvent
    ? getPriorityLabel(selectedPriorityScore)
    : "일반";

  const allEventFilters: EventListFilters = {
    kind: "전체",
    risk: "전체",
    attack: "전체",
    category: "전체",
    status: "전체",
    query: "",
  };

  return (
    <Panel title="우선 확인 이벤트" action={`${previewRows.length}건 미리보기`}>
      <div className="mb-4 rounded-md border border-slate-200 bg-slate-50 px-4 py-3">
        <p className="text-xs leading-5 text-slate-500">
          위험도, 상태, 공격 유형, 예측 신뢰도를 종합해 관리자가 먼저 확인해야 할 이벤트를 정렬합니다.
          이벤트를 선택한 뒤 AI 대응 리포트로 바로 이동할 수 있습니다.
        </p>
      </div>

      <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_320px]">
        <div className="overflow-x-auto">
          <table className="w-full min-w-[780px] border-separate border-spacing-0 text-left text-sm">
            <thead>
              <tr className="bg-slate-50 text-xs text-slate-500">
                {[
                  "우선순위",
                  "Event ID",
                  "시간",
                  "출발지 IP",
                  "공격 유형",
                  "신뢰도",
                  "위험도",
                  "상태",
                ].map((head) => (
                  <th
                    key={head}
                    className="border-y border-slate-200 px-3 py-3 first:rounded-l-md first:border-l last:rounded-r-md last:border-r"
                  >
                    {head}
                  </th>
                ))}
              </tr>
            </thead>

            <tbody>
              {previewRows.map((row) => {
                const priorityScore = getEventPriorityScore(row);
                const priorityLabel = getPriorityLabel(priorityScore);
                const isSelected = selectedEvent?.[0] === row[0];

                return (
                  <tr
                    key={row[0]}
                    onClick={() => setSelectedEvent(row)}
                    className={`cursor-pointer text-xs transition ${
                      isSelected
                        ? "bg-blue-50 ring-1 ring-inset ring-blue-200"
                        : "hover:bg-blue-50/60"
                    }`}
                  >
                    <td className="border-b border-slate-100 px-3 py-3">
                      <span
                        className={`inline-flex rounded-full border px-2.5 py-1 text-xs font-semibold ${getPriorityBadgeClass(
                          priorityLabel,
                        )}`}
                      >
                        {priorityLabel}
                      </span>
                    </td>

                    <td className="border-b border-slate-100 px-3 py-3 font-semibold text-slate-900">
                      {row[0]}
                    </td>

                    <td className="border-b border-slate-100 px-3 py-3 text-slate-600">
                      {row[1]}
                    </td>

                    <td className="border-b border-slate-100 px-3 py-3 font-mono text-slate-700">
                      {row[2]}
                    </td>

                    <td
                      className={`border-b border-slate-100 px-3 py-3 font-semibold ${getAttackEmphasisClass(
                        row[4],
                      )}`}
                    >
                      {row[4]}
                    </td>

                    <td className="border-b border-slate-100 px-3 py-3 text-slate-600">
                      {row[6]}
                    </td>

                    <td className="border-b border-slate-100 px-3 py-3">
                      <StatusBadge value={row[7]} />
                    </td>

                    <td className="border-b border-slate-100 px-3 py-3">
                      <StatusBadge value={row[8]} />
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        <aside className="rounded-lg border border-slate-200 bg-slate-50 px-4 py-4">
          {selectedEvent ? (
            <>
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="text-xs font-medium text-slate-500">선택 이벤트</p>
                  <p className="mt-1 text-2xl font-bold text-slate-950">
                    {selectedEvent[0]}
                  </p>
                </div>

                <span
                  className={`shrink-0 rounded-full border px-2.5 py-1 text-xs font-semibold ${getPriorityBadgeClass(
                    selectedPriorityLabel,
                  )}`}
                >
                  {selectedPriorityLabel}
                </span>
              </div>

              <div className="mt-4 flex flex-wrap gap-2">
                <StatusBadge value={selectedEvent[7]} />
                <StatusBadge value={selectedEvent[8]} />
              </div>

              <div className="mt-4 rounded-md border border-slate-200 bg-white px-3 py-3">
                <p className="text-xs font-medium text-slate-500">공격 유형</p>
                <p
                  className={`mt-1 text-lg font-bold ${getAttackEmphasisClass(
                    selectedEvent[4],
                  )}`}
                >
                  {selectedEvent[4]}
                </p>
                <p className="mt-1 text-xs text-slate-500">{selectedEvent[5]}</p>
              </div>

              <div className="mt-3 rounded-md border border-slate-200 bg-white px-3 py-3">
                <p className="text-xs font-medium text-slate-500">우선순위 점수</p>
                <p className="mt-1 text-lg font-bold text-slate-950">
                  {selectedPriorityScore}점
                </p>
              </div>

              <button
                type="button"
                onClick={() => onMoveTab?.("reports", getReportFilters(selectedEvent))}
                className="mt-4 h-10 w-full rounded-md bg-blue-600 px-4 text-sm font-semibold text-white shadow-sm shadow-blue-200 transition hover:bg-blue-700 active:scale-[0.99]"
              >
                선택 이벤트 AI 리포트 보기
              </button>

              <button
                type="button"
                onClick={() => onMoveTab?.("events", allEventFilters)}
                className="mt-2 h-9 w-full rounded-md border border-slate-200 bg-white px-4 text-sm font-medium text-slate-700 transition hover:border-slate-300 hover:bg-slate-50"
              >
                전체 이벤트 목록 보기
              </button>
            </>
          ) : (
            <div className="grid min-h-[240px] place-items-center text-center">
              <div>
                <p className="text-sm font-semibold text-slate-700">
                  선택된 이벤트가 없습니다.
                </p>
                <p className="mt-2 text-xs text-slate-500">
                  왼쪽 목록에서 분석할 이벤트를 선택하세요.
                </p>
              </div>
            </div>
          )}
        </aside>
      </div>
    </Panel>
  );
}