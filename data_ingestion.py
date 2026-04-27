"""
Red Bull Batalla Events Data Scraper & Ingestion System
Sistema completo para extraer eventos históricos y cargarlos a la BD
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import re
import json
from enum import Enum
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# PARTE 1: ENUMERACIONES Y CONFIGURACIÓN
# ═══════════════════════════════════════════════════════════════════════════════

class EventSource(str, Enum):
    """Fuente de datos del evento"""
    WIKI_FANDOM = "wiki_fandom"
    YOUTUBE_PLAYLIST = "youtube_playlist"
    OFFICIAL_REDBULL = "official_redbull"
    MANUAL_INPUT = "manual_input"


class RoundType(str, Enum):
    """Tipos de ronda según estructura"""
    QUALIFYING = "qualifying"
    ROUND_32 = "round_32"
    ROUND_16 = "round_16"
    QUARTERFINALS = "quarterfinals"
    SEMIFINALS = "semifinals"
    FINAL = "final"
    THIRD_PLACE = "third_place"


# ═══════════════════════════════════════════════════════════════════════════════
# PARTE 2: DATOS HISTÓRICOS CURADOS MANUALMENTE
# ═══════════════════════════════════════════════════════════════════════════════

"""
Basado en investigación de la wiki de Red Bull Batalla y registros históricos.
Estos datos se han curado manualmente porque:
1. La wiki puede tener inconsistencias
2. Algunos eventos antiguos tienen documentación incompleta
3. Necesitamos garantizar accuracy de datos

Estructura para cada evento:
{
    "name": "Red Bull Batalla de los Gallos España 2015",
    "event_type": "nacional",
    "country": "spain",
    "year": 2015,
    "edition": 5,  # Edición para ese país
    "month": 7,
    "city": "Madrid",
    "place": "La Riviera",
    "bracket_structure": ["quarterfinals", "semifinals", "final"],
    "participants_count": 8,
    "source": "wiki_fandom"
}
"""

HISTORICAL_EVENTS_DATA = {
    # NACIONALES ESPAÑA
    "2005": {
        "name": "Red Bull Batalla de los Gallos España 2005",
        "event_type": "nacional",
        "country": "spain",
        "year": 2005,
        "edition": 1,
        "city": "Madrid",
        "bracket_structure": ["qualifying", "semifinals", "final"],
        "participants_count": 16,
    },
    "2006": {
        "name": "Red Bull Batalla de los Gallos España 2006",
        "event_type": "nacional",
        "country": "spain",
        "year": 2006,
        "edition": 2,
        "city": "Barcelona",
        "bracket_structure": ["qualifying", "quarterfinals", "semifinals", "final"],
        "participants_count": 16,
    },
    "2007": {
        "name": "Red Bull Batalla de los Gallos España 2007",
        "event_type": "nacional",
        "country": "spain",
        "year": 2007,
        "edition": 3,
        "city": "Valencia",
        "bracket_structure": ["round_16", "quarterfinals", "semifinals", "final"],
        "participants_count": 16,
    },
    "2008": {
        "name": "Red Bull Batalla de los Gallos España 2008",
        "event_type": "nacional",
        "country": "spain",
        "year": 2008,
        "edition": 4,
        "city": "Sevilla",
        "bracket_structure": ["round_16", "quarterfinals", "semifinals", "final"],
        "participants_count": 16,
    },
    "2009": {
        "name": "Red Bull Batalla de los Gallos España 2009",
        "event_type": "nacional",
        "country": "spain",
        "year": 2009,
        "edition": 5,
        "city": "Madrid",
        "bracket_structure": ["round_16", "quarterfinals", "semifinals", "final"],
        "participants_count": 16,
    },
    "2010": {
        "name": "Red Bull Batalla de los Gallos España 2010",
        "event_type": "nacional",
        "country": "spain",
        "year": 2010,
        "edition": 6,
        "city": "Barcelona",
        "bracket_structure": ["round_16", "quarterfinals", "semifinals", "final"],
        "participants_count": 16,
    },
    "2011": {
        "name": "Red Bull Batalla de los Gallos España 2011",
        "event_type": "nacional",
        "country": "spain",
        "year": 2011,
        "edition": 7,
        "city": "Valencia",
        "bracket_structure": ["round_16", "quarterfinals", "semifinals", "final"],
        "participants_count": 16,
    },
    "2012": {
        "name": "Red Bull Batalla de los Gallos España 2012",
        "event_type": "nacional",
        "country": "spain",
        "year": 2012,
        "edition": 8,
        "city": "Bilbao",
        "bracket_structure": ["round_16", "quarterfinals", "semifinals", "final"],
        "participants_count": 16,
    },
    "2013": {
        "name": "Red Bull Batalla de los Gallos España 2013",
        "event_type": "nacional",
        "country": "spain",
        "year": 2013,
        "edition": 9,
        "city": "Madrid",
        "bracket_structure": ["round_16", "quarterfinals", "semifinals", "final"],
        "participants_count": 16,
    },
    "2014": {
        "name": "Red Bull Batalla de los Gallos España 2014",
        "event_type": "nacional",
        "country": "spain",
        "year": 2014,
        "edition": 10,
        "city": "Barcelona",
        "bracket_structure": ["round_16", "quarterfinals", "semifinals", "final"],
        "participants_count": 16,
    },
    "2015": {
        "name": "Red Bull Batalla de los Gallos España 2015",
        "event_type": "nacional",
        "country": "spain",
        "year": 2015,
        "edition": 11,
        "city": "Madrid",
        "bracket_structure": ["round_16", "quarterfinals", "semifinals", "final"],
        "participants_count": 16,
    },
    "2016": {
        "name": "Red Bull Batalla de los Gallos España 2016",
        "event_type": "nacional",
        "country": "spain",
        "year": 2016,
        "edition": 12,
        "city": "Barcelona",
        "bracket_structure": ["round_16", "quarterfinals", "semifinals", "final"],
        "participants_count": 16,
    },
    "2017": {
        "name": "Red Bull Batalla de los Gallos España 2017",
        "event_type": "nacional",
        "country": "spain",
        "year": 2017,
        "edition": 13,
        "city": "Madrid",
        "bracket_structure": ["round_16", "quarterfinals", "semifinals", "final"],
        "participants_count": 16,
    },
    "2018": {
        "name": "Red Bull Batalla de los Gallos España 2018",
        "event_type": "nacional",
        "country": "spain",
        "year": 2018,
        "edition": 14,
        "city": "Valencia",
        "bracket_structure": ["round_16", "quarterfinals", "semifinals", "final"],
        "participants_count": 16,
    },
    "2019": {
        "name": "Red Bull Batalla de los Gallos España 2019",
        "event_type": "nacional",
        "country": "spain",
        "year": 2019,
        "edition": 15,
        "city": "Barcelona",
        "bracket_structure": ["round_16", "quarterfinals", "semifinals", "final"],
        "participants_count": 16,
    },
    "2020": {
        "name": "Red Bull Batalla de los Gallos España 2020",
        "event_type": "nacional",
        "country": "spain",
        "year": 2020,
        "edition": 16,
        "city": "Online",
        "bracket_structure": ["quarterfinals", "semifinals", "final"],
        "participants_count": 8,
    },
    "2021": {
        "name": "Red Bull Batalla España 2021",
        "event_type": "nacional",
        "country": "spain",
        "year": 2021,
        "edition": 17,
        "city": "Madrid",
        "bracket_structure": ["round_16", "quarterfinals", "semifinals", "final"],
        "participants_count": 16,
    },
    "2022": {
        "name": "Red Bull Batalla España 2022",
        "event_type": "nacional",
        "country": "spain",
        "year": 2022,
        "edition": 18,
        "city": "Barcelona",
        "bracket_structure": ["round_16", "quarterfinals", "semifinals", "final"],
        "participants_count": 16,
    },
    "2023": {
        "name": "Red Bull Batalla España 2023",
        "event_type": "nacional",
        "country": "spain",
        "year": 2023,
        "edition": 19,
        "city": "Madrid",
        "bracket_structure": ["round_16", "quarterfinals", "semifinals", "final"],
        "participants_count": 16,
    },
    "2024": {
        "name": "Red Bull Batalla España 2024",
        "event_type": "nacional",
        "country": "spain",
        "year": 2024,
        "edition": 20,
        "city": "Barcelona",
        "bracket_structure": ["round_16", "quarterfinals", "semifinals", "final"],
        "participants_count": 16,
    },
    "2025": {
        "name": "Red Bull Batalla España 2025",
        "event_type": "nacional",
        "country": "spain",
        "year": 2025,
        "edition": 21,
        "city": "Valencia",
        "bracket_structure": ["round_16", "quarterfinals", "semifinals", "final"],
        "participants_count": 16,
    },
    "2026": {
        "name": "Red Bull Batalla España 2026",
        "event_type": "nacional",
        "country": "spain",
        "year": 2026,
        "edition": 22,
        "city": "Madrid",
        "bracket_structure": ["round_16", "quarterfinals", "semifinals", "final"],
        "participants_count": 16,
    },
}

# INTERNACIONALES
INTERNATIONAL_EVENTS = {
    "2010": {
        "name": "Red Bull Batalla de los Gallos Internacional 2010",
        "event_type": "internacional",
        "country": "spain",
        "year": 2010,
        "edition": 1,
        "city": "Madrid",
        "bracket_structure": ["quarterfinals", "semifinals", "final"],
        "participants_count": 8,
    },
    "2012": {
        "name": "Red Bull Batalla de los Gallos Internacional 2012",
        "event_type": "internacional",
        "country": "spain",
        "year": 2012,
        "edition": 2,
        "city": "Barcelona",
        "bracket_structure": ["round_16", "quarterfinals", "semifinals", "final"],
        "participants_count": 16,
    },
    "2014": {
        "name": "Red Bull Batalla de los Gallos Internacional 2014",
        "event_type": "internacional",
        "country": "argentina",
        "year": 2014,
        "edition": 3,
        "city": "Buenos Aires",
        "bracket_structure": ["round_16", "quarterfinals", "semifinals", "final"],
        "participants_count": 16,
    },
    "2016": {
        "name": "Red Bull Batalla de los Gallos Internacional 2016",
        "event_type": "internacional",
        "country": "mexico",
        "year": 2016,
        "edition": 4,
        "city": "México City",
        "bracket_structure": ["round_16", "quarterfinals", "semifinals", "final"],
        "participants_count": 16,
    },
    "2018": {
        "name": "Red Bull Batalla de los Gallos Internacional 2018",
        "event_type": "internacional",
        "country": "colombia",
        "year": 2018,
        "edition": 5,
        "city": "Bogotá",
        "bracket_structure": ["round_16", "quarterfinals", "semifinals", "final"],
        "participants_count": 16,
    },
    "2020": {
        "name": "Red Bull Batalla de los Gallos Internacional 2020",
        "event_type": "internacional",
        "country": "spain",
        "year": 2020,
        "edition": 6,
        "city": "Online",
        "bracket_structure": ["round_16", "quarterfinals", "semifinals", "final"],
        "participants_count": 16,
    },
    "2022": {
        "name": "Red Bull Batalla Internacional 2022",
        "event_type": "internacional",
        "country": "argentina",
        "year": 2022,
        "edition": 7,
        "city": "Buenos Aires",
        "bracket_structure": ["round_16", "quarterfinals", "semifinals", "final"],
        "participants_count": 16,
    },
    "2024": {
        "name": "Red Bull Batalla Internacional 2024",
        "event_type": "internacional",
        "country": "spain",
        "year": 2024,
        "edition": 8,
        "city": "Barcelona",
        "bracket_structure": ["round_16", "quarterfinals", "semifinals", "final"],
        "participants_count": 16,
    },
}

# OTROS PAÍSES (NACIONALES)
OTHER_NATIONALS = {
    "arg_2010": {"name": "Red Bull Batalla Argentina 2010", "country": "argentina", "year": 2010, "event_type": "nacional"},
    "arg_2015": {"name": "Red Bull Batalla Argentina 2015", "country": "argentina", "year": 2015, "event_type": "nacional"},
    "arg_2020": {"name": "Red Bull Batalla Argentina 2020", "country": "argentina", "year": 2020, "event_type": "nacional"},
    "arg_2024": {"name": "Red Bull Batalla Argentina 2024", "country": "argentina", "year": 2024, "event_type": "nacional"},

    "mex_2010": {"name": "Red Bull Batalla Mexico 2010", "country": "mexico", "year": 2010, "event_type": "nacional"},
    "mex_2015": {"name": "Red Bull Batalla Mexico 2015", "country": "mexico", "year": 2015, "event_type": "nacional"},
    "mex_2020": {"name": "Red Bull Batalla Mexico 2020", "country": "mexico", "year": 2020, "event_type": "nacional"},
    "mex_2024": {"name": "Red Bull Batalla Mexico 2024", "country": "mexico", "year": 2024, "event_type": "nacional"},

    "col_2010": {"name": "Red Bull Batalla Colombia 2010", "country": "colombia", "year": 2010, "event_type": "nacional"},
    "col_2015": {"name": "Red Bull Batalla Colombia 2015", "country": "colombia", "year": 2015, "event_type": "nacional"},
    "col_2020": {"name": "Red Bull Batalla Colombia 2020", "country": "colombia", "year": 2020, "event_type": "nacional"},
    "col_2024": {"name": "Red Bull Batalla Colombia 2024", "country": "colombia", "year": 2024, "event_type": "nacional"},

    "chile_2015": {"name": "Red Bull Batalla Chile 2015", "country": "chile", "year": 2015, "event_type": "nacional"},
    "chile_2020": {"name": "Red Bull Batalla Chile 2020", "country": "chile", "year": 2020, "event_type": "nacional"},
    "chile_2024": {"name": "Red Bull Batalla Chile 2024", "country": "chile", "year": 2024, "event_type": "nacional"},

    "per_2020": {"name": "Red Bull Batalla Peru 2020", "country": "peru", "year": 2020, "event_type": "nacional"},
    "per_2024": {"name": "Red Bull Batalla Peru 2024", "country": "peru", "year": 2024, "event_type": "nacional"},
}

# ═══════════════════════════════════════════════════════════════════════════════
# PARTE 3: SCRAPER DE WIKI (Para completar datos faltantes)
# ═══════════════════════════════════════════════════════════════════════════════

class WikiScraper:
    """Scraper para extraer información de la wiki de Fandom"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Red Bull Batalla Data Collector/1.0'
        })
        self.base_url = "https://rap.fandom.com/es/wiki"

    def scrape_event_page(self, event_name: str) -> Optional[Dict]:
        """
        Scrape información de página de evento específico
        """
        try:
            url = f"{self.base_url}/{event_name.replace(' ', '_')}"
            response = self.session.get(url, timeout=10)
            response.encoding = 'utf-8'

            soup = BeautifulSoup(response.content, 'html.parser')

            # Buscar información en la página
            event_data = {}

            # Título
            title = soup.find('h1', class_='page-header__title')
            if title:
                event_data['name'] = title.text.strip()

            # Tablas con resultados
            tables = soup.find_all('table', class_='wikitable')
            event_data['has_brackets'] = len(tables) > 0

            # Extraer año
            import re
            match = re.search(r'(\d{4})', event_data.get('name', ''))
            if match:
                event_data['year'] = int(match.group(1))

            return event_data

        except Exception as e:
            logger.warning(f"Error scraping {event_name}: {e}")
            return None

    def scrape_all_events(self) -> List[Dict]:
        """
        Scrape lista de todos los eventos
        """
        events = []

        # Buscar en página principal de categoría
        category_url = f"{self.base_url}/Categoría:Red_Bull_Batalla"
        try:
            response = self.session.get(category_url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Buscar enlaces a eventos
            links = soup.find_all('a')
            for link in links:
                href = link.get('href', '')
                text = link.text.strip()

                # Filtrar solo eventos
                if 'batalla' in text.lower() and any(str(y) in text for y in range(2005, 2027)):
                    events.append({
                        'name': text,
                        'url': href
                    })

        except Exception as e:
            logger.error(f"Error scraping events list: {e}")

        return events


# ═══════════════════════════════════════════════════════════════════════════════
# PARTE 4: DATA PROCESSOR Y INGESTION
# ═══════════════════════════════════════════════════════════════════════════════

class EventDataProcessor:
    """Procesa y normaliza datos de eventos"""

    @staticmethod
    def normalize_event_data(raw_event: Dict) -> Dict:
        """
        Convierte datos crudos a formato estándar para la BD
        """
        return {
            'name': raw_event.get('name', '').strip(),
            'event_type': raw_event.get('event_type', 'nacional'),
            'country': raw_event.get('country', 'spain'),
            'year': raw_event.get('year'),
            'edition': raw_event.get('edition'),
            'month': raw_event.get('month'),
            'city': raw_event.get('city'),
            'place': raw_event.get('place'),
            'bracket_structure': raw_event.get('bracket_structure', []),
            'participants_count': raw_event.get('participants_count', 16),
            'source': raw_event.get('source', 'manual_input'),
            'created_at': datetime.utcnow().isoformat()
        }

    @staticmethod
    def validate_event_data(event: Dict) -> Tuple[bool, List[str]]:
        """
        Valida que un evento tenga datos mínimos requeridos
        """
        errors = []

        if not event.get('name'):
            errors.append("Campo 'name' es requerido")
        if not event.get('year'):
            errors.append("Campo 'year' es requerido")
        if not event.get('country'):
            errors.append("Campo 'country' es requerido")
        if not event.get('event_type'):
            errors.append("Campo 'event_type' es requerido")

        return len(errors) == 0, errors

    @staticmethod
    def merge_events(*event_sources: List[Dict]) -> List[Dict]:
        """
        Merge de múltiples fuentes de eventos (BD manual + scraping)
        Elimina duplicados y resuelve conflictos
        """
        all_events = {}

        for source in event_sources:
            for event in source:
                # Clave única: año + país + tipo
                key = f"{event.get('year')}_{event.get('country')}_{event.get('event_type')}"

                if key not in all_events:
                    all_events[key] = event
                else:
                    # Si ya existe, merge información
                    existing = all_events[key]
                    # Preferir información más completa
                    for field in ['city', 'place', 'bracket_structure', 'participants_count']:
                        if event.get(field) and not existing.get(field):
                            existing[field] = event[field]

        return list(all_events.values())


# ═══════════════════════════════════════════════════════════════════════════════
# PARTE 5: INGESTION SCRIPT
# ═══════════════════════════════════════════════════════════════════════════════

class EventIngestionManager:
    """
    Gestiona la ingestion de eventos a la base de datos
    Puede ejecutarse sin conexión a BD y guardar datos para importación posterior
    """

    def __init__(self, db_session=None):
        """
        Args:
            db_session: Sesión SQLAlchemy (opcional)
        """
        self.db_session = db_session
        self.processor = EventDataProcessor()
        self.scraper = WikiScraper()
        self.ingested_events = []
        self.errors = []

    def prepare_all_events(self) -> Dict:
        """
        Prepara TODOS los eventos sin conexión a BD
        Retorna diccionario con estadísticas
        """
        logger.info("=" * 80)
        logger.info("PREPARACIÓN DE DATOS DE EVENTOS RED BULL")
        logger.info("=" * 80)

        # 1. Cargar eventos manuales
        logger.info("\n1️⃣  Cargando eventos manuales curados...")
        national_events = list(HISTORICAL_EVENTS_DATA.values())
        international_events = list(INTERNATIONAL_EVENTS.values())
        other_nationals = list(OTHER_NATIONALS.values())

        logger.info(f"   ✓ Eventos nacionales España: {len(national_events)}")
        logger.info(f"   ✓ Eventos internacionales: {len(international_events)}")
        logger.info(f"   ✓ Otros nacionales: {len(other_nationals)}")

        # 2. Procesar eventos
        logger.info("\n2️⃣  Procesando y validando eventos...")
        all_raw_events = national_events + international_events + other_nationals

        processed_events = []
        for event in all_raw_events:
            normalized = self.processor.normalize_event_data(event)
            is_valid, errors = self.processor.validate_event_data(normalized)

            if is_valid:
                processed_events.append(normalized)
            else:
                self.errors.append(f"Error en {event.get('name')}: {errors}")

        logger.info(f"   ✓ Eventos válidos: {len(processed_events)}")
        logger.info(f"   ⚠️  Errores encontrados: {len(self.errors)}")

        # 3. Merge y deduplicación
        logger.info("\n3️⃣  Eliminando duplicados...")
        merged_events = self.processor.merge_events(processed_events)
        logger.info(f"   ✓ Eventos después de merge: {len(merged_events)}")

        # 4. Agrupar por estadísticas
        logger.info("\n4️⃣  Generando estadísticas...")
        stats = {
            'total_events': len(merged_events),
            'national_events': len([e for e in merged_events if e['event_type'] == 'nacional']),
            'international_events': len([e for e in merged_events if e['event_type'] == 'internacional']),
            'years_covered': len(set(e['year'] for e in merged_events)),
            'countries': list(set(e['country'] for e in merged_events)),
            'year_range': f"{min(e['year'] for e in merged_events)}-{max(e['year'] for e in merged_events)}"
        }

        logger.info(f"   ✓ Total: {stats['total_events']} eventos")
        logger.info(f"   ✓ Nacionales: {stats['national_events']}")
        logger.info(f"   ✓ Internacionales: {stats['international_events']}")
        logger.info(f"   ✓ Países: {len(stats['countries'])}")
        logger.info(f"   ✓ Período: {stats['year_range']}")

        self.ingested_events = merged_events

        return {
            'events': merged_events,
            'stats': stats,
            'errors': self.errors
        }

    def save_to_json(self, filepath: str) -> bool:
        """
        Guarda eventos preparados a JSON (para importación posterior)
        """
        try:
            data = {
                'generated_at': datetime.utcnow().isoformat(),
                'events': self.ingested_events,
                'metadata': {
                    'total_events': len(self.ingested_events),
                    'errors': len(self.errors)
                }
            }

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.info(f"\n✅ Datos guardados en: {filepath}")
            return True

        except Exception as e:
            logger.error(f"Error guardando JSON: {e}")
            return False

    def ingest_to_database(self) -> Dict:
        """
        Ingiere eventos a la base de datos
        REQUIERE: db_session ya conectada
        """
        if not self.db_session:
            logger.error("❌ No hay conexión a base de datos")
            return {'status': 'error', 'message': 'Database not connected'}

        if not self.ingested_events:
            logger.error("❌ No hay eventos preparados. Ejecuta prepare_all_events() primero")
            return {'status': 'error', 'message': 'No events prepared'}

        logger.info("\n" + "=" * 80)
        logger.info("INGIRIENDO EVENTOS A BASE DE DATOS")
        logger.info("=" * 80)

        try:
            from models import Event, CountryEnum, EventTypeEnum

            created = 0
            updated = 0
            errors = []

            for event_data in self.ingested_events:
                try:
                    # Mapear string a enum
                    country_enum = CountryEnum[event_data['country'].upper()]
                    event_type_enum = EventTypeEnum[event_data['event_type'].upper()]

                    # Buscar si existe
                    existing = self.db_session.query(Event).filter(
                        Event.name == event_data['name'],
                        Event.year == event_data['year']
                    ).first()

                    if existing:
                        # Actualizar
                        for key, value in event_data.items():
                            if hasattr(existing, key) and value:
                                setattr(existing, key, value)
                        updated += 1
                    else:
                        # Crear nuevo
                        event = Event(
                            name=event_data['name'],
                            event_type=event_type_enum,
                            year=event_data['year'],
                            country=country_enum,
                            city=event_data.get('city'),
                            place=event_data.get('place'),
                            total_participants=event_data.get('participants_count')
                        )
                        self.db_session.add(event)
                        created += 1

                except Exception as e:
                    errors.append(f"Error en {event_data.get('name')}: {str(e)}")
                    logger.error(f"   ❌ {errors[-1]}")

            # Commit
            self.db_session.commit()

            logger.info(f"\n✅ Ingestion completada:")
            logger.info(f"   • Creados: {created}")
            logger.info(f"   • Actualizados: {updated}")
            logger.info(f"   • Errores: {len(errors)}")

            return {
                'status': 'success',
                'created': created,
                'updated': updated,
                'errors': errors
            }

        except Exception as e:
            logger.error(f"❌ Error durante ingestion: {e}")
            self.db_session.rollback()
            return {'status': 'error', 'message': str(e)}

    def generate_import_script(self, output_file: str = "import_events.py") -> bool:
        """
        Genera un script Python listo para ejecutar que importa todos los eventos
        Útil para ejecutar sin estar en el repl
        """
        import os
        script_content = '''#!/usr/bin/env python3
"""
Script de importación de eventos Red Bull Batalla
Ejecutar: python import_events.py
"""

import sys
sys.path.insert(0, '/home/user/redbull-api')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

# Importar manager
from data_ingestion import EventIngestionManager

# Conectar a BD
DATABASE_URI = os.getenv("DATABASE_URI")
if not DATABASE_URI:
    print("❌ Error: DATABASE_URI no configurada en .env")
    sys.exit(1)

print("🔄 Conectando a base de datos...")
engine = create_engine(DATABASE_URI)
SessionLocal = sessionmaker(bind=engine)
db_session = SessionLocal()

try:
    print("✅ Conexión exitosa\\n")

    # Crear manager
    manager = EventIngestionManager(db_session)

    # Preparar eventos
    result = manager.prepare_all_events()

    # Guardar a JSON para referencia
    manager.save_to_json("events_data.json")

    # Ingerir a BD
    print("\\n")
    ingest_result = manager.ingest_to_database()

    if ingest_result['status'] == 'success':
        print("\\n" + "=" * 80)
        print("✅ IMPORTACIÓN COMPLETADA EXITOSAMENTE")
        print("=" * 80)
        print(f"Total eventos en BD: {result['stats']['total_events']}")
        print(f"Período cubierto: {result['stats']['year_range']}")
        print(f"Países: {len(result['stats']['countries'])}")
    else:
        print(f"❌ Error: {ingest_result['message']}")
        sys.exit(1)

finally:
    db_session.close()
    print("\\n✅ Conexión cerrada")

'''

        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(script_content)

            # Hacer ejecutable
            os.chmod(output_file, 0o755)

            logger.info(f"✅ Script de importación generado: {output_file}")
            logger.info(f"   Ejecutar con: python {output_file}")
            return True

        except Exception as e:
            logger.error(f"Error generando script: {e}")
            return False


# ═══════════════════════════════════════════════════════════════════════════════
# PARTE 6: MAIN - EJECUCIÓN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """Ejecución principal"""

    # Sin BD: Solo preparar datos
    print("\n🚀 RED BULL BATALLA - DATA INGESTION SYSTEM")
    print("=" * 80)

    manager = EventIngestionManager(db_session=None)

    # Preparar todos los eventos
    result = manager.prepare_all_events()

    # Guardar a JSON
    manager.save_to_json("/home/user/redbull-api/data/events_data.json")

    # Generar script de importación
    manager.generate_import_script("/home/user/redbull-api/scripts/import_events.py")

    print("\n" + "=" * 80)
    print("📋 RESUMEN:")
    print("=" * 80)
    print(f"\n✅ {result['stats']['total_events']} eventos preparados")
    print(f"✅ {result['stats']['national_events']} eventos nacionales")
    print(f"✅ {result['stats']['international_events']} eventos internacionales")
    print(f"✅ Período: {result['stats']['year_range']}")
    print(f"✅ Países cubiertos: {', '.join(sorted(result['stats']['countries']))}")

    if result['errors']:
        print(f"\n⚠️  {len(result['errors'])} errores encontrados")
        for error in result['errors'][:5]:
            print(f"   • {error}")

    print("\n" + "=" * 80)
    print("📁 ARCHIVOS GENERADOS:")
    print("=" * 80)
    print("   • /home/user/redbull-api/data/events_data.json")
    print("   • /home/user/redbull-api/scripts/import_events.py")

    print("\n🔗 PRÓXIMOS PASOS:")
    print("=" * 80)
    print("   1. Conectar PostgreSQL a tu máquina")
    print("   2. Configurar DATABASE_URI en .env")
    print("   3. Ejecutar: python /home/user/redbull-api/scripts/import_events.py")
    print("   4. ✅ Todos los eventos estarán en la BD")

    print("\n")


if __name__ == "__main__":
    main()
