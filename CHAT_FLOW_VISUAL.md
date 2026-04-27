# FLUJO VISUAL DE UNA CONSULTA EN CHAT

## Escenario Real: Usuario pregunta en tu chat frontend

### PASO 0: Usuario escribe y envía

```
┌─────────────────────────────────┐
│ Red Bull Batalla Chat           │
├─────────────────────────────────┤
│                                 │
│                                 │
│ ┌──────────────────────────────┐│
│ │ ¿Cómo le fue a Dani en      ││
│ │ España el último año?        ││
│ └──────────────────────────────┘│
│                          [ENVIAR]│
└─────────────────────────────────┘
```

---

## PASO 1: Frontend conecta a /api/query/stream

```javascript
// El frontend hace esto
POST http://localhost:8000/api/query/stream
Content-Type: application/json

{
    "query": "¿Cómo le fue a Dani en España el último año?"
}
```

**Backend recibe la pregunta y comienza el TOOL LOOP**

---

## PASO 2: Backend extrae intención

```
BatallaAgent comienza:

┌─────────────────────────────────────────────────────┐
│ PASO 1: _extract_intent()                           │
├─────────────────────────────────────────────────────┤
│                                                     │
│ Entrada: "¿Cómo le fue a Dani en España?"          │
│                                                     │
│ Análisis:                                           │
│  • Contiene "cómo le fue" → statistics              │
│  • Contiene "Dani" → MC name                        │
│  • Contiene "España" → country filter               │
│                                                     │
│ Salida:                                             │
│ {                                                   │
│   "type": "statistics",                             │
│   "confidence": 0.95,                               │
│   "entities": {                                     │
│     "names": ["Dani"],                              │
│     "countries": ["spain"],                         │
│     "years": [2025]                                 │
│   }                                                 │
│ }                                                   │
│                                                     │
│ ✅ Intención detectada: STATISTICS                 │
└─────────────────────────────────────────────────────┘

BACKEND EMITE EVENTO:
"""
event: progress
data: {
    "type": "progress",
    "stage": "ANALYZING",
    "progress": 10,
    "message": "Analizando pregunta..."
}
"""
```

**Frontend recibe este evento:**

```
┌─────────────────────────────────┐
│ Red Bull Batalla Chat           │
├─────────────────────────────────┤
│                                 │
│ Usuario: ¿Cómo le fue a Dani... │
│                                 │
│ Bot: Analizando pregunta...      │ ← Aparece aquí
│                                 │
└─────────────────────────────────┘
```

---

## PASO 3: Backend ejecuta tool loop

```
┌─────────────────────────────────────────────────────┐
│ PASO 2: _handle_statistics(query)                   │
├─────────────────────────────────────────────────────┤
│                                                     │
│ Llama a herramientas (tools):                       │
│                                                     │
│ [TOOL 1] search_person("Dani")                      │
│          ↓ Busca MCs con nombre similar             │
│          → Resultado: [{id: 1, aka: "Dani",        │
│                        country: "spain"}]           │
│                                                     │
│ [TOOL 2] get_person_statistics(person_id=1)        │
│          ↓ Obtiene stats del MC                     │
│          → Resultado: {                             │
│              total_battles: 30,                      │
│              wins: 24,                               │
│              win_rate: 80%,                          │
│              current_streak: 5,                      │
│              ...                                     │
│            }                                         │
│                                                     │
│ [TOOL 3] get_battles_by_person(person_id=1)        │
│          ↓ Obtiene batallas recientes               │
│          → Resultado: [batalla1, batalla2, ...]    │
│                                                     │
│ ✅ Herramientas ejecutadas                         │
└─────────────────────────────────────────────────────┘

BACKEND EMITE EVENTO:
"""
event: progress
data: {
    "type": "progress",
    "stage": "TOOLS_EXECUTED",
    "progress": 50,
    "message": "Se ejecutaron 3 herramientas"
}
"""
```

**Frontend recibe este evento:**

```
┌─────────────────────────────────┐
│ Red Bull Batalla Chat           │
├─────────────────────────────────┤
│                                 │
│ Usuario: ¿Cómo le fue a Dani... │
│                                 │
│ Bot: Analizando pregunta...      │
│     Se ejecutaron 3 herramientas │ ← Actualiza aquí
│                                 │
└─────────────────────────────────┘
```

---

## PASO 4: Backend genera respuesta (streaming)

```
┌─────────────────────────────────────────────────────┐
│ PASO 3: _generate_response()                        │
├─────────────────────────────────────────────────────┤
│                                                     │
│ Usa LLM (DeepSeek) para generar respuesta natural:  │
│                                                     │
│ Entrada del LLM:                                    │
│  - Query: "¿Cómo le fue a Dani en España?"         │
│  - Datos: {wins: 24, losses: 6, streak: 5, ...}   │
│  - Intent: "statistics"                             │
│                                                     │
│ LLM genera TOKEN POR TOKEN:                         │
│  1. "Dani"                                          │
│  2. " tiene"                                        │
│  3. " un"                                           │
│  4. " 80%"                                          │
│  5. " de"                                           │
│  6. " win"                                          │
│  7. " rate"                                         │
│  8. " en"                                           │
│  9. " España"                                       │
│  10. " con"                                         │
│  ...                                                │
│                                                     │
└─────────────────────────────────────────────────────┘

BACKEND EMITE EVENTOS (STREAMING):
"""
event: answer_chunk
data: {
    "type": "answer_chunk",
    "chunk": "Dani"
}
"""

"""
event: answer_chunk
data: {
    "type": "answer_chunk",
    "chunk": " tiene"
}
"""

"""
event: answer_chunk
data: {
    "type": "answer_chunk",
    "chunk": " un"
}
"""

... (más chunks)

"""
event: answer_chunk
data: {
    "type": "answer_chunk",
    "chunk": " de España."
}
"""
```

**Frontend recibe chunks y los muestra EN TIEMPO REAL:**

```
SEGUNDO 0.5:
┌─────────────────────────────────┐
│ Red Bull Batalla Chat           │
├─────────────────────────────────┤
│ Usuario: ¿Cómo le fue a Dani... │
│ Bot: Dani▌                       │
└─────────────────────────────────┘

SEGUNDO 1.0:
┌─────────────────────────────────┐
│ Red Bull Batalla Chat           │
├─────────────────────────────────┤
│ Usuario: ¿Cómo le fue a Dani... │
│ Bot: Dani tiene▌                │
└─────────────────────────────────┘

SEGUNDO 1.5:
┌─────────────────────────────────┐
│ Red Bull Batalla Chat           │
├─────────────────────────────────┤
│ Usuario: ¿Cómo le fue a Dani... │
│ Bot: Dani tiene un▌             │
└─────────────────────────────────┘

SEGUNDO 2.0:
┌─────────────────────────────────┐
│ Red Bull Batalla Chat           │
├─────────────────────────────────┤
│ Usuario: ¿Cómo le fue a Dani... │
│ Bot: Dani tiene un 80%▌         │
└─────────────────────────────────┘

SEGUNDO 5.0:
┌─────────────────────────────────────┐
│ Red Bull Batalla Chat               │
├─────────────────────────────────────┤
│ Usuario: ¿Cómo le fue a Dani...    │
│                                     │
│ Bot: Dani tiene un 80% de win      │
│     rate en España con 24 victorias │
│     en 30 batallas. Dominó en      │
│     cuartos de final con una racha  │
│     actual de 5 victorias seguidas. │
│     Ha evolucionado mucho desde...  │
│                                     │
│                              [▼]    │
└─────────────────────────────────────┘
```

---

## PASO 5: Backend completa (final_result)

```
BACKEND EMITE EVENTO FINAL:
"""
event: final_result
data: {
    "type": "final_result",
    "job_id": "550e8400-e29b...",
    "status": "complete",
    "query": "¿Cómo le fue a Dani en España?",
    "intent": {
        "type": "statistics",
        "confidence": 0.95
    },
    "tools_used": [
        "search_person",
        "get_person_statistics",
        "get_battles_by_person"
    ],
    "answer": "Dani tiene un 80% de win rate... [respuesta completa]"
}
"""
```

**Frontend finaliza:**

```
┌───────────────────────────────────────┐
│ Red Bull Batalla Chat                 │
├───────────────────────────────────────┤
│ Usuario: ¿Cómo le fue a Dani...      │
│                                       │
│ Bot: Dani tiene un 80% de win        │
│     rate en España con 24 victorias   │
│     en 30 batallas. Dominó en        │
│     cuartos de final con una racha    │
│     actual de 5 victorias seguidas.   │
│     Ha evolucionado mucho desde...    │
│                                       │
│ [Usuario puede escribir nueva pregunta]
│ ┌─────────────────────────────────┐ │
│ │ Pregunta siguiente...          │ │
│ └─────────────────────────────────┘ │
└───────────────────────────────────────┘
```

---

## TIMELINE COMPLETO

```
00:00 - Usuario cliquea ENVIAR
        └─ Frontend → POST /api/query/stream

00.5s - Evento: ANALYZING (10%)
        └─ Frontend muestra: "Analizando pregunta..."

01.5s - Evento: TOOLS_EXECUTED (50%)
        └─ Frontend muestra: "Se ejecutaron 3 herramientas"

02.0s - Primeros chunks de respuesta
        └─ Frontend muestra: "Dani tiene un 80%..."

02-05s - Streaming continuo de chunks
         └─ Frontend actualiza respuesta en tiempo real
            • "Dani tiene un 80% de win rate..."
            • "...con 24 victorias en 30 batallas..."
            • "...dominó en cuartos de final..."

05.0s - Evento: COMPLETE (100%)
        └─ Frontend marca mensaje como completo
           Usuario puede escribir nueva pregunta
```

---

## COMPARACIÓN CON OTROS ENDPOINTS

### POST /api/query (SIN STREAM)

```
00:00 - Usuario envía pregunta
05:00 - Backend procesa (usuario ve: "Cargando...")
05:00 - Backend retorna RESPUESTA COMPLETA
        └─ Esperar 5 segundos sin feedback

Problema: El usuario no sabe qué está pasando
          Mala experiencia de usuario
```

### POST /api/chat (CON HISTORIAL)

```
Entrada:
{
    "messages": [
        {role: "user", content: "¿Dani vs Chuty?"},
        {role: "assistant", content: "Dani ganó 7-3..."},
        {role: "user", content: "¿Y en 2023?"}
    ]
}

Salida: Respuesta que considera contexto anterior
        Pero SIN STREAMING (espera 5 segundos)
```

### GET /api/search/persons (SIN IA)

```
00:00 - Usuario escribe "Dan" (autocomplete)
00.01 - GET /api/search/persons?q=Dan
00.02 - Retorna: [{id: 1, aka: "Dani"}, ...]

Ventaja: Muy rápido, perfecto para autocomplete
Desventaja: No es IA, solo búsqueda fuzzy
```

---

## RESUMEN

| Aspecto | POST /api/query/stream | POST /api/query | POST /api/chat |
|--------|----------------------|-----------------|----------------|
| **IA** | ✅ Sí | ✅ Sí | ✅ Sí |
| **Streaming** | ✅ Sí | ❌ No | ❌ No |
| **Progreso visible** | ✅ Sí | ❌ No | ❌ No |
| **Velocidad percibida** | ✅ Rápida (usuarios ven progreso) | ❌ Lenta (espera 5s) | ❌ Lenta (espera 5s) |
| **Contexto previo** | ❌ No | ❌ No | ✅ Sí |
| **Para chat** | ✅ MEJOR | ⚠️ OK | ✅ Si es multi-turno |

**➜ PARA TU CHAT: Usa POST /api/query/stream**
