import React, { useState } from 'react';
import { useMutation } from 'react-query';
import axios from 'axios';
import { SearchResponse } from '../types';

interface SearchFormProps {
  onResults: (results: SearchResponse) => void;
}

const SearchForm: React.FC<SearchFormProps> = ({ onResults }) => {
  const [query, setQuery] = useState('');
  const [competitors, setCompetitors] = useState<string[]>(['']);
  const [searchIndex, setSearchIndex] = useState('');

  const mutation = useMutation(
    async (data: { query: string; competitors: string[]; num_results: number }) => {
      const response = await axios.post('http://127.0.0.1:8000/search', data);
      return response.data;
    },
    {
      onSuccess: (data) => {
        onResults(data);
      },
    }
  );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const validCompetitors = competitors.filter(c => c.trim() !== '');
    mutation.mutate({
      query,
      competitors: validCompetitors,
      num_results: 10 // Default to 10 results
    });
  };

  const addCompetitor = () => {
    setCompetitors([...competitors, '']);
  };

  const updateCompetitor = (index: number, value: string) => {
    const newCompetitors = [...competitors];
    newCompetitors[index] = value;
    setCompetitors(newCompetitors);
  };

  const removeCompetitor = (index: number) => {
    const newCompetitors = competitors.filter((_, i) => i !== index);
    setCompetitors(newCompetitors);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6 bg-white shadow px-4 py-5 sm:rounded-lg sm:p-6">
      <div>
        <label htmlFor="query" className="block text-sm font-medium text-gray-700">
          Search Query
        </label>
        <div className="mt-1">
          <input
          style={{padding: '10px'}}
            type="text"
            name="query"
            id="query"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
            placeholder="Enter your search query"
            required
          />
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">
          Competitors
        </label>
        <div className="mt-1 space-y-2">
          {competitors.map((competitor, index) => (
            <div key={index} className="flex items-center space-x-2">
              <div className="flex-grow relative">
                {index > 0 && (
                  <div className="absolute right-0 top-0 -mt-[40px]">
                    <button
                      type="button"
                      onClick={() => removeCompetitor(index -1)}
                      className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-red-700 bg-red-100 hover:bg-red-200"
                    >
                      Remove
                    </button>
                  </div>
                )}
                <br/>
                <input
                style={{padding: '10px'}}
                  type="text"
                  value={competitor}
                  onChange={(e) => updateCompetitor(index, e.target.value)}
                  className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
                  placeholder="Enter competitor name or URL"
                />
              </div>
            </div>
          ))}
          <button
            type="button"
            onClick={addCompetitor}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-indigo-700 bg-indigo-100 hover:bg-indigo-200"
          >
            Add Competitor
          </button>
        </div>
      </div>

      <div>
        <label htmlFor="searchIndex" className="block text-sm font-medium text-gray-700">
          Search Query Index
        </label>
        <div className="mt-1">
          <input
          style={{padding: '10px'}}
            type="text"
            name="searchIndex"
            id="searchIndex"
            value={searchIndex}
            onChange={(e) => setSearchIndex(e.target.value)}
            className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
            placeholder="Enter search query index"
          />
        </div>
      </div>

      <div>
        <button
          type="submit"
          disabled={mutation.isLoading}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
        >
          {mutation.isLoading ? 'Analyzing...' : 'Analyze'}
        </button>
      </div>

      {mutation.isError && (
        <div className="rounded-md bg-red-50 p-4">
          <div className="text-sm text-red-700">
            An error occurred. Please try again.
          </div>
        </div>
      )}
    </form>
  );
};

export default SearchForm;