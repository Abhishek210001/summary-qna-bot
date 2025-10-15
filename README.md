# 🤖 AI Document Summarizer & Q&A Bot Web UI

A beautiful, modern web interface for your AI-powered document summarization and question-answering bot. Built with Flask and powered by state-of-the-art transformer models from Hugging Face.

## ✨ Features

- **📄 Document Summarization**: Upload PDF/TXT files or paste text for intelligent summaries
- **❓ Question Answering**: Ask specific questions about your documents
- **🎨 Modern UI**: Beautiful, responsive design with drag-and-drop file upload
- **⚡ Fast Processing**: Optimized with BART and RoBERTa models
- **📱 Mobile Friendly**: Works perfectly on all devices
- **🔍 Smart Analysis**: Enhanced answer evaluation and context understanding

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager
- At least 4GB RAM (for model loading)

### Installation

1. **Clone or download this project**
   ```bash
   cd "C:\\kaggle project"
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   # On Windows:
   venv\\Scripts\\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Open your browser**
   Navigate to: `http://localhost:5000`

## 🎯 Usage

### Document Summarization
1. **Upload a file**: Drag & drop or click to select PDF/TXT files (max 16MB)
2. **Or paste text**: Use the text input tab for direct text entry
3. **Click Process**: Let AI generate an intelligent summary

### Question Answering
1. **Upload/enter your document** (same as above)
2. **Enter your question**: Type a specific question about the content
3. **Get answers**: Receive detailed, context-aware responses

### Example Questions
- "What is the main topic of this document?"
- "Which methods were used in this research?"
- "What are the key findings?"
- "How was the data preprocessed?"

## 🏗️ Technical Architecture

### Backend (Flask)
- **app.py**: Main Flask application with REST API
- **Models**: BART for summarization, RoBERTa for Q&A
- **File Processing**: PDF text extraction with PyMuPDF
- **Smart Enhancement**: Context-aware answer improvement

### Frontend (HTML/CSS/JS)
- **Responsive Design**: Modern UI with gradient backgrounds
- **Interactive Elements**: Drag-and-drop, tabs, real-time feedback
- **AJAX Processing**: Seamless document processing without page refresh
- **Progressive Enhancement**: Works with and without JavaScript

### AI Models
- **Summarization**: `facebook/bart-large-cnn`
- **Question Answering**: `deepset/roberta-large-squad2`
- **Text Processing**: Advanced paragraph scoring and relevance matching

## 📁 Project Structure

```
kaggle project/
├── app.py                 # Flask backend application
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # Main web interface
├── summery-and-qna-bot.ipynb  # Original Jupyter notebook
└── README.md             # This file
```

## ⚙️ Configuration

### Model Settings
- **Max Summary Length**: 200 tokens
- **Min Summary Length**: 100 tokens
- **Context Window**: 2048 characters for summarization
- **File Size Limit**: 16MB

### Performance Tips
- First run will download models (~2GB total)
- Models are cached locally for faster subsequent loads
- Consider using GPU for faster processing (requires PyTorch with CUDA)

## 🔧 Troubleshooting

### Common Issues

**Models taking too long to load:**
- First run downloads large models, be patient
- Ensure stable internet connection
- Models are cached after first download

**Out of memory errors:**
- Try processing smaller documents
- Close other applications to free RAM
- Consider using smaller model variants

**File upload not working:**
- Check file size (max 16MB)
- Ensure file format is PDF or TXT
- Clear browser cache and try again

### Error Messages
- `"Please provide either text or upload a file"`: No input provided
- `"Please upload a PDF or TXT file"`: Invalid file format
- `"An error occurred: [details]"`: Processing error - check file content

## 🎨 Customization

### Styling
- Edit `templates/index.html` to modify colors, fonts, layout
- CSS is embedded in the HTML file for easy editing
- Responsive design works on all screen sizes

### Functionality
- Modify `app.py` to add new features or change model parameters
- Add new file format support by extending `allowed_file()` function
- Customize answer enhancement in `enhance_answer()` function

## 📊 Features Comparison

| Feature | Jupyter Notebook | Web UI |
|---------|------------------|--------|
| File Upload | ❌ Manual path | ✅ Drag & Drop |
| Text Input | ❌ Code cells | ✅ Text area |
| User Interface | ❌ Technical | ✅ User-friendly |
| Multiple Users | ❌ Single user | ✅ Multi-user |
| Mobile Support | ❌ Desktop only | ✅ Responsive |
| Real-time Results | ❌ Run cells | ✅ Instant feedback |

## 🚀 Deployment Options

### Local Development
```bash
python app.py
# Access at http://localhost:5000
```

### Production Deployment
For production use, consider:
- Using Gunicorn WSGI server
- Setting up reverse proxy with Nginx
- Configuring SSL certificates
- Using environment variables for configuration

## 🤝 Contributing

This web UI is built on top of your original Jupyter notebook. Feel free to:
- Add new features or models
- Improve the user interface
- Optimize performance
- Add new file format support

## 📝 License

This project is based on your original summarization and Q&A bot implementation.

## 🎉 Acknowledgments

- **Transformers Library**: Hugging Face for the amazing transformer models
- **Flask**: For the lightweight web framework
- **PyMuPDF**: For PDF text extraction capabilities
- **Font Awesome**: For beautiful icons

---

**Happy Summarizing! 🤖📚**

