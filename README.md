# 🤖 AI-Powered PDF Summarizer + QnA Bot

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org/)
[![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)

> **An intelligent document processing application with dual deployment options: High-performance local Flask app and memory-optimized cloud Streamlit app.**

---

## 🌟 **Dual Deployment Architecture**

### 🏠 **Local Flask App (AI-Powered)**
- **AI Models**: BART-Large-CNN + RoBERTa-Large-Squad2 (with DistilBART/DistilBERT fallbacks)
- **High Accuracy**: Advanced AI summarization and Q&A
- **Access**: `http://localhost:5000`
- **Run**: `python working_flask_app.py`

### ☁️ **Cloud Streamlit App (Text Processing)**
- **Algorithm-Based**: Advanced text processing without AI models
- **Memory-Optimized**: Works within cloud memory limits
- **Global Access**: Deploy to Streamlit Cloud, Railway, Render
- **Run**: `streamlit run app.py`

---

## ✨ **Advanced Features**

### 📊 **Comprehensive Document Analysis**
```
📈 Document Analysis:
• Word Count: 1,247 words
• Character Count: 8,934 characters  
• Estimated Reading Time: 7 minutes
• Complexity Level: High

🎯 Resume Analysis:
• ✅ Contains contact information
• ✅ Contains work experience
• ✅ Contains educational background
• ✅ Contains technical skills
• ✅ Contains project experience

🔍 Key Details:
• 📅 Timeline: 2020 - 2024
• 📊 Key metrics: 95%, 40%, 85%
• 💻 Technologies: Python, JavaScript, React, SQL, Machine Learning
```

### 🎯 **Smart Q&A System**
```
🎯 Based on document analysis:

1. [Most relevant sentence matching your question]
2. [Second most relevant sentence]  
3. [Third most relevant sentence]

📊 Confidence Level: 87% (keyword matching)
🔍 Matches Found: 12 relevant sentences
```

### 🚀 **Actual Features Implemented**
- **📄 PDF Processing**: Text extraction using PyMuPDF (fitz)
- **📋 Resume Analysis**: Specialized text cleaning and structured formatting
- **🎯 Smart Chunking**: Intelligent text segmentation with overlap
- **📱 Responsive Design**: Modern HTML/CSS/JavaScript interface
- **📋 Copy to Clipboard**: JavaScript-based result copying
- **🔍 File Validation**: Client-side file size and type checking
- **⚡ Quick Questions**: Pre-built question buttons for resumes

---

## 🛠️ **Installation & Setup**

### **Prerequisites**
```bash
Python 3.8+
pip (Python package manager)
```

### **1. Clone Repository**
```bash
git clone https://github.com/Abhishek210001/summary-qna-bot.git
cd summary-qna-bot
```

### **2. Install Dependencies**

**For Local Flask App (AI Models):**
```bash
pip install flask transformers torch PyMuPDF werkzeug numpy
```

**For Cloud Streamlit App (Text Processing):**
```bash
pip install streamlit PyMuPDF numpy requests
```

### **3. Run Applications**

**Local Flask App:**
```bash
python working_flask_app.py
# Access: http://localhost:5000
```

**Streamlit App:**
```bash
streamlit run app.py
# Access: http://localhost:8501
```

---

## 🌐 **Deployment Options**

### **1. Streamlit Community Cloud** ⭐ *Recommended*
1. Fork this repository
2. Go to [share.streamlit.io](https://share.streamlit.io/)
3. Connect your GitHub account
4. Deploy using `app.py`
5. **Memory-optimized version will deploy successfully!**

### **2. Railway**
1. Connect GitHub repository
2. Use `app_deploy.py` as main file
3. Railway will auto-detect and deploy

### **3. Render**
1. Connect GitHub repository  
2. Use `app_deploy.py` as main file
3. Set build command: `pip install -r requirements_deploy.txt`

### **4. Heroku**
1. Connect GitHub repository
2. Uses `Procfile` for configuration
3. Automatic deployment with `app_deploy.py`

---

## 📁 **Project Structure**

```
📦 summary-qna-bot/
├── 🚀 Main Applications
│   ├── app.py                    # Cloud-optimized Streamlit app
│   ├── working_flask_app.py      # Local Flask app (high-performance)
│   └── app_cloud_optimized.py    # Backup cloud version
├── ⚙️ Deployment Configurations
│   ├── app_deploy.py             # General cloud deployment
│   ├── Procfile                  # Heroku/Railway config
│   ├── runtime.txt               # Python version
│   └── .streamlit/config.toml    # Streamlit theming
├── 📋 Requirements
│   ├── requirements.txt          # Minimal cloud dependencies
│   ├── requirements_deploy.txt   # Full deployment dependencies
│   └── requirements_minimal.txt  # Ultra-light requirements
├── 🎨 Frontend
│   └── templates/
│       └── index.html            # Beautiful web interface
├── 📚 Documentation
│   ├── README.md                 # This file
│   └── DEPLOYMENT_GUIDE.md       # Detailed deployment guide
└── 📓 Original Notebook
    └── summery-and-qna-bot.ipynb # Original Jupyter implementation
```

---

## 🎯 **Use Cases**

### **👨‍🎓 Students**
- Summarize research papers and textbooks
- Extract key information from academic documents
- Get quick answers about study materials

### **👨‍💼 Professionals**
- Process reports and documentation
- Analyze business documents
- Extract insights from lengthy files

### **🔍 Job Seekers**
- Optimize resumes and cover letters
- Get structured analysis of CV content
- Improve document formatting and content

### **👨‍🔬 Researchers**
- Extract insights from academic papers
- Summarize literature reviews
- Analyze research documents

---

## 🧠 **AI Models & Technology**

### **Local Flask App (AI-Powered)**
- **AI Models**: BART-Large-CNN (facebook/bart-large-cnn) for summarization
- **AI Models**: RoBERTa-Large-Squad2 (deepset/roberta-large-squad2) for Q&A
- **Fallbacks**: DistilBART-CNN-12-6 and DistilBERT-base-cased-distilled-squad
- **Processing**: Transformers pipeline, intelligent chunking, context preservation

### **Cloud Streamlit App (Algorithm-Based)**
- **Text Analysis**: Regex-based preprocessing and sentence extraction
- **Keyword Matching**: Intelligent Q&A using word scoring and relevance
- **Resume Processing**: Specialized text cleaning and structured formatting
- **Memory Efficient**: No AI models, pure Python text processing

### **Core Technologies Actually Used**
- **Frontend**: Streamlit (cloud), Flask + HTML/CSS/JavaScript (local)
- **PDF Processing**: PyMuPDF (fitz) for text extraction
- **AI Framework**: Transformers library (local Flask app only)
- **Text Processing**: Python regex, string manipulation, numpy
- **Deployment**: Streamlit Cloud, Railway, Render, Heroku support

---

## 📊 **Performance Comparison**

| Feature | Local Flask App | Cloud Streamlit App |
|---------|----------------|-------------------|
| **Technology** | AI Models (BART + RoBERTa) | Algorithm-based processing |
| **Accuracy** | High (AI-powered) | Good (keyword matching) |
| **Speed** | Moderate (model loading) | Fast (no models) |
| **Memory Usage** | High (~2-3GB with models) | Low (~100MB) |
| **Dependencies** | transformers, torch, flask | streamlit, PyMuPDF only |
| **Best For** | Maximum AI accuracy | Cloud deployment |

---

## 🚀 **Quick Start Examples**

### **Example 1: Resume Analysis**
```python
# Upload your resume PDF
# Get structured analysis:
# • Contact information extraction
# • Skills and technologies identified
# • Experience timeline
# • Educational background
# • Project highlights
```

### **Example 2: Research Paper Summary**
```python
# Upload academic paper
# Ask: "What are the main findings?"
# Get: Comprehensive summary with key insights
```

### **Example 3: Business Document Processing**
```python
# Upload business report
# Ask: "What are the financial highlights?"
# Get: Key metrics and important information
```

---

## 🔧 **Configuration**

### **Environment Variables**
```bash
# Optional: Disable Hugging Face symlink warnings
export HF_HUB_DISABLE_SYMLINKS_WARNING=1

# Optional: Set custom port for Flask
export FLASK_PORT=5000
```

### **Streamlit Configuration**
```toml
# .streamlit/config.toml
[theme]
primaryColor="#667eea"
backgroundColor="#262730"
secondaryBackgroundColor="#2e303e"
textColor="#ffffff"
font="sans serif"
```

---

## 🐛 **Troubleshooting**

### **Common Issues**

**1. Memory Issues on Cloud Deployment**
- ✅ **Solution**: Use `app.py` (memory-optimized version)
- ❌ **Avoid**: Using resource-intensive versions on free cloud tiers

**2. PDF Processing Errors**
- ✅ **Solution**: Ensure PDF is text-based (not scanned images)
- ✅ **Tip**: Try different PDF files to test functionality

**3. Local Flask App Not Starting**
- ✅ **Solution**: Run `python working_flask_app.py` instead of `python app.py`
- ✅ **Check**: Install AI dependencies: `pip install transformers torch`
- ✅ **Note**: First run downloads ~2-3GB of AI models

**4. Streamlit Command Not Found**
- ✅ **Solution**: Install streamlit: `pip install streamlit`
- ✅ **Alternative**: Use `python -m streamlit run app.py`

**5. AI Model Loading Errors (Local Flask)**
- ✅ **Solution**: Ensure stable internet for model downloads
- ✅ **Fallback**: App automatically uses lighter DistilBART/DistilBERT models
- ✅ **Space**: Ensure ~5GB free disk space for model cache

---

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 **Acknowledgments**

- **Streamlit** for the web app framework
- **Flask** for the web framework
- **PyMuPDF (fitz)** for PDF text extraction
- **Transformers (Hugging Face)** for AI model pipeline (local app)
- **Facebook AI** for BART-Large-CNN model
- **deepset** for RoBERTa-Large-Squad2 model
- **Font Awesome** for icons in the web interface

---

## 📞 **Support**

- **Issues**: [GitHub Issues](https://github.com/Abhishek210001/summary-qna-bot/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Abhishek210001/summary-qna-bot/discussions)
- **Email**: Create an issue for support requests

---

## 🌟 **Star History**

If you find this project helpful, please consider giving it a ⭐ on GitHub!

---

**🚀 Ready to transform your document processing workflow? Deploy now and experience the power of AI-driven text analysis!**