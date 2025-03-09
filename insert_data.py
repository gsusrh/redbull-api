import pandas as pd
from sqlalchemy import create_engine, text

# Conexión a PostgreSQL
db_url = "postgresql://postgres:HUOMtnXMvadivsKSrzQCmpxOqfTxaZJz@maglev.proxy.rlwy.net:30559/railway"
engine = create_engine(db_url)

# Cargar Excel
file_path = "plantilla_red_bull_batalla.xlsx"
events_df = pd.read_excel(file_path, sheet_name="events")
persons_df = pd.read_excel(file_path, sheet_name="persons")
battles_df = pd.read_excel(file_path, sheet_name="battles")

# Convertir todos los valores de texto a minúsculas
def normalize_lowercase(df):
    for col in df.columns:
        if df[col].dtype == object:  # Solo columnas de texto
            df[col] = df[col].astype(str).str.lower()
    return df

events_df = normalize_lowercase(events_df)
persons_df = normalize_lowercase(persons_df)
battles_df = normalize_lowercase(battles_df)

# Crear tablas con relaciones
with engine.connect() as conn:
    conn.execute(text("DROP TABLE IF EXISTS battles CASCADE"))
    conn.execute(text("DROP TABLE IF EXISTS persons CASCADE"))
    conn.execute(text("DROP TABLE IF EXISTS events CASCADE"))

    conn.execute(text("""
        CREATE TABLE events (
            evento_id INTEGER PRIMARY KEY,
            name TEXT,
            type TEXT,
            country TEXT,
            city TEXT,
            place TEXT,
            date DATE
        );
    """))

    conn.execute(text("""
        CREATE TABLE persons (
            person_id INTEGER PRIMARY KEY,
            aka TEXT NOT NULL,
            full_name TEXT,
            country TEXT,
            active BOOLEAN
        );
    """))

    conn.execute(text("""
        CREATE TABLE battles (
            battle_id INTEGER PRIMARY KEY,
            evento_id INTEGER REFERENCES events(evento_id),
            name TEXT,
            person_1_id INTEGER REFERENCES persons(person_id),
            person_2_id INTEGER REFERENCES persons(person_id),
            winner_id INTEGER REFERENCES persons(person_id),
            phase TEXT
        );
    """))

# Insertar datos
events_df.to_sql("events", engine, if_exists="append", index=False)
persons_df.to_sql("persons", engine, if_exists="append", index=False)
battles_df.to_sql("battles", engine, if_exists="append", index=False)

print("✅ Datos normalizados a minúsculas y cargados exitosamente en PostgreSQL.")
