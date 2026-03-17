
# AI Code Review Agent Core Logic


import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

LLM_MODEL = "llama-3.3-70b-versatile"


def get_llm():
    """Returns Groq LLM instance (FREE)."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not found!\n"
            "Add to .env: GROQ_API_KEY=gsk_your_key\n"
            "Get free key at groq.com"
        )
    return ChatGroq(
        groq_api_key=api_key,
        model_name=LLM_MODEL,
        temperature=0.1,
        max_tokens=2048
    )


def detect_bugs(code: str, language: str = "Python") -> str:
    """Tool 1: Find bugs in code."""
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are an expert code reviewer. "
         "Find ALL bugs in the code. "
         "For each bug: number, description, line, "
         "severity (CRITICAL/HIGH/MEDIUM/LOW), and fix. "
         "If no bugs found say: No bugs found."),
        ("human", "Find bugs in this {language} code:\n```{language}\n{code}\n```")
    ])
    return (prompt | get_llm() | StrOutputParser()).invoke(
        {"language": language, "code": code}
    )


def check_security(code: str, language: str = "Python") -> str:
    """Tool 2: Find security vulnerabilities."""
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are a cybersecurity expert. "
         "Find ALL security issues: SQL injection, hardcoded passwords, "
         "missing validation, insecure storage, etc. "
         "For each: name, risk level, what attacker can do, secure fix. "
         "If no issues found say: No security issues found."),
        ("human", "Security audit this {language} code:\n```{language}\n{code}\n```")
    ])
    return (prompt | get_llm() | StrOutputParser()).invoke(
        {"language": language, "code": code}
    )


def generate_tests(code: str, language: str = "Python") -> str:
    """Tool 3: Generate unit tests."""
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are a senior software engineer. "
         "Write complete runnable unit tests using pytest for Python. "
         "Cover: normal cases, edge cases, error cases. "
         "Write real runnable code only — no pseudocode."),
        ("human", "Write unit tests for this {language} code:\n```{language}\n{code}\n```")
    ])
    return (prompt | get_llm() | StrOutputParser()).invoke(
        {"language": language, "code": code}
    )


def generate_docs(code: str, language: str = "Python") -> str:
    """Tool 4: Generate documentation."""
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are a technical writer. "
         "Write professional documentation including: "
         "overview, each function with parameters/return/examples, "
         "dependencies, and usage example."),
        ("human", "Document this {language} code:\n```{language}\n{code}\n```")
    ])
    return (prompt | get_llm() | StrOutputParser()).invoke(
        {"language": language, "code": code}
    )


def run_agent(
    code: str,
    language: str = "Python",
    run_bugs: bool = True,
    run_security: bool = True,
    run_tests: bool = True,
    run_docs: bool = True
) -> dict:
    """Run all selected tools and return results."""
    results = {}
    if run_bugs:
        results["bugs"]          = detect_bugs(code, language)
    if run_security:
        results["security"]      = check_security(code, language)
    if run_tests:
        results["tests"]         = generate_tests(code, language)
    if run_docs:
        results["documentation"] = generate_docs(code, language)
    return results


# Quick test
if __name__ == "__main__":
    sample = """
def divide(a, b):
    return a / b

def get_user(username):
    import sqlite3
    conn   = sqlite3.connect('db.sqlite')
    cursor = conn.cursor()
    query  = "SELECT * FROM users WHERE name = '" + username + "'"
    cursor.execute(query)
    return cursor.fetchone()
"""
    print("Running agent on sample code...\n")
    results = run_agent(sample, "Python")
    for tool, result in results.items():
        print(f"\n{'='*50}\n{tool.upper()}\n{'='*50}")
        print(result)
