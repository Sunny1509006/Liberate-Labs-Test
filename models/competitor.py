from pydantic import BaseModel
from typing import List, Dict, Optional

class CompetitorProfile(BaseModel):
    name: str
    website: str
    description: str
    key_features: List[str]
    market_position: str
    strengths: List[str]
    weaknesses: List[str]

class CompetitorReport(BaseModel):
    executive_summary: str
    competitor_profiles: List[CompetitorProfile]
    swot_analysis: Dict[str, List[str]]
    feature_comparison: Dict[str, Dict[str, bool]]
    strategic_recommendations: List[str]
    
    class Config:
        schema_extra = {
            "example": {
                "executive_summary": "Comprehensive analysis of the competitive landscape...",
                "competitor_profiles": [],
                "swot_analysis": {
                    "strengths": ["Strong market presence", "Innovative features"],
                    "weaknesses": ["Limited integration capabilities"],
                    "opportunities": ["Expanding market", "New technology adoption"],
                    "threats": ["Increasing competition", "Market saturation"]
                },
                "feature_comparison": {},
                "strategic_recommendations": [
                    "Focus on AI capabilities",
                    "Expand integration ecosystem"
                ]
            }
        }