# Quick Start - Ceramica Classifier

## Minimum Requirements

To run the classification, you need:

### 1. Pottery Data

A table/sheet with at least:
- **Unique ID** for each pottery item
- **Decoration field** for filtering (optional but recommended)

### 2. Images

- Folder with pottery images
- Filenames that allow matching to records

### 3. Linking

A way to link each pottery item to its image.

---

## Configuration in 3 Steps

### Step 1: Database Connection

```
Type: PostgreSQL / MySQL / SQLite / Excel / CSV
Credentials: host, port, database, user, password
```

### Step 2: AI Analysis or Manual Configuration

AI will automatically analyze:
- Which table contains the pottery
- Which table contains the images
- How they are linked
- How to filter decorated pottery

### Step 3: Image Path

Specify:
- Base image folder
- Filename pattern (e.g., `{id_media}_{filename}.png`)

---

## Recommended Minimum Structure

### SQL Database

```
TABLE: pottery
├── id (INTEGER, primary key)
├── decorated (TEXT: 'Yes'/'No')
└── image (TEXT: filename)

IMAGE FOLDER:
└── /path/to/images/
    ├── 1.jpg
    ├── 2.jpg
    └── ...
```

### Excel File

```
SHEET: Pottery
├── Column A: ID
├── Column B: Decorated (Yes/No)
├── Column C: ImageName
└── ...

IMAGE FOLDER:
└── /path/to/images/
    ├── IMG001.jpg
    ├── IMG002.jpg
    └── ...
```

---

## Generated Query Examples

### Simple Case (embedded)
```sql
SELECT * FROM pottery WHERE decorated = 'Yes'
```

### Case with Media Table
```sql
SELECT p.*, m.filename
FROM pottery p
JOIN media m ON m.id = p.id_media
WHERE p.decorated = 'Yes'
```

### Complete Case (junction)
```sql
SELECT DISTINCT ON (p.id) p.*, m.filename
FROM pottery p
JOIN relations r ON r.id_pottery = p.id AND r.type = 'CERAMICA'
JOIN media m ON m.id = r.id_media
WHERE p.decorated = 'Yes'
```

---

## Classification Options

| Option | Description |
|--------|-------------|
| One image per pottery | Classify each pottery once |
| All images | Classify every single image |

---

## Common Troubleshooting

| Problem | Solution |
|---------|----------|
| 0 pottery found | Check decoration filter |
| Images not found | Check pattern and path |
| Too many records | Enable "One image per pottery" |
| Query error | Manually modify configuration |
