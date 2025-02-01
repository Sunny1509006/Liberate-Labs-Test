from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime

class SearchResult(BaseModel):
    title: str
    url: str
    snippet: str
    analysis: str
    data_source: str = "new"  # "new" or "cached"
    last_updated: Optional[datetime] = None

class CompetitorAnalysis(BaseModel):
    website: str
    name: str
    key_features: List[str]
    target_market: str
    pricing_model: str
    unique_selling_points: List[str]
    data_source: str = "new"  # "new" or "cached"
    last_updated: Optional[datetime] = None

class SwotAnalysis(BaseModel):
    strengths: List[str]
    weaknesses: List[str]
    opportunities: List[str]
    threats: List[str]

class ComparisonResult(BaseModel):
    main_product: Optional[CompetitorAnalysis]
    competitors: List[CompetitorAnalysis]
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
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "project management software comparison",
                "results": [
                    {
                        "title": "Best Project Management Software 2024",
                        "url": "https://example.com/article",
                        "snippet": "Detailed comparison of top project management tools...",
                        "analysis": "This article provides a comprehensive comparison...",
                        "data_source": "new",
                        "last_updated": "2024-01-01T12:00:00"
                    }
                ],
                "swot_analysis": {
                    "strengths": [
                        "Strong market presence",
                        "Advanced feature set"
                    ],
                    "weaknesses": [
                        "Higher pricing",
                        "Complex learning curve"
                    ],
                    "opportunities": [
                        "Growing remote work market",
                        "Integration possibilities"
                    ],
                    "threats": [
                        "Increasing competition",
                        "Market saturation"
                    ]
                },
                "comparison": {
                    "main_product": {
                        "website": "https://example.com",
                        "name": "Example Software",
                        "key_features": ["Feature 1", "Feature 2"],
                        "target_market": "Enterprise",
                        "pricing_model": "Per user/month",
                        "unique_selling_points": ["USP 1", "USP 2"],
                        "data_source": "new",
                        "last_updated": "2024-01-01T12:00:00"
                    },
                    "competitors": [
                        {
                            "website": "https://competitor.com",
                            "name": "Competitor Software",
                            "key_features": ["Feature A", "Feature B"],
                            "target_market": "SMB",
                            "pricing_model": "Flat rate",
                            "unique_selling_points": ["USP A", "USP B"],
                            "data_source": "cached",
                            "last_updated": "2024-01-01T10:00:00"
                        }
                    ],
                    "competitive_advantages": [
                        "Better pricing model",
                        "More integrations"
                    ],
                    "competitive_disadvantages": [
                        "Less features",
                        "Limited support"
                    ]
                },
                "data_source_info": {
                    "search_results_from_cache": True,
                    "competitors_from_cache": ["competitor.com"],
                    "fresh_competitors": ["newcompetitor.com"],
                    "last_cache_update": "2024-01-01T12:00:00"
                }
            }
        }