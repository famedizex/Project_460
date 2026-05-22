# core/ai_service.py
import json
import base64
from groq import Groq
from fastapi import HTTPException
from config import API_KEY

client = Groq(api_key=API_KEY)

PROMPT_INSTRUCTION = """
คุณคือ AI ผู้ช่วยวางแผนการเรียน หน้าที่ของคุณคือสกัดข้อมูลงาน (Assignment), โปรเจค (Project), และการสอบ (Exam) จากข้อมูล Course Syllabus ที่แนบมา

จงสกัดข้อมูลแล้วคืนค่ากลับมาเป็นรูปแบบ JSON เท่านั้น ห้ามมีข้อความอื่นนอกจาก JSON โดยมีโครงสร้างดังนี้:
{
  "tasks": [
    {
      "name": "ชื่องาน",
      "type": "exam|project|assignment|quiz|reading",
      "deadline": "YYYY-MM-DD หรือ null ถ้าไม่มีกำหนด",
      "estimatedHours": 2.0,
      "priority": "critical|high|medium|low",
      "quadrant": "q1|q2|q3|q4",
      "description": "คำอธิบายสั้นๆ"
    }
  ]
}

กฎ:
1. type: exam, project, assignment, quiz, reading
2. deadline: รูปแบบ YYYY-MM-DD ถ้าไม่มีปีให้ใช้ 2026 ถ้าไม่มีวันกำหนดให้เป็น null
3. estimatedHours: ประเมินเวลาที่ต้องใช้ (ชั่วโมง)
4. quadrant: q1=สำคัญ+เร่งด่วน, q2=สำคัญ+ไม่เร่งด่วน, q3=ไม่สำคัญ+เร่งด่วน, q4=ไม่สำคัญ+ไม่เร่งด่วน
5. priority: q1=critical, q2=high, q3=medium, q4=low
"""

def analyze_content_with_groq(contents: list):
    text_parts = [p for p in contents if isinstance(p, str)]
    full_text = "\n\n".join(text_parts)

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": PROMPT_INSTRUCTION},
                {"role": "user", "content": full_text}
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
            max_tokens=4096,
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Error: {str(e)}")


def analyze_image_with_groq(image_bytes: bytes, mime_type: str):
    b64 = base64.standard_b64encode(image_bytes).decode("utf-8")
    try:
        # Step 1: ให้ vision model อ่านข้อความจากรูป
        vision_response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:{mime_type};base64,{b64}"}
                        },
                        {
                            "type": "text",
                            "text": "กรุณาอ่านและถอดข้อความทั้งหมดจากรูปภาพนี้ให้ครบถ้วน โดยเฉพาะชื่องาน วันส่ง และรายละเอียดต่างๆ"
                        }
                    ]
                }
            ],
            max_tokens=2048,
            temperature=0.1,
        )
        extracted_text = vision_response.choices[0].message.content

        # Step 2: ส่งข้อความที่อ่านได้ให้ text model สร้าง JSON
        return analyze_content_with_groq([extracted_text])

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Error: {str(e)}")
