# ⚡ Soluzione Rapida: Repository Non Trovato

## 🎯 Il Problema

Git dice "Repository not found" ma il repository esiste su GitHub.

## ✅ Soluzione Immediata

### Se il Repository è PRIVATO:

GitHub richiede autenticazione. Usa un **Personal Access Token**:

1. **Crea Token:**
   - Vai su: https://github.com/settings/tokens
   - Clicca "Generate new token (classic)"
   - Nome: `agri-note-push`
   - Permessi: ✅ `repo` (tutti i permessi)
   - Clicca "Generate token"
   - **COPIA IL TOKEN** (lo vedi solo una volta!)

2. **Prova Push:**
```bash
git push -u origin main
```

3. **Quando chiede credenziali:**
   - Username: `cgiuntareply`
   - Password: **incolla il token** (non la password normale!)

### Se il Nome è Diverso:

1. Vai su: https://github.com/cgiuntareply?tab=repositories
2. Controlla il nome ESATTO
3. Aggiorna remote:

```bash
# Se il nome è diverso (es: AgriNote, agrinote, etc.)
git remote set-url origin https://github.com/cgiuntareply/NOME_ESATTO.git
git push -u origin main
```

### Usa SSH (Più Semplice):

```bash
# 1. Genera chiave SSH
ssh-keygen -t ed25519 -C "tua.email@example.com"
# Premi Enter 3 volte (default, no passphrase)

# 2. Copia chiave pubblica
cat ~/.ssh/id_ed25519.pub
# Copia tutto l'output

# 3. Aggiungi su GitHub
# Vai su: https://github.com/settings/keys
# Clicca "New SSH key"
# Incolla la chiave e salva

# 4. Cambia remote a SSH
git remote set-url origin git@github.com:cgiuntareply/agri-note.git

# 5. Test
ssh -T git@github.com
# Dovresti vedere: "Hi cgiuntareply! You've successfully authenticated..."

# 6. Push
git push -u origin main
```

## 🚀 Alternativa: GitHub CLI

```bash
# Installa
brew install gh

# Login (apre browser)
gh auth login

# Push (gestisce tutto automaticamente)
git push -u origin main
```

## ✅ Verifica Stato

```bash
# Verifica remote
git remote -v

# Verifica branch
git branch

# Verifica commit
git log --oneline -5
```

