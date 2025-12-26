# File di Esempio - Ceramica Classifier

Questa cartella contiene file di esempio con diverse strutture dati che il classificatore può gestire.

Tutti i file contengono **50 ceramiche decorate** estratte dal database khutm2.

---

## 1. esempio_utente_semplice.xlsx / .csv

**Scenario**: Un utente che registra i propri dati in un semplice foglio Excel con nomi colonne in italiano.

### Struttura

| Colonna | Descrizione | Esempio |
|---------|-------------|---------|
| Numero_Inventario | ID univoco | 1 |
| Sito_Archeologico | Nome sito | Al-Khutm |
| Area_Scavo | Area | A |
| Unita_Stratigrafica | US | 100 |
| Tipo_Forma | Forma ceramica | Bowl |
| Impasto | Tipo impasto | Fine |
| Decorazione_Esterna | Sì/No | Sì |
| Decorazione_Interna | Sì/No | No |
| Tipo_Decorazione | Descrizione | Incisa |
| Cronologia | Datazione | Iron Age II |
| Note | Note libere | ... |
| File_Immagine | Nome file completo | 2359_DSC01166.png |

### Configurazione AI

```
Tabella: Sheet1 (o Ceramiche)
Campo ID: Numero_Inventario
Campo decorazione: Decorazione_Esterna = 'Sì' OR Decorazione_Interna = 'Sì'
Pattern immagine: {File_Immagine}
```

---

## 2. esempio_due_fogli.xlsx

**Scenario**: Utente più organizzato che separa ceramiche e immagini in due fogli.

### Foglio "Pottery"

| Colonna | Descrizione |
|---------|-------------|
| ID | ID ceramica |
| Site | Sito |
| Area | Area |
| SU | Unità stratigrafica |
| Shape | Forma |
| Fabric | Impasto |
| Ext_Decoration | Yes/No |
| Int_Decoration | Yes/No |
| Decoration_Type | Tipo decorazione |
| Dating | Datazione |
| Notes | Note |
| Image_ID | → FK a foglio Images |

### Foglio "Images"

| Colonna | Descrizione |
|---------|-------------|
| Image_ID | ID immagine |
| Filename | Nome file originale |
| Full_Path | Nome file completo |

### Configurazione AI

```
Tabella ceramiche: Pottery
Tabella media: Images
Relazione: DIRECT (Pottery.Image_ID → Images.Image_ID)
Campo decorazione: Ext_Decoration = 'Yes' OR Int_Decoration = 'Yes'
Pattern immagine: {Full_Path}
```

---

## 3. esempio_minimo.csv

**Scenario**: Struttura minimalista con solo i dati essenziali.

### Struttura

```csv
id,decorated,image
1,yes,2359_DSC01166 - Copia.png
2,yes,2328_DSC01143.png
3,yes,5375_DSC01918 - DSC01921.png
```

| Colonna | Descrizione |
|---------|-------------|
| id | ID univoco |
| decorated | yes/no |
| image | Nome file immagine |

### Configurazione AI

```
Tabella: (nome file senza estensione)
Campo ID: id
Campo decorazione: decorated = 'yes'
Pattern immagine: {image}
```

---

## 4. esempio_catalogo_museo.xlsx

**Scenario**: Catalogo museale con codici inventario formattati e descrizioni strutturate.

### Struttura

| Colonna | Descrizione | Esempio |
|---------|-------------|---------|
| Codice_Reperto | Codice museo | KTM-0001 |
| Provenienza | Sito + Area + US | Al-Khutm - A - US100 |
| Categoria | Categoria reperto | Ceramica |
| Sottocategoria | Forma | Bowl |
| Materiale | Impasto | Fine |
| Stato_Decorazione | Descrizione decorazione | Decorato (est+int) |
| Datazione | Cronologia | Iron Age II |
| Descrizione | Note | ... |
| Foto_Principale | Nome file | DSC01166.png |
| ID_Foto | ID numerico foto | 2359 |

### Configurazione AI

```
Tabella: Catalogo
Campo ID: Codice_Reperto (o ID_Foto)
Campo decorazione: Stato_Decorazione LIKE '%Decorato%'
Pattern immagine: {ID_Foto}_{Foto_Principale}
```

---

## Come Testare

1. Apri http://localhost:5002
2. Seleziona tipo database: **Excel** o **CSV**
3. Inserisci il percorso del file
4. Clicca "Analizza con AI" o configura manualmente
5. Imposta il percorso immagini: `/Volumes/extesione4T/KTM2025/photolog/original`
6. Avvia la classificazione

---

## Note

- I nomi file delle immagini corrispondono a quelli in `/Volumes/extesione4T/KTM2025/photolog/original`
- Il pattern più comune è `{id_media}_{filename}.png`
- Per i file Excel, il sistema legge automaticamente tutti i fogli
- I valori di decorazione possono essere: Yes/No, Sì/No, yes/no, true/false, 1/0
