"""
Red Bull Batalla Agent Suite - FastAPI Main Application
Suite completa de agentes IA para análisis inteligente de batallas de freestyle.
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from config import DEEPSEEK_MODEL_CONFIG
from models import Base
from agents import BatallaAgent, AmbiguityResolver
from tools import BatallaToolkit
from services.cache_service import CacheService
from services.normalization_service import NormalizationService
from services.scraper_service import ScraperService

# --- Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Configuración ---
DATABASE_URI = os.getenv("DATABASE_URI", "postgresql://postgres:HUOMtnXMvadivsKSrzQCmpxOqfTxaZJz@maglev.proxy.rlwy.net:30559/railway")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-cd23ed33b5e34e45a6ca9c2438bfe1ee")

# --- Base de datos ---
engine = create_engine(DATABASE_URI, echo=False, pool_size=10, max_overflow=20)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear tablas si no existen
Base.metadata.create_all(bind=engine)

# --- FastAPI App ---
app = FastAPI(
    title="Red Bull Batalla Agent Suite",
    description="Suite de agentes IA para análisis inteligente de batallas freestyle",
    version="2.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Servicios Globales ---
cache = CacheService(ttl_seconds=3600)
normalizer = NormalizationService()

# --- Dependency Injection ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_agent(db: Session = Depends(get_db)) -> BatallaAgent:
    llm_config = {
        "model_id": DEEPSEEK_MODEL_CONFIG.model_id,
        "api_key": DEEPSEEK_API_KEY,
        "base_url": DEEPSEEK_MODEL_CONFIG.base_url,
        "temperature": 0.2
    }
    return BatallaAgent(db, llm_config)

def get_toolkit(db: Session = Depends(get_db)) -> BatallaToolkit:
    return BatallaToolkit(db)

# --- Pydantic Models ---
class Message(BaseModel):
    role: str
    content: str = Field(..., min_length=1)
    isComplete: Optional[bool] = None

class ChatRequest(BaseModel):
    messages: List[Message] = Field(..., min_items=1)
    context: Optional[Dict[str, Any]] = None

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    context: Optional[Dict[str, Any]] = None

class ScrapingRequest(BaseModel):
    url: str
    data_type: str = Field(..., description="Type: 'participants', 'battles', 'results'")

class PersonIngestionRequest(BaseModel):
    aka: str
    full_name: Optional[str] = None
    country: str
    style: Optional[str] = None
    debut_year: Optional[int] = None

class EventIngestionRequest(BaseModel):
    name: str
    event_type: str
    year: int
    country: str
    city: Optional[str] = None
    place: Optional[str] = None
    total_participants: Optional[int] = None

# --- Streaming Helper ---
def format_sse(data: Dict[str, Any], event: Optional[str] = None) -> str:
    """Formatea datos al formato Server-Sent Events."""
    json_data = json.dumps(data, ensure_ascii=False, default=str)
    message = f"data: {json_data}\n\n"
    if event:
        message = f"event: {event}\n{message}"
    return message

async def stream_query_process(query: str, agent: BatallaAgent):
    """
    Generador asíncrono que emite eventos SSE del proceso de consulta.
    """
    try:
        # Paso 1: Extracción de intención
        yield format_sse(
            {"step": 1, "status": "in_progress", "message": "Analizando consulta..."},
            event="progress"
        )

        # Paso 2: Procesamiento
        result = agent.process_query(query)

        if result.get("ambiguities"):
            yield format_sse(
                {
                    "step": 2,
                    "status": "clarification_needed",
                    "ambiguities": result["ambiguities"],
                    "message": "Hay ambigüedades en la consulta. Por favor, aclara:"
                },
                event="ambiguity"
            )
            return

        if result.get("error"):
            yield format_sse(
                {"error": result["error"]},
                event="error"
            )
            return

        # Paso 3: Herramientas ejecutadas
        yield format_sse(
            {
                "step": 3,
                "status": "tools_executed",
                "tools": result.get("tool_calls", []),
                "message": f"Se ejecutaron {len(result.get('tool_calls', []))} herramientas"
            },
            event="progress"
        )

        # Paso 4: Respuesta final
        yield format_sse(
            {
                "step": 4,
                "status": "completed",
                "answer": result.get("final_answer", ""),
                "intent": result.get("intent", {}),
                "full_result": result
            },
            event="final_result"
        )

    except Exception as e:
        logger.exception("Error en stream_query_process")
        yield format_sse(
            {"error": str(e)},
            event="error"
        )

# --- Health Check ---
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0"
    }

# --- Query Endpoints ---
@app.post("/api/query")
async def query_agent(
    request: QueryRequest,
    agent: BatallaAgent = Depends(get_agent)
):
    """
    Endpoint principal para consultas de agentes.
    Retorna respuesta directa (sin streaming).
    """
    try:
        result = agent.process_query(request.query)

        if result.get("ambiguities"):
            return JSONResponse(
                status_code=422,
                content={
                    "status": "clarification_needed",
                    "ambiguities": result["ambiguities"]
                }
            )

        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "query": request.query,
                "intent": result.get("intent"),
                "tools_used": result.get("tool_calls"),
                "answer": result.get("final_answer"),
                "timestamp": datetime.utcnow().isoformat()
            }
        )

    except Exception as e:
        logger.exception("Error en query_agent")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/query/stream")
async def query_agent_stream(
    request: QueryRequest,
    agent: BatallaAgent = Depends(get_agent)
):
    """
    Endpoint de consulta con streaming (SSE).
    Emite progreso y tokens en tiempo real.
    """
    return StreamingResponse(
        stream_query_process(request.query, agent),
        media_type="text/event-stream"
    )

# --- Chat Endpoints ---
@app.post("/api/chat")
async def chat(
    request: ChatRequest,
    agent: BatallaAgent = Depends(get_agent)
):
    """
    Endpoint de chat que mantiene historial de mensajes.
    """
    # Obtener último mensaje del usuario
    last_user_message = next(
        (msg for msg in reversed(request.messages) if msg.role == "user"),
        None
    )

    if not last_user_message:
        raise HTTPException(status_code=422, detail="No user message found")

    result = agent.process_query(last_user_message.content)

    return JSONResponse(
        status_code=200,
        content={
            "status": "success" if not result.get("error") else "error",
            "assistant_message": result.get("final_answer", ""),
            "metadata": {
                "intent": result.get("intent"),
                "tools_used": len(result.get("tool_calls", [])),
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    )

# --- Search Endpoints ---
@app.get("/api/search/persons")
async def search_persons(
    q: str = Query(..., min_length=1),
    toolkit: BatallaToolkit = Depends(get_toolkit)
):
    """Busca MCs por nombre."""
    results = toolkit.search_person(q)
    return {"query": q, "results": results}

@app.get("/api/search/events")
async def search_events(
    q: str = Query(..., min_length=1),
    toolkit: BatallaToolkit = Depends(get_toolkit)
):
    """Busca eventos por nombre."""
    results = toolkit.search_event(q)
    return {"query": q, "results": results}

# --- Statistics Endpoints ---
@app.get("/api/person/{person_id}/stats")
async def get_person_stats(
    person_id: int,
    toolkit: BatallaToolkit = Depends(get_toolkit)
):
    """Obtiene estadísticas de un MC."""
    person = toolkit.get_person_by_id(person_id)
    if not person:
        raise HTTPException(status_code=404, detail="MC not found")

    stats = toolkit.get_person_statistics(person_id)
    battles = toolkit.get_battles_by_person(person_id, limit=20)
    timeline = toolkit.get_timeline(person_id)

    return {
        "person": person,
        "statistics": stats,
        "recent_battles": battles,
        "timeline": timeline
    }

@app.get("/api/battle/{battle_id}")
async def get_battle_details(
    battle_id: int,
    toolkit: BatallaToolkit = Depends(get_toolkit)
):
    """Obtiene detalles de una batalla."""
    battle = toolkit.get_battle_analysis(battle_id)
    if not battle:
        raise HTTPException(status_code=404, detail="Battle not found")
    return battle

@app.get("/api/h2h/{person1_id}/{person2_id}")
async def get_h2h(
    person1_id: int,
    person2_id: int,
    toolkit: BatallaToolkit = Depends(get_toolkit)
):
    """Obtiene historial H2H entre dos MCs."""
    h2h = toolkit.get_head_to_head(person1_id, person2_id)
    return h2h

# --- Ranking Endpoints ---
@app.get("/api/rankings/top-performers")
async def get_top_performers(
    country: Optional[str] = None,
    limit: int = Query(10, ge=1, le=100),
    toolkit: BatallaToolkit = Depends(get_toolkit)
):
    """Obtiene ranking de mejores MCs."""
    return toolkit.get_top_performers(country, limit)

@app.get("/api/rankings/by-style")
async def get_by_style(
    style: str = Query(..., description="Style: punchline, flow, trap, etc."),
    toolkit: BatallaToolkit = Depends(get_toolkit)
):
    """Obtiene MCs por estilo."""
    results = toolkit.search_by_style(style)
    if isinstance(results, dict) and "error" in results:
        raise HTTPException(status_code=400, detail=results["error"])
    return {"style": style, "results": results}

# --- Event Endpoints ---
@app.get("/api/events")
async def list_events(
    year: Optional[int] = None,
    toolkit: BatallaToolkit = Depends(get_toolkit)
):
    """Lista eventos."""
    return toolkit.list_all_events(year)

@app.get("/api/event/{event_id}")
async def get_event_details(
    event_id: int,
    toolkit: BatallaToolkit = Depends(get_toolkit)
):
    """Obtiene detalles de un evento."""
    event = toolkit.get_event_details(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

# --- Ingestion Endpoints ---
@app.post("/api/ingest/person")
async def ingest_person(
    request: PersonIngestionRequest,
    db: Session = Depends(get_db)
):
    """Ingiere una nueva persona."""
    scraper = ScraperService(db)
    result = scraper.ingest_person(
        request.aka,
        request.full_name,
        request.country,
        request.style,
        request.debut_year
    )
    return result

@app.post("/api/ingest/event")
async def ingest_event(
    request: EventIngestionRequest,
    db: Session = Depends(get_db)
):
    """Ingiere un nuevo evento."""
    scraper = ScraperService(db)
    result = scraper.ingest_event(
        request.name,
        request.event_type,
        request.year,
        request.country,
        request.city,
        request.place,
        request.total_participants
    )
    return result

# --- Scraping Endpoints ---
@app.post("/api/scrape")
async def scrape_data(
    request: ScrapingRequest,
    db: Session = Depends(get_db)
):
    """Scrape datos de una URL."""
    scraper = ScraperService(db)
    try:
        if request.data_type == "participants":
            result = await scraper.scrape_event_participants(request.url)
        elif request.data_type == "battles":
            result = await scraper.scrape_battle_results(request.url)
        else:
            raise HTTPException(status_code=400, detail="Invalid data_type")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Cache Management ---
@app.get("/api/cache/stats")
async def get_cache_stats():
    """Obtiene estadísticas del caché."""
    return cache.get_stats()

@app.post("/api/cache/clear")
async def clear_cache():
    """Limpia el caché."""
    cache.clear()
    return {"status": "cache_cleared"}

# --- Info Endpoints ---
@app.get("/api/info/persons/count")
async def get_persons_count(db: Session = Depends(get_db)):
    """Cuenta total de MCs."""
    from models import Person
    count = db.query(Person).count()
    return {"total_persons": count}

@app.get("/api/info/events/count")
async def get_events_count(db: Session = Depends(get_db)):
    """Cuenta total de eventos."""
    from models import Event
    count = db.query(Event).count()
    return {"total_events": count}

@app.get("/api/info/battles/count")
async def get_battles_count(db: Session = Depends(get_db)):
    """Cuenta total de batallas."""
    from models import Battle
    count = db.query(Battle).count()
    return {"total_battles": count}

# --- Root Endpoint ---
@app.get("/")
async def root():
    """Root endpoint con información de la API."""
    return {
        "name": "Red Bull Batalla Agent Suite",
        "version": "2.0.0",
        "description": "Suite completa de agentes IA para análisis inteligente de batallas freestyle",
        "documentation": "/docs",
        "openapi": "/openapi.json",
        "endpoints": {
            "query": "/api/query",
            "query_stream": "/api/query/stream",
            "chat": "/api/chat",
            "search": {
                "persons": "/api/search/persons",
                "events": "/api/search/events"
            },
            "rankings": "/api/rankings/top-performers",
            "events": "/api/events",
            "stats": "/api/person/{id}/stats"
        }
    }

# Para ejecutar:
# uvicorn main:app --reload --host 0.0.0.0 --port 8000