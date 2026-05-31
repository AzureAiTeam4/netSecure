//탭1. 이벤트 리스트

import type { EventRow } from "../widgets/data";
import EventList from "../widgets/EventList";
import SummaryGrid from "../widgets/SummaryGrid";

export default function EventsView({ eventRows }: { eventRows: EventRow[] }) {
  return (
    <>
      <SummaryGrid />
      <EventList expanded eventRows={eventRows} />
    </>
  );
}
