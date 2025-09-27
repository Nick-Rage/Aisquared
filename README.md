# 📄 PDF Chatbot (Local Setup with Ollama + S3)

This project is a Retrieval-Augmented Generation (RAG) chatbot that lets you upload PDFs to an S3 bucket, build embeddings, and chat with them using an Ollama LLM (like Gemma or Mistral). It runs fully locally via Flask + Ollama.

============================================================
🚀 Features
============================================================
- Upload PDFs to S3 bucket
- Extract text & build FAISS vector index
- Query documents with LangChain + Ollama
- Web UI (Flask + HTML/JS/CSS)
- Local-only setup (no public hosting)

============================================================
📦 Requirements
============================================================
- Python 3.10+ installed
- Ollama installed: https://ollama.com/download
- AWS CLI configured with your credentials
- An S3 bucket (example: nikhil-pdf-chatbot)

============================================================
🔧 Setup Instructions
============================================================

1. Clone the Repo
   powershell:
   git clone https://github.com/<your-repo>/Aisquared.git
   cd Aisquared

2. Create a Virtual Environment
   powershell:
   python -m venv .venv
   .venv\Scripts\activate
   (You should see (.venv) in your terminal after activation.)

3. Install Requirements
   powershell:
   pip install -r requirements.txt

4. Configure AWS CLI
   powershell:
   aws configure
   (Enter your AWS Access Key, Secret Key, region, etc.)

5. Start Ollama
   Check if Ollama is already running:
   tasklist | findstr ollama

   If not running:
   ollama serve

6. Pull a Model
   Recommend Gemma 2B (fast + small):
   ollama pull gemma:2b

============================================================
▶️ Running the App
============================================================

Start Flask:
   powershell:
   python app.py

The app will:
- Sync PDFs from your S3 bucket (nikhil-pdf-chatbot)
- Build FAISS embeddings
- Start a local Flask server at:
  👉 http://127.0.0.1:5000

============================================================
🖥️ Using the Chatbot
============================================================
- Upload new PDFs → stored in S3.
- Click "Refresh Index" → rebuild embeddings.
- Type a question and hit Enter (or click Send).
- Bot responds using Ollama LLM with PDF context.

============================================================
⚡ Troubleshooting
============================================================
- Port 11434 in use: Ollama already running.
  Kill it if needed:
  taskkill /IM ollama.exe /F
  ollama serve

- pip install errors:
  Ensure venv is active:
  .venv\Scripts\activate

- AWS errors:
  Run aws configure again.

============================================================
📂 Project Structure
============================================================
Aisquared/
│── app.py              # Flask app entrypoint
│── chatbot.py          # Core logic (PDF parsing, FAISS, Ollama queries)
│── requirements.txt    # Dependencies
│── templates/
│    └── index.html     # Web UI
│── static/
│    └── style.css      # Styling
│── data/               # Local copy of S3 PDFs
│── faiss_index/        # Vector DB

============================================================
✅ Example Workflow
============================================================
1. Place PDFs in your S3 bucket (nikhil-pdf-chatbot).
2. Start app with python app.py.
3. Open http://127.0.0.1:5000.
4. Ask:
   Summarize my-uncle-jules.pdf
   → Bot replies with context from the PDF.

============================================================
📌 Notes
============================================================
- Runs locally only (not exposed publicly).
- Ollama must be running before you query.
- To switch models, edit chatbot.py (change gemma:2b → mistral, llama2, llama3, etc.).

============================================================
📦 requirements.txt (Save as requirements.txt)
============================================================
flask==3.0.3
boto3==1.34.131
pdfplumber==0.11.4
faiss-cpu==1.8.0
langchain==0.2.7
langchain-community==0.2.7
sentence-transformers==3.0.1
