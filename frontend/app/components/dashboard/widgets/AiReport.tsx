import { reportItems } from "./data";
import Panel from "./Panel";

export default function AiReport({ expanded = false }: { expanded?: boolean }) {
  return (
    <Panel title="AI 대응 리포트" action="Azure OpenAI">
      <div className={`space-y-4 ${expanded ? "max-w-5xl" : ""}`}>
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
