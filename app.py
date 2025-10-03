import streamlit as st
import google.generativeai as genai
import PyPDF2 as pdf
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Configure Gemini API key from .env file
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# ---------- Function to get Gemini response ----------
def get_gemini_response(input_text: str) -> str:
    try:
        # Use a supported Gemini model (update if necessary)
        model = genai.GenerativeModel("gemini-2.5-flash-lite")
        response = model.generate_content(input_text)
        return getattr(response, "text", str(response))
    except Exception as e:
        return f"Error: {str(e)}"

# ---------- Extract text from uploaded PDF ----------
def input_pdf_text(uploaded_file) -> str:
    try:
        reader = pdf.PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

# ---------- Safe JSON Parsing ----------
def safe_json_parse(response: str):
    try:
        return json.loads(response)
    except:
        try:
            start = response.find("{")
            end = response.rfind("}") + 1
            if start != -1 and end != -1:
                json_str = response[start:end]
                return json.loads(json_str)
        except:
            return None
    return None

# ---------- Prompt Template ----------
INPUT_PROMPT = """
You are an experienced Technical Human Resource Manager. Your task is to evaluate the resume against the provided job description. 
Give me the result in the following structured JSON format only:

{{
  "JD Match": "<percentage match>",
  "MissingKeywords": ["<list of missing keywords>"],
  "Profile Summary": "<summary of the candidate profile>"
}}

Job Description:
{jd}

Resume Text:
{text}
"""

# ---------- Streamlit App ----------
st.set_page_config(page_title="AI ATS Resume Evaluator", layout="wide")
st.title("🤖 AI ATS Resume Evaluator")
st.markdown("### Automate and improve resume screening with Generative AI")

# Inputs
jd = st.text_area("📋 Paste the Job Description here", height=200)
uploaded_file = st.file_uploader("📂 Upload your Resume (PDF only)", type="pdf")

# Evaluate button
if st.button("Evaluate Resume"):
    if uploaded_file is None:
        st.warning("⚠️ Please upload a PDF resume.")
    elif not jd.strip():
        st.warning("⚠️ Please paste a job description.")
    else:
        with st.spinner("Extracting resume text..."):
            resume_text = input_pdf_text(uploaded_file)

        prompt = INPUT_PROMPT.format(jd=jd, text=resume_text)

        with st.spinner("Evaluating resume with Gemini..."):
            response = get_gemini_response(prompt)

        result_json = safe_json_parse(response)

        if result_json:
            st.success("✅ Evaluation Completed")
            st.json(result_json)
        else:
            st.error("⚠️ Could not parse structured JSON. Showing raw response instead:")
            st.text(response)

