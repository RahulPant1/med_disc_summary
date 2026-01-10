import { Zap } from 'lucide-react';

const ProgressIndicator = ({ progress, cacheHits, totalAgents = 5 }) => {
  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      <div className="mb-4">
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm font-medium text-gray-700">
            Analysis Progress
          </span>
          <span className="text-sm font-semibold text-blue-600">
            {Math.round(progress)}%
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3">
          <div
            className="bg-blue-600 h-3 rounded-full transition-all duration-500 ease-out"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {cacheHits > 0 && (
        <div className="flex items-center gap-2 text-sm text-green-600">
          <Zap className="h-4 w-4" />
          <span>
            {cacheHits}/{totalAgents} results from cache (
            {Math.round((cacheHits / totalAgents) * 100)}% hit rate)
          </span>
        </div>
      )}
    </div>
  );
};

export default ProgressIndicator;
