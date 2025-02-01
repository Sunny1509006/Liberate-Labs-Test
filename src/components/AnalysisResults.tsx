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

      {/* Competitor Profiles */}
      {results.comparison?.competitors.map((competitor, index) => (
        <div key={index} className="bg-white shadow overflow-hidden sm:rounded-lg">
          <div className="px-4 py-5 sm:px-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900">
              {competitor.company_info.name} - Competitor Analysis
            </h3>
          </div>
          <div className="border-t border-gray-200">
            <dl>
              {/* Company Overview */}
              <div className="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                <dt className="text-sm font-medium text-gray-500">Company Overview</dt>
                <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                  <p><strong>Industry:</strong> {competitor.company_info.industry}</p>
                  <p><strong>Founded:</strong> {competitor.company_info.founded_year || 'N/A'}</p>
                  <p><strong>Location:</strong> {competitor.company_info.location || 'N/A'}</p>
                  {competitor.company_info.founders && (
                    <p><strong>Founders:</strong> {competitor.company_info.founders.join(', ')}</p>
                  )}
                </dd>
              </div>

              {/* Market Positioning */}
              <div className="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                <dt className="text-sm font-medium text-gray-500">Market Positioning</dt>
                <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                  <p><strong>Target Audience:</strong> {competitor.market_position.target_audience.join(', ')}</p>
                  <p><strong>Brand Reputation:</strong> {competitor.market_position.brand_reputation}</p>
                  <div>
                    <strong>Value Propositions:</strong>
                    <ul className="list-disc pl-5 mt-1">
                      {competitor.market_position.value_propositions.map((prop, idx) => (
                        <li key={idx}>{prop}</li>
                      ))}
                    </ul>
                  </div>
                </dd>
              </div>

              {/* Product & Service */}
              <div className="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                <dt className="text-sm font-medium text-gray-500">Product & Service</dt>
                <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                  <div className="mb-3">
                    <strong>Key Features:</strong>
                    <ul className="list-disc pl-5 mt-1">
                      {competitor.product_service.features.map((feature, idx) => (
                        <li key={idx}>{feature}</li>
                      ))}
                    </ul>
                  </div>
                  <div className="mb-3">
                    <strong>Pricing:</strong>
                    <ul className="list-none pl-5 mt-1">
                      {Object.entries(competitor.product_service.pricing).map(([plan, price], idx) => (
                        <li key={idx}>{plan}: {price}</li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <strong>Differentiators:</strong>
                    <ul className="list-disc pl-5 mt-1">
                      {competitor.product_service.differentiators.map((diff, idx) => (
                        <li key={idx}>{diff}</li>
                      ))}
                    </ul>
                  </div>
                </dd>
              </div>

              {/* Online Presence */}
              <div className="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                <dt className="text-sm font-medium text-gray-500">Online Presence</dt>
                <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                  <p><strong>Website Traffic:</strong> {competitor.online_presence.website_traffic || 'N/A'}</p>
                  <p><strong>Domain Authority:</strong> {competitor.online_presence.domain_authority || 'N/A'}</p>
                  <div className="mb-3">
                    <strong>Social Media Presence:</strong>
                    <ul className="list-none pl-5 mt-1">
                      {Object.entries(competitor.online_presence.social_media).map(([platform, metric], idx) => (
                        <li key={idx}>{platform}: {metric}</li>
                      ))}
                    </ul>
                  </div>
                  <p><strong>Content Strategy:</strong> {competitor.online_presence.content_strategy || 'N/A'}</p>
                </dd>
              </div>

              {/* Customer Sentiment */}
              <div className="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                <dt className="text-sm font-medium text-gray-500">Customer Sentiment</dt>
                <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                  <div className="mb-3">
                    <strong>Positive Feedback:</strong>
                    <ul className="list-disc pl-5 mt-1">
                      {competitor.customer_sentiment.positive_feedback.map((feedback, idx) => (
                        <li key={idx}>{feedback}</li>
                      ))}
                    </ul>
                  </div>
                  <div className="mb-3">
                    <strong>Negative Feedback:</strong>
                    <ul className="list-disc pl-5 mt-1">
                      {competitor.customer_sentiment.negative_feedback.map((feedback, idx) => (
                        <li key={idx}>{feedback}</li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <strong>Common Pain Points:</strong>
                    <ul className="list-disc pl-5 mt-1">
                      {competitor.customer_sentiment.common_pain_points.map((point, idx) => (
                        <li key={idx}>{point}</li>
                      ))}
                    </ul>
                  </div>
                </dd>
              </div>

              {/* Business Growth */}
              <div className="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                <dt className="text-sm font-medium text-gray-500">Business Growth</dt>
                <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                  {competitor.business_growth.funding_rounds && (
                    <div className="mb-3">
                      <strong>Funding Rounds:</strong>
                      <ul className="list-none pl-5 mt-1">
                        {competitor.business_growth.funding_rounds.map((round, idx) => (
                          <li key={idx}>
                            {Object.entries(round).map(([key, value]) => `${key}: ${value}`).join(', ')}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                  <p><strong>Revenue Estimates:</strong> {competitor.business_growth.revenue_estimates || 'N/A'}</p>
                  <div className="mb-3">
                    <strong>Partnerships:</strong>
                    <ul className="list-disc pl-5 mt-1">
                      {competitor.business_growth.partnerships.map((partnership, idx) => (
                        <li key={idx}>{partnership}</li>
                      ))}
                    </ul>
                  </div>
                  <p><strong>Market Growth:</strong> {competitor.business_growth.market_growth}</p>
                </dd>
              </div>

              {/* Technology Stack */}
              <div className="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                <dt className="text-sm font-medium text-gray-500">Technology Stack</dt>
                <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                  <div className="mb-3">
                    <strong>Tools:</strong>
                    <ul className="list-disc pl-5 mt-1">
                      {competitor.tech_stack.tools.map((tool, idx) => (
                        <li key={idx}>{tool}</li>
                      ))}
                    </ul>
                  </div>
                  {competitor.tech_stack.ai_ml_usage && (
                    <p><strong>AI/ML Usage:</strong> {competitor.tech_stack.ai_ml_usage}</p>
                  )}
                  <div className="mb-3">
                    <strong>Frameworks:</strong>
                    <ul className="list-disc pl-5 mt-1">
                      {competitor.tech_stack.frameworks.map((framework, idx) => (
                        <li key={idx}>{framework}</li>
                      ))}
                    </ul>
                  </div>
                  <p><strong>Platform Details:</strong> {competitor.tech_stack.platform_details}</p>
                </dd>
              </div>

              {/* Marketing Strategy */}
              <div className="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                <dt className="text-sm font-medium text-gray-500">Marketing Strategy</dt>
                <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                  <div className="mb-3">
                    <strong>Campaigns:</strong>
                    <ul className="list-disc pl-5 mt-1">
                      {competitor.marketing_strategy.campaigns.map((campaign, idx) => (
                        <li key={idx}>{campaign}</li>
                      ))}
                    </ul>
                  </div>
                  <div className="mb-3">
                    <strong>Marketing Channels:</strong>
                    <ul className="list-disc pl-5 mt-1">
                      {competitor.marketing_strategy.channels.map((channel, idx) => (
                        <li key={idx}>{channel}</li>
                      ))}
                    </ul>
                  </div>
                  <p><strong>Brand Positioning:</strong> {competitor.marketing_strategy.positioning}</p>
                  {competitor.marketing_strategy.engagement_metrics && (
                    <div>
                      <strong>Engagement Metrics:</strong>
                      <ul className="list-none pl-5 mt-1">
                        {Object.entries(competitor.marketing_strategy.engagement_metrics).map(([metric, value], idx) => (
                          <li key={idx}>{metric}: {value}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </dd>
              </div>
            </dl>
          </div>
        </div>
      ))}

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
    </div>
  );
};

export default AnalysisResults;