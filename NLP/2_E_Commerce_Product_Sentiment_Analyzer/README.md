# 🛍️ Multilingual E-Commerce Sentiment & Aspect Extraction Engine

An enterprise-grade Aspect-Based Sentiment Analysis (ABSA) system engineered to process unstructured customer reviews, extract granular product aspects using NLP dependency parsing, and perform fine-grained sentiment classification. Features real-time automated email notifications dispatched to administrators upon detecting negative customer feedback.

## 🏗️ Architecture & Decoupled Infrastructure

The application follows a resilient microservice architecture designed to handle heavy Deep Learning workloads while ensuring zero serverless execution timeouts:

* **Backend Microservice (Docker + Railway):** Containerized using Docker and hosted on Railway for continuous 24/7 execution, overcoming serverless storage and memory limits for PyTorch and Transformer models.
* **Email Notification Subsystem (Resend API):** Utilizes an HTTP-based transactional mail API (Resend SDK) to bypass traditional cloud SMTP port restrictions (ports 587/465) for guaranteed, instant email alert delivery.
* **Frontend Application (Vercel):** Single-Page Application (SPA) hosted on Vercel as pure static assets, communicating asynchronously with the Railway API via CORS-enabled REST endpoints.

## 🚀 Key Technical Features

* **Linguistic Aspect Extraction:** Powered by **SpaCy** dependency trees and noun chunk parsing to dynamically isolate product features (e.g., *"battery backup"*, *"build quality"*) without static keyword rules.
* **Transformer Sentiment Engine:** Integrated with **Hugging Face RoBERTa** (`twitter-roberta-base-sentiment-latest`) for multi-class sentiment predictions and confidence scoring.
* **HTTP-Based Admin Alerts:** Triggers automatic HTML email notifications to store administrators for negative reviews via Resend API HTTP calls.
* **Glassmorphism Interactive UI:** Clean frontend featuring custom CSS glassmorphism, tech stack animations, responsive contact forms, and real-time payload visualization.

## 🛠️ Tech Stack

* **Backend:** Python, FastAPI, Uvicorn, Pydantic
* **NLP & Deep Learning:** SpaCy (`en_core_web_sm`), Hugging Face Transformers, PyTorch
* **Transactional Mail:** Resend API SDK (HTTP REST Integration)
* **DevOps & Hosting:** Docker, Railway (Containerized Backend), Vercel (Static Frontend)
* **Frontend:** HTML5, Modern CSS3, Vanilla JavaScript (Fetch API)

## 📌 API Endpoints

* `POST /api/analyze` — Parses review text, extracts aspect tokens, computes sentiment confidence, and dispatches negative feedback alert emails.
* `POST /api/contact` — Routes user contact queries directly to the administrator's primary inbox.
