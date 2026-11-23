"""Literal, composable Mongo filters; never interpret user text as regex."""
import re
from datetime import datetime, timedelta, timezone


def build_job_filters(search=None, location=None, company=None, remote_type=None,
                      source=None, seniority=None, industry=None, skills=None,
                      min_score=None, status=None, posted_days=None,
                      salary_only=False, include_expired=False, **_):
    clauses = []
    def literal(value):
        return {"$regex": re.escape(value.strip()), "$options": "i"}
    if search and search.strip():
        for term in search.split():
            clauses.append({"$or": [{field: literal(term)} for field in ("title", "company", "skills_required", "tags")]})
    for key, value in [("location", location), ("company", company), ("seniority_level", seniority), ("industry", industry)]:
        if value and value.strip(): clauses.append({key: literal(value)})
    for key, value in [("remote_type", remote_type), ("source_name", source), ("status", status)]:
        if value: clauses.append({key: {"$in": value.split(",")}})
    for skill in (skills or "").split(","):
        if skill.strip(): clauses.append({"skills_required": literal(skill)})
    if min_score is not None: clauses.append({"score": {"$gte": min_score}})
    now = datetime.now(timezone.utc)
    if posted_days: clauses.append({"discovered_at": {"$gte": now - timedelta(days=posted_days)}})
    if salary_only: clauses.append({"salary_range": {"$nin": [None, "", "Not disclosed", "Not specified"]}})
    if not include_expired: clauses.append({"$or": [{"expires_at": None}, {"expires_at": {"$gt": now}}]})
    return {"$and": clauses} if clauses else {}
