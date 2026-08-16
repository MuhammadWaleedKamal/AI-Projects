import os
import pandas as pd
from urllib.parse import quote_plus
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from sqlalchemy import create_engine, inspect, text

class QueryDecision(BaseModel):
    is_ambiguous: bool = Field(
        description="True if the request lacks specific metrics or has multiple valid interpretations on the given schema."
    )
    clarification_question: Optional[str] = Field(
        default=None,
        description="Clarifying question explaining what criteria is required."
    )
    options: Optional[List[str]] = Field(
        default=None,
        description="2 to 4 concrete interpretation options for the user."
    )
    sql_query: Optional[str] = Field(
        default=None,
        description="Standard valid SQL query corresponding to the active dialect. Only populated if is_ambiguous is False."
    )
    reasoning: str = Field(
        description="Brief justification of the decision based on database schema."
    )

class UniversalClarificationEngine:
    def __init__(self, db_type: str = "sqlite", connection_params: Optional[Dict[str, Any]] = None, api_key: Optional[str] = None):
        self.db_type = db_type.lower()
        self.connection_params = connection_params or {}
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not provided.")
        
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = "gemini-3.5-flash-lite"
        self.engine = self._create_db_engine()

    def _create_db_engine(self):
        if self.db_type == "sqlite":
            db_path = self.connection_params.get("db_path", "ecommerce.db")
            return create_engine(f"sqlite:///{db_path}")
        elif self.db_type == "mysql":
            user = self.connection_params.get("user", "root")
            password = self.connection_params.get("password", "")
            host = self.connection_params.get("host", "localhost")
            port = self.connection_params.get("port", 3306)
            database = self.connection_params.get("database", "")
            
            safe_password = quote_plus(password)
            safe_user = quote_plus(user)
            
            uri = f"mysql+pymysql://{safe_user}:{safe_password}@{host}:{port}/{database}"
            is_local = host.lower() in ["localhost", "127.0.0.1"]
            
            if not is_local:
                return create_engine(
                    uri,
                    connect_args={
                        "ssl": {
                            "check_hostname": False,
                            "ssl_mode": "REQUIRED"
                        }
                    }
                )
            return create_engine(uri)
        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")

    def test_connection(self) -> tuple[bool, str]:
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True, "Connection successful"
        except Exception as e:
            return False, str(e)

    def get_database_schema(self, max_tables: int = 25, max_cols_per_table: int = 30) -> str:
        """
        Extracts schema while preventing token blowup on enterprise/massive databases.
        """
        try:
            inspector = inspect(self.engine)
            tables = inspector.get_table_names()
            if not tables:
                return "No tables found in the database."
            
            schema_text = f"Database Type: {self.db_type.upper()}\n"
            schema_text += f"Total Database Tables: {len(tables)}\n\n"
            
            # Guard against massive databases with 50+ tables
            displayed_tables = tables[:max_tables]
            
            for table_name in displayed_tables:
                schema_text += f"Table: {table_name}\nColumns:\n"
                columns = inspector.get_columns(table_name)
                pk_constraint = inspector.get_pk_constraint(table_name)
                pk_cols = pk_constraint.get("constrained_columns", []) if pk_constraint else []

                # Guard against wide tables with 50+ columns
                for col in columns[:max_cols_per_table]:
                    pk_tag = " (PRIMARY KEY)" if col["name"] in pk_cols else ""
                    schema_text += f"- {col['name']} ({col['type']}){pk_tag}\n"
                
                if len(columns) > max_cols_per_table:
                    schema_text += f"  ... and {len(columns) - max_cols_per_table} more columns\n"
                schema_text += "\n"
                
            if len(tables) > max_tables:
                schema_text += f"\n[Notice: Showing first {max_tables} out of {len(tables)} tables to optimize token context]\n"

            return schema_text
        except Exception as e:
            return f"Error extracting schema: {str(e)}"

    def execute_sql(self, sql_query: str, max_rows: int = 5000) -> Dict[str, Any]:
        """
        Executes query with safe memory limits (max_rows) to prevent browser/RAM crashes.
        """
        try:
            with self.engine.connect() as connection:
                # Stream results with chunksize or fetch limited rows
                result = connection.execute(text(sql_query))
                
                # Fetch only up to max_rows
                rows = result.fetchmany(max_rows)
                columns = result.keys()
                
                df = pd.DataFrame(rows, columns=columns)
                
                # Check if there was more data
                is_truncated = False
                if len(rows) == max_rows:
                    is_truncated = True

            return {
                "status": "success", 
                "df": df, 
                "row_count": len(df),
                "is_truncated": is_truncated
            }
        except Exception as e:
            return {"status": "error", "error_message": str(e)}

    def analyze_query(self, user_prompt: str, context: Optional[str] = None) -> QueryDecision:
        current_schema = self.get_database_schema()
        dialect_name = "MySQL" if self.db_type == "mysql" else "SQLite"

        system_instruction = f"""
You are an expert Database Architect and Query Disambiguation Engine.
Target SQL Dialect: {dialect_name}

Analyze the user's request against this schema:
{current_schema}

Rules:
1. Detect Ambiguity: If the query lacks clear business metrics (e.g. 'best customers', 'top items') or could map to multiple fields, set `is_ambiguous=True`. Provide `clarification_question` and 2-4 concrete `options`.
2. Generate Executable SQL: If unambiguous, set `is_ambiguous=False` and write a valid {dialect_name} SELECT query in `sql_query`.
3. Strict Safety: Never output markdown fences (```sql). Never generate mutating statements (INSERT, UPDATE, DELETE, DROP).
4. Dialect Specifics: Use syntax compatible with {dialect_name}.
5. Big Data Safety: When querying large transaction or log tables, default to an appropriate LIMIT (e.g., LIMIT 50 or LIMIT 100) unless an aggregation (SUM, AVG, COUNT) is requested.
6. Use User Clarification: If clarification choice is provided, resolve ambiguity strictly based on that selection.
"""
        full_prompt = f"User Request: {user_prompt}"
        if context:
            full_prompt += f"\nUser clarification selected: {context}"

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=full_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                response_schema=QueryDecision,
                temperature=0.1
            )
        )
        return QueryDecision.model_validate_json(response.text)

    def generate_direct_sql(self, user_prompt: str) -> Dict[str, Any]:
        current_schema = self.get_database_schema()
        dialect_name = "MySQL" if self.db_type == "mysql" else "SQLite"

        system_instruction = f"""
You are a standard Text-to-SQL converter.
Target Dialect: {dialect_name}
Schema:
{current_schema}

Rules:
1. Convert the user prompt directly into a valid {dialect_name} SELECT statement.
2. If ambiguous, make a default assumption.
3. Output ONLY raw SQL without markdown blocks.
"""
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=f"User Request: {user_prompt}",
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.1
            )
        )
        raw_query = response.text.strip().replace("```sql", "").replace("```", "").strip()
        exec_result = self.execute_sql(raw_query)
        return {
            "sql_query": raw_query,
            "status": exec_result["status"],
            "df": exec_result.get("df"),
            "row_count": exec_result.get("row_count", 0),
            "is_truncated": exec_result.get("is_truncated", False),
            "error_message": exec_result.get("error_message")
        }