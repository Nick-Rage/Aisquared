import os
import boto3
import pdfplumber
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import Ollama

# ==== CONFIG ====
LOCAL_FOLDER = "data"
INDEX_PATH = "faiss_index"
S3_BUCKET = "nikhil-pdf-chatbot"  

PDF_STATS = []  

# S3 client
s3 = boto3.client("s3")

# SYNC S3 TO LOCAL
def sync_from_s3():
    os.makedirs(LOCAL_FOLDER, exist_ok=True)
    response = s3.list_objects_v2(Bucket=S3_BUCKET)
    if "Contents" in response:
        for obj in response["Contents"]:
            key = obj["Key"]
            local_path = os.path.join(LOCAL_FOLDER, key)
            if not os.path.exists(local_path):  # avoid re-downloading
                print(f"⬇️ Downloading {key} from S3...")
                s3.download_file(S3_BUCKET, key, local_path)

# LOAD PDFs + stats
def extract_text():
    global PDF_STATS
    PDF_STATS.clear()
    docs = []
    for filename in os.listdir(LOCAL_FOLDER):
        if filename.endswith(".pdf"):
            path = os.path.join(LOCAL_FOLDER, filename)
            word_count = 0
            with pdfplumber.open(path) as pdf:
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if text and text.strip():
                        wc = len(text.split())
                        word_count += wc
                        docs.append(Document(
                            page_content=text,
                            metadata={
                                "source": filename,
                                "page": i+1,
                                "words": wc,
                                "total_pages": len(pdf.pages),
                                "total_words": word_count
                            }
                        ))
            PDF_STATS.append({
                "filename": filename,
                "pages": len(pdf.pages),
                "words": word_count
            })
            print(f"✅ {filename}: {len(pdf.pages)} pages, {word_count} words")
    return docs

def chunk_docs(docs):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(docs)
    print(f"🔎 Created {len(chunks)} chunks from {len(docs)} pages.")
    return chunks


def build_index(docs):
    model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = FAISS.from_documents(docs, model)
    vectorstore.save_local(INDEX_PATH)
    print(f"📦 Index saved with {len(docs)} chunks.")
    return vectorstore

def load_index():
    model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return FAISS.load_local(INDEX_PATH, model, allow_dangerous_deserialization=True)

#PUBLIC FUNCTIONS 
def get_vectorstore():
    sync_from_s3()  # pull latest PDFs from S3
    docs = extract_text()
    chunks = chunk_docs(docs)
    if not os.path.exists(INDEX_PATH):
        return build_index(chunks)
    else:
        return load_index()

def refresh_index():
    """Force rebuild index from S3 (used when new files are uploaded)."""
    sync_from_s3()
    docs = extract_text()
    chunks = chunk_docs(docs)
    return build_index(chunks)

def ask_question(vectorstore, query):
    if query.lower() in ["hi", "hello", "hey", "how are you?", "how are you"]:
        return "I’m doing well 😊 Thanks for asking! How can I help with your PDFs?"

    # 🔄 Switched from mistral to gemma:2b
    llm = Ollama(model="gemma:2b", options={"num_ctx": 1024})

    system_prompt = """
You are a helpful AI assistant.
You can answer conversationally like ChatGPT, but you also have access to PDF data.
- Always use the PDF_STATS (list of PDFs, pages, words).
- Use retrieved chunks for detailed answers.
- If context doesn’t contain an answer, say “I don’t know”.
"""

    stats_text = "\n".join(
        [f"{s['filename']} — {s['pages']} pages, {s['words']} words" for s in PDF_STATS]
    )

    docs = vectorstore.similarity_search(query, k=15)
    context = "\n".join(
        [f"[{d.metadata['source']} - p{d.metadata['page']}]: {d.page_content}" for d in docs]
    )

    prompt = f"""
{system_prompt}

PDF_STATS:
{stats_text}

Context:
{context}

User Question: {query}
Answer:
"""
    response = llm.invoke(prompt)
    return str(response)


