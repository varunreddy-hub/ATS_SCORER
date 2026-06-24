import httpx
import json
import logging
import os
from datetime import datetime, timezone
from typing import List, Optional, Dict
import streamlit as st

logger = logging.getLogger('ats_resume_scorer')

def _get_supabase_config():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
    except:
        url = os.environ.get("SUPABASE_URL", "")
        key = os.environ.get("SUPABASE_KEY", "")
    return url, key

def _get_headers():
    url, key = _get_supabase_config()
    if not url or not key:
        return None, None
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    return url, headers

def google_oauth_url() -> dict:
    url, key = _get_supabase_config()
    if not url or not key:
        return {"error": "Supabase not configured"}
    try:
        redirect = os.environ.get("AUTH_REDIRECT_URL", "http://localhost:8501")
        auth_url = f"{url.rstrip('/')}/auth/v1/authorize?provider=google&redirect_to={redirect}"
        return {"url": auth_url}
    except Exception as exc:
        return {"error": str(exc)}

def sign_in_with_password(email: str, password: str) -> dict:
    url, key = _get_supabase_config()
    if not url or not key:
        return {"error": "Supabase not configured"}
    try:
        response = httpx.post(
            f"{url.rstrip('/')}/auth/v1/token?grant_type=password",
            headers={"apikey": key, "Content-Type": "application/json"},
            json={"email": email, "password": password}
        )
        data = response.json()
        if "error" in data or "error_description" in data:
            return {"error": data.get("error_description", data.get("error"))}
        return {
            "user": data.get("user"),
            "access_token": data.get("access_token"),
            "refresh_token": data.get("refresh_token")
        }
    except Exception as exc:
        return {"error": str(exc)}

def sign_up(email: str, password: str) -> dict:
    url, key = _get_supabase_config()
    if not url or not key:
        return {"error": "Supabase not configured"}
    try:
        response = httpx.post(
            f"{url.rstrip('/')}/auth/v1/signup",
            headers={"apikey": key, "Content-Type": "application/json"},
            json={"email": email, "password": password}
        )
        data = response.json()
        if "error" in data:
            return {"error": data.get("error_description", data.get("error"))}
        return {"user": data.get("user")}
    except Exception as exc:
        return {"error": str(exc)}

def sign_up_with_password(email: str, password: str) -> dict:
    return sign_up(email, password)

def sign_out(access_token: str) -> dict:
    url, key = _get_supabase_config()
    if not url or not key:
        return {"error": "Supabase not configured"}
    try:
        httpx.post(
            f"{url.rstrip('/')}/auth/v1/logout",
            headers={"apikey": key, "Authorization": f"Bearer {access_token}"}
        )
        return {"success": True}
    except Exception as exc:
        return {"error": str(exc)}

def get_user(access_token: str) -> dict:
    url, key = _get_supabase_config()
    if not url or not key:
        return {"error": "Supabase not configured"}
    try:
        response = httpx.get(
            f"{url.rstrip('/')}/auth/v1/user",
            headers={"apikey": key, "Authorization": f"Bearer {access_token}"}
        )
        data = response.json()
        if "error" in data:
            return {"error": data.get("error_description", data.get("error"))}
        return {"user": data}
    except Exception as exc:
        return {"error": str(exc)}

def exchange_code_for_session(code: str) -> dict:
    url, key = _get_supabase_config()
    if not url or not key:
        return {"error": "Supabase not configured"}
    try:
        response = httpx.post(
            f"{url.rstrip('/')}/auth/v1/token?grant_type=pkce",
            headers={"apikey": key, "Content-Type": "application/json"},
            json={"auth_code": code}
        )
        data = response.json()
        if "error" in data:
            return {"error": data.get("error_description", data.get("error"))}
        return {
            "user": data.get("user"),
            "access_token": data.get("access_token"),
            "refresh_token": data.get("refresh_token")
        }
    except Exception as exc:
        return {"error": str(exc)}

def save_analysis(user_id: str, filename: str, analysis_result: Dict) -> Optional[str]:
    url, headers = _get_headers()
    if not headers:
        return None

    def _json_default(o):
        if hasattr(o, 'model_dump'):
            return o.model_dump()
        return str(o)

    serializable_result = json.loads(json.dumps(analysis_result, default=_json_default))
    doc = {
        "user_id": user_id,
        "filename": filename,
        "ats_score": serializable_result.get("ATS_score") or serializable_result.get("ats_score") or 0,
        "keyword_match": serializable_result.get("keyword_match", 0),
        "missing_keywords": serializable_result.get("missing_keywords", []),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "analysis_result": serializable_result,
    }
    try:
        response = httpx.post(
            f"{url.rstrip('/')}/rest/v1/analyses",
            headers=headers,
            json=doc
        )
        response.raise_for_status()
        data = response.json()
        if data and len(data) > 0:
            return str(data[0].get("id"))
        return None
    except Exception as exc:
        logger.error(f"Failed to save analysis: {exc}")
        return None

def get_user_history(user_id: str) -> List[Dict]:
    url, headers = _get_headers()
    if not headers:
        return []
    try:
        response = httpx.get(
            f"{url.rstrip('/')}/rest/v1/analyses",
            headers=headers,
            params={"user_id": f"eq.{user_id}", "order": "created_at.desc"}
        )
        response.raise_for_status()
        docs = response.json()
        results = []
        for doc in docs:
            results.append({
                "id": str(doc.get("id")),
                "filename": doc.get("filename", "resume"),
                "resume_name": doc.get("filename", "resume"),
                "ats_score": doc.get("ats_score", 0),
                "keyword_match": doc.get("keyword_match", 0),
                "missing_keywords": doc.get("missing_keywords", []),
                "date": doc.get("created_at", ""),
                "created_at": doc.get("created_at", ""),
                "analysis_result": doc.get("analysis_result", {}),
            })
        return results
    except Exception as exc:
        logger.error(f"Failed to fetch history: {exc}")
        return []

def delete_analysis(analysis_id: str, user_id: str) -> bool:
    url, headers = _get_headers()
    if not headers:
        return False
    try:
        response = httpx.delete(
            f"{url.rstrip('/')}/rest/v1/analyses",
            headers=headers,
            params={"id": f"eq.{analysis_id}", "user_id": f"eq.{user_id}"}
        )
        response.raise_for_status()
        return True
    except Exception as exc:
        logger.error(f"Failed to delete analysis: {exc}")
        return False