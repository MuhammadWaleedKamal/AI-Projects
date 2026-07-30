# 🧠 Smart AI Text & Insight Assistant

An intelligent, full-stack web application designed for dynamic text analysis, summarization, and educational concept explanation using Google's Gemini Large Language Models.

---

## ✨ Features

* 📝 **Multi-Mode AI Processing**:
  * **General Q&A / Writing**: Direct multi-purpose conversational assistance.
  * **Summarize Key Points**: Structured bulleted insights with emphasized key topics.
  * **Explain Simply**: Core concept breakdowns using real-world analogies.
* 📄 **Document File Parsing**: Upload and analyze `.pdf`, `.docx`, and `.txt` files directly without manual copy-pasting.
* ⚡ **Serverless Deployment**: Architected with a Python Flask backend served seamlessly via Vercel Serverless Functions.
* 🎨 **Clean & Responsive UI**: Built with HTML5, CSS3, Vanilla JS, and Markdown rendering support.

---

## 🛠️ Tech Stack

* **Frontend**: HTML5, CSS3, Vanilla JavaScript, Marked.js (Markdown Parser)
* **Backend**: Python 3.x, Flask, Flask-CORS
* **AI Orchestration**: Google GenAI SDK (`gemini-1.5-flash`)
* **Document Handling**: `pypdf`, `python-docx`
* **Deployment**: Vercel Serverless Platform

---

## 📂 Project Structure

```text
1_Smart AI Assistant/
│
├── api/
│   └── index.py        # Flask Backend & API Routes
├── public/
|   ├── aboutus.html
│   ├── contactus.html   
│   ├── index.html      # UI Layout & Favicon
│   ├── style.css       # Responsive Stylesheet
│   └── scripts.js      # Async Event Handling & API Integration
├── .gitignore          # Environment & Cache Exclusions
├── requirements.txt    # Python Package Dependencies
└── vercel.json         # Vercel Routing Configuration
```

## ⚙️ Local Setup Guide
**Clone the repository:**

```Bash
git clone [https://github.com/MuhammadWaleedKamal/AI-Projects.git](https://github.com/MuhammadWaleedKamal/AI-Projects.git)
cd AI-Projects/LLM\ \&\ Generative\ AI/1_Smart\ AI\ Assistant
```

**Set up virtual environment:**

```Bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

**Install dependencies:**

```Bash
pip install -r requirements.txt
```

## Environment Configuration:
**Create a .env file in the root directory:**

**Code snippet**

GEMINI_API_KEY=your_google_gemini_api_key

## Run the Flask application:

```Bash
python api/index.py
```
Open http://127.0.0.1:5000 in your browser.
