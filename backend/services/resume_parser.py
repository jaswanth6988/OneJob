import os
import re
from typing import Dict, List, Any
import fitz  # PyMuPDF
import docx
import json
import httpx
from backend.schemas.resume import ResumeParsedData
from backend.core.config import settings

def parse_pdf(file_path: str) -> str:
    text = ""
    try:
        doc = fitz.open(file_path)
        for page in doc:
            text += page.get_text()
        doc.close()
    except Exception as e:
        print(f"Error parsing PDF: {e}")
    return text

def parse_docx(file_path: str) -> str:
    text = ""
    try:
        doc = docx.Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        print(f"Error parsing DOCX: {e}")
    return text

def extract_skills(text: str) -> List[str]:
    # Basic keyword extraction - in a real app, this would use NLP or an AI API
    common_skills = [
        "python", "java", "javascript", "c++", "c#", "ruby", "go", "rust",
        "react", "angular", "vue", "node.js", "express", "django", "fastapi", "flask",
        "sql", "mysql", "postgresql", "mongodb", "redis", "elasticsearch",
        "aws", "azure", "gcp", "docker", "kubernetes", "ci/cd", "git",
        "machine learning", "data science", "ai", "nlp", "computer vision"
    ]
    
    text_lower = text.lower()
    found_skills = set()
    
    for skill in common_skills:
        # Simple word boundary regex
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            found_skills.add(skill)
            
    return list(found_skills)

async def extract_sections(text: str) -> Dict[str, Any]:
    if not settings.GEMINI_API_KEY:
        # Fallback if no API key
        return {
            "experience": [],
            "education": [],
            "skills": [],
            "certifications": []
        }
        
    prompt = f"""
    Extract the following from the resume text into a strictly valid JSON object.
    Do not include markdown blocks, just the raw JSON string.
    
    Format:
    {{
      "experience": [{{"company": "", "title": "", "duration": "", "bullets": [""]}}],
      "education": [{{"school": "", "degree": "", "field": "", "year": ""}}],
      "skills": [""],
      "certifications": [""]
    }}
    
    Resume Text:
    {text[:8000]}
    """
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.GEMINI_MODEL or 'gemini-2.0-flash'}:generateContent?key={settings.GEMINI_API_KEY}"
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
            if resp.status_code == 200:
                reply = resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
                if reply.startswith("```json"):
                    reply = reply[7:-3]
                elif reply.startswith("```"):
                    reply = reply[3:-3]
                return json.loads(reply)
    except Exception as e:
        print(f"Failed to extract sections with AI: {e}")
        
    return {
        "experience": [],
        "education": [],
        "skills": [],
        "certifications": []
    }

async def parse_resume(file_path: str, file_type: str) -> ResumeParsedData:
    """Dispatcher for parsing different resume file types."""
    import asyncio
    
    # Run CPU bound PDF/DOCX parsing in a separate thread
    loop = asyncio.get_event_loop()
    if file_type == "pdf":
        raw_text = await loop.run_in_executor(None, parse_pdf, file_path)
    elif file_type == "docx":
        raw_text = await loop.run_in_executor(None, parse_docx, file_path)
    else:
        raw_text = ""
        
    skills = extract_skills(raw_text)
    sections = await extract_sections(raw_text)
    
    # Merge skills
    all_skills = list(set(skills + sections.get("skills", [])))
    
    return ResumeParsedData(
        skills=all_skills,
        experience=sections.get("experience", []),
        education=sections.get("education", []),
        certifications=sections.get("certifications", []),
        raw_text=raw_text
    )
