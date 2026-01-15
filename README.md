# RAG Chatbot with Gemini AI 🤖

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.128-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.2-61dafb.svg)](https://reactjs.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

> A production-ready chatbot with Retrieval Augmented Generation (RAG), real-time streaming, and document intelligence. Built with FastAPI, React, and Google Gemini AI.

[**🚀 Live Demo**](#) | [**📖 Documentation**](DEMO.md) | [**🎥 Video Demo**](#)

---

## 🌟 Highlights

- **Real-Time Streaming**: Sub-100ms first token latency with Server-Sent Events
- **Smart Document Search**: FAISS vector database with semantic similarity
- **Production Ready**: Comprehensive error handling, validation, and logging
- **Secure by Design**: Rate limiting, input sanitization, security headers
- **Modern Stack**: FastAPI + React + Vite with hot module replacement
- **Mobile First**: Responsive design tested on iOS and Android

## Features

- 🤖 **AI-Powered Chat**: Streaming responses with Gemini 2.5 Flash
- 📄 **Document Upload**: Support for PDF, TXT, and DOCX files
- 🔍 **RAG Integration**: Context-aware responses using uploaded documents
- 📱 **Responsive Design**: Mobile-first UI that works on all devices
- ⚡ **Real-Time Streaming**: Word-by-word response display via Server-Sent Events
- 🎨 **Markdown Support**: Formatted AI responses with code highlighting
- 🔒 **Security**: Rate limiting, input sanitization, file validation, HTTPS enforcement

## Architecture

### Backend (FastAPI)
- **Document Processing**: Extract and chunk text from multiple file formats
- **Vector Search**: FAISS-based semantic search with 768-dim embeddings
- **RAG Pipeline**: Query → Embed → Search → Augment → Generate
- **Streaming API**: SSE for real-time response streaming

### Frontend (React + Vite)
- **Modern Stack**: React 18, Vite 5, Axios
- **State Management**: Context API for global state
- **Real-Time UI**: SSE-based streaming with markdown rendering
- **Responsive**: Mobile-first CSS with breakpoints

### Technology Stack

**Backend:**
- FastAPI 0.128.0
- Google Gemini API (text-embedding-004, gemini-2.5-flash)
- FAISS (in-memory vector store)
- PyPDF2, python-docx (document processing)
- Pydantic (validation)

**Frontend:**
- React 18.2
- Vite 5.2
- Axios 1.6
- react-markdown
- Custom CSS (no framework)

## Project Structure

```
RAG_chatbot/
├── app/
│   ├── backend/
│   │   ├── models/          # Pydantic models
│   │   ├── routes/          # API endpoints
│   │   └── services/        # Business logic
│   │       ├── document_processor.py
│   │       ├── embedding_service.py
│   │       ├── vector_store.py
│   │       └── rag_service.py
│   ├── frontend/
│   │   └── src/
│   │       ├── components/  # React components
│   │       ├── services/    # API clients
│   │       ├── context/     # State management
│   │       ├── hooks/       # Custom hooks
│   │       └── styles/      # CSS files
│   ├── middleware/
│   │   └── settings/        # Configuration
│   └── thirdparty_API/      # Gemini client
├── uploads/                 # User-uploaded files
├── main.py                  # FastAPI app
└── requirements.txt         # Python dependencies
```

## Installation

### Prerequisites
- Python 3.12+
- Node.js 18+
- Gemini API key

### Backend Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd RAG_chatbot
```

2. Create virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
```bash
GEMINI_API_KEY=your_api_key_here
```

5. Start backend:
```bash
uvicorn main:app --reload --port 8000
```

### Frontend Setup

1. Navigate to frontend:
```bash
cd app/frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start development server:
```bash
npm run dev
```

Frontend runs on: http://localhost:5173

## Usage

### Development

**Backend**: http://localhost:8000
- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/api/health

**Frontend**: http://localhost:5173

### Production Build

1. Build frontend:
```bash
cd app/frontend
npm run build
```

2. Start backend (serves both API and frontend):
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

Access at: http://localhost:8000

### Mobile Access

On the same WiFi network, access via:
```
http://<your-ip>:8000
```

## API Endpoints

### Health
- `GET /api/health` - Server status and vector store stats

### Upload
- `POST /api/upload` - Upload document for RAG
  - Accepts: PDF, TXT, DOCX
  - Max size: 10MB
  - Returns: Chunk count and file ID

### Chat
- `POST /api/chat/stream` - Streaming chat (SSE)
- `POST /api/chat` - Non-streaming chat
  
Request body:
```json
{
  "message": "Your question here",
  "conversation_history": [],
  "use_rag": true
}
```

## Security

Built-in security features:

- ✅ **Rate Limiting**: 10 chat requests/minute, 5 uploads/minute per IP
- ✅ **Input Sanitization**: XSS prevention with HTML/script tag removal
- ✅ **File Validation**: Extension whitelist, size limits, path traversal protection
- ✅ **Security Headers**: HSTS, CSP, X-Frame-Options, X-Content-Type-Options
- ✅ **HTTPS Enforcement**: Automatic on deployment platforms
- ✅ **API Key Protection**: Environment variables only, never in code

**Important**:
- Never commit `.env` file (already in `.gitignore`)
- Rotate API keys every 90 days
- Monitor API usage at https://aistudio.google.com/app/apikey

📖 **Read the full security guide**: [SECURITY.md](SECURITY.md)

## Configuration

### Backend Settings (`app/middleware/settings/settings.py`)

**AI Configuration:**
- `GEMINI_API_KEY`: API key (from .env)
- `GEMINI_MODEL`: gemini-2.5-flash
- `GEMINI_EMBEDDING_MODEL`: models/text-embedding-004

**Security Configuration:**
- `RATE_LIMIT_CHAT`: "10/minute"
- `RATE_LIMIT_UPLOAD`: "5/minute"
- `MAX_MESSAGE_LENGTH`: 4000 characters
- `MAX_CONVERSATION_HISTORY`: 20 messages
- `ENABLE_SANITIZATION`: true

**RAG Configuration:**
- `UPLOAD_DIR`: uploads/
- `MAX_UPLOAD_SIZE_MB`: 10
- `ALLOWED_FILE_TYPES`: [".pdf", ".txt", ".docx"]
- `CHUNK_SIZE`: 500 words
- `CHUNK_OVERLAP`: 50 words
- `TOP_K_RESULTS`: 5

**CORS Configuration:**
- `CORS_ORIGINS`: Allowed origins for CORS

### Gemini API Free Tier Limits

- 15 requests/minute
- 1M tokens/minute
- 1,500 requests/day

## Development Workflow

1. **Backend changes**: Auto-reload with `--reload` flag
2. **Frontend changes**: Hot module replacement (HMR) with Vite
3. **Testing**: Use `test_main.http` for API testing

## Optimization Opportunities

### Performance
- [ ] Add Redis caching for embeddings
- [x] Implement request rate limiting ✅
- [ ] Add database for conversation persistence
- [ ] Optimize chunking strategy (sliding window)

### Features
- [ ] User authentication (JWT)
- [ ] Multi-user support with isolated vector stores
- [ ] Conversation history persistence
- [ ] File management UI (delete, list uploads)
- [ ] Advanced RAG: re-ranking, query expansion
- [ ] Support more file types (PPT, HTML, CSV)

### Infrastructure
- [ ] Docker containerization
- [ ] Kubernetes deployment
- [ ] CI/CD pipeline
- [ ] Monitoring and logging (Sentry, DataDog)
- [ ] Production vector DB (Pinecone, ChromaDB)

### UI/UX
- [ ] Dark mode toggle
- [ ] Message reactions
- [ ] Copy to clipboard
- [ ] Export conversation
- [ ] File preview before upload

## Troubleshooting

### Backend issues
- Check `.env` file has valid `GEMINI_API_KEY`
- Verify port 8000 is not in use
- Check Python version: `python --version`

### Frontend issues
- Clear `node_modules` and reinstall: `rm -rf node_modules && npm install`
- Check API proxy in `vite.config.js`
- Verify backend is running

### CORS issues
- Add your origin to `CORS_ORIGINS` in settings
- Check browser console for CORS errors

## License

MIT

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit with descriptive messages
4. Submit a pull request

## Author

Built with ❤️ using Claude Code
