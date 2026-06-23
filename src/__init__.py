# -*- coding: utf-8 -*-
"""
Knowlium - AI-Powered Document Intelligence Platform
Main package initialization
"""

__version__ = "1.0.0"
__author__ = "Knowlium Team"
__description__ = "AI-Powered Document Intelligence Platform"

# Package-level imports for convenience
from .config import init_page_config, init_session_state, inject_custom_css
from .pdf_processor import extract_images_from_pdf, extract_text_and_chunk
from .rag_engine import (
    load_embeddings,
    build_vectorstore,
    get_groq_llm,
    query_llm,
    analyze_document_type,
    generate_summary,
    extract_key_insights,
    get_specialized_prompt,
    calculate_ats_score,
    generate_interview_questions
)
from .utils import (
    get_question_hash,
    validate_question,
    highlight_scores_in_text,
    verify_answer,
    format_answer_with_confidence,
    get_document_stats,
    classify_document_type
)

__all__ = [
    # Config
    "init_page_config",
    "init_session_state",
    "inject_custom_css",
    # PDF Processor
    "extract_images_from_pdf",
    "extract_text_and_chunk",
    # RAG Engine
    "load_embeddings",
    "build_vectorstore",
    "get_groq_llm",
    "query_llm",
    "analyze_document_type",
    "generate_summary",
    "extract_key_insights",
    "get_specialized_prompt",
    "calculate_ats_score",
    "generate_interview_questions",
    # Utils
    "get_question_hash",
    "validate_question",
    "highlight_scores_in_text",
    "verify_answer",
    "format_answer_with_confidence",
    "get_document_stats",
    "classify_document_type",
]
