import asyncio
import json
import os
import threading
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="FinSight AI",
    description="Multi-agent AI system for Indian equity research",
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


@app.get("/")
async def root():
    return {"service": "FinSight AI", "docs": "/docs", "health": "/api/health"}


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "FinSight AI", "version": "1.0.0"}


@app.get("/api/analyze")
async def analyze_stream(
    ticker: str = Query(..., description="NSE/BSE ticker e.g. HDFCBANK.NS"),
    company: str = Query("", description="Company name for better news search"),
):
    """
    SSE endpoint — streams progress events as each agent completes,
    then sends the final report as a 'complete' event.
    """
    from crew import run_analysis_sync

    loop = asyncio.get_running_loop()
    queue: asyncio.Queue = asyncio.Queue()

    def progress_callback(event_data: dict):
        asyncio.run_coroutine_threadsafe(queue.put(event_data), loop)

    def run_in_thread():
        try:
            result = run_analysis_sync(ticker, company or ticker, progress_callback)
            asyncio.run_coroutine_threadsafe(
                queue.put({"type": "complete", "report": result.get("report", "")}),
                loop,
            )
        except Exception as exc:
            asyncio.run_coroutine_threadsafe(
                queue.put({"type": "error", "message": str(exc)}),
                loop,
            )

    threading.Thread(target=run_in_thread, daemon=True).start()

    async def event_generator():
        yield {"data": json.dumps({"type": "started", "ticker": ticker, "company": company or ticker})}

        while True:
            try:
                event = await asyncio.wait_for(queue.get(), timeout=300.0)
                yield {"data": json.dumps(event)}
                if event.get("type") in ("complete", "error"):
                    break
            except asyncio.TimeoutError:
                yield {"data": json.dumps({"type": "error", "message": "Analysis timed out (5 min limit)"})}
                break

    return EventSourceResponse(event_generator())


class PdfRequest(BaseModel):
    ticker: str
    company: str
    report: str


@app.post("/api/report/pdf")
async def generate_pdf_report(req: PdfRequest):
    """Generate and return a PDF version of the analysis report."""
    from pdf_exporter import generate_pdf

    pdf_bytes = generate_pdf(req.report, req.company, req.ticker)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{req.ticker}_analysis.pdf"'},
    )


class IndexRequest(BaseModel):
    pass


@app.get("/api/cache")
async def list_cached_analyses():
    """List all cached analyses (most recent first)."""
    from analysis_cache import list_cache
    return {"analyses": list_cache()}


@app.delete("/api/cache")
async def clear_cached_analyses(ticker: str = Query(None, description="Ticker to clear, or omit for all")):
    """Delete cached analyses for a ticker or all."""
    from analysis_cache import clear_cache
    count = clear_cache(ticker)
    return {"deleted": count, "ticker": ticker or "all"}


@app.get("/api/rbi/status")
async def rbi_index_status():
    """Check if the RBI circular index has been built."""
    from tools.rbi_rag_tool import INDEX_PATH, CHUNKS_PATH

    built = INDEX_PATH.exists() and CHUNKS_PATH.exists()
    return {"indexed": built}
