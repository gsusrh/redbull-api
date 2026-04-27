# Red Bull Batalla Agent Suite v2.0.0

Suite profesional de agentes IA para análisis inteligente de batallas de freestyle Red Bull. Sistema completo con orquestación de agentes, búsqueda inteligente, estadísticas avanzadas e ingesta de datos.

## 🚀 Características Principales

### Agentes Inteligentes
- **BatallaAgent**: Orquestador central con ciclo de tool-loop y manejo de ambigüedades
- **Tool-Loop Pattern**: Validación estricta sin alucinaciones en nombres
- **Detección de Intención**: Clasifica automáticamente el tipo de consulta
- **Manejo de Ambigüedades**: Solicita aclaración si hay múltiples coincidencias

### Herramientas (30+)
- Búsqueda fuzzy de MCs y eventos
- Estadísticas complejas (win rate, streaks, H2H)
- Rankings y top performers
- Análisis de batallas
- Timeline de carreras
- Historial de eventos
- Información por país/estilo

### Endpoints Ricos
- REST API completa con Pydantic validation
- Streaming SSE para respuestas en tiempo real
- Chat con historial
- Ingesta de datos
- Web scraping automático

### Base de Datos Relacional
- 10+ tablas normalizadas
- Índices optimizados
- Estadísticas pre-calculadas
- Caché con TTL automático

## 📦 Tech Stack

```
Backend:      FastAPI 0.115+
LLM:          DeepSeek v4 (via OpenRouter)
Database:     PostgreSQL 12+
ORM:          SQLAlchemy 2.0+
Validation:   Pydantic v2
Search:       RapidFuzz 3.13+
```

## 🏗️ Arquitectura

```
┌─ main.py ──────────────────────────┐
│  FastAPI App + Endpoints            │
├─────────────────────────────────────┤
│  ┌── agents.py ─────────────────┐   │
│  │ BatallaAgent (Orchestrator)   │   │
│  │ - process_query()             │   │
│  │ - _execute_tool_loop()        │   │
│  │ - _handle_*()                 │   │
│  └───────────────────────────────┘   │
│  ┌── tools.py ──────────────────┐   │
│  │ BatallaToolkit (30+ tools)    │   │
│  │ - search_person()             │   │
│  │ - get_statistics()            │   │
│  │ - get_h2h()                   │   │
│  └───────────────────────────────┘   │
├─────────────────────────────────────┤
│  Services                           │
│  ├─ cache_service.py                │
│  ├─ normalization_service.py        │
│  └─ scraper_service.py              │
├─────────────────────────────────────┤
│  ┌── models.py ─────────────────┐   │
│  │ SQLAlchemy Models (10 tables) │   │
│  │ - Person, Event, Battle       │   │
│  │ - Intervention, Statistics    │   │
│  └───────────────────────────────┘   │
├─────────────────────────────────────┤
│  PostgreSQL Database                │
└─────────────────────────────────────┘
```

## 🎯 Tipos de Consultas Soportadas

### 1. Head-to-Head (H2H)
```
"Dani vs Chuty en España"
→ Historial directo
→ Record general
→ Últimas 5 batallas
```

### 2. Estadísticas
```
"¿Cuál es el win rate de Dani?"
→ Win rate, rachas
→ Batallas totales
→ Historial detallado
```

### 3. Rankings
```
"Top 10 mejores freestylers"
→ Ranking por win rate
→ Filtrable por país
```

### 4. Eventos
```
"Batalla de Gallos España 2023"
→ Participantes
→ Batallas por ronda
→ Ganador
```

### 5. Historial
```
"Carrera completa de Wos"
→ Timeline cronológica
→ Eventos participados
→ Evolución de record
```

### 6. Búsqueda General
```
"¿Quién es Jonan?"
→ Información básica
→ País, debut, estilo
```

## 🚀 Quick Start

### 1. Instalación

```bash
# Clonar repo
git clone https://github.com/gsusrh/redbull-api.git
cd redbull-api

# Crear venv
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configuración

```bash
# Copiar .env
cp .env.example .env

# Editar .env con tus credenciales
export DATABASE_URI="postgresql://..."
export DEEPSEEK_API_KEY="sk-..."
```

### 3. Ejecutar

```bash
# Desarrollo (con auto-reload)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Producción
uvicorn main:app --workers 4 --host 0.0.0.0 --port 8000
```

### 4. Acceder

```
API Docs:    http://localhost:8000/docs
ReDoc:       http://localhost:8000/redoc
OpenAPI:     http://localhost:8000/openapi.json
```

## 📚 API Endpoints

### Queries
```http
POST /api/query
{
    "query": "¿Cómo le fue a Dani en España?"
}

POST /api/query/stream
# Streaming SSE con progreso en tiempo real

POST /api/chat
# Chat con historial de mensajes
```

### Search
```http
GET /api/search/persons?q=Dani
GET /api/search/events?q=España
```

### Statistics
```http
GET /api/person/{id}/stats
GET /api/battle/{id}
GET /api/h2h/{id1}/{id2}
```

### Rankings
```http
GET /api/rankings/top-performers?country=spain&limit=10
GET /api/rankings/by-style?style=punchline
```

### Events
```http
GET /api/events?year=2023
GET /api/event/{id}
```

### Data Ingestion
```http
POST /api/ingest/person
{
    "aka": "Nuevo MC",
    "country": "spain",
    "style": "flow"
}

POST /api/scrape
{
    "url": "https://...",
    "data_type": "battles"
}
```

## 🔧 Configuración Avanzada

### Cache
```python
# TTL automático de 1 hora
cache = CacheService(ttl_seconds=3600)

# Obtener stats
stats = cache.get_stats()  # Size, entries, etc.

# Limpiar
cache.clear()
```

### Normalización
```python
from services.normalization_service import NormalizationService

# Normalizar texto
normalized = NormalizationService.normalize("Dani García")
# → "dani garcia"

# Búsqueda fuzzy
matches = NormalizationService.fuzzy_match(
    "Dani",
    ["Dani", "Dani García", "Daniel"],
    threshold=80
)
```

### Scraping
```python
from services.scraper_service import ScraperService

scraper = ScraperService(db_session)

# Ingerir persona
result = scraper.ingest_person(
    aka="Nuevo MC",
    full_name="Nombre Completo",
    country="spain",
    style="flow",
    debut_year=2015
)

# Ingerir evento
result = scraper.ingest_event(
    name="Batalla de Gallos",
    event_type="nacional",
    year=2023,
    country="spain"
)
```

## 📊 Modelos de Base de Datos

### Person (MCs)
```python
- id: Integer (PK)
- aka: String (unique per country)
- full_name: String
- country: Enum (Spain, Argentina, etc.)
- style: Enum (Punchline, Flow, etc.)
- debut_year: Integer
- biography: Text
```

### Event
```python
- id: Integer (PK)
- name: String
- event_type: Enum (Nacional, Internacional, etc.)
- year: Integer
- country: Enum
- city: String
- place: String
- total_participants: Integer
```

### Battle
```python
- id: Integer (PK)
- event_id: FK → Event
- mc1_id: FK → Person
- mc2_id: FK → Person
- winner_id: FK → Person
- round: Enum (Final, Semifinal, etc.)
- format: Enum (1v1, 2v2, etc.)
- duration_seconds: Integer
- video_url: String
```

### Plus: Intervention, LyricAnalysis, Statistics, H2H Records

## 🧪 Testing

```bash
# Ejecutar tests
pytest -v

# Con coverage
pytest --cov=.

# Test específico
pytest tests/test_tools.py::test_search_person_exact_match -v
```

## 🔐 Seguridad

- ✅ Input validation con Pydantic
- ✅ SQL injection prevention (ORM)
- ✅ Rate limiting ready
- ✅ CORS configurado
- ✅ Normalización obligatoria
- ✅ Validación de tipos

## 📈 Performance

- **Búsqueda**: O(n log n) con índices
- **Caché**: O(1) con TTL automático
- **Fuzzy Match**: Optimizado con RapidFuzz
- **Connection Pool**: 10 conexiones + 20 overflow
- **Streaming**: Respuestas inmediatas vía SSE

## 🤝 Contribución

1. Fork el repo
2. Crea feature branch (`git checkout -b feature/amazing`)
3. Commit cambios (`git commit -am 'Add amazing feature'`)
4. Push a rama (`git push origin feature/amazing`)
5. Open Pull Request

## 📝 Changelog

### v2.0.0 (2026-04-27)
- ✅ Arquitectura completa de agentes
- ✅ 30+ herramientas especializadas
- ✅ Tool-loop pattern implementado
- ✅ Manejo de ambigüedades
- ✅ Endpoints REST completos
- ✅ Caché inteligente
- ✅ Web scraping
- ✅ Tests unitarios

### v1.0.0
- SQL Agent básico
- Endpoints de consulta

## 📚 Documentación

- **CLAUDE.md**: Guía completa de arquitectura
- **models.py**: Definiciones de base de datos
- **tools.py**: Especificación de herramientas
- **agents.py**: Lógica de orquestación
- **/docs**: Swagger UI (FastAPI)

## 🎓 Ejemplos

### Ejemplo 1: H2H Simple
```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Dani vs Chuty"}'
```

Response:
```json
{
    "status": "success",
    "answer": "Dani vs Chuty: 7-3 a favor de Dani con 10 enfrentamientos...",
    "intent": {"type": "head_to_head"}
}
```

### Ejemplo 2: Estadísticas con Streaming
```bash
curl -N -X POST http://localhost:8000/api/query/stream \
  -H "Content-Type: application/json" \
  -d '{"query": "Estadísticas de Wos"}'
```

Response (SSE):
```
event: progress
data: {"step": 1, "status": "in_progress"}

event: progress
data: {"step": 2, "status": "tools_executed"}

event: final_result
data: {"answer": "Wos tiene un win rate del 72%..."}
```

### Ejemplo 3: Rankings por País
```bash
curl http://localhost:8000/api/rankings/top-performers?country=spain
```

Response:
```json
[
    {"aka": "Dani", "win_rate": "87.5%", "total_battles": 24},
    {"aka": "Chuty", "win_rate": "75.0%", "total_battles": 20}
]
```

## 🆘 Troubleshooting

### "Connection refused"
```bash
# Verificar que PostgreSQL está ejecutándose
psql postgresql://user:pass@localhost:5432/redbull_batalla
```

### "API Key invalid"
```bash
# Verificar credenciales en .env
export DEEPSEEK_API_KEY="sk-correct-key"
```

### "Ambiguity detected"
El sistema encontró múltiples MCs con nombre similar:
```json
{
    "status": "clarification_needed",
    "ambiguities": [{
        "options": [
            {"id": 1, "aka": "Dani", "country": "spain"},
            {"id": 2, "aka": "Dani", "country": "argentina"}
        ]
    }]
}
```
Especifica país: "Dani España" o "Dani Argentina"

## 📞 Soporte

- 📧 Email: support@redbull-batalla.ai
- 🐛 Issues: github.com/gsusrh/redbull-api/issues
- 💬 Discussions: github.com/gsusrh/redbull-api/discussions

## 📄 Licencia

MIT License - Ver LICENSE.md

---

**Built with ❤️ for Red Bull Batalla Freestyle Community**

*Last Updated: 2026-04-27 | Version: 2.0.0 | Status: Production Ready* ✅
