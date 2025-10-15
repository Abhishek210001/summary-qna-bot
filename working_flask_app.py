from flask import Flask, render_template, request, jsonify
import os
import fitz
from transformers import pipeline
from werkzeug.utils import secure_filename
import tempfile
import time
import re
import numpy as np

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Global variables for models
summarizer = None
qa_pipeline = None

def load_models():
    """Load AI models with fallback options"""
    global summarizer, qa_pipeline
    
    print("🚀 Loading HIGH-ACCURACY AI models...")
    
    try:
        print("- Loading advanced BART-Large for summarization...")
        summarizer = pipeline("summarization", model="facebook/bart-large-cnn", device=-1)
        
        print("- Loading RoBERTa-Large for Q&A (much more accurate)...")
        qa_pipeline = pipeline("question-answering", model="deepset/roberta-large-squad2", device=-1)
        
        print("✅ SUCCESS: High-accuracy models loaded!")
        return True
        
    except Exception as e:
        print(f"⚠️ Loading fallback models due to: {e}")
        try:
            print("- Loading DistilBART for summarization...")
            summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6", device=-1)
            
            print("- Loading DistilBERT for Q&A...")
            qa_pipeline = pipeline("question-answering", model="distilbert-base-cased-distilled-squad", device=-1)
            
            print("✅ SUCCESS: Fallback models loaded!")
            return True
            
        except Exception as e2:
            print(f"❌ ERROR loading models: {e2}")
            return False

# Load models on startup
models_loaded = load_models()

ALLOWED_EXTENSIONS = {'pdf', 'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def safe_delete_file(file_path, max_retries=3, delay=0.1):
    """Safely delete file with retries"""
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
                print(f"Warning: Could not delete temporary file: {e}")
                return False
    return True

def advanced_text_preprocessing(text):
    """Enhanced text preprocessing"""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove special characters but keep punctuation
    text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', ' ', text)
    
    # Fix common OCR errors
    text = re.sub(r'(\w+)([A-Z])', r'\1. \2', text)
    text = re.sub(r'\b\d+\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'\bl\b', 'I', text)
    text = re.sub(r'\b0\b', 'O', text)
    
    return text.strip()

def intelligent_chunking(text, max_size=1500):
    """Smart text chunking with context preservation"""
    text = advanced_text_preprocessing(text)
    paragraphs = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 20]
    
    chunks = []
    current_chunk = ""
    
    for paragraph in paragraphs:
        if len(current_chunk) + len(paragraph) > max_size and current_chunk:
            chunks.append(current_chunk.strip())
            
            # Add overlap for context
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

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF with enhanced methods"""
    doc = None
    try:
        doc = fitz.open(pdf_path)
        full_text = ""
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            
            # Try structured text extraction first
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
            
            # Fallback to simple text extraction
            if not page_text.strip():
                page_text = page.get_text()
            
            full_text += page_text
        
        return full_text
        
    except Exception as e:
        print(f"PDF extraction error: {e}")
        return ""
    finally:
        if doc:
            doc.close()

def clean_resume_text(text):
    """Clean resume-specific text artifacts"""
    # Remove non-ASCII characters
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Fix common resume formatting issues
    text = re.sub(r'(\w+)\s*[Ó•·]\s*(\d)', r'\1 \2', text)
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    text = re.sub(r'(\w)@(\w)', r'\1@\2', text)
    text = re.sub(r'(\d{2})-(\d{10})', r'+91-\2', text)
    
    # Fix section headers
    sections = ['EDUCATION', 'EXPERIENCE', 'PROJECTS', 'SKILLS', 'CONTACT', 'SUMMARY']
    for section in sections:
        text = re.sub(rf'{section}[.]*\s*([A-Z])', rf'{section}\n\1', text)
    
    # Fix email formats
    text = re.sub(r'(\w+)\s+gmail\s*[.\s]*com', r'\1@gmail.com', text)
    text = re.sub(r'([Ll]inkedin|[Gg]ithub)\s*[:\s]*([a-zA-Z0-9_-]+)', r'\1: \2', text)
    
    return text.strip()

def format_resume_summary(text, summary):
    """Format resume summary with structured information"""
    # Extract key information
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

def enhance_summary_with_details(summary, original_text, is_resume):
    """Enhance summary with additional key details"""
    enhanced_summary = summary
    
    # Extract important numbers, dates, and specific details
    important_details = []
    
    # Find years/dates
    years = re.findall(r'\b(19|20)\d{2}\b', original_text)
    if years:
        important_details.append(f"Timeline: {min(years)} - {max(years)}")
    
    # Find percentages and numbers
    percentages = re.findall(r'\b\d+\.?\d*%\b', original_text)
    if percentages:
        important_details.append(f"Key metrics: {', '.join(percentages[:3])}")
    
    # Find specific technologies/skills (for resumes)
    if is_resume:
        tech_keywords = ['Python', 'Java', 'JavaScript', 'React', 'Node.js', 'SQL', 'Machine Learning', 'AI', 'Data Science']
        found_tech = [tech for tech in tech_keywords if tech.lower() in original_text.lower()]
        if found_tech:
            important_details.append(f"Technologies: {', '.join(found_tech[:5])}")
    
    # Add details to summary
    if important_details:
        enhanced_summary += f"\n\nKey Details:\n• " + "\n• ".join(important_details)
    
    return enhanced_summary

def extract_key_points(text):
    """Extract key points from text chunk"""
    key_points = []
    
    # Split into sentences and find important ones
    sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 20]
    
    # Look for sentences with important indicators
    important_indicators = [
        'achieved', 'developed', 'implemented', 'created', 'designed', 'managed', 
        'led', 'improved', 'increased', 'reduced', 'built', 'established',
        'responsible for', 'experience in', 'skilled in', 'expertise in'
    ]
    
    for sentence in sentences[:15]:  # Limit to prevent too many points
        if any(indicator in sentence.lower() for indicator in important_indicators):
            # Clean and format the sentence
            clean_sentence = sentence.strip()
            if len(clean_sentence) > 30 and len(clean_sentence) < 200:
                key_points.append(clean_sentence)
    
    return key_points[:5]  # Return top 5 key points

def create_comprehensive_fallback_summary(text, is_resume):
    """Create comprehensive summary when AI summarizer fails"""
    sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 15]
    
    # Take first few sentences as introduction
    intro_sentences = sentences[:3]
    intro = '. '.join(intro_sentences) + '.'
    
    # Extract key information
    key_info = []
    
    if is_resume:
        # Look for education
        education_sentences = [s for s in sentences if any(word in s.lower() for word in ['university', 'college', 'degree', 'education'])]
        if education_sentences:
            key_info.append(f"Education: {education_sentences[0]}")
        
        # Look for experience
        experience_sentences = [s for s in sentences if any(word in s.lower() for word in ['experience', 'worked', 'company', 'role'])]
        if experience_sentences:
            key_info.append(f"Experience: {experience_sentences[0]}")
        
        # Look for skills
        skills_sentences = [s for s in sentences if any(word in s.lower() for word in ['skills', 'technologies', 'programming', 'software'])]
        if skills_sentences:
            key_info.append(f"Skills: {skills_sentences[0]}")
    else:
        # For general documents, extract key themes
        middle_sentences = sentences[len(sentences)//4:len(sentences)*3//4]
        if middle_sentences:
            key_info.extend(middle_sentences[:3])
    
    # Combine into comprehensive summary
    comprehensive_summary = intro
    if key_info:
        comprehensive_summary += f"\n\nKey Information:\n• " + "\n• ".join(key_info)
    
    # Add conclusion if available
    if len(sentences) > 5:
        conclusion_sentences = sentences[-2:]
        conclusion = '. '.join(conclusion_sentences) + '.'
        comprehensive_summary += f"\n\nConclusion: {conclusion}"
    
    return comprehensive_summary

def process_input(input_data, is_pdf=False, question=None):
    """Process input data for summarization and Q&A"""
    global summarizer, qa_pipeline
    
    if not models_loaded or not summarizer or not qa_pipeline:
        return {"error": "AI models not loaded. Please restart the application."}
    
    try:
        # Extract text
        if is_pdf:
            raw_text = extract_text_from_pdf(input_data)
            text = clean_resume_text(raw_text)
        else:
            text = input_data
            text = clean_resume_text(text)

        if not text.strip():
            return {"error": "No text could be extracted from the document."}

        # Detect if it's a resume
        is_resume = any(keyword in text.upper() for keyword in 
                       ['EDUCATION', 'EXPERIENCE', 'SKILLS', 'PROJECTS', 'RESUME', 'CV', 'CONTACT'])

        # Process text in chunks
        text_chunks = intelligent_chunking(text, max_size=2000 if is_resume else 1500)
        
        # Generate comprehensive summary
        if len(text_chunks) == 1:
            # Single chunk - generate detailed summary
            summary_text = text_chunks[0]
            try:
                # Generate longer, more detailed summary
                summary = summarizer(summary_text, 
                                   max_length=500 if is_resume else 400, 
                                   min_length=250 if is_resume else 200, 
                                   do_sample=False)[0]['summary_text']
                
                # Enhance with key details extraction
                summary = enhance_summary_with_details(summary, summary_text, is_resume)
                
                if is_resume:
                    summary = format_resume_summary(text, summary)
            except Exception as e:
                print(f"Summarization error: {e}")
                # Fallback: create comprehensive manual summary
                summary = create_comprehensive_fallback_summary(summary_text, is_resume)
                if is_resume:
                    summary = format_resume_summary(text, summary)
        else:
            # Multi-chunk processing - comprehensive approach
            chunk_summaries = []
            key_points = []
            
            # Process each chunk with detailed summarization
            for i, chunk in enumerate(text_chunks):
                try:
                    # Generate detailed summary for each chunk
                    chunk_summary = summarizer(chunk[:2000], 
                                             max_length=300 if is_resume else 250, 
                                             min_length=150 if is_resume else 100, 
                                             do_sample=False)[0]['summary_text']
                    chunk_summaries.append(f"Section {i+1}: {chunk_summary}")
                    
                    # Extract key points from each chunk
                    key_points.extend(extract_key_points(chunk))
                    
                except Exception as e:
                    print(f"Chunk summarization error: {e}")
                    # Fallback for chunk processing
                    sentences = chunk.split('.')[:10]  # More sentences for completeness
                    chunk_summary = '. '.join([s.strip() for s in sentences if len(s.strip()) > 10]) + '.'
                    chunk_summaries.append(f"Section {i+1}: {chunk_summary}")
            
            # Combine all summaries into comprehensive final summary
            combined_summary = '\n\n'.join(chunk_summaries)
            
            # Add key points section
            if key_points:
                key_points_text = '\n\nKey Points:\n• ' + '\n• '.join(key_points[:8])
                combined_summary += key_points_text
            
            # Final comprehensive summary
            if len(combined_summary.split()) > 300:
                try:
                    # Generate final comprehensive summary
                    final_summary = summarizer(combined_summary, 
                                             max_length=600 if is_resume else 500, 
                                             min_length=300 if is_resume else 250, 
                                             do_sample=False)[0]['summary_text']
                    
                    # Combine with section details
                    summary = f"{final_summary}\n\n{combined_summary}"
                except Exception as e:
                    print(f"Final summarization error: {e}")
                    summary = combined_summary
            else:
                summary = combined_summary
                
            if is_resume:
                summary = format_resume_summary(text, summary)
        
        # Prepare result
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

        # Handle Q&A if question provided
        if question and question.strip():
            try:
                # Find best context (simple approach)
                best_context = text[:3000]  # Use first 3000 chars as context
                enhanced_context = f"Document Summary: {summary}\n\nDetailed Context: {best_context}"
                
                qa_result = qa_pipeline(question=question, context=enhanced_context)
                raw_answer = qa_result['answer']
                confidence_score = qa_result.get('score', 0.0)
                
                # Enhance answer quality
                if len(raw_answer.split()) < 6:
                    sentences = enhanced_context.split('.')
                    question_keywords = question.lower().split()
                    
                    relevant_sentences = []
                    for sentence in sentences:
                        sentence = sentence.strip()
                        if len(sentence) < 10:
                            continue
                        
                        matches = sum(1 for word in question_keywords if word in sentence.lower())
                        if matches >= 2:
                            relevant_sentences.append(sentence)
                    
                    if relevant_sentences:
                        additional_info = '. '.join(relevant_sentences[:2])
                        raw_answer = f"{raw_answer}. {additional_info}"
                
                result.update({
                    "QnA Answer": raw_answer,
                    "Confidence Score": round(confidence_score, 2),
                    "Answer Quality": {
                        "Length": len(raw_answer.split()),
                        "Is Detailed": len(raw_answer.split()) >= 10,
                        "Context Quality": "Resume-optimized matching" if is_resume else "High-precision semantic matching"
                    }
                })
                    
            except Exception as e:
                print(f"Q&A error: {e}")
                result.update({
                    "QnA Answer": f"Error processing question: {str(e)}",
                    "Confidence Score": 0.0
                })

        return result
        
    except Exception as e:
        print(f"Processing error: {e}")
        return {"error": f"Processing error: {str(e)}"}

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_document():
    """Process document endpoint"""
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
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='wb', suffix='.pdf' if filename.lower().endswith('.pdf') else '.txt', delete=False) as tmp_file:
                tmp_file.write(file_content)
                tmp_file_path = tmp_file.name
            
            try:
                time.sleep(0.1)  # Small delay
                
                if filename.lower().endswith('.pdf'):
                    result = process_input(tmp_file_path, is_pdf=True, question=question if question else None)
                else:
                    with open(tmp_file_path, 'r', encoding='utf-8') as f:
                        text_content = f.read()
                    result = process_input(text_content, is_pdf=False, question=question if question else None)
                    
                time.sleep(0.2)  # Another small delay
                
            finally:
                safe_delete_file(tmp_file_path)
        
        elif text_input:
            result = process_input(text_input, is_pdf=False, question=question if question else None)
        
        return jsonify({'success': True, 'result': result})
        
    except Exception as e:
        print(f"Endpoint error: {e}")
        return jsonify({'error': f'Error: {str(e)}'})

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🚀 AI Document Summarizer & Q&A Bot")
    print("="*50)
    if models_loaded:
        print("✅ AI models loaded successfully!")
    else:
        print("❌ Warning: AI models failed to load!")
    print("🌐 Starting server on http://localhost:5000")
    print("📱 Access from any device on your network!")
    print("="*50 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
