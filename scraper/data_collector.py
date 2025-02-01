import aiohttp
import asyncio
from bs4 import BeautifulSoup
from typing import List, Dict, Optional, Union
from models.request import AnalysisRequest
from models.response import (
    SearchResult, SearchResponse, SwotAnalysis,
    ComparisonResult, DataSourceInfo
)
from models.competitor import (
    CompetitorProfile, CompanyInfo, MarketPosition,
    ProductService, OnlinePresence, CustomerSentiment,
    BusinessGrowth, TechnologyStack, MarketingStrategy
)
import os
from dotenv import load_dotenv
from openai import OpenAI
import json
from urllib.parse import urlparse, quote_plus
from datetime import datetime
from .db_manager import DBManager

class DataCollector:
    def __init__(self):
        load_dotenv()
        
        # Initialize API keys
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.google_search_id = os.getenv("GOOGLE_SEARCH_ID")
        self.google_search_url = os.getenv("GOOGLE_CUSTOM_SEARCH_URL")
        
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        if not self.google_api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is not set")
        if not self.google_search_id:
            raise ValueError("GOOGLE_SEARCH_ID environment variable is not set")
        if not self.google_search_url:
            raise ValueError("GOOGLE_CUSTOM_SEARCH_URL environment variable is not set")
        
        self.client = OpenAI(api_key=self.openai_api_key)
        self.db_manager = DBManager()

    async def collect_data(self, request: AnalysisRequest) -> SearchResponse:
        """Collect and analyze data about competitors"""
        data_source_info = DataSourceInfo()
        
        # Check cache for search results
        cached_results = await self.db_manager.get_search_results(request.query)
        if cached_results:
            results = []
            for result in cached_results:
                result_data = result.copy()
                result_data['data_source'] = 'cached'
                result_data['last_updated'] = datetime.fromisoformat(result_data.get('last_updated', datetime.utcnow().isoformat()))
                results.append(SearchResult(**result_data))
            data_source_info.search_results_from_cache = True
            data_source_info.last_cache_update = results[0].last_updated if results else None
        else:
            # Perform new search
            results = await self._search_google(request.query, request.num_results)
            # Store new results
            await self.db_manager.store_search_results(
                request.query,
                [result.dict() for result in results]
            )
            for result in results:
                result.data_source = 'new'
                result.last_updated = datetime.utcnow()

        # Analyze competitors
        competitor_profiles = []
        if request.competitors:
            for competitor in request.competitors:
                # Check cache for competitor data
                cached_data = await self.db_manager.get_competitor_data(competitor)
                if cached_data:
                    cached_data['data_source'] = 'cached'
                    cached_data['last_updated'] = datetime.fromisoformat(cached_data.get('last_updated', datetime.utcnow().isoformat()))
                    profile = CompetitorProfile(**cached_data)
                    data_source_info.competitors_from_cache.append(competitor)
                else:
                    profile = await self._analyze_competitor(competitor)
                    profile.data_source = 'new'
                    profile.last_updated = datetime.utcnow()
                    # Store new competitor data
                    await self.db_manager.store_competitor_data(profile.dict())
                    data_source_info.fresh_competitors.append(competitor)
                competitor_profiles.append(profile)

        # Generate SWOT analysis
        swot_analysis = await self._generate_swot_analysis(request.query, results, competitor_profiles)

        # Generate comparison if competitors are provided
        comparison = None
        if competitor_profiles:
            comparison = ComparisonResult(
                competitors=competitor_profiles,
                competitive_advantages=await self._generate_competitive_analysis(results, competitor_profiles, True),
                competitive_disadvantages=await self._generate_competitive_analysis(results, competitor_profiles, False)
            )

        return SearchResponse(
            query=request.query,
            results=results,
            swot_analysis=swot_analysis,
            comparison=comparison,
            data_source_info=data_source_info
        )

    async def _search_google(self, query: str, num_results: int) -> List[SearchResult]:
        """Search using Google Custom Search API"""
        results = []
        try:
            search_url = f"{self.google_search_url}?key={self.google_api_key}&cx={self.google_search_id}&q={quote_plus(query)}&num={num_results}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(search_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        items = data.get('items', [])
                        
                        for item in items:
                            title = item.get('title', '')
                            url = item.get('link', '')
                            snippet = item.get('snippet', '')
                            
                            # Analyze the content using OpenAI
                            analysis = await self._analyze_content(title, snippet)
                            
                            results.append(SearchResult(
                                title=title,
                                url=url,
                                snippet=snippet,
                                analysis=analysis,
                                data_source='new',
                                last_updated=datetime.utcnow()
                            ))
                    else:
                        print(f"Error in Google search API: {response.status}")
        except Exception as e:
            print(f"Error in Google search: {str(e)}")
        
        return results

    async def _get_company_url(self, company_name: str) -> Optional[str]:
        """Get company website URL using Google Custom Search"""
        try:
            search_url = f"{self.google_search_url}?key={self.google_api_key}&cx={self.google_search_id}&q={quote_plus(company_name + ' official website')}&num=1"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(search_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        items = data.get('items', [])
                        if items:
                            return items[0].get('link')
            return None
        except Exception as e:
            print(f"Error finding company URL for {company_name}: {str(e)}")
            return None

    async def _analyze_content(self, title: str, content: str) -> str:
        """Analyze content using OpenAI"""
        try:
            prompt = f"""
            Please analyze this content and provide key insights in JSON format:

            Title: {title}
            Content: {content}

            Return a JSON object with this structure:
            {{
                "analysis": "string containing 2-3 sentences of insights"
            }}
            """

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert business analyst. Provide your analysis in JSON format."},
                    {"role": "user", "content": prompt}
                ],
                response_format={ "type": "json_object" }
            )
            
            analysis_data = json.loads(response.choices[0].message.content)
            return analysis_data.get('analysis', "Analysis not available")
        except Exception as e:
            print(f"Error in OpenAI analysis: {str(e)}")
            return "Analysis not available"

    async def _analyze_competitor(self, competitor: str) -> CompetitorProfile:
        """Analyze a competitor comprehensively"""
        try:
            # Get competitor website if not provided
            website = competitor if competitor.startswith(('http://', 'https://')) else await self._get_company_url(competitor)
            if not website:
                raise ValueError(f"Could not find website for {competitor}")

            # Collect data about the competitor
            async with aiohttp.ClientSession() as session:
                async with session.get(website) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Extract basic information
                        title = soup.title.string if soup.title else website
                        description = ""
                        meta_desc = soup.find('meta', {'name': 'description'})
                        if meta_desc:
                            description = meta_desc.get('content', '')

                        # Use OpenAI to analyze the competitor
                        analysis_prompt = f"""
                        Please analyze this company website and provide a detailed analysis in JSON format.

                        Website Information:
                        URL: {website}
                        Title: {title}
                        Description: {description}

                        Provide your analysis as a JSON object with the following structure:
                        {{
                            "company_info": {{
                                "name": "string",
                                "website": "string",
                                "industry": "string",
                                "founded_year": null,
                                "location": null,
                                "founders": null
                            }},
                            "market_position": {{
                                "target_audience": ["string"],
                                "brand_reputation": "string",
                                "value_propositions": ["string"]
                            }},
                            "product_service": {{
                                "features": ["string"],
                                "pricing": {{"plan_name": "price"}},
                                "differentiators": ["string"]
                            }},
                            "online_presence": {{
                                "website_traffic": null,
                                "domain_authority": null,
                                "social_media": {{}},
                                "content_strategy": null
                            }},
                            "customer_sentiment": {{
                                "positive_feedback": ["string"],
                                "negative_feedback": ["string"],
                                "common_pain_points": ["string"],
                                "praise_points": ["string"]
                            }},
                            "business_growth": {{
                                "funding_rounds": null,
                                "revenue_estimates": null,
                                "partnerships": ["string"],
                                "market_growth": "string"
                            }},
                            "tech_stack": {{
                                "tools": ["string"],
                                "ai_ml_usage": null,
                                "frameworks": ["string"],
                                "platform_details": "string"
                            }},
                            "marketing_strategy": {{
                                "campaigns": ["string"],
                                "channels": ["string"],
                                "positioning": "string",
                                "engagement_metrics": null
                            }}
                        }}
                        """

                        response = self.client.chat.completions.create(
                            model="gpt-3.5-turbo",
                            messages=[
                                {"role": "system", "content": "You are an expert business analyst. Provide your analysis in JSON format."},
                                {"role": "user", "content": analysis_prompt}
                            ],
                            response_format={ "type": "json_object" }
                        )

                        analysis_data = json.loads(response.choices[0].message.content)
                        
                        return CompetitorProfile(
                            company_info=CompanyInfo(**analysis_data['company_info']),
                            market_position=MarketPosition(**analysis_data['market_position']),
                            product_service=ProductService(**analysis_data['product_service']),
                            online_presence=OnlinePresence(**analysis_data['online_presence']),
                            customer_sentiment=CustomerSentiment(**analysis_data['customer_sentiment']),
                            business_growth=BusinessGrowth(**analysis_data['business_growth']),
                            tech_stack=TechnologyStack(**analysis_data['tech_stack']),
                            marketing_strategy=MarketingStrategy(**analysis_data['marketing_strategy']),
                            last_updated=datetime.utcnow(),
                            data_source='new'
                        )

        except Exception as e:
            print(f"Error analyzing competitor {competitor}: {str(e)}")
            # Return a minimal profile with error information
            return CompetitorProfile(
                company_info=CompanyInfo(
                    name=competitor,
                    website=website if 'website' in locals() else "Error",
                    industry="Unknown",
                    founded_year=None,
                    location=None,
                    founders=None
                ),
                market_position=MarketPosition(
                    target_audience=["Unknown"],
                    brand_reputation="Unknown",
                    value_propositions=["Analysis failed"]
                ),
                product_service=ProductService(
                    features=["Analysis not available"],
                    pricing={},
                    differentiators=[]
                ),
                online_presence=OnlinePresence(
                    website_traffic=None,
                    domain_authority=None,
                    social_media={},
                    content_strategy=None
                ),
                customer_sentiment=CustomerSentiment(
                    positive_feedback=[],
                    negative_feedback=[],
                    common_pain_points=[],
                    praise_points=[]
                ),
                business_growth=BusinessGrowth(
                    funding_rounds=None,
                    revenue_estimates=None,
                    partnerships=[],
                    market_growth="Unknown"
                ),
                tech_stack=TechnologyStack(
                    tools=[],
                    ai_ml_usage=None,
                    frameworks=[],
                    platform_details="Unknown"
                ),
                marketing_strategy=MarketingStrategy(
                    campaigns=[],
                    channels=[],
                    positioning="Unknown",
                    engagement_metrics=None
                ),
                last_updated=datetime.utcnow(),
                data_source='error'
            )

    async def _generate_swot_analysis(self, query: str, results: List[SearchResult], competitor_profiles: List[CompetitorProfile]) -> SwotAnalysis:
        """Generate SWOT analysis using OpenAI"""
        try:
            # Prepare content for analysis
            content = f"Query: {query}\n\nSearch Results:\n"
            for result in results:
                content += f"\nTitle: {result.title}\nSnippet: {result.snippet}\nAnalysis: {result.analysis}\n"

            if competitor_profiles:
                content += "\nCompetitor Profiles:\n"
                for profile in competitor_profiles:
                    content += f"""
                    \nCompetitor: {profile.company_info.name}
                    Industry: {profile.company_info.industry}
                    Target Market: {', '.join(profile.market_position.target_audience)}
                    Key Features: {', '.join(profile.product_service.features)}
                    Value Propositions: {', '.join(profile.market_position.value_propositions)}
                    """

            prompt = f"""
            Based on the following data, generate a comprehensive SWOT analysis in JSON format:

            {content}

            Provide your analysis as a JSON object with this structure:
            {{
                "strengths": ["string"],
                "weaknesses": ["string"],
                "opportunities": ["string"],
                "threats": ["string"]
            }}
            """

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert business analyst. Provide your SWOT analysis in JSON format."},
                    {"role": "user", "content": prompt}
                ],
                response_format={ "type": "json_object" }
            )
            
            swot_data = json.loads(response.choices[0].message.content)
            
            return SwotAnalysis(
                strengths=swot_data.get('strengths', []),
                weaknesses=swot_data.get('weaknesses', []),
                opportunities=swot_data.get('opportunities', []),
                threats=swot_data.get('threats', [])
            )
        except Exception as e:
            print(f"Error generating SWOT analysis: {str(e)}")
            return SwotAnalysis(
                strengths=["Analysis not available"],
                weaknesses=["Analysis not available"],
                opportunities=["Analysis not available"],
                threats=["Analysis not available"]
            )

    async def _generate_competitive_analysis(
        self,
        results: List[SearchResult],
        competitor_profiles: List[CompetitorProfile],
        advantages: bool
    ) -> List[str]:
        """Generate competitive advantages or disadvantages"""
        try:
            content = "Search Results:\n"
            for result in results:
                content += f"\nTitle: {result.title}\nAnalysis: {result.analysis}\n"

            content += "\nCompetitor Profiles:\n"
            for profile in competitor_profiles:
                content += f"""
                \nCompetitor: {profile.company_info.name}
                Features: {', '.join(profile.product_service.features)}
                Target Market: {', '.join(profile.market_position.target_audience)}
                Differentiators: {', '.join(profile.product_service.differentiators)}
                """

            prompt = f"""
            Based on the following data, analyze the {'advantages' if advantages else 'disadvantages'} and provide the results in JSON format:

            {content}

            Provide your analysis as a JSON object with this structure:
            {{
                "points": ["string"]
            }}
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert business analyst. Provide your analysis in JSON format."},
                    {"role": "user", "content": prompt}
                ],
                response_format={ "type": "json_object" }
            )
            
            analysis_data = json.loads(response.choices[0].message.content)
            return analysis_data.get('points', [])
        except Exception as e:
            print(f"Error generating competitive analysis: {str(e)}")
            return ["Analysis not available"]