//이벤트리스트 탭에서 사용
//위험도 별 색깔 뱃지

export default function StatusBadge({ value }: { value: string }) {
  const className =
    value === "High" || value === "확인 필요"
      ? "bg-red-50 text-red-600 border-red-100"
      : value === "Medium" || value === "관찰 필요"
        ? "bg-amber-50 text-amber-700 border-amber-100"
        : "bg-emerald-50 text-emerald-700 border-emerald-100";

  return (
    <span className={`inline-flex rounded px-2 py-1 font-semibold ${className}`}>
      {value}
    </span>
  );
}
