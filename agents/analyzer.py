from typing import Dict
from langchain_openai import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import os
from dotenv import load_dotenv
import openai

class AnalyzerAgent:
    def __init__(self):
        load_dotenv()  # Load environment variables from .env file
        
        # Get API key from environment
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
            
        # Set the API key for both openai and langchain
        openai.api_key = api_key
        
        # Initialize OpenAI with explicit API key
        self.llm = OpenAI(
            api_key=api_key,  # Use api_key instead of openai_api_key
            temperature=0.7
        )
        
        self.swot_template = PromptTemplate(
            input_variables=["company_data"],
            template="""
            Based on the following company data, provide a detailed SWOT analysis:
            {company_data}
            
            Format your response as:
            Strengths:
            -
            Weaknesses:
            -
            Opportunities:
            -
            Threats:
            -
            """
        )
        self.swot_chain = LLMChain(llm=self.llm, prompt=self.swot_template)

    async def analyze(self, data: Dict) -> Dict:
        """
        Analyze collected data using LLM
        """
        analysis_results = {
            "swot_analysis": await self._generate_swot(data),
            "feature_comparison": await self._compare_features(data),
            "market_positioning": await self._analyze_positioning(data),
            "competitive_advantages": await self._identify_advantages(data)
        }
        return analysis_results

    async def _generate_swot(self, data: Dict) -> Dict:
        """
        Generate SWOT analysis using LLM
        """
        return await self.swot_chain.arun(company_data=str(data))

    async def _compare_features(self, data: Dict) -> Dict:
        # Feature comparison logic
        pass

    async def _analyze_positioning(self, data: Dict) -> Dict:
        # Market positioning analysis
        pass

    async def _identify_advantages(self, data: Dict) -> Dict:
        # Competitive advantages analysis
        pass