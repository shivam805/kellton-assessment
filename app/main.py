
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from typing import Optional, List
import uuid, os

from .extract import extract_text
from .agent import analyze_text, modify_text
from .storage import save_temp, get_temp_path

app = FastAPI(title="Compliance API")

class ModifyRequest(BaseModel):
    doc_id: Optional[str] = None
    text: Optional[str] = None
    rules: Optional[List[str]] = None
    format: str = "docx"  # or "txt" / "pdf"

@app.get("/health")
def health():
    return {'status': 'ok'}

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    if file.content_type not in {"application/pdf", 
                                "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}:
        raise HTTPException(status_code=400, detail="Only PDF or DOCX accepted")

    doc_id = str(uuid.uuid4())
    disk_path = save_temp(doc_id, file)
    text = extract_text(disk_path, content_type=file.content_type)
    report = analyze_text(text)
    return JSONResponse({'doc_id': doc_id, 'report': report})

@app.post("/modify")
async def modify(req: ModifyRequest):
    if not req.doc_id and not req.text:
        raise HTTPException(status_code=400, detail="Provide doc_id or text")

    text = req.text
    if req.doc_id and not text:
        text = extract_text(get_temp_path(req.doc_id))

    updated_text, changes = modify_text(text, rules=req.rules or [])
    out_path = get_temp_path(f"{uuid.uuid4()}.{req.format}")

    if req.format == "docx":
        from docx import Document
        doc = Document()
        for para in updated_text.split('\n'):
            doc.add_paragraph(para)
        doc.save(out_path)
    else:
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(updated_text)

    return FileResponse(out_path, filename=os.path.basename(out_path))
