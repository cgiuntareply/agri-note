"""
Script per pulire tutti i campi esistenti e ricreare il database
Utile per risolvere problemi con campi vecchi senza colonne centro
"""
from sqlalchemy import create_engine, text
from models import DATABASE_URL, Base, Campo, Trattamento
from sqlalchemy.orm import sessionmaker

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def pulisci_campi():
    """Elimina tutti i campi e i trattamenti associati"""
    db = SessionLocal()
    
    try:
        # Conta campi prima
        num_campi = db.query(Campo).count()
        print(f"📊 Trovati {num_campi} campi da eliminare")
        
        if num_campi == 0:
            print("✅ Nessun campo da eliminare")
            return
        
        # Elimina tutti i trattamenti (cascade dovrebbe farlo automaticamente, ma meglio essere espliciti)
        num_trattamenti = db.query(Trattamento).count()
        print(f"📊 Trovati {num_trattamenti} trattamenti da eliminare")
        
        # Elimina trattamenti
        db.query(Trattamento).delete()
        print(f"✅ Eliminati {num_trattamenti} trattamenti")
        
        # Elimina campi
        db.query(Campo).delete()
        print(f"✅ Eliminati {num_campi} campi")
        
        db.commit()
        print("\n🎉 Pulizia completata! Ora puoi ricreare i campi.")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Errore durante la pulizia: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    import sys
    
    print("🧹 Avvio pulizia campi...\n")
    
    # Se viene passato --force, salta la conferma
    if '--force' not in sys.argv:
        conferma = input("⚠️  ATTENZIONE: Questo eliminerà TUTTI i campi e trattamenti. Continuare? (s/n): ")
        if conferma.lower() != 's':
            print("❌ Operazione annullata")
            exit(0)
    else:
        print("⚠️  Modalità --force: eliminazione automatica")
    
    pulisci_campi()

