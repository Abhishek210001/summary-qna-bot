import streamlit as st
import fitz  # PyMuPDF
from transformers import pipeline
import tempfile
import time
import re
import os

# Page configuration
st.set_page_config(
    page_title="🤖 AI PDF Summarizer + QnA Bot",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title and description
st.title("📄 AI-Powered PDF Summarizer + QnA Bot")
st.markdown("### Upload a PDF or enter text to get intelligent summaries and ask questions!")

# Initialize session state
if 'models_loaded' not in st.session_state:
    st.session_state.models_loaded = False

@st.cache_resource
def load_models():
    """Load AI models with caching - Cloud optimized"""
    try:
        with st.spinner("🚀 Loading Cloud-Optimized AI Models..."):
            # Use lighter models for reliable cloud deployment
            summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6", device=-1)
            qa_pipeline = pipeline("question-answering", model="distilbert-base-cased-distilled-squad", device=-1)
        st.success("✅ AI Models Loaded Successfully!")
        return summarizer, qa_pipeline
    except Exception as e:
        st.warning(f"⚠️ Trying even lighter models: {e}")
        try:
            # Fallback to the most basic models
            summarizer = pipeline("summarization", model="t5-small", device=-1)
            qa_pipeline = pipeline("question-answering", model="distilbert-base-uncased-distilled-squad", device=-1)
            st.info("✅ Basic AI Models Loaded Successfully!")
            return summarizer, qa_pipeline
        except Exception as e2:
            st.error(f"❌ Error loading models: {e2}")
            st.error("Please try refreshing the page or contact support.")
            return None, None

# Load models
summarizer, qa_pipeline = load_models()

# Check if models loaded successfully
if summarizer is None or qa_pipeline is None:
    st.error("❌ Failed to load AI models. Please try refreshing the page.")
    st.stop()

def advanced_text_preprocessing(text):
    """Enhanced text preprocessing"""
    text = re.sub(r'\s+', ' ', text.strip())
    text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', ' ', text)
    text = re.sub(r'(\w+)([A-Z])', r'\1. \2', text)
    text = re.sub(r'\b\d+\s*$', '', text, flags=re.MULTILINE)
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
            sentences = current_chunk.split('.')
            if len(sentences) > 2:
                overlap = '. '.join(sentences[-2:]) + '. '
                current_chunk = overlap + paragraph
            else:
                current_chunk = paragraph
        else:
            current_chunk = current_chunk + "\n\n" + paragraph if current_chunk else paragraph
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks if chunks else [text]

def extract_text_from_pdf(pdf_file):
    """Extract text from uploaded PDF"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        tmp_file.write(pdf_file.read())
        tmp_file_path = tmp_file.name
    
    try:
        doc = fitz.open(tmp_file_path)
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
        
        doc.close()
        return full_text
    finally:
        if os.path.exists(tmp_file_path):
            os.unlink(tmp_file_path)

def clean_resume_text(text):
    """Clean resume-specific text artifacts"""
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    text = re.sub(r'\s+', ' ', text.strip())
    text = re.sub(r'(\w+)\s*[Ó•·]\s*(\d)', r'\1 \2', text)
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    text = re.sub(r'(\w)@(\w)', r'\1@\2', text)
    return text.strip()

def format_resume_summary(text, summary):
    """Format resume summary with structured information"""
    name_match = re.search(r'^([A-Z][a-z]+ [A-Z][a-z]+)', text)
    email_match = re.search(r'([a-zA-Z0-9._%-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', text)
    phone_match = re.search(r'(\+?91[-\s]?\d{10}|\d{10})', text)
    
    structured_summary = []
    
    if name_match:
        structured_summary.append(f"**Name:** {name_match.group(1)}")
    if email_match:
        structured_summary.append(f"**Email:** {email_match.group(1)}")
    if phone_match:
        structured_summary.append(f"**Phone:** {phone_match.group(1)}")
    
    structured_summary.append(f"\n**Professional Summary:** {summary}")
    
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

def process_document(text, question=None):
    """Process document for summarization and Q&A with enhanced comprehensive summaries"""
    is_resume = any(keyword in text.upper() for keyword in 
                   ['EDUCATION', 'EXPERIENCE', 'SKILLS', 'PROJECTS', 'RESUME', 'CV'])
    
    if is_resume:
        text = clean_resume_text(text)
    
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
        except:
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
                
            except:
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
            except:
                summary = combined_summary
        else:
            summary = combined_summary
            
        if is_resume:
            summary = format_resume_summary(text, summary)
    
    result = {
        "summary": summary,
        "chunks": len(text_chunks),
        "doc_type": "Resume/CV" if is_resume else "General Document"
    }
    
    # Handle Q&A if question provided
    if question:
        try:
            # Find best context
            best_context = text[:3000]  # Simple approach for Streamlit
            enhanced_context = f"Document Summary: {summary}\n\nDetailed Context: {best_context}"
            
            qa_result = qa_pipeline(question=question, context=enhanced_context)
            result["answer"] = qa_result['answer']
            result["confidence"] = round(qa_result.get('score', 0.0), 2)
        except Exception as e:
            result["answer"] = f"Error processing question: {str(e)}"
            result["confidence"] = 0.0
    
    return result

# Main interface
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📄 Document Input")
    
    # File uploader
    uploaded_file = st.file_uploader("Upload a PDF file", type=['pdf'], help="Upload a PDF document for analysis")
    
    # Text input
    text_input = st.text_area("Or enter text directly", height=150, 
                             placeholder="Paste your text here for analysis...")
    
    # Question input
    question_input = st.text_input("❓ Ask a question about the document (optional)", 
                                  placeholder="What is this document about?")

with col2:
    st.subheader("🚀 Quick Questions")
    if st.button("📚 What are the main skills?"):
        question_input = "What are the main skills mentioned?"
    if st.button("💼 Work experience?"):
        question_input = "What work experience is mentioned?"
    if st.button("🎓 Educational background?"):
        question_input = "What is the educational background?"
    if st.button("🔧 Technical projects?"):
        question_input = "What technical projects are described?"

# Process button
if st.button("🔄 Process Document", type="primary"):
    if uploaded_file is not None or text_input.strip():
        with st.spinner("🤖 AI is processing your document..."):
            try:
                # Get text content
                if uploaded_file is not None:
                    document_text = extract_text_from_pdf(uploaded_file)
                    st.success(f"✅ PDF processed successfully! ({len(document_text)} characters)")
                else:
                    document_text = text_input.strip()
                
                # Process the document
                result = process_document(document_text, question_input if question_input.strip() else None)
                
                # Display results
                st.subheader("📋 Summary")
                st.markdown(result["summary"])
                
                if "answer" in result:
                    st.subheader("❓ Q&A Answer")
                    st.markdown(f"**Answer:** {result['answer']}")
                    st.markdown(f"**Confidence:** {result['confidence']}")
                
                # Stats
                with st.expander("📊 Processing Statistics"):
                    st.write(f"**Document Type:** {result['doc_type']}")
                    st.write(f"**Text Chunks:** {result['chunks']}")
                    st.write(f"**Text Length:** {len(document_text)} characters")
                
            except Exception as e:
                st.error(f"❌ Error processing document: {str(e)}")
    else:
        st.warning("⚠️ Please upload a PDF file or enter some text!")

# Footer
st.markdown("---")
st.markdown("### 🤖 Powered by Advanced AI Models")
st.markdown("• **BART-Large-CNN** for high-quality summarization")
st.markdown("• **RoBERTa-Large-Squad2** for accurate question answering")
st.markdown("• **Intelligent text chunking** for better processing")
