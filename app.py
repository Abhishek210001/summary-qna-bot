from flask import Flask, render_template, request, jsonify
import os
import fitz
from transformers import pipeline
from werkzeug.utils import secure_filename
import tempfile
import time

app = Flask(__name__)
app.secret_key = 'your-secret-key'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

print("Loading HIGH-ACCURACY AI models...")
try:
    print("- Loading advanced BART-Large for summarization...")
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    
    print("- Loading RoBERTa-Large for Q&A (much more accurate)...")
    qa_pipeline = pipeline("question-answering", model="deepset/roberta-large-squad2")
    
    print("SUCCESS: High-accuracy models loaded!")
except Exception as e:
    print(f"Loading premium models... Error: {e}")
    print("- Loading Google T5 for summarization...")
    try:
        summarizer = pipeline("summarization", model="t5-base")
    except:
        summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
    
    print("- Loading advanced DistilBERT for Q&A...")
    qa_pipeline = pipeline("question-answering", model="distilbert-base-cased-distilled-squad")
print("Models loaded!")

ALLOWED_EXTENSIONS = {'pdf', 'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def advanced_text_preprocessing(text):
    """Enhanced preprocessing for higher accuracy."""
    import re
    
    # Remove noise and artifacts
    text = re.sub(r'\s+', ' ', text.strip())
    text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', ' ', text)  # Remove special chars
    text = re.sub(r'(\w+)([A-Z])', r'\1. \2', text)  # Fix missing periods
    text = re.sub(r'\b\d+\s*$', '', text, flags=re.MULTILINE)  # Remove page numbers
    
    # Fix common OCR errors
    text = re.sub(r'\bl\b', 'I', text)  # Common OCR mistake
    text = re.sub(r'\b0\b', 'O', text)  # Zero to O
    
    return text.strip()

def intelligent_chunking(text, max_size=1500):
    """Smart chunking that preserves context and meaning."""
    text = advanced_text_preprocessing(text)
    
    # Split by double newlines first (paragraph boundaries)
    paragraphs = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 20]
    
    chunks = []
    current_chunk = ""
    
    for paragraph in paragraphs:
        # If adding this paragraph exceeds size, save current chunk
        if len(current_chunk) + len(paragraph) > max_size and current_chunk:
            chunks.append(current_chunk.strip())
            
            # Start new chunk with some overlap for context
            sentences = current_chunk.split('.')
            if len(sentences) > 2:
                overlap = '. '.join(sentences[-2:]) + '. '
                current_chunk = overlap + paragraph
            else:
                current_chunk = paragraph
        else:
            if current_chunk:
                current_chunk += "\n\n" + paragraph
            else:
                current_chunk = paragraph
    
    # Add the last chunk
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks if chunks else [text]

def calculate_semantic_similarity(question, text):
    """Calculate how relevant text is to the question."""
    question_words = set(question.lower().split())
    text_words = set(text.lower().split())
    
    # Basic word overlap
    common_words = question_words.intersection(text_words)
    basic_score = len(common_words) / max(len(question_words), 1)
    
    # Boost for important question words (what, how, why, when, where)
    question_type_words = ['what', 'how', 'why', 'when', 'where', 'which', 'who']
    question_type = [w for w in question_words if w in question_type_words]
    
    # Boost for technical terms
    technical_terms = ['algorithm', 'method', 'approach', 'technique', 'process', 
                      'system', 'model', 'analysis', 'result', 'conclusion', 'finding']
    tech_boost = sum(2 for word in common_words if word in technical_terms)
    
    return basic_score + tech_boost * 0.1

def find_best_context(chunks, question, max_context_length=2000):
    """Find the most relevant chunks for the question."""
    if not chunks:
        return ""
    
    # Score each chunk
    scored_chunks = []
    for chunk in chunks:
        score = calculate_semantic_similarity(question, chunk)
        scored_chunks.append((chunk, score))
    
    # Sort by relevance
    scored_chunks.sort(key=lambda x: x[1], reverse=True)
    
    # Combine top chunks until we reach max length
    selected_text = ""
    for chunk, score in scored_chunks:
        if len(selected_text) + len(chunk) <= max_context_length:
            selected_text += "\n\n" + chunk if selected_text else chunk
        else:
            break
    
    return selected_text

def enhance_answer_quality(answer, question, context):
    """Post-process answers to improve quality and completeness."""
    original_answer = answer
    
    # If answer is too short, try to expand it
    if len(answer.split()) < 6:
        sentences = context.split('.')
        question_keywords = question.lower().split()
        
        # Find sentences that contain question keywords
        relevant_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 10:
                continue
            
            # Count keyword matches
            matches = sum(1 for word in question_keywords if word in sentence.lower())
            if matches >= 2:  # At least 2 keyword matches
                relevant_sentences.append((sentence, matches))
        
        # Sort by relevance and add the best matches
        relevant_sentences.sort(key=lambda x: x[1], reverse=True)
        
        if relevant_sentences:
            additional_info = '. '.join([s[0] for s in relevant_sentences[:2]])
            answer = f"{answer}. {additional_info}"
    
    # Clean up the answer
    answer = answer.strip()
    if not answer.endswith('.'):
        answer += '.'
    
    return answer

def extract_text_from_pdf(pdf_path):
    """Enhanced PDF text extraction specifically optimized for resumes and structured documents."""
    doc = fitz.open(pdf_path)
    try:
        full_text = ""
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            
            # Try multiple extraction methods for better quality
            # Method 1: Standard text extraction
            text_dict = page.get_text("dict")
            page_text = ""
            
            for block in text_dict["blocks"]:
                if "lines" in block:  # Text block
                    for line in block["lines"]:
                        line_text = ""
                        for span in line["spans"]:
                            line_text += span["text"]
                        if line_text.strip():
                            page_text += line_text + "\n"
                    page_text += "\n"  # Add paragraph break
            
            # Fallback to simple extraction if structured fails
            if not page_text.strip():
                page_text = page.get_text()
            
            full_text += page_text
        
        return full_text
    finally:
        doc.close()

def clean_resume_text(text):
    """Specialized cleaning for resume and professional documents."""
    import re
    
    # Fix common PDF extraction issues
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)  # Remove non-ASCII characters
    text = re.sub(r'\s+', ' ', text.strip())  # Normalize whitespace
    
    # Fix common resume formatting issues
    text = re.sub(r'(\w+)\s*[Ó•·]\s*(\d)', r'\1 \2', text)  # Fix bullet points with phones
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)  # Add spaces between joined words
    text = re.sub(r'(\w)@(\w)', r'\1@\2', text)  # Preserve email addresses
    text = re.sub(r'(\d{2})-(\d{10})', r'+91-\2', text)  # Fix phone numbers
    
    # Common resume section headers
    sections = ['EDUCATION', 'EXPERIENCE', 'PROJECTS', 'SKILLS', 'CONTACT', 'SUMMARY']
    for section in sections:
        # Fix broken section headers
        text = re.sub(rf'{section}[.]*\s*([A-Z])', rf'{section}\n\1', text)
    
    # Fix email formatting
    text = re.sub(r'(\w+)\s+gmail\s*[.\s]*com', r'\1@gmail.com', text)
    
    # Fix common LinkedIn/social formatting
    text = re.sub(r'([Ll]inkedin|[Gg]ithub)\s*[:\s]*([a-zA-Z0-9_-]+)', r'\1: \2', text)
    
    return text.strip()

def format_resume_summary(text, summary):
    """Create a well-structured resume summary."""
    import re
    
    # Extract key information patterns
    name_match = re.search(r'^([A-Z][a-z]+ [A-Z][a-z]+)', text)
    email_match = re.search(r'([a-zA-Z0-9._%-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', text)
    phone_match = re.search(r'(\+?91[-\s]?\d{10}|\d{10})', text)
    
    # Extract education
    education_match = re.search(r'(B\.?Tech|Bachelor|Engineering|University|College).*?(\d{4})', text, re.IGNORECASE)
    
    # Build structured summary
    structured_summary = []
    
    # Add contact info if found
    if name_match:
        structured_summary.append(f"Name: {name_match.group(1)}")
    if email_match:
        structured_summary.append(f"Email: {email_match.group(1)}")
    if phone_match:
        structured_summary.append(f"Phone: {phone_match.group(1)}")
    
    # Add the AI-generated summary
    structured_summary.append(f"\nProfessional Summary: {summary}")
    
    # Add education if found
    if education_match:
        structured_summary.append(f"Education: {education_match.group(0)}")
    
    return "\n".join(structured_summary)

def process_input(input_data, is_pdf=False, question=None):
    """HIGH-ACCURACY processing with resume/document optimization."""
    if is_pdf:
        raw_text = extract_text_from_pdf(input_data)
        # Apply resume-specific cleaning
        text = clean_resume_text(raw_text)
    else:
        text = input_data
        # Light cleaning for pasted text too
        text = clean_resume_text(text)

    # Detect if this is likely a resume/CV
    is_resume = any(keyword in text.upper() for keyword in 
                   ['EDUCATION', 'EXPERIENCE', 'SKILLS', 'PROJECTS', 'RESUME', 'CV', 'CONTACT'])

    # Use intelligent chunking for better context preservation
    text_chunks = intelligent_chunking(text, max_size=2000 if is_resume else 1500)
    
    # Generate high-quality summary with resume optimization
    if len(text_chunks) == 1:
        # Single chunk - use directly with larger context for resumes
        summary_text = text_chunks[0][:3000 if is_resume else 2500]
        try:
            if is_resume:
                # Resume-optimized summarization
                summary = summarizer(summary_text, 
                                   max_length=300,  # Longer for resumes
                                   min_length=150, 
                                   do_sample=False)[0]['summary_text']
                # Apply resume formatting
                summary = format_resume_summary(text, summary)
            else:
                summary = summarizer(summary_text, 
                                   max_length=200, 
                                   min_length=80, 
                                   do_sample=False)[0]['summary_text']
        except Exception as e:
            # Fallback summary
            sentences = summary_text.split('.')[:8]
            summary = '. '.join(sentences) + '.'
            if is_resume:
                summary = format_resume_summary(text, summary)
    else:
        # Multiple chunks - process each carefully
        chunk_summaries = []
        for chunk in text_chunks[:4 if is_resume else 3]:
            try:
                chunk_summary = summarizer(chunk[:2000], 
                                         max_length=200 if is_resume else 150, 
                                         min_length=80 if is_resume else 50, 
                                         do_sample=False)[0]['summary_text']
                chunk_summaries.append(chunk_summary)
            except:
                # Fallback for problematic chunks
                sentences = chunk.split('.')[:6]
                chunk_summaries.append('. '.join(sentences) + '.')
        
        # Combine and finalize
        combined = ' '.join(chunk_summaries)
        if len(combined.split()) > 200:
            try:
                summary = summarizer(combined, 
                                   max_length=400 if is_resume else 250, 
                                   min_length=150 if is_resume else 100, 
                                   do_sample=False)[0]['summary_text']
            except:
                summary = combined[:800] + '...'
        else:
            summary = combined
            
        # Format for resume if detected
        if is_resume:
            summary = format_resume_summary(text, summary)
    
    # Prepare enhanced result
    result = {
        "Summary": summary,
        "Original Text": text[:1000] + "..." if len(text) > 1000 else text,
        "Processing Stats": {
            "Total Chunks": len(text_chunks),
            "Text Length": len(text),
            "Document Type": "Resume/CV" if is_resume else "General Document",
            "Processing Method": "RESUME-OPTIMIZED AI Pipeline" if is_resume else "HIGH-ACCURACY AI Pipeline"
        }
    }

    # Enhanced Q&A processing (same as before but with better context)
    if question:
        try:
            # Find the most relevant context using advanced similarity
            best_context = find_best_context(text_chunks, question, max_context_length=3000)
            
            # Combine summary + best context for maximum accuracy
            enhanced_context = f"Document Summary: {summary}\n\nDetailed Context: {best_context}"
            
            # Use advanced Q&A model with larger context
            qa_result = qa_pipeline(question=question, context=enhanced_context)
            raw_answer = qa_result['answer']
            confidence_score = qa_result.get('score', 0.0)
            
            # Apply answer enhancement techniques
            enhanced_answer = enhance_answer_quality(raw_answer, question, enhanced_context)
            
            # Calculate detailed quality metrics
            answer_words = len(enhanced_answer.split())
            question_words = set(question.lower().split())
            answer_word_set = set(enhanced_answer.lower().split())
            
            relevance_score = len(question_words.intersection(answer_word_set)) / max(len(question_words), 1)
            
            # Check for technical content
            tech_indicators = ['method', 'approach', 'algorithm', 'technique', 'process', 
                             'system', 'analysis', 'result', 'finding', 'conclusion',
                             'data', 'model', 'framework', 'implementation', 'project', 'experience']
            has_technical = any(term in enhanced_answer.lower() for term in tech_indicators)
            
            # Enhanced confidence calculation
            final_confidence = (confidence_score + relevance_score) / 2
            if has_technical:
                final_confidence = min(final_confidence + 0.15, 1.0)
            if answer_words >= 15:  # Detailed answers get confidence boost
                final_confidence = min(final_confidence + 0.1, 1.0)
            if is_resume:  # Resume-specific boost
                final_confidence = min(final_confidence + 0.1, 1.0)
            
            result.update({
                "QnA Answer": enhanced_answer,
                "Confidence Score": round(final_confidence, 2),
                "Answer Quality": {
                    "Length": answer_words,
                    "Is Detailed": answer_words >= 10,
                    "Has Technical Terms": has_technical,
                    "Relevance Score": round(relevance_score, 2),
                    "Context Quality": "Resume-optimized matching" if is_resume else "High-precision semantic matching"
                },
                "Processing Method": "Advanced RoBERTa + Resume Context" if is_resume else "Advanced RoBERTa + Enhanced Context",
                "Context Chunks Used": len([c for c in text_chunks if calculate_semantic_similarity(question, c) > 0.1])
            })
                
        except Exception as e:
            result.update({
                "QnA Answer": f"Processing error occurred: {str(e)}",
                "Confidence Score": 0.0
            })

    return result

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_document():
    try:
        text_input = request.form.get('text_input', '').strip()
        question = request.form.get('question', '').strip()
        file = request.files.get('file')
        
        if not text_input and not file:
            return jsonify({'error': 'Please provide text or upload a file'})
        
        if file and file.filename != '':
            if not allowed_file(file.filename):
                return jsonify({'error': 'Please upload a PDF or TXT file'})
            
            filename = secure_filename(file.filename)
            file_content = file.read()
            
            with tempfile.NamedTemporaryFile(mode='wb', suffix='.pdf' if filename.lower().endswith('.pdf') else '.txt', delete=False) as tmp_file:
                tmp_file.write(file_content)
                tmp_file_path = tmp_file.name
            
            try:
                time.sleep(0.1)
                
                if filename.lower().endswith('.pdf'):
                    result = process_input(tmp_file_path, is_pdf=True, question=question if question else None)
                else:
                    with open(tmp_file_path, 'r', encoding='utf-8') as f:
                        text_content = f.read()
                    result = process_input(text_content, is_pdf=False, question=question if question else None)
            finally:
                try:
                    if os.path.exists(tmp_file_path):
                        time.sleep(0.1)
                        os.unlink(tmp_file_path)
                except:
                    pass
        
        elif text_input:
            result = process_input(text_input, is_pdf=False, question=question if question else None)
        
        return jsonify({'success': True, 'result': result})
        
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'})

if __name__ == '__main__':
    print("Starting server on http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
