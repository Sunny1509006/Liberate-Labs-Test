import React from 'react';
import { SearchResponse } from '../types';

interface AnalysisResultsProps {
  results: SearchResponse;
}

const AnalysisResults: React.FC<AnalysisResultsProps> = ({ results }) => {
  return (
    <div className="mt-8 space-y-8">
      {/* SWOT Analysis */}
      <div className="bg-white shadow overflow-hidden sm:rounded-lg">
        <div className="px-4 py-5 sm:px-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900">SWOT Analysis</h3>
        </div>
        <div className="border-t border-gray-200">
          <div className="grid grid-cols-2 gap-4 p-4">
            <div className="bg-green-50 p-4 rounded">
              <h4 className="font-semibold text-green-800">Strengths</h4>
              <ul className="mt-2 list-disc list-inside text-green-700">
                {results.swot_analysis.strengths.map((strength, index) => (
                  <li key={index}>{strength}</li>
                ))}
              </ul>
            </div>
            <div className="bg-red-50 p-4 rounded">
              <h4 className="font-semibold text-red-800">Weaknesses</h4>
              <ul className="mt-2 list-disc list-inside text-red-700">
                {results.swot_analysis.weaknesses.map((weakness, index) => (
                  <li key={index}>{weakness}</li>
                ))}
              </ul>
            </div>
            <div className="bg-blue-50 p-4 rounded">
              <h4 className="font-semibold text-blue-800">Opportunities</h4>
              <ul className="mt-2 list-disc list-inside text-blue-700">
                {results.swot_analysis.opportunities.map((opportunity, index) => (
                  <li key={index}>{opportunity}</li>
                ))}
              </ul>
            </div>
            <div className="bg-yellow-50 p-4 rounded">
              <h4 className="font-semibold text-yellow-800">Threats</h4>
              <ul className="mt-2 list-disc list-inside text-yellow-700">
                {results.swot_analysis.threats.map((threat, index) => (
                  <li key={index}>{threat}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* Search Results */}
      <div className="bg-white shadow overflow-hidden sm:rounded-lg">
        <div className="px-4 py-5 sm:px-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900">Search Results</h3>
        </div>
        <div className="border-t border-gray-200">
          <ul className="divide-y divide-gray-200">
            {results.results.map((result, index) => (
              <li key={index} className="px-4 py-4">
                <div className="space-y-2">
                  <h4 className="text-lg font-medium">
                    <a href={result.url} target="_blank" rel="noopener noreferrer" className="text-indigo-600 hover:text-indigo-900">
                      {result.title}
                    </a>
                  </h4>
                  <p className="text-sm text-gray-600">{result.snippet}</p>
                  <p className="text-sm text-gray-500">{result.analysis}</p>
                  <div className="text-xs text-gray-400">
                    Source: {result.data_source} | Last Updated: {result.last_updated?.toString()}
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Competitor Comparison */}
      {results.comparison && (
        <div className="bg-white shadow overflow-hidden sm:rounded-lg">
          <div className="px-4 py-5 sm:px-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900">Competitor Comparison</h3>
          </div>
          <div className="border-t border-gray-200 px-4 py-4">
            <div className="space-y-4">
              <div>
                <h4 className="font-medium text-gray-900">Competitive Advantages</h4>
                <ul className="mt-2 list-disc list-inside text-green-600">
                  {results.comparison.competitive_advantages.map((advantage, index) => (
                    <li key={index}>{advantage}</li>
                  ))}
                </ul>
              </div>
              <div>
                <h4 className="font-medium text-gray-900">Competitive Disadvantages</h4>
                <ul className="mt-2 list-disc list-inside text-red-600">
                  {results.comparison.competitive_disadvantages.map((disadvantage, index) => (
                    <li key={index}>{disadvantage}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AnalysisResults;