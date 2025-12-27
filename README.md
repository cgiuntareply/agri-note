# 🌾 AgriNote - Gestionale Agricolo MVP

Web App gestionale agricola sviluppata con Python, FastAPI e Jinja2 per la gestione di aziende agricole secondo la normativa italiana.

## 💰 Strategia "Costo Zero"

AgriNote è progettato con una **strategia tecnica a costo zero**, utilizzando solo tecnologie Open Source e Free Tier:

- ✅ **Database**: SQLite (locale) → Supabase Free Tier (online)
- ✅ **Mappe**: Leaflet.js + OpenStreetMap (gratuite per sempre)
- ✅ **OCR**: PyMuPDF (PDF nativi) + Tesseract opzionale (immagini)
- ✅ **Meteo**: Open-Meteo API (gratuito, illimitato per uso non commerciale)

Vedi [STRATEGIA_COSTO_ZERO.md](STRATEGIA_COSTO_ZERO.md) per dettagli completi.

## 📋 Caratteristiche

- **Dashboard** con scadenze mezzi e widget meteo
- **Mappa Campi** interattiva con Leaflet.js per disegnare e salvare poligoni
- **Magazzino Smart** con upload fatture PDF e analisi automatica (OCR mockup)
- **Quaderno di Campagna** con calcolo automatico delle quantità totali

## 🛠️ Stack Tecnologico

- **Backend**: Python 3.10+, FastAPI
- **Database**: SQLite con SQLAlchemy
- **Frontend**: Jinja2 Templates, TailwindCSS (CDN)
- **Mappe**: Leaflet.js con OpenStreetMap
- **Meteo**: Open-Meteo API (gratuita)

## 🚀 Installazione

### 1. Clona o scarica il progetto

```bash
cd agri-note
```

### 2. Crea un ambiente virtuale (consigliato)

```bash
python3 -m venv venv
source venv/bin/activate  # Su Windows: venv\Scripts\activate
```

### 3. Installa le dipendenze

```bash
pip install -r requirements.txt
```

### 4. Inizializza il database e popola con dati di prova

```bash
python seed.py
```

**Nota**: Se hai già un database esistente e hai aggiornato il codice, esegui prima la migrazione:

```bash
python migrate_db.py
```

Questo creerà:
- Un utente di prova: `admin` / `admin123`
- Un'azienda di esempio
- 3 campi
- 4 prodotti (fitofarmaci e concimi)
- 3 mezzi con scadenze
- 2 trattamenti di esempio

### 5. Avvia il server

```bash
python main.py
```

Oppure con uvicorn direttamente:

```bash
uvicorn main:app --reload
```

### 6. Apri il browser

Vai su: http://localhost:8000

## 📁 Struttura Progetto

```
agri-note/
├── main.py              # Applicazione FastAPI principale
├── models.py            # Modelli SQLAlchemy
├── seed.py              # Script per popolare il database
├── requirements.txt     # Dipendenze Python
├── agrinote.db          # Database SQLite (creato automaticamente)
├── templates/           # Template HTML Jinja2
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   ├── mappa.html
│   ├── magazzino.html
│   └── quaderno.html
└── static/              # File statici
    └── uploads/         # PDF caricati (creato automaticamente)
```

## 🎯 Funzionalità Principali

### Dashboard
- Visualizzazione dati azienda
- Widget meteo (Milano, Italia)
- Scadenze mezzi (prossimi 30 giorni)
- Statistiche rapide (campi, prodotti, mezzi)

### Mappa Campi
- Mappa interattiva OpenStreetMap
- Disegno poligoni cliccando sulla mappa
- Calcolo automatico superficie in ettari
- Salvataggio campi con coordinate

### Magazzino
- Upload fatture PDF
- Analisi automatica testo (OCR mockup)
- Classificazione automatica: Fitofarmaco/Concime
- Gestione inventario prodotti

### Quaderno di Campagna
- Form per registrare trattamenti
- Calcolo automatico: `Quantità Totale = Dose/ha × Ettari`
- Tabella conforme ad Allegato A/B normativa italiana
- Filtri per campo, prodotto, data

## 🔐 Credenziali Default

- **Username**: `admin`
- **Password**: `admin123`

⚠️ **Importante**: Cambia le credenziali in produzione!

## 📝 Note Tecniche

### Calcolo Area Poligono
Il sistema usa una formula Shoelace semplificata per calcolare l'area approssimativa dei poligoni disegnati sulla mappa. La conversione in ettari è approssimativa (basata su coordinate geografiche medie italiane).

### OCR Mockup
L'analisi PDF è un mockup che cerca parole chiave nel testo estratto:
- **Fitofarmaci**: "fungicida", "insetticida", "erbicida", "glifosato", "roundup"
- **Concimi**: "urea", "nitrato", "ammoniacale", "fosfato", "potassio", "npk"

In produzione, considera l'integrazione con servizi OCR reali (es. Tesseract, Google Vision API).

### Database
Il database SQLite viene creato automaticamente al primo avvio. Per ricrearlo da zero, elimina il file `agrinote.db` e riesegui `seed.py`.

## 🐛 Troubleshooting

### Errore "Module not found"
Assicurati di aver attivato l'ambiente virtuale e installato tutte le dipendenze:
```bash
pip install -r requirements.txt
```

### Errore "Port already in use"
Cambia la porta in `main.py`:
```python
uvicorn.run(app, host="0.0.0.0", port=8001)
```

### PDF non analizzato correttamente
L'OCR mockup è limitato. Assicurati che il PDF contenga testo (non solo immagini). Per PDF scansionati, considera l'integrazione con Tesseract OCR.

## 📄 Licenza

Questo progetto è rilasciato sotto licenza MIT. Vedi [LICENSE](LICENSE) per dettagli.

## 🚀 Deploy su GitHub

Per pubblicare il progetto su GitHub:

```bash
# 1. Inizializza Git (se non già fatto)
git init

# 2. Aggiungi tutti i file
git add .

# 3. Crea il primo commit
git commit -m "Initial commit: AgriNote MVP - Gestionale Agricolo"

# 4. Crea un nuovo repository su GitHub (senza README, .gitignore, o license)

# 5. Aggiungi il remote e fai push
git remote add origin https://github.com/TUO_USERNAME/agri-note.git
git branch -M main
git push -u origin main
```

## 📦 Repository GitHub

Se vuoi contribuire o segnalare bug, apri una issue su GitHub!

---

**AgriNote** - Gestione Agricola Semplificata 🌾

## 👨‍💻 Sviluppo

Per contribuire o estendere il progetto:
1. Aggiungi nuove funzionalità in `main.py`
2. Estendi i modelli in `models.py` se necessario
3. Crea nuovi template in `templates/`
4. Aggiorna `seed.py` per includere nuovi dati di prova

---

**AgriNote** - Gestione Agricola Semplificata 🌾

