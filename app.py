import os
import streamlit as st
import numpy as np
import faiss
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
from google import genai
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Government Scheme Finder", page_icon="🇮🇳", layout="wide")
st.title("🇮🇳 AI-Powered Government Scheme Finder")
st.caption("Discover potentially relevant Central Government schemes using your profile and official scheme documents.")

st.info("Academic prototype: results are preliminary matches, not an official eligibility decision. Always verify current rules with the scheme-owning ministry or official portal.")

API_KEY = os.getenv("GEMINI_API_KEY", "")

@st.cache_resource
def get_embedder():
    return SentenceTransformer("all-MiniLM-L6-v2")

def extract_pdf_pages(files):
    records = []
    for uploaded in files:
        reader = PdfReader(uploaded)
        for page_no, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            if text.strip():
                records.append({
                    "source": uploaded.name,
                    "page": page_no,
                    "text": " ".join(text.split())
                })
    return records

def chunk_pages(pages, chunk_size=950, overlap=160):
    chunks = []
    for page in pages:
        text = page["text"]
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            part = text[start:end].strip()
            if part:
                chunks.append({
                    "text": part,
                    "source": page["source"],
                    "page": page["page"]
                })
            if end >= len(text):
                break
            start = max(end - overlap, start + 1)
    return chunks

def make_faiss(chunks, embedder):
    vectors = embedder.encode(
        [c["text"] for c in chunks],
        convert_to_numpy=True,
        normalize_embeddings=True
    ).astype("float32")
    idx = faiss.IndexFlatIP(vectors.shape[1])
    idx.add(vectors)
    return idx

def retrieve(query, chunks, index, embedder, top_k):
    q = embedder.encode([query], convert_to_numpy=True, normalize_embeddings=True).astype("float32")
    scores, ids = index.search(q, min(top_k, len(chunks)))
    found = []
    for score, i in zip(scores[0], ids[0]):
        if i >= 0:
            item = dict(chunks[int(i)])
            item["score"] = float(score)
            found.append(item)
    return found

def make_profile_query(profile, question):
    return (
        f"Find Central Government schemes and eligibility conditions relevant to a citizen "
        f"with age {profile['age']}, annual family income INR {profile['income']}, "
        f"state {profile['state']}, occupation {profile['occupation']}, "
        f"and additional details: {profile['extra']}. User question: {question}"
    )

def ask_gemini(profile, question, passages, model_name):
    client = genai.Client(api_key=API_KEY)
    context = "\n\n".join(
        f"Source: {p['source']} | PDF page: {p['page']}\n{p['text']}"
        for p in passages
    )
    prompt = f"""You are an assistant that helps citizens understand Central Government schemes in India.
Use ONLY the supplied document excerpts. Do not use outside knowledge or invent scheme names, thresholds, benefits, deadlines, URLs, or eligibility rules.
Treat the citizen profile as information to compare with the stated rules, not as proof of eligibility.
For every scheme discussed, provide:
1. Scheme name (only if clearly stated in the excerpts)
2. Potential match: likely match / possible match / information insufficient / does not appear to match
3. Criteria supported by the excerpts and how the profile compares
4. Missing information or conditions that need official verification
5. Benefits and application steps only if stated in the excerpts
6. Source filename and PDF page number
If the excerpts do not contain enough evidence, say so and do not guess.
Never claim that the citizen is officially approved or definitively eligible.
Keep the response clear and practical.

CITIZEN PROFILE:
Age: {profile['age']}
Annual family income (INR): {profile['income']}
State: {profile['state']}
Occupation: {profile['occupation']}
Additional information: {profile['extra']}

USER QUESTION:
{question}

RETRIEVED OFFICIAL DOCUMENT EXCERPTS:
{context}
"""
    response = client.models.generate_content(model=model_name, contents=prompt)
    return response.text or "No response was generated."

with st.sidebar:
    st.header("Model settings")
    model_name = st.text_input("Gemini model", "gemini-3.5-flash-lite")
    top_k = st.slider("Retrieved passages", 2, 8, 5)
    st.markdown("**API key**")
    if API_KEY:
        st.success("Gemini API key detected")
    else:
        st.warning("Set GEMINI_API_KEY before asking questions.")

st.subheader("1. Enter citizen profile")
c1, c2 = st.columns(2)
with c1:
    age = st.number_input("Age (years)", min_value=0, max_value=120, value=25, step=1)
    income = st.number_input("Annual family income (₹)", min_value=0, max_value=100000000, value=300000, step=10000)
with c2:
    state = st.selectbox("State / Union Territory", [
        "Andhra Pradesh","Arunachal Pradesh","Assam","Bihar","Chhattisgarh","Goa","Gujarat",
        "Haryana","Himachal Pradesh","Jharkhand","Karnataka","Kerala","Madhya Pradesh",
        "Maharashtra","Manipur","Meghalaya","Mizoram","Nagaland","Odisha","Punjab",
        "Rajasthan","Sikkim","Tamil Nadu","Telangana","Tripura","Uttar Pradesh",
        "Uttarakhand","West Bengal","Andaman and Nicobar Islands","Chandigarh",
        "Dadra and Nagar Haveli and Daman and Diu","Delhi","Jammu and Kashmir",
        "Ladakh","Lakshadweep","Puducherry"
    ])
    occupation = st.selectbox("Occupation", [
        "Student", "Farmer", "Self-employed", "Salaried employee",
        "Unemployed", "Daily wage worker", "Business owner",
        "Homemaker", "Senior citizen", "Other"
    ])
extra = st.text_input("Additional details (optional)", placeholder="Example: pursuing a diploma, small business owner, etc.")
profile = {"age": age, "income": income, "state": state, "occupation": occupation, "extra": extra}

st.subheader("2. Upload official Central Government scheme documents")
st.write("Upload scheme guidelines, official FAQs or ministry PDFs. Use current documents from official government sources.")
pdfs = st.file_uploader("Upload one or more scheme PDFs", type=["pdf"], accept_multiple_files=True)

if "chunks" not in st.session_state:
    st.session_state.chunks = None
    st.session_state.index = None

if st.button("Process scheme documents", disabled=not pdfs):
    try:
        with st.spinner("Extracting, chunking and indexing documents..."):
            pages = extract_pdf_pages(pdfs)
            if not pages:
                st.error("No selectable text found. Scanned PDFs need OCR before they can be used.")
            else:
                chunks = chunk_pages(pages)
                embedder = get_embedder()
                index = make_faiss(chunks, embedder)
                st.session_state.chunks = chunks
                st.session_state.index = index
                st.success(f"Indexed {len(pdfs)} PDF(s), {len(pages)} pages and {len(chunks)} passages.")
    except Exception as e:
        st.error(f"Document processing failed: {e}")

st.subheader("3. Find potentially relevant schemes")
question = st.text_area(
    "What would you like to know?",
    value="Find Central Government schemes that may match my profile. Explain the eligibility criteria and how to apply.",
    height=95
)

if st.button("Find schemes", type="primary"):
    if not API_KEY:
        st.error("Configure GEMINI_API_KEY first.")
    elif not st.session_state.chunks or st.session_state.index is None:
        st.error("Upload and process at least one official scheme PDF first.")
    elif not question.strip():
        st.error("Enter a question.")
    else:
        try:
            with st.spinner("Retrieving relevant scheme information and preparing explanations..."):
                embedder = get_embedder()
                query = make_profile_query(profile, question)
                passages = retrieve(query, st.session_state.chunks, st.session_state.index, embedder, top_k)
                answer = ask_gemini(profile, question, passages, model_name)
            st.markdown("### Results")
            st.markdown(answer)
            with st.expander("View retrieved source passages"):
                for p in passages:
                    st.markdown(f"**{p['source']} · Page {p['page']} · Similarity {p['score']:.3f}**")
                    st.write(p["text"])
        except Exception as e:
            st.error(f"Could not generate results: {e}")

st.divider()
st.caption("This prototype does not submit applications or verify identity. Confirm eligibility, documents, dates and application links with the responsible ministry or official scheme portal.")
st.markdown("Official discovery portal: [myScheme.gov.in](https://www.myscheme.gov.in/)")
