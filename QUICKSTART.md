## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose (for containerized deployment)
- OpenAI API Key

---

## 📦 Setup Local Environment

### 1. Clone & Install
```bash
cd "pixely partners"
python -m venv venv
.\venv\Scripts\activate        # Windows PowerShell
# source venv/bin/activate   # Linux/Mac

pip install -r requirements.txt
```

### 2. Configure Environment
```bash
# Copy template and add your API key
copy .env.example .env
# Edit .env and set OPENAI_API_KEY=sk-...
```

### 3. Run Locally

**Option A: Run Orchestrator Only (Generate Analysis JSON)**
```bash
python orchestrator/analyze.py
# Outputs saved to orchestrator/outputs/q1_emociones.json, q2_personalidad.json, etc.
```

**Option B: Run Frontend Only (View Results)**
```bash
streamlit run frontend/app.py
# Opens http://localhost:8501
# Shows 10 analysis modules in sidebar
```

**Option C: Run Both (Full Pipeline)**
```powershell
# Terminal 1: Run orchestrator
python orchestrator/analyze.py

# Terminal 2: Run frontend
streamlit run frontend/app.py
# Visit http://localhost:8501
```

---

## 🐳 Docker Deployment

### 1. Build & Start Services
```bash
docker-compose up --build
# Orchestrator runs once, then Frontend starts
# Frontend available at http://localhost:8501
```

### 2. View Logs
```bash
docker-compose logs -f orchestrator
docker-compose logs -f frontend
```

### 3. Cleanup
```bash
docker-compose down
docker-compose down -v          # Also remove volumes
```

---

## 🧪 Run Tests

```bash
pytest tests/ -v
# Validates all 10 modules import correctly
# Tests BaseAnalyzer, analyze.py, views
```

---

## 📊 Project Structure

```
pixely_partners/
├── orchestrator/
│   ├── base_analyzer.py           # Abstract base class
│   ├── analyze.py                 # Main orchestrator
│   ├── analysis_modules/          # Q1-Q10 analysis
│   │   ├── q1_emociones.py
│   │   ├── q2_personalidad.py
│   │   └── ... (q3-q10)
│   └── outputs/                   # Generated JSON results
│       └── ingested_data.json      # Example input data
├── frontend/
│   ├── app.py                     # Streamlit main
│   └── view_components/           # Display functions
│       ├── _outputs.py
│       └── qual/
│           ├── q1_view.py
│           └── ... (q2-q10)
├── tests/
│   └── test_imports.py            # Basic validation
├── docker-compose.yml
├── Dockerfile.orchestrator
├── Dockerfile.frontend
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md                      # Full documentation
```

---

## 📝 Data Flow

1. **Input:** `orchestrator/outputs/ingested_data.json` (posts + comments)
2. **Processing:** Each Qx module analyzes independently
3. **Output:** `orchestrator/outputs/qX_name.json` (results)
4. **Display:** Frontend loads JSONs and renders via Streamlit

---

## ⚠️ Troubleshooting

**Import errors when running locally?**
```bash
pip install -r requirements.txt --upgrade
```

**Streamlit not finding outputs?**
- Ensure orchestrator has run and created JSON files
- Check `PIXELY_OUTPUTS_DIR` in `.env`

**Docker container exits immediately?**
```bash
docker-compose logs orchestrator   # Check error message
```

---

## 🔧 Next Steps

1. ✅ Add real LLM prompts to each Qx module (replace stubs)
2. ✅ Connect to real social media data source
3. ✅ Add authentication to frontend
4. ✅ Deploy to cloud (AWS/GCP/Azure)

---

## 📚 Documentation

See `README.md` for comprehensive architecture, development guide, and API reference.
