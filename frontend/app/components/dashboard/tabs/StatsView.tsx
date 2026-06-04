import type { EventRow } from "../widgets/data";
import StatsOverview from "../widgets/StatsOverview";

export default function StatsView({ eventRows }: { eventRows: EventRow[] }) {
  return <StatsOverview expanded eventRows={eventRows} />;
}