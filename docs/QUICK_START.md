# Quick Start - Ceramica Classifier

## Requisiti Minimi

Per far funzionare la classificazione, hai bisogno di:

### 1. Dati delle Ceramiche

Una tabella/foglio con almeno:
- **ID univoco** per ogni ceramica
- **Campo decorazione** per filtrare (opzionale ma consigliato)

### 2. Immagini

- Cartella con le immagini delle ceramiche
- Nomi file che permettano di associarli ai record

### 3. Collegamento

Un modo per collegare ogni ceramica alla sua immagine.

---

## Configurazione in 3 Passaggi

### Passo 1: Connessione Database

```
Tipo: PostgreSQL / MySQL / SQLite / Excel / CSV
Credenziali: host, porta, database, utente, password
```

### Passo 2: Analisi AI o Configurazione Manuale

L'AI analizzerà automaticamente:
- Quale tabella contiene le ceramiche
- Quale tabella contiene le immagini
- Come sono collegati
- Come filtrare le ceramiche decorate

### Passo 3: Percorso Immagini

Specifica:
- Cartella base delle immagini
- Pattern del nome file (es: `{id_media}_{filename}.png`)

---

## Struttura Minima Consigliata

### Database SQL

```
TABELLA: ceramiche
├── id (INTEGER, chiave primaria)
├── decorata (TEXT: 'Yes'/'No')
└── immagine (TEXT: nome del file)

CARTELLA IMMAGINI:
└── /path/to/images/
    ├── 1.jpg
    ├── 2.jpg
    └── ...
```

### File Excel

```
FOGLIO: Ceramiche
├── Colonna A: ID
├── Colonna B: Decorata (Yes/No)
├── Colonna C: NomeImmagine
└── ...

CARTELLA IMMAGINI:
└── /path/to/images/
    ├── IMG001.jpg
    ├── IMG002.jpg
    └── ...
```

---

## Esempi di Query Generate

### Caso Semplice (embedded)
```sql
SELECT * FROM ceramiche WHERE decorata = 'Yes'
```

### Caso con Tabella Media
```sql
SELECT c.*, m.filename
FROM ceramiche c
JOIN media m ON m.id = c.id_media
WHERE c.decorata = 'Yes'
```

### Caso Completo (junction)
```sql
SELECT DISTINCT ON (c.id) c.*, m.filename
FROM ceramiche c
JOIN relazioni r ON r.id_ceramica = c.id AND r.tipo = 'CERAMICA'
JOIN media m ON m.id = r.id_media
WHERE c.decorata = 'Yes'
```

---

## Opzioni di Classificazione

| Opzione | Descrizione |
|---------|-------------|
| Una immagine per ceramica | Classifica ogni ceramica una volta |
| Tutte le immagini | Classifica ogni singola immagine |

---

## Risoluzione Problemi Comuni

| Problema | Soluzione |
|----------|-----------|
| 0 ceramiche trovate | Verifica il filtro decorazione |
| Immagini non trovate | Controlla il pattern e il percorso |
| Troppi record | Attiva "Una immagine per ceramica" |
| Errore query | Modifica manualmente la configurazione |
