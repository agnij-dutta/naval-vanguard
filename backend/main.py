from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from ocr import *
from backend.rag.rag import process_rag
from db import store_report, get_contacts
import uvicorn

app = FastAPI()

# Route to handle OCR
@app.post("/process_report/")
async def process_report(file: UploadFile = File(...)):
    ocr_text = process_ocr(file.file)
    structured_data = process_rag(ocr_text)
    store_report(structured_data)
    return JSONResponse(content=structured_data)

# Route to get contacts for visualization
@app.get("/contacts/")
def contacts():
    return JSONResponse(content=get_contacts())

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
