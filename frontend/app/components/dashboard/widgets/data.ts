//더미데이터

export type TabId = "dashboard" | "events" | "reports" | "stats";

export const navigation: Array<{ id: TabId; label: string; icon: string }> = [
  { id: "dashboard", label: "대시보드", icon: "D" },
  { id: "events", label: "이벤트 목록", icon: "E" },
  { id: "reports", label: "AI 리포트", icon: "R" },
  { id: "stats", label: "통계", icon: "S" },
];

export const summaryCards = [
  {
    label: "전체 이벤트",
    value: "3,000",
    change: "+12.5%",
    tone: "blue",
    note: "지난 7일 대비",
  },
  {
    label: "공격 이벤트",
    value: "2,000",
    change: "+15.3%",
    tone: "red",
    note: "지난 7일 대비",
  },
  {
    label: "정상 이벤트",
    value: "1,000",
    change: "-3.7%",
    tone: "green",
    note: "지난 7일 대비",
  },
  {
    label: "위험 이벤트",
    value: "820",
    change: "+18.2%",
    tone: "orange",
    note: "지난 7일 대비",
  },
];

export type EventRow = [string, string, string, string, string, string, string, string, string];

const baseEventRows: EventRow[] = [
  ["E-0001", "2025-05-21 14:21:03", "192.168.0.12", "10.0.0.8", "Injection", "웹 공격", "0.93", "High", "확인 필요"],
  ["E-0002", "2025-05-21 14:20:11", "192.168.0.15", "10.0.0.5", "XSS", "웹 공격", "0.89", "High", "확인 필요"],
  ["E-0003", "2025-05-21 14:19:45", "192.168.0.23", "10.0.0.7", "Scanning", "탐색형 공격", "0.72", "Medium", "관찰 필요"],
  ["E-0004", "2025-05-21 14:18:32", "192.168.0.31", "10.0.0.2", "Reconnaissance", "탐색형 공격", "0.68", "Medium", "관찰 필요"],
  ["E-0005", "2025-05-21 14:17:55", "192.168.0.44", "10.0.0.9", "Password", "인증 공격", "0.91", "High", "확인 필요"],
  ["E-0006", "2025-05-21 14:16:22", "192.168.0.51", "10.0.0.3", "Benign", "정상", "0.96", "Low", "정상"],
];

function formatEventTime(index: number, anchorDate: Date) {
  const date = new Date(anchorDate);
  date.setSeconds(date.getSeconds() - index * 52);

  const pad = (value: number) => String(value).padStart(2, "0");

  return [
    date.getFullYear(),
    pad(date.getMonth() + 1),
    pad(date.getDate()),
  ].join("-") + ` ${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`;
}

export function generateEventRows(anchorDate: Date): EventRow[] {
  return Array.from({ length: 3000 }, (_, index) => {
    const base = baseEventRows[index % baseEventRows.length];
    const eventNumber = index + 1;
    const confidence = Math.max(0.61, Number(base[6]) - (index % 7) * 0.01).toFixed(2);

    return [
      `E-${String(eventNumber).padStart(4, "0")}`,
      formatEventTime(index, anchorDate),
      `192.168.0.${12 + (index * 3) % 240}`,
      `10.0.0.${2 + (index * 5) % 80}`,
      base[4],
      base[5],
      confidence,
      base[7],
      base[8],
    ];
  });
}

export const attackBars = [
  ["Scanning", 700, "bg-blue-500"],
  ["Reconnaissance", 420, "bg-teal-500"],
  ["XSS", 310, "bg-amber-400"],
  ["Password", 280, "bg-violet-500"],
  ["Injection", 290, "bg-rose-500"],
] as const;

export const reportItems = [
  ["이벤트 요약", "해당 이벤트는 Injection 공격이 의심됩니다. 웹 서비스의 입력값 검증 요청 파라미터를 통해 비정상적인 명령이 삽입되었을 가능성이 있습니다."],
  ["위험 원인", "공격자가 SQL 문법 또는 시스템 명령을 삽입하여 데이터베이스 조회, 수정, 시스템 명령 실행을 시도할 수 있습니다."],
  ["예상 영향", "데이터 유출, 데이터 변조, 시스템 악용 등 심각한 보안 사고로 이어질 수 있습니다."],
  ["권장 대응 방안", "웹 서버 접근 로그와 파라미터 값을 확인하고 WAF 룰 및 입력값 필터링 정책을 점검하세요."],
];

export const toneClasses: Record<string, string> = {
  blue: "text-blue-600 bg-blue-50 border-blue-100",
  red: "text-red-600 bg-red-50 border-red-100",
  green: "text-emerald-600 bg-emerald-50 border-emerald-100",
  orange: "text-orange-600 bg-orange-50 border-orange-100",
};
