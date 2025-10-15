import os
from flask import Flask, render_template, request, jsonify
import fitz
from transformers import pipeline
from werkzeug.utils import secure_filename
import tempfile
import time
import re

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

print("Loading HIGH-ACCURACY AI models...")

try:
    print("- Loading advanced BART-Large for summarization...")
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn", 
                         device=-1)  # Force CPU for deployment
    
    print("- Loading RoBERTa-Large for Q&A (much more accurate)...")
    qa_pipeline = pipeline("question-answering", model="deepset/roberta-large-squad2",
                          device=-1)  # Force CPU for deployment
    
    print("SUCCESS: High-accuracy models loaded!")
except Exception as e:
    print(f"Using fallback models due to: {e}")
    summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
    qa_pipeline = pipeline("question-answering", model="distilbert-base-cased-distilled-squad")

print("Models loaded!")

ALLOWED_EXTENSIONS = {'pdf', 'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def safe_delete_file(file_path, max_retries=3, delay=0.1):
    for attempt in range(max_retries):
        try:
            if os.path.exists(file_path):
                time.sleep(delay)
                os.unlink(file_path)
                return True
        except (OSError, PermissionError) as e:
            if attempt < max_retries - 1:
                time.sleep(delay * (attempt + 1))
                continue
            else:
                print(f"Warning: Could not delete temporary file after {max_retries} attempts: {e}")
                return False
    return True

def advanced_text_preprocessing(text):
    text = re.sub(r'\s+', ' ', text.strip())
    text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', ' ', text)
    text = re.sub(r'(\w+)([A-Z])', r'\1. \2', text)
    text = re.sub(r'\b\d+\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'\bl\b', 'I', text)
    text = re.sub(r'\b0\b', 'O', text)
    return text.strip()

def intelligent_chunking(text, max_size=1500):
    text = advanced_text_preprocessing(text)
    paragraphs = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 20]
    
    chunks = []
    current_chunk = ""
    
    for paragraph in paragraphs:
        if len(current_chunk) + len(paragraph) > max_size and current_chunk:
            chunks.append(current_chunk.strip())
            
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
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks if chunks else [text]

def calculate_semantic_similarity(question, text):
    question_words = set(question.lower().split())
    text_words = set(text.lower().split())
    
    common_words = question_words.intersection(text_words)
    basic_score = len(common_words) / max(len(question_words), 1)
    
    technical_terms = ['algorithm', 'method', 'approach', 'technique', 'process', 
                      'system', 'model', 'analysis', 'result', 'conclusion', 'finding']
    tech_boost = sum(2 for word in common_words if word in technical_terms)
    
    return basic_score + tech_boost * 0.1

def find_best_context(chunks, question, max_context_length=2000):
    if not chunks:
        return ""
    
    scored_chunks = []
    for chunk in chunks:
        score = calculate_semantic_similarity(question, chunk)
        scored_chunks.append((chunk, score))
    
    scored_chunks.sort(key=lambda x: x[1], reverse=True)
    
    selected_text = ""
    for chunk, score in scored_chunks:
        if len(selected_text) + len(chunk) <= max_context_length:
            selected_text += "\n\n" + chunk if selected_text else chunk
        else:
            break
    
    return selected_text

def enhance_answer_quality(answer, question, context):
    original_answer = answer
    
    if len(answer.split()) < 6:
        sentences = context.split('.')
        question_keywords = question.lower().split()
        
        relevant_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 10:
                continue
            
            matches = sum(1 for word in question_keywords if word in sentence.lower())
            if matches >= 2:
                relevant_sentences.append((sentence, matches))
        
        relevant_sentences.sort(key=lambda x: x[1], reverse=True)
        
        if relevant_sentences:
            additional_info = '. '.join([s[0] for s in relevant_sentences[:2]])
            answer = f"{answer}. {additional_info}"
    
    answer = answer.strip()
    if not answer.endswith('.'):
        answer += '.'
    
    return answer

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    try:
        full_text = ""
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            
            text_dict = page.get_text("dict")
            page_text = ""
            
            for block in text_dict["blocks"]:
                if "lines" in block:
                    for line in block["lines"]:
                        line_text = ""
                        for span in line["spans"]:
                            line_text += span["text"]
                        if line_text.strip():
                            page_text += line_text + "\n"
                    page_text += "\n"
            
            if not page_text.strip():
                page_text = page.get_text()
            
            full_text += page_text
        
        return full_text
    finally:
        doc.close()

def clean_resume_text(text):
    import re
    
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    text = re.sub(r'\s+', ' ', text.strip())
    
    text = re.sub(r'(\w+)\s*[Ó•·]\s*(\d)', r'\1 \2', text)
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    text = re.sub(r'(\w)@(\w)', r'\1@\2', text)
    text = re.sub(r'(\d{2})-(\d{10})', r'+91-\2', text)
    
    sections = ['EDUCATION', 'EXPERIENCE', 'PROJECTS', 'SKILLS', 'CONTACT', 'SUMMARY']
    for section in sections:
        text = re.sub(rf'{section}[.]*\s*([A-Z])', rf'{section}\n\1', text)
    
    text = re.sub(r'(\w+)\s+gmail\s*[.\s]*com', r'\1@gmail.com', text)
    text = re.sub(r'([Ll]inkedin|[Gg]ithub)\s*[:\s]*([a-zA-Z0-9_-]+)', r'\1: \2', text)
    
    return text.strip()

def format_resume_summary(text, summary):
    import re
    
    name_match = re.search(r'^([A-Z][a-z]+ [A-Z][a-z]+)', text)
    email_match = re.search(r'([a-zA-Z0-9._%-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', text)
    phone_match = re.search(r'(\+?91[-\s]?\d{10}|\d{10})', text)
    
    education_match = re.search(r'(B\.?Tech|Bachelor|Engineering|University|College).*?(\d{4})', text, re.IGNORECASE)
    
    structured_summary = []
    
    if name_match:
        structured_summary.append(f"Name: {name_match.group(1)}")
    if email_match:
        structured_summary.append(f"Email: {email_match.group(1)}")
    if phone_match:
        structured_summary.append(f"Phone: {phone_match.group(1)}")
    
    structured_summary.append(f"\nProfessional Summary: {summary}")
    
    if education_match:
        structured_summary.append(f"Education: {education_match.group(0)}")
    
    return "\n".join(structured_summary)

def process_input(input_data, is_pdf=False, question=None):
    if is_pdf:
        raw_text = extract_text_from_pdf(input_data)
        text = clean_resume_text(raw_text)
    else:
        text = input_data
        text = clean_resume_text(text)

    is_resume = any(keyword in text.upper() for keyword in 
                   ['EDUCATION', 'EXPERIENCE', 'SKILLS', 'PROJECTS', 'RESUME', 'CV', 'CONTACT'])

    text_chunks = intelligent_chunking(text, max_size=2000 if is_resume else 1500)
    
    if len(text_chunks) == 1:
        summary_text = text_chunks[0][:3000 if is_resume else 2500]
        try:
            if is_resume:
                summary = summarizer(summary_text, 
                                   max_length=300, min_length=150, 
                                   do_sample=False)[0]['summary_text']
                summary = format_resume_summary(text, summary)
            else:
                summary = summarizer(summary_text, 
                                   max_length=200, min_length=80, 
                                   do_sample=False)[0]['summary_text']
        except Exception as e:
            sentences = summary_text.split('.')[:8]
            summary = '. '.join(sentences) + '.'
            if is_resume:
                summary = format_resume_summary(text, summary)
    else:
        chunk_summaries = []
        for chunk in text_chunks[:4 if is_resume else 3]:
            try:
                chunk_summary = summarizer(chunk[:2000], 
                                         max_length=200 if is_resume else 150, 
                                         min_length=80 if is_resume else 50, 
                                         do_sample=False)[0]['summary_text']
                chunk_summaries.append(chunk_summary)
            except:
                sentences = chunk.split('.')[:6]
                chunk_summaries.append('. '.join(sentences) + '.')
        
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
            
        if is_resume:
            summary = format_resume_summary(text, summary)
    
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

    if question:
        try:
            best_context = find_best_context(text_chunks, question, max_context_length=3000)
            enhanced_context = f"Document Summary: {summary}\n\nDetailed Context: {best_context}"
            
            qa_result = qa_pipeline(question=question, context=enhanced_context)
            raw_answer = qa_result['answer']
            confidence_score = qa_result.get('score', 0.0)
            
            enhanced_answer = enhance_answer_quality(raw_answer, question, enhanced_context)
            
            answer_words = len(enhanced_answer.split())
            question_words = set(question.lower().split())
            answer_word_set = set(enhanced_answer.lower().split())
            
            relevance_score = len(question_words.intersection(answer_word_set)) / max(len(question_words), 1)
            
            tech_indicators = ['method', 'approach', 'algorithm', 'technique', 'process', 
                             'system', 'analysis', 'result', 'finding', 'conclusion',
                             'data', 'model', 'framework', 'implementation', 'project', 'experience']
            has_technical = any(term in enhanced_answer.lower() for term in tech_indicators)
            
            final_confidence = (confidence_score + relevance_score) / 2
            if has_technical:
                final_confidence = min(final_confidence + 0.15, 1.0)
            if answer_words >= 15:
                final_confidence = min(final_confidence + 0.1, 1.0)
            if is_resume:
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
            return jsonify({'error': 'Please provide either text or upload a file'})
        
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
                    
                time.sleep(0.2)
                
            finally:
                safe_delete_file(tmp_file_path)
        
        elif text_input:
            result = process_input(text_input, is_pdf=False, question=question if question else None)
        
        return jsonify({'success': True, 'result': result})
        
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
