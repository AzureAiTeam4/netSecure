import type { EventRow } from "./data";
import Panel from "./Panel";

function getRiskMessage(risk: string) {
  if (risk === "High") {
    return "높은 위험도로 분류된 이벤트입니다. 관리자 확인과 즉각적인 로그 점검이 필요합니다.";
  }

  if (risk === "Medium") {
    return "중간 위험도로 분류된 이벤트입니다. 반복 발생 여부와 관련 IP의 추가 활동을 관찰해야 합니다.";
  }

  return "낮은 위험도로 분류된 이벤트입니다. 현재 즉각적인 조치보다는 정상 트래픽 여부 확인이 우선입니다.";
}

function getAttackDescription(attackType: string, category: string) {
  const descriptions: Record<string, string> = {
    Injection:
      "웹 서비스 입력값에 비정상적인 명령이나 쿼리 문법이 포함되었을 가능성이 있습니다.",
    XSS:
      "웹 페이지 입력 영역을 통해 스크립트 삽입이 시도되었을 가능성이 있습니다.",
    Scanning:
      "공격자가 서버의 열린 포트, 서비스, 취약 지점을 탐색하고 있을 가능성이 있습니다.",
    Reconnaissance:
      "공격자가 시스템 구조, 네트워크 정보, 서비스 구성을 사전에 파악하려는 정찰 행위일 가능성이 있습니다.",
    Password:
      "계정 접근을 목적으로 비밀번호 대입 또는 인증 우회 시도가 발생했을 가능성이 있습니다.",
    Benign:
      "현재 이벤트는 정상 트래픽으로 분류되었습니다. 다만 반복 패턴이 있는 경우 추가 확인이 필요합니다.",
  };

  return descriptions[attackType] ?? `${category} 유형의 이상 이벤트로 분류되었습니다.`;
}

function getImpactMessage(attackType: string) {
  const impacts: Record<string, string> = {
    Injection:
      "데이터베이스 정보 노출, 데이터 변조, 서버 명령 실행 등으로 이어질 수 있습니다.",
    XSS:
      "사용자 세션 탈취, 악성 스크립트 실행, 피싱 페이지 유도 등으로 이어질 수 있습니다.",
    Scanning:
      "직접적인 피해보다 후속 공격을 위한 사전 탐색 단계일 가능성이 큽니다.",
    Reconnaissance:
      "공격자가 취약한 서비스나 네트워크 구조를 파악한 뒤 추가 침투를 시도할 수 있습니다.",
    Password:
      "계정 탈취, 권한 상승, 내부 시스템 접근으로 이어질 수 있습니다.",
    Benign:
      "현재 기준에서는 직접적인 보안 피해 가능성이 낮습니다.",
  };

  return impacts[attackType] ?? "서비스 장애, 비정상 접근, 추가 공격 시도로 이어질 수 있습니다.";
}

function getActionMessage(attackType: string, sourceIp: string, destinationIp: string) {
  const actions: Record<string, string> = {
    Injection:
      "웹 서버 접근 로그와 요청 파라미터를 확인하고, 입력값 검증 및 WAF 룰을 점검하세요.",
    XSS:
      "입력값 필터링, 출력 인코딩, 스크립트 삽입 로그를 확인하고 관련 URL 접근 기록을 점검하세요.",
    Scanning:
      "동일 출발지 IP의 반복 접근 여부를 확인하고, 필요 시 방화벽 차단 또는 rate limit 정책을 적용하세요.",
    Reconnaissance:
      "해당 IP의 접근 경로와 요청 패턴을 확인하고, 불필요하게 노출된 서비스가 없는지 점검하세요.",
    Password:
      "로그인 실패 횟수, 인증 로그, 계정 잠금 정책을 확인하고 의심 계정의 비밀번호 재설정을 검토하세요.",
    Benign:
      "정상 이벤트로 분류되었지만, 동일 IP에서 반복적인 이상 패턴이 발생하는지 모니터링하세요.",
  };

  return `${actions[attackType] ?? "관련 로그와 네트워크 흐름을 확인하고 관리자 검토를 진행하세요."} 출발지 ${sourceIp}에서 목적지 ${destinationIp}로 향한 트래픽을 우선 확인하는 것이 좋습니다.`;
}

function createReportItems(event?: EventRow) {
  if (!event) {
    return [
      ["이벤트 요약", "선택된 이벤트가 없습니다. 이벤트 목록에서 분석할 이벤트를 선택하세요."],
      ["위험 원인", "이벤트를 선택하면 공격 유형, 위험도, 신뢰도 기준으로 원인을 요약합니다."],
      ["예상 영향", "이벤트를 선택하면 예상 피해 범위와 보안 영향을 확인할 수 있습니다."],
      ["권장 대응 방안", "이벤트를 선택하면 관리자 조치 방향을 확인할 수 있습니다."],
    ];
  }

  const [eventId, time, sourceIp, destinationIp, attackType, category, confidence, risk] = event;

  return [
    [
      "이벤트 요약",
      `${eventId} 이벤트는 ${time}에 발생했으며, ${sourceIp}에서 ${destinationIp}로 향한 트래픽입니다. 공격 유형은 ${attackType}, 카테고리는 ${category}, 예측 신뢰도는 ${Math.round(Number(confidence) * 100)}%입니다.`,
    ],
    [
      "위험 원인",
      `${getAttackDescription(attackType, category)} ${getRiskMessage(risk)}`,
    ],
    [
      "예상 영향",
      getImpactMessage(attackType),
    ],
    [
      "권장 대응 방안",
      getActionMessage(attackType, sourceIp, destinationIp),
    ],
  ];
}

export default function AiReport({
  expanded = false,
  event,
}: {
  expanded?: boolean;
  event?: EventRow;
}) {
  const reportItems = createReportItems(event);

  return (
    <Panel title="AI 대응 리포트" action={event ? event[0] : "Azure OpenAI"}>
      <div className="space-y-4">
        {reportItems.map(([title, body]) => (
          <div key={title} className="rounded-md border border-blue-100 bg-blue-50/40 p-4">
            <p className="text-sm font-bold text-blue-700">{title}</p>
            <p className="mt-2 text-sm leading-6 text-slate-700">{body}</p>
          </div>
        ))}
      </div>
    </Panel>
  );
}