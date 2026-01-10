import { useState } from 'react';
import { ChevronDown, ChevronUp, AlertCircle, AlertTriangle, Info } from 'lucide-react';

const IssueCard = ({ issue }) => {
  const [expanded, setExpanded] = useState(false);

  const getSeverityConfig = (severity) => {
    switch (severity) {
      case 'HIGH':
        return {
          bgColor: 'bg-red-50',
          borderColor: 'border-red-300',
          textColor: 'text-red-800',
          badgeBg: 'bg-red-100',
          icon: AlertCircle,
        };
      case 'MEDIUM':
        return {
          bgColor: 'bg-orange-50',
          borderColor: 'border-orange-300',
          textColor: 'text-orange-800',
          badgeBg: 'bg-orange-100',
          icon: AlertTriangle,
        };
      case 'LOW':
        return {
          bgColor: 'bg-yellow-50',
          borderColor: 'border-yellow-300',
          textColor: 'text-yellow-800',
          badgeBg: 'bg-yellow-100',
          icon: Info,
        };
      default:
        return {
          bgColor: 'bg-gray-50',
          borderColor: 'border-gray-300',
          textColor: 'text-gray-800',
          badgeBg: 'bg-gray-100',
          icon: Info,
        };
    }
  };

  const config = getSeverityConfig(issue.severity);
  const Icon = config.icon;

  return (
    <div
      className={`${config.bgColor} border ${config.borderColor} rounded-lg p-4 mb-3 transition-all duration-200 hover:shadow-md`}
    >
      {/* Header */}
      <div
        className="flex items-start justify-between cursor-pointer"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-start gap-3 flex-1">
          <Icon className={`${config.textColor} h-5 w-5 mt-0.5 flex-shrink-0`} />
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              <span className={`inline-block px-2 py-0.5 ${config.badgeBg} ${config.textColor} text-xs font-semibold rounded`}>
                {issue.severity}
              </span>
              <span className="text-xs text-gray-500">
                {issue.type}
              </span>
            </div>
            <h4 className="font-medium text-gray-900 mb-1">
              {issue.location}
            </h4>
            <p className="text-sm text-gray-700 line-clamp-2">
              {issue.explanation}
            </p>
          </div>
        </div>
        <button className="ml-2 text-gray-400 hover:text-gray-600 flex-shrink-0">
          {expanded ? <ChevronUp className="h-5 w-5" /> : <ChevronDown className="h-5 w-5" />}
        </button>
      </div>

      {/* Expanded Details */}
      {expanded && (
        <div className="mt-4 pl-8 space-y-3 border-t border-gray-200 pt-3">
          <div>
            <label className="text-xs font-semibold text-gray-600 uppercase">
              Current:
            </label>
            <p className="text-sm text-gray-800 mt-1 bg-white p-2 rounded border border-gray-200">
              {issue.current}
            </p>
          </div>
          <div>
            <label className="text-xs font-semibold text-gray-600 uppercase">
              Suggestion:
            </label>
            <p className="text-sm text-gray-800 mt-1 bg-white p-2 rounded border border-gray-200">
              {issue.suggestion}
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default IssueCard;
