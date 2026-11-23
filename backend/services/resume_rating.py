"""Transparent structural rubric, not a hiring probability or vendor ATS score."""
import re

def rate_resume(text, skills):
    checks = [
        ("Readable text (200+ words)",len(text.split()) >= 200,20),
        ("Contact email",bool(re.search(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}',text)),15),
        ("Experience or projects section",bool(re.search(r'\b(experience|projects)\b',text,re.I)),20),
        ("Education section",bool(re.search(r'\beducation\b',text,re.I)),15),
        ("At least five identified skills",len(set(skills))>=5,15),
        ("Quantified results",bool(re.search(r'\d+\s*(%|percent|users|customers|hours)',text,re.I)),15),
    ]
    return {"score":sum(points for _,passed,points in checks if passed),"method":"Structural checklist; not an ATS prediction", "checks":[{"label":label,"passed":passed,"points":points} for label,passed,points in checks]}
