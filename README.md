# Ceramica Classifier

**ML Classification System for Umm an-Nar to Wadi Suq, Late Bronze Age, Iron Age**

A Machine Learning-based system for automatically classifying decorated pottery sherds from Oman archaeological excavations. The system compares pottery decorations with reference collections to identify typological parallels and suggest chronological attributions.

## Features

- **Universal Database Support**: PostgreSQL, MySQL, SQLite, MongoDB, Excel, CSV
- **AI-Powered Schema Analysis**: Automatically detects table structures and relationships
- **ML Classification**: Uses computer vision to find similar pottery decorations
- **Interactive Web Interface**: Real-time classification with visual feedback
- **Multi-language Documentation**: English and Italian support
- **Batch Processing**: Classify entire collections with progress tracking

## Screenshots

![Interface Preview](docs/screenshot.png)

## Requirements

- Python 3.10+
- pip (Python package manager)

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/enzococca/ceramic-classifier.git
cd ceramic-classifier
```

### 2. Create a virtual environment (recommended)

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables (optional)

Create a `.env` file for custom configuration:

```bash
# Anthropic API key for AI schema analysis
ANTHROPIC_API_KEY=your_api_key_here

# ML API URL (default: Railway deployment)
ML_API_URL=https://pottery-comparison-oman.up.railway.app/api/ml/similar

# Server port
PORT=5002
```

### 5. Run the application

```bash
python app.py
```

The application will be available at `http://localhost:5002`

## Usage

### Quick Start

1. **Upload Database/File**: Select your database type (PostgreSQL, SQLite, Excel, etc.) and provide connection details or upload a file.

2. **Configure Image Path**: Specify where your pottery images are stored.

3. **AI Analysis**: Click "Analyze with AI" to automatically detect your schema structure.

4. **Start Classification**: Review the configuration and start the ML classification process.

### Supported Data Sources

| Source | Connection Method |
|--------|-------------------|
| PostgreSQL | Host, port, database, user, password |
| MySQL | Host, port, database, user, password |
| SQLite | File upload or path |
| MongoDB | Connection string |
| Excel (.xlsx) | File upload |
| CSV | File upload |

### Database Structure

For optimal results, your database should contain:

1. **Pottery Table**: Main table with pottery/artifact data
2. **Media Table**: References to images
3. **Relationship**: How pottery and images are linked (junction table, direct FK, or embedded)

See the [Database Structure Guide](docs/DATABASE_STRUCTURE_EN.md) for detailed information.

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main web interface |
| `/api/connect` | POST | Connect to database |
| `/api/analyze` | POST | AI schema analysis |
| `/api/preview` | POST | Preview query results |
| `/api/start-classification` | POST | Start ML classification |
| `/api/docs/<lang>` | GET | Get documentation (en/it) |

## Project Structure

```
ceramica-classifier/
├── app.py                 # Main Flask application
├── db_connector.py        # Universal database connector
├── ai_analyzer.py         # AI schema analyzer (Claude API)
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # Web interface
├── docs/
│   ├── QUICK_START.md           # Italian quick start
│   ├── QUICK_START_EN.md        # English quick start
│   ├── DATABASE_STRUCTURE.md    # Italian DB guide
│   └── DATABASE_STRUCTURE_EN.md # English DB guide
└── README.md
```

## ML API

This classifier uses a remote ML API for pottery comparison. The default endpoint is:

```
https://pottery-comparison-oman.up.railway.app/api/ml/similar
```

You can configure a custom ML API by setting the `ML_API_URL` environment variable.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Author

**Enzo Cocca**

## Related Projects

- [ceramic-khutm](https://github.com/enzococca/ceramic-khutm) - KhUTM-specific pottery classifier
