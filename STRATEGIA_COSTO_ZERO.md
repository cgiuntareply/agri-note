# 💰 Strategia Tecnica "Costo Zero"

Questo documento descrive le scelte tecnologiche adottate per mantenere **zero costi operativi** nell'MVP di AgriNote.

## ✅ Tecnologie Implementate (Tutte Gratuite)

### 1. Database: SQLite → PostgreSQL (Supabase)

**Attuale (MVP Locale):**
- ✅ **SQLite** - Incluso in Python, zero configurazione
- ✅ File locale: `agrinote.db`
- ✅ Perfetto per sviluppo e test locali

**Futuro (Deploy Online):**
- 🔄 **Supabase Free Tier** (PostgreSQL)
  - 500 MB database storage
  - 2 GB bandwidth/mese
  - API auto-generate
  - Autenticazione integrata
  - **Costo: €0/mese**

**Migrazione:**
- Script di migrazione SQLite → PostgreSQL incluso
- Configurazione tramite variabili d'ambiente
- Zero downtime durante migrazione

### 2. Mappe: Leaflet.js + OpenStreetMap

**Implementato:**
- ✅ **Leaflet.js** (CDN gratuito)
- ✅ **OpenStreetMap** tiles (gratuite per sempre)
- ✅ Nessuna API key richiesta
- ✅ Nessun limite di chiamate
- ✅ Open source e community-driven

**Alternativa Scartata:**
- ❌ Google Maps (richiede API key, a pagamento dopo free tier)

**Vantaggi:**
- Mappe dettagliate per uso agricolo
- Possibilità di aggiungere layer personalizzati
- Nessun costo anche a scale elevate

### 3. OCR: PyMuPDF + Tesseract (Opzionale)

**Attuale (MVP):**
- ✅ **PyMuPDF (fitz)** - Estrazione testo da PDF nativi
- ✅ Funziona su PDF digitali (non scansionati)
- ✅ Zero costi, zero API calls
- ✅ Processamento locale

**Futuro (Opzionale):**
- 🔄 **Tesseract OCR** - Per PDF scansionati/immagini
  - Open source, gratuito
  - Richiede installazione locale: `brew install tesseract` (macOS) o `apt-get install tesseract-ocr` (Linux)
  - Nessun costo operativo

**Alternativa Scartata:**
- ❌ Google Vision API (€1.50 per 1000 immagini)
- ❌ AWS Textract (a pagamento)

**Nota:** Per l'MVP ci concentriamo su PDF digitali che sono più comuni nelle fatture moderne.

### 4. Meteo: Open-Meteo API

**Implementato:**
- ✅ **Open-Meteo API** - Completamente gratuito
- ✅ Nessuna API key richiesta
- ✅ Previsioni 7 giorni
- ✅ Dati storici disponibili
- ✅ Uso non commerciale illimitato

**Limiti Free Tier:**
- 10,000 richieste/giorno (più che sufficiente per MVP)
- Nessun costo anche per uso commerciale leggero

**Alternativa Scartata:**
- ❌ OpenWeatherMap (limite 60 chiamate/minuto nel free tier)
- ❌ Weather.com API (a pagamento)

## 📊 Riepilogo Costi

| Servizio | Costo Attuale | Costo Futuro (Scale) |
|----------|---------------|---------------------|
| Database | €0 (SQLite) | €0 (Supabase Free) |
| Mappe | €0 (OSM) | €0 (OSM) |
| OCR | €0 (PyMuPDF) | €0 (Tesseract) |
| Meteo | €0 (Open-Meteo) | €0 (Open-Meteo) |
| **TOTALE** | **€0/mese** | **€0/mese** |

## 🚀 Scalabilità Futura

### Quando Superare il Free Tier

**Supabase:**
- Oltre 500 MB database → €25/mese (Pro)
- Oltre 2 GB bandwidth → €25/mese (Pro)

**Open-Meteo:**
- Oltre 10k chiamate/giorno → Contattare per pricing enterprise

**Soluzioni:**
- Caching intelligente per ridurre chiamate API
- Compressione dati per ridurre storage
- Ottimizzazione query per ridurre bandwidth

## 🔧 Configurazione

Tutte le configurazioni sono in `main.py` e possono essere modificate tramite variabili d'ambiente:

```python
# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./agrinote.db")

# Meteo (coordinate default)
METEO_LAT = float(os.getenv("METEO_LAT", "45.4642"))  # Milano
METEO_LNG = float(os.getenv("METEO_LNG", "9.1900"))
```

## 📝 Note Implementative

### OCR Mockup Attuale

L'OCR attuale è un "mockup" che:
1. Estrae testo da PDF usando PyMuPDF
2. Cerca parole chiave per classificare prodotti
3. Non richiede machine learning o API esterne

**Miglioramenti Futuri:**
- Integrazione Tesseract per immagini
- Pattern matching più sofisticato
- Estrazione automatica quantità e prezzi

### Mappe

Leaflet.js supporta:
- Disegno poligoni (già implementato)
- Calcolo area (già implementato)
- Layer personalizzati (futuro: fogli catastali)
- Export/Import GeoJSON

**Futuro:**
- Integrazione fogli catastali (se disponibili come open data)
- Sovrapposizione Google Earth (richiede API key, opzionale)

## ✅ Conclusione

Tutte le tecnologie scelte sono:
- ✅ **Gratuite** per sempre (o con free tier generoso)
- ✅ **Open Source** (trasparenza e controllo)
- ✅ **Scalabili** (possibilità di upgrade quando necessario)
- ✅ **Affidabili** (usate da milioni di utenti)

**Zero costi operativi garantiti per l'MVP e oltre!** 🎉

