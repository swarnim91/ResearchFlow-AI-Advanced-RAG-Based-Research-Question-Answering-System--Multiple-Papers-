# ResearchFlow AI 🔬

**Advanced RAG-Based Academic Research & Question Answering System**

ResearchFlow AI is an intelligent platform designed for academic researchers, students, and professionals to search, organize, and synthesize insights from batches of complex PDF research papers. Built with a modern **React + Vite** frontend and a **FastAPI + LangChain** backend, the application uses HuggingFace embeddings, ChromaDB vector storage, and Groq LLMs to extract metadata and deliver accurate, synthesized answers with exact document citations.

---

## 🌟 Key Features

- **Upload & Automated Metadata Extraction:**
  Automatically extracts structured metadata (*Title, Authors, Publication Year, Summary, and Keywords*) using LLM-powered PDF analysis.

- **Vector Storage & Semantic QA:**
  Chunks paper content with optimized overlap and indexes them into ChromaDB using SentenceTransformers (`all-MiniLM-L6-v2`).

- **AI Synthesis & Citation:**
  Synthesizes paragraph-level structured responses (**Summary**, **Key Details**, **Synthesis**) with exact paper references.

- **Unified Full-Stack Deployment:**
  Configured to serve the production React frontend directly from FastAPI, allowing single-port deployment on Docker, Render, Railway, HuggingFace, etc.

---

## 🛠️ Technology Stack

- **Frontend:** React 19, Vite, Lucide-React, CSS Glassmorphism UI
- **Backend:** Python 3.11+, FastAPI, Uvicorn
- **AI Core:** LangChain, HuggingFace Sentence Transformers
- **LLM Provider:** Groq (`openai/gpt-oss-20b` or custom models)
- **Vector Database:** ChromaDB 0.5.x
- **PDF Parsing:** PyMuPDF, PyPDF

---

## 🚀 Deployment & Getting Started

### Prerequisites

- **Python >= 3.11** and **Node.js >= 18**
- A valid **Groq API Key** ([Get one here](https://console.groq.com/keys))

---

### Option 1: 1-Command Local Development (Recommended)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/swarnim91/ResearchFlow-AI-Advanced-RAG-Based-Research-Question-Answering-System--Multiple-Papers-.git
   cd ResearchFlow-AI-Advanced-RAG-Based-Research-Question-Answering-System--Multiple-Papers-
   ```

2. **Configure Environment:**
   Create a `.env` file in the project root:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   MODEL_NAME=openai/gpt-oss-20b
   ```

3. **Install Dependencies:**
   ```bash
   # Backend
   pip install -r requirements.txt

   # Frontend
   cd frontend && npm install && cd ..
   ```

4. **Launch Both Backend & Frontend:**
   ```bash
   python run.py
   ```
   - **Frontend UI:** `http://localhost:5173`
   - **Backend API:** `http://127.0.0.1:8000`

---

### Option 2: Docker Container Deployment (Multi-Stage Production)

Deploy the complete application (Frontend + Backend) inside a single containerized setup:

```bash
# Set your API Key
export GROQ_API_KEY=your_groq_api_key_here

# Build and run with Docker Compose
docker compose up --build
```
Access the unified web application at `http://localhost:8000`.

---

### Option 3: Cloud PaaS (Render, Railway, Heroku)

#### **1-Click Render Deployment (`render.yaml`)**
1. Connect your repository to [Render](https://render.com).
2. Select **Blueprints** and point to `render.yaml`.
3. Set your `GROQ_API_KEY` in the Render dashboard environment variables.

#### **Manual Web Service Deployment**
- **Build Command:** `pip install -r requirements.txt && cd frontend && npm install && npm run build`
- **Start Command:** `uvicorn backend.api:app --host 0.0.0.0 --port $PORT`

---

## ⚙️ Environment Variables

| Variable | Default | Description |
|---|---|---|
| `GROQ_API_KEY` | *(Required)* | Groq Cloud API Key |
| `MODEL_NAME` | `openai/gpt-oss-20b` | Groq LLM Model name |
| `CHUNK_SIZE` | `1000` | Text chunk size for vector embedding |
| `CHUNK_OVERLAP` | `200` | Overlap between chunks |
| `NUM_RETRIEVED_DOCS` | `4` | Top K chunks retrieved for QA |

---

## 📝 License

Distributed under the MIT License.
