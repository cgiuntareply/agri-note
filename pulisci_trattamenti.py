"""
Script per pulire tutti i trattamenti esistenti
Utile per risolvere problemi con trattamenti vecchi
"""
from sqlalchemy import create_engine
from models import DATABASE_URL, Trattamento
from sqlalchemy.orm import sessionmaker

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def pulisci_trattamenti():
    """Elimina tutti i trattamenti"""
    db = SessionLocal()
    
    try:
        # Conta trattamenti prima
        num_trattamenti = db.query(Trattamento).count()
        print(f"📊 Trovati {num_trattamenti} trattamenti da eliminare")
        
        if num_trattamenti == 0:
            print("✅ Nessun trattamento da eliminare")
            return
        
        # Elimina trattamenti
        db.query(Trattamento).delete()
        print(f"✅ Eliminati {num_trattamenti} trattamenti")
        
        db.commit()
        print("\n🎉 Pulizia completata! Ora puoi ricreare i trattamenti.")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Errore durante la pulizia: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    import sys
    
    print("🧹 Avvio pulizia trattamenti...\n")
    
    # Se viene passato --force, salta la conferma
    if '--force' not in sys.argv:
        conferma = input("⚠️  ATTENZIONE: Questo eliminerà TUTTI i trattamenti. Continuare? (s/n): ")
        if conferma.lower() != 's':
            print("❌ Operazione annullata")
            exit(0)
    else:
        print("⚠️  Modalità --force: eliminazione automatica")
    
    pulisci_trattamenti()

