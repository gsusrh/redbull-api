/**
 * Chat Frontend Template - Red Bull Batalla
 *
 * Componente React listo para usar con /api/query/stream
 * Muestra progreso en tiempo real y streaming de respuesta
 *
 * Uso:
 *  <ChatComponent apiUrl="http://localhost:8000" />
 */

import React, { useState, useRef, useEffect } from 'react';
import './ChatComponent.css'; // Estilos al final

export default function ChatComponent({ apiUrl = "http://localhost:8000" }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [currentProgress, setCurrentProgress] = useState(null);
  const messagesEndRef = useRef(null);

  // Auto-scroll al final cuando hay nuevos mensajes
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async (e) => {
    e.preventDefault();

    if (!input.trim()) return;

    // Agregar mensaje del usuario
    const userMessage = input.trim();
    setMessages(prev => [...prev, {
      id: Date.now(),
      role: "user",
      content: userMessage,
      timestamp: new Date()
    }]);

    setInput("");
    setIsLoading(true);
    setCurrentProgress(null);
    let assistantContent = "";
    const assistantId = Date.now() + 1;

    try {
      // 1. Conectar a /api/query/stream
      const response = await fetch(`${apiUrl}/api/query/stream`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          query: userMessage
        })
      });

      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }

      // 2. Leer stream
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n\n");

        // Procesar líneas completas
        for (let i = 0; i < lines.length - 1; i++) {
          const line = lines[i];

          if (line.startsWith("event: ")) {
            const eventType = line.slice(7);
            const dataLine = lines[i + 1];

            if (dataLine && dataLine.startsWith("data: ")) {
              try {
                const eventData = JSON.parse(dataLine.slice(6));

                // 3. Procesar eventos
                switch (eventData.type) {
                  case "progress":
                    // Mostrar progreso
                    setCurrentProgress({
                      stage: eventData.stage,
                      message: eventData.message,
                      percent: eventData.progress
                    });
                    break;

                  case "answer_chunk":
                    // Agregar chunk a respuesta
                    assistantContent += eventData.chunk;

                    // Actualizar UI en tiempo real
                    setMessages(prev => {
                      const updated = [...prev];
                      const lastMsg = updated[updated.length - 1];

                      if (lastMsg && lastMsg.id === assistantId) {
                        // Actualizar mensaje existente
                        lastMsg.content = assistantContent;
                      } else {
                        // Crear nuevo mensaje
                        updated.push({
                          id: assistantId,
                          role: "assistant",
                          content: assistantContent,
                          timestamp: new Date()
                        });
                      }

                      return updated;
                    });
                    break;

                  case "final_result":
                    // Query completada
                    console.log("Query completada:", eventData);
                    setCurrentProgress(null);
                    break;
                }
              } catch (e) {
                console.warn("Error parsing event:", e);
              }
            }

            i++; // Skip la línea de data
          }
        }

        // Guardar lo que no fue procesado
        buffer = lines[lines.length - 1];
      }

    } catch (error) {
      console.error("Error:", error);
      setMessages(prev => [...prev, {
        id: Date.now() + 2,
        role: "assistant",
        content: `❌ Error: ${error.message}. Por favor intenta de nuevo.`,
        timestamp: new Date(),
        isError: true
      }]);
    } finally {
      setIsLoading(false);
      setCurrentProgress(null);
    }
  };

  return (
    <div className="chat-container">
      {/* Header */}
      <div className="chat-header">
        <h1>🎤 Red Bull Batalla Chat</h1>
        <p>Pregunta sobre MCs, batallas y estadísticas</p>
      </div>

      {/* Messages Area */}
      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="empty-state">
            <h2>Bienvenido a Red Bull Batalla</h2>
            <p>Pregunta sobre:</p>
            <ul>
              <li>Estadísticas de MCs</li>
              <li>Head-to-head entre dos raperos</li>
              <li>Rankings y mejores freestylers</li>
              <li>Detalles de eventos</li>
              <li>Historial de batallas</li>
            </ul>
          </div>
        )}

        {messages.map((msg) => (
          <div key={msg.id} className={`message ${msg.role}`}>
            <div className="message-bubble">
              {msg.role === "user" ? (
                <>
                  <span className="avatar">👤</span>
                  <span className="content">{msg.content}</span>
                </>
              ) : (
                <>
                  <span className="avatar">🤖</span>
                  <div className="content">
                    {msg.content}
                    {msg.isError && <span className="error-indicator">⚠️</span>}
                  </div>
                </>
              )}
            </div>
            {msg.timestamp && (
              <span className="timestamp">
                {msg.timestamp.toLocaleTimeString()}
              </span>
            )}
          </div>
        ))}

        {/* Progress Indicator */}
        {currentProgress && (
          <div className="progress-indicator">
            <div className="spinner">⚙️</div>
            <div className="progress-text">
              <p className="stage">{currentProgress.stage}</p>
              <p className="message">{currentProgress.message}</p>
              <div className="progress-bar">
                <div
                  className="progress-fill"
                  style={{ width: `${currentProgress.percent}%` }}
                />
              </div>
              <p className="percent">{currentProgress.percent}%</p>
            </div>
          </div>
        )}

        {/* Auto-scroll target */}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <form onSubmit={handleSend} className="chat-input-form">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Escribe tu pregunta... (ej: ¿Cómo le fue a Dani en España?)"
          disabled={isLoading}
          className="chat-input"
          autoFocus
        />
        <button
          type="submit"
          disabled={isLoading || !input.trim()}
          className="send-button"
        >
          {isLoading ? "⏳ Procesando..." : "📤 Enviar"}
        </button>
      </form>

      {/* Example Queries */}
      {messages.length === 0 && (
        <div className="example-queries">
          <p>Ejemplos de preguntas:</p>
          <button
            onClick={() => setInput("¿Estadísticas de Dani?")}
            className="example-btn"
          >
            Estadísticas de Dani
          </button>
          <button
            onClick={() => setInput("Dani vs Chuty")}
            className="example-btn"
          >
            Dani vs Chuty
          </button>
          <button
            onClick={() => setInput("Top 10 mejores freestylers")}
            className="example-btn"
          >
            Top 10
          </button>
        </div>
      )}
    </div>
  );
}

/**
 * ESTILOS CSS (ChatComponent.css)
 */
const CSS = `
.chat-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.chat-header {
  background: rgba(0, 0, 0, 0.2);
  color: white;
  padding: 20px;
  text-align: center;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.chat-header h1 {
  margin: 0;
  font-size: 24px;
}

.chat-header p {
  margin: 5px 0 0 0;
  opacity: 0.9;
  font-size: 14px;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.message {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message.user {
  align-items: flex-end;
}

.message-bubble {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  max-width: 70%;
}

.message.user .message-bubble {
  flex-direction: row-reverse;
}

.avatar {
  font-size: 24px;
  flex-shrink: 0;
}

.content {
  background: white;
  border-radius: 15px;
  padding: 12px 15px;
  line-height: 1.5;
  color: #333;
  word-wrap: break-word;
  overflow-wrap: break-word;
}

.message.user .content {
  background: #667eea;
  color: white;
}

.timestamp {
  font-size: 12px;
  opacity: 0.7;
  color: white;
  margin-top: 5px;
  padding: 0 10px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100%;
  color: white;
  text-align: center;
}

.empty-state h2 {
  font-size: 28px;
  margin-bottom: 15px;
}

.empty-state ul {
  list-style: none;
  padding: 0;
  margin: 10px 0;
}

.empty-state li {
  padding: 5px 0;
  opacity: 0.9;
}

.progress-indicator {
  display: flex;
  gap: 15px;
  background: rgba(255, 255, 255, 0.1);
  padding: 15px;
  border-radius: 10px;
  color: white;
}

.spinner {
  font-size: 24px;
  animation: spin 1s linear infinite;
  flex-shrink: 0;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.progress-text {
  flex: 1;
}

.stage {
  font-weight: bold;
  margin: 0 0 5px 0;
  font-size: 14px;
}

.message {
  margin: 0 0 5px 0;
  font-size: 13px;
  opacity: 0.9;
}

.progress-bar {
  width: 100%;
  height: 4px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 2px;
  overflow: hidden;
  margin: 8px 0;
}

.progress-fill {
  height: 100%;
  background: #4CAF50;
  width: 0%;
  transition: width 0.3s ease;
}

.percent {
  font-size: 12px;
  opacity: 0.8;
  margin: 5px 0 0 0;
}

.chat-input-form {
  display: flex;
  gap: 10px;
  padding: 15px 20px;
  background: rgba(0, 0, 0, 0.1);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.chat-input {
  flex: 1;
  padding: 12px 15px;
  border: none;
  border-radius: 25px;
  font-size: 14px;
  outline: none;
  background: white;
  color: #333;
}

.chat-input::placeholder {
  color: #999;
}

.chat-input:disabled {
  background: #f0f0f0;
  color: #ccc;
}

.send-button {
  padding: 12px 25px;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 25px;
  cursor: pointer;
  font-weight: bold;
  transition: background 0.3s;
}

.send-button:hover:not(:disabled) {
  background: #45a049;
}

.send-button:disabled {
  background: #cccccc;
  cursor: not-allowed;
}

.example-queries {
  padding: 15px 20px;
  text-align: center;
  color: white;
}

.example-queries p {
  margin: 0 0 10px 0;
  opacity: 0.9;
}

.example-btn {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  padding: 8px 15px;
  border-radius: 15px;
  margin: 5px;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 13px;
}

.example-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.05);
}

.error-indicator {
  margin-left: 5px;
}

/* Responsive */
@media (max-width: 768px) {
  .message-bubble {
    max-width: 95% !important;
  }

  .chat-header h1 {
    font-size: 20px;
  }
}
`;
