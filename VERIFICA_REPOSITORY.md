# 🔍 Verifica Repository GitHub

## Problema: "Repository not found"

Se il repository esiste su GitHub ma Git non lo trova, potrebbe essere:

### 1. 🔐 Problema di Autenticazione

GitHub richiede autenticazione per repository privati o per push. Verifica:

```bash
# Prova a fare fetch con autenticazione
git fetch origin

# Se chiede credenziali, usa:
# - Username: cgiuntareply
# - Password: Personal Access Token (NON la password normale)
```

**Crea Personal Access Token:**
1. Vai su: https://github.com/settings/tokens
2. Clicca "Generate new token (classic)"
3. Nome: `agri-note-local`
4. Permessi: Seleziona `repo` (tutti i permessi)
5. Genera e copia il token
6. Usa il token come password quando Git lo chiede

### 2. 📝 Nome Repository Diverso

Verifica il nome esatto del repository:
- Vai su: https://github.com/cgiuntareply?tab=repositories
- Controlla il nome esatto del repository
- Potrebbe essere: `agri-note`, `AgriNote`, `agrinote`, etc.

Se il nome è diverso, aggiorna il remote:

```bash
# Rimuovi remote attuale
git remote remove origin

# Aggiungi con il nome corretto
git remote add origin https://github.com/cgiuntareply/NOME_CORRETTO.git

# Verifica
git remote -v
```

### 3. 🔒 Repository Privato

Se il repository è privato, assicurati di:
- Essere loggato su GitHub con l'account corretto
- Avere i permessi di accesso al repository
- Usare un Personal Access Token con permessi `repo`

### 4. ✅ Soluzione: Usa SSH invece di HTTPS

Se hai problemi con HTTPS, prova SSH:

```bash
# Genera SSH key (se non ce l'hai)
ssh-keygen -t ed25519 -C "tua.email@example.com"

# Aggiungi la chiave a GitHub
# Copia la chiave pubblica:
cat ~/.ssh/id_ed25519.pub

# Incollala su: https://github.com/settings/keys

# Cambia remote a SSH
git remote set-url origin git@github.com:cgiuntareply/agri-note.git

# Prova
git push -u origin main
```

### 5. 🧪 Test Connessione

```bash
# Test connessione GitHub
curl -I https://github.com/cgiuntareply/agri-note

# Se restituisce 200 = repository esiste e è pubblico
# Se restituisce 404 = repository non esiste o nome errato
# Se restituisce 301/302 = redirect (nome diverso)
```

## 🚀 Comandi Rapidi

```bash
# Verifica remote
git remote -v

# Test connessione
git ls-remote origin

# Prova push con verbose
GIT_CURL_VERBOSE=1 GIT_TRACE=1 git push -u origin main
```

## 💡 Suggerimento

Il modo più semplice è usare GitHub CLI:

```bash
# Installa
brew install gh

# Login
gh auth login

# Verifica repository
gh repo view cgiuntareply/agri-note

# Push
git push -u origin main
```

