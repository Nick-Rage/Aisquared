from flask import Flask, render_template, request, jsonify
from chatbot import get_vectorstore, ask_question, PDF_STATS, refresh_index, S3_BUCKET, s3

app = Flask(__name__)

# Warm up (downloads from S3, builds index)
vectorstore = get_vectorstore()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    query = data.get("query", "")
    vs = vectorstore or get_vectorstore()
    answer = ask_question(vs, query)
    return jsonify({"answer": answer})

@app.route("/stats")
def stats():
    return jsonify(PDF_STATS)

@app.route("/upload-url", methods=["POST"])
def upload_url():
    data = request.get_json()
    filename = data["filename"]
    key = filename
    presigned = s3.generate_presigned_post(
        Bucket=S3_BUCKET,
        Key=key,
        Fields={"Content-Type": "application/pdf"},
        Conditions=[{"Content-Type": "application/pdf"}],
        ExpiresIn=3600,
    )
    return jsonify(presigned)

@app.route("/reindex", methods=["POST"])
def reindex():
    refresh_index()
    return jsonify({"ok": True, "count": len(PDF_STATS)})

if __name__ == "__main__":
    # Run only on localhost
    app.run(debug=True)
