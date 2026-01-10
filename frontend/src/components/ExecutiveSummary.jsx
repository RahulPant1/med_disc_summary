import { AlertCircle, AlertTriangle, Info, Clock, Zap } from 'lucide-react';

const ExecutiveSummary = ({ summary }) => {
  if (!summary) return null;

  const getRiskLevel = () => {
    if (summary.high_severity_count > 0) {
      return { level: 'HIGH RISK', color: 'text-red-600', bgColor: 'bg-red-50', borderColor: 'border-red-300' };
    } else if (summary.medium_severity_count > 0) {
      return { level: 'MEDIUM RISK', color: 'text-orange-600', bgColor: 'bg-orange-50', borderColor: 'border-orange-300' };
    } else if (summary.low_severity_count > 0) {
      return { level: 'LOW RISK', color: 'text-yellow-600', bgColor: 'bg-yellow-50', borderColor: 'border-yellow-300' };
    }
    return { level: 'NO ISSUES', color: 'text-green-600', bgColor: 'bg-green-50', borderColor: 'border-green-300' };
  };

  const risk = getRiskLevel();

  return (
    <div className={`${risk.bgColor} border ${risk.borderColor} rounded-lg shadow-md p-6 mb-6`}>
      <h2 className="text-2xl font-bold text-gray-900 mb-4">Executive Summary</h2>

      {/* Overall Risk */}
      <div className="mb-6">
        <div className="flex items-center gap-2 mb-2">
          <span className="text-sm font-medium text-gray-700">Overall Risk Level:</span>
          <span className={`text-lg font-bold ${risk.color}`}>{risk.level}</span>
        </div>
      </div>

      {/* Statistics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {/* Total Issues */}
        <div className="bg-white rounded-lg p-4 shadow-sm">
          <div className="text-sm text-gray-600 mb-1">Total Issues</div>
          <div className="text-3xl font-bold text-gray-900">{summary.total_issues}</div>
        </div>

        {/* High Severity */}
        <div className="bg-white rounded-lg p-4 shadow-sm">
          <div className="flex items-center gap-2 mb-1">
            <AlertCircle className="h-4 w-4 text-red-600" />
            <span className="text-sm text-gray-600">Critical</span>
          </div>
          <div className="text-3xl font-bold text-red-600">{summary.high_severity_count}</div>
        </div>

        {/* Medium Severity */}
        <div className="bg-white rounded-lg p-4 shadow-sm">
          <div className="flex items-center gap-2 mb-1">
            <AlertTriangle className="h-4 w-4 text-orange-600" />
            <span className="text-sm text-gray-600">Medium</span>
          </div>
          <div className="text-3xl font-bold text-orange-600">{summary.medium_severity_count}</div>
        </div>

        {/* Low Severity */}
        <div className="bg-white rounded-lg p-4 shadow-sm">
          <div className="flex items-center gap-2 mb-1">
            <Info className="h-4 w-4 text-yellow-600" />
            <span className="text-sm text-gray-600">Low</span>
          </div>
          <div className="text-3xl font-bold text-yellow-600">{summary.low_severity_count}</div>
        </div>
      </div>

      {/* Performance Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Processing Time */}
        <div className="bg-white rounded-lg p-4 shadow-sm">
          <div className="flex items-center gap-2 mb-1">
            <Clock className="h-4 w-4 text-blue-600" />
            <span className="text-sm text-gray-600">Processing Time</span>
          </div>
          <div className="text-2xl font-semibold text-gray-900">
            {summary.total_processing_time.toFixed(2)}s
          </div>
        </div>

        {/* Cache Hit Rate */}
        <div className="bg-white rounded-lg p-4 shadow-sm">
          <div className="flex items-center gap-2 mb-1">
            <Zap className="h-4 w-4 text-green-600" />
            <span className="text-sm text-gray-600">Cache Hit Rate</span>
          </div>
          <div className="text-2xl font-semibold text-green-600">
            {summary.cache_hit_rate.toFixed(0)}%
          </div>
        </div>

        {/* Agents Completed */}
        <div className="bg-white rounded-lg p-4 shadow-sm">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-sm text-gray-600">Agents Completed</span>
          </div>
          <div className="text-2xl font-semibold text-gray-900">
            {summary.agents_completed}/5
          </div>
        </div>
      </div>
    </div>
  );
};

export default ExecutiveSummary;
