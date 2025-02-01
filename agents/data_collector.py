from typing import List, Dict
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from models.request import AnalysisRequest
import os
from dotenv import load_dotenv

class DataCollectorAgent:
    def __init__(self):
        load_dotenv()
        
        # Validate API keys
        self.crunchbase_api_key = os.getenv("CRUNCHBASE_API_KEY")
        self.g2_api_key = os.getenv("G2_API_KEY")
        
        if not self.crunchbase_api_key:
            raise ValueError("CRUNCHBASE_API_KEY environment variable is not set")
        if not self.g2_api_key:
            raise ValueError("G2_API_KEY environment variable is not set")

    async def collect_data(self, request: AnalysisRequest) -> Dict:
        """
        Collect data from multiple sources in parallel
        """
        async with aiohttp.ClientSession() as session:
            tasks = [
                self._fetch_crunchbase_data(session, request),
                self._fetch_linkedin_data(session, request),
                self._fetch_g2_data(session, request)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out any exceptions and combine successful results
            valid_results = [r for r in results if not isinstance(r, Exception)]
            combined_data = self._normalize_data(valid_results)
            return combined_data

    async def _fetch_crunchbase_data(self, session: aiohttp.ClientSession, request: AnalysisRequest) -> Dict:
        """Fetch data from Crunchbase API"""
        try:
            # Example URL - replace with actual Crunchbase API endpoint
            url = f"https://api.crunchbase.com/v3.1/organizations"
            headers = {"X-CB-User-Key": self.crunchbase_api_key}
            params = {"name": request.query} if request.query else {}
            
            async with session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    return await response.json()
                return {"error": f"Crunchbase API error: {response.status}"}
        except Exception as e:
            return {"error": f"Crunchbase API error: {str(e)}"}

    async def _fetch_linkedin_data(self, session: aiohttp.ClientSession, request: AnalysisRequest) -> Dict:
        """Fetch data from LinkedIn"""
        try:
            if not request.target_competitors:
                return {"error": "No target competitors specified"}
                
            results = {}
            for competitor in request.target_competitors:
                # Note: This is a simplified example. Real LinkedIn data collection
                # would require proper authentication and API usage
                url = f"https://www.linkedin.com/company/{competitor}"
                async with session.get(url) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        results[competitor] = {
                            "name": competitor,
                            "description": soup.find("meta", {"name": "description"})["content"] if soup.find("meta", {"name": "description"}) else "",
                        }
            return results
        except Exception as e:
            return {"error": f"LinkedIn data collection error: {str(e)}"}

    async def _fetch_g2_data(self, session: aiohttp.ClientSession, request: AnalysisRequest) -> Dict:
        """Fetch data from G2 API"""
        try:
            # Example URL - replace with actual G2 API endpoint
            url = "https://api.g2.com/products"
            headers = {"Authorization": f"Bearer {self.g2_api_key}"}
            params = {"q": request.query} if request.query else {}
            
            async with session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    return await response.json()
                return {"error": f"G2 API error: {response.status}"}
        except Exception as e:
            return {"error": f"G2 API error: {str(e)}"}

    def _normalize_data(self, raw_data: List[Dict]) -> Dict:
        """Normalize and consolidate data from different sources"""
        normalized = {
            "competitors": [],
            "market_insights": []
        }
        
        for data in raw_data:
            if isinstance(data, dict):
                if "error" not in data:
                    # Process valid data and add to normalized structure
                    if "competitors" in normalized:
                        normalized["competitors"].extend(self._extract_competitor_data(data))
                    if "market_insights" in normalized:
                        normalized["market_insights"].extend(self._extract_market_insights(data))
        
        return normalized

    def _extract_competitor_data(self, data: Dict) -> List[Dict]:
        """Extract competitor information from raw data"""
        competitors = []
        # Implementation depends on the structure of your data
        # This is a simplified example
        if "items" in data:
            for item in data["items"]:
                competitor = {
                    "name": item.get("name", ""),
                    "website": item.get("website", ""),
                    "description": item.get("description", ""),
                    "key_features": item.get("features", []),
                    "market_position": item.get("market_position", ""),
                    "strengths": item.get("strengths", []),
                    "weaknesses": item.get("weaknesses", [])
                }
                competitors.append(competitor)
        return competitors

    def _extract_market_insights(self, data: Dict) -> List[Dict]:
        """Extract market insights from raw data"""
        insights = []
        # Implementation depends on the structure of your data
        # This is a simplified example
        if "market_data" in data:
            for insight in data["market_data"]:
                insights.append({
                    "trend": insight.get("trend", ""),
                    "impact": insight.get("impact", ""),
                    "recommendation": insight.get("recommendation", "")
                })
        return insights