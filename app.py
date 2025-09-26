from flask import Flask, render_template, request, jsonify
from chatbot import get_vectorstore, ask_question, PDF_STATS, refresh_index, S3_BUCKET, s3

import os

app = Flask(__name__)

# Warm up on startup (downloads from S3, builds index)
vectorstore = None

def warmup():
    global vectorstore
    if vectorstore is None:
        vectorstore = get_vectorstore()


@app.route("/")
def index():
    warmup()
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():
    warmup()
    data = request.get_json()
    query = data.get("query", "")
    vs = vectorstore or get_vectorstore()
    answer = ask_question(vs, query)
    return jsonify({"answer": answer})


@app.route("/stats")
def stats():
    warmup()
    return jsonify(PDF_STATS)


@app.route("/upload-url", methods=["POST"])
def upload_url():
    warmup()
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
    warmup()
    refresh_index()
    return jsonify({"ok": True, "count": len(PDF_STATS)})


if __name__ == "__main__":
    warmup()  # do it once on startup
    app.run(host="0.0.0.0", port=5000, debug=False)
