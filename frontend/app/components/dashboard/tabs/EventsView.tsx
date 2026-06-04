import type { EventRow, TabId } from "../widgets/data";
import EventList from "../widgets/EventList";
import SummaryGrid from "../widgets/SummaryGrid";
import type { EventListFilters } from "../widgets/EventList";

export default function EventsView({
  eventRows,
  onMoveTab,
  eventListFilters,
}: {
  eventRows: EventRow[];
  onMoveTab?: (tabId: TabId, filters?: EventListFilters) => void;
  eventListFilters?: EventListFilters;
}) {
  return (
    <>
      <SummaryGrid eventRows={eventRows} onMoveTab={onMoveTab} />
      <EventList expanded eventRows={eventRows} initialFilters={eventListFilters} />
    </>
  );
}