from pydantic import BaseModel
from typing import Optional, List

class AnalysisRequest(BaseModel):
    query: str
    num_results: Optional[int] = 10
    competitors: Optional[List[str]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "project management software comparison",
                "num_results": 5,
                "competitors": [
                    "asana.com",
                    "monday.com"
                ]
            }
        }