import React, { useState } from 'react';
import { QueryClient, QueryClientProvider } from 'react-query';
import SearchForm from './components/SearchForm';
import AnalysisResults from './components/AnalysisResults';
import { SearchResponse } from './types';

const queryClient = new QueryClient();

function App() {
  const [results, setResults] = useState<SearchResponse | null>(null);

  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen bg-gray-50">
        <header className="bg-white shadow">
          <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
            <h1 className="text-3xl font-bold text-gray-900">
              Competitor Analysis Tool
            </h1>
          </div>
        </header>
        <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <div className="px-4 py-6 sm:px-0">
            <SearchForm onResults={setResults} />
            {results && <AnalysisResults results={results} />}
          </div>
        </main>
      </div>
    </QueryClientProvider>
  );
}

export default App;