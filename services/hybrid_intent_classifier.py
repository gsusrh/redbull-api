"""
Hybrid Intent Classifier - MiniLM + DeepSeek Fallback
Si MiniLM no está seguro, delega a LLM para máxima precisión
"""

import logging
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass

from services.minilm_intent_classifier import (
    get_intent_classifier,
    IntentPrediction
)
from config import get_llm

logger = logging.getLogger(__name__)


@dataclass
class HybridIntentResult:
    """Resultado de clasificación híbrida"""
    intent: str
    confidence: float
    similarity_score: float
    source: str  # "minilm" o "deepseek"
    elapsed_ms: float
    alternatives: list = None
    explanation: Optional[str] = None


class HybridIntentClassifier:
    """
    Clasificador híbrido: MiniLM + DeepSeek LLM fallback

    Estrategia:
    1. Intenta MiniLM (rápido, 150-200ms)
    2. Si confidence >= threshold → retorna
    3. Si confidence < threshold → delega a DeepSeek (preciso, 800-1200ms)

    Esto optimiza para velocidad Y precisión:
    - 90% queries usan MiniLM rápido
    - 10% queries complejas usan DeepSeek preciso
    - Latencia promedio: ~250ms
    - Precisión promedio: 96-98%
    """

    def __init__(
        self,
        minilm_threshold: float = 0.70,
        enable_deepseek_fallback: bool = True
    ):
        """
        Args:
            minilm_threshold: Confianza mínima de MiniLM (0-1)
                Si es menor, delega a DeepSeek
                Recomendado: 0.70 (equilibrado)
            enable_deepseek_fallback: Si usar DeepSeek como fallback
        """
        self.minilm_classifier = get_intent_classifier(use_fallback=False)
        self.threshold = minilm_threshold
        self.enable_deepseek_fallback = enable_deepseek_fallback
        self.llm = get_llm() if enable_deepseek_fallback else None

        logger.info(
            f"🤖 HybridIntentClassifier inicializado "
            f"(MiniLM threshold: {minilm_threshold:.0%}, "
            f"DeepSeek fallback: {enable_deepseek_fallback})"
        )

    def classify(self, query: str) -> HybridIntentResult:
        """
        Clasifica intención con fallback inteligente

        Args:
            query: Texto de entrada del usuario

        Returns:
            HybridIntentResult con intención, confianza y fuente
        """
        start_time = time.time()

        # Paso 1: Intenta MiniLM (rápido)
        minilm_result = self.minilm_classifier.classify(query)
        minilm_elapsed = (time.time() - start_time) * 1000

        logger.info(
            f"📊 MiniLM: {minilm_result.intent} "
            f"({minilm_result.confidence:.1%}) [{minilm_elapsed:.1f}ms]"
        )

        # Paso 2: Verifica confianza
        if minilm_result.confidence >= self.threshold:
            # ✅ MiniLM tiene suficiente confianza
            return HybridIntentResult(
                intent=minilm_result.intent,
                confidence=minilm_result.confidence,
                similarity_score=minilm_result.similarity_score,
                source="minilm",
                elapsed_ms=minilm_elapsed,
                alternatives=minilm_result.alternatives
            )

        # Paso 3: Confianza baja → delega a DeepSeek
        if not self.enable_deepseek_fallback:
            logger.warning(
                f"⚠️  MiniLM baja confianza ({minilm_result.confidence:.1%}) "
                f"pero DeepSeek fallback deshabilitado"
            )
            return HybridIntentResult(
                intent=minilm_result.intent,
                confidence=minilm_result.confidence,
                similarity_score=minilm_result.similarity_score,
                source="minilm",
                elapsed_ms=minilm_elapsed,
                alternatives=minilm_result.alternatives,
                explanation="Baja confianza de MiniLM pero fallback deshabilitado"
            )

        logger.info(
            f"⚠️  MiniLM baja confianza ({minilm_result.confidence:.1%}) "
            f"→ Delegando a DeepSeek..."
        )

        # Delega a DeepSeek
        deepseek_result = self._classify_with_deepseek(query)
        total_elapsed = (time.time() - start_time) * 1000

        logger.info(
            f"🧠 DeepSeek: {deepseek_result['intent']} "
            f"({deepseek_result['confidence']:.1%}) [total: {total_elapsed:.1f}ms]"
        )

        return HybridIntentResult(
            intent=deepseek_result["intent"],
            confidence=deepseek_result["confidence"],
            similarity_score=deepseek_result.get("similarity_score", 0.0),
            source="deepseek",
            elapsed_ms=total_elapsed,
            alternatives=deepseek_result.get("alternatives"),
            explanation=f"MiniLM no confiable ({minilm_result.confidence:.1%}), "
                        f"DeepSeek consultado para precisión ({deepseek_result['confidence']:.1%})"
        )

    def _classify_with_deepseek(self, query: str) -> Dict[str, Any]:
        """
        Clasifica usando DeepSeek LLM para máxima precisión

        Args:
            query: Texto de entrada

        Returns:
            Dict con intención y confianza
        """
        from datasets.intent_training_data import INTENT_DATASET

        # Construye prompt para DeepSeek
        intents_list = "\n".join([
            f"- {intent}: {INTENT_DATASET[intent]['description']}"
            for intent in INTENT_DATASET.keys()
        ])

        prompt = f"""Eres un experto en clasificación de intenciones para un sistema de consultas sobre Red Bull Batalla.

INTENCIONES DISPONIBLES:
{intents_list}

QUERY DEL USUARIO:
"{query}"

INSTRUCCIONES:
1. Analiza la query cuidadosamente
2. Clasifica en UNA de las 12 intenciones disponibles
3. Proporciona confianza de 0 a 1

RESPUESTA (JSON):
{{
    "intent": "<nombre_intención>",
    "confidence": <número_0_a_1>,
    "reasoning": "<explicación_breve>"
}}"""

        try:
            response = self.llm.invoke(prompt)
            result_text = response.content

            # Parsea respuesta JSON
            import json
            import re

            # Extrae JSON de la respuesta
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                return {
                    "intent": result.get("intent", "general_search"),
                    "confidence": min(1.0, max(0.0, float(result.get("confidence", 0.85)))),
                    "similarity_score": float(result.get("confidence", 0.85)),
                    "reasoning": result.get("reasoning", "")
                }

        except Exception as e:
            logger.error(f"❌ Error en DeepSeek fallback: {e}")

        # Fallback final: usa MiniLM como está
        logger.warning("⚠️  DeepSeek fallback falló, retornando MiniLM como está")
        minilm_result = self.minilm_classifier.classify(query)
        return {
            "intent": minilm_result.intent,
            "confidence": minilm_result.confidence,
            "similarity_score": minilm_result.similarity_score
        }

    def batch_classify(self, queries: list) -> list:
        """
        Clasifica múltiples queries de una vez

        Args:
            queries: Lista de textos

        Returns:
            Lista de HybridIntentResult
        """
        results = []
        for query in queries:
            result = self.classify(query)
            results.append(result)

        return results

    def set_threshold(self, new_threshold: float):
        """
        Cambia el threshold de MiniLM para delegación

        Args:
            new_threshold: Nuevo threshold (0-1)
                0.60 = muy permisivo (más DeepSeek)
                0.70 = equilibrado (recomendado)
                0.85 = muy conservador (menos DeepSeek)
        """
        if not 0.0 <= new_threshold <= 1.0:
            raise ValueError("Threshold debe estar entre 0 y 1")

        self.threshold = new_threshold
        logger.info(f"🔧 Threshold actualizado a {new_threshold:.0%}")

    def get_stats(self) -> Dict[str, Any]:
        """Retorna estadísticas de uso"""
        return {
            "threshold": self.threshold,
            "deepseek_enabled": self.enable_deepseek_fallback,
            "model_minilm": "paraphrase-multilingual-MiniLM-L12-v2",
            "model_deepseek": "deepseek-chat",
        }


# Instancia global
_hybrid_classifier: HybridIntentClassifier = None


def get_hybrid_intent_classifier(
    minilm_threshold: float = 0.70,
    enable_deepseek_fallback: bool = True
) -> HybridIntentClassifier:
    """
    Factory para obtener instancia del clasificador híbrido (singleton)

    Args:
        minilm_threshold: Confianza mínima para aceptar MiniLM
        enable_deepseek_fallback: Habilitar fallback a DeepSeek
    """
    global _hybrid_classifier

    if _hybrid_classifier is None:
        _hybrid_classifier = HybridIntentClassifier(
            minilm_threshold=minilm_threshold,
            enable_deepseek_fallback=enable_deepseek_fallback
        )

    return _hybrid_classifier
