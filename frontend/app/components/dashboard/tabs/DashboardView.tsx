//대시보드 - 선택한이벤트 상세정보 칸

import AiReport from "../widgets/AiReport";
import type { EventRow } from "../widgets/data";
import EventList from "../widgets/EventList";
import SelectedEvent from "../widgets/SelectedEvent";
import StatsOverview from "../widgets/StatsOverview";
import SummaryGrid from "../widgets/SummaryGrid";

export default function DashboardView({ eventRows }: { eventRows: EventRow[] }) {
  return (
    <>
      <SummaryGrid />
      <div className="space-y-5">
        <StatsOverview />
      </div>
      <div className="mt-5 grid gap-5 2xl:grid-cols-[minmax(0,1fr)_360px]">
        <EventList eventRows={eventRows} />
        <div className="space-y-5">
          <SelectedEvent event={eventRows[0]} />
          <AiReport />
        </div>
      </div>
    </>
  );
}
