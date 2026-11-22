# Two-Page Procedure Report — Complete after actual testing

**Project title:** AI-Powered Government Scheme Finder Using Generative AI and RAG  
**Problem statement:** 39 — Government Scheme Finder  
**Name:** [Your name]  
**Roll number:** 39  
**Class:** [Your class]  
**GitHub link:** [Add after publishing]

## 1. Problem statement
Citizens may not know which government schemes could apply to them. This project accepts age, annual family income, state and occupation, searches uploaded official Central Government scheme documents using Retrieval-Augmented Generation (RAG), and uses an LLM to explain potential scheme matches and the supporting eligibility criteria.

## 2. Tools and model
- Programming language: Python
- UI framework: Streamlit
- PDF extraction: PyPDF
- Embedding model: Sentence Transformers (`all-MiniLM-L6-v2`)
- Vector search: FAISS
- LLM: Google Gemini via `google-genai`
- Architecture: Retrieval-Augmented Generation (RAG)

## 3. Procedure
1. Set up Python and installed dependencies from `requirements.txt`.
2. Obtained a Gemini API key and configured it locally as `GEMINI_API_KEY`.
3. Collected current official Central Government scheme guideline/FAQ PDFs from official government sources.
4. Developed PDF text extraction and divided extracted text into overlapping chunks, retaining filename and page number.
5. Generated vector embeddings for each chunk and stored them in a FAISS index.
6. Collected the user's age, annual income, state and occupation through Streamlit.
7. Combined the profile and question to retrieve relevant passages from the vector index.
8. Sent retrieved excerpts and the profile to Gemini with a prompt requiring answers to use only the supplied excerpts, identify missing information and cite source pages.
9. Tested the application using five sample profiles and recorded actual outputs.

## 4. Prompt used
[Paste the final prompt from `ask_gemini()` in app.py. Explain one improvement made during testing, such as instructing the model not to infer missing eligibility criteria.]

## 5. Results
[Insert 1–2 screenshots from the running application. Show a sample profile, uploaded official PDF and the generated answer with source references.]

## 6. Challenges
[Describe actual issues faced and solutions, such as scanned PDF text extraction, API key configuration, package installation, retrieval relevance or missing eligibility details.]

## 7. Conclusion
The project demonstrates how RAG and an LLM can make official scheme documents easier to search and understand. The output is only a preliminary information aid; users must verify current eligibility and application details with the responsible government authority. A future improvement could add OCR, multilingual support and a larger regularly updated verified scheme collection.
