import { useState } from 'react';
import { ChevronDown, ChevronRight, CheckCircle, Clock, Zap } from 'lucide-react';
import IssueCard from './IssueCard';

const CategoryAccordion = ({ agentName, agentData, loading }) => {
  const [expanded, setExpanded] = useState(true);

  const getAgentDisplayName = (name) => {
    const displayNames = {
      linguistic: 'Linguistic Quality',
      structural: 'Structural Compliance',
      clinical: 'Clinical Consistency',
      terminology: 'Terminology Standards',
      critical_data: 'Critical Data Validation',
    };
    return displayNames[name] || name;
  };

  const getAgentIcon = (name) => {
    if (loading) return <Clock className="h-5 w-5 text-blue-500 animate-pulse" />;
    if (agentData?.from_cache) return <Zap className="h-5 w-5 text-green-500" />;
    return <CheckCircle className="h-5 w-5 text-blue-500" />;
  };

  const issues = agentData?.issues || [];
  const issueCount = issues.length;

  return (
    <div className="bg-white rounded-lg shadow-md mb-4 overflow-hidden">
      {/* Header */}
      <div
        className="flex items-center justify-between p-4 cursor-pointer hover:bg-gray-50 transition-colors"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center gap-3 flex-1">
          {getAgentIcon(agentName)}
          <div>
            <h3 className="font-semibold text-gray-900">
              {getAgentDisplayName(agentName)}
            </h3>
            <div className="flex items-center gap-3 mt-1">
              {loading ? (
                <span className="text-sm text-gray-500">Analyzing...</span>
              ) : (
                <>
                  <span className="text-sm text-gray-600">
                    {issueCount} {issueCount === 1 ? 'issue' : 'issues'} found
                  </span>
                  {agentData?.from_cache && (
                    <span className="inline-flex items-center gap-1 text-xs text-green-600 bg-green-50 px-2 py-0.5 rounded">
                      <Zap className="h-3 w-3" />
                      Cached
                    </span>
                  )}
                  {agentData?.processing_time > 0 && (
                    <span className="text-xs text-gray-500">
                      {agentData.processing_time.toFixed(2)}s
                    </span>
                  )}
                </>
              )}
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {issueCount > 0 && (
            <span className="px-3 py-1 bg-blue-100 text-blue-800 text-sm font-semibold rounded-full">
              {issueCount}
            </span>
          )}
          {expanded ? (
            <ChevronDown className="h-5 w-5 text-gray-400" />
          ) : (
            <ChevronRight className="h-5 w-5 text-gray-400" />
          )}
        </div>
      </div>

      {/* Content */}
      {expanded && (
        <div className="px-4 pb-4">
          {loading ? (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
          ) : issueCount > 0 ? (
            <div className="space-y-2">
              {issues.map((issue, idx) => (
                <IssueCard key={idx} issue={issue} />
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <CheckCircle className="h-12 w-12 mx-auto mb-2 text-green-500" />
              <p>No issues found</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default CategoryAccordion;
