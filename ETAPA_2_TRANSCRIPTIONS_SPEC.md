# ETAPA 2: Sistema Completo de Transcripciones + Real-Time Progress

## 1. Visión de la Etapa 2

**Objetivo**: Transformar videos YouTube de batallas en transcripciones estructuradas con análisis de speaker y sistema de review manual.

**Entrada**: `https://youtube.com/watch?v=xYz123`
**Salida**: 
```json
{
  "battle_id": 123,
  "transcription": {
    "text": "Dani: [00:05] blablabla...",
    "speaker_turns": [...],
    "metadata": {...}
  },
  "status": "PENDING_MANUAL_REVIEW",
  "review_dashboard_url": "..."
}
```

**Timeline**: 10-20 minutos de video → Transcripción automática + Identificación de speakers + Listo para review manual

---

## 2. Arquitectura de Transcripciones

```
┌─ YouTube URL ────────────────────┐
│  (Usuario proporciona)            │
└────────────────┬──────────────────┘
                 │
         ┌───────▼────────┐
         │ Video Downloader│  (yt-dlp)
         └───────┬────────┘
                 │
         ┌───────▼────────┐
         │ Audio Extractor │  (FFmpeg)
         └───────┬────────┘
                 │
         ┌───────▼──────────────┐
         │ Transcription Engine  │  (OpenAI Whisper)
         │ ↓ + Backup (Deepgram)│
         └───────┬──────────────┘
                 │
         ┌───────▼────────────┐
         │ Speaker Diarization │  (Pyannote Audio)
         └───────┬────────────┘
                 │
         ┌───────▼─────────────┐
         │ Speaker Mapping      │  (ML matching)
         │ Speaker_1 → Dani    │
         │ Speaker_2 → Chuty   │
         └───────┬─────────────┘
                 │
         ┌───────▼──────────────┐
         │ Text Processing      │  (Limpieza, segmentación)
         └───────┬──────────────┘
                 │
         ┌───────▼──────────────┐
         │ Manual Review Queue   │  (Para 23 reviewers)
         └──────────────────────┘
```

---

## 3. Sistema de Progreso (WebSocket + Celery)

### 3.1 Endpoints

#### POST /api/transcription/submit
```python
Request:
{
    "youtube_url": "https://youtube.com/watch?v=...",
    "battle_id": 123,  # Opcionalmente vincular a batalla existente
    "notes": "Batalla Dani vs Chuty, final 2024"
}

Response:
{
    "job_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "PENDING",
    "websocket_url": "ws://localhost:8000/ws/job/550e8400-e29b-41d4-a716-446655440000",
    "estimated_duration_minutes": 15
}
```

#### GET /api/transcription/job/{job_id}
```python
Response:
{
    "job_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "TRANSCRIBING",
    "progress": 45,
    "stage": "TRANSCRIBING",
    "current_message": "Transcribiendo: 00:05:30 / 00:12:45",
    "eta_seconds": 420,
    "timeline": [
        {
            "timestamp": "2026-04-27T10:00:00Z",
            "stage": "DOWNLOADING",
            "progress": 15,
            "message": "..."
        },
        ...
    ]
}
```

#### WS /ws/job/{job_id}
```python
# Cliente se conecta
ws = WebSocket('ws://localhost:8000/ws/job/550e8400...')

# Servidor emite eventos
{
    "type": "progress",
    "job_id": "550e8400-e29b-41d4-a716-446655440000",
    "stage": "TRANSCRIBING",
    "progress": 45,
    "message": "Transcribiendo 00:05:30 / 00:12:45",
    "eta_seconds": 420,
    "timestamp": "2026-04-27T10:04:00Z"
}

# Cuando completa
{
    "type": "complete",
    "job_id": "550e8400-e29b-41d4-a716-446655440000",
    "result": {
        "transcription_id": 789,
        "battle_id": 123,
        "duration_seconds": 765,
        "word_count": 5432,
        "speaker_count": 3,
        "speakers": {
            "speaker_1": "Dani",
            "speaker_2": "Chuty",
            "speaker_3": "Juez"
        },
        "confidence_score": 0.94,
        "review_url": "/dashboard/review/789"
    }
}
```

### 3.2 Estados de Transición

```
PENDING
  ↓ (Worker inicia)
DOWNLOADING (0-15%)
  "Descargando video (2.4 MB / 145 MB)..."
  ↓
EXTRACTING_AUDIO (15-25%)
  "Extrayendo audio de video..."
  ↓
TRANSCRIBING (25-75%)
  "Transcribiendo con OpenAI Whisper..."
  Milestones: 25% → 50% → 75%
  ↓
DIARIZING (75-85%)
  "Identificando speakers..."
  "Speaker 1: 83% confidence → Dani"
  "Speaker 2: 79% confidence → Chuty"
  ↓
PROCESSING (85-95%)
  "Procesando texto..."
  "Detectadas 34 intervenciones"
  "Identificadas 67 referencias"
  ↓
INDEXING (95-100%)
  "Indexando para búsqueda..."
  ↓
COMPLETE (100%)
  "¡Transcripción completada!"
  
O en caso de error:
  ↓
FAILED
  "Error: Could not extract audio"
  Auto-retry enabled (1 de 3 intentos)
```

---

## 4. Modelos de Base de Datos

### 4.1 Tabla: transcription_jobs

```sql
CREATE TABLE transcription_jobs (
    id UUID PRIMARY KEY,
    youtube_url VARCHAR(500) NOT NULL,
    battle_id INT FOREIGN KEY REFERENCES battles(id),
    status ENUM('PENDING', 'DOWNLOADING', ..., 'COMPLETE', 'FAILED'),
    progress INT (0-100),
    stage VARCHAR(50),
    
    -- Timestamps
    created_at TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    
    -- Metadata
    video_duration_seconds INT,
    video_title VARCHAR(255),
    video_duration_seconds INT,
    
    -- Resultado
    transcription_id INT FOREIGN KEY REFERENCES transcriptions(id),
    error_message TEXT,
    retry_count INT DEFAULT 0,
    
    -- Storage
    video_path_s3 VARCHAR(255),
    audio_path_s3 VARCHAR(255),
    transcription_raw JSON,
    diarization_result JSON
);
```

### 4.2 Tabla: transcriptions

```sql
CREATE TABLE transcriptions (
    id INT PRIMARY KEY,
    battle_id INT FOREIGN KEY,
    job_id UUID FOREIGN KEY,
    
    -- Contenido
    full_text TEXT,
    structured_data JSON,  -- { "turns": [...], "metadata": {} }
    
    -- Metadata
    duration_seconds INT,
    word_count INT,
    speaker_count INT,
    
    -- Calidad
    confidence_score FLOAT (0.0 - 1.0),
    accuracy_estimate FLOAT,
    
    -- Versiones
    version INT,  -- Para tracking de cambios
    is_manual_review_complete BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    created_at TIMESTAMP,
    manual_review_completed_at TIMESTAMP
);
```

### 4.3 Tabla: speaker_assignments

```sql
CREATE TABLE speaker_assignments (
    id INT PRIMARY KEY,
    transcription_id INT FOREIGN KEY,
    speaker_diarization_id VARCHAR(50),  -- "speaker_0", "speaker_1"
    person_id INT FOREIGN KEY,
    confidence_score FLOAT,
    
    -- Manual review
    confirmed_by_reviewer BOOLEAN DEFAULT FALSE,
    reviewed_at TIMESTAMP
);
```

### 4.4 Tabla: transcription_edits

```sql
CREATE TABLE transcription_edits (
    id INT PRIMARY KEY,
    transcription_id INT FOREIGN KEY,
    edited_by INT (reviewer_id),
    
    segment_index INT,  # Qué parte fue editada
    before TEXT,
    after TEXT,
    
    edit_type ENUM('TEXT_CORRECTION', 'SPEAKER_ADJUSTMENT', 'PUNCHLINE_MARK'),
    reason TEXT,
    
    created_at TIMESTAMP
);
```

---

## 5. Implementación del Worker (Celery)

### 5.1 celery_app.py

```python
from celery import Celery
from kombu import Exchange, Queue
import redis

app = Celery('redbull_batalla')
app.conf.broker_url = 'redis://localhost:6379/0'
app.conf.result_backend = 'redis://localhost:6379/1'

# Queues
app.conf.task_queues = (
    Queue('transcription', Exchange('transcription'), routing_key='transcription.#'),
    Queue('analysis', Exchange('analysis'), routing_key='analysis.#'),
    Queue('indexing', Exchange('indexing'), routing_key='indexing.#'),
)

# Priority
app.conf.task_acks_late = True
app.conf.worker_prefetch_multiplier = 1
```

### 5.2 transcription_worker.py

```python
from celery import shared_task
from services.transcription_service import TranscriptionService
from services.websocket_manager import WebSocketManager
import asyncio

ws_manager = WebSocketManager()
transcription_service = TranscriptionService()

@shared_task(bind=True)
def process_transcription(self, job_id: str, youtube_url: str, battle_id: int):
    """
    Celery task: Procesa completo de transcripción
    Emite eventos por WebSocket en cada milestone
    """
    
    try:
        # Estado inicial
        await ws_manager.broadcast(job_id, {
            "type": "progress",
            "stage": "DOWNLOADING",
            "progress": 0,
            "message": "Iniciando descarga..."
        })
        
        # 1. Descargar video
        video_path = await transcription_service.download_video(youtube_url, job_id)
        await ws_manager.broadcast(job_id, {
            "type": "progress",
            "stage": "DOWNLOADING",
            "progress": 15,
            "message": f"Video descargado ({video_path})"
        })
        
        # 2. Extraer audio
        audio_path = await transcription_service.extract_audio(video_path, job_id)
        await ws_manager.broadcast(job_id, {
            "type": "progress",
            "stage": "EXTRACTING_AUDIO",
            "progress": 25,
            "message": "Audio extraído"
        })
        
        # 3. Transcribir
        transcription_result = await transcription_service.transcribe_audio(
            audio_path, 
            job_id,
            progress_callback=lambda p: ws_manager.broadcast(job_id, {
                "type": "progress",
                "stage": "TRANSCRIBING",
                "progress": 25 + (p * 0.5),  # 25-75%
                "message": f"Transcribiendo... {p*100:.0f}%"
            })
        )
        
        # 4. Speaker diarization
        diarization_result = await transcription_service.diarize_speakers(
            audio_path,
            job_id
        )
        await ws_manager.broadcast(job_id, {
            "type": "progress",
            "stage": "DIARIZING",
            "progress": 80,
            "message": "Identificando speakers..."
        })
        
        # 5. Mapear speakers a personas
        speaker_mapping = await transcription_service.map_speakers_to_persons(
            diarization_result,
            battle_id
        )
        
        # 6. Procesar texto
        processed = await transcription_service.process_text(
            transcription_result,
            speaker_mapping
        )
        
        # 7. Guardar en BD
        transcription_id = await transcription_service.save_to_db(
            job_id, 
            battle_id,
            processed
        )
        
        # 8. Indexar para búsqueda
        await transcription_service.index_for_search(transcription_id)
        
        # Completado
        await ws_manager.broadcast(job_id, {
            "type": "complete",
            "progress": 100,
            "result": {
                "transcription_id": transcription_id,
                "status": "PENDING_MANUAL_REVIEW"
            }
        })
        
        return {"status": "success", "transcription_id": transcription_id}
        
    except Exception as e:
        # Error handling
        await ws_manager.broadcast(job_id, {
            "type": "error",
            "message": str(e)
        })
        # Auto-retry
        self.retry(countdown=10, max_retries=3)
```

---

## 6. WebSocket Manager

### 6.1 websocket_manager.py

```python
from fastapi import WebSocket
from redis import Redis
import json
from typing import Dict, Set

class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.redis = Redis(host='localhost', port=6379, db=2)
    
    async def connect(self, job_id: str, websocket: WebSocket):
        await websocket.accept()
        if job_id not in self.active_connections:
            self.active_connections[job_id] = set()
        self.active_connections[job_id].add(websocket)
        
        # Enviar histórico de eventos
        history = self.redis.lrange(f"job_history:{job_id}", 0, -1)
        for event in history:
            await websocket.send_json(json.loads(event))
    
    async def disconnect(self, job_id: str, websocket: WebSocket):
        self.active_connections[job_id].discard(websocket)
    
    async def broadcast(self, job_id: str, message: dict):
        """Envía evento a todos los clientes conectados"""
        json_msg = json.dumps(message)
        
        # Guardar en Redis (historial)
        self.redis.rpush(f"job_history:{job_id}", json_msg)
        self.redis.expire(f"job_history:{job_id}", 604800)  # 7 días
        
        # Enviar a clientes activos
        if job_id in self.active_connections:
            for connection in self.active_connections[job_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    pass  # Cliente desconectado

# En main.py
manager = WebSocketManager()

@app.websocket("/ws/job/{job_id}")
async def websocket_endpoint(websocket: WebSocket, job_id: str):
    await manager.connect(job_id, websocket)
    try:
        while True:
            # Esperar mensajes del cliente
            data = await websocket.receive_text()
            # Procesar comandos (pause, cancel, etc)
    except Exception:
        await manager.disconnect(job_id, websocket)
```

---

## 7. Servicios de Transcripción

### 7.1 transcription_service.py (Estructura)

```python
class TranscriptionService:
    
    def __init__(self):
        self.whisper_client = OpenAI(api_key=OPENAI_API_KEY)
        self.deepgram_client = DeepgramClient(api_key=DEEPGRAM_API_KEY)
        self.diarization_pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1"
        )
    
    async def download_video(self, url: str, job_id: str) -> str:
        """Descarga video desde YouTube usando yt-dlp"""
        # Implementación
    
    async def extract_audio(self, video_path: str, job_id: str) -> str:
        """Extrae audio usando FFmpeg"""
        # Implementación
    
    async def transcribe_audio(self, audio_path: str, job_id: str) -> dict:
        """Transcribe usando Whisper (+ fallback Deepgram)"""
        try:
            # Intenta con Whisper (mejor calidad)
            result = self.whisper_client.audio.transcriptions.create(
                model="whisper-1",
                file=open(audio_path, "rb"),
                language="es"
            )
        except:
            # Fallback a Deepgram
            result = self.deepgram_client.transcribe(audio_path)
        
        return result
    
    async def diarize_speakers(self, audio_path: str, job_id: str) -> dict:
        """Identifica quién habla en cada momento"""
        # Implementación con Pyannote
    
    async def map_speakers_to_persons(self, diarization: dict, battle_id: int) -> dict:
        """Mapea speaker_0, speaker_1, etc. a personas reales (Dani, Chuty)"""
        # ML matching con voice embeddings
    
    async def process_text(self, transcription: dict, mapping: dict) -> dict:
        """Limpia, normaliza, segmenta en barras"""
        # Implementación
    
    async def save_to_db(self, job_id: str, battle_id: int, processed: dict) -> int:
        """Guarda todo en PostgreSQL"""
        # Implementación
    
    async def index_for_search(self, transcription_id: int):
        """Crea embeddings para búsqueda vectorial (Etapa 3)"""
        # Implementación
```

---

## 8. Dashboard de Review Manual

### 8.1 Interfaz React (Frontend)

```javascript
// ReviewDashboard.jsx

export default function ReviewDashboard() {
  const [jobs, setJobs] = useState([]);
  const [currentReview, setCurrentReview] = useState(null);
  
  // Cargar jobs pendientes
  useEffect(() => {
    fetchPendingJobs();
  }, []);
  
  const fetchPendingJobs = async () => {
    const res = await fetch('/api/transcription/pending');
    const data = await res.json();
    setJobs(data);
  };
  
  const handleEditTranscription = (job) => {
    setCurrentReview(job);
    // Abrir editor
  };
  
  return (
    <div className="dashboard">
      <h1>Review de Transcripciones</h1>
      
      {currentReview ? (
        <TranscriptionEditor 
          job={currentReview}
          onSave={handleSave}
          onCancel={() => setCurrentReview(null)}
        />
      ) : (
        <JobsList jobs={jobs} onSelect={handleEditTranscription} />
      )}
    </div>
  );
}

// TranscriptionEditor.jsx
export default function TranscriptionEditor({ job, onSave, onCancel }) {
  const [transcription, setTranscription] = useState(job.transcription);
  const [timeline, setTimeline] = useState(job.speaker_turns);
  
  const handleTextEdit = (index, newText) => {
    // Actualizar texto
    const updated = [...timeline];
    updated[index].text = newText;
    setTimeline(updated);
  };
  
  const handleSpeakerChange = (index, newSpeaker) => {
    // Cambiar speaker
    const updated = [...timeline];
    updated[index].speaker = newSpeaker;
    setTimeline(updated);
  };
  
  const markAsPunchline = (index) => {
    // Marcar intervención como punchline
  };
  
  const handleSave = async () => {
    const res = await fetch(`/api/transcription/${job.id}/review`, {
      method: 'POST',
      body: JSON.stringify({
        edits: calculateEdits(job.transcription, transcription),
        timeline: timeline
      })
    });
    
    onSave(res.json());
  };
  
  return (
    <div className="editor">
      <div className="timeline">
        {timeline.map((turn, i) => (
          <TranscriptionTurn
            key={i}
            turn={turn}
            onTextEdit={(t) => handleTextEdit(i, t)}
            onSpeakerChange={(s) => handleSpeakerChange(i, s)}
            onMarkPunchline={() => markAsPunchline(i)}
          />
        ))}
      </div>
      
      <button onClick={handleSave}>Guardar Cambios</button>
      <button onClick={onCancel}>Cancelar</button>
    </div>
  );
}
```

### 8.2 Backend para Review (review_backend.py)

```python
@app.get("/api/transcription/pending")
async def get_pending_transcriptions(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Transcripciones pendientes de review para este usuario"""
    jobs = db.query(TranscriptionJob).filter(
        TranscriptionJob.status == "PENDING_MANUAL_REVIEW"
    ).order_by(TranscriptionJob.created_at).limit(20).all()
    
    return jobs

@app.post("/api/transcription/{transcription_id}/review")
async def submit_review(
    transcription_id: int,
    edits: dict,
    timeline: list,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Guardar cambios de una transcripción"""
    
    # Guardar cada edit
    for edit in edits['changes']:
        db.add(TranscriptionEdit(
            transcription_id=transcription_id,
            edited_by=current_user.id,
            before=edit['before'],
            after=edit['after'],
            edit_type=edit['type']
        ))
    
    # Actualizar transcription
    transcription = db.query(Transcription).get(transcription_id)
    transcription.structured_data = timeline
    transcription.is_manual_review_complete = True
    transcription.manual_review_completed_at = datetime.utcnow()
    
    db.commit()
    
    # Trigger: Re-indexar para búsqueda
    # (Etapa 3: embeddings)
    
    return {"status": "review_completed", "transcription_id": transcription_id}
```

---

## 9. Configuración Docker-Compose

```yaml
version: '3.8'

services:
  
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: redbull_batalla
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
  
  fastapi:
    build: .
    depends_on:
      - postgres
      - redis
    environment:
      DATABASE_URI: postgresql://user:pass@postgres:5432/redbull_batalla
      REDIS_URL: redis://redis:6379/0
      DEEPSEEK_API_KEY: ${DEEPSEEK_API_KEY}
      OPENAI_API_KEY: ${OPENAI_API_KEY}
    ports:
      - "8000:8000"
    volumes:
      - ./:/app
      - /tmp/videos:/tmp/videos
  
  celery_worker:
    build: .
    command: celery -A workers.celery_app worker -l info -c 2
    depends_on:
      - redis
      - postgres
    environment:
      DATABASE_URI: postgresql://user:pass@postgres:5432/redbull_batalla
      REDIS_URL: redis://redis:6379/0
    volumes:
      - /tmp/videos:/tmp/videos
  
  celery_flower:
    build: .
    command: celery -A workers.celery_app flower
    ports:
      - "5555:5555"
    depends_on:
      - redis

volumes:
  postgres_data:
```

---

## 10. Arquitectura de Estabilidad

### 10.1 Error Handling

```python
# En celery task
try:
    # Process
except YouTubeVideoNotFound:
    status = "FAILED_VIDEO_NOT_FOUND"
    await notify_user("El video no está disponible")
except AudioExtractionFailed:
    status = "FAILED_AUDIO_EXTRACTION"
    # Auto-retry
    self.retry(countdown=30, max_retries=3)
except TranscriptionTimeout:
    status = "FAILED_TRANSCRIPTION_TIMEOUT"
    # Usar fallback (Deepgram)
except Exception as e:
    status = "FAILED_UNKNOWN"
    # Notify Sentry
    sentry.capture_exception(e)
    await notify_admin(f"Error crítico en job {job_id}: {e}")
```

### 10.2 Resilencia

- ✅ **Retry automático**: 3 intentos con backoff exponencial
- ✅ **Fallback services**: Whisper → Deepgram (transcripción)
- ✅ **Checkpoint restoration**: Si worker muere, reinicia desde último checkpoint
- ✅ **Client reconnect**: WebSocket se reconecta automáticamente
- ✅ **Job persistence**: Redis + PostgreSQL para datos
- ✅ **Dead Letter Queue**: Jobs que fallan 3 veces se envían a DLQ para revisión manual

---

## 11. Métricas de Éxito

```
Étapa 2 - Transcripciones:

✅ Accuracy: 95%+ (en español, condiciones normales)
✅ Speed: 15 min promedio para batalla de 10-15 min
✅ Speaker Accuracy: 90%+
✅ Manual Review Time: <2 min por barra (optimizado)
✅ Parallelism: 23 reviewers simultáneamente sin bottleneck
✅ Uptime: 99.5%+
✅ Auto-recovery: 100% de jobs recuperables en caso de fallo
```

---

## 12. Dependencias Nuevas

```
# requirements-transcription.txt
yt-dlp==2024.4.9
pydub==0.25.1
openai==1.14.0
deepgram-sdk==3.2.0
pyannote.audio==3.0.1
celery==5.4.0
redis==5.0.1
websockets==12.0
python-socketio==5.10.0
```

---

## 13. Resumen de Implementación Etapa 2

```
Sprint 1 (Semanas 1-2): Video Download + Audio Extraction
  - youtube_downloader.py
  - audio_extractor.py
  - video_validator.py

Sprint 2 (Semanas 2-3): Transcription Engine
  - whisper_wrapper.py
  - deepgram_wrapper.py
  - transcription_service.py

Sprint 3 (Semanas 3-4): Diarization + Mapping
  - diarization_service.py
  - speaker_embedding.py
  - speaker_mapper.py

Sprint 4 (Semanas 4-5): Celery + WebSocket
  - celery_app.py
  - transcription_worker.py
  - websocket_manager.py
  - Web API endpoints
  - Frontend (React)

Sprint 5 (Semanas 5-6): Manual Review Dashboard
  - review_dashboard.py
  - reviewer_interface.html
  - Edit tracking + versioning
  - RBAC (Role-based access control)

Sprint 6 (Semana 6): Testing + Deployment
  - Load testing
  - Integration tests
  - Performance tuning
  - Docker-compose setup
  - Documentation

Total: 6 semanas
Code: ~5,000-7,000 líneas nuevas
Equipo: 2 devs backend + 1 ml engineer + 1 frontend dev
```

Este es el roadmap detallado para Etapa 2. ¿Comenzamos?
