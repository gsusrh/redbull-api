"""
Servicio de caché para optimizar consultas frecuentes.
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from functools import lru_cache
import json


class CacheService:
    """Gestor de caché con expiración automática."""

    def __init__(self, ttl_seconds: int = 3600):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl = ttl_seconds

    def get(self, key: str) -> Optional[Any]:
        """Obtiene valor del caché si existe y no ha expirado."""
        if key in self.cache:
            entry = self.cache[key]
            if datetime.utcnow() < entry["expires_at"]:
                return entry["value"]
            else:
                del self.cache[key]
        return None

    def set(self, key: str, value: Any) -> None:
        """Almacena valor en caché con TTL."""
        self.cache[key] = {
            "value": value,
            "expires_at": datetime.utcnow() + timedelta(seconds=self.ttl),
            "created_at": datetime.utcnow()
        }

    def delete(self, key: str) -> None:
        """Elimina entrada del caché."""
        if key in self.cache:
            del self.cache[key]

    def clear(self) -> None:
        """Limpia todo el caché."""
        self.cache.clear()

    def get_stats(self) -> Dict[str, Any]:
        """Retorna estadísticas del caché."""
        return {
            "total_entries": len(self.cache),
            "ttl_seconds": self.ttl,
            "cache_size_mb": sum(
                len(json.dumps(entry["value"]).encode())
                for entry in self.cache.values()
            ) / (1024 * 1024)
        }
