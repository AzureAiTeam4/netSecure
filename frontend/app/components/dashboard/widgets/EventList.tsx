"use client";

import { useMemo, useState } from "react";
import type { EventRow } from "./data";
import Panel from "./Panel";
import StatusBadge from "./StatusBadge";

export default function EventList({
  expanded = false,
  eventRows,
}: {
  expanded?: boolean;
  eventRows: EventRow[];
}) {
  const [page, setPage] = useState(1);
  const rowsPerPage = expanded ? 12 : 14;
  const totalPages = Math.ceil(eventRows.length / rowsPerPage);
  const visibleRows = useMemo(() => {
    const startIndex = (page - 1) * rowsPerPage;
    return eventRows.slice(startIndex, startIndex + rowsPerPage);
  }, [eventRows, page, rowsPerPage]);

  const pageItems = [1, 2, 3, 4, 5].filter((item) => item <= totalPages);

  return (
    <Panel title={`이벤트 목록 ${expanded ? "(전체 3,000건)" : "(총 3,000건)"}`} className="flex h-full flex-col">
      <div className="mb-4 grid gap-3 md:grid-cols-4">
        {["위험도", "공격 유형", "공격 카테고리"].map((label) => (
          <select key={label} className="h-10 rounded-md border border-slate-200 bg-white px-3 text-sm text-slate-600">
            <option>{label}: 전체</option>
          </select>
        ))}
        <input className="h-10 rounded-md border border-slate-200 px-3 text-sm" placeholder="IP 주소, Event ID 검색" />
      </div>
      <div className="overflow-x-auto">
        <table className="w-full min-w-[780px] border-separate border-spacing-0 text-left text-sm">
          <thead>
            <tr className="bg-slate-50 text-xs text-slate-500">
              {["Event ID", "시간", "출발지 IP", "목적지 IP", "공격 유형", "카테고리", "신뢰도", "위험도", "상태"].map((head) => (
                <th key={head} className="border-y border-slate-200 px-3 py-3 first:rounded-l-md first:border-l last:rounded-r-md last:border-r">
                  {head}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {visibleRows.map((row) => (
              <tr key={row[0]} className="text-xs hover:bg-blue-50/60">
                {row.map((cell, index) => (
                  <td key={`${row[0]}-${index}`} className="border-b border-slate-100 px-3 py-3">
                    {index >= 7 ? <StatusBadge value={cell} /> : cell}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="mt-auto flex items-center justify-center gap-2 pt-6 text-sm text-slate-500">
        <button
          type="button"
          onClick={() => setPage((current) => Math.max(1, current - 1))}
          disabled={page === 1}
          className="grid h-9 w-9 place-items-center rounded-md border border-slate-200 disabled:cursor-not-allowed disabled:opacity-40"
          aria-label="이전 페이지"
        >
          &lt;
        </button>
        {pageItems.map((item) => (
          <button
            key={item}
            type="button"
            onClick={() => setPage(item)}
            className={`h-9 min-w-9 rounded-md px-3 font-semibold ${
              page === item
                ? "bg-blue-600 text-white shadow-sm shadow-blue-200"
                : "border border-transparent text-slate-600 hover:border-slate-200 hover:bg-slate-50"
            }`}
          >
            {item}
          </button>
        ))}
        {totalPages > 6 ? <span className="px-2">...</span> : null}
        {totalPages > 5 ? (
          <button
            type="button"
            onClick={() => setPage(totalPages)}
            className={`h-9 min-w-12 rounded-md px-3 font-semibold ${
              page === totalPages
                ? "bg-blue-600 text-white shadow-sm shadow-blue-200"
                : "border border-transparent text-slate-600 hover:border-slate-200 hover:bg-slate-50"
            }`}
          >
            {totalPages}
          </button>
        ) : null}
        <button
          type="button"
          onClick={() => setPage((current) => Math.min(totalPages, current + 1))}
          disabled={page === totalPages}
          className="grid h-9 w-9 place-items-center rounded-md border border-slate-200 disabled:cursor-not-allowed disabled:opacity-40"
          aria-label="다음 페이지"
        >
          &gt;
        </button>
      </div>
    </Panel>
  );
}
