"""
GUÍA COMPLETA: Tool Loop + Endpoints de Chat
Explicación exhaustiva de cómo funciona el sistema
"""

# ═══════════════════════════════════════════════════════════════════════════════
# PARTE 1: ENTENDER EL TOOL LOOP
# ═══════════════════════════════════════════════════════════════════════════════

"""
EL TOOL LOOP ES UN CICLO DE INTELIGENCIA ARTIFICIAL QUE:

1. Recibe pregunta del usuario
2. Entiende la intención (intent detection)
3. Extrae entidades (nombres, años, países)
4. Valida ambigüedades
5. Ejecuta herramientas correctas
6. Genera respuesta natural

Ejemplo Real:

Usuario pregunta:
    "¿Cómo le fue a Dani en España?"

Tool Loop ejecuta:
    ├─ PASO 1: Extraer Intención
    │  └─ Tipo: "statistics" (pregunta sobre estadísticas)
    │
    ├─ PASO 2: Extraer Entidades
    │  ├─ MC: "Dani"
    │  └─ País: "spain"
    │
    ├─ PASO 3: Buscar MC "Dani"
    │  ├─ search_person("Dani")
    │  └─ Resultado: [{id: 1, aka: "Dani", country: "spain"}]
    │
    ├─ PASO 4: Validar Ambigüedad
    │  ├─ ¿Hay múltiples "Dani"?
    │  └─ No → Continuar
    │
    ├─ PASO 5: Ejecutar Herramientas
    │  ├─ Tool 1: get_person_statistics(person_id=1)
    │  │  └─ Retorna: {wins: 24, losses: 6, win_rate: 80%}
    │  │
    │  └─ Tool 2: get_battles_by_person(person_id=1)
    │     └─ Retorna: [batalla1, batalla2, ...]
    │
    └─ PASO 6: Generar Respuesta Natural
       └─ "Dani tiene un 80% de win rate en España con 24 victorias
          en 30 batallas..."
"""

# ═══════════════════════════════════════════════════════════════════════════════
# PARTE 2: EL CÓDIGO DEL TOOL LOOP (agents.py)
# ═══════════════════════════════════════════════════════════════════════════════

"""
En agents.py, el tool loop funciona así:

class BatallaAgent:
    def process_query(self, user_query: str) -> Dict[str, Any]:
        '''
        PASO 1: EXTRAER INTENCIÓN
        '''
        intent = self._extract_intent(user_query)
        # Retorna: {type: "statistics", confidence: 0.90}
        
        '''
        PASO 2: EJECUTAR TOOL LOOP SEGÚN INTENCIÓN
        '''
        match intent["type"]:
            case "head_to_head":
                # Si pregunta "Dani vs Chuty"
                tool_calls, data = self._handle_head_to_head(query)
                # Ejecuta: search_person(Dani) + search_person(Chuty) + get_h2h()
                
            case "statistics":
                # Si pregunta sobre estadísticas
                tool_calls, data = self._handle_statistics(query)
                # Ejecuta: search_person() + get_person_statistics()
                
            case "ranking":
                # Si pregunta "top 10"
                tool_calls, data = self._handle_ranking(query)
                # Ejecuta: get_top_performers()
        
        '''
        PASO 3: GENERAR RESPUESTA NATURAL
        '''
        final_answer = self._generate_response(query, data, intent)
        # LLM convierte datos en texto natural
        
        '''
        PASO 4: RETORNAR RESULTADO
        '''
        return {
            "query": query,
            "intent": intent,
            "tool_calls": tool_calls,
            "final_answer": final_answer
        }
"""

# ═══════════════════════════════════════════════════════════════════════════════
# PARTE 3: ENDPOINTS EXPLICADOS (Por qué hay tantos)
# ═══════════════════════════════════════════════════════════════════════════════

"""
HAY MUCHOS ENDPOINTS PORQUE CADA UNO SIRVE UN CASO DE USO DIFERENTE.

Piensa en una tienda: no tienes 1 solo mostrador, tienes:
- Mostrador de caja (pagar)
- Mostrador de devoluciones
- Mostrador de preguntas
- Etc.

En nuestra API es lo mismo. Cada endpoint es una "ruta" específica:

═══════════════════════════════════════════════════════════════════════════════
1. ENDPOINTS DE CHAT/QUERY (Para preguntas inteligentes)
═══════════════════════════════════════════════════════════════════════════════

POST /api/query
    ├─ Usa: Tool Loop (agents.py)
    ├─ Entrada: {"query": "¿Cómo le fue a Dani?"}
    ├─ Salida: {status, answer, intent, tools_used}
    ├─ Velocidad: ~2-5 segundos (depende de LLM)
    ├─ Respuesta: JSON completo
    └─ Uso: Cuando necesitas respuesta completa de una vez

POST /api/query/stream
    ├─ Usa: Tool Loop + SSE (Server-Sent Events)
    ├─ Entrada: {"query": "¿Cómo le fue a Dani?"}
    ├─ Salida: Stream de eventos:
    │  ├─ event: "progress" → stage: "ANALYZING"
    │  ├─ event: "progress" → stage: "TOOLS_EXECUTED"
    │  ├─ event: "answer_chunk" → token: "Dani"
    │  ├─ event: "answer_chunk" → token: " tiene"
    │  └─ event: "final_result" → {complete_answer}
    ├─ Velocidad: Streaming en tiempo real
    ├─ Respuesta: Stream de eventos
    └─ Uso: Cuando necesitas ver progreso paso a paso (RECOMENDADO PARA CHAT)

POST /api/chat
    ├─ Usa: Tool Loop + historial de mensajes
    ├─ Entrada: {messages: [{role: "user", content: "¿Dani?"}]}
    ├─ Salida: {status, assistant_message, metadata}
    ├─ Velocidad: ~2-5 segundos
    ├─ Respuesta: JSON con respuesta del asistente
    └─ Uso: Cuando tienes múltiples turnos de conversación

═══════════════════════════════════════════════════════════════════════════════
2. ENDPOINTS DE BÚSQUEDA DIRECTA (Sin tool loop, búsqueda rápida)
═══════════════════════════════════════════════════════════════════════════════

GET /api/search/persons?q=Dani
    ├─ Usa: Búsqueda fuzzy directa (sin LLM)
    ├─ Entrada: Query string
    ├─ Salida: [{id, aka, country, style}]
    ├─ Velocidad: <100ms
    └─ Uso: Autocomplete, búsqueda rápida

GET /api/search/events?q=España
    ├─ Usa: Búsqueda fuzzy de eventos
    ├─ Salida: [{id, name, year, country}]
    ├─ Velocidad: <100ms
    └─ Uso: Búsqueda de eventos

═══════════════════════════════════════════════════════════════════════════════
3. ENDPOINTS DE DATOS ESPECÍFICOS (Acceso directo sin IA)
═══════════════════════════════════════════════════════════════════════════════

GET /api/person/{id}/stats
    ├─ Retorna: Estadísticas completas de un MC
    ├─ Velocidad: <50ms (caché)
    └─ Uso: Cuando YA SABES el ID del MC

GET /api/battle/{id}
    ├─ Retorna: Detalles completos de batalla
    ├─ Velocidad: <50ms
    └─ Uso: Detalles específicos

GET /api/h2h/{id1}/{id2}
    ├─ Retorna: Head-to-head entre dos MCs
    ├─ Velocidad: <50ms
    └─ Uso: Comparativa directa

═══════════════════════════════════════════════════════════════════════════════
4. ENDPOINTS DE RANKINGS (Datos calculados previamente)
═══════════════════════════════════════════════════════════════════════════════

GET /api/rankings/top-performers?country=spain&limit=10
    ├─ Retorna: Top 10 MCs por win rate
    ├─ Velocidad: <50ms
    └─ Uso: Página de rankings

GET /api/rankings/by-style?style=punchline
    ├─ Retorna: MCs especializados en estilo
    ├─ Velocidad: <50ms
    └─ Uso: Filtrar por estilo

═══════════════════════════════════════════════════════════════════════════════
5. ENDPOINTS DE EVENTOS (Información de torneos)
═══════════════════════════════════════════════════════════════════════════════

GET /api/events?year=2023
    ├─ Retorna: Todos los eventos de un año
    ├─ Velocidad: <50ms
    └─ Uso: Listar eventos

GET /api/event/{id}
    ├─ Retorna: Detalles completos del evento
    ├─ Velocidad: <50ms
    └─ Uso: Página de evento

═══════════════════════════════════════════════════════════════════════════════
6. ENDPOINTS DE ADMINISTRACIÓN (Para llenar datos)
═══════════════════════════════════════════════════════════════════════════════

POST /api/ingest/person
    ├─ Crea nueva persona
    └─ Uso: Admin panel

POST /api/ingest/event
    ├─ Crea nuevo evento
    └─ Uso: Admin panel

═══════════════════════════════════════════════════════════════════════════════
"""

# ═══════════════════════════════════════════════════════════════════════════════
# PARTE 4: CUÁL USAR PARA TU CHAT
# ═══════════════════════════════════════════════════════════════════════════════

"""
PARA UN CHAT EN FRONTEND, DEBES USAR:

    POST /api/query/stream

¿Por qué?

1. MUESTRA PROGRESO EN TIEMPO REAL
   └─ Usuario ve que el sistema está pensando

2. STREAMING DE RESPUESTA
   └─ Las palabras aparecen mientras el LLM genera

3. MEJOR UX
   └─ No espera 5 segundos en pantalla en blanco

FLUJO COMPLETO DEL CHAT:

Cliente (Frontend React/Vue)
    ↓
Usuario escribe: "¿Cómo le fue a Dani en España?"
    ↓
Cliquea ENVIAR
    ↓
Frontend POST /api/query/stream
    {
        "query": "¿Cómo le fue a Dani en España?"
    }
    ↓
FastAPI Backend abre evento stream (SSE)
    ↓
Backend INICIA Tool Loop:
    ├─ Extrae intención: "statistics"
    ├─ Extrae entidades: MC="Dani", País="Spain"
    ├─ Frontend RECIBE: {type: "progress", stage: "ANALYZING"}
    │
    ├─ Busca MC: search_person("Dani")
    ├─ Obtiene estadísticas: get_person_statistics(id=1)
    ├─ Frontend RECIBE: {type: "progress", stage: "TOOLS_EXECUTED"}
    │
    ├─ LLM genera respuesta
    ├─ Frontend RECIBE: {type: "answer_chunk", chunk: "Dani"}
    ├─ Frontend RECIBE: {type: "answer_chunk", chunk: " tiene"}
    ├─ Frontend RECIBE: {type: "answer_chunk", chunk: " un 80%..."}
    │
    └─ Completo
       └─ Frontend RECIBE: {type: "final_result", ...}

Frontend muestra:
    ├─ [Escribiendo...] (mientras ANALYZING)
    ├─ [Ejecutando herramientas...] (mientras TOOLS_EXECUTED)
    ├─ Dani tiene un 80%... (streaming de texto)
    └─ [Mensaje completo] (cuando final_result)
"""

# ═══════════════════════════════════════════════════════════════════════════════
# PARTE 5: CÓDIGO FRONTEND (CÓMO CONECTARSE)
# ═══════════════════════════════════════════════════════════════════════════════

"""
OPCIÓN 1: Usando EventSource (SSE nativo del navegador)

// ChatComponent.jsx

export default function ChatComponent() {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState("");
    const [isLoading, setIsLoading] = useState(false);

    const handleSend = async (e) => {
        e.preventDefault();
        
        // Agregar mensaje del usuario al chat
        setMessages(prev => [...prev, {
            role: "user",
            content: input
        }]);
        
        setInput("");
        setIsLoading(true);
        let assistantMessage = "";

        try {
            // CONECTAR A /api/query/stream
            const response = await fetch("http://localhost:8000/api/query/stream", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    query: input
                })
            });

            // EventSource para SSE
            const reader = response.body.getReader();
            const decoder = new TextDecoder();

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const text = decoder.decode(value);
                const lines = text.split("\\n\\n");

                for (const line of lines) {
                    if (line.startsWith("data: ")) {
                        const jsonStr = line.slice(6);
                        const event = JSON.parse(jsonStr);

                        // PROCESAR EVENTOS
                        if (event.type === "progress") {
                            // Mostrar: "Analizando...", "Ejecutando herramientas..."
                            console.log(`[${event.stage}] ${event.message}`);
                        }
                        else if (event.type === "answer_chunk") {
                            // Agregar chunk a respuesta
                            assistantMessage += event.chunk;
                            
                            // Actualizar UI en tiempo real
                            setMessages(prev => {
                                const updated = [...prev];
                                if (updated[updated.length - 1]?.role === "assistant") {
                                    updated[updated.length - 1].content = assistantMessage;
                                } else {
                                    updated.push({
                                        role: "assistant",
                                        content: assistantMessage
                                    });
                                }
                                return updated;
                            });
                        }
                        else if (event.type === "final_result") {
                            // Procesar resultado final si necesario
                            console.log("Query completada:", event);
                        }
                    }
                }
            }
        } catch (error) {
            console.error("Error:", error);
            setMessages(prev => [...prev, {
                role: "assistant",
                content: "Error al procesar la consulta"
            }]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="chat-container">
            <div className="messages">
                {messages.map((msg, i) => (
                    <div key={i} className={`message ${msg.role}`}>
                        {msg.content}
                    </div>
                ))}
            </div>

            <form onSubmit={handleSend}>
                <input
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Pregunta sobre Red Bull Batalla..."
                    disabled={isLoading}
                />
                <button type="submit" disabled={isLoading}>
                    {isLoading ? "Pensando..." : "Enviar"}
                </button>
            </form>
        </div>
    );
}
"""

# ═══════════════════════════════════════════════════════════════════════════════
# PARTE 6: COMPARATIVA DE ENDPOINTS PARA CHAT
# ═══════════════════════════════════════════════════════════════════════════════

"""
¿CUÁL ENDPOINT USAR SEGÚN TU CASO?

┌─────────────────────────────────────────────────────────────────────┐
│ CASO 1: Chat simple, usuario pregunta 1 cosa                        │
├─────────────────────────────────────────────────────────────────────┤
│ Usa: POST /api/query/stream                                         │
│ Ventaja: Muestra progreso, streaming de respuesta                   │
│ Desventaja: Ninguna (recomendado)                                   │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ CASO 2: Chat multi-turno con contexto                              │
├─────────────────────────────────────────────────────────────────────┤
│ Usa: POST /api/chat                                                │
│ Estructura: {messages: [{role: "user", content: "..."}, ...]}     │
│ Ventaja: Mantiene contexto de conversación                         │
│ Desventaja: No streaming (recibe respuesta completa)               │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ CASO 3: Búsqueda rápida para autocomplete                          │
├─────────────────────────────────────────────────────────────────────┤
│ Usa: GET /api/search/persons?q=Dani                                │
│ Ventaja: Muy rápido (<100ms), perfecto para autocomplete           │
│ Desventaja: No es IA, solo búsqueda fuzzy                          │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ CASO 4: Página de detalles de MC (ya sabes su ID)                 │
├─────────────────────────────────────────────────────────────────────┤
│ Usa: GET /api/person/{id}/stats                                    │
│ Ventaja: Muy rápido (<50ms), datos pre-calculados                  │
│ Desventaja: Necesitas saber el ID                                  │
└─────────────────────────────────────────────────────────────────────┘

RECOMENDACIÓN FINAL PARA CHAT:
    ➜ POST /api/query/stream

Porque:
    ✅ Muestra progreso al usuario (UX)
    ✅ Streaming de respuesta (no espera)
    ✅ Usa tool loop (respuestas inteligentes)
    ✅ Maneja ambigüedades automáticamente
"""

# ═══════════════════════════════════════════════════════════════════════════════
# PARTE 7: DIAGRAMA VISUAL DEL FLUJO
# ═══════════════════════════════════════════════════════════════════════════════

"""
FLUJO COMPLETO DE UNA PREGUNTA EN CHAT:

USUARIO (Frontend)
    │
    └─ "¿Cómo le fue a Dani en España?"
            │
            ↓
    POST /api/query/stream
            │
            ↓
BACKEND (FastAPI + BatallaAgent)
            │
            ├─ [1] _extract_intent()
            │      └─ Tipo: "statistics"
            │
            ├─ [2] _handle_statistics()
            │      ├─ search_person("Dani")
            │      ├─ [EVENTO: progress → ANALYZING]
            │      └─ get_person_statistics()
            │
            ├─ [3] _generate_response()
            │      ├─ [EVENTO: progress → TOOLS_EXECUTED]
            │      └─ LLM crea respuesta
            │
            └─ [4] Stream response
                   ├─ [EVENTO: answer_chunk → "Dani"]
                   ├─ [EVENTO: answer_chunk → " tiene"]
                   ├─ [EVENTO: answer_chunk → " un 80%"]
                   └─ [EVENTO: final_result → {...}]
                        │
                        ↓
                   USUARIO VE:
                   ┌─────────────────────────────┐
                   │ Analizando...               │
                   │ [mostrador de progreso]     │
                   └─────────────────────────────┘
                        │
                        ↓ (después 2-3 seg)
                   ┌─────────────────────────────┐
                   │ Ejecutando herramientas...  │
                   │ [mostrador de progreso]     │
                   └─────────────────────────────┘
                        │
                        ↓ (después 1-2 seg)
                   ┌─────────────────────────────┐
                   │ Dani tiene un 80% de win... │
                   │ [texto streaming]           │
                   └─────────────────────────────┘
                        │
                        ↓ (después 3-5 seg TOTAL)
                   ┌─────────────────────────────┐
                   │ Dani tiene un 80% de win    │
                   │ rate con 24 victorias en    │
                   │ 30 batallas. Dominó en      │
                   │ cuartos de final...         │
                   │ [mensaje completo]         │
                   └─────────────────────────────┘
"""

# ═══════════════════════════════════════════════════════════════════════════════
# PARTE 8: CÓDIGO MÍNIMO PARA ENTENDER
# ═══════════════════════════════════════════════════════════════════════════════

"""
CÓDIGO MÍNIMO EN TU FRONTEND (React):

import { useState } from 'react';

export default function Chat() {
    const [messages, setMessages] = useState([]);
    
    const sendMessage = async (query) => {
        // Mostrar pregunta del usuario
        setMessages(m => [...m, { role: 'user', content: query }]);
        
        // Conectar a stream
        const res = await fetch('http://localhost:8000/api/query/stream', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query })
        });
        
        // Leer stream
        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        let assistantMsg = '';
        
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            const text = decoder.decode(value);
            const lines = text.split('\\n\\n');
            
            for (const line of lines) {
                if (!line.startsWith('data: ')) continue;
                
                const event = JSON.parse(line.slice(6));
                
                if (event.type === 'answer_chunk') {
                    // Ir agregando chunks
                    assistantMsg += event.chunk;
                    setMessages(m => {
                        const updated = [...m];
                        if (updated[updated.length-1]?.role === 'assistant') {
                            updated[updated.length-1].content = assistantMsg;
                        } else {
                            updated.push({ role: 'assistant', content: assistantMsg });
                        }
                        return updated;
                    });
                }
            }
        }
    };
    
    return (
        <div>
            {messages.map((m, i) => (
                <div key={i} className={m.role}>
                    {m.content}
                </div>
            ))}
            <input 
                onKeyPress={(e) => e.key === 'Enter' && sendMessage(e.target.value)}
                placeholder="Pregunta..."
            />
        </div>
    );
}
"""

print("""
════════════════════════════════════════════════════════════════════════════════
RESUMEN FINAL
════════════════════════════════════════════════════════════════════════════════

✅ TOOL LOOP: Ciclo de IA que entiende, extrae, ejecuta herramientas, responde

✅ ENDPOINT PRINCIPAL: POST /api/query/stream

✅ ¿POR QUÉ TANTOS ENDPOINTS?
   • Cada uno optimizado para un caso de uso específico
   • Algunos rápidos (búsqueda)
   • Otros inteligentes (chat con IA)
   • Otros para admin (ingerir datos)

✅ PARA TU CHAT NECESITAS:
   1. Frontend → POST /api/query/stream
   2. Backend responde con SSE (Server-Sent Events)
   3. Frontend recibe eventos de progreso + chunks de respuesta
   4. Usuario ve respuesta streaming en tiempo real

✅ VELOCIDAD TÍPICA:
   • Análisis: 1-2 seg
   • Ejecución de herramientas: 1-2 seg
   • Generación de respuesta: 2-3 seg
   • TOTAL: 4-7 segundos

✅ PRÓXIMO PASO: Conectar tu frontend React/Vue a /api/query/stream
════════════════════════════════════════════════════════════════════════════════
""")
