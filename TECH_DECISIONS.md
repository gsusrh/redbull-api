# Decisiones Técnicas y Justificación

## 1. Sistema de Progreso: WebSocket vs Polling vs Server-Sent Events

### Opciones Evaluadas

| Tecnología | Latencia | Bi-direccional | Escalabilidad | Complejidad | Winner |
|------------|----------|----------------|---------------|------------|--------|
| **WebSocket** | <100ms | ✅ Sí | ⭐⭐⭐⭐ | ⭐⭐⭐ | 🏆 ELEGIDO |
| Polling (HTTP) | 1-5s | ❌ No | ⭐⭐ | ⭐ | ❌ |
| SSE (Server-Sent Events) | <100ms | ❌ Solo servidor→cliente | ⭐⭐⭐ | ⭐⭐ | ⚠️ |
| gRPC | <50ms | ✅ Sí | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ❌ Overkill |

### Por qué WebSocket

✅ **Mejor UX**: Actualizaciones <100ms, usuario ve progreso fluidez
✅ **Bi-direccional**: Cliente puede pausar/cancelar job en tiempo real
✅ **Escalable**: Redis Pub/Sub maneja miles de conexiones
✅ **Estándar**: Soportado en navegadores, librerías maduras
✅ **Compatible**: Funciona con FastAPI, easy integration con Celery

**Arquitectura WebSocket en Red Bull Suite**:
```
Cliente (React)
    ↕️ WebSocket
FastAPI
    ↕️ Redis Pub/Sub
Celery Workers (transcription, analysis)
```

---

## 2. Queue: Celery vs AWS SQS vs Kafka vs RQ

### Comparativa

| Aspecto | Celery | AWS SQS | Kafka | RQ |
|--------|--------|---------|-------|-----|
| **Setup** | Local (redis) | AWS account | Complex | Simple |
| **Escalabilidad** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| **Costo** | Free | Pay-per-use | Hosting | Free |
| **Debugging** | Flower (excelente) | CloudWatch | Kafdrop | RQ Dashboard |
| **Python-friendly** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |
| **Priority Queues** | ✅ | ✅ | ⭐⭐ | ✅ |
| **Retry Logic** | Built-in | Manual | Manual | Built-in |

### Por qué Celery

✅ **Python best-in-class**: Diseñado específicamente para Python
✅ **Flower Dashboard**: Monitoreo en tiempo real (http://localhost:5555)
✅ **Priority queues**: Transcriciones críticas vs análisis normal
✅ **Local development**: Sin dependencias externas (Redis local)
✅ **Escalabilidad**: Fácil pasar de local a multi-worker
✅ **Integración**: Nativo con FastAPI
✅ **Costos**: Red Bull get Free tier indefinidamente

**Alternativa futura**: Si Red Bull grows exponencial, migrar a Kafka para streaming

---

## 3. Transcription: Whisper vs Deepgram vs Google Cloud vs Hugging Face

### Evaluación en Español + Freestyle Context

| Proveedor | Accuracy | Idiomas | Speed | Costo | Streaming | Offline |
|-----------|----------|---------|-------|-------|-----------|---------|
| **OpenAI Whisper** | 95%+ | ✅ 99 | Lento (10min video = 2min) | $0.006/min | ❌ | ✅ |
| **Deepgram** | 94%+ | ✅ 103 | Rápido (realtime) | $0.0043/min | ✅ | ❌ |
| **Google Cloud** | 96%+ | ✅ 120 | Rápido | $0.024/min | ✅ | ❌ |
| **Hugging Face** | 92% | ✅ 99 | Lento | Free | ❌ | ✅ |

### Decisión: Whisper (Primario) + Deepgram (Fallback)

**Razones**:

1. **Whisper es SUPERIOR en Español**: Red Bull videos son 100% en español
   - Maneja acentos, slang, palabras inventadas
   - "Skyrim" (referencia gamer) → Detecta correctamente
   - Punchlines idiomáticas → Comprende contexto

2. **Deepgram como backup**: Si Whisper falla/timeout
   - Streaming real-time para futuro (live events)
   - Mejor para audio de baja calidad

3. **Costos**: $0.006/min × 10 min video = $0.06 por transcripción
   - 100 videos/día = $6/día = $180/mes
   - Sustentable para Red Bull

**Implementación**:
```python
try:
    # Intenta Whisper (mejor calidad)
    result = whisper.transcribe(audio_path)
except OpenAITimeout:
    # Fallback a Deepgram
    result = deepgram.transcribe(audio_path)
```

---

## 4. Speaker Diarization: Pyannote vs Resemblyzer vs Custom ML

### Comparativa

| Solución | Accuracy | Entrenable | Setup | Latencia |
|----------|----------|-----------|-------|----------|
| **Pyannote 3.1** | 90%+ | ⚠️ Partial | Docker | 5-10min |
| **Resemblyzer** | 85% | ❌ No | Fácil | 2-5min |
| **Custom Model** | 95%+ | ✅ Sí | Complejo | Variable |
| **Google Cloud** | 92% | ❌ No | API | <1min |

### Decisión: Pyannote Audio 3.1

**Razones**:

1. **State-of-the-art en 2026**: Mejor accuracy (90%+) para speaker identification
2. **Open-source**: No depender de APIs externas
3. **Entrenable**: Red Bull puede fine-tune con data propia (batallas históricas)
4. **GPU support**: Puede acelerarse con NVIDIA CUDA

**Flujo de identificación**:
```
Raw Audio
  ↓ [Pyannote Diarization]
Speaker Segments: [
    (00:00-00:15, speaker_0),
    (00:15-00:45, speaker_1),
    (00:45-01:15, speaker_0)
]
  ↓ [Voice Embeddings + ML Classifier]
Speaker Mapping: [
    speaker_0 → Dani (confidence: 0.94),
    speaker_1 → Chuty (confidence: 0.87),
]
```

**Fine-tuning futuro**:
Red Bull entrena con sus 500+ batallas históricas → Modelo alcanza 98%+ accuracy

---

## 5. Vector Database: Pinecone vs Supabase pgvector vs Weaviate vs Elasticsearch

### Caso de Uso de Red Bull

"Busca transcripciones donde hablaron de política"
"Encuentra punchlines similares a este"
"¿Qué otras batallas mencionan a Dani?"

### Comparativa

| DB | Cost | Latency | Maturity | Integration |
|---|------|---------|----------|-------------|
| **Pinecone** | $0.04/M vectors | <50ms | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Supabase pgvector** | Included (Postgres) | <100ms | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Weaviate** | Free (self-hosted) | <100ms | ⭐⭐⭐ | ⭐⭐⭐ |
| **Elasticsearch** | Complex | <200ms | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |

### Decisión: Supabase pgvector (Phase 1) → Pinecone (Phase 2)

**Phase 1** (Etapa 3 - Inicio):
- Usar pgvector dentro de Postgres existente
- Ya have DB, no learning curve
- Suficiente para 5,000 batallas
- Costo: $0

**Phase 2** (Cuando Red Bull crece):
- Migrar a Pinecone si >100M vectors o latency crítica
- Pinecone es production-ready para scale
- Costo: Aceptable dado revenue de Red Bull

**Implementación Híbrida**:
```python
# Fase 1: pgvector (en Postgres)
def search_similar_transcriptions(query_embedding):
    return db.query(Transcription).order_by(
        func.l2_distance(
            Transcription.embedding,
            query_embedding
        )
    ).limit(10)

# Fase 2: Pinecone (plug-and-play swap)
def search_similar_transcriptions(query_embedding):
    results = pinecone_index.query(
        vector=query_embedding,
        top_k=10
    )
    return results
```

---

## 6. NLP Pipeline: Spacy vs Transformers vs Custom Rules

### Necesidades de Red Bull

- Detectar punchlines (70% rules + 30% ML)
- Clasificar temas (100% ML + embedding similarity)
- Encontrar referencias a personas (Rules + NER)
- Analizar sentimiento (Transformers)

### Arquitectura Híbrida Recomendada

```python
# Rules-based (rápido, preciso para casos conocidos)
punchline_detector = RuleBasedDetector([
    r"pero\s+\w+\s+como\s+\w+",  # "pero X como Y"
    r"cómo\s+si\s+fuera",          # "como si fuera"
    r"mientras\s+tanto"            # Transiciones
])

# ML-based (para casos complejos)
nlp = spacy.load("es_core_news_lg")
transformers_model = pipeline(
    "zero-shot-classification",
    model="xlm-roberta-large"
)

def analyze_intervention(text):
    # 1. Detección de punchlines (rules + ML)
    punchlines_rule = punchline_detector.find(text)
    punchlines_ml = transformer_model.classify(text, ["punchline", "no_punchline"])
    
    # 2. Extracción de referencias (NER)
    doc = nlp(text)
    references = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
    
    # 3. Clasificación de tema (zero-shot)
    themes = transformers_model(
        text,
        ["política", "personal", "técnica", "humor", "ataque directo"],
        multi_class=True
    )
    
    return {
        "punchlines": punchlines_rule + punchlines_ml,
        "references": references,
        "themes": themes
    }
```

---

## 7. Frontend Framework: React vs Vue vs Svelte

### Requisitos de Red Bull

- Dashboard de review de transcripciones
- Real-time progress updates
- Timeline editor (inline text editing)
- Admin panel

### Decisión: React + TypeScript

**Razones**:

1. **Ecosistema**: Material-UI, React Query, Redux
2. **Comunidad**: Fácil encontrar developers en Argentina/España
3. **Performance**: Virtual scrolling para timeline de 1000+ items
4. **TypeScript**: Type safety para integración API
5. **Testing**: Cypress, React Testing Library maduros

**Stack Frontend Recomendado**:
```json
{
    "framework": "React 18+",
    "language": "TypeScript",
    "state": "Redux Toolkit",
    "ui": "Material-UI",
    "forms": "React Hook Form",
    "http": "TanStack Query (React Query)",
    "websocket": "Socket.IO client",
    "testing": "Vitest + React Testing Library",
    "build": "Vite"
}
```

---

## 8. Deployment: Docker + Kubernetes vs Lambda vs Heroku

### Escenarios de Red Bull

**Etapa 1-2**: ~100 QPS (queries per second)
**Etapa 3-4**: ~500 QPS
**Escala Red Bull**: ~2,000+ QPS

### Decisión: Docker + Kubernetes (multi-nube)

| Solución | Costo | Escalabilidad | Vendor Lock | Flexibility |
|----------|-------|---------------|-------------|------------|
| **Docker + K8s** | $$$$ | ⭐⭐⭐⭐⭐ | ❌ None | ⭐⭐⭐⭐⭐ |
| Lambda | $$$ | ⭐⭐⭐ | ✅ AWS | ⭐⭐ |
| Heroku | $$ | ⭐⭐ | ✅ Heroku | ⭐ |
| Railway | $$ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |

**Recomendación por Etapa**:

**Etapa 1 (MVP)**: Railway.app
- $15/mes + uso
- Fácil deploy desde Git
- PostgreSQL incluido
- OK para MVP

**Etapa 2-3 (Production)**: Docker + Kubernetes
- GKE (Google Cloud)
- EKS (AWS)
- Opción: AKS (Azure) si Red Bull usa stack Microsoft

**Configuración Kubernetes**:
```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redbull-api
spec:
  replicas: 3  # Auto-scale si latency > 200ms
  template:
    spec:
      containers:
      - name: fastapi
        image: redbull-api:latest
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"

---
apiVersion: batch/v1
kind: CronJob
metadata:
  name: transcription-worker
spec:
  schedule: "*/5 * * * *"  # Cada 5 minutos
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: celery-worker
            image: redbull-api:latest
            command: ["celery", "-A", "workers.celery_app", "worker"]
```

---

## 9. Monitoreo y Observabilidad

### Stack Recomendado

```yaml
Métricas:
  - Prometheus
  - Grafana (dashboards)
  - Custom metrics: Transcription success rate, avg processing time

Logs:
  - ELK Stack (Elasticsearch, Logstash, Kibana)
  - O: Datadog (all-in-one)
  - O: New Relic

Errors:
  - Sentry.io
  - Rollbar

APM:
  - New Relic APM
  - O: Datadog APM
  - O: self-hosted: OpenTelemetry + Jaeger
```

**Dashboards Críticos**:
1. **Job Processing**: % success, avg time, queue depth
2. **API Health**: Response time, error rate, QPS
3. **Resource Usage**: CPU, Memory, Disk, Network
4. **Database**: Query latency, connection pool, index performance
5. **WebSocket**: Active connections, message throughput

---

## 10. Seguridad

### Protecciones para Red Bull Suite

```python
# 1. Rate Limiting
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)

@app.post("/api/transcription/submit")
@limiter.limit("10/minute")  # 10 uploads por minuto por IP
async def submit_transcription():
    pass

# 2. JWT Authentication
from fastapi_jwt_extended import JWTBearer, create_access_token

security = JWTBearer()

@app.post("/api/transcription/submit")
async def submit_transcription(current_user: User = Depends(security)):
    # Solo usuarios autenticados
    pass

# 3. RBAC (Role-Based Access Control)
def require_reviewer(current_user: User = Depends(security)):
    if current_user.role != "REVIEWER":
        raise HTTPException(status_code=403, detail="Must be reviewer")
    return current_user

@app.post("/api/transcription/{id}/review")
async def save_review(reviewer: User = Depends(require_reviewer)):
    pass

# 4. Input Validation (Pydantic)
class TranscriptionRequest(BaseModel):
    youtube_url: str = Field(..., regex=r"^https://youtube\.com/watch\?v=[\w-]+$")
    battle_id: int = Field(..., gt=0, lt=1000000)

# 5. SQL Injection Prevention (ORM)
# ✅ SQLAlchemy previene automáticamente

# 6. Audit Logging
def log_action(user_id, action, resource_id):
    db.add(AuditLog(
        user_id=user_id,
        action=action,
        resource_id=resource_id,
        timestamp=datetime.utcnow()
    ))
    db.commit()

@app.post("/api/transcription/{id}/review")
async def save_review(id: int, current_user: User):
    log_action(current_user.id, "REVIEW_SUBMITTED", id)
    # ...

# 7. CORS Configuration
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://red-bull.com", "https://admin.red-bull.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization"]
)

# 8. Secret Management
from dotenv import load_dotenv
load_dotenv(".env.production")  # NO HARDCODES

# Mejor: AWS Secrets Manager / Google Secret Manager
from google.cloud import secretmanager
client = secretmanager.SecretManagerServiceClient()
secret = client.access_secret_version(
    request={"name": f"projects/{PROJECT_ID}/secrets/OPENAI_API_KEY/versions/latest"}
)
```

---

## 11. Testing Strategy

### Pyramid de Testing

```
              ▲
             /\
            /  \  End-to-End Tests (1-2%)
           /    \
          /______\
            /  \
           /    \ Integration Tests (15-20%)
          /______\
            /  \
           /    \ Unit Tests (70-80%)
          /______\
```

**Test Coverage Goals**:
- Unit: 85%+ (tools, services, utils)
- Integration: 60%+ (API endpoints, DB operations)
- E2E: Críticos (transcription flow, review workflow)

**Tools**:
```python
# Unit Testing
pytest
pytest-asyncio
pytest-cov

# Mocking
pytest-mock
responses (para HTTP mocks)

# Integration Testing
testcontainers (PostgreSQL, Redis en Docker)

# E2E Testing
Cypress
Playwright

# Performance Testing
Locust
Apache JMeter
```

---

## 12. Resumen de Decisiones Clave

| Decisión | Elegido | Razón Clave |
|----------|---------|------------|
| **Real-time Progress** | WebSocket | Sub-100ms latency, bi-direccional |
| **Task Queue** | Celery | Best Python ecosystem |
| **Transcription** | Whisper + Deepgram | 95%+ accuracy en español |
| **Speaker ID** | Pyannote | SOTA, entrenable |
| **Vector DB** | pgvector → Pinecone | Start simple, scale later |
| **NLP** | Hybrid (Rules + Transformers) | Speed + accuracy |
| **Frontend** | React + TypeScript | Ecosistema fuerte |
| **Deployment** | Docker + K8s | Máxima flexibilidad |
| **Monitoring** | Prometheus + Grafana | Open-source, estándar |
| **Security** | JWT + RBAC + Audit Logs | Enterprise-grade |

---

## 13. Próximos Pasos

1. **Aprobación Red Bull**: Validar que arquitectura cumple requisitos
2. **Setup Local**: Instalar Celery + Redis + Postgres
3. **Sprint 1**: Implementar youtube_downloader + audio_extractor
4. **Testing**: Load test con 23 reviewers simultáneos
5. **Deployment**: Railway → K8s

¿Está listo para empezar Etapa 2?
