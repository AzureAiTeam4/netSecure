//탭3. 통계

import StatsOverview from "../widgets/StatsOverview";
import SummaryGrid from "../widgets/SummaryGrid";

export default function StatsView() {
  return (
    <>
      <SummaryGrid />
      <StatsOverview expanded />
    </>
  );
}
