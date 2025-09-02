"""Simple AI tutor stub."""
import os

API_KEY = os.getenv("OPENAI_API_KEY")

def generate_hint(query: str, schema: str) -> str:
    # Placeholder implementation
    return f"Consider the columns available: {schema}. Review your WHERE clause."

def explain_solution(query: str, expected_output: str) -> str:
    # Placeholder implementation
    return (
        "The query works by selecting records that match the criteria. "
        "Ensure joins are using appropriate keys."
    )
