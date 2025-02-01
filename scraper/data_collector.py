import aiohttp
import asyncio
from bs4 import BeautifulSoup
from typing import List, Dict, Optional, Union
from models.request import AnalysisRequest
from models.response import (
    SearchResult, SearchResponse, SwotAnalysis,
    CompetitorAnalysis, ComparisonResult, DataSourceInfo
)
from googlesearch import search
import os
from dotenv import load_dotenv
from openai import OpenAI
import json
from urllib.parse import urlparse
from pydantic import HttpUrl
from .db_manager import DBManager
from datetime import datetime

class DataCollector:
    def __init__(self):
        load_dotenv()
        
        # Initialize OpenAI client
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        
        self.client = OpenAI(api_key=openai_api_key)
        self.db_manager = DBManager()

    async def collect_data(self, request: AnalysisRequest) -> SearchResponse:
        """Collect and analyze data from Google Search or database"""
        data_source_info = DataSourceInfo()
        
        # Check if we have cached search results
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
        competitor_analyses = []
        if request.competitors:
            for competitor in request.competitors:
                # Check for cached competitor data
                cached_data = await self.db_manager.get_competitor_data(str(competitor))
                if cached_data:
                    cached_data['data_source'] = 'cached'
                    cached_data['last_updated'] = datetime.fromisoformat(cached_data.get('last_updated', datetime.utcnow().isoformat()))
                    analysis = CompetitorAnalysis(**cached_data)
                    data_source_info.competitors_from_cache.append(str(competitor))
                else:
                    analysis = await self._analyze_competitor(str(competitor))
                    analysis.data_source = 'new'
                    analysis.last_updated = datetime.utcnow()
                    # Store new competitor data
                    await self.db_manager.store_competitor_data(analysis.dict())
                    data_source_info.fresh_competitors.append(str(competitor))
                competitor_analyses.append(analysis)
        
        # Generate SWOT analysis
        swot_analysis = await self._generate_swot_analysis(request.query, results, competitor_analyses)
        
        # Generate competitor comparison if competitors are provided
        comparison = None
        if request.competitors:
            comparison = await self._generate_comparison(
                request.query,
                results,
                request.competitors
            )
        
        return SearchResponse(
            query=request.query,
            results=results,
            swot_analysis=swot_analysis,
            comparison=comparison,
            data_source_info=data_source_info
        )

    async def _search_google(self, query: str, num_results: int) -> List[SearchResult]:
        """Search Google and collect results"""
        results = []
        try:
            # Using googlesearch-python to get results
            search_results = search(query, num_results=num_results)
            
            async with aiohttp.ClientSession() as session:
                for url in search_results:
                    try:
                        async with session.get(url) as response:
                            if response.status == 200:
                                html = await response.text()
                                soup = BeautifulSoup(html, 'html.parser')
                                
                                title = soup.title.string if soup.title else url
                                # Get the first paragraph or div as snippet
                                snippet = soup.find('p').get_text()[:200] if soup.find('p') else ""
                                
                                # Analyze the content using OpenAI
                                analysis = await self._analyze_content(title, snippet)
                                
                                results.append(SearchResult(
                                    title=title,
                                    url=url,
                                    snippet=f"{snippet}...",
                                    analysis=analysis
                                ))
                    except Exception as e:
                        print(f"Error fetching {url}: {str(e)}")
                        continue
        except Exception as e:
            print(f"Error in Google search: {str(e)}")
        
        return results

    async def _get_company_url(self, company_name: str) -> str:
        """Get company website URL from company name using Google search"""
        try:
            # Search for company website
            search_query = f"{company_name} official website"
            search_results = list(search(search_query, num_results=1))
            
            if search_results:
                return search_results[0]
            return None
        except Exception as e:
            print(f"Error finding company URL for {company_name}: {str(e)}")
            return None

    async def _analyze_content(self, title: str, content: str) -> str:
        """Analyze content using OpenAI"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that analyzes web content."},
                    {"role": "user", "content": f"Please analyze this content and provide key insights in 2-3 sentences:\n\nTitle: {title}\n\nContent: {content}"}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error in OpenAI analysis: {str(e)}")
            return "Analysis not available"

    async def _generate_swot_analysis(self, query: str, results: List[SearchResult], competitor_analyses: List[CompetitorAnalysis] = None) -> SwotAnalysis:
        """Generate SWOT analysis using OpenAI, including competitor comparison if available"""
        try:
            # Prepare content for analysis
            content = f"Query: {query}\n\nResults:\n"
            for result in results:
                content += f"\nTitle: {result.title}\nSnippet: {result.snippet}\nAnalysis: {result.analysis}\n"

            # Add competitor information if available
            if competitor_analyses:
                content += "\nCompetitor Analysis:\n"
                for comp in competitor_analyses:
                    content += f"""
                    \nCompetitor: {comp.name}
                    Website: {comp.website}
                    Target Market: {comp.target_market}
                    Key Features: {', '.join(comp.key_features)}
                    Pricing Model: {comp.pricing_model}
                    Unique Selling Points: {', '.join(comp.unique_selling_points)}
                    """

            system_prompt = """You are a helpful assistant that creates SWOT analyses. 
            If competitor information is provided, include competitive analysis in each SWOT category:
            - Strengths should highlight advantages over competitors
            - Weaknesses should address areas where competitors are stronger
            - Opportunities should consider market gaps not addressed by competitors
            - Threats should include competitive pressures and market challenges
            
            Return the response in JSON format with 'strengths', 'weaknesses', 'opportunities', and 'threats' as arrays of strings."""

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Please provide a SWOT analysis based on these search results and competitor data:\n\n{content}"}
                ],
                response_format={ "type": "json_object" }
            )
            
            # Parse the JSON response
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

    async def _analyze_competitor(self, competitor: str) -> CompetitorAnalysis:
        """Analyze a competitor by name or URL"""
        try:
            # Check if the competitor is a URL or company name
            if competitor.startswith(('http://', 'https://')):
                url = competitor
            else:
                # If it's a company name, search for its website
                url = await self._get_company_url(competitor)
                if not url:
                    return CompetitorAnalysis(
                        website="Not found",
                        name=competitor,
                        key_features=["Analysis not available"],
                        target_market="Unknown",
                        pricing_model="Unknown",
                        unique_selling_points=[]
                    )

            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Extract basic information
                        title = soup.title.string if soup.title else url
                        description = ""
                        meta_desc = soup.find('meta', {'name': 'description'})
                        if meta_desc:
                            description = meta_desc.get('content', '')
                        
                        # Use OpenAI to analyze the website
                        analysis_prompt = f"""
                        Analyze this website and provide information in JSON format:
                        URL: {url}
                        Title: {title}
                        Description: {description}

                        Return a JSON object with the following fields:
                        - name (string): Company name
                        - key_features (array): List of main features
                        - target_market (string): Primary target market
                        - pricing_model (string): Brief description of pricing model
                        - unique_selling_points (array): List of unique selling points
                        """
                        
                        response = self.client.chat.completions.create(
                            model="gpt-3.5-turbo",
                            messages=[
                                {"role": "system", "content": "You are a helpful assistant that analyzes websites."},
                                {"role": "user", "content": analysis_prompt}
                            ],
                            response_format={ "type": "json_object" }
                        )
                        
                        analysis_data = json.loads(response.choices[0].message.content)
                        
                        return CompetitorAnalysis(
                            website=url,
                            name=analysis_data.get('name', urlparse(url).netloc),
                            key_features=analysis_data.get('key_features', []),
                            target_market=analysis_data.get('target_market', ''),
                            pricing_model=analysis_data.get('pricing_model', ''),
                            unique_selling_points=analysis_data.get('unique_selling_points', [])
                        )
        except Exception as e:
            print(f"Error analyzing competitor {competitor}: {str(e)}")
            return CompetitorAnalysis(
                website="Error",
                name=competitor,
                key_features=["Analysis not available"],
                target_market="Unknown",
                pricing_model="Unknown",
                unique_selling_points=[]
            )

    async def _generate_comparison(
        self,
        query: str,
        results: List[SearchResult],
        competitors: List[Union[str, HttpUrl]]
    ) -> ComparisonResult:
        """Generate comparison analysis between main product and competitors"""
        try:
            # Analyze each competitor
            competitor_analyses = []
            for competitor in competitors:
                analysis = await self._analyze_competitor(str(competitor))
                competitor_analyses.append(analysis)
            
            # Extract main product information from search results
            main_product_info = f"Query: {query}\n\nSearch Results:\n"
            for result in results:
                main_product_info += f"\nTitle: {result.title}\nSnippet: {result.snippet}\nAnalysis: {result.analysis}\n"
            
            # Generate comparative analysis using OpenAI
            comparison_prompt = f"""
            Analyze the main product and its competitors and provide a comparison in JSON format:

            Main Product Information:
            {main_product_info}

            Competitors:
            {json.dumps([comp.dict() for comp in competitor_analyses], indent=2)}

            Return a JSON object with:
            - competitive_advantages (array): List of advantages over competitors
            - competitive_disadvantages (array): List of disadvantages compared to competitors
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that analyzes competitive landscapes."},
                    {"role": "user", "content": comparison_prompt}
                ],
                response_format={ "type": "json_object" }
            )
            
            comparison_data = json.loads(response.choices[0].message.content)
            
            return ComparisonResult(
                main_product=None,  # Main product details are spread across search results
                competitors=competitor_analyses,
                competitive_advantages=comparison_data.get('competitive_advantages', []),
                competitive_disadvantages=comparison_data.get('competitive_disadvantages', [])
            )
        except Exception as e:
            print(f"Error generating comparison: {str(e)}")
            return ComparisonResult(
                main_product=None,
                competitors=[],
                competitive_advantages=["Analysis not available"],
                competitive_disadvantages=["Analysis not available"]
            )