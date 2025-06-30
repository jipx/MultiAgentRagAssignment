import streamlit as st
import json
import requests
import re
from docx import Document

st.set_page_config(page_title="📄 DOCX to Bedrock JSON", layout="wide")
st.title("📤 Upload DOCX to Bedrock KB (Preview → Upload)")

# Load config from secrets.toml
API_BASE = st.secrets["bedrock"]["api_base"]
S3_BUCKET_NAME = st.secrets["bedrock"]["s3_bucket"]

# DOCX to markdown and chunked JSON
def docx_to_chunks(docx_file, extra_meta=None):
    doc = Document(docx_file)
    lines = []
    for para in doc.paragraphs:
        style = para.style.name
        text = para.text.strip()
        if not text:
            continue
        if style.startswith("Heading"):
            level = re.findall(r"\d+", style)
            lines.append(f"{'#' * int(level[0])} {text}" if level else f"## {text}")
        else:
            lines.append(text)
    markdown = "\n".join(lines)
    raw_chunks = re.split(r"\n(?=#+ )", markdown)
    structured = []
    for idx, chunk in enumerate(raw_chunks, start=1):
        title_match = re.match(r"#+\s*(Task \d+):?", chunk)
        task_id = title_match.group(1) if title_match else f"Chunk {idx}"
        metadata = {
            "source": "UploadedDoc",
            "task_number": task_id,
            "chunk_id": idx
        }
        if extra_meta:
            metadata.update(extra_meta)
        structured.append({
            "text": chunk.strip(),
            "metadata": metadata
        })
    return structured, markdown

def get_presigned_url(key, method):
    payload = {"key": key, "method": method}
    st.code(f"📤 POST to /presigned-url\n{json.dumps(payload, indent=2)}", language="json")
    try:
        res = requests.post(f"{API_BASE}/presigned-url", json=payload)
        st.code(f"✅ Response [{res.status_code}]\n{res.text}", language="json")
        res.raise_for_status()
        return res.json()["url"]
    except Exception as e:
        st.error(f"❌ Presigned URL request failed.")
        st.exception(e)
        raise

# Upload input
uploaded = st.file_uploader("📎 Upload a DOCX file", type=["docx"])
if uploaded:
    st.info("✅ File uploaded. Add metadata to generate preview.")

    with st.form("metadata_form"):
        module = st.text_input("Module", value="Module 2")
        author = st.text_input("Author", value="Instructor")
        version = st.text_input("Version", value="1.0")
        submit_meta = st.form_submit_button("➕ Generate Preview")

    if submit_meta:
        meta_fields = {"module": module, "author": author, "version": version}
        chunks, markdown = docx_to_chunks(uploaded, extra_meta=meta_fields)
        json_output = json.dumps(chunks, indent=2)
        json_filename = uploaded.name.replace(".docx", ".json")
        s3_key = f"processed/{json_filename}"

        # Save to session_state
        st.session_state["json_output"] = json_output
        st.session_state["s3_key"] = s3_key
        st.session_state["markdown"] = markdown
        st.session_state["chunks"] = chunks

# Show preview and upload button if preview was generated
if "json_output" in st.session_state:
    st.subheader("📄 Markdown Preview")
    st.code(st.session_state["markdown"], language="markdown")

    st.subheader("📦 JSON with Metadata")
    st.json(st.session_state["chunks"])

    if st.button("📤 Upload JSON to S3 via Presigned URL"):
        try:
            json_output = st.session_state["json_output"]
            s3_key = st.session_state["s3_key"]

            # Step 1: Get PUT URL
            put_url = get_presigned_url(s3_key, "put")
            st.code(f"⬆️ PUT to: {put_url}", language="bash")

            # Step 2: Upload
            res = requests.put(put_url, data=json_output.encode())
            st.code(f"📡 Upload Response: {res.status_code}", language="http")
            st.code(f"Headers:\n{json.dumps(dict(res.headers), indent=2)}", language="json")
            st.code(res.text or "(No response body)", language="json")
            res.raise_for_status()

            # Step 3: Show GET + Public URL
            get_url = get_presigned_url(s3_key, "get")
            public_url = f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{s3_key}"

            st.success("🎉 Upload complete!")
            st.markdown(f"[📥 Presigned Download]({get_url})")
            st.markdown(f"🔍 **S3 Object URL:** `{public_url}`")

        except requests.exceptions.RequestException as upload_err:
            st.error("❌ Upload failed!")
            st.exception(upload_err)
