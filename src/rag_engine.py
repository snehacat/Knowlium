# -*- coding: utf-8 -*-
"""
Knowlium - RAG Engine Module
RAG implementation, LLM integration, and document analysis
"""

import os
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq

def load_embeddings():
    """Load HuggingFace embeddings model for semantic search"""
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'}
    )

def build_vectorstore(chunks, embeddings):
    """Build FAISS vector database from text chunks"""
    if not chunks:
        return None
    
    # Create documents with better metadata
    documents = []
    for i, chunk in enumerate(chunks):
        documents.append(chunk)
    
    # Build FAISS index with more efficient settings
    vectorstore = FAISS.from_texts(documents, embeddings)
    return vectorstore

def get_groq_llm(model_name="llama-3.1-8b-instant", temperature=0.3):
    """Initialize Groq LLM with specified parameters"""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in environment variables")
    
    return ChatGroq(
        model=model_name,
        temperature=temperature,
        groq_api_key=api_key,
        max_tokens=1500  
    )

def query_llm(llm, prompt):
    """Query LLM with given prompt and return response"""
    response = llm.invoke(prompt)
    return response.content.strip()

def analyze_document_type(text_sample: str) -> dict:
    """Deep analysis of document type using LLM"""
    llm = get_groq_llm(temperature=0.1)
    
    prompt = f"""Analyze this document excerpt and classify it into the MOST SPECIFIC category that fits.

Document Excerpt:
{text_sample[:2000]}

**Document Categories** (choose the MOST SPECIFIC):

1. **Resume/CV** - Professional background, work experience, skills, employment history
2. **Cover Letter** - Job application letter, introduction to potential employer, position-specific
3. **Statement of Purpose (SOP)** - Academic/graduate school application, personal statement, motivation letter, study plans
4. **Research Paper** - Academic paper with abstract, methodology, literature review, results, citations
5. **Study Material** - Textbooks, course notes, lecture materials, educational content with chapters/lessons
6. **Technical Documentation** - API docs, user manuals, software documentation, technical guides
7. **Business Report** - Business analysis, financial reports, quarterly reports, executive summaries
8. **Legal Document** - Contracts, agreements, terms of service, legal notices, policies
9. **Proposal** - Project proposals, business proposals, grant proposals, funding requests
10. **Essay/Article** - Opinion pieces, blog posts, essays, articles without formal structure
11. **Presentation** - Slides, presentation notes, pitch decks
12. **General Document** - Other document types not fitting above categories

**Classification Rules:**
- Be VERY SPECIFIC - don't default to "General" unless truly unclassifiable
- Statement of Purpose ≠ Study Material (SOP is personal/motivational, study material is educational content)
- Cover Letter ≠ Resume (cover letter is narrative, resume is structured history)
- Research Paper has formal structure (abstract, methodology, results, references)
- Look for specific indicators and keywords

Provide your analysis in this EXACT format:
TYPE: [EXACT category name from above list]
CONFIDENCE: [0.0-1.0]
KEY_FEATURES: [3-4 specific features that led to this classification]
RECOMMENDED_MODE: [suggested interaction mode]

Be precise and specific."""

    try:
        response = query_llm(llm, prompt)
        
        # Parse response
        type_match = None
        confidence = 0.7
        features = []
        mode = "General Chat"
        
        for line in response.split('\n'):
            line = line.strip()
            if line.startswith('TYPE:'):
                type_match = line.replace('TYPE:', '').strip()
            elif line.startswith('CONFIDENCE:'):
                try:
                    confidence = float(line.replace('CONFIDENCE:', '').strip())
                except:
                    confidence = 0.7
            elif line.startswith('KEY_FEATURES:'):
                features.append(line.replace('KEY_FEATURES:', '').strip())
            elif line.startswith('RECOMMENDED_MODE:'):
                mode = line.replace('RECOMMENDED_MODE:', '').strip()
            elif line.startswith('-') or line.startswith('•'):
                features.append(line.lstrip('-•').strip())
        
        # Normalize document type to match exact categories
        normalized_type = type_match or 'General Document'
        
        # Normalize variations to standard names with PRIORITY ORDER
        normalized_lower = normalized_type.lower()
        
        # Check for specific types FIRST (most specific to least specific)
        if 'statement of purpose' in normalized_lower or 'sop' in normalized_lower or 'motivation letter' in normalized_lower or 'personal statement' in normalized_lower:
            normalized_type = 'Statement of Purpose'
        elif 'cover letter' in normalized_lower or 'application letter' in normalized_lower:
            normalized_type = 'Cover Letter'
        elif 'resume' in normalized_lower or 'cv' in normalized_lower or 'curriculum vitae' in normalized_lower:
            normalized_type = 'Resume'
        elif 'research paper' in normalized_lower or 'academic paper' in normalized_lower or ('paper' in normalized_lower and ('abstract' in normalized_lower or 'methodology' in normalized_lower)):
            normalized_type = 'Research Paper'
        elif 'proposal' in normalized_lower or 'grant' in normalized_lower:
            normalized_type = 'Proposal'
        elif 'technical' in normalized_lower or 'documentation' in normalized_lower or 'api' in normalized_lower or 'manual' in normalized_lower:
            normalized_type = 'Technical Documentation'
        elif 'legal' in normalized_lower or 'contract' in normalized_lower or 'agreement' in normalized_lower or 'terms' in normalized_lower:
            normalized_type = 'Legal Document'
        elif 'business report' in normalized_lower or 'financial report' in normalized_lower or 'quarterly' in normalized_lower or 'executive summary' in normalized_lower:
            normalized_type = 'Business Report'
        elif 'presentation' in normalized_lower or 'slides' in normalized_lower or 'pitch deck' in normalized_lower:
            normalized_type = 'Presentation'
        elif 'essay' in normalized_lower or 'article' in normalized_lower or 'blog' in normalized_lower:
            normalized_type = 'Essay/Article'
        elif 'study' in normalized_lower or 'material' in normalized_lower or 'textbook' in normalized_lower or 'course' in normalized_lower or 'lecture' in normalized_lower:
            normalized_type = 'Study Material'
        elif 'report' in normalized_lower:
            normalized_type = 'Business Report'
        else:
            normalized_type = 'General Document'
        
        return {
            'type': normalized_type,
            'confidence': confidence,
            'features': features[:4],
            'recommended_mode': mode
        }
    except Exception as e:
        return {
            'type': 'General Document',
            'confidence': 0.5,
            'features': ['Analysis failed'],
            'recommended_mode': 'General Chat'
        }

def generate_summary(text: str, max_length: int = 300) -> str:
    """Generate concise summary of document"""
    llm = get_groq_llm(temperature=0.2)
    
    prompt = f"""Provide a concise summary (max {max_length} words) of this document:

{text[:3000]}

Focus on the main topics, key points, and overall purpose."""

    try:
        summary = query_llm(llm, prompt)
        return summary
    except Exception as e:
        return "Summary generation failed. Please try again."

def extract_key_insights(chunks: list, document_type: str) -> list:
    """Extract key insights based on document type"""
    llm = get_groq_llm(temperature=0.2)
    
    # Combine relevant chunks
    sample_text = "\n\n".join(chunks[:5])  # First 5 chunks
    
    if document_type == "Resume":
        prompt = f"""Analyze this resume and extract key professional highlights:

{sample_text}

Provide a concise bullet-point analysis:

**PROFESSIONAL SUMMARY:**
- Current role/title and experience level
- Top 3 technical/professional skills
- Years of relevant experience

**KEY ACHIEVEMENTS:**
- Most impressive accomplishments (with metrics if available)
- Career highlights

**EDUCATION & CERTIFICATIONS:**
- Highest degree and institution
- Relevant certifications

**STANDOUT QUALITIES:**
- What makes this candidate unique
- Strongest selling points

Format as clear, scannable bullet points. Be specific and use actual data from the resume."""
    
    elif document_type == "Cover Letter":
        prompt = f"""Analyze this cover letter and extract key points:

{sample_text}

Provide a concise analysis:

**TARGET POSITION & COMPANY:**
- Position applied for
- Company/organization mentioned

**KEY QUALIFICATIONS:**
- Top relevant skills highlighted
- Main experiences referenced

**MOTIVATION & FIT:**
- Why candidate is interested
- How candidate aligns with role

**CALL TO ACTION:**
- Closing message and next steps

Be specific and concise."""
    
    elif document_type == "Statement of Purpose":
        prompt = f"""Analyze this Statement of Purpose and extract key elements:

{sample_text}

Provide a structured analysis:

**ACADEMIC/CAREER GOALS:**
- Primary objectives
- Program/opportunity seeking

**BACKGROUND & EXPERIENCE:**
- Relevant academic background
- Key projects or research experience

**MOTIVATION:**
- Why this program/opportunity
- What drives the candidate

**FUTURE PLANS:**
- Career aspirations
- How this opportunity fits

Be clear and specific."""
    
    elif document_type == "Research Paper":
        prompt = f"""Extract key insights from this research paper:

{sample_text}

Provide:
- Main Research Question
- Methodology
- Key Findings (top 3)
- Conclusions

Be concise and bullet-pointed."""
    
    elif document_type == "Study Material":
        prompt = f"""Extract key learning points from this study material:

{sample_text}

Provide:
- Main Topics (top 3-4)
- Key Concepts
- Important Definitions
- Practice Areas

Be concise and bullet-pointed."""
    
    elif document_type in ["Business Report", "Proposal"]:
        prompt = f"""Extract key insights from this {document_type.lower()}:

{sample_text}

Provide:
- Executive Summary
- Key Findings (top 3-4)
- Recommendations
- Next Steps/Action Items

Be concise and bullet-pointed."""
    
    elif document_type == "Technical Documentation":
        prompt = f"""Extract key technical points from this documentation:

{sample_text}

Provide:
- Main Features/Components
- Key Technical Concepts
- Important Configuration/Setup Steps
- Common Use Cases

Be concise and bullet-pointed."""
    
    elif document_type == "Legal Document":
        prompt = f"""Extract key points from this legal document:

{sample_text}

Provide:
- Document Type and Purpose
- Key Terms and Conditions
- Important Obligations
- Notable Clauses or Restrictions

Be concise and bullet-pointed."""
    
    elif document_type in ["Essay/Article", "Presentation"]:
        prompt = f"""Extract main points from this {document_type.lower()}:

{sample_text}

Provide:
- Main Thesis/Message
- Key Arguments (top 3-4)
- Supporting Evidence
- Conclusions

Be concise and bullet-pointed."""
    
    else:
        prompt = f"""Extract the most important insights from this document:

{sample_text}

Provide:
- Main Purpose
- Key Points (top 4)
- Important Details
- Conclusions/Takeaways

Be concise and bullet-pointed."""
    
    try:
        insights = query_llm(llm, prompt)
        # Split into list
        insight_list = [line.strip() for line in insights.split('\n') if line.strip() and len(line.strip()) > 5]
        return insight_list[:8]  # Max 8 insights
    except Exception as e:
        return ["Insight extraction failed. Please try asking specific questions."]

def get_specialized_prompt(question: str, context: str, mode: str) -> str:
    """Generate specialized prompts based on active mode"""
    
    base_instruction = f"""Context from document:
{context}

User Question: {question}

"""
    
    if mode == "Resume Analysis":
        # Check if question is about ATS score
        if any(keyword in question.lower() for keyword in ['ats', 'score', 'optimization', 'optimize']):
            return base_instruction + """You are an expert ATS (Applicant Tracking System) analyzer and resume consultant.

Analyze this resume and provide:

1. **ATS SCORE (0-100)**:
   - Calculate overall ATS compatibility score
   - Consider: keyword optimization, formatting, section structure, measurable achievements

2. **STRENGTHS** (What's working well):
   - Strong keywords and skills
   - Well-formatted sections
   - Quantifiable achievements
   - Industry-relevant experience

3. **WEAKNESSES** (What needs improvement):
   - Missing critical keywords
   - Formatting issues
   - Vague descriptions
   - Gaps or inconsistencies

4. **OPTIMIZATION RECOMMENDATIONS**:
   - Specific keywords to add
   - Sections to improve
   - Achievement metrics to include
   - Action verbs to use

5. **QUICK WINS** (Easy improvements for immediate impact)

Be specific, actionable, and professional. Use only information from the provided context."""

        # Check if question is about interview questions
        elif any(keyword in question.lower() for keyword in ['interview', 'question', 'prepare', 'preparation']):
            return base_instruction + """You are an expert interview coach preparing a candidate based on their resume.

Generate comprehensive interview preparation:

1. **TOP 10 INTERVIEW QUESTIONS** (Based on this resume):
   - Behavioral questions about experience
   - Technical questions about skills mentioned
   - Situational questions about projects
   - Questions about achievements and impact

2. **SUGGESTED ANSWERS** (For each question):
   - Use the STAR method (Situation, Task, Action, Result)
   - Reference specific experiences from the resume
   - Highlight measurable achievements
   - Keep answers concise (2-3 minutes)

3. **KEY TALKING POINTS**:
   - Your unique value proposition
   - Top 3 strengths to emphasize
   - Notable achievements to mention
   - Career progression story

4. **POTENTIAL CONCERNS TO ADDRESS**:
   - Any career gaps
   - Job transitions
   - Missing qualifications
   - How to position yourself

5. **QUESTIONS TO ASK THE INTERVIEWER**:
   - 5 intelligent questions based on the role/industry

Be specific, reference the resume directly, and provide actionable guidance."""

        else:
            # General resume analysis
            return base_instruction + """You are a professional resume analyst and career consultant. Provide insights about:
- Skills, expertise, and qualifications
- Experience level and career progression
- Strengths and notable achievements
- Areas of specialization
- Professional background

Be professional, concise, and evidence-based. Only use information from the provided context."""

    elif mode == "Deep Study":
        return base_instruction + """You are a study assistant. Help the user understand the material by:
- Explaining concepts clearly
- Providing examples when helpful
- Breaking down complex topics
- Connecting related ideas

Be educational, clear, and thorough. Use only the provided context."""

    elif mode == "Interview Prep":
        return base_instruction + """You are helping prepare for an interview based on this document. Provide:
- Potential interview questions
- Key talking points
- How to present information effectively
- Areas to emphasize

Be strategic and practical. Use only the provided context."""

    elif mode == "Document Insights":
        return base_instruction + """You are analyzing this document for insights. Provide:
- Data-driven observations
- Key patterns or trends
- Important conclusions
- Actionable takeaways

Be analytical and objective. Use only the provided context."""

    else:  # General Chat
        return base_instruction + """Answer the user's question based on the document context provided.
Be accurate, concise, and helpful. 
Only use information from the provided context.
If the answer isn't in the context, say so clearly."""


def calculate_ats_score(resume_text: str) -> dict:
    """Calculate ATS compatibility score for a resume"""
    llm = get_groq_llm(temperature=0.1)
    
    prompt = f"""As an ATS (Applicant Tracking System) expert, analyze this resume and calculate its ATS compatibility score.

Resume:
{resume_text[:3000]}

Provide analysis in this exact format:

ATS_SCORE: [number 0-100]
KEYWORD_SCORE: [number 0-100]
FORMAT_SCORE: [number 0-100]
CONTENT_SCORE: [number 0-100]

STRENGTHS:
- [strength 1]
- [strength 2]
- [strength 3]

WEAKNESSES:
- [weakness 1]
- [weakness 2]
- [weakness 3]

CRITICAL_KEYWORDS_MISSING:
- [missing keyword 1]
- [missing keyword 2]

RECOMMENDATIONS:
- [recommendation 1]
- [recommendation 2]
- [recommendation 3]

Be specific and actionable. Base scores on: keyword optimization, formatting clarity, quantifiable achievements, and ATS-friendly structure."""

    try:
        response = query_llm(llm, prompt)
        
        # Parse the response
        lines = response.split('\n')
        result = {
            'ats_score': 70,
            'keyword_score': 70,
            'format_score': 70,
            'content_score': 70,
            'strengths': [],
            'weaknesses': [],
            'missing_keywords': [],
            'recommendations': []
        }
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('ATS_SCORE:'):
                try:
                    result['ats_score'] = int(line.split(':')[1].strip())
                except:
                    pass
            elif line.startswith('KEYWORD_SCORE:'):
                try:
                    result['keyword_score'] = int(line.split(':')[1].strip())
                except:
                    pass
            elif line.startswith('FORMAT_SCORE:'):
                try:
                    result['format_score'] = int(line.split(':')[1].strip())
                except:
                    pass
            elif line.startswith('CONTENT_SCORE:'):
                try:
                    result['content_score'] = int(line.split(':')[1].strip())
                except:
                    pass
            elif line.startswith('STRENGTHS:'):
                current_section = 'strengths'
            elif line.startswith('WEAKNESSES:'):
                current_section = 'weaknesses'
            elif line.startswith('CRITICAL_KEYWORDS_MISSING:'):
                current_section = 'missing_keywords'
            elif line.startswith('RECOMMENDATIONS:'):
                current_section = 'recommendations'
            elif line.startswith('-') and current_section:
                item = line.lstrip('- ').strip()
                if item:
                    result[current_section].append(item)
        
        return result
        
    except Exception as e:
        return {
            'ats_score': 0,
            'error': str(e),
            'strengths': [],
            'weaknesses': ['Analysis failed'],
            'missing_keywords': [],
            'recommendations': ['Please try again']
        }


def generate_interview_questions(resume_text: str) -> dict:
    """Generate interview questions based on resume"""
    llm = get_groq_llm(temperature=0.3)
    
    prompt = f"""As an expert interview coach, generate comprehensive interview preparation based on this resume.

Resume:
{resume_text[:3000]}

Provide:

BEHAVIORAL_QUESTIONS: (5 questions)
1. [Question about experience]
2. [Question about teamwork]
3. [Question about challenges]
4. [Question about leadership]
5. [Question about conflict resolution]

TECHNICAL_QUESTIONS: (5 questions based on skills mentioned)
1. [Technical question 1]
2. [Technical question 2]
3. [Technical question 3]
4. [Technical question 4]
5. [Technical question 5]

SITUATIONAL_QUESTIONS: (3 questions)
1. [Situational scenario 1]
2. [Situational scenario 2]
3. [Situational scenario 3]

KEY_TALKING_POINTS:
- [Talking point 1]
- [Talking point 2]
- [Talking point 3]

QUESTIONS_TO_ASK:
- [Intelligent question 1]
- [Intelligent question 2]
- [Intelligent question 3]

Base all questions on actual experience, skills, and achievements from the resume."""

    try:
        response = query_llm(llm, prompt)
        return {
            'success': True,
            'content': response
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }