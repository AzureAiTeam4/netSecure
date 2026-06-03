import type { EventRow, TabId } from "../widgets/data";
import type { EventListFilters } from "../widgets/EventList";
import RecentRiskEvents from "../widgets/RecentRiskEvents";
import SummaryGrid from "../widgets/SummaryGrid";

export default function DashboardView({
  eventRows,
  onMoveTab,
}: {
  eventRows: EventRow[];
  onMoveTab?: (tabId: TabId, filters?: EventListFilters) => void;
}) {
  return (
    <>
      <SummaryGrid eventRows={eventRows} onMoveTab={onMoveTab} />

      <div className="space-y-5">
        <RecentRiskEvents eventRows={eventRows} onMoveTab={onMoveTab} />
      </div>
    </>
  );
}