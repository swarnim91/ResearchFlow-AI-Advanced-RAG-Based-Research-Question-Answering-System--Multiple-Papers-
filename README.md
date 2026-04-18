# ResearchFlow AI 🔬

**Advanced RAG-Based Research & Question Answering System**

ResearchFlow AI is a cutting-edge platform designed for academic researchers, students, and professionals to seamlessly search, organize, and synthesize answers from batches of complex PDF research papers. Built on a modern **React + Vite** frontend and a sophisticated **FastAPI + Langchain** backend, the platform leverages LLMs to provide intelligent vector retrieval capabilities.

---

## 🌟 Key Features

- **Upload & Automated Metadata Extraction:**
  When you upload PDF research papers, our backend utilizes **Langchain's structured outputs via Groq** to read the first few pages and automatically extract robust metadata: *Title, Authors, Publication Year (Explicitly typed as strictly integer), Summary, and Keywords.*

- **Self-Querying Context Retrieval:**
  Thanks to the Langchain `SelfQueryRetriever`, you can ask complex natural language questions. The application autonomously translates inquiries like *"Find papers published >= 2020 about neural networks"* into explicit exact-match numeric filters on the ChromaDB vector database while simultaneously performing deep semantic similarity searches.

- **Intelligent Synthesis:** 
  It uses **Llama 3 (via Groq Cloud)** to read the filtered context passages and synthesize exact paragraph-level answers. If the requested information doesn't exist within the uploaded documents, it is strict enough to confidently reply *"Not found in the provided papers."*

- **Beautiful, Immersive UI:**
  Built with **React and Vanilla CSS**, the frontend avoids standard templates in favor of a bespoke, aesthetically stunning interface featuring dynamic glass-morphism effects, lively gradients, and micro-animations designed to *wow* its users.

---

## 🛠️ Technology Stack

- **Frontend:** React 19, Vite, Lucide-React for styling/icons.
- **Backend:** Python 3.11+, FastAPI, Uvicorn.
- **AI Core:** LangChain, HuggingFace Sentence Transformers (Embeddings).
- **LLM Provider:** Groq (Ultra-fast Llama 3 inference).
- **Vector Database:** ChromaDB (Version 0.5.x).
- **PDF Parsing:** PyMuPDF, PyPDF.

---

## 🚀 Getting Started

To get a local development environment running, follow these steps.

### Prerequisites

- **Python >= 3.11** 
- **Node.js** 
- A valid **Groq API Key** (Create one [here](https://console.groq.com/keys))

### Installation 

1. **Clone the Repository**
   ```bash
   git clone https://github.com/swarnim91/ResearchFlow-AI-Advanced-RAG-Based-Research-Question-Answering-System-Multiple-Papers-React-UI-.git
   cd ResearchFlow-AI-Advanced-RAG-Based-Research-Question-Answering-System-Multiple-Papers-React-UI-
   ```

2. **Backend Setup**
   ```bash
   # Make sure you are in the project root directory where requirements.txt is located.
   
   # Optional but recommended (Create Virtual Env):
   python -m venv .venv
   source .venv/bin/activate # On Windows use: .venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```
   *Note: This project also supports `uv` package manager syntax `uv pip install -r requirements.txt` if installed.*

3. **Environment Setup**
   - In the root folder, locate or create a `.env` file.
   - Add your Groq API Key:
   ```env
   GROQ_API_KEY=your_grossly_incandescent_key_here
   ```

4. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

### Running the Application

**Terminal 1 (Start the Backend):**
```bash
# From the project root
uvicorn backend.api:app --reload
# Or, if using uv:
uv run uvicorn backend.api:app --reload
```
*The API will start running on `http://127.0.0.1:8000`*


**Terminal 2 (Start the Frontend):**
```bash
# Inside the /frontend folder
npm run dev
```
*The UI will generate an immersive dashboard accessible at `http://localhost:5173/`*

---

## 🧪 How It Works (The Pipeline)

1. **User Interaction:** The user drags & drops PDFs in the frontend.
2. **Metadata Construction:** `metadata_extractor.py` instructs ChatGroq to analyze chunked texts to produce a strictly defined Pydantic JSON template mapped exactly to the paper's properties.
3. **Chunking & Vectoring:** Papers are split via `RecursiveCharacterTextSplitter` and transformed into dense vectors via `all-MiniLM-L6-v2`. They are stored in ChromaDB decorated seamlessly with their LLM-extracted metadata.
4. **Self-Query Orchestration:** The user asks an inquiring question. 
5. **RetrievalQA & LLM Response:** The `SelfQueryRetriever` parses deterministic filters out of the user query (e.g. `< 2024`) and isolates the exact paragraphs. The LLM processes those paragraphs directly to formulate a verified answer while the UI displays exact `Cited Papers` references.

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! 
Feel free to check [issues page](https://github.com/swarnim91/ResearchFlow-AI-Advanced-RAG-Based-Research-Question-Answering-System-Multiple-Papers-React-UI-/issues) if you want to contribute.

---

## 📝 License

This project is open-source and available under the terms of the MIT License.
