from flask import Blueprint, render_template, request, jsonify
from .resume_parser import parse_resume, analyze_resume
from datetime import datetime

main = Blueprint('main', __name__)

@main.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

@main.route('/')
def home():
    return render_template('index.html')

@main.route('/upload', methods=['POST'])
def upload():
    if 'resume' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['resume']
    text = parse_resume(file)
    analysis = analyze_resume(text)
    return jsonify(analysis)
