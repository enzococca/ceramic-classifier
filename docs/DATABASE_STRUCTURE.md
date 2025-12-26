# Guida alla Struttura dei Dati per Ceramica Classifier

Questa guida spiega come strutturare i tuoi dati (database o file Excel/CSV) affinché il sistema di classificazione AI possa analizzarli correttamente.

---

## Indice

1. [Concetti Fondamentali](#concetti-fondamentali)
2. [Schema Ideale del Database](#schema-ideale-del-database)
3. [Tipi di Relazione tra Ceramiche e Immagini](#tipi-di-relazione)
4. [Campi Richiesti e Opzionali](#campi-richiesti-e-opzionali)
5. [Esempi per Tipo di Database](#esempi-per-tipo-di-database)
6. [Struttura File Excel/CSV](#struttura-file-excelcsv)
7. [Configurazione Manuale](#configurazione-manuale)
8. [Troubleshooting](#troubleshooting)

---

## Concetti Fondamentali

Il sistema di classificazione ha bisogno di identificare tre elementi principali:

```
┌─────────────────────────────────────────────────────────────────┐
│                    ELEMENTI NECESSARI                           │
├─────────────────────────────────────────────────────────────────┤
│  1. TABELLA CERAMICHE    → I dati delle ceramiche/reperti      │
│  2. TABELLA MEDIA        → I riferimenti alle immagini         │
│  3. RELAZIONE            → Come sono collegati ceramiche e     │
│                             immagini                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## Schema Ideale del Database

### Struttura Consigliata (3 Tabelle)

```
┌──────────────────────┐         ┌──────────────────────┐
│   POTTERY_TABLE      │         │    MEDIA_TABLE       │
├──────────────────────┤         ├──────────────────────┤
│ id_rep (PK)          │         │ id_media (PK)        │
│ sito                 │         │ filename             │
│ area                 │         │ filepath             │
│ us                   │         │ description          │
│ form                 │         │ date_created         │
│ fabric               │         └──────────────────────┘
│ exdeco (Yes/No)      │                   │
│ intdeco (Yes/No)     │                   │
│ decoration_type      │                   │
│ period               │                   │
│ description          │                   │
└──────────────────────┘                   │
          │                                │
          │         ┌──────────────────────┴───────┐
          │         │   MEDIA_TO_ENTITY_TABLE      │
          │         │   (Tabella di Relazione)     │
          │         ├──────────────────────────────┤
          └─────────│ id_entity (FK → pottery)     │
                    │ id_media (FK → media)        │
                    │ entity_type ('CERAMICA')     │
                    └──────────────────────────────┘
```

### Perché Usare una Tabella di Relazione?

La tabella di relazione (junction table) permette:
- **Molti-a-molti**: Una ceramica può avere più immagini, un'immagine può essere associata a più record
- **Flessibilità**: Lo stesso sistema media può servire ceramiche, US, strutture, ecc.
- **Filtraggio**: Il campo `entity_type` permette di filtrare solo le immagini delle ceramiche

---

## Tipi di Relazione

Il sistema supporta tre tipi di relazione tra ceramiche e immagini:

### 1. JUNCTION (Consigliata)

```
┌─────────────┐     ┌─────────────────┐     ┌─────────────┐
│  POTTERY    │────▶│  JUNCTION TABLE │◀────│   MEDIA     │
│  (id_rep)   │     │  (id_entity,    │     │  (id_media) │
└─────────────┘     │   id_media,     │     └─────────────┘
                    │   entity_type)  │
                    └─────────────────┘

Esempio Query:
SELECT p.*, m.filename
FROM pottery_table p
JOIN media_to_entity r ON r.id_entity = p.id_rep AND r.entity_type = 'CERAMICA'
JOIN media_table m ON m.id_media = r.id_media
```

**Vantaggi**: Flessibile, scalabile, standard professionale
**Uso**: Database archeologici complessi, sistemi multi-entità

### 2. DIRECT (Relazione Diretta)

```
┌─────────────────────┐     ┌─────────────┐
│      POTTERY        │────▶│   MEDIA     │
│  (id_rep,           │     │  (id_media) │
│   id_media → FK)    │     └─────────────┘
└─────────────────────┘

Esempio Query:
SELECT p.*, m.filename
FROM pottery_table p
JOIN media_table m ON m.id_media = p.id_media
```

**Vantaggi**: Semplice, veloce
**Svantaggi**: Una sola immagine per ceramica
**Uso**: Cataloghi semplici, inventari base

### 3. EMBEDDED (Immagine Incorporata)

```
┌─────────────────────────────┐
│         POTTERY             │
│  (id_rep,                   │
│   image_path,               │  ← Percorso immagine diretto
│   image_filename)           │
└─────────────────────────────┘

Esempio Query:
SELECT * FROM pottery_table WHERE decorated = 'Yes'
```

**Vantaggi**: Semplicissimo, tutto in una tabella
**Svantaggi**: Poco flessibile, duplicazione dati
**Uso**: Excel, CSV, database minimali

---

## Campi Richiesti e Opzionali

### Tabella Ceramiche (POTTERY)

| Campo | Tipo | Richiesto | Descrizione |
|-------|------|-----------|-------------|
| `id` / `id_rep` | INTEGER | **Sì** | Identificatore univoco |
| `sito` / `site` | TEXT | No | Nome del sito archeologico |
| `area` | TEXT | No | Area di scavo |
| `us` | TEXT | No | Unità stratigrafica |
| `form` / `forma` | TEXT | No | Forma della ceramica |
| `fabric` / `impasto` | TEXT | No | Tipo di impasto |
| `exdeco` | TEXT | **Consigliato** | Decorazione esterna (Yes/No) |
| `intdeco` | TEXT | **Consigliato** | Decorazione interna (Yes/No) |
| `decoration_type` | TEXT | No | Tipo di decorazione |
| `period` / `periodo` | TEXT | No | Periodo cronologico |
| `description` / `note` | TEXT | No | Descrizione libera |

### Valori per Campi Decorazione

Il sistema riconosce questi valori come "decorato":

```
✓ 'Yes', 'YES', 'yes'
✓ 'Si', 'SI', 'si', 'Sì'
✓ 'True', 'true', '1', 1
✓ Qualsiasi valore non vuoto (se configurato)
```

E questi come "non decorato":
```
✗ 'No', 'NO', 'no'
✗ 'False', 'false', '0', 0
✗ NULL, vuoto
```

### Tabella Media

| Campo | Tipo | Richiesto | Descrizione |
|-------|------|-----------|-------------|
| `id_media` | INTEGER | **Sì** | Identificatore univoco |
| `filename` | TEXT | **Sì** | Nome del file immagine |
| `filepath` | TEXT | No | Percorso completo (opzionale) |
| `description` | TEXT | No | Descrizione dell'immagine |

### Tabella di Relazione (Junction)

| Campo | Tipo | Richiesto | Descrizione |
|-------|------|-----------|-------------|
| `id_entity` | INTEGER | **Sì** | FK verso pottery |
| `id_media` | INTEGER | **Sì** | FK verso media |
| `entity_type` | TEXT | **Consigliato** | Tipo di entità ('CERAMICA', 'POTTERY', etc.) |

---

## Esempi per Tipo di Database

### PostgreSQL

```sql
-- Tabella ceramiche
CREATE TABLE pottery_table (
    id_rep SERIAL PRIMARY KEY,
    sito VARCHAR(100),
    area VARCHAR(50),
    us VARCHAR(50),
    form VARCHAR(100),
    fabric VARCHAR(100),
    exdeco VARCHAR(10) DEFAULT 'No',
    intdeco VARCHAR(10) DEFAULT 'No',
    decoration_type VARCHAR(200),
    period VARCHAR(100),
    description TEXT
);

-- Tabella media
CREATE TABLE media_table (
    id_media SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    filepath TEXT,
    description TEXT
);

-- Tabella di relazione
CREATE TABLE media_to_entity_table (
    id SERIAL PRIMARY KEY,
    id_entity INTEGER REFERENCES pottery_table(id_rep),
    id_media INTEGER REFERENCES media_table(id_media),
    entity_type VARCHAR(50) DEFAULT 'CERAMICA'
);

-- Indici per performance
CREATE INDEX idx_entity ON media_to_entity_table(id_entity, entity_type);
CREATE INDEX idx_decorated ON pottery_table(exdeco, intdeco);
```

### SQLite

```sql
-- Struttura identica ma senza SERIAL
CREATE TABLE pottery_table (
    id_rep INTEGER PRIMARY KEY AUTOINCREMENT,
    sito TEXT,
    area TEXT,
    us TEXT,
    form TEXT,
    exdeco TEXT DEFAULT 'No',
    intdeco TEXT DEFAULT 'No',
    description TEXT
);

CREATE TABLE media_table (
    id_media INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    filepath TEXT
);

CREATE TABLE media_to_entity_table (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_entity INTEGER,
    id_media INTEGER,
    entity_type TEXT DEFAULT 'CERAMICA',
    FOREIGN KEY (id_entity) REFERENCES pottery_table(id_rep),
    FOREIGN KEY (id_media) REFERENCES media_table(id_media)
);
```

### MySQL

```sql
CREATE TABLE pottery_table (
    id_rep INT AUTO_INCREMENT PRIMARY KEY,
    sito VARCHAR(100),
    area VARCHAR(50),
    us VARCHAR(50),
    form VARCHAR(100),
    exdeco ENUM('Yes', 'No') DEFAULT 'No',
    intdeco ENUM('Yes', 'No') DEFAULT 'No',
    description TEXT
) ENGINE=InnoDB;

CREATE TABLE media_table (
    id_media INT AUTO_INCREMENT PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    filepath TEXT
) ENGINE=InnoDB;

CREATE TABLE media_to_entity_table (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_entity INT,
    id_media INT,
    entity_type VARCHAR(50) DEFAULT 'CERAMICA',
    FOREIGN KEY (id_entity) REFERENCES pottery_table(id_rep),
    FOREIGN KEY (id_media) REFERENCES media_table(id_media)
) ENGINE=InnoDB;
```

### MongoDB (NoSQL)

MongoDB usa **documenti JSON** invece di tabelle relazionali. Ci sono due approcci principali:

#### Approccio 1: Documenti Embedded (Consigliato per semplicità)

Tutto in una sola collection, con le immagini embedded nel documento:

```javascript
// Collection: pottery
{
    "_id": ObjectId("..."),
    "id_rep": 1,
    "sito": "SitoA",
    "area": "Area1",
    "us": "US100",
    "form": "Ciotola",
    "fabric": "Impasto grossolano",
    "exdeco": "Yes",
    "intdeco": "No",
    "decoration_type": "Incisa",
    "period": "MBA",
    "description": "Frammento di ciotola decorata",

    // Immagini embedded direttamente
    "images": [
        {
            "id_media": 101,
            "filename": "DSC00401",
            "filepath": "/photos/DSC00401.jpg",
            "description": "Foto frontale"
        },
        {
            "id_media": 102,
            "filename": "DSC00402",
            "filepath": "/photos/DSC00402.jpg",
            "description": "Foto laterale"
        }
    ]
}
```

**Query per ceramiche decorate:**
```javascript
db.pottery.find({
    $or: [
        { "exdeco": "Yes" },
        { "intdeco": "Yes" }
    ]
})
```

#### Approccio 2: Collections Separate (Più flessibile)

Tre collections separate, simile al modello relazionale:

```javascript
// Collection: pottery
{
    "_id": ObjectId("..."),
    "id_rep": 1,
    "sito": "SitoA",
    "area": "Area1",
    "form": "Ciotola",
    "exdeco": "Yes",
    "intdeco": "No"
}

// Collection: media
{
    "_id": ObjectId("..."),
    "id_media": 101,
    "filename": "DSC00401",
    "filepath": "/photos/DSC00401.jpg"
}

// Collection: pottery_media (relazione)
{
    "_id": ObjectId("..."),
    "id_pottery": 1,        // riferimento a pottery.id_rep
    "id_media": 101,        // riferimento a media.id_media
    "entity_type": "CERAMICA"
}
```

**Query con aggregation pipeline:**
```javascript
db.pottery.aggregate([
    // Filtra ceramiche decorate
    { $match: { $or: [{ "exdeco": "Yes" }, { "intdeco": "Yes" }] } },

    // Join con pottery_media
    { $lookup: {
        from: "pottery_media",
        localField: "id_rep",
        foreignField: "id_pottery",
        as: "relations"
    }},

    // Unwind relations
    { $unwind: "$relations" },

    // Join con media
    { $lookup: {
        from: "media",
        localField: "relations.id_media",
        foreignField: "id_media",
        as: "media"
    }},

    // Unwind media
    { $unwind: "$media" }
])
```

#### Struttura Consigliata per MongoDB

```
┌─────────────────────────────────────────────────────────────────┐
│                    MONGODB - APPROCCIO EMBEDDED                  │
└─────────────────────────────────────────────────────────────────┘

    Collection: pottery
    ┌─────────────────────────────────────────┐
    │ {                                       │
    │   "_id": ObjectId("..."),               │
    │   "id_rep": 1,                          │
    │   "sito": "SitoA",                      │
    │   "exdeco": "Yes",                      │
    │   "images": [                    ◀──────│── Array di immagini
    │     {                                   │
    │       "id_media": 101,                  │
    │       "filename": "DSC001"              │
    │     },                                  │
    │     {                                   │
    │       "id_media": 102,                  │
    │       "filename": "DSC002"              │
    │     }                                   │
    │   ]                                     │
    │ }                                       │
    └─────────────────────────────────────────┘

    Vantaggi:
    ✓ Query semplici e veloci
    ✓ Tutto in un documento
    ✓ Nessun JOIN necessario

    Svantaggi:
    ✗ Duplicazione se stessa immagine usata più volte
    ✗ Limite 16MB per documento
```

#### Configurazione AI per MongoDB

Quando usi MongoDB, l'AI cercherà:

1. **Collection principale**: `pottery`, `ceramics`, `ceramiche`, `reperti`
2. **Campo decorazione**: `exdeco`, `intdeco`, `decorated`, `decorazione`
3. **Array immagini**: `images`, `media`, `photos`, `foto`
4. **Campi immagine**: `filename`, `filepath`, `path`, `url`

**Esempio configurazione manuale MongoDB:**
```json
{
    "database": {
        "type": "mongodb",
        "connection": {
            "host": "localhost",
            "port": 27017,
            "database": "archeologia"
        }
    },
    "pottery_collection": "pottery",
    "filter": {
        "$or": [
            { "exdeco": "Yes" },
            { "intdeco": "Yes" }
        ]
    },
    "image_field": "images",
    "image_filename_field": "filename"
}
```

---

## Struttura File Excel/CSV

### Opzione 1: Foglio Unico (Embedded)

Un solo foglio con tutti i dati:

| id | sito | area | us | form | exdeco | intdeco | image_filename |
|----|------|------|----|------|--------|---------|----------------|
| 1 | SitoA | Area1 | US100 | Ciotola | Yes | No | IMG_001.jpg |
| 2 | SitoA | Area1 | US100 | Piatto | Yes | Yes | IMG_002.jpg |
| 3 | SitoA | Area2 | US200 | Olla | No | No | IMG_003.jpg |

**Pattern immagini**: `{image_filename}` → cerca direttamente il file

### Opzione 2: Due Fogli Separati

**Foglio "Ceramiche":**

| id_rep | sito | area | form | exdeco | id_media |
|--------|------|------|------|--------|----------|
| 1 | SitoA | Area1 | Ciotola | Yes | 101 |
| 2 | SitoA | Area1 | Piatto | Yes | 102 |

**Foglio "Media":**

| id_media | filename | description |
|----------|----------|-------------|
| 101 | IMG_001.jpg | Foto frontale |
| 102 | IMG_002.jpg | Foto laterale |

### Opzione 3: Tre Fogli (Completa)

**Foglio "pottery"**: dati ceramiche
**Foglio "media"**: dati immagini
**Foglio "relations"**: collegamenti (id_pottery, id_media)

### Come Funzionano le Query AI con Excel/CSV

Quando l'AI analizza il tuo file Excel/CSV, genera **query in stile SQL** che vengono automaticamente interpretate ed eseguite sui tuoi dati. Questo significa che hai le stesse potenti capacità di filtraggio dei database reali.

**Esempio di query generata:**
```sql
SELECT DISTINCT ON (p.Numero_Inventario) p.Numero_Inventario as id, p.Sito as site,
       p.Area as area, p.US as us, p.Forma as form, p.Decorazione as decoration
FROM Ceramiche p
WHERE (p.exdeco = 'Yes' OR p.intdeco = 'Yes')
ORDER BY p.Numero_Inventario
```

**Cosa supporta il sistema:**
- `SELECT` con alias colonne (`colonna AS alias`)
- `FROM` (il nome del foglio è abbinato in modo case-insensitive)
- `WHERE` con condizioni:
  - Uguaglianza: `colonna = 'valore'`
  - Disuguaglianza: `colonna != 'valore'` o `colonna <> 'valore'`
  - Pattern LIKE: `colonna LIKE '%pattern%'`
  - Condizioni combinate: `AND`, `OR`
- `DISTINCT ON` (restituisce tutte le righe corrispondenti)

**Operatori supportati nella clausola WHERE:**
| Operatore | Esempio | Descrizione |
|-----------|---------|-------------|
| `=` | `exdeco = 'Yes'` | Corrispondenza esatta |
| `!=` o `<>` | `status != 'deleted'` | Diverso da |
| `LIKE` | `name LIKE '%ciotola%'` | Pattern match (case-insensitive) |
| `AND` | `exdeco = 'Yes' AND area = 'A1'` | Entrambe le condizioni |
| `OR` | `exdeco = 'Yes' OR intdeco = 'Yes'` | Una delle condizioni |

**Nota:** I nomi dei fogli sono abbinati in modo case-insensitive. Se il tuo foglio si chiama "CERAMICHE" e la query fa riferimento a "Ceramiche", funzionerà comunque correttamente.

---

## Pattern Nome File Immagini

Il sistema cerca le immagini usando pattern configurabili:

### Pattern Comuni

| Pattern | Esempio | Descrizione |
|---------|---------|-------------|
| `{id_media}_{filename}.png` | `101_IMG001.png` | ID + nome originale |
| `{filename}.jpg` | `IMG001.jpg` | Solo nome file |
| `{id_rep}.png` | `1.png` | Solo ID ceramica |
| `{sito}_{id_rep}.jpg` | `SitoA_1.jpg` | Sito + ID |

### Come Funziona la Ricerca

```
1. Applica il pattern: {id_media}_{filename}.png → 101_IMG001.png
2. Cerca nel percorso base: /path/to/images/101_IMG001.png
3. Se non trova, prova estensioni alternative: .jpg, .jpeg, .PNG
4. Se ancora non trova, cerca con glob: *101*
```

---

## Configurazione Manuale

Se l'AI non riconosce correttamente la struttura, puoi configurare manualmente:

### Parametri da Specificare

```json
{
  "database": {
    "type": "postgresql",
    "connection": {
      "host": "localhost",
      "port": 5432,
      "database": "nome_db",
      "user": "utente",
      "password": "password"
    }
  },
  "pottery_table": {
    "name": "nome_tabella_ceramiche",
    "id_field": "id_rep"
  },
  "media_table": {
    "name": "nome_tabella_media",
    "id_field": "id_media",
    "filename_field": "filename"
  },
  "relation": {
    "type": "junction",
    "junction_table": "nome_tabella_relazione",
    "pottery_fk": "id_entity",
    "media_fk": "id_media",
    "entity_type_field": "entity_type",
    "entity_type_value": "CERAMICA"
  },
  "filter_decorated": {
    "field": "exdeco",
    "value": "Yes",
    "operator": "=",
    "additional_condition": "OR p.intdeco = 'Yes'"
  },
  "images": {
    "base_path": "/path/to/images",
    "pattern": "{id_media}_{filename}.png"
  }
}
```

---

## Troubleshooting

### Problema: "Nessuna ceramica trovata"

**Cause possibili:**
1. Filtro decorazione errato
2. entity_type non corrisponde
3. Tabella di relazione vuota

**Soluzione:**
```sql
-- Verifica quante ceramiche decorate esistono
SELECT COUNT(*) FROM pottery_table WHERE exdeco = 'Yes' OR intdeco = 'Yes';

-- Verifica collegamenti media
SELECT COUNT(*) FROM media_to_entity_table WHERE entity_type = 'CERAMICA';
```

### Problema: "Immagini non trovate"

**Cause possibili:**
1. Pattern nome file errato
2. Percorso base errato
3. Estensione file diversa

**Soluzione:**
```bash
# Verifica i nomi file nella cartella
ls /path/to/images | head -10

# Confronta con i dati nel database
SELECT id_media, filename FROM media_table LIMIT 10;
```

### Problema: "Troppe immagini" (duplicati)

**Causa:** Una ceramica ha più immagini associate

**Soluzione:** Attiva l'opzione "Una sola immagine per ceramica" (DISTINCT ON)

### Problema: "column 'xxx' does not exist"

**Causa:** Nome colonna errato nella query

**Soluzione:** Verifica i nomi esatti delle colonne:
```sql
-- PostgreSQL
SELECT column_name FROM information_schema.columns
WHERE table_name = 'pottery_table';

-- SQLite
PRAGMA table_info(pottery_table);
```

---

## Checklist Pre-Classificazione

Prima di avviare la classificazione, verifica:

- [ ] La tabella ceramiche ha un campo ID univoco
- [ ] Esiste un modo per identificare le ceramiche decorate
- [ ] Le immagini sono accessibili nel percorso specificato
- [ ] I nomi file delle immagini corrispondono al pattern
- [ ] Se usi junction table, il campo entity_type è corretto
- [ ] La query preview mostra il numero corretto di record

---

## Supporto

Per problemi o domande:
- Controlla i log del server per errori dettagliati
- Usa la funzione "Modifica Manualmente" per correggere la configurazione AI
- Verifica la query generata prima di avviare la classificazione

---

*Documentazione Ceramica Classifier v1.0*
