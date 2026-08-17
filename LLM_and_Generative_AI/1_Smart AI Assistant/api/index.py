import os
import warnings
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Document/PDF Parsing
import docx
from pypdf import PdfReader

warnings.filterwarnings("ignore", category=FutureWarning)

from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai
from google.genai import types

load_dotenv(override=True)

app = Flask(__name__)
CORS(app)

# Environment Variables
api_key = os.environ.get("GEMINI_API_KEY")
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD")
RECEIVER_EMAIL = os.environ.get("RECEIVER_EMAIL")

SYSTEM_INSTRUCTIONS = {
    "summarize": "You are a professional summarizer. Summarize the provided content strictly into clear, bulleted key insights with bold headings.",
    "explain": "You are a friendly explainable person. Explain the core concepts of the provided content in simple terms using a creative real-world analogy.",
    "general": "You are a helpful AI assistant. Provide a concise, clear analysis and structured response to the user's content."
}

def extract_text_from_file(file, filename):
    text = ""
    if filename.endswith('.pdf'):
        reader = PdfReader(file)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    elif filename.endswith(('.docx', '.doc')):
        doc = docx.Document(file)
        text = "\n".join([para.text for para in doc.paragraphs])
    elif filename.endswith('.txt'):
        text = file.read().decode('utf-8')
    return text.strip()

@app.route('/api/analyze', methods=['POST'])
def analyze():
    if not api_key:
        return jsonify({"error": "GEMINI_API_KEY environment variable is missing."}), 500

    data = request.get_json() or {}
    user_prompt = data.get("prompt", "").strip()
    task_type = data.get("task") or data.get("taskSelect") or "general"

    if not user_prompt:
        return jsonify({"error": "Please provide input text."}), 400

    instruction = SYSTEM_INSTRUCTIONS.get(task_type, SYSTEM_INSTRUCTIONS["general"])

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model='gemini-3.5-flash-lite',
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=instruction
            )
        )
        return jsonify({"result": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/analyze_file', methods=['POST'])
def analyze_file():
    if not api_key:
        return jsonify({"error": "GEMINI_API_KEY is not configured."}), 500

    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded."}), 400

    uploaded_file = request.files['file']
    filename = uploaded_file.filename.lower()
    task_type = request.form.get("task") or request.form.get("taskSelect") or "general"

    if filename == '':
        return jsonify({"error": "No file selected."}), 400

    instruction = SYSTEM_INSTRUCTIONS.get(task_type, SYSTEM_INSTRUCTIONS["general"])

    try:
        client = genai.Client(api_key=api_key)
        config = types.GenerateContentConfig(system_instruction=instruction)

        if filename.endswith(('.pdf', '.docx', '.doc', '.txt')):
            extracted_text = extract_text_from_file(uploaded_file, filename)
            
            if not extracted_text:
                return jsonify({"error": "Could not extract text from document or file is empty."}), 400

            response = client.models.generate_content(
                model='gemini-3.5-flash-lite',
                contents=extracted_text,
                config=config
            )
            return jsonify({"result": response.text})

        else:
            return jsonify({"error": "Unsupported file format."}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/contact', methods=['POST'])
def send_contact_email():
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        return jsonify({"error": "Email credentials are not configured in environment variables."}), 500

    data = request.get_json() or {}
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    message = data.get("message", "").strip()

    if not name or not email or not message:
        return jsonify({"error": "All fields are required."}), 400

    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECEIVER_EMAIL or SENDER_EMAIL
        msg['Reply-To'] = email
        msg['Subject'] = f"New Contact Form Message from {name}"

        body_content = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"
        msg.attach(MIMEText(body_content, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()

        return jsonify({"message": "Email sent successfully!"}), 200

    except Exception as e:
        return jsonify({"error": "Failed to send email."}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)

