import CategoryAccordion from './CategoryAccordion';
import ExecutiveSummary from './ExecutiveSummary';

const RealTimeIssueStream = ({ results, loading, summary }) => {
  const agentOrder = ['linguistic', 'structural', 'clinical', 'terminology', 'critical_data'];

  if (Object.keys(results).length === 0 && !loading && !summary) {
    return null;
  }

  return (
    <div className="mt-6">
      {/* Executive Summary */}
      {summary && <ExecutiveSummary summary={summary} />}

      {/* Results Section */}
      <div className="space-y-4">
        <h2 className="text-xl font-bold text-gray-900 mb-4">
          Detailed Analysis Results
        </h2>

        {agentOrder.map((agentName) => {
          const agentData = results[agentName];
          const isLoading = loading && !agentData;

          // Show accordion if loading or has data
          if (isLoading || agentData) {
            return (
              <CategoryAccordion
                key={agentName}
                agentName={agentName}
                agentData={agentData}
                loading={isLoading}
              />
            );
          }

          return null;
        })}
      </div>
    </div>
  );
};

export default RealTimeIssueStream;
