import streamlit as st
import os, time
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

def get_llm():
    return ChatGroq(
        groq_api_key=os.environ["GROQ_API_KEY"],
        model_name="llama-3.3-70b-versatile",
        temperature=0.1,
        max_tokens=2048
    )

def run_tool(sys_msg, human_msg, code, language):
    prompt = ChatPromptTemplate.from_messages([
        ("system", sys_msg),
        ("human", human_msg)
    ])
    return (prompt | get_llm() | StrOutputParser()).invoke({"language": language, "code": code})

st.set_page_config(page_title="AI Code Review Agent", layout="centered")
st.title("AI Code Review Agent")

language = st.selectbox("Language", ["Python", "JavaScript", "Java", "TypeScript", "C++"])
code     = st.text_area("Paste your code:", height=250)

col1, col2, col3, col4 = st.columns(4)
do_bugs = col1.checkbox("Bugs",     value=True)
do_sec  = col2.checkbox("Security", value=True)
do_test = col3.checkbox("Tests",    value=True)
do_docs = col4.checkbox("Docs",     value=True)

if st.button("Review Code", type="primary", use_container_width=True):
    if not code.strip():
        st.error("Paste some code first!")
        st.stop()

    results = {}
    tools   = sum([do_bugs, do_sec, do_test, do_docs])
    done    = 0
    bar     = st.progress(0)
    status  = st.empty()
    start   = time.time()

    if do_bugs:
        status.text("Running Bug Detection...")
        results["Bugs"] = run_tool(
            "Find ALL bugs. For each: number, description, severity, fix.",
            "Find bugs in {language}:\n{code}",
            code, language
        )
        done += 1; bar.progress(done / tools)

    if do_sec:
        status.text("Running Security Analysis...")
        results["Security"] = run_tool(
            "Find ALL security issues. For each: name, risk, impact, fix.",
            "Security audit {language}:\n{code}",
            code, language
        )
        done += 1; bar.progress(done / tools)

    if do_test:
        status.text("Generating Unit Tests...")
        results["Tests"] = run_tool(
            "Write complete pytest unit tests. Cover normal, edge, error cases.",
            "Write tests for {language}:\n{code}",
            code, language
        )
        done += 1; bar.progress(done / tools)

    if do_docs:
        status.text("Generating Documentation...")
        results["Docs"] = run_tool(
            "Write professional docs: overview, functions, params, returns, usage.",
            "Document {language}:\n{code}",
            code, language
        )
        done += 1; bar.progress(done / tools)

    elapsed = round(time.time() - start, 1)
    status.text(f"Done in {elapsed}s!")

    for tab, (name, content) in zip(st.tabs(list(results.keys())), results.items()):
        with tab:
            st.markdown(content)
            st.download_button("Download", content, f"{name}_report.md", key=name)