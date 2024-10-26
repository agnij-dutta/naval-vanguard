from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
import sqlite3
import uvicorn
from ocr import OCRProcessor
import json
from scripts.rag_pipeline import *
from scripts.generate_dataset import *
from database.db import *
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import shutil

ocr = OCRProcessor()
upload_folder = r'uploads'

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

'''
THIS CODE IS SHIT, DONT FOLLOW THIS CODE JUST COOK UP SOMETHING USING FASTAPI. IF NOT POSSIBLE THEN PIVOT TO FLASK. BUT NOT DJANGO.
DJANGO TOO HARD
'''

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Use ["http://localhost:8000"] to restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)
conn = sqlite3.connect('./database/localdb/contacts.db')
create_database()

#if text run process_message_rag_pipeline(message, )
#if file run ocr.process_image(image_path)

with open(r'./database/data/parsed_maritime_data.json', 'r') as infile:
    parsed_data = json.load(infile)

class TextInput(BaseModel):
    text: str

@app.post("/api/post/textdata")
async def submit_text(data: TextInput):
    # Handle the text received here
    print(data.text)
    report = {
            "location": process_message_rag_pipeline(data.text, "The location of the contact (not coordinates)"),
            "vessel_name": extract_vessel_name(data.text),
            "message": data.text,
            "priority": process_message_rag_pipeline(data.text, "status/priority of the message into the following categories: urgent/immediate/top secret/secret/confidential/routine/secret"),
            "coordinates": extract_coordinates(data.text),
            "additional_info": process_message_rag_pipeline(data.text, "relevant information summary") + extract_additional_info(data.text)
        }
    insert_into_contacts(conn, report)
    return {"received_text": report["message"]+report["additional_info"]}

@app.post("/api/post/file")
async def upload_file(file: UploadFile = File(...)):
    try:
        filename = file.filename
        file_path = os.path.join(upload_folder, filename)

        # Save the uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Process the uploaded file with OCR
        text = ocr.process_image(file_path)
        
        report = {
            "location": process_message_rag_pipeline(text, "The location of the contact (not coordinates)"),
            "vessel_name": extract_vessel_name(text),
            "message": text,
            "priority": process_message_rag_pipeline(text, "status/priority of the message into the following categories: urgent/immediate/top secret/secret/confidential/routine/secret"),
            "coordinates": extract_coordinates(text),
            "additional_info": process_message_rag_pipeline(text, "relevant information summary") + extract_additional_info(text)
        }
        insert_into_contacts(conn, report)
        return {"received_text": report["message"] + report["additional_info"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def redirect_to_ops():
    return RedirectResponse(url="/ops")

@app.get("/ops", response_class=HTMLResponse)
async def read_ops():
    with open("static/dashboard.html") as f:
        return HTMLResponse(content=f.read())
    

@app.get("/team", response_class=HTMLResponse)
async def read_ops():
    with open("static/team.html") as f:
        return HTMLResponse(content=f.read())


@app.get("/api/contacts", response_class=JSONResponse)
async def read_records():
    conn = sqlite3.connect('./database/localdb/contacts.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM contacts_basic")
    records = cursor.fetchall()
    conn.close()
    
    # Convert tuples to lists
    records_as_lists = [list(record) for record in records]
    return records_as_lists

@app.get("/", response_class=HTMLResponse)
async def read_ops_norm():
    return RedirectResponse(url="/ops")

@app.get("/api/zones", response_class=JSONResponse)
async def read_records():
    conn = sqlite3.connect('./database/localdb/contacts.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM zones_basic")
    records = cursor.fetchall()
    conn.close()
    
    # Convert tuples to lists
    records_as_lists = [list(record) for record in records]
    return records_as_lists


if __name__ == "_main_":
    uvicorn.run(app, host="0.0.0.0", port=8000, debug=True)