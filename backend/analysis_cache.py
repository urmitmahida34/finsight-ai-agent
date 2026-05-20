"""
Stores analysis results per ticker per calendar day.
File: data/analysis_cache/{TICKER}_{YYYY-MM-DD}.json

Same ticker on the same day → instant result from file, 0 LLM calls.
Next day → fresh analysis runs automatically.
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

CACHE_DIR = Path(__file__).parent / "data" / "analysis_cache"


def _cache_path(ticker: str) -> Path:
    date = datetime.now().strftime("%Y-%m-%d")
    safe = ticker.upper().replace(".", "_").replace("/", "_")
    return CACHE_DIR / f"{safe}_{date}.json"


def get_cached(ticker: str) -> Optional[str]:
    """Return cached report string if today's analysis exists, else None."""
    path = _cache_path(ticker)
    if path.exists():
        try:
            with open(path) as f:
                return json.load(f).get("report")
        except Exception:
            return None
    return None


def save_cache(ticker: str, report: str, company: str = "") -> None:
    """Persist a completed analysis to disk."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = _cache_path(ticker)
    with open(path, "w") as f:
        json.dump(
            {
                "ticker": ticker,
                "company": company,
                "report": report,
                "cached_at": datetime.now().isoformat(),
                "date": datetime.now().strftime("%Y-%m-%d"),
            },
            f,
            indent=2,
        )


def list_cache() -> list:
    """List all cached analyses (most recent first)."""
    if not CACHE_DIR.exists():
        return []
    results = []
    for f in sorted(CACHE_DIR.glob("*.json"), reverse=True):
        try:
            with open(f) as fp:
                data = json.load(fp)
                results.append(
                    {
                        "ticker": data.get("ticker"),
                        "company": data.get("company", ""),
                        "cached_at": data.get("cached_at"),
                        "date": data.get("date"),
                    }
                )
        except Exception:
            pass
    return results


def clear_cache(ticker: str = None) -> int:
    """Delete cache for a specific ticker (all dates) or all caches. Returns count deleted."""
    if not CACHE_DIR.exists():
        return 0
    count = 0
    pattern = f"{ticker.upper().replace('.', '_')}_*.json" if ticker else "*.json"
    for f in CACHE_DIR.glob(pattern):
        f.unlink()
        count += 1
    return count
