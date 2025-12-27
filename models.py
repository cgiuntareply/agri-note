"""
Modelli SQLAlchemy per AgriNote
Database: SQLite
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey, Enum, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from enum import Enum as PyEnum
from datetime import date

Base = declarative_base()


class TipoProdotto(PyEnum):
    FITOFARMACO = "Fitofarmaco"
    CONCIME = "Concime"


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    
    # Relazioni
    aziende = relationship("Azienda", back_populates="user", cascade="all, delete-orphan")


class Azienda(Base):
    __tablename__ = "aziende"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    ragione_sociale = Column(String, nullable=False)
    p_iva = Column(String, unique=True, nullable=False)
    indirizzo = Column(String, nullable=False)
    legale_rappresentante = Column(String, nullable=False)
    codice_fiscale = Column(String, nullable=True)  # Codice fiscale azienda
    comune = Column(String, nullable=True)  # Comune sede legale
    provincia = Column(String, nullable=True)  # Provincia
    cap = Column(String, nullable=True)  # CAP
    telefono = Column(String, nullable=True)
    email = Column(String, nullable=True)
    numero_registro_imprese = Column(String, nullable=True)  # Numero REA
    
    # Relazioni
    user = relationship("User", back_populates="aziende")
    campi = relationship("Campo", back_populates="azienda", cascade="all, delete-orphan")
    prodotti = relationship("Prodotto", back_populates="azienda", cascade="all, delete-orphan")
    mezzi = relationship("Mezzo", back_populates="azienda", cascade="all, delete-orphan")


class Campo(Base):
    __tablename__ = "campi"
    
    id = Column(Integer, primary_key=True, index=True)
    azienda_id = Column(Integer, ForeignKey("aziende.id"), nullable=False)
    nome = Column(String, nullable=False)
    superficie_ettari = Column(Float, nullable=False)
    coordinate_poligono = Column(JSON, nullable=True)  # Lista di coordinate [lat, lng]
    centro_lat = Column(Float, nullable=True)  # Latitudine centro campo
    centro_lng = Column(Float, nullable=True)  # Longitudine centro campo
    coltura_attuale = Column(String, nullable=True)
    
    # Relazioni
    azienda = relationship("Azienda", back_populates="campi")
    trattamenti = relationship("Trattamento", back_populates="campo", cascade="all, delete-orphan")


class Prodotto(Base):
    __tablename__ = "prodotti"
    
    id = Column(Integer, primary_key=True, index=True)
    azienda_id = Column(Integer, ForeignKey("aziende.id"), nullable=False)
    nome_commerciale = Column(String, nullable=False)
    tipo = Column(Enum(TipoProdotto), nullable=False)
    quantita_disponibile = Column(Float, nullable=False)
    unita_misura = Column(String, nullable=False)  # "kg" o "L"
    
    # Relazioni
    azienda = relationship("Azienda", back_populates="prodotti")
    trattamenti = relationship("Trattamento", back_populates="prodotto")


class Mezzo(Base):
    __tablename__ = "mezzi"
    
    id = Column(Integer, primary_key=True, index=True)
    azienda_id = Column(Integer, ForeignKey("aziende.id"), nullable=False)
    nome = Column(String, nullable=False)
    targa = Column(String, nullable=True)
    data_revisione = Column(Date, nullable=False)
    note_manutenzione = Column(Text, nullable=True)
    tipo_mezzo = Column(String, nullable=True)  # Es: "Trattore", "Spandiconcime", etc.
    marca = Column(String, nullable=True)
    modello = Column(String, nullable=True)
    anno_acquisto = Column(Integer, nullable=True)
    
    # Relazioni
    azienda = relationship("Azienda", back_populates="mezzi")
    interventi = relationship("InterventoManutenzione", back_populates="mezzo", cascade="all, delete-orphan")


class InterventoManutenzione(Base):
    __tablename__ = "interventi_manutenzione"
    
    id = Column(Integer, primary_key=True, index=True)
    mezzo_id = Column(Integer, ForeignKey("mezzi.id"), nullable=False)
    data_intervento = Column(Date, nullable=False)
    tipo_intervento = Column(String, nullable=False)  # Es: "Revisione", "Tagliando", "Riparazione"
    descrizione = Column(Text, nullable=True)
    costo = Column(Float, nullable=True)
    officina = Column(String, nullable=True)
    prossima_scadenza = Column(Date, nullable=True)
    note = Column(Text, nullable=True)
    
    # Relazioni
    mezzo = relationship("Mezzo", back_populates="interventi")


class Trattamento(Base):
    __tablename__ = "trattamenti"
    
    id = Column(Integer, primary_key=True, index=True)
    campo_id = Column(Integer, ForeignKey("campi.id"), nullable=False)
    data = Column(Date, nullable=False)
    prodotto_id = Column(Integer, ForeignKey("prodotti.id"), nullable=False)
    avversita = Column(String, nullable=True)  # Avversità o obiettivo trattamento
    quantita_per_ettaro = Column(Float, nullable=False)
    quantita_totale = Column(Float, nullable=False)  # Calcolata: dose * ettari
    operatore = Column(String, nullable=True)  # Nome operatore
    mezzo_id = Column(Integer, ForeignKey("mezzi.id"), nullable=True)  # Mezzo utilizzato
    condizioni_meteo = Column(String, nullable=True)  # Condizioni meteo durante trattamento
    temperatura = Column(Float, nullable=True)  # Temperatura (°C)
    umidita = Column(Float, nullable=True)  # Umidità relativa (%)
    velocita_vento = Column(Float, nullable=True)  # Velocità vento (km/h)
    note = Column(Text, nullable=True)  # Note aggiuntive
    numero_lotto = Column(String, nullable=True)  # Numero lotto prodotto (se disponibile)
    
    # Relazioni
    campo = relationship("Campo", back_populates="trattamenti")
    prodotto = relationship("Prodotto", back_populates="trattamenti")
    mezzo = relationship("Mezzo")


# Setup database
DATABASE_URL = "sqlite:///./agrinote.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Crea tutte le tabelle nel database"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency per ottenere la sessione DB"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

