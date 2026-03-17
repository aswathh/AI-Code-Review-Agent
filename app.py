
# Streamlit UI for AI Code Review Agent


import streamlit as st
import os
import sys
import time
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))
from agent import detect_bugs, check_security, generate_tests, generate_docs

# ---- Page Config ----
st.set_page_config(
    page_title="AI Code Review Agent",
    page_icon="🤖",
    layout="wide"
)

# ---- Sidebar ----
with st.sidebar:
    st.title(" Settings")

    language = st.selectbox(
        "Programming Language",
        ["Python", "JavaScript", "Java", "TypeScript", "C++"],
        index=0
    )

    st.divider()
    st.markdown("###  Select Tools")
    do_bugs = st.checkbox(" Bug Detection",       value=True)
    do_sec  = st.checkbox(" Security Analysis",   value=True)
    do_test = st.checkbox(" Generate Unit Tests", value=True)
    do_docs = st.checkbox(" Generate Docs",       value=True)

    st.divider()

    if os.getenv("GROQ_API_KEY"):
        st.success(" API Key found!")
    else:
        st.error(" GROQ_API_KEY missing!")
        st.code("Add to .env:\nGROQ_API_KEY=gsk_your_key")

    st.divider()
    st.markdown("**How it works:**")
    st.markdown("""
```
Code Input
    ↓
Bug Detector
    ↓
Security Checker
    ↓
Test Generator
    ↓
Doc Generator
    ↓
Full Report
```
    """)

# ---- Main ----
st.title(" AI Code Review Agent")
st.caption("Paste code → 4 AI tools analyze it → Get full review report")

# Sample code button
if st.button(" Load Sample Code"):
    st.session_state["code"] = """\
import sqlite3

def get_user(username, password):
    conn   = sqlite3.connect('users.db')
    cursor = conn.cursor()
    # Bug: SQL Injection!
    query  = "SELECT * FROM users WHERE username = '" + username + "'"
    cursor.execute(query)
    user   = cursor.fetchone()
    if user and user[2] == password:
        return user
    return None

def calculate_average(numbers):
    total = 0
    for n in numbers:
        total += n
    # Bug: ZeroDivisionError if list is empty!
    return total / len(numbers)

def save_config():
    # Bug: Hardcoded secret!
    api_key = "sk-secret123456789"
    with open('config.txt', 'w') as f:
        f.write(api_key)
"""

if "code" not in st.session_state:
    st.session_state["code"] = ""

code = st.text_area(
    " Paste your code here:",
    value=st.session_state["code"],
    height=280,
    placeholder="Paste Python, JavaScript, Java or any code here..."
)
st.session_state["code"] = code

col1, col2, col3 = st.columns([2, 1, 2])
with col2:
    run = st.button(" Review Code", type="primary", use_container_width=True)

# ---- Run Agent ----
if run:
    if not code.strip():
        st.error("Please paste some code first!")
        st.stop()
    if not any([do_bugs, do_sec, do_test, do_docs]):
        st.error("Select at least one tool!")
        st.stop()
    if not os.getenv("GROQ_API_KEY"):
        st.error("GROQ_API_KEY missing! Add to .env file.")
        st.stop()

    results = {}
    elapsed = 0
    total   = sum([do_bugs, do_sec, do_test, do_docs])
    done    = 0
    bar     = st.progress(0)
    status  = st.empty()
    start   = time.time()

    try:
        if do_bugs:
            status.text(" Running Bug Detection...")
            results[" Bugs"]     = detect_bugs(code, language)
            done += 1; bar.progress(done / total)

        if do_sec:
            status.text(" Running Security Analysis...")
            results[" Security"] = check_security(code, language)
            done += 1; bar.progress(done / total)

        if do_test:
            status.text(" Generating Unit Tests...")
            results["Tests"]    = generate_tests(code, language)
            done += 1; bar.progress(done / total)

        if do_docs:
            status.text(" Generating Documentation...")
            results[" Docs"]     = generate_docs(code, language)
            done += 1; bar.progress(done / total)

        elapsed = round(time.time() - start, 1)
        bar.progress(1.0)
        status.text(f" Done in {elapsed}s!")

    except Exception as e:
        st.error(f"Error: {e}")
        st.info("Check your GROQ_API_KEY in .env file")
        st.stop()

    # Results
    st.markdown(f"### Complete — {len(results)} tools ran in {elapsed}s")
    tabs = st.tabs(list(results.keys()))
    for tab, (name, content) in zip(tabs, results.items()):
        with tab:
            st.markdown(content)
            st.download_button(
                f"⬇ Download",
                content,
                f"{name.split()[1].lower()}_report.md",
                key=f"dl_{name}"
            )

    st.markdown("---")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Tools Run",  len(results))
    c2.metric("Language",   language)
    c3.metric("Lines",      len(code.split("\n")))
    c4.metric("Time",       f"{elapsed}s")

# Empty state
if not run:
    st.info(" Click 'Load Sample Code' then ' Review Code' to see a demo!")
    st.markdown("""
    **What you get:**
    -  List of all bugs with severity and fixes
    -  Security vulnerabilities with risk levels
    -  Complete runnable unit tests
    -  Professional documentation
    """)
