"""
MiMo Web3 Marketing Agent - Main Entry Point
Multi-agent system for Web3 marketing automation powered by MiMo LLM.
"""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse

from src.core.kernel import AgentKernel
from src.core.monitor import MetricsCollector
from src.agents.content_agent import ContentAgent
from src.agents.analytics_agent import AnalyticsAgent
from src.agents.social_agent import SocialAgent
from src.agents.narrative_agent import NarrativeAgent
from src.agents.rag_agent import RAGAgent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s"
)
logger = logging.getLogger("mimo-marketing")

# Global kernel instance
kernel: AgentKernel = None
metrics: MetricsCollector = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - startup and shutdown."""
    global kernel, metrics
    
    logger.info("Starting MiMo Web3 Marketing Agent...")
    
    # Initialize kernel
    kernel = AgentKernel()
    metrics = MetricsCollector()
    
    # Register agents
    kernel.register("content", ContentAgent())
    kernel.register("analytics", AnalyticsAgent())
    kernel.register("social", SocialAgent())
    kernel.register("narrative", NarrativeAgent())
    kernel.register("rag", RAGAgent())
    
    # Start all agents
    await kernel.start_all()
    logger.info(f"Started {len(kernel.agents)} agents")
    
    yield
    
    # Shutdown
    await kernel.stop_all()
    logger.info("All agents stopped")


app = FastAPI(
    title="MiMo Web3 Marketing Agent",
    description="AI-powered Web3 marketing automation with multi-agent architecture",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the dashboard."""
    with open("templates/index.html", "r") as f:
        return f.read()


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "agents": kernel.status() if kernel else {}}


@app.post("/api/generate")
async def generate_content(request: dict):
    """Generate marketing content for a Web3 project."""
    project = request.get("project", {})
    content_type = request.get("type", "tweet")
    tone = request.get("tone", "engaging")
    chain = request.get("chain", "ethereum")
    
    result = await kernel.dispatch("content", {
        "action": "generate",
        "project": project,
        "content_type": content_type,
        "tone": tone,
        "chain": chain,
    })
    metrics.record("content_generated")
    return JSONResponse(content=result)


@app.post("/api/analyze")
async def analyze_narrative(request: dict):
    """Analyze current Web3 narratives and suggest content."""
    chain = request.get("chain", "ethereum")
    timeframe = request.get("timeframe", "24h")
    
    result = await kernel.dispatch("narrative", {
        "action": "analyze",
        "chain": chain,
        "timeframe": timeframe,
    })
    metrics.record("narrative_analyzed")
    return JSONResponse(content=result)


@app.post("/api/onchain")
async def onchain_metrics(request: dict):
    """Get on-chain metrics for a project/token."""
    address = request.get("address", "")
    chain = request.get("chain", "ethereum")
    
    result = await kernel.dispatch("analytics", {
        "action": "metrics",
        "address": address,
        "chain": chain,
    })
    metrics.record("onchain_fetched")
    return JSONResponse(content=result)


@app.post("/api/campaign")
async def create_campaign(request: dict):
    """Create and schedule a marketing campaign."""
    result = await kernel.dispatch("social", {
        "action": "campaign",
        "config": request,
    })
    metrics.record("campaign_created")
    return JSONResponse(content=result)


@app.post("/api/rag/ingest")
async def ingest_docs(request: dict):
    """Ingest project documentation for RAG pipeline."""
    docs = request.get("documents", [])
    project_id = request.get("project_id", "default")
    
    result = await kernel.dispatch("rag", {
        "action": "ingest",
        "documents": docs,
        "project_id": project_id,
    })
    return JSONResponse(content=result)


@app.get("/api/metrics")
async def get_metrics():
    """Get system metrics."""
    return JSONResponse(content=metrics.summary())


@app.get("/api/agents")
async def list_agents():
    """List all agents and their status."""
    return JSONResponse(content=kernel.status())


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
