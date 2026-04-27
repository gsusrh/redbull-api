#!/usr/bin/env python3
"""
Script de Importación de Eventos Red Bull Batalla
Importa todos los eventos históricos a la base de datos PostgreSQL

Uso:
    python scripts/import_events.py

Requisitos:
    - PostgreSQL corriendo y accesible
    - DATABASE_URI configurada en .env
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()


def main():
    """Importar eventos a BD"""

    logger.info("=" * 80)
    logger.info("RED BULL BATALLA - IMPORTACIÓN DE EVENTOS A BASE DE DATOS")
    logger.info("=" * 80)

    DATABASE_URI = os.getenv("DATABASE_URI")
    if not DATABASE_URI:
        logger.error("❌ DATABASE_URI no configurada en .env")
        sys.exit(1)

    logger.info(f"\n🔗 Conectando a base de datos...")

    try:
        engine = create_engine(DATABASE_URI, echo=False)
        SessionLocal = sessionmaker(bind=engine)
        db_session = SessionLocal()
        db_session.execute("SELECT 1")
        logger.info("✅ Conexión exitosa\n")

    except Exception as e:
        logger.error(f"❌ Error de conexión: {e}")
        sys.exit(1)

    try:
        from data_ingestion import EventIngestionManager
        from models import Base

        # Crear tablas
        logger.info("📋 Verificando tablas...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Tablas listas\n")

        # Preparar e ingerir
        manager = EventIngestionManager(db_session)
        logger.info("🔄 Preparando eventos...")
        result = manager.prepare_all_events()

        logger.info("\n⬇️  Importando a base de datos...\n")
        ingest_result = manager.ingest_to_database()

        if ingest_result['status'] == 'success':
            logger.info("\n" + "=" * 80)
            logger.info("✅ IMPORTACIÓN COMPLETADA")
            logger.info("=" * 80)
            logger.info(f"\nEventos: {result['stats']['total_events']}")
            logger.info(f"Período: {result['stats']['year_range']}")
            logger.info(f"Países: {len(result['stats']['countries'])}")
            logger.info(f"\nCreados: {ingest_result['created']}")
            logger.info(f"Actualizados: {ingest_result['updated']}")
            logger.info("\n🎉 Sistema listo para usar!\n")
        else:
            logger.error(f"❌ {ingest_result['message']}")
            sys.exit(1)

    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    finally:
        db_session.close()


if __name__ == "__main__":
    main()
