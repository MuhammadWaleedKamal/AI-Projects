# ⚡ Universal Text-to-SQL Engine with Ambiguity Clarification Pipeline

An enterprise-ready, dual-mode **Text-to-SQL Disambiguation Engine** built with **Google Gemini (GenAI)**, **Pydantic**, **SQLAlchemy**, and **Streamlit**.

Unlike naive Text-to-SQL converters that make arbitrary assumptions on underspecified natural language queries, this system intercepts semantic ambiguity and dynamically presents interactive clarification options before generating dialect-specific SQL.

---

## 🛑 The Problem: The "Silent Hallucination" in Text-to-SQL

Standard LLM-powered Text-to-SQL pipelines operate on a dangerous assumption: **they assume every natural language request has a single, deterministic answer.**

In real-world business environments, most user queries are inherently ambiguous:
* Asking **"Show top customers"** could mean highest total spend, largest order volume, or highest loyalty tier.
* Asking **"Find active users"** could mean logged in recently, completed a transaction, or active account status.
* Asking **"Identify failing products"** could mean lowest sales, highest return rates, or poorest review ratings.

### Why Baseline Text-to-SQL Fails
1. **Silent Metric Assumption:** Baseline models guess a single metric without informing the user, returning plausible-looking SQL queries that answer the wrong business question.
2. **Costly Decision Making:** Non-technical business stakeholders unknowingly make decisions based on misaligned data.
3. **Loss of Trust in AI:** When stakeholders discover the discrepancy, confidence in self-service analytics drops completely.

---

## 💡 The Solution: Interactive Disambiguation & Guardrailed Execution

This engine replaces guesswork with an **Ambiguity-Aware Pipeline**:

* 🔍 **Proactive Ambiguity Interception:** The model inspects the database schema and detects when a query lacks clear business metrics before generating SQL.
* 🎯 **Structured User Disambiguation:** Instead of hallucinating criteria, it halts direct execution and returns 2–4 concrete, clickable interpretation options.
* 🛡️ **Dialect-Aware Safe Generation:** Once the user selects their exact intent, the engine generates strictly validated, read-only SQL for the target database dialect (SQLite / MySQL).
* ⚖️ **Side-by-Side Verification:** Includes a benchmark mode allowing users to compare the engine's precision directly against standard naive LLM generation.

## 🏛️ System Architecture

<img width="200" height="320" alt="Architecture_Diagram" src="https://github.com/user-attachments/assets/3591bd1b-672d-4396-9a31-cae9a15523ad" />

---

## 🌟 Core Features

- **Interactive Disambiguation Pipeline:** Powered by Gemini Structured Outputs (`QueryDecision` schema) to detect underspecified business logic (e.g., *top customers*, *churn risk*, *slow-moving inventory*).
- **Dual-Pipeline Benchmarking:** Side-by-side comparison between **With Clarification Engine** vs. **Baseline (Direct Assumption)**.
- **Universal Multi-Database Engine:**
  - **SQLite:** Built-in default e-commerce database & custom `.db` file upload.
  - **Live Cloud MySQL:** Full SSL/TLS authentication support for cloud databases (Aiven, TiDB Cloud).
- **Production Guardrails:**
  - **Schema Token Optimization:** Prunes wide/massive schemas to prevent LLM context overflows.
  - **OOM Memory Protection:** Safe batch fetching (`fetchmany`) to prevent browser crashes on large result sets.
  - **SQL Injection & Mutation Guard:** Enforces read-only `SELECT` queries.

---

## 📊 Disambiguation Benchmark Queries

The engine was evaluated on 20 standard ambiguous enterprise queries:

| ID | Natural Language Query | Ambiguity Factor / Conflict |
|---|---|---|
| 01 | *Show top customers.* | Total spend vs. Order count vs. Loyalty tier |
| 02 | *Find active users.* | Recent login vs. Placed orders vs. Account status |
| 03 | *Items needing restock.* | Reorder threshold vs. Low stock units |
| 04 | *Get popular products.* | Highest sales volume vs. Highest ratings |
| 05 | *Show recent transactions.* | Last 7 days vs. Last 30 days vs. Top 10 latest |
| 06 | *Find VIP clients.* | Tier classification vs. Lifetime value (LTV) |
| 07 | *List high value orders.* | Order total threshold vs. Quantity threshold |
| 08 | *Identify failing products.* | High returns vs. Low conversion vs. Poor rating |
| 09 | *Best cities for business.* | Revenue volume vs. Total customer count |
| 10 | *Loyal customers in Karachi.* | Tenure length vs. Frequency of purchases |
| ... | *10 additional evaluation cases* | *See benchmark report sheet* |

[SQL Query Report.xlsx](https://github.com/user-attachments/files/31195818/SQL.Query.Report.xlsx)

---

## 📊 Performance & Benchmark Summary (20 Test Cases)

| Evaluation Metric | Baseline (Without Clarification) | With Clarification Engine | Improvement |
| :--- | :---: | :---: | :---: |
| **Intent Disambiguation Rate** | 0% *(Silent Guess)* | **100%** *(Explicitly Resolved)* | **+100%** |
| **Business Logic Accuracy** | 25% | **95%** | **+70%** |
| **Silent Metric Hallucinations** | 75% | **0%** | **-75% (Eliminated)** |
| **SQL Execution Success (Dialect)** | 60% | **100%** | **+40%** |

## 🛠️ Tech Stack

- **LLM / GenAI:** Google Gemini API (`gemini-3.5-flash-lite`)
- **Structured Validation:** Pydantic v2
- **Database Layer:** SQLAlchemy 2.0, PyMySQL, Cryptography
- **UI & Deployment:** Streamlit Community Cloud + UptimeRobot Keep-Alive

---

## 🚀 Getting Started

### 1. Clone Repository
```bash
git clone [https://github.com/MuhammadWaleedKamal/AI-Projects.git](https://github.com/MuhammadWaleedKamal/AI-Projects.git)
cd "LLM_and_Generative_AI/2_Text_to_SQL_with_Clarification_Engine"
```

### 2. Install Dependencies
```bash
pip install -r frontend/requirements.txt
```

### 3. Setup Environment Variables

Create a .env file in the project folder:

Ini, TOML
```bash
GEMINI_API_KEY="your_google_gemini_api_key"
```

### 4. Run Application
```bash
streamlit run frontend/app.py
```
