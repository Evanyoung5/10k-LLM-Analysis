import streamlit as st
import requests

API_URL = "http://localhost:8000"  # Adjust if your FastAPI backend is remote

st.set_page_config(page_title="10-K AI Assistant", page_icon="📊")
st.title("📊 10-K AI Research Assistant")

# Upload Section
st.header("Upload a 10-K PDF")

uploaded_file = st.file_uploader("Choose a 10-K PDF file", type=["pdf"])

if uploaded_file is not None:
    if st.button("Upload and Process"):
        with st.spinner("Uploading and processing PDF..."):
            try:
                files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}
                response = requests.post(f"{API_URL}/upload", files=files)
                if response.status_code == 200:
                    st.success(response.json().get("message", "Upload succeeded!"))
                else:
                    st.error(f"❌ Upload failed: {response.text}")
            except Exception as e:
                st.error(f"⚠️ Exception occurred: {e}")

st.divider()

# Question Section
st.header("Ask a Question About the 10-K")

query = st.text_input("Enter your question")

if st.button("Ask"):
    if not query:
        st.warning("⚠️ Please enter a question before submitting.")
    else:
        with st.spinner("Retrieving answer..."):
            try:
                response = requests.get(f"{API_URL}/ask", params={"query": query})
                if response.status_code == 200:
                    data = response.json()
                    st.markdown("### ✅ Answer")
                    st.success(data.get("answer", "No answer returned."))

                    st.markdown("### 🔍 Context Used")
                    for i, chunk in enumerate(data.get("context_used", []), 1):
                        st.markdown(f"**Chunk {i}:**")
                        st.code(chunk)
                else:
                    st.error(f"❌ Query failed: {response.text}")
            except Exception as e:
                st.error(f"⚠️ Exception occurred: {e}")
