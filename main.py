"""
AgriNote - Web App Gestionale Agricola
FastAPI Backend con Jinja2 Templates
"""
from fastapi import FastAPI, Request, Depends, HTTPException, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import date, datetime, timedelta
from contextlib import asynccontextmanager
import json
import httpx
import fitz  # PyMuPDF
import os
from typing import Optional

from models import (
    Base, engine, SessionLocal, get_db,
    User, Azienda, Campo, Prodotto, Mezzo, Trattamento, TipoProdotto, InterventoManutenzione
)

# Configurazione
try:
    from config import SECRET_KEY, ALGORITHM, METEO_LAT, METEO_LNG
except ImportError:
    # Fallback se config.py non esiste
    SECRET_KEY = "agrinote-secret-key-change-in-production"
    ALGORITHM = "HS256"
    METEO_LAT = 45.4642
    METEO_LNG = 9.1900

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Lifespan Events (sostituisce on_event deprecato)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: inizializza database
    from models import Base, engine
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown: cleanup se necessario (opzionale)


# FastAPI App
app = FastAPI(title="AgriNote", lifespan=lifespan)

# Templates e Static Files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Crea directory se non esistono
os.makedirs("static/uploads", exist_ok=True)
os.makedirs("templates", exist_ok=True)


# Utility Functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica password"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash password"""
    return pwd_context.hash(password)


def create_access_token(data: dict):
    """Crea JWT token"""
    to_encode = data.copy()
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(request: Request, db: Session = Depends(get_db)) -> Optional[User]:
    """Ottiene l'utente corrente dalla sessione"""
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
    except JWTError:
        return None
    
    user = db.query(User).filter(User.username == username).first()
    return user


def require_auth(request: Request, db: Session = Depends(get_db)) -> User:
    """Richiede autenticazione, altrimenti solleva eccezione"""
    user = get_current_user(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="Non autenticato")
    return user


# Calcolo area poligono (formula Shoelace con conversione precisa)
def calcola_area_poligono(coordinate: list) -> float:
    """Calcola area in ettari da coordinate poligono (lat, lng)"""
    import math
    
    if len(coordinate) < 3:
        print(f"ERRORE: Coordinate insufficienti: {len(coordinate)} punti")
        return 0.0
    
    # Verifica formato coordinate
    try:
        # Assicurati che le coordinate siano nel formato [lat, lng]
        coord_validate = []
        for p in coordinate:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                coord_validate.append([float(p[0]), float(p[1])])
            else:
                raise ValueError(f"Formato coordinata non valido: {p}")
        
        if len(coord_validate) < 3:
            print(f"ERRORE: Coordinate validate insufficienti: {len(coord_validate)} punti")
            return 0.0
        
        coordinate = coord_validate
    except (ValueError, TypeError) as e:
        print(f"ERRORE validazione coordinate: {e}")
        print(f"Coordinate ricevute: {coordinate}")
        return 0.0
    
    # Calcola latitudine media per conversione precisa
    lat_media = sum(p[0] for p in coordinate) / len(coordinate)
    
    # Metri per grado di latitudine (costante)
    metri_per_grado_lat = 111320.0
    
    # Metri per grado di longitudine (dipende dalla latitudine)
    metri_per_grado_lng = 111320.0 * math.cos(math.radians(lat_media))
    
    # Formula Shoelace per area poligono (in gradi²)
    # IMPORTANTE: coordinate[i] = [lat, lng] = [y, x]
    # Formula Shoelace: sum(x_i * y_{i+1} - x_{i+1} * y_i) / 2
    # dove x = longitudine (lng), y = latitudine (lat)
    area_gradi2 = 0.0
    n = len(coordinate)
    
    print(f"DEBUG calcola_area: Calcolo con {n} punti")
    print(f"DEBUG calcola_area: Primo punto: {coordinate[0]}")
    print(f"DEBUG calcola_area: Ultimo punto: {coordinate[-1]}")
    
    for i in range(n):
        j = (i + 1) % n
        # x_i * y_{i+1} - x_{i+1} * y_i
        # lng_i * lat_{i+1} - lng_{i+1} * lat_i
        term = coordinate[i][1] * coordinate[j][0] - coordinate[j][1] * coordinate[i][0]
        area_gradi2 += term
        if i < 3:  # Debug primi 3 termini
            print(f"DEBUG: Termine {i}: lng[{i}]={coordinate[i][1]:.6f} * lat[{j}]={coordinate[j][0]:.6f} - lng[{j}]={coordinate[j][1]:.6f} * lat[{i}]={coordinate[i][0]:.6f} = {term:.10f}")
    
    area_gradi2 = abs(area_gradi2) / 2.0
    
    print(f"DEBUG calcola_area: Area in gradi²: {area_gradi2:.12f}")
    
    # Se l'area è troppo piccola, potrebbe essere un errore
    if area_gradi2 < 1e-12:
        print(f"WARNING: Area in gradi² troppo piccola: {area_gradi2:.15f}")
        print(f"WARNING: Coordinate potrebbero essere errate o poligono troppo piccolo")
        return 0.0
    
    # Conversione da gradi² a metri²
    # 1 grado² = (metri_per_grado_lat * metri_per_grado_lng) metri²
    area_metri2 = area_gradi2 * metri_per_grado_lat * metri_per_grado_lng
    
    print(f"DEBUG calcola_area: Area in metri²: {area_metri2:.2f}")
    
    # Conversione da metri² a ettari (1 ettaro = 10,000 m²)
    area_ettari = area_metri2 / 10000.0
    
    result = round(area_ettari, 2)
    print(f"DEBUG calcola_area: Area finale: {result} ettari")
    
    return result


# OCR Mockup - Estrazione testo da PDF
def analizza_fattura_pdf(file_path: str) -> dict:
    """Analizza PDF fattura e estrae informazioni prodotto"""
    doc = fitz.open(file_path)
    testo_completo = ""
    
    for page in doc:
        testo_completo += page.get_text()
    
    doc.close()
    
    testo_lower = testo_completo.lower()
    
    # Parole chiave per classificazione
    concimi_keywords = ["urea", "nitrato", "ammoniacale", "fosfato", "potassio", "npk", "concime"]
    fitofarmaci_keywords = ["fungicida", "insetticida", "erbicida", "glifosato", "roundup", "fitofarmaco"]
    
    # Determina tipo
    tipo = None
    if any(keyword in testo_lower for keyword in fitofarmaci_keywords):
        tipo = TipoProdotto.FITOFARMACO
    elif any(keyword in testo_lower for keyword in concimi_keywords):
        tipo = TipoProdotto.CONCIME
    
    # Estrai nome prodotto (cerca righe con caratteristiche prodotto)
    nome_prodotto = "Prodotto da Fattura"
    righe = testo_completo.split("\n")
    for riga in righe:
        if len(riga) > 5 and len(riga) < 50:
            if any(char.isupper() for char in riga[:10]):
                nome_prodotto = riga.strip()
                break
    
    return {
        "nome": nome_prodotto,
        "tipo": tipo,
        "testo_estratto": testo_completo[:500]  # Primi 500 caratteri
    }


# API Meteo (Open-Meteo - Gratuita)
async def get_meteo(lat: float = None, lng: float = None) -> dict:
    """Ottiene dati meteo da Open-Meteo API"""
    if lat is None:
        lat = METEO_LAT
    if lng is None:
        lng = METEO_LNG
    """Ottiene dati meteo da Open-Meteo API"""
    try:
        async with httpx.AsyncClient() as client:
            url = f"https://api.open-meteo.com/v1/forecast"
            params = {
                "latitude": lat,
                "longitude": lng,
                "current": "temperature_2m,weather_code",
                "timezone": "Europe/Rome"
            }
            response = await client.get(url, params=params, timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                current = data.get("current", {})
                return {
                    "temperatura": current.get("temperature_2m", "N/A"),
                    "codice_meteo": current.get("weather_code", 0)
                }
    except Exception as e:
        print(f"Errore meteo: {e}")
    return {"temperatura": "N/A", "codice_meteo": 0}


# ROUTES

# Database initialization è ora gestito nel lifespan handler (riga 40-46)


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Redirect a login se non autenticato, altrimenti dashboard"""
    user = get_current_user(request, next(get_db()))
    if user:
        return RedirectResponse(url="/dashboard", status_code=303)
    return RedirectResponse(url="/login", status_code=303)


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Pagina login"""
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
async def login(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Endpoint login"""
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Credenziali non valide")
    
    access_token = create_access_token(data={"sub": user.username})
    response = RedirectResponse(url="/dashboard", status_code=303)
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return response


@app.get("/logout")
async def logout():
    """Logout"""
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie(key="access_token")
    return response


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    """Dashboard principale"""
    user = require_auth(request, db)
    
    # Ottieni azienda dell'utente
    oggi = date.today()
    azienda = db.query(Azienda).filter(Azienda.user_id == user.id).first()
    if not azienda:
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "user": user,
            "azienda": None,
            "scadenze": [],
            "meteo": {"temperatura": "N/A"},
            "oggi": oggi
        })
    
    # Scadenze mezzi (prossimi 30 giorni)
    oggi = date.today()
    scadenza_limite = oggi + timedelta(days=30)
    mezzi_scadenti = db.query(Mezzo).filter(
        Mezzo.azienda_id == azienda.id,
        Mezzo.data_revisione <= scadenza_limite,
        Mezzo.data_revisione >= oggi
    ).order_by(Mezzo.data_revisione).all()
    
    # Meteo con alert
    meteo_data = await get_meteo_esteso()
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": user,
        "azienda": azienda,
        "scadenze": mezzi_scadenti,
        "meteo": meteo_data,
        "oggi": oggi
    })


@app.get("/mappa", response_class=HTMLResponse)
async def mappa(request: Request, campo_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Pagina mappa campi"""
    user = require_auth(request, db)
    azienda = db.query(Azienda).filter(Azienda.user_id == user.id).first()
    
    if not azienda:
        raise HTTPException(status_code=404, detail="Azienda non trovata")
    
    campi = db.query(Campo).filter(Campo.azienda_id == azienda.id).all()
    
    # Se è specificato un campo_id, carica quel campo per visualizzarlo
    campo_selezionato = None
    if campo_id:
        campo_selezionato = db.query(Campo).filter(
            Campo.id == campo_id,
            Campo.azienda_id == azienda.id
        ).first()
    
    # Prepara dati campi con superficie per il template
    campi_data = []
    for campo in campi:
        campi_data.append({
            "id": campo.id,
            "nome": campo.nome,
            "superficie_ettari": campo.superficie_ettari,
            "coltura_attuale": campo.coltura_attuale,
            "centro_lat": campo.centro_lat,
            "centro_lng": campo.centro_lng,
            "coordinate_poligono": campo.coordinate_poligono
        })
    
    return templates.TemplateResponse("mappa.html", {
        "request": request,
        "user": user,
        "azienda": azienda,
        "campi": campi_data,
        "campo_selezionato": campo_selezionato
    })


@app.post("/api/campo/salva")
async def salva_campo(
    request: Request,
    nome: str = Form(...),
    coordinate: str = Form(...),
    coltura: str = Form(None),
    db: Session = Depends(get_db)
):
    """Salva nuovo campo dalla mappa"""
    user = require_auth(request, db)
    azienda = db.query(Azienda).filter(Azienda.user_id == user.id).first()
    
    if not azienda:
        raise HTTPException(status_code=404, detail="Azienda non trovata")
    
    try:
        coord_list = json.loads(coordinate)
        
        # Debug: verifica coordinate
        if not coord_list or len(coord_list) < 3:
            raise HTTPException(status_code=400, detail="Coordinate non valide: servono almeno 3 punti")
        
        # Verifica formato coordinate: devono essere [lat, lng]
        if not isinstance(coord_list[0], list) or len(coord_list[0]) != 2:
            raise HTTPException(status_code=400, detail="Formato coordinate non valido: atteso [[lat, lng], ...]")
        
        # Debug logging
        print(f"DEBUG salva_campo: Ricevute {len(coord_list)} coordinate")
        print(f"DEBUG salva_campo: Primo punto: {coord_list[0]}")
        
        # Calcola superficie
        superficie = calcola_area_poligono(coord_list)
        
        print(f"DEBUG salva_campo: Superficie calcolata: {superficie} ettari")
        
        if superficie <= 0:
            print(f"WARNING: Superficie calcolata è 0 o negativa!")
            print(f"DEBUG: Coordinate complete: {coord_list}")
            # Ricalcola per debug
            import math
            lat_media = sum(p[0] for p in coord_list) / len(coord_list)
            print(f"DEBUG: Latitudine media: {lat_media}")
            
            # Ricalcola manualmente per debug
            area_gradi2 = 0.0
            n = len(coord_list)
            for i in range(n):
                j = (i + 1) % n
                area_gradi2 += coord_list[i][1] * coord_list[j][0]
                area_gradi2 -= coord_list[j][1] * coord_list[i][0]
            area_gradi2 = abs(area_gradi2) / 2.0
            print(f"DEBUG: Area in gradi²: {area_gradi2}")
            
            metri_per_grado_lat = 111320.0
            metri_per_grado_lng = 111320.0 * math.cos(math.radians(lat_media))
            area_metri2 = area_gradi2 * metri_per_grado_lat * metri_per_grado_lng
            print(f"DEBUG: Area in metri²: {area_metri2}")
            superficie = area_metri2 / 10000.0
            print(f"DEBUG: Superficie ricalcolata: {superficie} ettari")
        
        # Calcola centro del poligono (centroide)
        centro_lat = sum(p[0] for p in coord_list) / len(coord_list)
        centro_lng = sum(p[1] for p in coord_list) / len(coord_list)
        
        campo = Campo(
            azienda_id=azienda.id,
            nome=nome,
            superficie_ettari=superficie,
            coordinate_poligono=coord_list,
            centro_lat=centro_lat,
            centro_lng=centro_lng,
            coltura_attuale=coltura
        )
        db.add(campo)
        db.commit()
        db.refresh(campo)
        
        print(f"DEBUG salva_campo: Campo salvato con superficie: {campo.superficie_ettari} ettari")
        
        return {"success": True, "campo_id": campo.id, "superficie": superficie}
    except json.JSONDecodeError as e:
        db.rollback()
        print(f"ERRORE JSON: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Errore parsing coordinate: {str(e)}")
    except Exception as e:
        db.rollback()
        print(f"ERRORE salvataggio campo: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"Errore: {str(e)}")


@app.post("/api/campo/{campo_id}/elimina")
async def elimina_campo(
    campo_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Elimina un campo"""
    user = require_auth(request, db)
    azienda = db.query(Azienda).filter(Azienda.user_id == user.id).first()
    
    if not azienda:
        raise HTTPException(status_code=404, detail="Azienda non trovata")
    
    # Verifica che il campo appartenga all'azienda
    campo = db.query(Campo).filter(
        Campo.id == campo_id,
        Campo.azienda_id == azienda.id
    ).first()
    
    if not campo:
        raise HTTPException(status_code=404, detail="Campo non trovato")
    
    try:
        nome_campo = campo.nome
        
        # Elimina prima i trattamenti associati (se cascade non funziona)
        from models import Trattamento
        trattamenti = db.query(Trattamento).filter(Trattamento.campo_id == campo_id).all()
        for trattamento in trattamenti:
            db.delete(trattamento)
        
        # Elimina il campo
        db.delete(campo)
        db.commit()
        
        print(f"✅ Campo '{nome_campo}' (ID: {campo_id}) eliminato con successo")
        return {"success": True, "message": f"Campo '{nome_campo}' eliminato con successo"}
    except Exception as e:
        db.rollback()
        print(f"ERRORE eliminazione campo: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"Errore durante l'eliminazione: {str(e)}")


@app.get("/magazzino", response_class=HTMLResponse)
async def magazzino(request: Request, db: Session = Depends(get_db)):
    """Pagina magazzino prodotti"""
    user = require_auth(request, db)
    azienda = db.query(Azienda).filter(Azienda.user_id == user.id).first()
    
    if not azienda:
        raise HTTPException(status_code=404, detail="Azienda non trovata")
    
    prodotti = db.query(Prodotto).filter(Prodotto.azienda_id == azienda.id).all()
    
    return templates.TemplateResponse("magazzino.html", {
        "request": request,
        "user": user,
        "azienda": azienda,
        "prodotti": prodotti
    })


@app.post("/magazzino/upload")
async def upload_fattura(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload e analisi fattura PDF"""
    user = require_auth(request, db)
    azienda = db.query(Azienda).filter(Azienda.user_id == user.id).first()
    
    if not azienda:
        raise HTTPException(status_code=404, detail="Azienda non trovata")
    
    # Salva file
    file_path = f"static/uploads/{file.filename}"
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # Analizza PDF
    risultato = analizza_fattura_pdf(file_path)
    
    if risultato["tipo"]:
        # Crea prodotto
        prodotto = Prodotto(
            azienda_id=azienda.id,
            nome_commerciale=risultato["nome"],
            tipo=risultato["tipo"],
            quantita_disponibile=0.0,  # Da inserire manualmente
            unita_misura="kg"
        )
        db.add(prodotto)
        db.commit()
    
    return RedirectResponse(url="/magazzino", status_code=303)


@app.post("/magazzino/prodotto/nuovo")
async def nuovo_prodotto(
    request: Request,
    nome_commerciale: str = Form(...),
    tipo: str = Form(...),
    quantita: float = Form(...),
    unita: str = Form(...),
    db: Session = Depends(get_db)
):
    """Crea nuovo prodotto manualmente"""
    user = require_auth(request, db)
    azienda = db.query(Azienda).filter(Azienda.user_id == user.id).first()
    
    if not azienda:
        raise HTTPException(status_code=404, detail="Azienda non trovata")
    
    tipo_enum = TipoProdotto.FITOFARMACO if tipo == "Fitofarmaco" else TipoProdotto.CONCIME
    
    prodotto = Prodotto(
        azienda_id=azienda.id,
        nome_commerciale=nome_commerciale,
        tipo=tipo_enum,
        quantita_disponibile=quantita,
        unita_misura=unita
    )
    db.add(prodotto)
    db.commit()
    
    return RedirectResponse(url="/magazzino", status_code=303)


@app.get("/quaderno", response_class=HTMLResponse)
async def quaderno(request: Request, db: Session = Depends(get_db)):
    """Pagina quaderno di campagna"""
    user = require_auth(request, db)
    azienda = db.query(Azienda).filter(Azienda.user_id == user.id).first()
    
    if not azienda:
        raise HTTPException(status_code=404, detail="Azienda non trovata")
    
    campi = db.query(Campo).filter(Campo.azienda_id == azienda.id).all()
    prodotti = db.query(Prodotto).filter(Prodotto.azienda_id == azienda.id).all()
    
    # Query trattamenti con gestione errori per dati vecchi
    try:
        trattamenti = db.query(Trattamento).join(Campo).filter(
            Campo.azienda_id == azienda.id
        ).order_by(Trattamento.data.desc()).all()
    except Exception as e:
        print(f"WARNING: Errore query trattamenti: {e}")
        # Fallback: query diretta e filtraggio manuale
        tutti_trattamenti = db.query(Trattamento).all()
        trattamenti = []
        for tr in tutti_trattamenti:
            try:
                if tr.campo and tr.campo.azienda_id == azienda.id:
                    trattamenti.append(tr)
            except:
                # Trattamento orfano, salta
                pass
        trattamenti.sort(key=lambda x: x.data, reverse=True)
    
    return templates.TemplateResponse("quaderno.html", {
        "request": request,
        "user": user,
        "azienda": azienda,
        "campi": campi,
        "prodotti": prodotti,
        "trattamenti": trattamenti,
        "oggi": date.today()
    })


@app.post("/quaderno/trattamento/nuovo")
async def nuovo_trattamento(
    request: Request,
    campo_id: int = Form(...),
    data: str = Form(...),
    prodotto_id: int = Form(...),
    avversita: str = Form(None),
    quantita_per_ettaro: float = Form(...),
    operatore: str = Form(None),
    db: Session = Depends(get_db)
):
    """Crea nuovo trattamento"""
    user = require_auth(request, db)
    azienda = db.query(Azienda).filter(Azienda.user_id == user.id).first()
    
    if not azienda:
        raise HTTPException(status_code=404, detail="Azienda non trovata")
    
    # Verifica campo appartiene all'azienda
    campo = db.query(Campo).filter(
        Campo.id == campo_id,
        Campo.azienda_id == azienda.id
    ).first()
    
    if not campo:
        raise HTTPException(status_code=404, detail="Campo non trovato")
    
    # Calcola quantità totale
    quantita_totale = quantita_per_ettaro * campo.superficie_ettari
    
    # Parsing data
    data_obj = datetime.strptime(data, "%Y-%m-%d").date()
    
    trattamento = Trattamento(
        campo_id=campo_id,
        data=data_obj,
        prodotto_id=prodotto_id,
        avversita=avversita,
        quantita_per_ettaro=quantita_per_ettaro,
        quantita_totale=quantita_totale,
        operatore=operatore
    )
    db.add(trattamento)
    db.commit()
    
    return RedirectResponse(url="/quaderno", status_code=303)


@app.post("/quaderno/trattamento/{trattamento_id}/elimina")
async def elimina_trattamento(
    trattamento_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Elimina un trattamento"""
    user = require_auth(request, db)
    azienda = db.query(Azienda).filter(Azienda.user_id == user.id).first()
    
    if not azienda:
        raise HTTPException(status_code=404, detail="Azienda non trovata")
    
    try:
        # Verifica che il trattamento appartenga a un campo dell'azienda
        # Usa outerjoin per gestire anche trattamenti orfani
        trattamento = db.query(Trattamento).join(Campo, Trattamento.campo_id == Campo.id).filter(
            Trattamento.id == trattamento_id,
            Campo.azienda_id == azienda.id
        ).first()
        
        # Se non trovato con join, prova a cercare direttamente (per gestire dati vecchi)
        if not trattamento:
            trattamento = db.query(Trattamento).filter(
                Trattamento.id == trattamento_id
            ).first()
            
            # Se esiste ma non ha campo valido, eliminalo comunque (dato orfano)
            if trattamento:
                print(f"WARNING: Trattamento {trattamento_id} trovato ma senza campo valido - eliminazione forzata")
            else:
                raise HTTPException(status_code=404, detail="Trattamento non trovato")
        
        # Elimina il trattamento
        db.delete(trattamento)
        db.commit()
        
        print(f"✅ Trattamento ID {trattamento_id} eliminato con successo")
        return {"success": True, "message": "Trattamento eliminato con successo"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"ERRORE eliminazione trattamento: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"Errore durante l'eliminazione: {str(e)}")


@app.get("/api/campo/{campo_id}/ettari")
async def get_ettari_campo(
    campo_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """API per ottenere ettari di un campo"""
    user = require_auth(request, db)
    azienda = db.query(Azienda).filter(Azienda.user_id == user.id).first()
    
    campo = db.query(Campo).filter(
        Campo.id == campo_id,
        Campo.azienda_id == azienda.id
    ).first()
    
    if not campo:
        raise HTTPException(status_code=404, detail="Campo non trovato")
    
    return {"ettari": campo.superficie_ettari}


# ========== GESTIONE AZIENDA ==========

@app.get("/azienda/modifica", response_class=HTMLResponse)
async def modifica_azienda_page(request: Request, db: Session = Depends(get_db)):
    """Pagina modifica dati azienda"""
    user = require_auth(request, db)
    azienda = db.query(Azienda).filter(Azienda.user_id == user.id).first()
    
    if not azienda:
        raise HTTPException(status_code=404, detail="Azienda non trovata")
    
    return templates.TemplateResponse("azienda_modifica.html", {
        "request": request,
        "user": user,
        "azienda": azienda
    })


@app.post("/azienda/modifica")
async def modifica_azienda(
    request: Request,
    ragione_sociale: str = Form(...),
    p_iva: str = Form(...),
    indirizzo: str = Form(...),
    legale_rappresentante: str = Form(...),
    db: Session = Depends(get_db)
):
    """Salva modifiche azienda"""
    user = require_auth(request, db)
    azienda = db.query(Azienda).filter(Azienda.user_id == user.id).first()
    
    if not azienda:
        raise HTTPException(status_code=404, detail="Azienda non trovata")
    
    # Verifica P.IVA univoca (se cambiata)
    if azienda.p_iva != p_iva:
        existing = db.query(Azienda).filter(Azienda.p_iva == p_iva).first()
        if existing:
            raise HTTPException(status_code=400, detail="P.IVA già esistente")
    
    azienda.ragione_sociale = ragione_sociale
    azienda.p_iva = p_iva
    azienda.indirizzo = indirizzo
    azienda.legale_rappresentante = legale_rappresentante
    
    db.commit()
    
    return RedirectResponse(url="/dashboard", status_code=303)


# ========== GESTIONE MEZZI ==========

@app.get("/mezzi", response_class=HTMLResponse)
async def mezzi_page(request: Request, db: Session = Depends(get_db)):
    """Pagina gestione mezzi"""
    user = require_auth(request, db)
    azienda = db.query(Azienda).filter(Azienda.user_id == user.id).first()
    
    if not azienda:
        raise HTTPException(status_code=404, detail="Azienda non trovata")
    
    mezzi = db.query(Mezzo).filter(Mezzo.azienda_id == azienda.id).all()
    
    return templates.TemplateResponse("mezzi.html", {
        "request": request,
        "user": user,
        "azienda": azienda,
        "mezzi": mezzi,
        "oggi": date.today()
    })


@app.post("/mezzi/nuovo")
async def nuovo_mezzo(
    request: Request,
    nome: str = Form(...),
    targa: str = Form(None),
    data_revisione: str = Form(...),
    tipo_mezzo: str = Form(None),
    marca: str = Form(None),
    modello: str = Form(None),
    anno_acquisto: int = Form(None),
    note_manutenzione: str = Form(None),
    db: Session = Depends(get_db)
):
    """Crea nuovo mezzo"""
    user = require_auth(request, db)
    azienda = db.query(Azienda).filter(Azienda.user_id == user.id).first()
    
    if not azienda:
        raise HTTPException(status_code=404, detail="Azienda non trovata")
    
    data_rev = datetime.strptime(data_revisione, "%Y-%m-%d").date()
    
    mezzo = Mezzo(
        azienda_id=azienda.id,
        nome=nome,
        targa=targa,
        data_revisione=data_rev,
        tipo_mezzo=tipo_mezzo,
        marca=marca,
        modello=modello,
        anno_acquisto=anno_acquisto,
        note_manutenzione=note_manutenzione
    )
    db.add(mezzo)
    db.commit()
    
    return RedirectResponse(url="/mezzi", status_code=303)


@app.post("/mezzi/{mezzo_id}/modifica")
async def modifica_mezzo(
    mezzo_id: int,
    request: Request,
    nome: str = Form(...),
    targa: str = Form(None),
    data_revisione: str = Form(...),
    tipo_mezzo: str = Form(None),
    marca: str = Form(None),
    modello: str = Form(None),
    anno_acquisto: int = Form(None),
    note_manutenzione: str = Form(None),
    db: Session = Depends(get_db)
):
    """Modifica mezzo esistente"""
    user = require_auth(request, db)
    azienda = db.query(Azienda).filter(Azienda.user_id == user.id).first()
    
    mezzo = db.query(Mezzo).filter(
        Mezzo.id == mezzo_id,
        Mezzo.azienda_id == azienda.id
    ).first()
    
    if not mezzo:
        raise HTTPException(status_code=404, detail="Mezzo non trovato")
    
    data_rev = datetime.strptime(data_revisione, "%Y-%m-%d").date()
    
    mezzo.nome = nome
    mezzo.targa = targa
    mezzo.data_revisione = data_rev
    mezzo.tipo_mezzo = tipo_mezzo
    mezzo.marca = marca
    mezzo.modello = modello
    mezzo.anno_acquisto = anno_acquisto
    mezzo.note_manutenzione = note_manutenzione
    
    db.commit()
    
    return RedirectResponse(url="/mezzi", status_code=303)


@app.get("/mezzi/{mezzo_id}/libretto", response_class=HTMLResponse)
async def libretto_mezzo(request: Request, mezzo_id: int, db: Session = Depends(get_db)):
    """Pagina libretto manutenzione mezzo"""
    user = require_auth(request, db)
    azienda = db.query(Azienda).filter(Azienda.user_id == user.id).first()
    
    mezzo = db.query(Mezzo).filter(
        Mezzo.id == mezzo_id,
        Mezzo.azienda_id == azienda.id
    ).first()
    
    if not mezzo:
        raise HTTPException(status_code=404, detail="Mezzo non trovato")
    
    interventi = db.query(InterventoManutenzione).filter(
        InterventoManutenzione.mezzo_id == mezzo_id
    ).order_by(InterventoManutenzione.data_intervento.desc()).all()
    
    return templates.TemplateResponse("libretto_mezzo.html", {
        "request": request,
        "user": user,
        "azienda": azienda,
        "mezzo": mezzo,
        "interventi": interventi,
        "oggi": date.today()
    })


@app.post("/mezzi/{mezzo_id}/intervento/nuovo")
async def nuovo_intervento(
    mezzo_id: int,
    request: Request,
    data_intervento: str = Form(...),
    tipo_intervento: str = Form(...),
    descrizione: str = Form(None),
    costo: float = Form(None),
    officina: str = Form(None),
    prossima_scadenza: str = Form(None),
    note: str = Form(None),
    db: Session = Depends(get_db)
):
    """Aggiungi nuovo intervento manutenzione"""
    user = require_auth(request, db)
    azienda = db.query(Azienda).filter(Azienda.user_id == user.id).first()
    
    mezzo = db.query(Mezzo).filter(
        Mezzo.id == mezzo_id,
        Mezzo.azienda_id == azienda.id
    ).first()
    
    if not mezzo:
        raise HTTPException(status_code=404, detail="Mezzo non trovato")
    
    data_int = datetime.strptime(data_intervento, "%Y-%m-%d").date()
    prossima_scad = datetime.strptime(prossima_scadenza, "%Y-%m-%d").date() if prossima_scadenza else None
    
    intervento = InterventoManutenzione(
        mezzo_id=mezzo_id,
        data_intervento=data_int,
        tipo_intervento=tipo_intervento,
        descrizione=descrizione,
        costo=costo,
        officina=officina,
        prossima_scadenza=prossima_scad,
        note=note
    )
    db.add(intervento)
    
    # Aggiorna data revisione del mezzo se è una revisione
    if tipo_intervento.lower() in ["revisione", "revisione annuale"] and prossima_scad:
        mezzo.data_revisione = prossima_scad
    
    db.commit()
    
    return RedirectResponse(url=f"/mezzi/{mezzo_id}/libretto", status_code=303)


# ========== ALERT METEO ==========

async def get_meteo_esteso(lat: float = None, lng: float = None) -> dict:
    """Ottiene previsioni meteo estese e genera alert"""
    if lat is None:
        lat = METEO_LAT
    if lng is None:
        lng = METEO_LNG
    """Ottiene previsioni meteo estese e genera alert"""
    try:
        async with httpx.AsyncClient() as client:
            url = "https://api.open-meteo.com/v1/forecast"
            params = {
                "latitude": lat,
                "longitude": lng,
                "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum",
                "forecast_days": 7,
                "timezone": "Europe/Rome"
            }
            response = await client.get(url, params=params, timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                daily = data.get("daily", {})
                
                # Analizza condizioni per alert
                alert = None
                consiglio = None
                
                # Controlla pioggia prevista
                if daily.get("precipitation_sum", [0])[0] > 5:
                    alert = "Pioggia prevista"
                    consiglio = "Evitare trattamenti fitosanitari nei prossimi giorni"
                elif daily.get("precipitation_sum", [0])[0] > 0:
                    alert = "Possibile pioggia"
                    consiglio = "Verificare condizioni meteo prima di trattamenti"
                
                # Controlla temperatura
                temp_max = daily.get("temperature_2m_max", [0])[0]
                if temp_max > 30:
                    if not alert:
                        alert = "Temperature elevate"
                    consiglio = "Evitare trattamenti nelle ore più calde"
                
                return {
                    "temperatura": daily.get("temperature_2m_max", [0])[0],
                    "precipitazioni": daily.get("precipitation_sum", [0]),
                    "alert": alert,
                    "consiglio": consiglio,
                    "previsioni": daily
                }
    except Exception as e:
        print(f"Errore meteo: {e}")
    
    return {"temperatura": "N/A", "alert": None, "consiglio": None}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

