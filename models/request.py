from pydantic import BaseModel, HttpUrl
from typing import Optional, List

class AnalysisRequest(BaseModel):
    query: str
    num_results: Optional[int] = 10
    competitors: Optional[List[HttpUrl]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "project management software comparison",
                "num_results": 5,
                "competitors": [
                    "https://asana.com",
                    "https://monday.com"
                ]
            }
        }