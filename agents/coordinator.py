from typing import List
from .data_collector import DataCollectorAgent
from .analyzer import AnalyzerAgent
from .report_generator import ReportGeneratorAgent
from models.competitor import CompetitorProfile, CompetitorReport
from models.request import AnalysisRequest

class CompetitorAnalysisCoordinator:
    def __init__(self, data_collector: DataCollectorAgent,
                 analyzer: AnalyzerAgent,
                 report_generator: ReportGeneratorAgent):
        self.data_collector = data_collector
        self.analyzer = analyzer
        self.report_generator = report_generator

    async def run_analysis(self, request: AnalysisRequest) -> CompetitorReport:
        # Step 1: Collect raw data
        raw_data = await self.data_collector.collect_data(request)
        
        # Step 2: Analyze collected data
        analyzed_data = await self.analyzer.analyze(raw_data)
        
        # Step 3: Generate final report
        report = await self.report_generator.generate_report(analyzed_data)
        
        return report