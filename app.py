# -*- coding: utf-8 -*-
"""
Knowlium - AI-Powered Document Intelligence Platform
Main application file
"""

import streamlit as st
import time
from dotenv import load_dotenv
from datetime import datetime

# Internal Module Imports
from src.config import init_page_config, init_session_state, inject_custom_css
from src.pdf_processor import extract_images_from_pdf, extract_text_and_chunk
from src.rag_engine import (
    load_embeddings, build_vectorstore, get_groq_llm, query_llm,
    analyze_document_type, generate_summary, extract_key_insights, get_specialized_prompt
)
from src.utils import (
    get_question_hash, validate_question, highlight_scores_in_text, 
    verify_answer, format_answer_with_confidence, get_document_stats,
    classify_document_type
)

load_dotenv()

# App setups
init_page_config()
inject_custom_css()
init_session_state()

# --- HEADER WITH BRANDING ---
st.markdown("""
<div style="
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
    border-radius: 20px;
    padding: 2.5rem 2rem;
    margin-bottom: 2rem;
    border: 1px solid rgba(99, 102, 241, 0.3);
    backdrop-filter: blur(10px);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1.5rem;">
        <div style="flex: 1; min-width: 300px;">
            <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
                <div style="
                    font-size: 4.5rem;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    line-height: 1;
                ">⚡</div>
                <div>
                    <h1 style="
                        font-size: 4rem !important;
                        font-weight: 900 !important;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
                        -webkit-background-clip: text;
                        -webkit-text-fill-color: transparent;
                        margin: 0 !important;
                        letter-spacing: -0.03em;
                        line-height: 1;
                    ">
                        Knowlium
                    </h1>
                    <p style="
                        color: #A5B4FC !important;
                        font-size: 1rem !important;
                        font-weight: 600 !important;
                        margin: 0.5rem 0 0 0 !important;
                        letter-spacing: 0.08em;
                        text-transform: uppercase;
                    ">
                        Unlock Intelligence · Every Document
                    </p>
                </div>
            </div>
            <div style="display: flex; gap: 0.75rem; flex-wrap: wrap; margin-top: 1.5rem;">
                <span style="
                    background: linear-gradient(135deg, rgba(99, 102, 241, 0.2) 0%, rgba(99, 102, 241, 0.1) 100%);
                    border: 1px solid rgba(99, 102, 241, 0.5);
                    padding: 0.5rem 1rem;
                    border-radius: 25px;
                    font-size: 0.8rem;
                    color: #C7D2FE;
                    font-weight: 600;
                    display: inline-flex;
                    align-items: center;
                    gap: 0.5rem;
                ">
                    <span style="font-size: 1rem;">🤖</span> AI-Powered
                </span>
                <span style="
                    background: linear-gradient(135deg, rgba(139, 92, 246, 0.2) 0%, rgba(139, 92, 246, 0.1) 100%);
                    border: 1px solid rgba(139, 92, 246, 0.5);
                    padding: 0.5rem 1rem;
                    border-radius: 25px;
                    font-size: 0.8rem;
                    color: #DDD6FE;
                    font-weight: 600;
                    display: inline-flex;
                    align-items: center;
                    gap: 0.5rem;
                ">
                    <span style="font-size: 1rem;">💬</span> Smart Q&A
                </span>
                <span style="
                    background: linear-gradient(135deg, rgba(16, 185, 129, 0.2) 0%, rgba(16, 185, 129, 0.1) 100%);
                    border: 1px solid rgba(16, 185, 129, 0.5);
                    padding: 0.5rem 1rem;
                    border-radius: 25px;
                    font-size: 0.8rem;
                    color: #A7F3D0;
                    font-weight: 600;
                    display: inline-flex;
                    align-items: center;
                    gap: 0.5rem;
                ">
                    <span style="font-size: 1rem;">⚡</span> Instant Insights
                </span>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Show active session badge if document is loaded
if st.session_state.processing_complete:
    pdf_name_trimmed = st.session_state.pdf_name[:30] + ('...' if len(st.session_state.pdf_name) > 30 else '')
    st.markdown(f"""
    <div style="
        text-align: center;
        margin: -1rem 0 2rem 0;
    ">
        <div style="
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.2) 0%, rgba(16, 185, 129, 0.1) 100%);
            border: 2px solid rgba(16, 185, 129, 0.5);
            border-radius: 16px;
            padding: 1rem 1.5rem;
            display: inline-block;
            box-shadow: 0 4px 16px rgba(16, 185, 129, 0.2);
        ">
            <div style="
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 0.75rem;
            ">
                <span style="
                    width: 10px;
                    height: 10px;
                    background: #10b981;
                    border-radius: 50%;
                    box-shadow: 0 0 10px #10b981;
                    display: inline-block;
                "></span>
                <span style="
                    color: #10b981;
                    font-size: 0.9rem;
                    font-weight: 700;
                    letter-spacing: 0.05em;
                ">ACTIVE SESSION</span>
                <span style="
                    color: #E5E7EB;
                    font-size: 0.85rem;
                    font-weight: 600;
                ">• {pdf_name_trimmed}</span>
            </div>
        </div>
    </div>
    <style>
    @keyframes pulse {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.6; }}
    }}
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("""
    <div style="
        text-align: center;
        padding: 1.5rem 1rem;
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(139, 92, 246, 0.15) 100%);
        border-radius: 12px;
        margin-bottom: 1.5rem;
        border: 1px solid rgba(99, 102, 241, 0.3);
    ">
        <h2 style="
            margin: 0;
            font-size: 2rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        ">⚡ Knowlium</h2>
        <p style="margin: 0.5rem 0 0 0; font-size: 0.8rem; color: #9CA3AF;">Document Intelligence</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="margin-bottom: 0.5rem;">
        <h3 style="font-size: 1.1rem; margin: 0; display: flex; align-items: center; gap: 0.5rem;">
            <span>📤</span> Upload Document
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="
        background: rgba(99, 102, 241, 0.1);
        border-left: 3px solid #6366f1;
        padding: 0.75rem;
        border-radius: 6px;
        margin-bottom: 1rem;
    ">
        <p style="margin: 0; font-size: 0.85rem; color: #C7D2FE;">
            📁 Drag & drop PDF or click Browse
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded = st.file_uploader("Choose PDF", type="pdf", key="pdf_uploader", label_visibility="collapsed")
    
    # Process uploaded document
    if uploaded and st.session_state.pdf_name != uploaded.name:
        st.session_state.processing_complete = False
        st.session_state.pdf_name = uploaded.name
        st.session_state.chat_history = []  # Reset chat
        st.session_state.key_insights = None
        st.session_state.document_analysis = None
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Step 1: Extract images
            status_text.text("📸 Extracting images...")
            progress_bar.progress(20)
            st.session_state.pdf_images = extract_images_from_pdf(uploaded)
            
            # Step 2: Extract and chunk text
            status_text.text("📖 Processing text...")
            progress_bar.progress(40)
            chunks, total_pages = extract_text_and_chunk(uploaded)
            
            if not chunks:
                st.error("❌ Could not extract readable text from PDF")
                st.stop()
            
            st.session_state.chunks = chunks
            st.session_state.pdf_pages = total_pages
            st.session_state.full_text = " ".join(chunks[:10])  # First 10 chunks for analysis
            
            # Step 3: Build vector database
            status_text.text("🔍 Building semantic search index...")
            progress_bar.progress(60)
            embeddings = load_embeddings()
            st.session_state.vectorstore = build_vectorstore(chunks, embeddings)
            
            # Step 4: Analyze document type
            status_text.text("🤖 Analyzing document type...")
            progress_bar.progress(80)
            doc_analysis = analyze_document_type(st.session_state.full_text)
            st.session_state.document_analysis = doc_analysis
            st.session_state.document_type = doc_analysis.get('type', 'General Document')
            
            # Step 5: Extract key insights
            status_text.text("💡 Extracting key insights...")
            progress_bar.progress(90)
            insights = extract_key_insights(chunks, st.session_state.document_type)
            st.session_state.key_insights = insights
            
            progress_bar.progress(100)
            status_text.empty()
            progress_bar.empty()
            
            st.session_state.processing_complete = True
            st.success("✅ Document processed successfully!")
            st.balloons()
            time.sleep(1)
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Error processing document: {str(e)}")
            st.stop()
    
    # Show document info if processed
    if st.session_state.processing_complete:
        st.markdown("""
        <div style="
            height: 1px;
            background: linear-gradient(90deg, transparent 0%, rgba(99, 102, 241, 0.5) 50%, transparent 100%);
            margin: 1.5rem 0;
        "></div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <h3 style="font-size: 1.1rem; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem;">
            <span>📊</span> Document Overview
        </h3>
        """, unsafe_allow_html=True)
        
        # Document stats
        stats = get_document_stats(
            st.session_state.chunks,
            st.session_state.pdf_pages,
            st.session_state.pdf_images
        )
        
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
            border-radius: 12px;
            padding: 1rem;
            margin-bottom: 1rem;
            border: 1px solid rgba(99, 102, 241, 0.2);
        ">
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 0.75rem;">
                <div style="text-align: center;">
                    <div style="font-size: 1.8rem; font-weight: 700; color: #6366f1;">
                        {stats['total_pages']}
                    </div>
                    <div style="font-size: 0.75rem; color: #9CA3AF; margin-top: 0.25rem;">
                        Pages
                    </div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 1.8rem; font-weight: 700; color: #8b5cf6;">
                        {stats['total_images']}
                    </div>
                    <div style="font-size: 0.75rem; color: #9CA3AF; margin-top: 0.25rem;">
                        Images
                    </div>
                </div>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                <div style="text-align: center;">
                    <div style="font-size: 1.8rem; font-weight: 700; color: #10b981;">
                        {stats['total_words']:,}
                    </div>
                    <div style="font-size: 0.75rem; color: #9CA3AF; margin-top: 0.25rem;">
                        Words
                    </div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 1.8rem; font-weight: 700; color: #f59e0b;">
                        {stats['estimated_read_time']}m
                    </div>
                    <div style="font-size: 0.75rem; color: #9CA3AF; margin-top: 0.25rem;">
                        Read Time
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Document type
        if st.session_state.document_analysis:
            doc_type = st.session_state.document_analysis.get('type', 'Unknown')
            confidence = st.session_state.document_analysis.get('confidence', 0)
            
            st.markdown(f"""
            <div class="mode-badge" style="padding: 0.5rem; background: rgba(255,255,255,0.05); border-radius: 6px; text-align: center; margin-bottom: 1rem;">
                📄 {doc_type} <span style="color: #9CA3AF;">({int(confidence*100)}%)</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="
            height: 1px;
            background: linear-gradient(90deg, transparent 0%, rgba(99, 102, 241, 0.5) 50%, transparent 100%);
            margin: 1.5rem 0;
        "></div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <h3 style="font-size: 1.1rem; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem;">
            <span>🎯</span> Interaction Modes
        </h3>
        """, unsafe_allow_html=True)
        
        # Mode selection based on document type
        mode_options = ["General Chat"]
        doc_type = st.session_state.document_type or "General Document"
        
        if doc_type == "Resume":
            mode_options.extend(["Resume Analysis", "Interview Prep"])
        elif doc_type in ["Cover Letter", "Statement of Purpose"]:
            mode_options.extend(["Application Review", "Writing Improvement"])
        elif doc_type == "Research Paper":
            mode_options.extend(["Deep Study", "Document Insights"])
        elif doc_type == "Study Material":
            mode_options.extend(["Deep Study", "Exam Prep"])
        elif doc_type in ["Business Report", "Proposal"]:
            mode_options.extend(["Document Insights", "Executive Summary"])
        elif doc_type == "Technical Documentation":
            mode_options.extend(["Technical Deep Dive", "Implementation Guide"])
        elif doc_type == "Legal Document":
            mode_options.extend(["Legal Analysis", "Clause Breakdown"])
        elif doc_type in ["Essay/Article", "Presentation"]:
            mode_options.extend(["Content Analysis", "Key Points"])
        else:
            mode_options.extend(["Deep Study", "Document Insights"])
        
        selected_mode = st.selectbox(
            "Choose interaction mode",
            mode_options,
            key="interaction_mode",
            help="Select how you want to interact with this document"
        )
        st.session_state.active_mode = selected_mode
        
        # Mode descriptions with enhanced styling
        mode_descriptions = {
            "General Chat": ("💬", "Ask any questions about the document", "#6366f1"),
            "Resume Analysis": ("📋", "Professional resume insights and analysis", "#8b5cf6"),
            "Interview Prep": ("🎯", "Preparation for interviews based on content", "#f59e0b"),
            "Application Review": ("📝", "Review and evaluate application documents", "#8b5cf6"),
            "Writing Improvement": ("✍️", "Suggestions to improve writing quality", "#10b981"),
            "Deep Study": ("📖", "In-depth learning and concept explanation", "#10b981"),
            "Exam Prep": ("📚", "Preparation for exams and assessments", "#f59e0b"),
            "Document Insights": ("📊", "Extract patterns, trends, and key findings", "#ec4899"),
            "Executive Summary": ("📈", "High-level overview and key takeaways", "#ec4899"),
            "Technical Deep Dive": ("⚙️", "Detailed technical analysis and explanation", "#6366f1"),
            "Implementation Guide": ("🛠️", "Step-by-step implementation guidance", "#10b981"),
            "Legal Analysis": ("⚖️", "Legal interpretation and risk analysis", "#f59e0b"),
            "Clause Breakdown": ("📋", "Detailed analysis of terms and clauses", "#8b5cf6"),
            "Content Analysis": ("🔍", "Analyze arguments, themes, and structure", "#ec4899"),
            "Key Points": ("🎯", "Extract and summarize main points", "#6366f1")
        }
        
        icon, desc, color = mode_descriptions.get(selected_mode, ("💬", "", "#6366f1"))
        
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
            border-left: 3px solid {color};
            padding: 0.75rem 1rem;
            border-radius: 8px;
            margin: 0.75rem 0;
        ">
            <p style="margin: 0; font-size: 0.9rem; color: #E5E7EB; display: flex; align-items: center; gap: 0.5rem;">
                <span style="font-size: 1.2rem;">{icon}</span> {desc}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Settings
        with st.expander("⚙️ Settings"):
            st.session_state.confidence_threshold = st.slider(
                "Confidence Threshold",
                0.0, 1.0, 0.7, 0.05,
                help="Minimum confidence score for answers"
            )
            
            if st.button("🗑️ Clear Chat History"):
                st.session_state.chat_history = []
                st.rerun()
            
            if st.button("🔄 Reset Document"):
                st.session_state.processing_complete = False
                st.session_state.pdf_name = ""
                st.session_state.chat_history = []
                st.rerun()

# --- MAIN CHAT AREA ---
if not st.session_state.processing_complete:
    # Header landing container
    st.write("### Transform your documents into intelligent conversations")
    st.write("Upload a PDF to unlock instant insights")

    # Native Python 2x2 column layouts to safely replace unrendered HTML grid
    grid_col1, grid_col2 = st.columns(2)
    with grid_col1:
        st.info("🔍 **Smart Search**\n\nSemantic search powered by advanced RAG technology")
        st.success("✅ **Verified Answers**\n\nFact-checking with confidence scores for accuracy")

    with grid_col2:
        st.warning("🤖 **AI Analysis**\n\nGroq LLM-powered intelligent document understanding")
        st.error("🎯 **Smart Modes**\n\nSpecialized interaction for resumes, research & more")

    st.caption("👈 Start by uploading a PDF from the sidebar")

else:
    # Show key insights at the top (collapsible)
    if st.session_state.key_insights and len(st.session_state.chat_history) == 0:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, rgba(251, 191, 36, 0.1) 0%, rgba(245, 158, 11, 0.1) 100%);
            border: 1px solid rgba(251, 191, 36, 0.3);
            border-radius: 16px;
            padding: 1.5rem;
            margin-bottom: 2rem;
        ">
            <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem;">
                <div style="font-size: 1.8rem;">💡</div>
                <h3 style="margin: 0; color: #FCD34D; font-size: 1.3rem; font-weight: 700;">Quick Insights</h3>
            </div>
        """, unsafe_allow_html=True)
        for insight in st.session_state.key_insights[:5]:
            st.markdown(f"""
            <div style="
                padding: 0.75rem 1rem;
                background: rgba(251, 191, 36, 0.05);
                border-left: 3px solid rgba(251, 191, 36, 0.5);
                border-radius: 6px;
                margin-bottom: 0.5rem;
            ">
                <p style="margin: 0; color: #FEF3C7; font-size: 0.95rem; line-height: 1.6;">
                    ▸ {insight}
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    # Show suggested questions if no chat history
    if len(st.session_state.chat_history) == 0:
        # Smart suggestions based on document type - STRICTLY MATCHED
        suggestions = {
            "Resume": [
                "▸ Calculate the ATS score and provide optimization tips",
                "▸ Generate interview questions based on this resume",
                "▸ What are the strongest skills and achievements?",
                "▸ How can I improve this resume for job applications?"
            ],
            "Resume/CV": [  # Alternative naming
                "▸ Calculate the ATS score and provide optimization tips",
                "▸ Generate interview questions based on this resume",
                "▸ What are the strongest skills and achievements?",
                "▸ How can I improve this resume for job applications?"
            ],
            "Cover Letter": [
                "▸ How effective is this cover letter?",
                "▸ What are the key strengths highlighted?",
                "▸ How can I make this cover letter more compelling?",
                "▸ Does this align well with the position requirements?"
            ],
            "Statement of Purpose": [
                "▸ Evaluate the strength and clarity of my motivation",
                "▸ What are the key strengths in this SOP?",
                "▸ How can I improve this statement of purpose?",
                "▸ Does this effectively communicate my goals and qualifications?"
            ],
            "Research Paper": [
                "▸ What is the main research question and hypothesis?",
                "▸ What are the key findings and results?",
                "▸ Explain the methodology and approach used",
                "▸ What conclusions and future work are suggested?"
            ],
            "Study Material": [
                "▸ What are the main topics and learning objectives?",
                "▸ Explain the key concepts in simple terms",
                "▸ What are the important definitions and formulas?",
                "▸ Create practice questions from this material"
            ],
            "Technical Documentation": [
                "▸ What are the main features and functionalities?",
                "▸ Explain the key technical concepts",
                "▸ What are the important configuration steps?",
                "▸ Summarize the API endpoints and parameters"
            ],
            "Business Report": [
                "▸ What are the key findings and insights?",
                "▸ Summarize the executive summary and overview",
                "▸ What trends and patterns are identified?",
                "▸ What are the main recommendations and action items?"
            ],
            "Legal Document": [
                "▸ What are the main terms and conditions?",
                "▸ What are the key obligations and rights?",
                "▸ Summarize the important clauses",
                "▸ What are the potential risks or concerns?"
            ],
            "Proposal": [
                "▸ What problem does this proposal address?",
                "▸ What is the proposed solution and approach?",
                "▸ What are the expected outcomes and benefits?",
                "▸ What is the timeline and budget?"
            ],
            "Essay/Article": [
                "▸ What is the main argument or thesis?",
                "▸ What are the key points and supporting evidence?",
                "▸ Summarize the author's perspective",
                "▸ What conclusions are drawn?"
            ],
            "Presentation": [
                "▸ What are the main talking points?",
                "▸ Summarize the key slides and messages",
                "▸ What data or evidence is presented?",
                "▸ What is the call to action?"
            ],
            "General Document": [
                "▸ What is the main purpose of this document?",
                "▸ Provide a comprehensive summary",
                "▸ What are the key points and takeaways?",
                "▸ Explain the main topics covered"
            ]
        }
        
        # Get document type and find matching suggestions
        doc_type = st.session_state.document_type or "General Document"
        
        # Try exact match first, then fallback
        doc_suggestions = suggestions.get(doc_type)
        if not doc_suggestions:
            # Try partial match (more specific matching)
            doc_type_lower = doc_type.lower()
            
            if "statement of purpose" in doc_type_lower or "sop" in doc_type_lower:
                doc_suggestions = suggestions["Statement of Purpose"]
            elif "cover letter" in doc_type_lower:
                doc_suggestions = suggestions["Cover Letter"]
            elif "resume" in doc_type_lower or "cv" in doc_type_lower:
                doc_suggestions = suggestions["Resume"]
            elif "research" in doc_type_lower or "paper" in doc_type_lower:
                doc_suggestions = suggestions["Research Paper"]
            elif "proposal" in doc_type_lower:
                doc_suggestions = suggestions["Proposal"]
            elif "technical" in doc_type_lower or "documentation" in doc_type_lower:
                doc_suggestions = suggestions["Technical Documentation"]
            elif "legal" in doc_type_lower or "contract" in doc_type_lower:
                doc_suggestions = suggestions["Legal Document"]
            elif "business report" in doc_type_lower or "report" in doc_type_lower:
                doc_suggestions = suggestions["Business Report"]
            elif "presentation" in doc_type_lower or "slides" in doc_type_lower:
                doc_suggestions = suggestions["Presentation"]
            elif "essay" in doc_type_lower or "article" in doc_type_lower:
                doc_suggestions = suggestions["Essay/Article"]
            elif "study" in doc_type_lower or "material" in doc_type_lower:
                doc_suggestions = suggestions["Study Material"]
            else:
                doc_suggestions = suggestions["General Document"]
        
        # Display suggestions in a nice grid
        cols = st.columns(2)
        for idx, suggestion in enumerate(doc_suggestions):
            with cols[idx % 2]:
                if st.button(suggestion, key=f"suggestion_{idx}", use_container_width=True):
                    # Extract just the text without emoji
                    question = ' '.join(suggestion.split()[1:])
                    st.session_state.pending_question = question
                    st.rerun()
    
    # Render chat history
    for i, chat in enumerate(st.session_state.chat_history):
        with st.chat_message("user"):
            st.write(chat['q'])
        
        with st.chat_message("assistant"):
            answer = chat['a']
            confidence = chat.get('confidence', 0.8)
            sources = chat.get('sources', [])
            
            # Format answer with confidence and sources
            if confidence > 0:
                formatted_answer = format_answer_with_confidence(answer, confidence, sources)
                st.markdown(formatted_answer, unsafe_allow_html=True)
            else:
                # Legacy support for old format
                highlighted = highlight_scores_in_text(answer)
                st.markdown(highlighted, unsafe_allow_html=True)
    
    # Enhanced Composer Section
    st.markdown("---")
    st.markdown('<div class="composer-container">', unsafe_allow_html=True)
    
    # Composer header
    mode = st.session_state.active_mode or "General Chat"
    mode_emoji = {
        "General Chat": "💬",
        "Resume Analysis": "📋",
        "Deep Study": "📖",
        "Interview Prep": "🎯",
        "Document Insights": "📊"
    }
    
    st.markdown(f"""
    <div style="margin-bottom: 0.5rem;">
        <span style="color: #9CA3AF; font-size: 0.85rem;">
            {mode_emoji.get(mode, "💬")} <strong>{mode}</strong> • Ready to answer your questions
        </span>
    </div>
    """, unsafe_allow_html=True)
    
    # Chat input with better placeholder
    placeholders = {
        "General Chat": "Ask anything about your document...",
        "Resume Analysis": "Ask about skills, experience, achievements...",
        "Deep Study": "Ask me to explain concepts or topics...",
        "Interview Prep": "Ask about preparation strategies...",
        "Document Insights": "Ask for analysis and patterns..."
    }
    
    question = st.chat_input(placeholders.get(mode, "Type your question here..."))
    
    # Process pending question from suggestion pills
    if 'pending_question' in st.session_state and st.session_state.pending_question:
        question = st.session_state.pending_question
        st.session_state.pending_question = None  # Clear immediately to avoid reprocessing
        
    if question:
        # Validate question
        is_valid, msg = validate_question(question)
        if not is_valid:
            st.error(msg)
            st.stop()
        
        # Show user message immediately
        with st.chat_message("user"):
            st.write(question)
        
        # Process question
        with st.chat_message("assistant"):
            with st.spinner("⏳ Thinking..."):
                try:
                    # Retrieve relevant documents
                    docs = st.session_state.vectorstore.similarity_search(question, k=8)  # Increased for better context
                    context = "\n\n".join([d.page_content for d in docs])
                    
                    # Get specialized prompt based on mode
                    mode = st.session_state.active_mode or "General Chat"
                    prompt = get_specialized_prompt(question, context, mode)
                    
                    # Query LLM
                    llm = get_groq_llm()
                    answer = query_llm(llm, prompt)
                    
                    # Verify answer and get confidence
                    verification = verify_answer(answer, docs, st.session_state.chunks)
                    confidence = verification['confidence']
                    sources = verification['sources']
                    
                    # Check against threshold
                    if confidence < st.session_state.confidence_threshold:
                        answer = f"{answer}\n\n⚠️ **Note:** This answer has low confidence ({int(confidence*100)}%). It may not be fully supported by the document. Please verify independently."
                    
                    # Format and display
                    formatted_answer = format_answer_with_confidence(answer, confidence, sources)
                    st.markdown(formatted_answer, unsafe_allow_html=True)
                    
                    # Save to history
                    st.session_state.chat_history.append({
                        'q': question,
                        'a': answer,
                        'confidence': confidence,
                        'sources': sources
                    })
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error generating answer: {str(e)}")