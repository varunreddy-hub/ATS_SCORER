import spacy
from sentence_transformers import SentenceTransformer

from MainApp.backend.services.resume_parser import parse_resume_file
from MainApp.backend.services.resume_analyzer import analyze_full_resume
import streamlit as st
# Load once

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    import subprocess
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"], check=True)
    nlp = spacy.load("en_core_web_sm")
    
embedder = SentenceTransformer("all-MiniLM-L6-v2")


def analyze_resume_locally(resume_file, job_description=""):
    st.error("LOCAL ANALYZER STARTED")

    file_bytes = resume_file.getvalue()
    filename = resume_file.name
    st.error("PARSING RESUME")
    resume_text, _ = parse_resume_file(
        file_bytes,
        filename
    )

    st.error("CALLING analyze_full_resume")

    result = analyze_full_resume(
        resume_text=resume_text,
        nlp=nlp,
        embedder=embedder,
        job_description=job_description,
    )

    return result