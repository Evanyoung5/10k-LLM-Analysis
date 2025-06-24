import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.title("📊 10-K AI Research Assistant")

# Upload PDF
st.header("Upload 10-K Filing")
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
if uploaded_file is not None:
    if st.button("Upload and Process"):
        with st.spinner("Uploading and embedding..."):
            files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}
            response = requests.post(f"{API_URL}/upload", files=files)
        if response.ok:
            st.success(response.json().get("message", "Uploaded successfully!"))
        else:
            st.error(f"Upload failed: {response.text}")

# Ask questions
st.header("Ask a Question")
query = st.text_input("Enter your question here")

if st.button("Ask"):
    if not query:
        st.warning("Please enter a question first!")
    else:
        with st.spinner("Getting answer..."):
            params = {"query": query}
            response = requests.get(f"{API_URL}/ask", params=params)
        if response.ok:
            data = response.json()
            st.markdown("**Answer:**")
            st.write(data.get("answer", "No answer returned."))
            with st.expander("Context Used"):
                for i, ctx in enumerate(data.get("context_used", []), 1):
                    st.write(f"### Chunk {i}")
                    st.write(ctx)
        else:
            st.error(f"Query failed: {response.text}")
