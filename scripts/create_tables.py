#!/usr/bin/env python3
"""
Script para crear las tablas de la base de datos
"""

import os
import sys
from pathlib import Path

# Agregar directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from models import Base

# Obtener DATABASE_URI
DATABASE_URI = os.getenv("DATABASE_URI")
if not DATABASE_URI:
    print("❌ ERROR: DATABASE_URI no configurada")
    print("\nAgrega a tu .env:")
    print("DATABASE_URI=postgresql://usuario:contraseña@host:puerto/base_datos")
    exit(1)

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
