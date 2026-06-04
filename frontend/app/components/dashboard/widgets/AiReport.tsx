import type { EventRow } from "./data";
import Panel from "./Panel";

export type AiReportResponse = {
  event_id: string;
  report_id: string;
  report_summary: string;
  report_reason: string;
  report_impact: string;
  report_checkpoints: string[];
  report_response: string[];
  report_created_at: string;
};

function getReportId(eventId: string) {
  const number = eventId.replace(/\D/g, "") || "0000";
  return `R-${number.padStart(4, "0")}`;
}

function getReportCreatedAt() {
  return new Date().toISOString().slice(0, 19).replace("T", " ");
}

function getMockRagReport(event: EventRow): AiReportResponse {
  const [eventId, , sourceIp, destinationIp, attackType, category] = event;

  if (attackType === "Injection") {
    return {
      event_id: eventId,
      report_id: getReportId(eventId),
      report_summary: `${eventId} 이벤트는 웹 입력값 또는 요청 파라미터를 통한 Injection 공격이 의심됩니다.`,
      report_reason:
        "웹 입력값 또는 요청 파라미터를 통해 비정상 명령이나 쿼리가 삽입되었을 가능성이 있습니다.",
      report_impact:
        "공격이 성공할 경우 데이터베이스 조회, 수정, 정보 노출, 서버 명령 실행 등의 위험으로 이어질 수 있습니다.",
      report_checkpoints: [
        "웹 요청 로그에서 비정상 파라미터 또는 특수문자 패턴을 확인합니다.",
        "DB 접근 로그에서 비정상 조회 또는 수정 요청이 있었는지 확인합니다.",
        `출발지 ${sourceIp}에서 목적지 ${destinationIp}로 향한 반복 요청 여부를 확인합니다.`,
      ],
      report_response: [
        "입력값 검증 로직을 점검하고 허용되지 않은 문자나 쿼리 패턴을 차단합니다.",
        "Prepared Statement 또는 Parameterized Query 적용 여부를 확인합니다.",
        "웹 방화벽(WAF) 정책을 점검하고 Injection 공격 패턴 탐지 규칙을 강화합니다.",
      ],
      report_created_at: getReportCreatedAt(),
    };
  }

  if (attackType === "XSS") {
    return {
      event_id: eventId,
      report_id: getReportId(eventId),
      report_summary: `${eventId} 이벤트는 XSS 공격 가능성이 있는 웹 공격 이벤트입니다.`,
      report_reason:
        "사용자 입력값이나 요청 데이터에 스크립트 삽입 패턴이 포함되었을 가능성이 있습니다.",
      report_impact:
        "공격이 성공할 경우 사용자 세션 탈취, 악성 스크립트 실행, 페이지 변조 등의 문제가 발생할 수 있습니다.",
      report_checkpoints: [
        "웹 요청 로그에서 script 태그, 이벤트 핸들러, 인코딩 우회 패턴을 확인합니다.",
        "출력 시 HTML 엔티티 인코딩이 적용되는지 점검합니다.",
        "해당 요청이 게시판, 댓글, 검색창 등 사용자 입력 영역에서 발생했는지 확인합니다.",
      ],
      report_response: [
        "입력값 검증과 출력 인코딩 로직을 강화합니다.",
        "HTML Sanitization 라이브러리 적용 여부를 확인합니다.",
        "Content Security Policy 적용을 검토합니다.",
      ],
      report_created_at: getReportCreatedAt(),
    };
  }

  if (attackType === "Password") {
    return {
      event_id: eventId,
      report_id: getReportId(eventId),
      report_summary: `${eventId} 이벤트는 인증 공격 또는 비밀번호 대입 시도로 의심됩니다.`,
      report_reason:
        "짧은 시간 내 반복적인 인증 시도나 비정상 로그인 패턴이 발생했을 가능성이 있습니다.",
      report_impact:
        "공격이 성공할 경우 계정 탈취, 내부 시스템 접근, 데이터 유출 등의 보안 사고로 이어질 수 있습니다.",
      report_checkpoints: [
        "로그인 실패 횟수와 반복 시도 간격을 확인합니다.",
        `출발지 ${sourceIp}의 다른 계정 대상 접근 시도 여부를 확인합니다.`,
        "계정 잠금 정책과 MFA 적용 여부를 점검합니다.",
      ],
      report_response: [
        "의심 IP를 차단하거나 접근 제한 정책을 적용합니다.",
        "로그인 실패 횟수 제한과 계정 잠금 정책을 강화합니다.",
        "관리자 계정과 주요 계정에 MFA 적용을 검토합니다.",
      ],
      report_created_at: getReportCreatedAt(),
    };
  }

  if (attackType === "Scanning") {
    return {
      event_id: eventId,
      report_id: getReportId(eventId),
      report_summary: `${eventId} 이벤트는 서비스 탐색 또는 포트 스캔 가능성이 있는 이벤트입니다.`,
      report_reason:
        "공격자가 활성화된 포트나 서비스를 식별하기 위해 다수의 접근을 시도했을 가능성이 있습니다.",
      report_impact:
        "노출된 서비스 정보가 후속 공격에 활용될 수 있으며, 취약 서비스가 발견될 경우 침해 시도로 이어질 수 있습니다.",
      report_checkpoints: [
        `출발지 ${sourceIp}에서 여러 목적지 또는 포트로 반복 접근했는지 확인합니다.`,
        "스캔 대상 시스템의 불필요한 포트와 서비스가 열려 있는지 점검합니다.",
        "동일 IP의 후속 공격 이벤트 발생 여부를 확인합니다.",
      ],
      report_response: [
        "불필요한 포트와 서비스를 비활성화합니다.",
        "방화벽 또는 접근 제어 정책으로 의심 IP를 제한합니다.",
        "반복 스캔 패턴에 대한 모니터링 규칙을 강화합니다.",
      ],
      report_created_at: getReportCreatedAt(),
    };
  }

  if (attackType === "Reconnaissance") {
    return {
      event_id: eventId,
      report_id: getReportId(eventId),
      report_summary: `${eventId} 이벤트는 정찰 단계의 정보 수집 행위로 의심됩니다.`,
      report_reason:
        "공격자가 대상 네트워크나 서비스 정보를 파악하기 위해 DNS, WHOIS, 서비스 배너 등의 정보를 수집했을 가능성이 있습니다.",
      report_impact:
        "수집된 정보는 이후 표적 공격, 취약점 악용, 피싱, 침투 시도에 활용될 수 있습니다.",
      report_checkpoints: [
        "DNS 질의, WHOIS 조회, 서비스 배너 수집 시도 여부를 확인합니다.",
        "동일 출발지 IP의 반복 접근 패턴을 확인합니다.",
        "외부에 노출된 서비스와 도메인 정보 범위를 점검합니다.",
      ],
      report_response: [
        "불필요하게 노출된 서비스 정보를 최소화합니다.",
        "의심스러운 출발지 IP에 대한 접근 제한을 검토합니다.",
        "정찰성 트래픽 탐지 규칙과 로그 모니터링을 강화합니다.",
      ],
      report_created_at: getReportCreatedAt(),
    };
  }

  return {
    event_id: eventId,
    report_id: getReportId(eventId),
    report_summary: `${eventId} 이벤트는 ${category} 범주로 분류된 보안 이벤트입니다.`,
    report_reason:
      "현재 이벤트는 정상 또는 낮은 위험도로 분류되었지만, 반복 패턴이 있을 경우 추가 검토가 필요합니다.",
    report_impact:
      "단일 이벤트로는 영향이 제한적일 수 있으나, 반복 발생 시 이상 행위의 일부일 가능성이 있습니다.",
    report_checkpoints: [
      "동일 출발지 IP의 반복 이벤트 발생 여부를 확인합니다.",
      "동일 목적지로 향한 유사 트래픽이 있는지 확인합니다.",
      "정상 트래픽 패턴과 비교해 비정상성이 있는지 점검합니다.",
    ],
    report_response: [
      "이벤트를 관찰 상태로 유지하고 반복 발생 여부를 모니터링합니다.",
      "동일 패턴이 증가할 경우 위험도 재평가를 검토합니다.",
    ],
    report_created_at: getReportCreatedAt(),
  };
}

function ReportSection({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div className="rounded-lg border border-slate-200 bg-slate-50 px-4 py-4">
      <p className="text-sm font-bold text-blue-700">{title}</p>
      <div className="mt-3 text-sm leading-6 text-slate-700">{children}</div>
    </div>
  );
}

function ReportList({ items }: { items: string[] }) {
  return (
    <ul className="space-y-2">
      {items.map((item, index) => (
        <li key={`${item}-${index}`} className="flex gap-2">
          <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-blue-500" />
          <span>{item}</span>
        </li>
      ))}
    </ul>
  );
}

export default function AiReport({
  event,
  expanded = false,
  report,
  isLoading = false,
  error,
}: {
  event?: EventRow;
  expanded?: boolean;
  report?: AiReportResponse;
  isLoading?: boolean;
  error?: string | null;
}) {
  if (!event) {
    return (
      <Panel title="AI 대응 리포트">
        <div className="rounded-lg border border-dashed border-slate-200 bg-slate-50 px-4 py-10 text-center">
          <p className="text-sm font-semibold text-slate-700">선택된 이벤트가 없습니다.</p>
          <p className="mt-2 text-sm text-slate-500">
            이벤트를 선택하면 AI 대응 리포트를 확인할 수 있습니다.
          </p>
        </div>
      </Panel>
    );
  }

  const reportData = report ?? getMockRagReport(event);

  return (
    <Panel
      title="AI 대응 리포트"
      action={reportData.event_id}
      className={expanded ? "" : "h-full"}
    >
      {isLoading ? (
        <div className="rounded-lg border border-blue-100 bg-blue-50 px-4 py-8 text-center">
          <p className="text-sm font-semibold text-blue-700">
            AI 대응 리포트를 생성하고 있습니다.
          </p>
          <p className="mt-2 text-sm text-slate-600">
            선택 이벤트의 위험 원인과 대응 방안을 분석하는 중입니다.
          </p>
        </div>
      ) : null}

      {error ? (
        <div className="rounded-lg border border-rose-100 bg-rose-50 px-4 py-4">
          <p className="text-sm font-semibold text-rose-600">리포트 생성 실패</p>
          <p className="mt-2 text-sm text-slate-600">{error}</p>
        </div>
      ) : null}

      {!isLoading && !error ? (
        <div className="space-y-4">
          <div className="rounded-lg border border-blue-100 bg-blue-50/60 px-4 py-4">
            <div className="flex flex-col gap-2 md:flex-row md:items-start md:justify-between">
              <div>
                <p className="text-xs font-medium text-blue-700">
                  Report ID: {reportData.report_id}
                </p>
                <h3 className="mt-2 text-lg font-bold text-slate-950">
                  {reportData.report_summary}
                </h3>
              </div>

              <p className="shrink-0 text-xs text-slate-500">
                생성 시간: {reportData.report_created_at || "-"}
              </p>
            </div>
          </div>

          <ReportSection title="위험 원인">
            <p>{reportData.report_reason}</p>
          </ReportSection>

          <ReportSection title="예상 영향">
            <p>{reportData.report_impact}</p>
          </ReportSection>

          <div className="grid gap-4 xl:grid-cols-2">
            <ReportSection title="추가 확인 사항">
              <ReportList items={reportData.report_checkpoints} />
            </ReportSection>

            <ReportSection title="권장 대응 방안">
              <ReportList items={reportData.report_response} />
            </ReportSection>
          </div>
        </div>
      ) : null}
    </Panel>
  );
}