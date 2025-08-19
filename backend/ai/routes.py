# backend/modules/ai/routes.py

from flask import Blueprint, request, jsonify
from .auto_tagging import auto_tag
from .copilot import ask_copilot
from .ocr_engine import ocr_image

ai_bp = Blueprint("ai", __name__)

@ai_bp.route("/tag", methods=["POST"])
def tag_text():
    data = request.get_json()
    text = data.get("text")
    if not text:
        return jsonify({"message": "Text is required"}), 400
    
    tags = auto_tag(text)
    return jsonify({"tags": tags}), 200

@ai_bp.route("/copilot", methods=["POST"])
def get_copilot_response():
    data = request.get_json()
    prompt = data.get("prompt")
    if not prompt:
        return jsonify({"message": "Prompt is required"}), 400
    
    response = ask_copilot(prompt)
    return jsonify({"response": response}), 200

@ai_bp.route("/ocr", methods=["POST"])
def perform_ocr():
    if 'file' not in request.files:
        return jsonify({"message": "No file part in the request"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"message": "No selected file"}), 400
    
    file_bytes = file.read()
    extracted_text = ocr_image(file_bytes)
    return jsonify({"text": extracted_text}), 200