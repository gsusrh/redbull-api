#!/usr/bin/env python3
"""
Script para crear las tablas de la base de datos
"""

import os
from sqlalchemy import create_engine
from models import Base

# Obtener DATABASE_URI
DATABASE_URI = os.getenv(
    "DATABASE_URI",
    "postgresql://postgres:HUOMtnXMvadivsKSrzQCmpxOqfTxaZJz@maglev.proxy.rlwy.net:30559/railway"
)

print(f"📦 Conectando a: {DATABASE_URI[:50]}...")

try:
    # Crear engine
    engine = create_engine(DATABASE_URI, echo=False)

    # Crear todas las tablas
    print("📝 Creando tablas...")
    Base.metadata.create_all(bind=engine)

    print("✅ ¡Tablas creadas exitosamente!")
    print("\n📚 Tablas creadas:")
    for table in Base.metadata.tables.keys():
        print(f"   • {table}")

except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)
