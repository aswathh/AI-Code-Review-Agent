import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

LLM_MODEL = "llama-3.3-70b-versatile"

def get_llm():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found! Add to .env: GROQ_API_KEY=gsk_your_key")
    return ChatGroq(groq_api_key=api_key, model_name=LLM_MODEL, temperature=0.1, max_tokens=2048)

def detect_bugs(code: str, language: str = "Python") -> str:
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert code reviewer. Find ALL bugs. "
         "For each: number, description, line, severity (CRITICAL/HIGH/MEDIUM/LOW), fix. "
         "If no bugs: say No bugs found."),
        ("human", "Find bugs in this {language} code:\n```{language}\n{code}\n```")
    ])
    return (prompt | get_llm() | StrOutputParser()).invoke({"language": language, "code": code})

def check_security(code: str, language: str = "Python") -> str:
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a cybersecurity expert. Find ALL security issues. "
         "For each: name, risk level, what attacker can do, secure fix. "
         "If no issues: say No security issues found."),
        ("human", "Security audit this {language} code:\n```{language}\n{code}\n```")
    ])
    return (prompt | get_llm() | StrOutputParser()).invoke({"language": language, "code": code})

def generate_tests(code: str, language: str = "Python") -> str:
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a senior software engineer. "
         "Write complete runnable pytest unit tests. "
         "Cover: normal, edge, and error cases. Real code only."),
        ("human", "Write unit tests for this {language} code:\n```{language}\n{code}\n```")
    ])
    return (prompt | get_llm() | StrOutputParser()).invoke({"language": language, "code": code})

def generate_docs(code: str, language: str = "Python") -> str:
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a technical writer. Write professional documentation: "
         "overview, functions with params/returns/examples, dependencies, usage."),
        ("human", "Document this {language} code:\n```{language}\n{code}\n```")
    ])
    return (prompt | get_llm() | StrOutputParser()).invoke({"language": language, "code": code})

def run_agent(
    code: str,
    language: str = "Python",
    run_bugs: bool = True,
    run_security: bool = True,
    run_tests: bool = True,
    run_docs: bool = True
) -> dict:
    results = {}
    if run_bugs:     results["bugs"]          = detect_bugs(code, language)
    if run_security: results["security"]      = check_security(code, language)
    if run_tests:    results["tests"]         = generate_tests(code, language)
    if run_docs:     results["documentation"] = generate_docs(code, language)
    return results