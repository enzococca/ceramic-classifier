# Data Structure Guide for Ceramica Classifier

This guide explains how to structure your data (database or Excel/CSV files) so that the AI classification system can analyze them correctly.

---

## Table of Contents

1. [Fundamental Concepts](#fundamental-concepts)
2. [Ideal Database Schema](#ideal-database-schema)
3. [Types of Pottery-Image Relationships](#types-of-relationships)
4. [Required and Optional Fields](#required-and-optional-fields)
5. [Examples by Database Type](#examples-by-database-type)
6. [Excel/CSV File Structure](#excelcsv-file-structure)
7. [Manual Configuration](#manual-configuration)
8. [Troubleshooting](#troubleshooting)

---

## Fundamental Concepts

The classification system needs to identify three main elements:

```
┌─────────────────────────────────────────────────────────────────┐
│                    REQUIRED ELEMENTS                             │
├─────────────────────────────────────────────────────────────────┤
│  1. POTTERY TABLE     → The pottery/artifact data               │
│  2. MEDIA TABLE       → References to images                    │
│  3. RELATIONSHIP      → How pottery and images are linked       │
└─────────────────────────────────────────────────────────────────┘
```

---

## Ideal Database Schema

### Recommended Structure (3 Tables)

```
┌──────────────────────┐         ┌──────────────────────┐
│   POTTERY_TABLE      │         │    MEDIA_TABLE       │
├──────────────────────┤         ├──────────────────────┤
│ id_rep (PK)          │         │ id_media (PK)        │
│ site                 │         │ filename             │
│ area                 │         │ filepath             │
│ su                   │         │ description          │
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
          │         │   (Junction Table)           │
          │         ├──────────────────────────────┤
          └─────────│ id_entity (FK → pottery)     │
                    │ id_media (FK → media)        │
                    │ entity_type ('CERAMICA')     │
                    └──────────────────────────────┘
```

### Why Use a Junction Table?

The junction table allows:
- **Many-to-many**: One pottery item can have multiple images, one image can be associated with multiple records
- **Flexibility**: The same media system can serve pottery, stratigraphic units, structures, etc.
- **Filtering**: The `entity_type` field allows filtering only pottery images

---

## Types of Relationships

The system supports three types of relationships between pottery and images:

### 1. JUNCTION (Recommended)

```
┌─────────────┐     ┌─────────────────┐     ┌─────────────┐
│  POTTERY    │────▶│  JUNCTION TABLE │◀────│   MEDIA     │
│  (id_rep)   │     │  (id_entity,    │     │  (id_media) │
└─────────────┘     │   id_media,     │     └─────────────┘
                    │   entity_type)  │
                    └─────────────────┘

Example Query:
SELECT p.*, m.filename
FROM pottery_table p
JOIN media_to_entity r ON r.id_entity = p.id_rep AND r.entity_type = 'CERAMICA'
JOIN media_table m ON m.id_media = r.id_media
```

**Advantages**: Flexible, scalable, professional standard
**Use for**: Complex archaeological databases, multi-entity systems

### 2. DIRECT (Direct Relationship)

```
┌─────────────────────┐     ┌─────────────┐
│      POTTERY        │────▶│   MEDIA     │
│  (id_rep,           │     │  (id_media) │
│   id_media → FK)    │     └─────────────┘
└─────────────────────┘

Example Query:
SELECT p.*, m.filename
FROM pottery_table p
JOIN media_table m ON m.id_media = p.id_media
```

**Advantages**: Simple, fast
**Disadvantages**: Only one image per pottery item
**Use for**: Simple catalogs, basic inventories

### 3. EMBEDDED (Embedded Image)

```
┌─────────────────────────────┐
│         POTTERY             │
│  (id_rep,                   │
│   image_path,               │  ← Direct image path
│   image_filename)           │
└─────────────────────────────┘

Example Query:
SELECT * FROM pottery_table WHERE decorated = 'Yes'
```

**Advantages**: Very simple, everything in one table
**Disadvantages**: Less flexible, data duplication
**Use for**: Excel, CSV, minimal databases

---

## Required and Optional Fields

### Pottery Table (POTTERY)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` / `id_rep` | INTEGER | **Yes** | Unique identifier |
| `site` | TEXT | No | Archaeological site name |
| `area` | TEXT | No | Excavation area |
| `su` | TEXT | No | Stratigraphic unit |
| `form` | TEXT | No | Pottery form |
| `fabric` | TEXT | No | Fabric type |
| `exdeco` | TEXT | **Recommended** | External decoration (Yes/No) |
| `intdeco` | TEXT | **Recommended** | Internal decoration (Yes/No) |
| `decoration_type` | TEXT | No | Type of decoration |
| `period` | TEXT | No | Chronological period |
| `description` / `notes` | TEXT | No | Free description |

### Decoration Field Values

The system recognizes these values as "decorated":

```
✓ 'Yes', 'YES', 'yes'
✓ 'Si', 'SI', 'si', 'Sì'
✓ 'True', 'true', '1', 1
✓ Any non-empty value (if configured)
```

And these as "not decorated":
```
✗ 'No', 'NO', 'no'
✗ 'False', 'false', '0', 0
✗ NULL, empty
```

### Media Table

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id_media` | INTEGER | **Yes** | Unique identifier |
| `filename` | TEXT | **Yes** | Image filename |
| `filepath` | TEXT | No | Full path (optional) |
| `description` | TEXT | No | Image description |

### Junction Table

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id_entity` | INTEGER | **Yes** | FK to pottery |
| `id_media` | INTEGER | **Yes** | FK to media |
| `entity_type` | TEXT | **Recommended** | Entity type ('CERAMICA', 'POTTERY', etc.) |

---

## Examples by Database Type

### PostgreSQL

```sql
-- Pottery table
CREATE TABLE pottery_table (
    id_rep SERIAL PRIMARY KEY,
    site VARCHAR(100),
    area VARCHAR(50),
    su VARCHAR(50),
    form VARCHAR(100),
    fabric VARCHAR(100),
    exdeco VARCHAR(10) DEFAULT 'No',
    intdeco VARCHAR(10) DEFAULT 'No',
    decoration_type VARCHAR(200),
    period VARCHAR(100),
    description TEXT
);

-- Media table
CREATE TABLE media_table (
    id_media SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    filepath TEXT,
    description TEXT
);

-- Junction table
CREATE TABLE media_to_entity_table (
    id SERIAL PRIMARY KEY,
    id_entity INTEGER REFERENCES pottery_table(id_rep),
    id_media INTEGER REFERENCES media_table(id_media),
    entity_type VARCHAR(50) DEFAULT 'CERAMICA'
);

-- Indexes for performance
CREATE INDEX idx_entity ON media_to_entity_table(id_entity, entity_type);
CREATE INDEX idx_decorated ON pottery_table(exdeco, intdeco);
```

### SQLite

```sql
CREATE TABLE pottery_table (
    id_rep INTEGER PRIMARY KEY AUTOINCREMENT,
    site TEXT,
    area TEXT,
    su TEXT,
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
    site VARCHAR(100),
    area VARCHAR(50),
    su VARCHAR(50),
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

MongoDB uses **JSON documents** instead of relational tables. There are two main approaches:

#### Approach 1: Embedded Documents (Recommended for simplicity)

Everything in a single collection, with images embedded in the document:

```javascript
// Collection: pottery
{
    "_id": ObjectId("..."),
    "id_rep": 1,
    "site": "SiteA",
    "area": "Area1",
    "su": "SU100",
    "form": "Bowl",
    "fabric": "Coarse ware",
    "exdeco": "Yes",
    "intdeco": "No",
    "decoration_type": "Incised",
    "period": "MBA",
    "description": "Decorated bowl fragment",

    // Images embedded directly
    "images": [
        {
            "id_media": 101,
            "filename": "DSC00401",
            "filepath": "/photos/DSC00401.jpg",
            "description": "Front view"
        },
        {
            "id_media": 102,
            "filename": "DSC00402",
            "filepath": "/photos/DSC00402.jpg",
            "description": "Side view"
        }
    ]
}
```

**Query for decorated pottery:**
```javascript
db.pottery.find({
    $or: [
        { "exdeco": "Yes" },
        { "intdeco": "Yes" }
    ]
})
```

#### Approach 2: Separate Collections (More flexible)

Three separate collections, similar to the relational model:

```javascript
// Collection: pottery
{
    "_id": ObjectId("..."),
    "id_rep": 1,
    "site": "SiteA",
    "area": "Area1",
    "form": "Bowl",
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

// Collection: pottery_media (relationship)
{
    "_id": ObjectId("..."),
    "id_pottery": 1,        // reference to pottery.id_rep
    "id_media": 101,        // reference to media.id_media
    "entity_type": "CERAMICA"
}
```

---

## Excel/CSV File Structure

### Option 1: Single Sheet (Embedded)

One sheet with all data:

| id | site | area | su | form | exdeco | intdeco | image_filename |
|----|------|------|----|------|--------|---------|----------------|
| 1 | SiteA | Area1 | SU100 | Bowl | Yes | No | IMG_001.jpg |
| 2 | SiteA | Area1 | SU100 | Plate | Yes | Yes | IMG_002.jpg |
| 3 | SiteA | Area2 | SU200 | Jar | No | No | IMG_003.jpg |

**Image pattern**: `{image_filename}` → searches directly for the file

### Option 2: Two Separate Sheets

**Sheet "Pottery":**

| id_rep | site | area | form | exdeco | id_media |
|--------|------|------|------|--------|----------|
| 1 | SiteA | Area1 | Bowl | Yes | 101 |
| 2 | SiteA | Area1 | Plate | Yes | 102 |

**Sheet "Media":**

| id_media | filename | description |
|----------|----------|-------------|
| 101 | IMG_001.jpg | Front view |
| 102 | IMG_002.jpg | Side view |

### Option 3: Three Sheets (Complete)

**Sheet "pottery"**: pottery data
**Sheet "media"**: image data
**Sheet "relations"**: links (id_pottery, id_media)

### How AI Queries Work with Excel/CSV

When the AI analyzes your Excel/CSV file, it generates **SQL-style queries** that are automatically parsed and executed on your data. This means you get the same powerful filtering capabilities as with real databases.

**Example generated query:**
```sql
SELECT DISTINCT ON (p.Numero_Inventario) p.Numero_Inventario as id, p.Sito as site,
       p.Area as area, p.US as us, p.Forma as form, p.Decorazione as decoration
FROM Ceramiche p
WHERE (p.exdeco = 'Yes' OR p.intdeco = 'Yes')
ORDER BY p.Numero_Inventario
```

**What the system supports:**
- `SELECT` with column aliases (`column AS alias`)
- `FROM` clause (sheet name matching is case-insensitive)
- `WHERE` clause with conditions:
  - Equality: `column = 'value'`
  - Inequality: `column != 'value'` or `column <> 'value'`
  - LIKE patterns: `column LIKE '%pattern%'`
  - Combined conditions: `AND`, `OR`
- `DISTINCT ON` (returns all matching rows)

**Supported operators in WHERE clause:**
| Operator | Example | Description |
|----------|---------|-------------|
| `=` | `exdeco = 'Yes'` | Exact match |
| `!=` or `<>` | `status != 'deleted'` | Not equal |
| `LIKE` | `name LIKE '%bowl%'` | Pattern match (case-insensitive) |
| `AND` | `exdeco = 'Yes' AND area = 'A1'` | Both conditions |
| `OR` | `exdeco = 'Yes' OR intdeco = 'Yes'` | Either condition |

**Note:** Sheet names are matched case-insensitively. If your sheet is named "CERAMICHE" and the query references "Ceramiche", it will still work correctly.

---

## Image Filename Patterns

The system searches for images using configurable patterns:

### Common Patterns

| Pattern | Example | Description |
|---------|---------|-------------|
| `{id_media}_{filename}.png` | `101_IMG001.png` | ID + original name |
| `{filename}.jpg` | `IMG001.jpg` | Filename only |
| `{id_rep}.png` | `1.png` | Pottery ID only |
| `{site}_{id_rep}.jpg` | `SiteA_1.jpg` | Site + ID |

### How the Search Works

```
1. Apply pattern: {id_media}_{filename}.png → 101_IMG001.png
2. Search in base path: /path/to/images/101_IMG001.png
3. If not found, try alternative extensions: .jpg, .jpeg, .PNG
4. If still not found, search with glob: *101*
```

---

## Manual Configuration

If AI doesn't correctly recognize the structure, you can configure manually:

### Parameters to Specify

```json
{
  "database": {
    "type": "postgresql",
    "connection": {
      "host": "localhost",
      "port": 5432,
      "database": "db_name",
      "user": "username",
      "password": "password"
    }
  },
  "pottery_table": {
    "name": "pottery_table_name",
    "id_field": "id_rep"
  },
  "media_table": {
    "name": "media_table_name",
    "id_field": "id_media",
    "filename_field": "filename"
  },
  "relation": {
    "type": "junction",
    "junction_table": "junction_table_name",
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

### Problem: "No pottery found"

**Possible causes:**
1. Wrong decoration filter
2. entity_type doesn't match
3. Junction table is empty

**Solution:**
```sql
-- Check how many decorated pottery exist
SELECT COUNT(*) FROM pottery_table WHERE exdeco = 'Yes' OR intdeco = 'Yes';

-- Check media links
SELECT COUNT(*) FROM media_to_entity_table WHERE entity_type = 'CERAMICA';
```

### Problem: "Images not found"

**Possible causes:**
1. Wrong filename pattern
2. Wrong base path
3. Different file extension

**Solution:**
```bash
# Check filenames in folder
ls /path/to/images | head -10

# Compare with database data
SELECT id_media, filename FROM media_table LIMIT 10;
```

### Problem: "Too many images" (duplicates)

**Cause:** One pottery item has multiple associated images

**Solution:** Enable "One image per pottery" option (DISTINCT ON)

### Problem: "column 'xxx' does not exist"

**Cause:** Wrong column name in query

**Solution:** Check exact column names:
```sql
-- PostgreSQL
SELECT column_name FROM information_schema.columns
WHERE table_name = 'pottery_table';

-- SQLite
PRAGMA table_info(pottery_table);
```

---

## Pre-Classification Checklist

Before starting classification, verify:

- [ ] Pottery table has a unique ID field
- [ ] There's a way to identify decorated pottery
- [ ] Images are accessible at the specified path
- [ ] Image filenames match the pattern
- [ ] If using junction table, entity_type field is correct
- [ ] Query preview shows correct number of records

---

## Support

For problems or questions:
- Check server logs for detailed errors
- Use "Edit Manually" function to correct AI configuration
- Verify the generated query before starting classification

---

*Ceramica Classifier Documentation v1.0*
