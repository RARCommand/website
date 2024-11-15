# app/api/upload.py
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = "static/uploads"
router = APIRouter()

@router.post("/upload-image/")
async def upload_image(file: UploadFile = File(...)):
    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    return JSONResponse(content={"filename": filename, "url": f"/{UPLOAD_FOLDER}/{filename}"})
