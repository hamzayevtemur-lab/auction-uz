import os
import uuid
from pathlib import Path
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from ..dependencies import get_current_user
from ..models.user import User

router = APIRouter(prefix="/upload", tags=["Upload"])

# Save uploads to backend/uploads/ — served as static files at /uploads
UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXT = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
MAX_SIZE = 5 * 1024 * 1024  # 5MB


@router.post("/image")
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXT:
        raise HTTPException(400, "Faqat JPG, PNG, WEBP yoki GIF rasm yuklash mumkin")

    contents = await file.read()
    if len(contents) > MAX_SIZE:
        raise HTTPException(400, "Rasm hajmi 5MB dan oshmasligi kerak")

    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = UPLOAD_DIR / filename
    with open(filepath, "wb") as f:
        f.write(contents)

    return {"url": f"/uploads/{filename}", "filename": filename}


@router.post("/images")
async def upload_images(
    files: list[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
):
    if len(files) > 6:
        raise HTTPException(400, "Maksimal 6 ta rasm yuklash mumkin")

    urls = []
    for file in files:
        ext = Path(file.filename).suffix.lower()
        if ext not in ALLOWED_EXT:
            raise HTTPException(400, f"'{file.filename}' — ruxsat etilmagan format")
        contents = await file.read()
        if len(contents) > MAX_SIZE:
            raise HTTPException(400, f"'{file.filename}' — 5MB dan katta")
        filename = f"{uuid.uuid4().hex}{ext}"
        with open(UPLOAD_DIR / filename, "wb") as f:
            f.write(contents)
        urls.append(f"/uploads/{filename}")

    return {"urls": urls}