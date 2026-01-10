import { useState } from 'react';
import { Upload, FileText } from 'lucide-react';

const UploadSection = ({ onAnalyze, loading }) => {
  const [content, setContent] = useState('');
  const [llmProvider, setLlmProvider] = useState('gemini');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (content.trim() && !loading) {
      onAnalyze(content, llmProvider);
    }
  };

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => {
        setContent(event.target.result);
      };
      reader.readAsText(file);
    }
  };

  const handleClear = () => {
    setContent('');
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-4 flex items-center gap-2">
        <FileText className="text-blue-600" />
        Discharge Summary Validator
      </h2>

      <form onSubmit={handleSubmit}>
        {/* LLM Provider Selection */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Select LLM Provider
          </label>
          <div className="flex gap-4">
            <label className="flex items-center cursor-pointer">
              <input
                type="radio"
                name="llm-provider"
                value="gemini"
                checked={llmProvider === 'gemini'}
                onChange={(e) => setLlmProvider(e.target.value)}
                className="mr-2"
                disabled={loading}
              />
              <span className="text-gray-700">Google Gemini</span>
            </label>
            <label className="flex items-center cursor-pointer">
              <input
                type="radio"
                name="llm-provider"
                value="claude"
                checked={llmProvider === 'claude'}
                onChange={(e) => setLlmProvider(e.target.value)}
                className="mr-2"
                disabled={loading}
              />
              <span className="text-gray-700">Anthropic Claude</span>
            </label>
          </div>
        </div>

        {/* Text Area */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Discharge Summary Content
          </label>
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="Paste discharge summary here..."
            className="w-full h-64 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            disabled={loading}
          />
        </div>

        {/* File Upload */}
        <div className="mb-4">
          <label className="inline-flex items-center px-4 py-2 bg-gray-100 text-gray-700 rounded-md cursor-pointer hover:bg-gray-200 transition-colors">
            <Upload className="mr-2 h-5 w-5" />
            Upload Text File
            <input
              type="file"
              accept=".txt,.md"
              onChange={handleFileUpload}
              className="hidden"
              disabled={loading}
            />
          </label>
          <span className="ml-3 text-sm text-gray-500">
            Supports .txt and .md files
          </span>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-3">
          <button
            type="submit"
            disabled={!content.trim() || loading}
            className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-md font-medium hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? 'Analyzing...' : 'Analyze Document'}
          </button>
          <button
            type="button"
            onClick={handleClear}
            disabled={loading}
            className="px-6 py-3 bg-gray-200 text-gray-700 rounded-md font-medium hover:bg-gray-300 disabled:bg-gray-100 disabled:cursor-not-allowed transition-colors"
          >
            Clear
          </button>
        </div>
      </form>
    </div>
  );
};

export default UploadSection;
