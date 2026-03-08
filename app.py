import streamlit as st
from dotenv import load_dotenv

from src.config import Settings
from src.embed_local import embed_text
from src.query import retrieve, filter_hits_by_query, format_sources_markdown, build_prompt
from src.llm_generate import generate_answer

load_dotenv()


def main():
    st.set_page_config(page_title="Ops Copilot", page_icon="🛠️", layout="wide")

    settings = Settings.from_env()

    st.title("🛠️ Ops Copilot")
    st.caption("Local RAG (FAISS) + Ollama/Bedrock (answers)")

    with st.sidebar:
        st.header("Settings")
        st.write("Loaded from `.env` (restart app after changes).")
        st.code(settings.safe_dump(), language="yaml")
        st.divider()
        debug = st.checkbox("Show debug (prompt, raw hits)", value=False)
        top_k = st.slider("Top-K retrieval", 1, 10, settings.top_k)

    question = st.text_input(
        "Ask a question about your runbooks:",
        placeholder="e.g., What should I check when RDS CPU spikes above 80%?",
    )
    ask = st.button("Ask", type="primary", disabled=not question.strip())

    if not ask:
        return

    with st.spinner("Embedding + retrieving…"):
        q_emb = embed_text(question, model_name=settings.embed_model)
        hits, conf = retrieve(question, q_emb, index_dir=settings.index_dir, top_k=top_k)
        hits = filter_hits_by_query(question, hits)

    st.subheader("Answer")
    st.metric("Confidence", f"{conf}/100")

    prompt, context_used = build_prompt(question, hits, max_context_chars=settings.max_context_chars)

    with st.spinner("Generating answer…"):
        answer = generate_answer(prompt=prompt, hits=hits, provider=settings.llm_provider, settings_override=settings)

    st.write(answer)

    with st.expander("Retrieved context"):
        st.markdown(format_sources_markdown(hits))

    if debug:
        with st.expander("Debug: prompt"):
            st.code(prompt, language="text")
        with st.expander("Debug: context length"):
            st.write(f"{len(context_used)} chars used")


if __name__ == "__main__":
    main()
