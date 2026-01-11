import CriticalSafetyDashboard from './CriticalSafetyDashboard';
import ExecutiveSummary from './ExecutiveSummary';

const RealTimeIssueStream = ({ results, loading, summary }) => {
  // Don't hide the component - let parent (App.jsx) control visibility via showResults
  // This prevents race conditions where loading becomes false before results/summary update

  return (
    <div className="mt-6">
      {/* Executive Summary */}
      {summary && <ExecutiveSummary summary={summary} />}

      {/* Critical Safety Dashboard (replaces CategoryAccordion loop) */}
      <CriticalSafetyDashboard results={results} loading={loading} />
    </div>
  );
};

export default RealTimeIssueStream;
