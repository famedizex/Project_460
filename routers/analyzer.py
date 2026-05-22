# routers/analyzer.py
import io
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from core.ai_service import analyze_content_with_groq, analyze_image_with_groq

def extract_text(file_bytes: bytes, content_type: str) -> str:
    if content_type == "application/pdf":
        try:
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(file_bytes))
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        except Exception:
            return ""
    return file_bytes.decode("utf-8", errors="ignore")

router = APIRouter(
    prefix="/api",
    tags=["AI Analyzer"]
)

IMAGE_TYPES = {"image/png", "image/jpeg", "image/jpg", "image/webp"}
TEXT_TYPES = {
    "text/plain",
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword",
}

@router.post("/analyze-file")
async def analyze_file(file: UploadFile = File(...), extra_info: str = Form("")):
    file_bytes = await file.read()
    content_type = file.content_type or ""

    if content_type in IMAGE_TYPES:
        return analyze_image_with_groq(file_bytes, content_type)

    if content_type in TEXT_TYPES:
        text_content = extract_text(file_bytes, content_type)
        if not text_content.strip():
            raise HTTPException(status_code=400, detail="ไม่สามารถอ่านเนื้อหาจากไฟล์ได้ กรุณาลองคัดลอกข้อความมาวางในช่อง text แทน")
        contents = [text_content]
        if extra_info:
            contents.append(extra_info)
        return analyze_content_with_groq(contents)

    raise HTTPException(
        status_code=400,
        detail=f"ไม่รองรับไฟล์ประเภทนี้ รองรับ: PNG, JPG, PDF, TXT, DOCX"
    )

@router.post("/analyze-text")
async def analyze_text(text: str = Form(...), extra_info: str = Form("")):
    final_text = text
    if extra_info:
        final_text += f"\n\n{extra_info}"
    return analyze_content_with_groq([final_text])
