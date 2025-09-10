
# AI Compliance API

A FastAPI service to analyze and auto-correct PDF/DOCX documents for English compliance (grammar, style, readability).

## Run locally

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
uvicorn app.main:app --reload
```

## Endpoints

- `GET /health` → Health check  
- `POST /analyze` → Upload PDF/DOCX and get compliance report  
- `POST /modify` → Get corrected version of text/file

## Example

```bash
curl -F "file=@samples/sample.pdf" http://localhost:8000/analyze
curl -X POST http://localhost:8000/modify -H "Content-Type: application/json"             -d '{"doc_id":"<from_analyze>", "format":"docx"}' --output corrected.docx
```
