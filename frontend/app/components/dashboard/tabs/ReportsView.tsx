//탭2. AI리포트

import AiReport from "../widgets/AiReport";
import SummaryGrid from "../widgets/SummaryGrid";

export default function ReportsView() {
  return (
    <>
      <SummaryGrid />
      <AiReport expanded />
    </>
  );
}
