from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
from .competitor import CompetitorProfile

class SearchResult(BaseModel):
    title: str
    url: str
    snippet: str
    analysis: str
    data_source: str = "new"
    last_updated: Optional[datetime] = None

class SwotAnalysis(BaseModel):
    strengths: List[str]
    weaknesses: List[str]
    opportunities: List[str]
    threats: List[str]

class ComparisonResult(BaseModel):
    main_product: Optional[CompetitorProfile] = None  # Make it optional with a default value
    competitors: List[CompetitorProfile]
    competitive_advantages: List[str]
    competitive_disadvantages: List[str]

class DataSourceInfo(BaseModel):
    search_results_from_cache: bool = False
    competitors_from_cache: List[str] = []
    fresh_competitors: List[str] = []
    last_cache_update: Optional[datetime] = None

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    swot_analysis: SwotAnalysis
    comparison: Optional[ComparisonResult]
    data_source_info: DataSourceInfo