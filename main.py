from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models.request import AnalysisRequest
from models.response import SearchResponse
from scraper.data_collector import DataCollector
import uvicorn

app = FastAPI(
    title="Google Search Analyzer",
    description="Web scraping system for collecting and analyzing Google Search results"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the data collector
collector = DataCollector()

@app.post("/search", response_model=SearchResponse)
async def search_and_analyze(request: AnalysisRequest):
    """
    Search Google and analyze results using OpenAI
    """
    try:
        results = await collector.collect_data(request)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)