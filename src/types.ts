export interface SearchResult {
    title: string;
    url: string;
    snippet: string;
    analysis: string;
    data_source: string;
    last_updated?: Date;
  }
  
  export interface CompetitorAnalysis {
    website: string;
    name: string;
    key_features: string[];
    target_market: string;
    pricing_model: string;
    unique_selling_points: string[];
    data_source: string;
    last_updated?: Date;
  }
  
  export interface SwotAnalysis {
    strengths: string[];
    weaknesses: string[];
    opportunities: string[];
    threats: string[];
  }
  
  export interface ComparisonResult {
    main_product?: CompetitorAnalysis;
    competitors: CompetitorAnalysis[];
    competitive_advantages: string[];
    competitive_disadvantages: string[];
  }
  
  export interface DataSourceInfo {
    search_results_from_cache: boolean;
    competitors_from_cache: string[];
    fresh_competitors: string[];
    last_cache_update?: Date;
  }
  
  export interface SearchResponse {
    query: string;
    results: SearchResult[];
    swot_analysis: SwotAnalysis;
    comparison?: ComparisonResult;
    data_source_info: DataSourceInfo;
  }