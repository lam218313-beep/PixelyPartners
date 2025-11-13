# Pixely Partners - Qualitative Analysis Platform

Pixely Partners is a **native single-client, modular platform** for qualitative social media analysis. It provides deep insights into audience sentiment, emotions, personality traits, and content performance through a collection of AI-powered analysis modules (Q1-Q10).

## Overview

**Architecture:**
- **Orchestrator**: Executes 10 qualitative analysis modules asynchronously
- **Frontend**: Streamlit-based dashboard for visualizing results
- **Outputs**: JSON files containing analysis results per module
- **Dockerized**: Full docker-compose setup for easy deployment

**Modules (Q1-Q10):**
- Q1: Emotional Analysis (Plutchik model)
- Q2: Personality Analysis (Aaker framework)
- Q3: Topic Modeling
- Q4: Narrative Framing (Entman)
- Q5: Influencers & Key Voices
- Q6: Opportunities Detection
- Q7: Detailed Sentiment Analysis
- Q8: Temporal Trends
- Q9: Recommendations
- Q10: Executive Summary

## Project Structure

```
Pixely Partners/
├── orchestrator/
│   ├── analysis_modules/
│   │   ├── q1_emociones.py
│   │   ├── q2_personalidad.py
│   │   ├── ... (q3-q10)
│   │   └── __init__.py
│   ├── base_analyzer.py
│   ├── analyze.py
│   ├── outputs/
│   │   └── ingested_data.json
│   └── __init__.py
├── frontend/
│   ├── view_components/
│   │   ├── qual/
│   │   │   ├── q1_view.py
│   │   │   ├── q2_view.py
│   │   │   ├── ... (q3-q10)
│   │   │   └── __init__.py
│   │   ├── _outputs.py
│   │   └── __init__.py
│   ├── app.py
│   └── __init__.py
├── tests/
│   ├── test_imports.py
│   └── __init__.py
├── docker-compose.yml
├── Dockerfile.orchestrator
├── Dockerfile.frontend
├── requirements.txt
├── .env.example
└── README.md
```

## Quick Start

### Local Development (No Docker)

#### 1. Setup Environment
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your OpenAI API key
# OPENAI_API_KEY=sk-...
```

#### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 3. Prepare Data
Ensure `orchestrator/outputs/ingested_data.json` exists with your social media data.

#### 4. Run Orchestrator
```bash
cd orchestrator
python analyze.py
# Runs all 10 modules and outputs JSON files to outputs/
```

#### 5. Run Frontend
In a new terminal:
```bash
streamlit run frontend/app.py
# Opens dashboard at http://localhost:8501
```

### Docker Deployment

#### 1. Build and Run
```bash
docker-compose up --build
```

Services will start:
- **Orchestrator**: Runs analysis on startup
- **Frontend**: Available at `http://localhost:8501`

#### 2. View Logs
```bash
docker-compose logs -f frontend
docker-compose logs -f orchestrator
```

#### 3. Stop Services
```bash
docker-compose down
```

## API & Data Flow

### Input: `orchestrator/outputs/ingested_data.json`

```json
{
  "client_ficha": {
    "client_id": 1,
    "client_name": "PixelyBrand",
    "primary_business_goal": "Aumentar Engagement",
    ...
  },
  "posts": [
    {
      "post_url": "https://instagram.com/p/...",
      "ownerUsername": "pixelybrand",
      "caption": "...",
      "likesCount": 1000,
      "commentsCount": 50,
      ...
    }
  ],
  "comments": [
    {
      "post_url": "https://instagram.com/p/...",
      "comment_text": "Great post!",
      "ownerUsername": "user123"
    }
  ]
}
```

### Output: `orchestrator/outputs/q{N}_{module_name}.json`

Each module produces:
```json
{
  "metadata": {
    "module": "Q1 Emociones",
    "version": 1,
    "description": "..."
  },
  "results": {
    "analisis_por_publicacion": [...],
    "resumen_global_emociones": {...}
  },
  "errors": []
}
```

## Development

### Adding a New Analysis Module

1. Create `orchestrator/analysis_modules/qX_nombre.py`:
```python
from ..base_analyzer import BaseAnalyzer

class QXNombre(BaseAnalyzer):
    async def analyze(self) -> Dict[str, Any]:
        # Load data
        ingested_data = self.load_ingested_data()
        
        # Analyze
        results = {...}
        
        return {
            "metadata": {"module": "QX Nombre", "version": 1},
            "results": results,
            "errors": []
        }
```

2. Register in `orchestrator/analyze.py`:
```python
from analysis_modules.qX_nombre import QXNombre

ANALYSIS_MODULES = {
    ...
    "QX": QXNombre,
}
```

3. Create frontend view `frontend/view_components/qual/qX_view.py`:
```python
def display_qX_nombre():
    st.header("QX: Nombre")
    outputs_dir = get_outputs_dir()
    json_path = os.path.join(outputs_dir, "qx_nombre.json")
    # Load and display results
```

### Running Tests

```bash
pytest tests/
```

## Architecture Notes

- **Single-Client Native**: No multi-client modes or competitor data. The system operates exclusively on client data.
- **Modular Isolation**: Each Q module runs independently, preventing cascade failures.
- **Async Processing**: Uses `asyncio` for concurrent LLM calls and analysis.
- **Error Resilience**: Exceptions are captured and returned in results, not raised.

## Configuration

### Environment Variables (`.env`)

```
OPENAI_API_KEY=your_key_here
ORCHESTRATOR_USER=orchestrator
ORCHESTRATOR_PASSWORD=secure_password
PIXELY_OUTPUTS_DIR=/app/orchestrator/outputs
```

### Docker Volumes

- `./orchestrator/outputs:/app/orchestrator/outputs` - Shared outputs directory
- `./orchestrator:/app/orchestrator` - Orchestrator source
- `./frontend:/app/frontend` - Frontend source

## Troubleshooting

### Module Import Errors
Ensure `analysis_modules/__init__.py` exists and `analyze.py` imports match file names.

### Missing JSON Files
Check that `orchestrator/outputs/ingested_data.json` exists and is valid JSON.

### Streamlit Port Issues
If port 8501 is in use:
```bash
streamlit run frontend/app.py --server.port 8502
```

### Docker Network Issues
```bash
docker-compose down -v  # Remove volumes
docker-compose up --build  # Rebuild from scratch
```

## Future Enhancements

- [ ] Add quantitative modules (Q11-Q20)
- [ ] Integrate PostgreSQL for persistence
- [ ] Add FastAPI layer for REST endpoints
- [ ] Implement JWT authentication
- [ ] Add real OpenAI LLM calls (currently stubs)
- [ ] Cron scheduling for automated analysis
- [ ] Advanced visualization with Plotly/Altair

## License

Pixely Partners © 2025

## Support

For issues, questions, or contributions, please refer to project documentation.
