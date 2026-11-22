# Government Scheme Finder — Problem Statement 39

AI-powered prototype that helps citizens explore potentially relevant Central Government schemes using profile details and uploaded official scheme documents.

## Assignment mapping
Problem 39 in the supplied assignment asks for a scheme finder based on age, income, state and occupation, using RAG over scheme PDFs and explaining why schemes may match.

## Features
- Collect age, annual family income, state and occupation.
- Upload one or more official scheme-guideline PDFs.
- Extract PDF text and split it into overlapping chunks while retaining source filename and page.
- Generate embeddings with `all-MiniLM-L6-v2` and index them using FAISS.
- Retrieve passages based on the profile and question.
- Ask Gemini to explain potential matches using only retrieved excerpts.
- Display retrieved passages and source page numbers.

## Official source for documents
Use current documents linked from the Government of India's myScheme portal:
https://www.myscheme.gov.in/
The portal is an official national platform for scheme discovery and eligibility information. This project is an academic prototype and is not affiliated with or endorsed by myScheme.

Download current scheme guidelines/FAQs from the relevant ministry or official scheme page and upload them in the app. Do not rely on outdated or unofficial PDFs.

## Setup
1. Install Python 3.10+.
2. Create and activate a virtual environment.
3. Install packages: `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and add your Gemini key as `GEMINI_API_KEY=...`.
5. Run: `streamlit run app.py`
6. Upload one or more text-based official scheme PDFs, click **Process scheme documents**, enter a profile and click **Find schemes**.

Never commit `.env` or API keys to GitHub.

## Suggested test profiles
1. Age 20, annual income ₹1,20,000, student, Maharashtra.
2. Age 35, annual income ₹2,40,000, farmer, Uttar Pradesh.
3. Age 42, annual income ₹8,00,000, salaried employee, Karnataka.
4. Age 65, annual income ₹1,80,000, senior citizen, Rajasthan.
5. Age 28, annual income ₹3,00,000, self-employed, Bihar.

These are test inputs only, not claims that a specific scheme will match. Record actual outputs and whether the documents support them.

## Limitations and safeguards
- The quality and coverage of results depend on the uploaded documents.
- Scanned PDFs without selectable text require OCR.
- A retrieved match is not an official eligibility determination or guarantee of benefit.
- The app does not submit applications or verify identity.
- Always check current criteria, dates, documents and application process with the responsible ministry or official portal.
- Do not upload personal identity documents or confidential information.

## Project structure
```text
government_scheme_finder_ps39/
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
└── report_template.md
```
