# Heroku Procfile
# Este archivo le dice a Heroku cómo ejecutar tu aplicación

web: streamlit run frontend/app.py --server.port=$PORT --server.address=0.0.0.0 --logger.level=debug
worker: python orchestrator/analyze.py
