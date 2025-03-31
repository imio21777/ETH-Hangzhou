import sqlite3
from typing import Dict, Any, Tuple, Optional, List
import os
from base_agent import BaseAgent

class Text2SQLAgent(BaseAgent):
    def __init__(self, name: str = "Text2SQLAgent", llm_model: str = None):
        super().__init__(name, llm_model)
        self.db_path = self.config.get('DB_PATH', 'blockchain_data.db')

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert natural language query to SQL and execute it.

        Args:
            input_data: Dictionary containing the query from user

        Returns:
            Dictionary with query results or error message
        """
        user_query = input_data.get("query", "")
        if not user_query:
            return {"status": "error", "message": "No query provided"}

        # Get table schema and sample data for context
        schema_data = self._get_db_schema()

        # Convert user query to SQL
        sql_query = self._convert_to_sql(user_query, schema_data)

        if not sql_query:
            return {
                "status": "error",
                "message": "Failed to convert query to SQL"
            }

        # Execute the SQL query
        try:
            results = self._execute_sql(sql_query)
            return {
                "status": "success",
                "sql_query": sql_query,
                "results": results
            }
        except Exception as e:
            # Try to fix the SQL query if execution failed
            fixed_sql = self._fix_sql_query(sql_query, str(e))
            if fixed_sql and fixed_sql != sql_query:
                try:
                    results = self._execute_sql(fixed_sql)
                    return {
                        "status": "success",
                        "sql_query": fixed_sql,
                        "original_query": sql_query,
                        "results": results
                    }
                except Exception as e2:
                    return {
                        "status": "error",
                        "sql_query": sql_query,
                        "fixed_sql": fixed_sql,
                        "message": f"Error executing SQL: {str(e2)}"
                    }
            return {
                "status": "error",
                "sql_query": sql_query,
                "message": f"Error executing SQL: {str(e)}"
            }

    def _get_db_schema(self) -> Dict[str, Any]:
        """Get database schema and sample data for providing context"""
        conn = None
        schema_data = {"tables": [], "sample_data": {}}

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Get list of tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            schema_data["tables"] = tables

            # Get schema and sample data for each table
            for table in tables:
                # Get table schema
                cursor.execute(f"PRAGMA table_info({table});")
                columns = [{"name": row[1], "type": row[2]} for row in cursor.fetchall()]

                # Get sample data (first 4 rows)
                try:
                    cursor.execute(f"SELECT * FROM {table} LIMIT 4;")
                    rows = cursor.fetchall()

                    if rows:
                        # Get column names
                        column_names = [description[0] for description in cursor.description]

                        # Format sample data
                        sample_data = []
                        for row in rows:
                            sample_row = {}
                            for i, col in enumerate(column_names):
                                sample_row[col] = row[i]
                            sample_data.append(sample_row)

                        schema_data["sample_data"][table] = {
                            "columns": column_names,
                            "rows": sample_data
                        }
                except Exception as e:
                    print(f"Error getting sample data for table {table}: {str(e)}")

        except Exception as e:
            print(f"Error getting database schema: {str(e)}")
        finally:
            if conn:
                conn.close()

        return schema_data

    def _convert_to_sql(self, user_query: str, schema_data: Dict[str, Any]) -> Optional[str]:
        """Convert user natural language query to SQL using LLM"""
        # Prepare sample data to show the LLM
        sample_data_text = ""
        for table_name, data in schema_data.get("sample_data", {}).items():
            sample_data_text += f"\nTable: {table_name}\n"

            if "columns" in data and "rows" in data:
                columns = data["columns"]
                rows = data["rows"]

                # Format column headers
                header = " | ".join(columns)
                sample_data_text += f"{header}\n"
                sample_data_text += "-" * len(header) + "\n"

                # Format rows
                for row in rows:
                    row_values = []
                    for col in columns:
                        row_values.append(str(row.get(col, "")))
                    sample_data_text += " | ".join(row_values) + "\n"

        # Construct the prompt
        prompt = f"""Below is a sample of the data you need to query, showing only the first 4 rows to help you understand the schema.

{sample_data_text}

Below is the user's request. You need to convert this request into an SQL query. Your SQL query must strictly follow the table format and field names shown above, otherwise it won't run. You should fuzzy match the user's query. We're using SQLite.

{user_query}

Please wrap your SQL query in <sql></sql> tags. If you can't create the SQL command, explain why within <reason></reason> tags.
"""

        # Use LLM to generate SQL
        response = self.call_llm(prompt)

        # Extract SQL from response
        sql_query = None
        if "<sql>" in response and "</sql>" in response:
            start = response.find("<sql>") + len("<sql>")
            end = response.find("</sql>")
            sql_query = response[start:end].strip()

        return sql_query

    def _fix_sql_query(self, sql_query: str, error_message: str) -> Optional[str]:
        """Try to fix SQL query that failed to execute"""
        prompt = f"""The SQL command below produced the following error:

{error_message}

Please correct the SQL command and wrap it in <sql></sql> tags. If you can't fix it, explain why within <reason></reason> tags.

Original SQL command:
{sql_query}
"""

        response = self.call_llm(prompt)

        # Extract fixed SQL from response
        fixed_sql = None
        if "<sql>" in response and "</sql>" in response:
            start = response.find("<sql>") + len("<sql>")
            end = response.find("</sql>")
            fixed_sql = response[start:end].strip()

        return fixed_sql

    def _execute_sql(self, sql_query: str) -> List[Dict[str, Any]]:
        """Execute SQL query and return results as a list of dictionaries"""
        conn = None
        results = []

        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # This enables column access by name
            cursor = conn.cursor()

            cursor.execute(sql_query)
            rows = cursor.fetchall()

            # Convert rows to dictionaries
            for row in rows:
                results.append({key: row[key] for key in row.keys()})

        except Exception as e:
            raise e
        finally:
            if conn:
                conn.close()

        return results