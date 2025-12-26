# Diagrammi Schema Database - Ceramica Classifier

## Schema Relazionale Completo

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           SCHEMA IDEALE                                      │
└─────────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────────────┐
    │      POTTERY_TABLE      │
    │    (Tabella Ceramiche)  │
    ├─────────────────────────┤
    │ * id_rep        [PK]    │───────┐
    │   sito          [TEXT]  │       │
    │   area          [TEXT]  │       │
    │   us            [TEXT]  │       │
    │   form          [TEXT]  │       │
    │   fabric        [TEXT]  │       │
    │   exdeco        [TEXT]  │       │    ┌─────────────────────────┐
    │   intdeco       [TEXT]  │       │    │   MEDIA_TO_ENTITY       │
    │   decoration    [TEXT]  │       │    │  (Tabella Relazione)    │
    │   period        [TEXT]  │       │    ├─────────────────────────┤
    │   description   [TEXT]  │       └───▶│   id_entity    [FK]     │
    └─────────────────────────┘            │   id_media     [FK]     │◀───┐
                                           │   entity_type  [TEXT]   │    │
                                           │   ('CERAMICA')          │    │
                                           └─────────────────────────┘    │
                                                                          │
    ┌─────────────────────────┐                                           │
    │      MEDIA_TABLE        │                                           │
    │    (Tabella Immagini)   │                                           │
    ├─────────────────────────┤                                           │
    │ * id_media      [PK]    │───────────────────────────────────────────┘
    │   filename      [TEXT]  │
    │   filepath      [TEXT]  │
    │   description   [TEXT]  │
    └─────────────────────────┘


    LEGENDA:
    ─────────
    [PK] = Chiave Primaria (Primary Key)
    [FK] = Chiave Esterna (Foreign Key)
    *    = Campo obbligatorio
    ───▶ = Relazione (freccia indica direzione FK)
```

---

## Tipi di Relazione

### Tipo 1: JUNCTION (Molti-a-Molti)

```
    POTTERY                    JUNCTION                    MEDIA
    ┌──────────┐              ┌──────────┐              ┌──────────┐
    │ id_rep   │◀────────────▶│id_entity │              │ id_media │
    │          │              │id_media  │◀────────────▶│ filename │
    │ exdeco   │              │entity_   │              │          │
    │          │              │  type    │              │          │
    └──────────┘              └──────────┘              └──────────┘

    Vantaggi:
    ✓ Una ceramica può avere N immagini
    ✓ entity_type filtra per tipo di entità
    ✓ Struttura professionale e scalabile
```

### Tipo 2: DIRECT (Uno-a-Uno)

```
    POTTERY                              MEDIA
    ┌──────────────┐                    ┌──────────┐
    │ id_rep       │                    │ id_media │
    │ id_media [FK]│───────────────────▶│ filename │
    │ exdeco       │                    │          │
    └──────────────┘                    └──────────┘

    Vantaggi:
    ✓ Semplice
    ✓ Query veloci

    Svantaggi:
    ✗ Una sola immagine per ceramica
```

### Tipo 3: EMBEDDED (Tutto in una tabella)

```
    POTTERY (unica tabella)
    ┌────────────────────────────┐
    │ id_rep                     │
    │ exdeco                     │
    │ image_filename  ◀──────────│── Nome file immagine diretto
    │ image_path                 │
    └────────────────────────────┘

    Vantaggi:
    ✓ Semplicissimo
    ✓ Ideale per Excel/CSV

    Svantaggi:
    ✗ Duplicazione dati
    ✗ Poco flessibile
```

---

## Flusso dei Dati

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         FLUSSO CLASSIFICAZIONE                           │
└──────────────────────────────────────────────────────────────────────────┘

     ┌──────────────┐
     │   DATABASE   │
     │  PostgreSQL  │
     │    MySQL     │
     │   SQLite     │
     │    Excel     │
     │     CSV      │
     └──────┬───────┘
            │
            ▼
     ┌──────────────┐
     │   AI/CONFIG  │  ◀─── Analizza schema o configurazione manuale
     │              │
     │ - Identifica │
     │   tabelle    │
     │ - Trova      │
     │   relazioni  │
     │ - Genera     │
     │   query      │
     └──────┬───────┘
            │
            ▼
     ┌──────────────┐
     │    QUERY     │
     │              │
     │ SELECT ...   │
     │ FROM pottery │
     │ JOIN media   │
     │ WHERE decor  │
     └──────┬───────┘
            │
            ▼
     ┌──────────────┐     ┌──────────────┐
     │   RESULTS    │────▶│   IMMAGINI   │
     │              │     │              │
     │ id: 1        │     │ /path/to/    │
     │ media_id: 10 │     │ 10_DSC01.png │
     │ filename:    │     │              │
     │   DSC001     │     │              │
     └──────────────┘     └──────┬───────┘
                                 │
                                 ▼
                          ┌──────────────┐
                          │   ML API     │
                          │              │
                          │ Classifica   │
                          │ l'immagine   │
                          │              │
                          │ → Periodo    │
                          │ → Decoraz.   │
                          │ → Simili     │
                          └──────────────┘
```

---

## Pattern Nome File Immagini

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    RICERCA FILE IMMAGINE                                │
└─────────────────────────────────────────────────────────────────────────┘

Database Record:
┌────────────────────────────┐
│ id_media: 101              │
│ filename: DSC00401         │
└────────────────────────────┘
            │
            │  Pattern: {id_media}_{filename}.png
            │
            ▼
┌────────────────────────────┐
│ 101_DSC00401.png           │  ◀── File generato dal pattern
└────────────────────────────┘
            │
            │  Cerca in: /path/to/images/
            │
            ▼
┌────────────────────────────┐
│ RICERCA SEQUENZIALE:       │
│                            │
│ 1. 101_DSC00401.png   ✓/✗  │
│ 2. 101_DSC00401.jpg   ✓/✗  │
│ 3. 101_DSC00401.PNG   ✓/✗  │
│ 4. *101*              ✓/✗  │  ◀── Fallback glob
└────────────────────────────┘
```

---

## Struttura Excel Consigliata

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           FOGLIO EXCEL                                   │
└─────────────────────────────────────────────────────────────────────────┘

Opzione A: Foglio Unico
──────────────────────────────────────────────────────────────────────────

     A          B        C       D       E          F         G
┌─────────┬────────┬───────┬───────┬─────────┬─────────┬────────────────┐
│   ID    │  SITO  │ AREA  │ FORMA │ DECORATA│ PERIODO │ FILE_IMMAGINE  │
├─────────┼────────┼───────┼───────┼─────────┼─────────┼────────────────┤
│    1    │ SitoA  │ Area1 │Ciotola│   Yes   │  MBA    │ IMG_0001.jpg   │
│    2    │ SitoA  │ Area1 │ Piatto│   Yes   │  LBA    │ IMG_0002.jpg   │
│    3    │ SitoA  │ Area2 │  Olla │   No    │   IA    │ IMG_0003.jpg   │
└─────────┴────────┴───────┴───────┴─────────┴─────────┴────────────────┘


Opzione B: Due Fogli
──────────────────────────────────────────────────────────────────────────

FOGLIO 1: "Ceramiche"
     A          B        C       D       E          F
┌─────────┬────────┬───────┬───────┬─────────┬─────────┐
│   ID    │  SITO  │ AREA  │ FORMA │ DECORATA│ ID_MEDIA│
├─────────┼────────┼───────┼───────┼─────────┼─────────┤
│    1    │ SitoA  │ Area1 │Ciotola│   Yes   │   101   │
│    2    │ SitoA  │ Area1 │ Piatto│   Yes   │   102   │
└─────────┴────────┴───────┴───────┴─────────┴─────────┘


FOGLIO 2: "Media"
     A          B              C
┌─────────┬────────────┬─────────────┐
│ ID_MEDIA│  FILENAME  │ DESCRIZIONE │
├─────────┼────────────┼─────────────┤
│   101   │ IMG_0001   │ Foto front. │
│   102   │ IMG_0002   │ Foto later. │
└─────────┴────────────┴─────────────┘
```

---

## MongoDB (NoSQL) Schema

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         MONGODB STRUCTURES                               │
└─────────────────────────────────────────────────────────────────────────┘


APPROCCIO 1: EMBEDDED (Consigliato)
═══════════════════════════════════════════════════════════════════════════

    Collection: pottery
    ┌─────────────────────────────────────────────────────────────────┐
    │ {                                                               │
    │   "_id": ObjectId("507f1f77bcf86cd799439011"),                 │
    │   "id_rep": 1,                                                  │
    │   "sito": "Khirbet al-Mudayna",                                │
    │   "area": "A",                                                  │
    │   "us": "100",                                                  │
    │   "form": "Ciotola",                                           │
    │   "exdeco": "Yes",                                              │
    │   "intdeco": "No",                                              │
    │   "period": "Iron Age II",                                      │
    │                                                                 │
    │   "images": [  ◀─────────────────── Array embedded              │
    │     {                                                           │
    │       "id_media": 101,                                          │
    │       "filename": "DSC00401",                                   │
    │       "type": "front"                                           │
    │     },                                                          │
    │     {                                                           │
    │       "id_media": 102,                                          │
    │       "filename": "DSC00402",                                   │
    │       "type": "side"                                            │
    │     }                                                           │
    │   ]                                                             │
    │ }                                                               │
    └─────────────────────────────────────────────────────────────────┘

    Query: db.pottery.find({ "exdeco": "Yes" })


APPROCCIO 2: COLLECTIONS SEPARATE
═══════════════════════════════════════════════════════════════════════════

    Collection: pottery          Collection: pottery_media
    ┌──────────────────┐        ┌──────────────────────┐
    │ {                │        │ {                    │
    │   "id_rep": 1,   │◀───────│   "id_pottery": 1,   │
    │   "sito": "...", │        │   "id_media": 101,   │───────┐
    │   "exdeco": "Yes"│        │   "type": "CERAMICA" │       │
    │ }                │        │ }                    │       │
    └──────────────────┘        └──────────────────────┘       │
                                                               │
                                                               ▼
                                Collection: media
                                ┌──────────────────────┐
                                │ {                    │
                                │   "id_media": 101,   │
                                │   "filename": "...", │
                                │   "filepath": "..."  │
                                │ }                    │
                                └──────────────────────┘

    Query: db.pottery.aggregate([
        { $match: { "exdeco": "Yes" } },
        { $lookup: { from: "pottery_media", ... } },
        { $lookup: { from: "media", ... } }
    ])


CONFRONTO APPROCCI MONGODB
═══════════════════════════════════════════════════════════════════════════

    ┌─────────────────────┬─────────────────────┬─────────────────────┐
    │      ASPETTO        │      EMBEDDED       │     SEPARATE        │
    ├─────────────────────┼─────────────────────┼─────────────────────┤
    │ Complessità Query   │   ✓ Semplice        │   ✗ Complessa       │
    │ Performance         │   ✓ Veloce          │   ✗ Più lenta       │
    │ Flessibilità        │   ✗ Limitata        │   ✓ Alta            │
    │ Duplicazione dati   │   ✗ Possibile       │   ✓ Nessuna         │
    │ Limite documento    │   ✗ 16MB max        │   ✓ Nessun limite   │
    │ Uso consigliato     │   Cataloghi piccoli │   Archivi grandi    │
    └─────────────────────┴─────────────────────┴─────────────────────┘
```

---

## Checklist Visuale

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     PRE-CLASSIFICAZIONE CHECKLIST                        │
└─────────────────────────────────────────────────────────────────────────┘

    DATI
    ════
    [ ] Tabella ceramiche con ID univoco
    [ ] Campo per identificare ceramiche decorate
    [ ] Dati campione inseriti correttamente

    IMMAGINI
    ════════
    [ ] Cartella immagini accessibile
    [ ] Nomi file corrispondono al pattern
    [ ] Formato supportato (jpg, png, jpeg)

    RELAZIONI
    ═════════
    [ ] Collegamento ceramiche → immagini funzionante
    [ ] Se junction: entity_type configurato
    [ ] Query preview mostra N record corretto

    CONFIGURAZIONE
    ══════════════
    [ ] Percorso base immagini impostato
    [ ] Pattern nome file corretto
    [ ] Filtro decorazione attivo
    [ ] Opzione DISTINCT ON se necessario
```

---

*Diagrammi Ceramica Classifier v1.0*
