# 🚀 Quick Start - Pubblica su GitHub

## ⚠️ ERRORE: Repository non trovato

Se vedi l'errore `remote: Repository not found`, significa che il repository GitHub non esiste ancora.

## ✅ Soluzione Rapida

### Opzione 1: Crea il repository su GitHub (Raccomandato)

1. **Vai su GitHub**: https://github.com/new
2. **Compila il form**:
   - Repository name: `agri-note`
   - Description: `Gestionale agricolo MVP con FastAPI - Gestione campi, trattamenti, magazzino e mezzi`
   - Visibility: Scegli Public o Private
   - **NON selezionare** README, .gitignore o license (li abbiamo già!)
3. **Clicca "Create repository"**

4. **Poi esegui**:
```bash
cd "/Users/carlogiunta/Documents/Dev Projects/agri-note"

# Rimuovi remote errato (se esiste)
git remote remove origin 2>/dev/null || true

# Aggiungi il remote corretto (sostituisci TUO_USERNAME)
git remote add origin https://github.com/TUO_USERNAME/agri-note.git

# Verifica
git remote -v

# Crea commit (se non già fatto)
git commit -m "Initial commit: AgriNote MVP completo"

# Push
git branch -M main
git push -u origin main
```

### Opzione 2: Usa GitHub CLI (se installato)

```bash
# Installa GitHub CLI se non ce l'hai: brew install gh

# Login
gh auth login

# Crea repository e push in un comando
gh repo create agri-note --public --source=. --remote=origin --push
```

### Opzione 3: Verifica nome repository

Se il repository esiste già con un nome diverso, usa quello:

```bash
# Rimuovi remote errato
git remote remove origin

# Aggiungi con il nome corretto
git remote add origin https://github.com/TUO_USERNAME/NOME_REPOSITORY.git

# Push
git push -u origin main
```

## 🔍 Verifica Stato Attuale

```bash
# Verifica remote
git remote -v

# Verifica commit
git log --oneline

# Verifica branch
git branch
```

## 💡 Suggerimenti

- **Username GitHub**: Verifica il tuo username su https://github.com/settings/profile
- **Autenticazione**: GitHub non accetta più password. Usa:
  - Personal Access Token (Settings → Developer settings → Personal access tokens)
  - Oppure GitHub CLI: `gh auth login`
- **Repository privato**: Se vuoi un repo privato, seleziona "Private" quando lo crei

## ✅ Dopo il Push

Una volta pubblicato, il tuo repository sarà disponibile su:
`https://github.com/TUO_USERNAME/agri-note`

Puoi condividerlo, clonarlo su altri computer, e collaborare!

