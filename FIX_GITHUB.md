# 🔧 Fix: Repository GitHub Non Trovato

## 🔍 Diagnosi

Il repository `https://github.com/cgiuntareply/agri-note` restituisce 404.

## ✅ Soluzioni

### Soluzione 1: Verifica Nome Esatto

1. Vai su: https://github.com/cgiuntareply?tab=repositories
2. Cerca il repository e controlla il nome ESATTO
3. Se il nome è diverso, aggiorna:

```bash
git remote set-url origin https://github.com/cgiuntareply/NOME_ESATTO.git
```

### Soluzione 2: Configura Autenticazione

GitHub non accetta più password. Usa un Personal Access Token:

```bash
# 1. Crea token su: https://github.com/settings/tokens
#    - Nome: agri-note-token
#    - Permessi: repo (tutti)

# 2. Configura Git per salvare le credenziali
git config --global credential.helper osxkeychain  # macOS
# oppure
git config --global credential.helper store        # Linux/Windows

# 3. Prova push (chiederà username e token come password)
git push -u origin main
# Username: cgiuntareply
# Password: [incolla il token qui]
```

### Soluzione 3: Usa SSH (Raccomandato)

```bash
# 1. Genera chiave SSH (se non ce l'hai)
ssh-keygen -t ed25519 -C "tua.email@example.com"
# Premi Enter per accettare percorso default
# (Opzionale: aggiungi passphrase)

# 2. Aggiungi chiave a GitHub
# Copia la chiave pubblica:
cat ~/.ssh/id_ed25519.pub
# Poi incollala su: https://github.com/settings/keys

# 3. Cambia remote a SSH
git remote set-url origin git@github.com:cgiuntareply/agri-note.git

# 4. Test connessione
ssh -T git@github.com
# Dovresti vedere: "Hi cgiuntareply! You've successfully authenticated..."

# 5. Push
git push -u origin main
```

### Soluzione 4: Crea Repository Se Non Esiste

Se il repository non esiste ancora:

1. Vai su: https://github.com/new
2. Nome: `agri-note`
3. Clicca "Create repository"
4. Poi:

```bash
git push -u origin main
```

## 🧪 Test Rapido

```bash
# Verifica se il repository è accessibile
curl -s -o /dev/null -w "%{http_code}" https://github.com/cgiuntareply/agri-note

# 200 = OK, esiste
# 404 = Non esiste o privato senza accesso
# 301/302 = Redirect (nome diverso)
```

## 💡 Pro Tip: GitHub CLI

Il modo più semplice:

```bash
# Installa
brew install gh

# Login (apre browser)
gh auth login

# Verifica repository
gh repo view cgiuntareply/agri-note

# Se non esiste, crealo
gh repo create agri-note --public --source=. --push
```

