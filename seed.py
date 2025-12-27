"""
Script di seed per popolare il database con dati di prova
"""
from sqlalchemy.orm import Session
from datetime import date, timedelta
from models import (
    engine, SessionLocal,
    User, Azienda, Campo, Prodotto, Mezzo, Trattamento, TipoProdotto
)
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def init_db():
    """Inizializza il database"""
    from models import Base
    Base.metadata.create_all(bind=engine)


def seed_data():
    """Popola il database con dati di prova"""
    db = SessionLocal()
    
    try:
        # Verifica se esiste già un utente
        existing_user = db.query(User).filter(User.username == "admin").first()
        if existing_user:
            print("⚠️  Database già popolato. Elimina il file agrinote.db per ricreare i dati.")
            return
        
        # 1. Crea Utente
        print("📝 Creazione utente...")
        user = User(
            username="admin",
            password_hash=pwd_context.hash("admin123")
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"✅ Utente creato: {user.username}")
        
        # 2. Crea Azienda
        print("🏢 Creazione azienda...")
        azienda = Azienda(
            user_id=user.id,
            ragione_sociale="Azienda Agricola Demo S.r.l.",
            p_iva="IT12345678901",
            indirizzo="Via dei Campi, 123 - 20100 Milano (MI)",
            legale_rappresentante="Mario Rossi"
        )
        db.add(azienda)
        db.commit()
        db.refresh(azienda)
        print(f"✅ Azienda creata: {azienda.ragione_sociale}")
        
        # 3. Crea Campi
        print("🌾 Creazione campi...")
        campi_data = [
            {
                "nome": "Campo Nord",
                "superficie_ettari": 5.5,
                "coordinate_poligono": [[45.47, 9.19], [45.48, 9.19], [45.48, 9.20], [45.47, 9.20]],
                "coltura_attuale": "Mais"
            },
            {
                "nome": "Campo Sud",
                "superficie_ettari": 3.2,
                "coordinate_poligono": [[45.46, 9.18], [45.47, 9.18], [45.47, 9.19], [45.46, 9.19]],
                "coltura_attuale": "Grano"
            },
            {
                "nome": "Campo Est",
                "superficie_ettari": 7.8,
                "coordinate_poligono": [[45.45, 9.20], [45.46, 9.20], [45.46, 9.21], [45.45, 9.21]],
                "coltura_attuale": "Soia"
            }
        ]
        
        for campo_data in campi_data:
            campo = Campo(
                azienda_id=azienda.id,
                **campo_data
            )
            db.add(campo)
        db.commit()
        print(f"✅ Creati {len(campi_data)} campi")
        
        # 4. Crea Prodotti
        print("📦 Creazione prodotti...")
        prodotti_data = [
            {
                "nome_commerciale": "Roundup",
                "tipo": TipoProdotto.FITOFARMACO,
                "quantita_disponibile": 150.0,
                "unita_misura": "L"
            },
            {
                "nome_commerciale": "Urea 46%",
                "tipo": TipoProdotto.CONCIME,
                "quantita_disponibile": 500.0,
                "unita_misura": "kg"
            },
            {
                "nome_commerciale": "Fungicida X",
                "tipo": TipoProdotto.FITOFARMACO,
                "quantita_disponibile": 25.0,
                "unita_misura": "L"
            },
            {
                "nome_commerciale": "NPK 20-10-10",
                "tipo": TipoProdotto.CONCIME,
                "quantita_disponibile": 300.0,
                "unita_misura": "kg"
            }
        ]
        
        for prodotto_data in prodotti_data:
            prodotto = Prodotto(
                azienda_id=azienda.id,
                **prodotto_data
            )
            db.add(prodotto)
        db.commit()
        print(f"✅ Creati {len(prodotti_data)} prodotti")
        
        # 5. Crea Mezzi
        print("🚜 Creazione mezzi...")
        oggi = date.today()
        mezzi_data = [
            {
                "nome": "Trattore John Deere",
                "targa": "AB123CD",
                "data_revisione": oggi + timedelta(days=15),
                "note_manutenzione": "Revisione annuale in scadenza"
            },
            {
                "nome": "Spandiconcime",
                "targa": None,
                "data_revisione": oggi + timedelta(days=45),
                "note_manutenzione": "In buone condizioni"
            },
            {
                "nome": "Atomizzatore",
                "targa": None,
                "data_revisione": oggi + timedelta(days=120),
                "note_manutenzione": None
            }
        ]
        
        for mezzo_data in mezzi_data:
            mezzo = Mezzo(
                azienda_id=azienda.id,
                **mezzo_data
            )
            db.add(mezzo)
        db.commit()
        print(f"✅ Creati {len(mezzi_data)} mezzi")
        
        # 6. Crea Trattamenti di esempio
        print("📋 Creazione trattamenti...")
        campi = db.query(Campo).filter(Campo.azienda_id == azienda.id).all()
        prodotti = db.query(Prodotto).filter(Prodotto.azienda_id == azienda.id).all()
        
        if campi and prodotti:
            trattamenti_data = [
                {
                    "campo": campi[0],
                    "data": oggi - timedelta(days=10),
                    "prodotto": prodotti[0],  # Roundup
                    "avversita": "Erbe infestanti",
                    "quantita_per_ettaro": 3.0,
                    "operatore": "Mario Rossi"
                },
                {
                    "campo": campi[1],
                    "data": oggi - timedelta(days=5),
                    "prodotto": prodotti[1],  # Urea
                    "avversita": None,
                    "quantita_per_ettaro": 200.0,
                    "operatore": "Luigi Bianchi"
                }
            ]
            
            for tr_data in trattamenti_data:
                campo = tr_data["campo"]
                quantita_totale = tr_data["quantita_per_ettaro"] * campo.superficie_ettari
                
                trattamento = Trattamento(
                    campo_id=campo.id,
                    data=tr_data["data"],
                    prodotto_id=tr_data["prodotto"].id,
                    avversita=tr_data["avversita"],
                    quantita_per_ettaro=tr_data["quantita_per_ettaro"],
                    quantita_totale=quantita_totale,
                    operatore=tr_data["operatore"]
                )
                db.add(trattamento)
            db.commit()
            print(f"✅ Creati {len(trattamenti_data)} trattamenti")
        
        print("\n🎉 Seed completato con successo!")
        print("\n📌 Credenziali di accesso:")
        print("   Username: admin")
        print("   Password: admin123")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Errore durante il seed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("🌱 Inizializzazione database...")
    init_db()
    print("🌱 Popolamento database con dati di prova...\n")
    seed_data()

