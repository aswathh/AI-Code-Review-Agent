import streamlit as st
import time
from agent import run_agent

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

    bar    = st.progress(0)
    status = st.empty()
    start  = time.time()

    status.text("Running analysis...")
    results = run_agent(
        code       = code,
        language   = language,
        run_bugs   = do_bugs,
        run_security = do_sec,
        run_tests  = do_test,
        run_docs   = do_docs
    )
    bar.progress(1.0)

    elapsed = round(time.time() - start, 1)
    status.text(f"Done in {elapsed}s!")

    for tab, (name, content) in zip(st.tabs(list(results.keys())), results.items()):
        with tab:
            st.markdown(content)
            st.download_button("Download", content, f"{name}_report.md", key=name)