# -*- coding: utf-8 -*-
"""
Knowlium - PDF Processor Module
PDF text extraction, image extraction, and chunking with OCR support
"""

import fitz  
from PyPDF2 import PdfReader
from PIL import Image
import io
from langchain_text_splitters import RecursiveCharacterTextSplitter

# OCR support
try:
    import pytesseract
    from pdf2image import convert_from_bytes
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("OCR not available. Install with: pip install pytesseract pdf2image pillow")

def extract_images_from_pdf(pdf_file) -> list:
    """Extract all images from PDF"""
    images = []
    try:
        pdf_file.seek(0)
        pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            for img_index, img in enumerate(page.get_images()):
                xref = img[0]
                base_image = pdf_document.extract_image(xref)
                image_bytes = base_image["image"]
                try:
                    image = Image.open(io.BytesIO(image_bytes))
                    if image.mode != 'RGB':
                        image = image.convert('RGB')
                    images.append({'page': page_num + 1, 'image': image, 'index': img_index})
                except:
                    continue
        pdf_document.close()
    except Exception:
        pass  # for the caller to handle exceptions
    return images

def extract_text_with_ocr(pdf_file):
    """Extract text from scanned PDFs using OCR"""
    if not OCR_AVAILABLE:
        print("DEBUG: OCR not available - skipping OCR extraction")
        return "", 0
    
    text = ""
    pdf_file.seek(0)
    
    try:
        print("DEBUG: 🔍 Attempting OCR extraction...")
        
        # Convert PDF to images
        images = convert_from_bytes(pdf_file.read(), dpi=200)
        total_pages = len(images)
        
        print(f"DEBUG: OCR processing {total_pages} pages (this may take a while)...")
        
        for page_num, image in enumerate(images):
            print(f"DEBUG: OCR Page {page_num + 1}/{total_pages}...")
            
            # Perform OCR on image
            page_text = pytesseract.image_to_string(image, lang='eng')
            
            if page_text.strip():
                word_count = len(page_text.split())
                print(f"DEBUG: OCR Page {page_num + 1}: {word_count} words extracted")
                text += f"\n\n{page_text}"
            else:
                print(f"DEBUG: OCR Page {page_num + 1}: No text found")
        
        total_words = len(text.split())
        print(f"DEBUG: ✓ OCR Total: {total_words} words extracted")
        
        return text.strip(), total_pages
        
    except Exception as e:
        print(f"DEBUG: OCR extraction failed: {e}")
        return "", 0

def extract_text_from_pdf(pdf_file):
    """Extract all text from PDF using multiple methods for better accuracy"""
    text = ""
    pdf_file.seek(0)
    total_pages = 0
    
    # Method 1: PyMuPDF (fitz) - Usually best for text extraction
    try:
        pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")
        total_pages = len(pdf_document)
        
        print(f"DEBUG: Processing {total_pages} pages...")
        
        for page_num, page in enumerate(pdf_document):
            # Extract text with better options
            page_text = page.get_text("text", sort=True)  # sort=True for better text order
            
            # If page seems empty, try different extraction method
            if len(page_text.strip()) < 10:
                page_text = page.get_text("blocks") 
                if isinstance(page_text, list):
                    page_text = " ".join([block[4] for block in page_text if len(block) > 4])
            
            page_word_count = len(page_text.split())
            print(f"DEBUG: Page {page_num + 1}: {page_word_count} words")
            
            text += f"\n\n{page_text}"  
        
        pdf_document.close()
        
        total_words = len(text.split())
        print(f"DEBUG: Total extracted: {total_words} words")
        
        # Check if OCR is needed (low word count indicates scanned PDF)
        avg_words_per_page = total_words / total_pages if total_pages > 0 else 0
        if avg_words_per_page < 100 and OCR_AVAILABLE:
            print(f"DEBUG:  Low word count detected ({avg_words_per_page:.0f} words/page)")
            print(f"DEBUG: This might be a scanned PDF - Attempting OCR...")
            
            ocr_text, ocr_pages = extract_text_with_ocr(pdf_file)
            
            if ocr_text and len(ocr_text.split()) > total_words * 2:  # OCR found significantly more text
                print(f"DEBUG: ✓ OCR extracted {len(ocr_text.split())} words (much better) - Using OCR results")
                return ocr_text, ocr_pages
            else:
                print("DEBUG: Keeping PyMuPDF results (OCR didn't improve)")
        
    except Exception as e:
        print(f"DEBUG: PyMuPDF failed: {e}")
        # Fallback Method: PyPDF2
        try:
            pdf_file.seek(0)
            reader = PdfReader(pdf_file, strict=False)
            total_pages = len(reader.pages)
            
            print(f"DEBUG: Fallback to PyPDF2 for {total_pages} pages...")
            
            for page_num, page in enumerate(reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        page_word_count = len(page_text.split())
                        print(f"DEBUG: Page {page_num + 1}: {page_word_count} words")
                        text += f"\n\n{page_text}"
                except Exception as pe:
                    print(f"DEBUG: Page {page_num + 1} failed: {pe}")
                    continue
            
            total_words = len(text.split())
            avg_words_per_page = total_words / total_pages if total_pages > 0 else 0
            
            if avg_words_per_page < 100 and OCR_AVAILABLE:
                print(f"DEBUG: Low word count from PyPDF2 ({avg_words_per_page:.0f} words/page) - Trying OCR...")
                ocr_text, ocr_pages = extract_text_with_ocr(pdf_file)
                
                if ocr_text and len(ocr_text.split()) > total_words * 2:
                    print("DEBUG: Using OCR results")
                    return ocr_text, ocr_pages
                    
        except Exception as e2:
            print(f"DEBUG: Both extraction methods failed: {e}, {e2}")
    
    return text.strip(), total_pages

def extract_text_and_chunk(pdf_file):
    """Extract text and create intelligent chunks with metadata"""
    
    # Extract all text
    text, total_pages = extract_text_from_pdf(pdf_file)
    
    if not text or len(text) < 50:
        return None, total_pages
    
    # Debug: Show total extracted text
    total_words = len(text.split())
    total_chars = len(text)
    print(f"DEBUG: Final text - {total_words} words, {total_chars} characters")
    
    # Create chunks with larger size for better context
    # Increased from 500 to 1000 characters with 100 overlap
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,  # Larger chunks for better context
        chunk_overlap=100,  # More overlap to maintain context
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""]  # Better split points
    )
    
    chunks = splitter.split_text(text)
    
    print(f"DEBUG: Created {len(chunks)} chunks")
    
    return chunks, total_pages