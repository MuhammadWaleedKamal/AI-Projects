import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

import os
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import inspect
from beckend.clarification_engine import UniversalClarificationEngine

load_dotenv(ROOT_DIR / ".env")

API_KEY = None
try:
    if "GEMINI_API_KEY" in st.secrets:
        API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    pass

if not API_KEY:
    API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    st.error("⚠️ GEMINI_API_KEY nahi mili! Apni `.env` file mein check karein.")
    st.stop()

st.set_page_config(
    page_title="Universal Text-to-SQL Comparison Hub",
    page_icon="⚡",
    layout="wide"
)

st.markdown("""
<style>
    .stChatFloatingInputContainer { bottom: 20px; }
    div[data-testid="stExpander"] { border-radius: 8px; border: 1px solid #e0e0e0; }
    .badge-clarify { background-color: #e6f4ea; color: #137333; padding: 4px 8px; border-radius: 4px; font-weight: bold; }
    .badge-baseline { background-color: #fce8e6; color: #c5221f; padding: 4px 8px; border-radius: 4px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# Session States
if "messages" not in st.session_state:
    st.session_state.messages = []
if "active_ambiguity" not in st.session_state:
    st.session_state.active_ambiguity = None
if "db_type" not in st.session_state:
    st.session_state.db_type = "sqlite"
if "conn_params" not in st.session_state:
    st.session_state.conn_params = {"db_path": "ecommerce.db"}
if "engine_mode" not in st.session_state:
    st.session_state.engine_mode = "With Clarification Engine"


# Sidebar: Database & Engine Mode Configuration
with st.sidebar:
    st.header("⚙️ Engine Mode")
    st.session_state.engine_mode = st.radio(
        "Select Pipeline Architecture:",
        ["With Clarification Engine", "Baseline (Without Clarification)"]
    )
    
    st.markdown("---")
    st.header("🗄️ Database Connection")
    
    db_choice = st.radio("Select Database Engine:", ["SQLite (File / Demo)", "MySQL (Live Server)"])
    
    if db_choice == "SQLite (File / Demo)":
        st.session_state.db_type = "sqlite"
        sqlite_source = st.radio("SQLite Source:", ["Default Demo DB", "Upload Custom SQLite (.db)"])
        
        if sqlite_source == "Default Demo DB":
            st.session_state.conn_params = {"db_path": "ecommerce.db"}
        else:
            uploaded_file = st.file_uploader("Upload SQLite Database (.db, .sqlite)", type=["db", "sqlite", "sqlite3"])
            if uploaded_file is not None:
                os.makedirs("uploaded_dbs", exist_ok=True)
                custom_path = os.path.join("uploaded_dbs", uploaded_file.name)
                with open(custom_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.session_state.conn_params = {"db_path": custom_path}
                st.success(f"Loaded: `{uploaded_file.name}`")

    else:
        st.session_state.db_type = "mysql"
        st.markdown("**MySQL Server Credentials**")
        host = st.text_input("Host", value="localhost")
        port = st.number_input("Port", value=3306, step=1)
        user = st.text_input("User", value="root")
        password = st.text_input("Password", type="password", value="")
        database = st.text_input("Database Name", value="")
        
        if st.button("Connect to MySQL"):
            st.session_state.conn_params = {
                "host": host,
                "port": port,
                "user": user,
                "password": password,
                "database": database
            }
            test_engine = UniversalClarificationEngine(
                db_type="mysql", 
                connection_params=st.session_state.conn_params, 
                api_key=API_KEY
            )
            success, msg = test_engine.test_connection()
            if success:
                st.success("Connected to MySQL Server successfully!")
            else:
                st.error(f"Connection Failed: {msg}")

    st.markdown("---")
    st.subheader("📊 Active DB Preview")
    
    try:
        engine_instance = UniversalClarificationEngine(
            db_type=st.session_state.db_type,
            connection_params=st.session_state.conn_params,
            api_key=API_KEY
        )
        inspector = inspect(engine_instance.engine)
        table_names = inspector.get_table_names()
        
        if table_names:
            st.info(f"**Engine:** `{st.session_state.db_type.upper()}` | **Tables:** {len(table_names)}")
            selected_table = st.selectbox("Preview Table:", table_names)
            if selected_table:
                preview_res = engine_instance.execute_sql(f"SELECT * FROM {selected_table} LIMIT 5")
                if preview_res["status"] == "success":
                    st.dataframe(preview_res["df"], hide_index=True)
        else:
            st.warning("No tables found in active database.")
    except Exception:
        st.warning("Database not connected yet.")

    st.markdown("---")
    if st.button("Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.active_ambiguity = None
        st.rerun()

# Main Chat UI
st.title("⚡ Universal Text-to-SQL Engine")

mode_badge = "🟢 Clarification Active" if st.session_state.engine_mode == "With Clarification Engine" else "🔴 Baseline Direct Execution"
st.caption(f"Mode: **{mode_badge}** | DB: **`{st.session_state.db_type.upper()}`**")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message.get("content"):
            st.markdown(message["content"])
        
        if message.get("type") == "clarification":
            st.info(f"**Clarification Required:** {message['question']}")
            if message.get("resolved_choice"):
                st.success(f"**Selected Option:** {message['resolved_choice']}")

        if message.get("type") == "sql_result":
            with st.expander("🔍 View Generated SQL Query", expanded=False):
                st.code(message["sql_query"], language="sql")
            
            if message["status"] == "success":
                df = message["df"]
                st.markdown(f"**Returned `{len(df)}` rows:**")
                
                # Large Data Warning Banner
                if message.get("is_truncated"):
                    st.warning("⚠️ **Large Dataset Safeguard:** Query output was capped at 5,000 rows to preserve UI responsiveness.")
                    
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.error(f"SQL Error: {message['error_message']}")

# Ambiguity Option Buttons
if st.session_state.active_ambiguity and st.session_state.engine_mode == "With Clarification Engine":
    ambiguity = st.session_state.active_ambiguity
    st.markdown(f"👉 **{ambiguity['question']}**")
    
    cols = st.columns(len(ambiguity["options"]))
    for i, option in enumerate(ambiguity["options"]):
        if cols[i].button(option, key=f"clarify_btn_{i}", use_container_width=True):
            engine = UniversalClarificationEngine(
                db_type=st.session_state.db_type,
                connection_params=st.session_state.conn_params,
                api_key=API_KEY
            )
            original_query = ambiguity["original_query"]
            
            for msg in reversed(st.session_state.messages):
                if msg.get("type") == "clarification" and not msg.get("resolved_choice"):
                    msg["resolved_choice"] = option
                    break
            
            with st.spinner("Generating dialect-specific SQL..."):
                decision = engine.analyze_query(
                    user_prompt=original_query,
                    context=f"The user specifically clarified: '{option}'"
                )
                
                if not decision.is_ambiguous and decision.sql_query:
                    exec_result = engine.execute_sql(decision.sql_query)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "type": "sql_result",
                        "content": f"**Refined Logic:** {decision.reasoning}",
                        "sql_query": decision.sql_query,
                        "status": exec_result["status"],
                        "df": exec_result.get("df"),
                        "error_message": exec_result.get("error_message")
                    })
                
            st.session_state.active_ambiguity = None
            st.rerun()

# User Input Processing
user_input = st.chat_input("Ask any question about your active database...")

if user_input:
    st.session_state.active_ambiguity = None
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        engine = UniversalClarificationEngine(
            db_type=st.session_state.db_type,
            connection_params=st.session_state.conn_params,
            api_key=API_KEY
        )
        
        # Pipeline Branching based on Engine Mode
        if st.session_state.engine_mode == "Baseline (Without Clarification)":
            with st.spinner("Generating direct baseline SQL (no disambiguation)..."):
                result = engine.generate_direct_sql(user_input)
                st.session_state.messages.append({
                    "role": "assistant",
                    "type": "sql_result",
                    "content": "⚠️ **Baseline Mode (No Disambiguation):** Direct query generated based on assumptions.",
                    "sql_query": result["sql_query"],
                    "status": result["status"],
                    "df": result.get("df"),
                    "error_message": result.get("error_message")
                })
                st.rerun()
        else:
            with st.spinner("Inspecting schema & evaluating ambiguity..."):
                decision = engine.analyze_query(user_input)
                
                if decision.is_ambiguous:
                    st.session_state.messages.append({
                        "role": "assistant",
                        "type": "clarification",
                        "content": f"**Intent Ambiguity Detected:** {decision.reasoning}",
                        "question": decision.clarification_question,
                        "options": decision.options,
                        "resolved_choice": None
                    })
                    st.session_state.active_ambiguity = {
                        "original_query": user_input,
                        "question": decision.clarification_question,
                        "options": decision.options
                    }
                    st.rerun()
                else:
                    exec_result = engine.execute_sql(decision.sql_query)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "type": "sql_result",
                        "content": f"**Execution Plan:** {decision.reasoning}",
                        "sql_query": decision.sql_query,
                        "status": exec_result["status"],
                        "df": exec_result.get("df"),
                        "error_message": exec_result.get("error_message")
                    })
                    st.rerun()