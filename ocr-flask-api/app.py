from flask import Flask, request, jsonify
from PIL import Image
import pytesseract
import io

app = Flask(__name__)

@app.route("/")
def home():
    return "🧠 OCR API is running."

@app.route("/ocr", methods=["POST"])
def ocr_image():
    file = request.files.get("image")
    if not file:
        return jsonify({"error": "No image provided"}), 400

    image = Image.open(file.stream).convert("RGB")
    text = pytesseract.image_to_string(image, lang="tha+eng")

    suspicious_words = ["มาจอง2pg", "สล็อตpg", "แตก2หมื่น"]
    found_words = [word for word in suspicious_words if word in text]

    result = {
        "text": text.strip(),
        "found": found_words,
        "status": "✅ พบ" if found_words else "❌ ไม่พบข้อความที่ต้องการ"
    }
    return jsonify(result), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)