import streamlit as st
import fitz  # PyMuPDF
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

def create_comprehensive_summary(text, is_resume=False):
    """Create comprehensive summary using advanced text processing"""
    sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 15]
    
    # Create detailed summary
    if len(sentences) <= 8:
        summary = '. '.join(sentences) + '.'
    else:
        # Take key sentences strategically
        key_sentences = []
        key_sentences.extend(sentences[:3])  # First 3 (introduction)
        
        # Middle section analysis
        mid_start = len(sentences) // 3
        mid_end = 2 * len(sentences) // 3
        middle_sentences = sentences[mid_start:mid_end]
        key_sentences.extend(middle_sentences[:3])  # Key middle content
        
        key_sentences.extend(sentences[-2:])  # Last 2 (conclusion)
        summary = '. '.join(key_sentences) + '.'
    
    # Add comprehensive analysis
    word_count = len(text.split())
    char_count = len(text)
    
    # Extract key information
    key_info = []
    
    # Find years/dates
    years = re.findall(r'\b(19|20)\d{2}\b', text)
    if years:
        key_info.append(f"📅 Timeline: {min(years)} - {max(years)}")
    
    # Find percentages and numbers
    percentages = re.findall(r'\b\d+\.?\d*%\b', text)
    if percentages:
        key_info.append(f"📊 Key metrics: {', '.join(percentages[:3])}")
    
    # Find technologies (for resumes/tech docs)
    tech_keywords = ['Python', 'Java', 'JavaScript', 'React', 'Node.js', 'SQL', 'Machine Learning', 'AI', 'Data Science', 'HTML', 'CSS']
    found_tech = [tech for tech in tech_keywords if tech.lower() in text.lower()]
    if found_tech:
        key_info.append(f"💻 Technologies: {', '.join(found_tech[:5])}")
    
    # Document statistics
    analysis = f"\n\n📈 **Document Analysis:**\n"
    analysis += f"• **Word Count:** {word_count:,} words\n"
    analysis += f"• **Character Count:** {char_count:,} characters\n"
    analysis += f"• **Estimated Reading Time:** {word_count // 200 + 1} minutes\n"
    analysis += f"• **Complexity Level:** {'High' if word_count > 1000 else 'Medium' if word_count > 500 else 'Low'}\n"
    
    if is_resume:
        # Resume-specific analysis
        analysis += f"\n🎯 **Resume Analysis:**\n"
        if 'email' in text.lower() or '@' in text:
            analysis += "• ✅ Contains contact information\n"
        if any(word in text.lower() for word in ['experience', 'work', 'job', 'company']):
            analysis += "• ✅ Contains work experience\n"
        if any(word in text.lower() for word in ['education', 'degree', 'university', 'college']):
            analysis += "• ✅ Contains educational background\n"
        if any(word in text.lower() for word in ['skill', 'technology', 'programming', 'software']):
            analysis += "• ✅ Contains technical skills\n"
        if any(word in text.lower() for word in ['project', 'developed', 'built', 'created']):
            analysis += "• ✅ Contains project experience\n"
    
    # Add key information
    if key_info:
        analysis += f"\n🔍 **Key Details:**\n• " + "\n• ".join(key_info)
    
    return summary + analysis

def smart_text_qa(question, text):
    """Advanced Q&A using intelligent text matching"""
    question_words = [word.lower() for word in question.split() if len(word) > 2]
    sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 10]
    
    # Score sentences based on relevance
    scored_sentences = []
    for sentence in sentences:
        sentence_lower = sentence.lower()
        
        # Calculate relevance score
        exact_matches = sum(2 for word in question_words if word in sentence_lower)
        partial_matches = sum(1 for word in question_words if any(word in w for w in sentence_lower.split()))
        
        total_score = exact_matches + partial_matches
        
        if total_score > 0:
            scored_sentences.append((sentence, total_score))
    
    if not scored_sentences:
        return "❌ I couldn't find specific information related to your question in the document. Try rephrasing your question or asking about different topics covered in the text."
    
    # Sort by relevance and create comprehensive answer
    scored_sentences.sort(key=lambda x: x[1], reverse=True)
    
    # Take top 3 most relevant sentences
    top_sentences = [s[0] for s in scored_sentences[:3]]
    
    answer = "🎯 **Based on document analysis:**\n\n"
    for i, sentence in enumerate(top_sentences, 1):
        answer += f"{i}. {sentence.strip()}\n\n"
    
    # Add confidence indicator
    max_score = scored_sentences[0][1]
    confidence = min(max_score * 10, 95)  # Scale to percentage
    
    answer += f"📊 **Confidence Level:** {confidence}% (keyword matching)\n"
    answer += f"🔍 **Matches Found:** {len(scored_sentences)} relevant sentences"
    
    return answer

def process_document(text, question=None):
    """Process document with comprehensive text analysis"""
    is_resume = any(keyword in text.upper() for keyword in 
                   ['EDUCATION', 'EXPERIENCE', 'SKILLS', 'PROJECTS', 'RESUME', 'CV'])
    
    if is_resume:
        text = clean_resume_text(text)
    
    # Create comprehensive summary
    summary = create_comprehensive_summary(text, is_resume)
    
    if is_resume:
        summary = format_resume_summary(text, summary)
    
    # Prepare result
    result = {
        "summary": summary,
        "chunks": len(intelligent_chunking(text)),
        "doc_type": "Resume/CV" if is_resume else "General Document"
    }
    
    # Handle Q&A if question provided
    if question and question.strip():
        answer = smart_text_qa(question, text)
        result["answer"] = answer
        result["confidence"] = 0.85  # High confidence for advanced text matching
    
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
        with st.spinner("🤖 Processing your document with advanced text analysis..."):
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
                st.subheader("📋 Comprehensive Summary")
                st.markdown(result["summary"])
                
                if "answer" in result:
                    st.subheader("❓ Q&A Answer")
                    st.markdown(result["answer"])
                
                # Stats
                with st.expander("📊 Processing Statistics"):
                    st.write(f"**Document Type:** {result['doc_type']}")
                    st.write(f"**Text Chunks:** {result['chunks']}")
                    st.write(f"**Text Length:** {len(document_text)} characters")
                    st.write(f"**Processing Method:** Advanced Text Analysis")
                
            except Exception as e:
                st.error(f"❌ Error processing document: {str(e)}")
    else:
        st.warning("⚠️ Please upload a PDF file or enter some text!")

# Footer
st.markdown("---")
st.markdown("### 🚀 Cloud-Optimized Text Processing")
st.markdown("• **Advanced Text Analysis** for comprehensive summaries")
st.markdown("• **Intelligent Q&A System** using smart keyword matching")
st.markdown("• **Resume-Optimized Processing** for structured documents")
st.markdown("• **Memory-Efficient** design for reliable cloud performance")

# Info about the processing
st.info("💡 **Note:** This version uses advanced text processing algorithms optimized for cloud deployment. For AI model-powered processing, use the local version at localhost:5000")
