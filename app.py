# app.py
import os
import json
import streamlit as st
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
DEFAULT_KB_ID = os.getenv("KB_ID", "")
DEFAULT_MODEL_ID = os.getenv("MODEL_ID", "amazon.nova-lite-v1:0")  # can be model id OR full ARN

st.set_page_config(page_title="Ops Copilot", page_icon="🛠️", layout="centered")

st.title("Ops Copilot — AI Runbook Assistant")
st.caption("Ask DevOps incident questions grounded in your runbooks via Amazon Bedrock Knowledge Bases.")

with st.sidebar:
    st.header("Configuration")
    aws_region = st.text_input("AWS Region", value=AWS_REGION)
    kb_id = st.text_input("Knowledge Base ID (KB_ID)", value=DEFAULT_KB_ID, placeholder="e.g., KBNNNNNNNN")
    model_id_or_arn = st.text_input(
        "Model ID or ARN (MODEL_ID)",
        value=DEFAULT_MODEL_ID,
        help="Example model id: amazon.nova-lite-v1:0  |  Or full ARN: arn:aws:bedrock:us-east-1::foundation-model/..."
    )
    max_results = st.slider("Retrieved chunks", min_value=1, max_value=10, value=5)

question = st.text_area(
    "Your question",
    placeholder="Example: ALB returning 5xx after deployment — what should I check first?",
    height=120
)

def _to_model_arn(region: str, model_id_or_arn: str) -> str:
    """Accept either a full ARN or a model id and return a modelArn."""
    s = (model_id_or_arn or "").strip()
    if s.startswith("arn:aws:bedrock:"):
        return s
    # Convert model id to foundation-model ARN
    return f"arn:aws:bedrock:{region}::foundation-model/{s}"

def retrieve_and_generate(region: str, kb_id: str, model_id_or_arn: str, q: str, k: int):
    client = boto3.client("bedrock-agent-runtime", region_name=region)

    payload = {
        "input": {"text": q},
        "retrieveAndGenerateConfiguration": {
            "type": "KNOWLEDGE_BASE",
            "knowledgeBaseConfiguration": {
                "knowledgeBaseId": kb_id,
                "modelArn": _to_model_arn(region, model_id_or_arn),
                "retrievalConfiguration": {
                    "vectorSearchConfiguration": {"numberOfResults": k}
                },
            },
        },
    }
    return client.retrieve_and_generate(**payload)

def render_citations(resp: dict):
    citations = resp.get("citations", [])
    if not citations:
        st.info("No citations returned. (KB may not be synced yet, or retrieval returned no matches.)")
        return

    st.subheader("Citations")
    for ci, c in enumerate(citations, start=1):
        refs = c.get("retrievedReferences", [])
        if not refs:
            continue
        st.markdown(f"**Citation {ci}**")
        for r in refs:
            loc = r.get("location", {})
            s3loc = (loc.get("s3Location") or {})
            uri = s3loc.get("uri", "")
            excerpt = ((r.get("content") or {}).get("text") or "").strip()

            if uri:
                st.write(f"- Source: `{uri}`")
            if excerpt:
                st.code(excerpt[:900])

col1, col2 = st.columns([1, 1])
with col1:
    ask_btn = st.button("Ask", type="primary")
with col2:
    show_raw = st.toggle("Show raw response", value=False)

if ask_btn:
    q = (question or "").strip()
    if not kb_id.strip():
        st.error("KB_ID is required (sidebar).")
        st.stop()
    if not q:
        st.error("Please enter a question.")
        st.stop()

    with st.spinner("Retrieving runbook context and generating answer..."):
        try:
            resp = retrieve_and_generate(
                region=aws_region.strip(),
                kb_id=kb_id.strip(),
                model_id_or_arn=model_id_or_arn.strip(),
                q=q,
                k=max_results,
            )
        except ClientError as e:
            st.error(f"AWS error: {e.response.get('Error', {}).get('Message', str(e))}")
            st.stop()
        except Exception as e:
            st.error(f"Request failed: {e}")
            st.stop()

    answer = (resp.get("output") or {}).get("text", "").strip()
    st.subheader("Answer")
    st.write(answer if answer else "_No answer returned._")

    render_citations(resp)

    if show_raw:
        st.subheader("Raw response")
        st.code(json.dumps(resp, indent=2)[:6000])

st.divider()
st.caption("Tip: For portfolio projects, deploy → demo → screenshot → delete KB/vector store to avoid ongoing costs.")
