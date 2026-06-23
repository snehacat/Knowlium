# -*- coding: utf-8 -*-
"""
Knowlium - Configuration Module
UI configuration, styling, and session state management
"""

import streamlit as st

def init_page_config():
    st.set_page_config(
        page_title="Knowlium - Document Intelligence Platform",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': 'https://github.com/snehacat/knowlium',
            'Report a bug': 'https://github.com/snehacat/knowlium/issues',
            'About': '# Knowlium\nAI-Powered Document Intelligence Platform'
        }
    )

def init_session_state():
    defaults = {
        'vectorstore': None, 'chat_history': [], 'pdf_pages': 0, 'chunks': [],
        'verified': 0, 'unverified': 0, 'pdf_name': "", 'embeddings_model': None,
        'answer_cache': {}, 'pdf_images': [], 'document_type': None,
        'document_analysis': None, 'active_mode': None, 'processing_complete': False,
        'full_text': '', 'key_insights': None, 'show_sidebar': True,
        'current_view': 'chat', 'confidence_threshold': 0.7, 'pending_question': None
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

def inject_custom_css():
    st.markdown("""
    <style>
        /* Modern Dark Theme */
        .stApp {
            background: linear-gradient(135deg, #0F1419 0%, #1a1f2e 100%);
        }
        
        /* Sidebar Styling */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1a1f2e 0%, #0F1419 100%);
            border-right: 1px solid rgba(99, 102, 241, 0.2);
        }
        
        section[data-testid="stSidebar"] > div {
            padding-top: 2rem;
        }
        
        /* Hide default Streamlit elements */
        #MainMenu, footer, header {
            visibility: hidden;
        }
        
        /* Typography */
        h1, h2, h3 {
            color: #F9FAFB !important;
            font-weight: 700 !important;
            letter-spacing: -0.02em;
        }
        
        h1 {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2.5rem !important;
            margin-bottom: 0.5rem !important;
        }
        
        p, div, span, label {
            color: #E5E7EB !important;
        }
        
        /* Chat Message Styling */
        .stChatMessage {
            background: rgba(255, 255, 255, 0.03) !important;
            border: 1px solid rgba(99, 102, 241, 0.1);
            border-radius: 12px;
            padding: 1rem;
            margin: 0.5rem 0;
            backdrop-filter: blur(10px);
        }
        
        .stChatMessage[data-testid="user-message"] {
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%) !important;
            border-left: 3px solid #6366f1;
        }
        
        .stChatMessage[data-testid="assistant-message"] {
            background: rgba(16, 185, 129, 0.05) !important;
            border-left: 3px solid #10b981;
        }
        
        /* Input Styling */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea {
            background-color: rgba(31, 41, 55, 0.8) !important;
            color: #F9FAFB !important;
            border: 1px solid rgba(99, 102, 241, 0.3) !important;
            border-radius: 8px;
            padding: 0.75rem;
            font-size: 0.95rem;
        }
        
        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus {
            border-color: #6366f1 !important;
            box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2) !important;
        }
        
        /* Button Styling */
        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white !important;
            border: none;
            border-radius: 8px;
            padding: 0.6rem 1.5rem;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 4px 6px rgba(99, 102, 241, 0.3);
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(99, 102, 241, 0.4);
        }
        
        /* File Uploader */
        .stFileUploader {
            background: rgba(31, 41, 55, 0.5);
            border: 2px dashed rgba(99, 102, 241, 0.4);
            border-radius: 12px;
            padding: 1.5rem;
            transition: all 0.3s ease;
        }
        
        .stFileUploader:hover {
            border-color: #6366f1;
            background: rgba(99, 102, 241, 0.05);
        }
        
        /* Metrics and Cards */
        div[data-testid="metric-container"] {
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
            border: 1px solid rgba(99, 102, 241, 0.2);
            border-radius: 10px;
            padding: 1rem;
            backdrop-filter: blur(10px);
        }
        
        div[data-testid="metric-container"] label {
            color: #9CA3AF !important;
            font-size: 0.85rem;
            font-weight: 500;
        }
        
        div[data-testid="metric-container"] > div {
            color: #F9FAFB !important;
            font-weight: 700;
            font-size: 1.5rem;
        }
        
        /* Expander */
        .streamlit-expanderHeader {
            background: rgba(31, 41, 55, 0.6);
            border: 1px solid rgba(99, 102, 241, 0.2);
            border-radius: 8px;
            color: #F9FAFB !important;
            font-weight: 600;
        }
        
        .streamlit-expanderHeader:hover {
            background: rgba(99, 102, 241, 0.1);
        }
        
        /* Spinner */
        .stSpinner > div {
            border-top-color: #6366f1 !important;
        }
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background: rgba(31, 41, 55, 0.5);
            padding: 0.5rem;
            border-radius: 10px;
        }
        
        .stTabs [data-baseweb="tab"] {
            background: transparent;
            color: #9CA3AF;
            border-radius: 6px;
            padding: 0.5rem 1rem;
            font-weight: 600;
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white !important;
        }
        
        /* Success/Error/Info Messages */
        .stSuccess, .stError, .stInfo, .stWarning {
            border-radius: 8px;
            border-left-width: 4px;
            backdrop-filter: blur(10px);
        }
        
        /* Scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: rgba(31, 41, 55, 0.5);
        }
        
        ::-webkit-scrollbar-thumb {
            background: rgba(99, 102, 241, 0.5);
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: rgba(99, 102, 241, 0.7);
        }
        
        /* Confidence Score Badge */
        .confidence-badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
            margin-left: 0.5rem;
        }
        
        .confidence-high {
            background: rgba(16, 185, 129, 0.2);
            color: #10b981;
            border: 1px solid rgba(16, 185, 129, 0.4);
        }
        
        .confidence-medium {
            background: rgba(251, 191, 36, 0.2);
            color: #fbbf24;
            border: 1px solid rgba(251, 191, 36, 0.4);
        }
        
        .confidence-low {
            background: rgba(239, 68, 68, 0.2);
            color: #ef4444;
            border: 1px solid rgba(239, 68, 68, 0.4);
        }
        
        /* Source Citation */
        .source-citation {
            background: rgba(99, 102, 241, 0.1);
            border-left: 3px solid #6366f1;
            padding: 0.75rem;
            margin: 0.5rem 0;
            border-radius: 6px;
            font-size: 0.9rem;
            font-style: italic;
        }
        
        /* Mode Badge */
        .mode-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.5rem 1rem;
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.2) 0%, rgba(139, 92, 246, 0.2) 100%);
            border: 1px solid rgba(99, 102, 241, 0.4);
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.9rem;
            margin: 0.5rem 0;
        }
        
        /* Quick Action Button */
        .quick-action {
            background: rgba(31, 41, 55, 0.8);
            border: 1px solid rgba(99, 102, 241, 0.3);
            border-radius: 8px;
            padding: 0.75rem;
            margin: 0.5rem 0;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .quick-action:hover {
            background: rgba(99, 102, 241, 0.1);
            border-color: #6366f1;
            transform: translateX(4px);
        }
        
        /* Document Stats */
        .doc-stat {
            background: rgba(31, 41, 55, 0.6);
            padding: 1rem;
            border-radius: 8px;
            border: 1px solid rgba(99, 102, 241, 0.2);
            text-align: center;
        }
        
        .doc-stat-value {
            font-size: 1.8rem;
            font-weight: 700;
            color: #6366f1;
        }
        
        .doc-stat-label {
            font-size: 0.85rem;
            color: #9CA3AF;
            margin-top: 0.25rem;
        }
        
        /* Enhanced Chat Input Composer */
        .stChatInputContainer {
            position: sticky;
            bottom: 0;
            background: linear-gradient(180deg, transparent 0%, #0F1419 20%);
            padding: 1.5rem 0 1rem 0;
            z-index: 999;
        }
        
        .stChatInput {
            background: rgba(31, 41, 55, 0.95) !important;
            border: 2px solid rgba(99, 102, 241, 0.4) !important;
            border-radius: 16px !important;
            backdrop-filter: blur(20px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4), 0 0 0 1px rgba(99, 102, 241, 0.2);
            transition: all 0.3s ease;
        }
        
        .stChatInput:focus-within {
            border-color: #6366f1 !important;
            box-shadow: 0 8px 32px rgba(99, 102, 241, 0.3), 0 0 0 2px rgba(99, 102, 241, 0.4);
            transform: translateY(-2px);
        }
        
        .stChatInput textarea {
            font-size: 0.95rem !important;
            line-height: 1.6 !important;
            color: #F9FAFB !important;
        }
        
        .stChatInput textarea::placeholder {
            color: #6B7280 !important;
            font-style: italic;
        }
        
        /* Composer Container */
        .composer-container {
            position: sticky;
            bottom: 0;
            background: linear-gradient(180deg, rgba(15, 20, 25, 0) 0%, rgba(15, 20, 25, 0.95) 20%, rgba(15, 20, 25, 1) 40%);
            padding: 2rem 1rem 1rem 1rem;
            margin-top: 2rem;
            z-index: 1000;
            backdrop-filter: blur(10px);
        }
        
        .composer-wrapper {
            background: rgba(31, 41, 55, 0.8);
            border: 2px solid rgba(99, 102, 241, 0.3);
            border-radius: 20px;
            padding: 1.5rem;
            backdrop-filter: blur(20px);
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
            transition: all 0.3s ease;
        }
        
        .composer-wrapper:focus-within {
            border-color: #6366f1;
            box-shadow: 0 10px 40px rgba(99, 102, 241, 0.4);
        }
        
        .composer-header {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            margin-bottom: 1rem;
            padding-bottom: 0.75rem;
            border-bottom: 1px solid rgba(99, 102, 241, 0.2);
        }
        
        .composer-icon {
            font-size: 1.2rem;
        }
        
        .composer-title {
            font-size: 0.9rem;
            font-weight: 600;
            color: #9CA3AF;
        }
        
        .quick-prompts {
            display: flex;
            gap: 0.5rem;
            margin-top: 0.75rem;
            flex-wrap: wrap;
        }
        
        .quick-prompt-btn {
            background: rgba(99, 102, 241, 0.1);
            border: 1px solid rgba(99, 102, 241, 0.3);
            color: #A5B4FC;
            padding: 0.4rem 0.8rem;
            border-radius: 12px;
            font-size: 0.8rem;
            cursor: pointer;
            transition: all 0.2s ease;
            white-space: nowrap;
        }
        
        .quick-prompt-btn:hover {
            background: rgba(99, 102, 241, 0.2);
            border-color: #6366f1;
            transform: translateY(-1px);
        }
        
        /* Suggestion Pills */
        .suggestion-pills {
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
            margin: 1rem 0;
            padding: 1rem;
            background: rgba(31, 41, 55, 0.4);
            border-radius: 12px;
            border: 1px solid rgba(99, 102, 241, 0.2);
        }
        
        .suggestion-pill {
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(139, 92, 246, 0.15) 100%);
            border: 1px solid rgba(99, 102, 241, 0.3);
            color: #C7D2FE;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-size: 0.85rem;
            cursor: pointer;
            transition: all 0.2s ease;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .suggestion-pill:hover {
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.25) 0%, rgba(139, 92, 246, 0.25) 100%);
            border-color: #6366f1;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
        }
    </style>
    """, unsafe_allow_html=True)