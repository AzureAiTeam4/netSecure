"use client";

import { useEffect, useMemo, useState } from "react";
import type { EventRow } from "./data";
import Panel from "./Panel";
import StatusBadge from "./StatusBadge";

export type EventKindFilter = "전체" | "공격" | "정상";

export type EventListFilters = {
  kind?: EventKindFilter;
  risk?: string;
  attack?: string;
  category?: string;
  status?: string;
  query?: string;

  priorityOnly?: boolean;

  focusEventId?: string;
  openReport?: boolean;
};

type SortKey =
  | "eventId"
  | "time"
  | "attackType"
  | "category"
  | "confidence"
  | "risk"
  | "status"
  | null;

type SortDirection = "asc" | "desc";

const riskRank: Record<string, number> = {
  High: 3,
  Medium: 2,
  Low: 1,
};

const statusRank: Record<string, number> = {
  "확인 필요": 3,
  "관찰 필요": 2,
  정상: 1,
};

function getEventNumber(eventId: string) {
  const number = eventId.replace(/\D/g, "");
  return Number(number || 0);
}

function getSortValue(row: EventRow, sortKey: SortKey) {
  if (sortKey === "eventId") return getEventNumber(row[0]);
  if (sortKey === "time") return new Date(row[1]).getTime();
  if (sortKey === "attackType") return row[4];
  if (sortKey === "category") return row[5];
  if (sortKey === "confidence") return Number(row[6]);
  if (sortKey === "risk") return riskRank[row[7]] ?? 0;
  if (sortKey === "status") return statusRank[row[8]] ?? 0;

  return "";
}

function SortIcon({
  active,
  direction,
}: {
  active: boolean;
  direction: SortDirection;
}) {
  if (!active) {
    return <span className="text-slate-300">↕</span>;
  }

  return <span className="text-blue-600">{direction === "asc" ? "↑" : "↓"}</span>;
}

export default function EventList({
  expanded = false,
  eventRows,
  selectedEventId,
  onSelectEvent,
  initialFilters,
  pageSize,
  title,
  compact = false,
  reportMode = false,
}: {
  expanded?: boolean;
  eventRows: EventRow[];
  selectedEventId?: string;
  onSelectEvent?: (event: EventRow) => void;
  initialFilters?: EventListFilters;
  pageSize?: number;
  title?: string;
  compact?: boolean;
  reportMode?: boolean;
}) {
  const [page, setPage] = useState(1);
  const [kindFilter, setKindFilter] = useState<EventKindFilter>(
    initialFilters?.kind ?? "전체",
  );
  const [riskFilter, setRiskFilter] = useState(initialFilters?.risk ?? "전체");
  const [attackFilter, setAttackFilter] = useState(initialFilters?.attack ?? "전체");
  const [categoryFilter, setCategoryFilter] = useState(
    initialFilters?.category ?? "전체",
  );
  const [statusFilter, setStatusFilter] = useState(
    initialFilters?.status ?? "전체",
  );
  const [query, setQuery] = useState(initialFilters?.query ?? "");
  const [sortKey, setSortKey] = useState<SortKey>("time");
  const [sortDirection, setSortDirection] = useState<SortDirection>("desc");

  const rowsPerPage = pageSize ?? (expanded ? 12 : 14);

  const riskOptions = useMemo(() => {
    return ["전체", ...Array.from(new Set(eventRows.map((row) => row[7])))];
  }, [eventRows]);

  const attackOptions = useMemo(() => {
    return ["전체", ...Array.from(new Set(eventRows.map((row) => row[4])))];
  }, [eventRows]);

  const categoryOptions = useMemo(() => {
    return ["전체", ...Array.from(new Set(eventRows.map((row) => row[5])))];
  }, [eventRows]);

  const statusOptions = useMemo(() => {
    return ["전체", ...Array.from(new Set(eventRows.map((row) => row[8])))];
  }, [eventRows]);

  const filteredRows = useMemo(() => {
    const keyword = query.trim().toLowerCase();

    return eventRows.filter((row) => {
      const matchesKind =
        kindFilter === "전체" ||
        (kindFilter === "공격" && row[4] !== "Benign") ||
        (kindFilter === "정상" && row[4] === "Benign");

      const matchesRisk = riskFilter === "전체" || row[7] === riskFilter;
      const matchesAttack = attackFilter === "전체" || row[4] === attackFilter;
      const matchesCategory = categoryFilter === "전체" || row[5] === categoryFilter;
      const matchesStatus = statusFilter === "전체" || row[8] === statusFilter;

      const matchesPriority =
        !initialFilters?.priorityOnly || row[7] === "High" || row[8] === "확인 필요";

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
    });
  }, [
    eventRows,
    kindFilter,
    riskFilter,
    attackFilter,
    categoryFilter,
    statusFilter,
    query,
    initialFilters?.priorityOnly,
  ]);

  const sortedRows = useMemo(() => {
    if (!sortKey) return filteredRows;

    return [...filteredRows].sort((a, b) => {
      const aValue = getSortValue(a, sortKey);
      const bValue = getSortValue(b, sortKey);

      if (typeof aValue === "number" && typeof bValue === "number") {
        return sortDirection === "asc" ? aValue - bValue : bValue - aValue;
      }

      return sortDirection === "asc"
        ? String(aValue).localeCompare(String(bValue))
        : String(bValue).localeCompare(String(aValue));
    });
  }, [filteredRows, sortKey, sortDirection]);

  const totalPages = Math.max(1, Math.ceil(sortedRows.length / rowsPerPage));

  const visibleRows = useMemo(() => {
    const startIndex = (page - 1) * rowsPerPage;
    return sortedRows.slice(startIndex, startIndex + rowsPerPage);
  }, [sortedRows, page, rowsPerPage]);

  const pageItems = useMemo(() => {
    const maxVisiblePages = 5;

    if (totalPages <= maxVisiblePages) {
      return Array.from({ length: totalPages }, (_, index) => index + 1);
    }

    let startPage = Math.max(1, page - 2);
    let endPage = startPage + maxVisiblePages - 1;

    if (endPage > totalPages) {
      endPage = totalPages;
      startPage = totalPages - maxVisiblePages + 1;
    }

    return Array.from(
      { length: endPage - startPage + 1 },
      (_, index) => startPage + index,
    );
  }, [page, totalPages]);

  function handleSort(nextSortKey: SortKey) {
    if (!nextSortKey) return;

    setPage(1);

    if (sortKey === nextSortKey) {
      setSortDirection((current) => (current === "asc" ? "desc" : "asc"));
      return;
    }

    setSortKey(nextSortKey);

    if (
      nextSortKey === "time" ||
      nextSortKey === "confidence" ||
      nextSortKey === "risk" ||
      nextSortKey === "status"
    ) {
      setSortDirection("desc");
    } else {
      setSortDirection("asc");
    }
  }

  useEffect(() => {
    setKindFilter(initialFilters?.kind ?? "전체");
    setRiskFilter(initialFilters?.risk ?? "전체");
    setAttackFilter(initialFilters?.attack ?? "전체");
    setCategoryFilter(initialFilters?.category ?? "전체");
    setStatusFilter(initialFilters?.status ?? "전체");
    setQuery(initialFilters?.query ?? "");
    setPage(1);
  }, [initialFilters]);

  useEffect(() => {
    setPage(1);
  }, [kindFilter, riskFilter, attackFilter, categoryFilter, statusFilter, query]);

  const headers: Array<{
    label: string;
    sortKey: SortKey;
  }> = [
    { label: "Event ID", sortKey: "eventId" },
    { label: "시간", sortKey: "time" },
    { label: "출발지 IP", sortKey: null },
    { label: "목적지 IP", sortKey: null },
    { label: "공격 유형", sortKey: "attackType" },
    { label: "카테고리", sortKey: "category" },
    { label: "신뢰도", sortKey: "confidence" },
    { label: "위험도", sortKey: "risk" },
    { label: "상태", sortKey: "status" },
  ];

  return (
    <Panel
      title={title ?? `이벤트 목록 ${expanded ? "(전체 화면)" : ""}`}
      action={`${sortedRows.length.toLocaleString()} / ${eventRows.length.toLocaleString()}건`}
      className={`flex flex-col ${reportMode ? "h-full" : ""}`}
    >
      <div
        className={`${reportMode ? "mb-5" : "mb-4"} grid gap-3 ${
          compact ? "lg:grid-cols-6" : "md:grid-cols-3 xl:grid-cols-6"
        }`}
      >
        <select
          value={kindFilter}
          onChange={(event) => setKindFilter(event.target.value as EventKindFilter)}
          className="h-10 rounded-md border border-slate-200 bg-white px-3 text-sm text-slate-600"
        >
          <option value="전체">이벤트 구분: 전체</option>
          <option value="공격">이벤트 구분: 공격</option>
          <option value="정상">이벤트 구분: 정상</option>
        </select>

        <select
          value={riskFilter}
          onChange={(event) => setRiskFilter(event.target.value)}
          className="h-10 rounded-md border border-slate-200 bg-white px-3 text-sm text-slate-600"
        >
          {riskOptions.map((option) => (
            <option key={option} value={option}>
              위험도: {option}
            </option>
          ))}
        </select>

        <select
          value={attackFilter}
          onChange={(event) => setAttackFilter(event.target.value)}
          className="h-10 rounded-md border border-slate-200 bg-white px-3 text-sm text-slate-600"
        >
          {attackOptions.map((option) => (
            <option key={option} value={option}>
              공격 유형: {option}
            </option>
          ))}
        </select>

        <select
          value={categoryFilter}
          onChange={(event) => setCategoryFilter(event.target.value)}
          className="h-10 rounded-md border border-slate-200 bg-white px-3 text-sm text-slate-600"
        >
          {categoryOptions.map((option) => (
            <option key={option} value={option}>
              공격 카테고리: {option}
            </option>
          ))}
        </select>

        <select
          value={statusFilter}
          onChange={(event) => setStatusFilter(event.target.value)}
          className="h-10 rounded-md border border-slate-200 bg-white px-3 text-sm text-slate-600"
        >
          {statusOptions.map((option) => (
            <option key={option} value={option}>
              상태: {option}
            </option>
          ))}
        </select>

        <input
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          className="h-10 rounded-md border border-slate-200 px-3 text-sm"
          placeholder="IP, Event ID 검색"
        />
      </div>

      <div className="overflow-x-auto">
        <table className="w-full min-w-[780px] border-separate border-spacing-0 text-left text-sm">
          <thead>
            <tr className="bg-slate-50 text-xs text-slate-500">
              {headers.map((head) => (
                <th
                  key={head.label}
                  className="border-y border-slate-200 px-3 py-3 first:rounded-l-md first:border-l last:rounded-r-md last:border-r"
                >
                  {head.sortKey ? (
                    <button
                      type="button"
                      onClick={() => handleSort(head.sortKey)}
                      className="flex items-center gap-1 font-semibold transition hover:text-slate-900"
                    >
                      {head.label}
                      <SortIcon active={sortKey === head.sortKey} direction={sortDirection} />
                    </button>
                  ) : (
                    <span>{head.label}</span>
                  )}
                </th>
              ))}
            </tr>
          </thead>

          <tbody>
            {visibleRows.length > 0 ? (
              visibleRows.map((row) => {
                const isSelected = selectedEventId === row[0];

                return (
                  <tr
                    key={row[0]}
                    onClick={() => onSelectEvent?.(row)}
                    className={`text-xs transition ${
                      onSelectEvent ? "cursor-pointer" : ""
                    } ${
                      isSelected
                        ? "bg-blue-50 ring-1 ring-inset ring-blue-200"
                        : "hover:bg-blue-50/60"
                    }`}
                  >
                    {row.map((cell, index) => (
                      <td
                        key={`${row[0]}-${index}`}
                        className={`border-b border-slate-100 px-3 ${
                          reportMode ? "py-4" : "py-2.5"
                        }`}
                      >
                        {index >= 7 ? <StatusBadge value={cell} /> : cell}
                      </td>
                    ))}
                  </tr>
                );
              })
            ) : (
              <tr>
                <td colSpan={9} className="py-10 text-center text-sm text-slate-500">
                  조건에 맞는 이벤트가 없습니다.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <div
        className={`flex items-center justify-center gap-2 text-sm text-slate-500 ${
          reportMode ? "pt-5" : "pt-4"
        }`}
      >
        <button
          type="button"
          onClick={() => setPage((current) => Math.max(1, current - 1))}
          disabled={page === 1}
          className="grid h-9 w-9 place-items-center rounded-md border border-slate-200 transition hover:border-slate-300 hover:bg-slate-50 hover:text-slate-900 disabled:cursor-not-allowed disabled:opacity-40 disabled:hover:bg-transparent"
          aria-label="이전 페이지"
        >
          &lt;
        </button>

        {pageItems.map((item) => (
          <button
            key={item}
            type="button"
            onClick={() => setPage(item)}
            className={`h-9 min-w-9 rounded-md px-3 font-semibold transition ${
              page === item
                ? "bg-blue-600 text-white shadow-sm shadow-blue-200"
                : "border border-transparent text-slate-600 hover:border-slate-200 hover:bg-slate-50 hover:text-slate-900"
            }`}
          >
            {item}
          </button>
        ))}

        <button
          type="button"
          onClick={() => setPage((current) => Math.min(totalPages, current + 1))}
          disabled={page === totalPages}
          className="grid h-9 w-9 place-items-center rounded-md border border-slate-200 transition hover:border-slate-300 hover:bg-slate-50 hover:text-slate-900 disabled:cursor-not-allowed disabled:opacity-40 disabled:hover:bg-transparent"
          aria-label="다음 페이지"
        >
          &gt;
        </button>

        <span className="ml-2 text-xs text-slate-400">
          {page} / {totalPages}
        </span>
      </div>
    </Panel>
  );
}