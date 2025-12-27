"""
Script per aggiungere nuovi campi al database per il quaderno di campagna completo
"""
from sqlalchemy import create_engine, text
from models import DATABASE_URL, Base
from sqlalchemy.orm import sessionmaker

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def migrate_quaderno():
    """Aggiunge nuovi campi per quaderno di campagna completo"""
    db = SessionLocal()
    
    try:
        # Aggiungi campi a Azienda
        print("📊 Aggiungo campi a tabella aziende...")
        try:
            db.execute(text("ALTER TABLE aziende ADD COLUMN codice_fiscale VARCHAR"))
            print("  ✅ codice_fiscale")
        except Exception as e:
            if "duplicate column" not in str(e).lower():
                print(f"  ⚠️  codice_fiscale: {e}")
        
        try:
            db.execute(text("ALTER TABLE aziende ADD COLUMN comune VARCHAR"))
            print("  ✅ comune")
        except Exception as e:
            if "duplicate column" not in str(e).lower():
                print(f"  ⚠️  comune: {e}")
        
        try:
            db.execute(text("ALTER TABLE aziende ADD COLUMN provincia VARCHAR"))
            print("  ✅ provincia")
        except Exception as e:
            if "duplicate column" not in str(e).lower():
                print(f"  ⚠️  provincia: {e}")
        
        try:
            db.execute(text("ALTER TABLE aziende ADD COLUMN cap VARCHAR"))
            print("  ✅ cap")
        except Exception as e:
            if "duplicate column" not in str(e).lower():
                print(f"  ⚠️  cap: {e}")
        
        try:
            db.execute(text("ALTER TABLE aziende ADD COLUMN telefono VARCHAR"))
            print("  ✅ telefono")
        except Exception as e:
            if "duplicate column" not in str(e).lower():
                print(f"  ⚠️  telefono: {e}")
        
        try:
            db.execute(text("ALTER TABLE aziende ADD COLUMN email VARCHAR"))
            print("  ✅ email")
        except Exception as e:
            if "duplicate column" not in str(e).lower():
                print(f"  ⚠️  email: {e}")
        
        try:
            db.execute(text("ALTER TABLE aziende ADD COLUMN numero_registro_imprese VARCHAR"))
            print("  ✅ numero_registro_imprese")
        except Exception as e:
            if "duplicate column" not in str(e).lower():
                print(f"  ⚠️  numero_registro_imprese: {e}")
        
        # Aggiungi campi a Trattamento
        print("\n📊 Aggiungo campi a tabella trattamenti...")
        try:
            db.execute(text("ALTER TABLE trattamenti ADD COLUMN mezzo_id INTEGER"))
            print("  ✅ mezzo_id")
        except Exception as e:
            if "duplicate column" not in str(e).lower():
                print(f"  ⚠️  mezzo_id: {e}")
        
        try:
            db.execute(text("ALTER TABLE trattamenti ADD COLUMN condizioni_meteo VARCHAR"))
            print("  ✅ condizioni_meteo")
        except Exception as e:
            if "duplicate column" not in str(e).lower():
                print(f"  ⚠️  condizioni_meteo: {e}")
        
        try:
            db.execute(text("ALTER TABLE trattamenti ADD COLUMN temperatura REAL"))
            print("  ✅ temperatura")
        except Exception as e:
            if "duplicate column" not in str(e).lower():
                print(f"  ⚠️  temperatura: {e}")
        
        try:
            db.execute(text("ALTER TABLE trattamenti ADD COLUMN umidita REAL"))
            print("  ✅ umidita")
        except Exception as e:
            if "duplicate column" not in str(e).lower():
                print(f"  ⚠️  umidita: {e}")
        
        try:
            db.execute(text("ALTER TABLE trattamenti ADD COLUMN velocita_vento REAL"))
            print("  ✅ velocita_vento")
        except Exception as e:
            if "duplicate column" not in str(e).lower():
                print(f"  ⚠️  velocita_vento: {e}")
        
        try:
            db.execute(text("ALTER TABLE trattamenti ADD COLUMN note TEXT"))
            print("  ✅ note")
        except Exception as e:
            if "duplicate column" not in str(e).lower():
                print(f"  ⚠️  note: {e}")
        
        try:
            db.execute(text("ALTER TABLE trattamenti ADD COLUMN numero_lotto VARCHAR"))
            print("  ✅ numero_lotto")
        except Exception as e:
            if "duplicate column" not in str(e).lower():
                print(f"  ⚠️  numero_lotto: {e}")
        
        db.commit()
        print("\n🎉 Migrazione completata!")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Errore durante la migrazione: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("🔄 Avvio migrazione database per quaderno di campagna completo...\n")
    migrate_quaderno()

