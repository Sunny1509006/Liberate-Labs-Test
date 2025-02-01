from typing import Dict, List
from jinja2 import Environment, FileSystemLoader
from models.competitor import CompetitorReport, CompetitorProfile

class ReportGeneratorAgent:
    def __init__(self):
        self.template_env = Environment(loader=FileSystemLoader("templates"))

    async def generate_report(self, analyzed_data: Dict) -> CompetitorReport:
        """
        Generate comprehensive competitor analysis report
        """
        report = CompetitorReport(
            executive_summary=self._generate_executive_summary(analyzed_data),
            competitor_profiles=self._generate_competitor_profiles(analyzed_data),
            swot_analysis=analyzed_data["swot_analysis"],
            feature_comparison=analyzed_data["feature_comparison"],
            strategic_recommendations=self._generate_recommendations(analyzed_data)
        )
        return report

    def _generate_executive_summary(self, data: Dict) -> str:
        # Generate executive summary using template
        template = self.template_env.get_template("executive_summary.j2")
        return template.render(data=data)

    def _generate_competitor_profiles(self, data: Dict) -> List[CompetitorProfile]:
        # Generate detailed competitor profiles
        profiles = []
        for competitor_data in data.get("competitors", []):
            profile = CompetitorProfile(
                name=competitor_data.get("name", ""),
                website=competitor_data.get("website", ""),
                description=competitor_data.get("description", ""),
                key_features=competitor_data.get("key_features", []),
                market_position=competitor_data.get("market_position", ""),
                strengths=competitor_data.get("strengths", []),
                weaknesses=competitor_data.get("weaknesses", [])
            )
            profiles.append(profile)
        return profiles

    def _generate_recommendations(self, data: Dict) -> List[str]:
        # Generate strategic recommendations based on analysis
        recommendations = []
        if "market_insights" in data:
            for insight in data["market_insights"]:
                if "recommendation" in insight:
                    recommendations.append(insight["recommendation"])
        return recommendations