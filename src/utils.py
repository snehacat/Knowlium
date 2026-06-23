# -*- coding: utf-8 -*-
"""
Knowlium - Utilities Module
Helper functions for validation, verification, and document statistics
"""

import hashlib
import re
import streamlit as st

def get_question_hash(q: str) -> str:
    return hashlib.md5(q.lower().strip().encode()).hexdigest()

def validate_question(question: str) -> tuple:
    """Validates user question for prompt injection and quality"""
    if not question or len(question.strip()) < 3:
        return False, "❌ Question too short. Please ask a meaningful question."
    
    if len(question) > 1000:
        return False, "❌ Question too long. Please keep it under 1000 characters."
    
    # Prompt injection detection
    dangerous_patterns = [
        r'ignore\s+(previous|above|all)\s+instructions?',
        r'system\s+prompt',
        r'you\s+are\s+(now|a)\s+',
        r'role\s*:\s*system',
        r'<\|.*?\|>',
        r'disregard',
        r'forget\s+(everything|all|previous)',
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, question.lower()):
            return False, "🚨 Potential prompt injection detected. Please rephrase your question."
    
    return True, "Valid"

def highlight_scores_in_text(text: str) -> str:
    """Highlights confidence scores in answer text"""
    # Match patterns like [confidence: 0.85] or [score: 85%]
    pattern = r'\[(?:confidence|score):\s*(\d+\.?\d*)%?\]'
    
    def replace_score(match):
        score = float(match.group(1))
        if score > 1:  # If percentage
            score = score / 100
        
        if score >= 0.8:
            badge_class = "confidence-high"
            emoji = "✓"
        elif score >= 0.6:
            badge_class = "confidence-medium"
            emoji = "⚠"
        else:
            badge_class = "confidence-low"
            emoji = "⚠"
        
        return f'<span class="confidence-badge {badge_class}">{emoji} {int(score*100)}% confident</span>'
    
    return re.sub(pattern, replace_score, text)

def verify_answer(answer: str, docs: list, chunks: list) -> dict:
    """Verifies answer against source documents and returns confidence metrics"""
    if not answer or not docs:
        return {
            'is_verified': False,
            'confidence': 0.0,
            'sources': [],
            'evidence_count': 0
        }
    
    # Extract sentences from answer
    answer_sentences = re.split(r'[.!?]+', answer.lower())
    answer_sentences = [s.strip() for s in answer_sentences if len(s.strip()) > 10]
    
    verified_count = 0
    sources = []
    
    for doc in docs:
        doc_content = doc.page_content.lower()
        for sentence in answer_sentences:
            # Check for substantial overlap
            words = sentence.split()
            if len(words) < 3:
                continue
            
            # Check if most words appear in document
            matching_words = sum(1 for word in words if len(word) > 3 and word in doc_content)
            overlap_ratio = matching_words / len(words)
            
            if overlap_ratio > 0.6:
                verified_count += 1
                if hasattr(doc, 'metadata') and doc.metadata not in sources:
                    sources.append(doc.metadata)
                break
    
    confidence = verified_count / max(len(answer_sentences), 1)
    
    return {
        'is_verified': confidence > 0.5,
        'confidence': min(confidence, 1.0),
        'sources': sources[:3],  # Top 3 sources
        'evidence_count': verified_count
    }

def format_answer_with_confidence(answer: str, confidence: float, sources: list) -> str:
    """Formats answer with confidence badge and source citations"""
    # Add confidence badge
    if confidence >= 0.8:
        badge = '<span class="confidence-badge confidence-high">✓ High Confidence</span>'
    elif confidence >= 0.6:
        badge = '<span class="confidence-badge confidence-medium">⚠ Medium Confidence</span>'
    else:
        badge = '<span class="confidence-badge confidence-low">⚠ Low Confidence</span>'
    
    formatted = f"{answer}\n\n{badge}"
    
    # Add source citations if available
    if sources:
        formatted += "\n\n**📚 Sources:**"
        for i, source in enumerate(sources, 1):
            page = source.get('page', 'N/A') if isinstance(source, dict) else 'N/A'
            formatted += f'\n<div class="source-citation">Source {i}: Page {page}</div>'
    
    return formatted

def get_document_stats(chunks: list, pdf_pages: int, images: list) -> dict:
    """Calculate document statistics"""
    total_words = sum(len(chunk.split()) for chunk in chunks)
    total_chars = sum(len(chunk) for chunk in chunks)
    avg_chunk_size = total_chars // len(chunks) if chunks else 0
    
    return {
        'total_pages': pdf_pages,
        'total_chunks': len(chunks),
        'total_words': total_words,
        'total_images': len(images),
        'avg_chunk_size': avg_chunk_size,
        'estimated_read_time': max(1, total_words // 200)  # Assuming 200 WPM
    }

def classify_document_type(text_sample: str) -> dict:
    """Quick document type classification based on text patterns"""
    text_lower = text_sample.lower()
    
    # Resume indicators
    resume_keywords = ['experience', 'education', 'skills', 'resume', 'cv', 'curriculum vitae', 
                       'employment', 'projects', 'certifications']
    resume_score = sum(1 for kw in resume_keywords if kw in text_lower)
    
    # Research paper indicators
    research_keywords = ['abstract', 'methodology', 'literature review', 'references', 
                         'conclusion', 'introduction', 'results', 'discussion']
    research_score = sum(1 for kw in research_keywords if kw in text_lower)
    
    # Study material indicators
    study_keywords = ['chapter', 'exercise', 'questions', 'answers', 'lesson', 'topic', 
                      'quiz', 'exam', 'study guide']
    study_score = sum(1 for kw in study_keywords if kw in text_lower)
    
    # Report indicators
    report_keywords = ['executive summary', 'findings', 'recommendations', 'analysis', 
                       'quarterly', 'annual report', 'statistics']
    report_score = sum(1 for kw in report_keywords if kw in text_lower)
    
    scores = {
        'Resume': resume_score,
        'Research Paper': research_score,
        'Study Material': study_score,
        'Report': report_score,
        'General Document': 1
    }
    
    doc_type = max(scores, key=scores.get)
    confidence = scores[doc_type] / 10  # Normalize
    
    return {
        'type': doc_type,
        'confidence': min(confidence, 1.0),
        'all_scores': scores
    }