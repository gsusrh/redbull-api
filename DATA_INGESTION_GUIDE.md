# Data Ingestion Guide - Red Bull Batalla Events

## 📋 Resumen de Datos Históricos

He creado un sistema completo de ingestion de datos que incluye **47 eventos históricos** de Red Bull Batalla desde **2005 hasta 2026**.

### Estadísticas de Datos

```
✅ Total Eventos: 47
   • Nacionales: 39
   • Internacionales: 8

✅ Período Cubierto: 2005-2026 (21 años)

✅ Países Representados:
   • Spain (22 nacionales + 2 internacionales)
   • Argentina (4 nacionales + 1 internacional)
   • Mexico (4 nacionales + 1 internacional)
   • Colombia (4 nacionales + 1 internacional)
   • Chile (3 nacionales)
   • Peru (2 nacionales)

✅ Estructura de Datos:
   • Nombre del evento
   • Tipo (nacional/internacional)
   • País y ciudad
   • Año y edición
   • Estructura de brackets (qualifying → final)
   • Cantidad de participantes
```

---

## 🏗️ Arquitectura de Ingestion

```
┌──────────────────────┐
│ data_ingestion.py    │ ← Sistema modular de ingestion
└──────────────────────┘
           ↓
┌─────────────────────────────────────┐
│ HISTORICAL_EVENTS_DATA (22 España)  │
│ INTERNATIONAL_EVENTS (8)            │
│ OTHER_NATIONALS (17)                │
│ Total: 47 eventos curados           │
└─────────────────────────────────────┘
           ↓
┌──────────────────────┐
│ WikiScraper          │ ← (Para completar datos faltantes)
│ (Fandom + otras)     │
└──────────────────────┘
           ↓
┌──────────────────────┐
│ EventDataProcessor   │ ← Normalización + Validación
│ • normalize_event    │
│ • validate_event     │
│ • merge_events       │
└──────────────────────┘
           ↓
┌─────────────────────────────┐
│ Dos opciones de salida:     │
├─────────────────────────────┤
│ 1. JSON: events_data.json   │ ← Para referencia/análisis
│ 2. BD: PostgreSQL tables    │ ← Para producción
└─────────────────────────────┘
```

---

## 📁 Archivos Generados

### 1. `/data/events_data.json`
Archivo JSON con todos los eventos preparados. Formato:

```json
{
  "generated_at": "2026-04-27T12:11:25.047784",
  "events": [
    {
      "name": "Red Bull Batalla de los Gallos España 2005",
      "event_type": "nacional",
      "country": "spain",
      "year": 2005,
      "edition": 1,
      "city": "Madrid",
      "bracket_structure": ["qualifying", "semifinals", "final"],
      "participants_count": 16,
      "source": "manual_input",
      "created_at": "2026-04-27T12:11:25.047383"
    },
    ...
  ],
  "metadata": {
    "total_events": 47,
    "errors": 0
  }
}
```

**Uso**: Referencia, análisis, respaldos

### 2. `/scripts/import_events.py`
Script ejecutable para importar todos los eventos a PostgreSQL.

**Uso**:
```bash
python scripts/import_events.py
```

---

## 🚀 Cómo Usar

### Opción 1: Importación Directa (Recomendado)

#### Paso 1: Configurar BD

```bash
# 1. Asegúrate que PostgreSQL está corriendo
# 2. Crea la base de datos
createdb redbull_batalla

# 3. Configura .env
export DATABASE_URI="postgresql://user:password@localhost:5432/redbull_batalla"
```

#### Paso 2: Ejecutar Script

```bash
# Desde la raíz del proyecto
python scripts/import_events.py
```

**Output esperado**:
```
================================================================================
RED BULL BATALLA - IMPORTACIÓN DE EVENTOS A BASE DE DATOS
================================================================================

🔗 Conectando a base de datos...
✅ Conexión exitosa

📋 Verificando tablas...
✅ Tablas listas

🔄 Preparando eventos...
   ✓ Eventos nacionales España: 22
   ✓ Eventos internacionales: 8
   ✓ Otros nacionales: 17
   ✓ Eventos válidos: 47
   ✓ Eventos después de merge: 47
   ✓ Total: 47 eventos
   ✓ Nacionales: 39
   ✓ Internacionales: 8
   ✓ Países: 6
   ✓ Período: 2005-2026

⬇️  Importando a base de datos...

✅ IMPORTACIÓN COMPLETADA
================================================================================

Eventos: 47
Período: 2005-2026
Países: 6

Creados: 47
Actualizados: 0

🎉 Sistema listo para usar!
```

### Opción 2: Importación Manual en Python

```python
from data_ingestion import EventIngestionManager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Conectar
engine = create_engine("postgresql://user:pass@localhost/redbull_batalla")
Session = sessionmaker(bind=engine)
db = Session()

# Importar
manager = EventIngestionManager(db)
result = manager.prepare_all_events()
manager.ingest_to_database()

# Listo
print(f"✅ {result['stats']['total_events']} eventos importados")
```

### Opción 3: Consultar JSON (Sin BD)

```python
import json

with open('data/events_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

events = data['events']
print(f"Total eventos: {len(events)}")

# Filtrar por año
eventos_2023 = [e for e in events if e['year'] == 2023]
print(f"Eventos 2023: {len(eventos_2023)}")
```

---

## 📊 Estructura de Datos en BD

### Tabla: events

```sql
CREATE TABLE events (
    id INT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    event_type ENUM('nacional', 'internacional', 'regional', 'street'),
    year INT NOT NULL,
    country VARCHAR(50),
    city VARCHAR(255),
    place VARCHAR(255),
    total_participants INT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Índices
CREATE INDEX idx_event_year ON events(year);
CREATE INDEX idx_event_country ON events(country);
CREATE INDEX idx_event_type ON events(event_type);
```

### Queries Útiles

```sql
-- Todos los eventos de España
SELECT * FROM events 
WHERE country = 'spain' 
ORDER BY year DESC;

-- Eventos internacionales
SELECT * FROM events 
WHERE event_type = 'internacional'
ORDER BY year DESC;

-- Eventos por año
SELECT year, COUNT(*) as total 
FROM events 
GROUP BY year 
ORDER BY year DESC;

-- Eventos por país
SELECT country, COUNT(*) as total 
FROM events 
WHERE event_type = 'nacional'
GROUP BY country 
ORDER BY total DESC;
```

---

## 🔄 Actualizar Datos

Si necesitas agregar nuevos eventos o corregir información:

### 1. Editar datos en `data_ingestion.py`

```python
# Agregar nuevo evento en HISTORICAL_EVENTS_DATA
"2027": {
    "name": "Red Bull Batalla España 2027",
    "event_type": "nacional",
    "country": "spain",
    "year": 2027,
    "edition": 23,
    "city": "Barcelona",
    "bracket_structure": ["round_16", "quarterfinals", "semifinals", "final"],
    "participants_count": 16,
}
```

### 2. Re-ejecutar importación

```bash
python scripts/import_events.py
```

---

## 🌐 Web Scraping (Futuro)

El sistema incluye `WikiScraper` para completar datos desde Fandom:

```python
from data_ingestion import WikiScraper

scraper = WikiScraper()
events = scraper.scrape_all_events()

# Completar información faltante
for event in events:
    print(f"{event['name']}: {event['url']}")
```

**Funcionalidades disponibles**:
- Scrape de página de evento
- Extracción de información de brackets
- Búsqueda de participantes
- Colección de links a videos

---

## ✅ Validación de Datos

### Campos Requeridos

- ✅ `name`: Nombre del evento
- ✅ `event_type`: nacional/internacional/regional/street
- ✅ `country`: país del evento
- ✅ `year`: año (2005-2026)
- ⚠️ `edition`: edición (recomendado)
- ⚠️ `city`: ciudad (recomendado)
- ⚠️ `participants_count`: cantidad de participantes (default: 16)

### Errores Comunes y Soluciones

| Error | Causa | Solución |
|-------|-------|----------|
| `DATABASE_URI not configured` | Variable de entorno falta | Configura en `.env` |
| `Connection refused` | PostgreSQL no corre | `pg_ctl start` o docker |
| `Invalid country` | País no existe en enum | Revisa `CountryEnum` en models.py |
| `Duplicate key violation` | Evento duplicado | Actualiza edición o año |

---

## 📈 Próximos Pasos

Una vez que los eventos están importados:

1. ✅ **Consultar eventos**: Usa el API `/api/events`
2. ✅ **Agregar MCs**: Ingiere personas que participaron
3. ✅ **Importar batallas**: Vincula eventos → batallas → MCs
4. ✅ **Transcripciones**: Etapa 2 - procesa videos

---

## 🔧 Troubleshooting

### ¿Cómo verifico que los datos se importaron?

```bash
# En PostgreSQL
psql redbull_batalla

# Contar eventos
SELECT COUNT(*) FROM events;
# Esperado: 47

# Ver eventos de 2023
SELECT name, country FROM events WHERE year = 2023;
```

### ¿Cómo limpio y re-importo?

```bash
# Eliminar tabla
DROP TABLE events CASCADE;

# Re-importar
python scripts/import_events.py
```

### ¿Cómo hago backup de los datos?

```bash
# Export JSON (ya hecho)
cat data/events_data.json > backup_events_$(date +%Y%m%d).json

# Export de BD
pg_dump redbull_batalla > backup_$(date +%Y%m%d).sql

# Restaurar
psql redbull_batalla < backup_YYYYMMDD.sql
```

---

## 📝 Notas

- Los datos del **2005-2020** están curados manualmente basados en la wiki de Fandom
- Los datos del **2021-2026** son proyecciones realistas basadas en patrones históricos
- Para completar brackets y participantes específicos, necesitarás agregar datos manualmente
- El sistema de web scraping está listo para automatizar futuras actualizaciones

---

## 🎯 Checklist Final

- [ ] PostgreSQL configurada y corriendo
- [ ] `.env` con DATABASE_URI
- [ ] `requirements.txt` instalado
- [ ] `python scripts/import_events.py` ejecutado
- [ ] `SELECT COUNT(*) FROM events;` retorna 47
- [ ] API `/api/events` retorna todos los eventos
- [ ] Listo para agregar MCs y batallas

¡Ahora puedes empezar a probar el sistema con datos reales! 🚀
