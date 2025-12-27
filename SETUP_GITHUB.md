# 🚀 Guida Setup GitHub per AgriNote

Questa guida ti aiuta a pubblicare il progetto AgriNote su GitHub.

## 📋 Prerequisiti

1. Account GitHub (crea su https://github.com)
2. Git installato sul tuo computer
3. Progetto AgriNote funzionante localmente

## 🔧 Passo 1: Inizializza Git (se non già fatto)

```bash
cd "/Users/carlogiunta/Documents/Dev Projects/agri-note"
git init
```

## 📝 Passo 2: Configura Git (se non già fatto)

```bash
git config user.name "Il Tuo Nome"
git config user.email "tua.email@example.com"
```

Oppure per configurazione globale:
```bash
git config --global user.name "Il Tuo Nome"
git config --global user.email "tua.email@example.com"
```

## ✅ Passo 3: Verifica file da committare

```bash
git status
```

Dovresti vedere tutti i file del progetto. I file esclusi da `.gitignore` (come `*.db`, `__pycache__/`, etc.) non verranno inclusi.

## 📦 Passo 4: Aggiungi file e crea primo commit

```bash
# Aggiungi tutti i file
git add .

# Crea il primo commit
git commit -m "Initial commit: AgriNote MVP - Gestionale Agricolo completo"
```

## 🌐 Passo 5: Crea repository su GitHub

1. Vai su https://github.com e accedi
2. Clicca su **"+"** in alto a destra → **"New repository"**
3. Compila il form:
   - **Repository name**: `agri-note` (o un nome a tua scelta)
   - **Description**: "Gestionale agricolo MVP con FastAPI - Gestione campi, trattamenti, magazzino e mezzi"
   - **Visibility**: Scegli Public o Private
   - **NON** selezionare:
     - ❌ Add a README file
     - ❌ Add .gitignore
     - ❌ Choose a license
   (Li abbiamo già nel progetto!)
4. Clicca **"Create repository"**

## 🔗 Passo 6: Collega repository locale a GitHub

GitHub ti mostrerà le istruzioni. Esegui:

```bash
# Sostituisci TUO_USERNAME con il tuo username GitHub
git remote add origin https://github.com/TUO_USERNAME/agri-note.git

# Rinomina branch principale (se necessario)
git branch -M main

# Fai il primo push
git push -u origin main
```

Se GitHub ti chiede autenticazione:
- **Token**: Crea un Personal Access Token su GitHub (Settings → Developer settings → Personal access tokens)
- Oppure usa GitHub CLI: `gh auth login`

## ✅ Verifica

Vai sul tuo repository GitHub e verifica che tutti i file siano stati caricati correttamente.

## 🔄 Comandi utili per il futuro

```bash
# Aggiungi modifiche
git add .

# Crea commit
git commit -m "Descrizione delle modifiche"

# Push su GitHub
git push

# Vedi stato
git status

# Vedi log commit
git log --oneline
```

## 📝 Buone pratiche

1. **Commit frequenti**: Fai commit spesso con messaggi descrittivi
2. **Branch**: Usa branch per nuove funzionalità (`git checkout -b feature/nuova-funzionalita`)
3. **README**: Mantieni il README aggiornato
4. **.gitignore**: Non committare mai file sensibili (password, chiavi API, database)

## 🎉 Fatto!

Il tuo progetto è ora su GitHub! Puoi condividerlo, collaborare e tracciare le modifiche.

