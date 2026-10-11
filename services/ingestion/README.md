# Ingestion / RAG

Turns NCERT PDFs into searchable, metadata-tagged chunks. See `docs/rag-step-by-step.md` for the full guide.

```bash
cd services/ingestion
pip install -r requirements.txt
python -m pytest tests/ -v                 # runs offline, no model download
python -m rag.cli ingest | query "..." | compare      # add --set key.path=value to override config
```
