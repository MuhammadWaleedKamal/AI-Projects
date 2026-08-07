import os
import warnings
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
import spacy
from dotenv import load_dotenv
from transformers import pipeline
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

load_dotenv()

os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
warnings.filterwarnings("ignore")
logging.getLogger("transformers").setLevel(logging.ERROR)

app = FastAPI(title="Aspect Sentiment Analyzer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Email Configuration
conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_USERNAME"),
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True
)

try:
    nlp = spacy.load("en_core_web_sm")
except Exception:
    import spacy.cli
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")
    
sentiment_pipeline = pipeline(
    "sentiment-analysis", 
    model="cardiffnlp/twitter-roberta-base-sentiment-latest"
)

# REMOVED owner_email from payload schema
class ReviewRequest(BaseModel):
    product_name: str
    review: str

class ContactRequest(BaseModel):
    name: str
    sender_email: EmailStr
    message: str

def extract_aspects(text: str):
    doc = nlp(text)
    aspects = []
    for chunk in doc.noun_chunks:
        clean_aspect = chunk.text.strip().lower()
        if len(clean_aspect) > 2 and clean_aspect not in ["i", "he", "she", "it", "they", "this", "that"]:
            aspects.append(clean_aspect)
            
    for token in doc:
        if token.pos_ in ["NOUN", "PROPN"]:
            for child in token.children:
                if child.pos_ == "ADJ":
                    aspect_phrase = f"{child.text} {token.text}".lower()
                    if aspect_phrase not in aspects:
                        aspects.append(aspect_phrase)
    return list(dict.fromkeys(aspects))

@app.post("/api/analyze")
async def analyze_sentiment(payload: ReviewRequest):
    review_text = payload.review.strip()
    product = payload.product_name.strip()

    if not review_text:
        raise HTTPException(status_code=400, detail="Review text cannot be empty.")

    overall_res = sentiment_pipeline(review_text)[0]
    overall_sentiment = overall_res["label"].capitalize()
    overall_score = round(float(overall_res["score"]), 3)

    extracted_aspects = extract_aspects(review_text)
    
    aspect_results = []
    for aspect in extracted_aspects:
        res = sentiment_pipeline(aspect)[0]
        aspect_results.append({
            "aspect": aspect.capitalize(),
            "sentiment": res["label"].capitalize(),
            "confidence": round(float(res["score"]), 2)
        })

    email_sent = False
    # Send alert to store owner (you) automatically if review is negative
    if overall_sentiment.lower() == "negative":
        owner_email = os.getenv("MAIL_USERNAME")
        if owner_email:
            aspect_list_str = ", ".join([a["aspect"] for a in aspect_results]) or "None detected"
            html_content = f"""
            <h3>⚠️ Negative Review Alert!</h3>
            <p><strong>Product:</strong> {product}</p>
            <p><strong>Customer Review:</strong> "{review_text}"</p>
            <p><strong>Extracted Aspects:</strong> {aspect_list_str}</p>
            <p><strong>Confidence Score:</strong> {overall_score * 100}%</p>
            """
            try:
                message = MessageSchema(
                    subject=f"🚨 Negative Feedback Alert: {product}",
                    recipients=[owner_email],
                    body=html_content,
                    subtype=MessageType.html
                )
                fm = FastMail(conf)
                await fm.send_message(message)
                email_sent = True
            except Exception as e:
                print(f"Failed to send alert email: {e}")

    return {
        "product": product,
        "overall_sentiment": overall_sentiment,
        "overall_confidence": overall_score,
        "aspects_count": len(aspect_results),
        "aspects": aspect_results,
        "email_alert_sent": email_sent
    }

@app.post("/api/contact")
async def handle_contact_form(payload: ContactRequest):
    html_content = f"""
    <h3>💬 New Contact Form Submission</h3>
    <p><strong>Name:</strong> {payload.name}</p>
    <p><strong>Email:</strong> {payload.sender_email}</p>
    <p><strong>Message:</strong></p>
    <p>{payload.message}</p>
    """
    
    try:
        recipient = os.getenv("MAIL_USERNAME")
        if not recipient:
            raise Exception("MAIL_USERNAME environment variable not configured.")

        message = MessageSchema(
            subject=f"💬 New Website Message from {payload.name}",
            recipients=[recipient],
            body=html_content,
            subtype=MessageType.html
        )
        fm = FastMail(conf)
        await fm.send_message(message)
        return {"status": "success", "message": "Email sent successfully!"}
    except Exception as e:
        print(f"Failed to send contact email: {e}")
        raise HTTPException(status_code=500, detail="Failed to send email message.")
