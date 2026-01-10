import { useState } from 'react';
import { AlertCircle } from 'lucide-react';
import UploadSection from './components/UploadSection';
import ProgressIndicator from './components/ProgressIndicator';
import RealTimeIssueStream from './components/RealTimeIssueStream';
import { useStreamingAnalysis } from './hooks/useStreamingAnalysis';

function App() {
  const {
    results,
    progress,
    loading,
    error,
    cacheHits,
    summary,
    startAnalysis,
    clearResults,
  } = useStreamingAnalysis();

  const [showResults, setShowResults] = useState(false);

  const handleAnalyze = async (content, llmProvider) => {
    setShowResults(true);
    await startAnalysis(content, llmProvider);
  };

  const handleClearResults = () => {
    clearResults();
    setShowResults(false);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <h1 className="text-3xl font-bold text-blue-600">
            Discharge Summary Validator
          </h1>
          <p className="mt-1 text-sm text-gray-600">
            Real-time validation with AI-powered analysis
          </p>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Upload Section */}
        <UploadSection onAnalyze={handleAnalyze} loading={loading} />

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border border-red-300 rounded-lg p-4 mb-6 flex items-start gap-3">
            <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="font-semibold text-red-900">Error</h3>
              <p className="text-sm text-red-700 mt-1">{error}</p>
            </div>
          </div>
        )}

        {/* Progress Indicator */}
        {showResults && loading && (
          <ProgressIndicator
            progress={progress}
            cacheHits={cacheHits}
            totalAgents={5}
          />
        )}

        {/* Results Stream */}
        {showResults && (
          <>
            <RealTimeIssueStream
              results={results}
              loading={loading}
              summary={summary}
            />

            {/* Clear Results Button */}
            {summary && !loading && (
              <div className="mt-6 flex justify-center">
                <button
                  onClick={handleClearResults}
                  className="px-6 py-3 bg-gray-600 text-white rounded-md font-medium hover:bg-gray-700 transition-colors"
                >
                  Clear Results & Start New Analysis
                </button>
              </div>
            )}
          </>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-sm text-gray-600">
            Discharge Summary Validator MVP - Real-time AI-powered validation with dual LLM support
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
