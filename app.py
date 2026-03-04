from flask import Flask, request, jsonify
from services.document_parser import extract_text_from_pdf
from services.compliance_checker import check_similarity

app = Flask(__name__)

@app.route("/")
def home():
    return "Intelligent Compliance Automation Running"

@app.route("/upload", methods=["POST"])
def upload():

    file = request.files["file"]
    file.save("temp.pdf")

    text = extract_text_from_pdf("temp.pdf")

    return jsonify({
        "extracted_text": text[:500]
    })


@app.route("/check", methods=["POST"])
def check():

    data = request.json

    regulation = data["regulation"]
    policy = data["policy"]

    score = check_similarity(regulation, policy)

    return jsonify({
        "similarity_score": score
    })


if __name__ == "__main__":
    app.run(debug=True)