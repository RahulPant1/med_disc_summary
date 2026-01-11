import { useState, useRef } from 'react';

/**
 * Custom hook for streaming analysis results via Server-Sent Events
 */
export const useStreamingAnalysis = () => {
  const [results, setResults] = useState({});
  const [progress, setProgress] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [cacheHits, setCacheHits] = useState(0);
  const [summary, setSummary] = useState(null);
  const eventSourceRef = useRef(null);

  const startAnalysis = async (content, llmProvider) => {
    // Reset state
    setResults({});
    setProgress(0);
    setLoading(true);
    setError(null);
    setCacheHits(0);
    setSummary(null);

    // Close existing connection if any
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    try {
      // Make POST request to start analysis
      const response = await fetch('/api/analyze/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content,
          llm_provider: llmProvider,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // Create EventSource from the response
      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      let buffer = '';

      const processStream = async () => {
        try {
          while (true) {
            const { done, value } = await reader.read();

            if (done) {
              // Process ALL remaining events in buffer before finishing
              if (buffer.trim()) {
                // Use correct delimiter for the platform (Windows: \r\n\r\n, Unix: \n\n)
                const finalDelimiter = buffer.includes('\r\n\r\n') ? '\r\n\r\n' : '\n\n';
                const finalLines = buffer.split(finalDelimiter).filter(line => line.trim());

                for (const line of finalLines) {
                  const eventMatch = line.match(/^event: (.+)$/m);
                  const dataMatch = line.match(/^data: (.+)$/m);

                  if (eventMatch && dataMatch) {
                    const eventType = eventMatch[1];
                    const data = JSON.parse(dataMatch[1]);
                    handleEvent(eventType, data);
                  }
                }
              }
              setLoading(false);
              break;
            }

            const chunk = decoder.decode(value, { stream: true });
            buffer += chunk;

            // Process complete events (handle both Unix \n\n and Windows \r\n\r\n)
            const delimiter = buffer.includes('\r\n\r\n') ? '\r\n\r\n' : '\n\n';
            const lines = buffer.split(delimiter);
            buffer = lines.pop() || '';

            for (const line of lines) {
              if (!line.trim()) continue;

              // Parse SSE format
              const eventMatch = line.match(/^event: (.+)$/m);
              const dataMatch = line.match(/^data: (.+)$/m);

              if (eventMatch && dataMatch) {
                const eventType = eventMatch[1];
                const data = JSON.parse(dataMatch[1]);
                handleEvent(eventType, data);
              }
            }
          }
        } catch (err) {
          console.error('Stream processing error:', err);
          setError(err.message);
          setLoading(false);
        }
      };

      processStream();

    } catch (err) {
      console.error('Analysis error:', err);
      setError(err.message);
      setLoading(false);
    }
  };

  const handleEvent = (eventType, data) => {
    switch (eventType) {
      case 'started':
        // Analysis started
        break;

      case 'agent_progress':
        setProgress(data.progress_percentage || 0);
        break;

      case 'agent_complete':
        // Update results with agent data
        setResults(prev => ({
          ...prev,
          [data.agent_name]: {
            issues: data.issues || [],
            from_cache: data.from_cache,
            processing_time: data.processing_time,
          }
        }));

        // Update progress
        setProgress(data.progress_percentage || 0);

        // Track cache hits
        if (data.from_cache) {
          setCacheHits(prev => prev + 1);
        }
        break;

      case 'analysis_complete':
        setSummary(data);
        setProgress(100);
        setLoading(false);
        break;

      case 'error':
        console.error('Analysis error:', data);
        setError(data.error);
        setLoading(false);
        break;

      default:
        console.warn('Unknown event type:', eventType);
    }
  };

  const stopAnalysis = () => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    setLoading(false);
  };

  const clearResults = () => {
    setResults({});
    setProgress(0);
    setError(null);
    setCacheHits(0);
    setSummary(null);
  };

  return {
    results,
    progress,
    loading,
    error,
    cacheHits,
    summary,
    startAnalysis,
    stopAnalysis,
    clearResults,
  };
};
