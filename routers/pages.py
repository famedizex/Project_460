# routers/pages.py
import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter(tags=["Web Pages"])

@router.get("/")
async def root():
    if os.path.exists("login.html"):
        return FileResponse("login.html")
    return {"message": "เซิร์ฟเวอร์รันปกติ กรุณาวางไฟล์ HTML ไว้ในโฟลเดอร์เดียวกัน"}

@router.get("/{filename}")
async def get_html(filename: str):
    allowed_files = [
        "login.html", 
        "register.html", 
        "studyai-planner.html",
        "firebase-config.js",
        "favicon.ico"
    ]
    if filename in allowed_files and os.path.exists(filename):
        return FileResponse(filename)
    raise HTTPException(status_code=404, detail="Page not found")
