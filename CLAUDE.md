# Red Bull Batalla Agent Suite - Documentación de Desarrollo

## Descripción General

Suite completa de agentes IA para análisis inteligente de batallas de freestyle Red Bull. Utiliza DeepSeek v4 como LLM orchestrator, FastAPI como framework web, y PostgreSQL para persistencia.

## Arquitectura

### Stack Tecnológico
- **Backend**: FastAPI (Python 3.11+)
- **LLM**: DeepSeek v4 via OpenRouter
- **Base de Datos**: PostgreSQL con SQLAlchemy ORM
- **Validación**: Pydantic v2
- **Búsqueda Difusa**: RapidFuzz
- **Normalización**: Unidecode

### Estructura de Carpetas

```
redbull-api/
├── main.py                          # Punto de entrada FastAPI
├── models.py                        # Modelos SQLAlchemy (Base de Datos)
├── agents.py                        # Orquestador de agentes (BatallaAgent)
├── tools.py                         # Suite completa de herramientas
├── config.py                        # Configuración de LLM
├── utils.py                         # Utilidades (validadores, formateadores)
├── requirements.txt                 # Dependencias Python
├── CLAUDE.md                        # Este archivo
├── services/
│   ├── cache_service.py            # Caché con TTL
│   ├── normalization_service.py    # Normalización de strings
│   ├── scraper_service.py          # Ingesta de datos desde URLs
│   └── query_service.py            # (Existente) Servicios de consultas
└── __pycache__/                    # (Ignorar) Cache de Python
```

## Flujo de Procesamiento

### 1. Request → Agent
```
QueryRequest (Pydantic)
    ↓
BatallaAgent.process_query()
    ├─ Extraer intención (keywords, entities)
    ├─ Ejecutar tool-loop apropiado
    ├─ Validar ambigüedades
    └─ Generar respuesta natural
```

### 2. Tool-Loop (Ciclo de Herramientas)
El agente utiliza un ciclo de validación estricta:

1. **Identificación de Intención**: Clasificar tipo de pregunta
2. **Extracción de Entidades**: Nombres, países, años, rondas
3. **Búsqueda Fuzzy**: Usar RapidFuzz para encontrar coincidencias
4. **Validación de Ambigüedad**: Si hay múltiples opciones, pedir aclaración
5. **Ejecución de Herramientas**: Llamar a métodos específicos del toolkit
6. **Generación de Respuesta**: Crear respuesta natural en español

### 3. Herramientas Disponibles (BatallaToolkit)

#### Búsqueda
- `search_person(query, threshold=80)` → Busca MCs con fuzzy matching
- `search_event(query, threshold=75)` → Busca eventos
- `search_by_style(style)` → Busca por estilo

#### Estadísticas
- `get_person_statistics(person_id)` → Win rate, streaks, etc.
- `get_head_to_head(person1_id, person2_id)` → Historial directo
- `get_top_performers(country=None, limit=10)` → Ranking de MCs
- `get_battle_analysis(battle_id)` → Análisis detallado de batalla

#### Historial
- `get_battles_by_person(person_id, limit=50)` → Batallas de un MC
- `get_battles_by_event(event_id)` → Batallas de un evento
- `get_timeline(person_id)` → Línea de tiempo de carrera
- `get_person_events(person_id)` → Eventos participados

#### Información
- `get_person_by_country(country)` → Todos los MCs de un país
- `get_event_participants(event_id)` → Participantes de evento
- `get_event_details(event_id)` → Detalles completos de evento
- `list_all_persons(country=None)` → Listar todos los MCs
- `list_all_events(year=None)` → Listar todos los eventos

#### Validación
- `get_ambiguity_clarification(aka)` → Detectar ambigüedades
- `_normalize_string(s)` → Normalizar strings

## Tipos de Consultas Soportadas

### 1. Head-to-Head (H2H)
```
Usuario: "Dani vs Chuty España"
Intent: "head_to_head"
Herramientas: search_person (x2) → get_head_to_head
Respuesta: Historial, record, últimas batallas
```

### 2. Estadísticas
```
Usuario: "Estadísticas de Dani"
Intent: "statistics"
Herramientas: search_person → get_person_statistics → get_battles_by_person
Respuesta: Win rate, rachas, historial
```

### 3. Ranking
```
Usuario: "Top 10 mejores freestylers"
Intent: "ranking"
Herramientas: get_top_performers
Respuesta: Ranking con win rates
```

### 4. Evento
```
Usuario: "Batalla de Gallos España 2023"
Intent: "event_details"
Herramientas: search_event → get_event_details
Respuesta: Participantes, batallas, ganador
```

### 5. Historial
```
Usuario: "Carrera de Chuty"
Intent: "history"
Herramientas: search_person → get_timeline → get_person_events
Respuesta: Línea de tiempo cronológica
```

### 6. Búsqueda General
```
Usuario: "¿Quién es Wos?"
Intent: "general_search"
Herramientas: search_person (fallback a search_event)
Respuesta: Información básica
```

## Manejo de Ambigüedades

Si una búsqueda retorna múltiples opciones, el sistema:

1. Detiene el procesamiento
2. Solicita al usuario que aclare cuál opción:
```json
{
    "status": "clarification_needed",
    "ambiguities": [
        {
            "field": "mc1",
            "query": "Dani",
            "options": [
                {"id": 1, "aka": "Dani", "country": "spain"},
                {"id": 2, "aka": "Dani", "country": "argentina"}
            ]
        }
    ]
}
```

3. User proporciona clarificación
4. Reintenta con ambigüedad resuelta

## Endpoints Principales

### Queries
- `POST /api/query` → Respuesta directa
- `POST /api/query/stream` → Streaming con SSE
- `POST /api/chat` → Chat con historial

### Search
- `GET /api/search/persons?q=Dani` → Buscar MCs
- `GET /api/search/events?q=España` → Buscar eventos

### Statistics
- `GET /api/person/{id}/stats` → Estadísticas de MC
- `GET /api/battle/{id}` → Detalles de batalla
- `GET /api/h2h/{id1}/{id2}` → H2H entre dos MCs

### Rankings
- `GET /api/rankings/top-performers?country=spain` → Ranking
- `GET /api/rankings/by-style?style=punchline` → Por estilo

### Events
- `GET /api/events?year=2023` → Listar eventos
- `GET /api/event/{id}` → Detalles de evento

### Data Ingestion
- `POST /api/ingest/person` → Añadir MC
- `POST /api/ingest/event` → Añadir evento
- `POST /api/scrape` → Scrape desde URL

## Desarrollo Local

### Setup
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Configuración
```bash
export DATABASE_URI="postgresql://user:pass@host/db"
export DEEPSEEK_API_KEY="sk-..."
```

### Ejecutar
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Testing
```bash
pytest -v
```

## Patrones Importantes

### 1. Validación Estricta
```python
# Siempre validar entrada
if not query:
    raise HTTPException(status_code=422, detail="Empty query")
```

### 2. Manejo de Ambigüedades
```python
# Busca difusa y validación
results = toolkit.search_person(query)
if len(results) > 1:
    return ambiguity_resolver.ask_for_clarification(results)
```

### 3. Caché Inteligente
```python
# Usar caché para consultas frecuentes
cache_key = f"person_stats_{person_id}"
cached = cache.get(cache_key)
if cached: return cached
# Calcular y cachear
result = calculate_stats(person_id)
cache.set(cache_key, result)
```

### 4. Normalización
```python
# Normalizar siempre antes de comparar
normalized = normalizer.normalize(user_input)
matches = toolkit.search_person(normalized)
```

## Enumeraciones

### Countries
Spain, Argentina, Mexico, Colombia, Chile, Peru, Ecuador, Venezuela, Brazil, Panama, Costa Rica, Cuba, Dominican Republic, Puerto Rico, USA, France, Italy, Portugal, Germany

### Rounds
Qualifying, Round 16, Quarterfinals, Semifinals, Final, Exhibition

### Formats
1v1, 2v2, Tag Team, Tournament, Exhibition

### Styles
Punchline, Flow, Trap, Wordplay, Storytelling, Aggressive, Technical, Mixed

### Event Types
Nacional, Internacional, Regional, Street

## Base de Datos

### Tablas Principales
- **persons** → MCs/Freestylers
- **events** → Eventos (Nacionales, Internacionales, etc.)
- **battles** → Enfrentamientos
- **interventions** → Barras individuales
- **lyric_analysis** → Análisis lingüísticos
- **person_statistics** → Estadísticas pre-calculadas
- **battle_statistics** → Estadísticas de batalla
- **head_to_head_records** → Históricos directos
- **event_participations** → Participación en eventos

### Índices Críticos
- `idx_aka` → Búsqueda rápida de MCs
- `idx_battle_event` → Batallas por evento
- `idx_h2h_person1/2` → Búsqueda H2H

## Mejoras Futuras

- [ ] Análisis de letras/transcripciones con NLP
- [ ] Generador de highlights automático
- [ ] Agente de trivias
- [ ] Integración con streaming en vivo
- [ ] Recomendaciones personalizadas
- [ ] Predicción de ganadores

## Notas de Desarrollo

- **Zero-Error Philosophy**: Validación estricta en todo momento
- **Normalización Obligatoria**: Todos los strings normalizados antes de comparar
- **Tool-Loop Pattern**: Siempre seguir el ciclo de herramientas
- **Streaming First**: Usar SSE para respuestas largas
- **Caché Agresivo**: Cachear estadísticas calculadas

## Contribución

Al hacer cambios:
1. Mantener la estructura modular
2. Añadir docstrings a nuevas funciones
3. Validar input en boundaries (user input, external APIs)
4. No agregar herramientas sin herramientas de validación
5. Actualizar este documento si cambias la arquitectura

---

**Última actualización**: 2026-04-27
**Versión**: 2.0.0
**Estado**: Production-ready
