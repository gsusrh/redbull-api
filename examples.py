"""
Ejemplos de uso de Red Bull Batalla Agent Suite.
Demostraciones prácticas de endpoints y funcionalidades.
"""

import httpx
import asyncio
import json

# URLs base
BASE_URL = "http://localhost:8000"


class APIExamples:
    """Ejemplos de uso de la API."""

    @staticmethod
    async def example_search_person():
        """Ejemplo 1: Buscar un MC."""
        print("\n📍 Ejemplo: Buscar MC")
        print("-" * 50)

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/api/search/persons?q=Dani",
                timeout=10.0
            )

        results = response.json()
        print(f"Resultados: {json.dumps(results, indent=2, ensure_ascii=False)}")

    @staticmethod
    async def example_h2h_query():
        """Ejemplo 2: Consulta H2H vía agent."""
        print("\n📍 Ejemplo: H2H (Dani vs Chuty)")
        print("-" * 50)

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/api/query",
                json={"query": "¿Quién ganó más entre Dani y Chuty?"},
                timeout=30.0
            )

        result = response.json()
        print(f"Pregunta: ¿Quién ganó más entre Dani y Chuty?")
        print(f"Respuesta: {result.get('answer', 'N/A')}")
        print(f"Intent: {result.get('intent', {}).get('type', 'N/A')}")

    @staticmethod
    async def example_stats_query():
        """Ejemplo 3: Estadísticas de un MC."""
        print("\n📍 Ejemplo: Estadísticas de MC")
        print("-" * 50)

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/api/query",
                json={"query": "¿Cuáles son las estadísticas de Dani?"},
                timeout=30.0
            )

        result = response.json()
        print(f"Pregunta: ¿Cuáles son las estadísticas de Dani?")
        print(f"Respuesta: {result.get('answer', 'N/A')}")

    @staticmethod
    async def example_ranking_endpoint():
        """Ejemplo 4: Ranking directo vía endpoint."""
        print("\n📍 Ejemplo: Top 10 Freestylers")
        print("-" * 50)

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/api/rankings/top-performers?limit=10",
                timeout=10.0
            )

        results = response.json()
        print(f"Top 10 Performers:")
        for performer in results[:10]:
            print(
                f"  {performer['aka']} ({performer['country']}) - "
                f"{performer['win_rate']} ({performer['wins']}/{performer['total_battles']})"
            )

    @staticmethod
    async def example_ranking_by_country():
        """Ejemplo 5: Ranking por país."""
        print("\n📍 Ejemplo: Top Performers en España")
        print("-" * 50)

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/api/rankings/top-performers?country=spain&limit=5",
                timeout=10.0
            )

        results = response.json()
        print(f"Top 5 Freestylers en España:")
        for performer in results:
            print(f"  {performer['aka']} - {performer['win_rate']}")

    @staticmethod
    async def example_event_details():
        """Ejemplo 6: Detalles de evento."""
        print("\n📍 Ejemplo: Evento por ID")
        print("-" * 50)

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/api/event/1",
                timeout=10.0
            )

        if response.status_code == 200:
            event = response.json()
            print(f"Evento: {event.get('name', 'N/A')}")
            print(f"Año: {event.get('year', 'N/A')}")
            print(f"País: {event.get('country', 'N/A')}")
            print(f"Participantes: {event.get('total_participants', 'N/A')}")
            print(f"Batallas: {len(event.get('battles_list', []))}")
        else:
            print(f"Evento no encontrado")

    @staticmethod
    async def example_person_stats():
        """Ejemplo 7: Estadísticas de persona por ID."""
        print("\n📍 Ejemplo: Estadísticas Detalladas")
        print("-" * 50)

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/api/person/1/stats",
                timeout=10.0
            )

        if response.status_code == 200:
            stats = response.json()
            person = stats.get('person', {})
            statistics = stats.get('statistics', {})

            print(f"MC: {person.get('aka', 'N/A')}")
            print(f"Estadísticas:")
            print(f"  Total Batallas: {statistics.get('total_battles', 'N/A')}")
            print(f"  Victorias: {statistics.get('total_wins', 'N/A')}")
            print(f"  Win Rate: {statistics.get('win_rate', 'N/A')}")
            print(f"  Racha Actual: {statistics.get('current_win_streak', 'N/A')}")
            print(f"  Mejor Racha: {statistics.get('longest_win_streak', 'N/A')}")

    @staticmethod
    async def example_h2h_endpoint():
        """Ejemplo 8: H2H directo vía endpoint."""
        print("\n📍 Ejemplo: H2H por IDs")
        print("-" * 50)

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/api/h2h/1/2",
                timeout=10.0
            )

        if response.status_code == 200:
            h2h = response.json()
            print(f"{h2h.get('person1', 'MC1')} vs {h2h.get('person2', 'MC2')}")
            print(f"{h2h.get('person1', 'MC1')} Victorias: {h2h.get('person1_wins', 0)}")
            print(f"{h2h.get('person2', 'MC2')} Victorias: {h2h.get('person2_wins', 0)}")
            print(f"Enfrentamientos Totales: {h2h.get('total_encounters', 0)}")

    @staticmethod
    async def example_ingest_person():
        """Ejemplo 9: Ingerir nueva persona."""
        print("\n📍 Ejemplo: Ingerir Nueva Persona")
        print("-" * 50)

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/api/ingest/person",
                json={
                    "aka": "Nuevo MC",
                    "full_name": "Nombre Completo",
                    "country": "spain",
                    "style": "flow",
                    "debut_year": 2015
                },
                timeout=10.0
            )

        result = response.json()
        print(f"Status: {result.get('status', 'N/A')}")
        print(f"Person ID: {result.get('person_id', 'N/A')}")
        print(f"AKA: {result.get('aka', 'N/A')}")

    @staticmethod
    async def example_ingest_event():
        """Ejemplo 10: Ingerir evento."""
        print("\n📍 Ejemplo: Ingerir Evento")
        print("-" * 50)

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/api/ingest/event",
                json={
                    "name": "Batalla de Gallos 2024",
                    "event_type": "nacional",
                    "year": 2024,
                    "country": "spain",
                    "city": "Madrid",
                    "place": "La Riviera",
                    "total_participants": 16
                },
                timeout=10.0
            )

        result = response.json()
        print(f"Status: {result.get('status', 'N/A')}")
        print(f"Event ID: {result.get('event_id', 'N/A')}")
        print(f"Nombre: {result.get('name', 'N/A')}")

    @staticmethod
    async def example_list_events():
        """Ejemplo 11: Listar eventos."""
        print("\n📍 Ejemplo: Listar Eventos")
        print("-" * 50)

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/api/events?year=2023",
                timeout=10.0
            )

        events = response.json()
        print(f"Eventos en 2023: {len(events)}")
        for event in events[:5]:
            print(
                f"  {event.get('name', 'N/A')} - "
                f"{event.get('city', 'N/A')}, {event.get('country', 'N/A')}"
            )

    @staticmethod
    async def example_by_style():
        """Ejemplo 12: MCs por estilo."""
        print("\n📍 Ejemplo: MCs por Estilo (Punchline)")
        print("-" * 50)

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/api/rankings/by-style?style=punchline",
                timeout=10.0
            )

        result = response.json()
        if isinstance(result, dict) and "error" not in result:
            people = result.get("results", [])
            print(f"MCs con estilo Punchline: {len(people)}")
            for person in people[:10]:
                print(f"  {person['aka']} ({person.get('country', 'N/A')})")

    @staticmethod
    async def example_health_check():
        """Ejemplo 13: Health check."""
        print("\n📍 Ejemplo: Health Check")
        print("-" * 50)

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/health",
                timeout=5.0
            )

        health = response.json()
        print(f"Status: {health.get('status', 'N/A')}")
        print(f"Version: {health.get('version', 'N/A')}")
        print(f"Timestamp: {health.get('timestamp', 'N/A')}")

    @staticmethod
    async def example_cache_stats():
        """Ejemplo 14: Cache stats."""
        print("\n📍 Ejemplo: Cache Stats")
        print("-" * 50)

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/api/cache/stats",
                timeout=5.0
            )

        stats = response.json()
        print(f"Cache Entries: {stats.get('total_entries', 0)}")
        print(f"TTL: {stats.get('ttl_seconds', 0)}s")
        print(f"Size: {stats.get('cache_size_mb', 0):.2f} MB")

    @staticmethod
    async def example_counts():
        """Ejemplo 15: Conteos de datos."""
        print("\n📍 Ejemplo: Conteos de Datos")
        print("-" * 50)

        async with httpx.AsyncClient() as client:
            persons = await client.get(f"{BASE_URL}/api/info/persons/count", timeout=5.0)
            events = await client.get(f"{BASE_URL}/api/info/events/count", timeout=5.0)
            battles = await client.get(f"{BASE_URL}/api/info/battles/count", timeout=5.0)

        print(f"Total Personas: {persons.json().get('total_persons', 0)}")
        print(f"Total Eventos: {events.json().get('total_events', 0)}")
        print(f"Total Batallas: {battles.json().get('total_battles', 0)}")


async def run_all_examples():
    """Ejecuta todos los ejemplos."""
    print("=" * 50)
    print("Red Bull Batalla Agent Suite - Examples")
    print("=" * 50)

    try:
        # Ejemplos básicos (no requieren datos)
        await APIExamples.example_health_check()

        # Ejemplos de búsqueda y consultas
        # (Descomentar cuando haya datos en BD)
        # await APIExamples.example_search_person()
        # await APIExamples.example_h2h_query()
        # await APIExamples.example_stats_query()
        # await APIExamples.example_ranking_endpoint()

        # Ejemplos de ingesta (crear datos)
        # await APIExamples.example_ingest_person()
        # await APIExamples.example_ingest_event()

        # Ejemplos finales
        await APIExamples.example_counts()
        await APIExamples.example_cache_stats()

    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    print("\nNota: Asegúrate que el servidor está corriendo:")
    print("  uvicorn main:app --reload")
    print()

    asyncio.run(run_all_examples())
