"""
Intent Classifier - MiniLM
Clasificador robusto de intenciones usando paraphrase-multilingual-MiniLM-L12-v2
Entiende typos, variaciones lingüísticas y español coloquial
"""

import json
import numpy as np
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from pathlib import Path
import pickle
import logging

try:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    MINILM_AVAILABLE = True
except ImportError:
    MINILM_AVAILABLE = False
    logging.warning("sentence-transformers no está instalado. Instala con: pip install sentence-transformers scikit-learn")

from datasets.intent_training_data import INTENT_DATASET, get_all_intents

logger = logging.getLogger(__name__)


@dataclass
class IntentPrediction:
    """Resultado de predicción de intención"""
    intent: str
    confidence: float
    similarity_score: float
    alternatives: List[Tuple[str, float]] = None  # Top 3 alternativas


class MiniLMIntentClassifier:
    """
    Clasificador de intenciones usando MiniLM

    Características:
    - Usa paraphrase-multilingual-MiniLM-L12-v2 (60MB, muy ligero)
    - Entiende typos, acentos mal puestos, variaciones
    - Funciona en CPU (~150-200ms por predicción)
    - Sin entrenamiento necesario (usa ejemplos del dataset)
    - Muy robusto a variaciones lingüísticas
    """

    MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    CACHE_DIR = Path(__file__).parent.parent / ".cache" / "minilm"

    def __init__(self, use_gpu: bool = False):
        """
        Inicializa el clasificador

        Args:
            use_gpu: Si usar GPU (si está disponible)
        """
        if not MINILM_AVAILABLE:
            raise ImportError(
                "sentence-transformers es requerido. Instala con:\n"
                "pip install sentence-transformers scikit-learn"
            )

        logger.info("🔄 Cargando MiniLM model...")
        device = "cuda" if use_gpu else "cpu"
        self.model = SentenceTransformer(
            self.MODEL_NAME,
            device=device,
            cache_folder=str(self.CACHE_DIR)
        )
        logger.info(f"✅ MiniLM cargado en {device}")

        # Preparar embeddings de entrenamiento
        self._prepare_training_embeddings()

    def _prepare_training_embeddings(self):
        """
        Prepara embeddings para todos los ejemplos de entrenamiento
        Los calcula una sola vez al inicio
        """
        logger.info("🔄 Calculando embeddings de entrenamiento...")

        self.intent_embeddings = {}
        self.intent_examples = {}
        self.all_embeddings = []
        self.all_intents = []

        for intent in get_all_intents():
            examples = INTENT_DATASET[intent]["examples"]
            self.intent_examples[intent] = examples

            # Embeeds todos los ejemplos
            embeddings = self.model.encode(
                examples,
                convert_to_numpy=True,
                show_progress_bar=True
            )

            self.intent_embeddings[intent] = embeddings
            self.all_embeddings.extend(embeddings)
            self.all_intents.extend([intent] * len(examples))

        self.all_embeddings = np.array(self.all_embeddings)
        logger.info(f"✅ {len(self.all_embeddings)} embeddings calculados")

    def predict(self, query: str, top_k: int = 3) -> IntentPrediction:
        """
        Predice la intención de una query

        Args:
            query: Texto de entrada del usuario
            top_k: Número de alternativas a retornar

        Returns:
            IntentPrediction con intención, confianza y alternativas
        """
        # Embeeds la query
        query_embedding = self.model.encode([query], convert_to_numpy=True)[0]

        # Calcula similitud coseno con todos los embeddings de entrenamiento
        similarities = cosine_similarity([query_embedding], self.all_embeddings)[0]

        # Encuentra el vecino más cercano
        top_indices = np.argsort(similarities)[::-1][:top_k]

        # Extrae intenciones predichas
        top_intents = [(self.all_intents[i], similarities[i]) for i in top_indices]

        # Agrupa por intención y calcula promedio
        intent_scores = {}
        for intent, score in top_intents:
            if intent not in intent_scores:
                intent_scores[intent] = []
            intent_scores[intent].append(score)

        # Promedia scores por intención
        intent_avg_scores = {
            intent: (np.mean(scores), max(scores))
            for intent, scores in intent_scores.items()
        }

        # Intención más probable
        best_intent = max(intent_avg_scores, key=lambda x: x[1])
        best_score = intent_avg_scores[best_intent][1]

        # Confianza basada en el score (0-1)
        confidence = min(1.0, float(best_score))

        # Alternativas
        alternatives = [
            (intent, float(intent_avg_scores[intent][1]))
            for intent in sorted(
                intent_avg_scores,
                key=lambda x: x[1],
                reverse=True
            )[:top_k]
        ]

        return IntentPrediction(
            intent=best_intent,
            confidence=confidence,
            similarity_score=float(best_score),
            alternatives=alternatives
        )

    def batch_predict(self, queries: List[str]) -> List[IntentPrediction]:
        """
        Predice intención para múltiples queries de una vez (más rápido)

        Args:
            queries: Lista de textos

        Returns:
            Lista de IntentPrediction
        """
        # Embeeds todas las queries de una vez
        query_embeddings = self.model.encode(
            queries,
            convert_to_numpy=True,
            show_progress_bar=False
        )

        results = []
        for query_embedding in query_embeddings:
            similarities = cosine_similarity([query_embedding], self.all_embeddings)[0]
            top_indices = np.argsort(similarities)[::-1][:3]
            top_intents = [(self.all_intents[i], similarities[i]) for i in top_indices]

            intent_scores = {}
            for intent, score in top_intents:
                if intent not in intent_scores:
                    intent_scores[intent] = []
                intent_scores[intent].append(score)

            intent_avg_scores = {
                intent: (np.mean(scores), max(scores))
                for intent, scores in intent_scores.items()
            }

            best_intent = max(intent_avg_scores, key=lambda x: x[1])
            best_score = intent_avg_scores[best_intent][1]
            confidence = min(1.0, float(best_score))

            alternatives = [
                (intent, float(intent_avg_scores[intent][1]))
                for intent in sorted(
                    intent_avg_scores,
                    key=lambda x: x[1],
                    reverse=True
                )[:3]
            ]

            results.append(IntentPrediction(
                intent=best_intent,
                confidence=confidence,
                similarity_score=float(best_score),
                alternatives=alternatives
            ))

        return results

    def get_description(self, intent: str) -> str:
        """Retorna descripción de la intención"""
        if intent in INTENT_DATASET:
            return INTENT_DATASET[intent]["description"]
        return "Intención desconocida"

    def explain_prediction(self, query: str, prediction: IntentPrediction) -> Dict[str, Any]:
        """
        Explica por qué se predijo una intención
        Útil para debugging
        """
        return {
            "query": query,
            "predicted_intent": prediction.intent,
            "confidence": prediction.confidence,
            "similarity_score": prediction.similarity_score,
            "description": self.get_description(prediction.intent),
            "alternatives": [
                {"intent": alt[0], "score": alt[1]}
                for alt in prediction.alternatives
            ],
            "examples_from_dataset": self.intent_examples[prediction.intent][:5]
        }


class IntentClassifierWithFallback:
    """
    Wrapper que combina MiniLM + reglas heurísticas
    Usa MiniLM pero con fallback a heurísticos si confianza es baja
    """

    def __init__(self, minilm_threshold: float = 0.70):
        """
        Args:
            minilm_threshold: Confianza mínima para aceptar predicción MiniLM
                             Si es menor, aplica reglas heurísticas adicionales
        """
        self.classifier = MiniLMIntentClassifier()
        self.threshold = minilm_threshold

    def classify(self, query: str) -> IntentPrediction:
        """
        Clasifica intención con MiniLM + fallback a heurísticos
        """
        # Intenta con MiniLM
        prediction = self.classifier.predict(query)

        # Si confianza es baja, aplica heurísticas adicionales
        if prediction.confidence < self.threshold:
            heuristic_intent = self._apply_heuristics(query)
            if heuristic_intent:
                # Retorna predicción heurística pero marca como de baja confianza
                return IntentPrediction(
                    intent=heuristic_intent,
                    confidence=0.65,  # Confianza intermedia
                    similarity_score=prediction.similarity_score,
                    alternatives=prediction.alternatives
                )

        return prediction

    def _apply_heuristics(self, query: str) -> str:
        """
        Reglas heurísticas como fallback
        """
        query_lower = query.lower()

        # Head-to-head
        if any(x in query_lower for x in ["vs", "versus", "enfrenta", "batalla entre"]):
            if any(name in query_lower for name in ["dani", "chuty", "wos", "trueno"]):
                return "head_to_head"

        # Ranking
        if any(x in query_lower for x in ["top", "ranking", "mejores", "leaderboard"]):
            return "ranking"

        # Estadísticas
        if any(x in query_lower for x in ["estadísticas", "estadisticas", "stats", "números", "record"]):
            return "statistics"

        # Batalla específica
        if "batalla" in query_lower and any(x in query_lower for x in ["final", "semifinal", "cuartos", "ronda"]):
            return "battle_details"

        return None


# Instancia global para usar en endpoints
_classifier_instance: IntentClassifierWithFallback = None

def get_intent_classifier(use_fallback: bool = True) -> IntentClassifierWithFallback:
    """
    Factory para obtener instancia del clasificador (singleton)
    """
    global _classifier_instance

    if _classifier_instance is None:
        logger.info("📦 Inicializando clasificador de intenciones...")
        _classifier_instance = IntentClassifierWithFallback()

    return _classifier_instance
