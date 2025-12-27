"""
Script di migrazione database per aggiungere nuove colonne
"""
from sqlalchemy import create_engine, text
from models import DATABASE_URL

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

def migrate():
    """Aggiunge le colonne mancanti al database esistente"""
    with engine.connect() as conn:
        try:
            # Aggiungi colonne a mezzi se non esistono
            conn.execute(text("""
                ALTER TABLE mezzi ADD COLUMN tipo_mezzo VARCHAR;
            """))
            print("✅ Aggiunta colonna tipo_mezzo")
        except Exception as e:
            if "duplicate column" not in str(e).lower():
                print(f"⚠️  tipo_mezzo: {e}")
        
        try:
            conn.execute(text("""
                ALTER TABLE mezzi ADD COLUMN marca VARCHAR;
            """))
            print("✅ Aggiunta colonna marca")
        except Exception as e:
            if "duplicate column" not in str(e).lower():
                print(f"⚠️  marca: {e}")
        
        try:
            conn.execute(text("""
                ALTER TABLE mezzi ADD COLUMN modello VARCHAR;
            """))
            print("✅ Aggiunta colonna modello")
        except Exception as e:
            if "duplicate column" not in str(e).lower():
                print(f"⚠️  modello: {e}")
        
        try:
            conn.execute(text("""
                ALTER TABLE mezzi ADD COLUMN anno_acquisto INTEGER;
            """))
            print("✅ Aggiunta colonna anno_acquisto")
        except Exception as e:
            if "duplicate column" not in str(e).lower():
                print(f"⚠️  anno_acquisto: {e}")
        
        # Aggiungi colonne centro a campi se non esistono
        try:
            conn.execute(text("""
                ALTER TABLE campi ADD COLUMN centro_lat FLOAT;
            """))
            print("✅ Aggiunta colonna centro_lat")
        except Exception as e:
            if "duplicate column" not in str(e).lower():
                print(f"⚠️  centro_lat: {e}")
        
        try:
            conn.execute(text("""
                ALTER TABLE campi ADD COLUMN centro_lng FLOAT;
            """))
            print("✅ Aggiunta colonna centro_lng")
        except Exception as e:
            if "duplicate column" not in str(e).lower():
                print(f"⚠️  centro_lng: {e}")
        
        # Crea tabella interventi_manutenzione se non esiste
        try:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS interventi_manutenzione (
                    id INTEGER NOT NULL PRIMARY KEY,
                    mezzo_id INTEGER NOT NULL,
                    data_intervento DATE NOT NULL,
                    tipo_intervento VARCHAR NOT NULL,
                    descrizione TEXT,
                    costo FLOAT,
                    officina VARCHAR,
                    prossima_scadenza DATE,
                    note TEXT,
                    FOREIGN KEY(mezzo_id) REFERENCES mezzi (id)
                );
            """))
            print("✅ Creata tabella interventi_manutenzione")
        except Exception as e:
            print(f"⚠️  interventi_manutenzione: {e}")
        
        conn.commit()
        print("\n🎉 Migrazione completata!")

if __name__ == "__main__":
    print("🔄 Avvio migrazione database...\n")
    migrate()

