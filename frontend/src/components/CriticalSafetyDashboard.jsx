import { useState } from 'react';
import { AlertCircle, CheckCircle, ChevronDown, ChevronRight } from 'lucide-react';
import IssueCard from './IssueCard';

const CriticalSafetyDashboard = ({ results, loading }) => {
  const [showNonCritical, setShowNonCritical] = useState(false);

  // Flatten all issues from both agents
  const allIssues = [];
  Object.values(results).forEach(agentResult => {
    if (agentResult?.issues) {
      allIssues.push(...agentResult.issues);
    }
  });

  // Organize by severity
  const highIssues = allIssues.filter(i => i.severity === 'HIGH');
  const mediumIssues = allIssues.filter(i => i.severity === 'MEDIUM');
  const lowIssues = allIssues.filter(i => i.severity === 'LOW');

  if (loading && allIssues.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600">Analyzing for critical safety issues...</p>
      </div>
    );
  }

  return (
    <div className="mt-6">
      {/* CRITICAL BANNER */}
      {highIssues.length > 0 && (
        <div className="bg-red-600 text-white p-6 rounded-lg mb-6 shadow-lg">
          <div className="flex items-center gap-3">
            <AlertCircle className="h-8 w-8" />
            <div>
              <h2 className="text-2xl font-bold">
                {highIssues.length} CRITICAL SAFETY {highIssues.length === 1 ? 'ISSUE' : 'ISSUES'} FOUND
              </h2>
              <p className="mt-1 text-sm">These issues require immediate attention before discharge</p>
            </div>
          </div>
        </div>
      )}

      {/* HIGH SEVERITY ISSUES (auto-expanded) */}
      {highIssues.length > 0 && (
        <div className="space-y-3 mb-6">
          <h3 className="text-lg font-bold text-gray-900">Critical Issues</h3>
          {highIssues.map((issue, idx) => (
            <IssueCard key={idx} issue={issue} autoExpanded={true} />
          ))}
        </div>
      )}

      {/* MEDIUM/LOW ISSUES (collapsible) */}
      {(mediumIssues.length > 0 || lowIssues.length > 0) && (
        <div className="mt-8">
          <button
            onClick={() => setShowNonCritical(!showNonCritical)}
            className="flex items-center gap-2 text-gray-700 hover:text-gray-900 font-medium"
          >
            {showNonCritical ? <ChevronDown className="h-5 w-5" /> : <ChevronRight className="h-5 w-5" />}
            Show {mediumIssues.length + lowIssues.length} Additional {mediumIssues.length + lowIssues.length === 1 ? 'Issue' : 'Issues'} (Medium/Low Priority)
          </button>

          {showNonCritical && (
            <div className="space-y-3 mt-4">
              {mediumIssues.map((issue, idx) => (
                <IssueCard key={`m-${idx}`} issue={issue} autoExpanded={false} />
              ))}
              {lowIssues.map((issue, idx) => (
                <IssueCard key={`l-${idx}`} issue={issue} autoExpanded={false} />
              ))}
            </div>
          )}
        </div>
      )}

      {/* NO ISSUES STATE */}
      {allIssues.length === 0 && !loading && (
        <div className="text-center py-12 bg-green-50 rounded-lg border-2 border-green-200">
          <CheckCircle className="h-16 w-16 mx-auto text-green-600 mb-4" />
          <h3 className="text-2xl font-bold text-green-800">No Critical Safety Issues</h3>
          <p className="text-green-600 mt-2">This discharge summary passes all safety validations</p>
        </div>
      )}
    </div>
  );
};

export default CriticalSafetyDashboard;
