from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime

class CompanyInfo(BaseModel):
    name: str
    website: str
    industry: str
    founded_year: Optional[int]
    location: Optional[str]
    founders: Optional[List[str]]

class MarketPosition(BaseModel):
    target_audience: List[str]
    brand_reputation: str
    value_propositions: List[str]

class ProductService(BaseModel):
    features: List[str]
    pricing: Dict[str, str]
    differentiators: List[str]

class OnlinePresence(BaseModel):
    website_traffic: Optional[str]
    domain_authority: Optional[int]
    social_media: Dict[str, str]
    content_strategy: Optional[str]

class CustomerSentiment(BaseModel):
    positive_feedback: List[str]
    negative_feedback: List[str]
    common_pain_points: List[str]
    praise_points: List[str]

class BusinessGrowth(BaseModel):
    funding_rounds: Optional[List[Dict[str, str]]]
    revenue_estimates: Optional[str]
    partnerships: List[str]
    market_growth: str

class TechnologyStack(BaseModel):
    tools: List[str]
    ai_ml_usage: Optional[str]
    frameworks: List[str]
    platform_details: str

class MarketingStrategy(BaseModel):
    campaigns: List[str]
    channels: List[str]
    positioning: str
    engagement_metrics: Optional[Dict[str, str]]

class CompetitorProfile(BaseModel):
    company_info: CompanyInfo
    market_position: MarketPosition
    product_service: ProductService
    online_presence: OnlinePresence
    customer_sentiment: CustomerSentiment
    business_growth: BusinessGrowth
    tech_stack: TechnologyStack
    marketing_strategy: MarketingStrategy
    last_updated: datetime
    data_source: str

class CompetitorReport(BaseModel):
    executive_summary: str
    competitor_profiles: List[CompetitorProfile]
    swot_analysis: Dict[str, List[str]]
    feature_comparison: Dict[str, Dict[str, bool]]
    strategic_recommendations: List[str]