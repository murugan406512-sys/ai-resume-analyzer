import os
import json
import streamlit as st
from pypdf import PdfReader
from dotenv import load_dotenv

# Load local environment variables if available
load_dotenv()

# ==========================================
# PAGE CONFIGURATION & STYLING
# ==========================================
st.set_page_config(
    page_title="AI Resume Analyzer & ATS Score Checker",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .score-card {
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
        border: 1px solid #BFDBFE;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .skill-badge-green {
        display: inline-block;
        padding: 4px 12px;
        margin: 3px;
        border-radius: 16px;
        background-color: #DCFCE7;
        color: #166534;
        font-weight: 600;
        font-size: 0.85rem;
        border: 1px solid #86EFAC;
    }
    .skill-badge-red {
        display: inline-block;
        padding: 4px 12px;
        margin: 3px;
        border-radius: 16px;
        background-color: #FEE2E2;
        color: #991B1B;
        font-weight: 600;
        font-size: 0.85rem;
        border: 1px solid #FCA5A5;
    }
    .suggestion-box {
        background-color: #F8FAFC;
        padding: 12px 16px;
        border-left: 4px solid #3B82F6;
        border-radius: 4px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# HELPER FUNCTIONS
# ==========================================
def extract_text_from_pdf(uploaded_file) -> str:
    """Extracts text content from an uploaded PDF file."""
    try:
        reader = PdfReader(uploaded_file)
        text = ""
        for page_num, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text.strip()
    except Exception as e:
        st.error(f"Error reading PDF file: {e}")
        return ""

def call_gemini_api(api_key: str, resume_text: str, job_description: str, model_name: str = "gemini-2.5-flash") -> dict:
    """
    Sends the resume and job description to Google Gemini and retrieves
    structured ATS analysis.
    Supports both `google-genai` and `google-generativeai` SDKs.
    """
    prompt = f"""
You are an expert ATS (Applicant Tracking System) and Senior Technical Hiring Manager.
Analyze the following candidate's Resume against the provided Job Description.

Candidate Resume:
\"\"\"
{resume_text}
\"\"\"

Target Job Description:
\"\"\"
{job_description}
\"\"\"

Evaluate the match and return your response STRICTLY as a valid JSON object with the following keys:
1. "match_score": an integer from 0 to 100 representing the overall ATS match percentage.
2. "match_level": a string ("High Match (75-100%)", "Moderate Match (50-74%)", or "Needs Optimization (<50%)").
3. "summary": a 2-3 sentence executive assessment of the candidate's alignment with the role.
4. "matched_skills": a list of specific technical and soft skills found in BOTH the resume and job description.
5. "missing_skills": a list of important keywords, tools, or requirements from the job description NOT found in the resume.
6. "improvement_suggestions": a list of exactly 5 clear, actionable, and specific suggestions to improve the resume for this exact job.
7. "sample_bullet_rewrite": an object with "original_weak_bullet" and "ats_optimized_bullet" showing how the candidate can rewrite a project/experience bullet point with action verbs and quantifiable metrics.

DO NOT return any markdown wrapping like ```json. Return ONLY valid JSON text.
"""

    # Try new official google-genai SDK first
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
        )
        raw_output = response.text.strip()
    except (ImportError, Exception) as genai_err:
        # Fallback to legacy google.generativeai if installed
        try:
            import google.generativeai as legacy_genai
            legacy_genai.configure(api_key=api_key)
            model = legacy_genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            raw_output = response.text.strip()
        except Exception as legacy_err:
            raise RuntimeError(f"API Call failed. Details: {genai_err} | Fallback: {legacy_err}")

    # Clean JSON markdown fences if model returned them
    if raw_output.startswith("```json"):
        raw_output = raw_output[7:]
    if raw_output.startswith("```"):
        raw_output = raw_output[3:]
    if raw_output.endswith("```"):
        raw_output = raw_output[:-3]
    raw_output = raw_output.strip()

    return json.loads(raw_output)

def get_demo_analysis() -> dict:
    """Returns sample analysis output for testing without API keys."""
    return {
        "match_score": 78,
        "match_level": "High Match (75-100%)",
        "summary": "The candidate has strong Python fundamentals, web framework experience (Flask, Streamlit), and machine learning project background. The profile is well-aligned with junior developer roles but lacks explicit cloud/containerization and CI/CD keywords.",
        "matched_skills": [
            "Python", "Flask", "Streamlit", "SQL", "Pandas", "Scikit-Learn",
            "Git & GitHub", "REST APIs", "Data Visualization"
        ],
        "missing_skills": [
            "Docker / Containerization", "PostgreSQL", "FastAPI",
            "CI/CD (GitHub Actions)", "Cloud (AWS / GCP)", "Unit Testing (pytest)"
        ],
        "improvement_suggestions": [
            "Highlight experience or academic coursework with Docker containers and cloud deployment (AWS or GCP).",
            "Mention FastAPI or asynchronous web services alongside Flask to show versatility in modern Python web frameworks.",
            "Quantify results in the projects section (e.g., 'achieved 88% accuracy', 'reduced processing time by 20%').",
            "Incorporate unit testing (pytest) and CI/CD tools to demonstrate production-ready coding practices.",
            "Add a concise 2-sentence Professional Summary at the top of the resume featuring target keywords from the job description."
        ],
        "sample_bullet_rewrite": {
            "original_weak_bullet": "Built a web app to track expenses and made some charts.",
            "ats_optimized_bullet": "Developed a full-stack financial tracking application using Python, Flask, and SQLite; designed interactive Chart.js visualizations that improved weekly user budget engagement by 40%."
        }
    }

# ==========================================
# SIDEBAR CONFIGURATION
# ==========================================
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/resume.png", width=64)
    st.title("Settings & Config")

    st.markdown("### 🔑 Gemini API Key")
    env_key = os.getenv("GEMINI_API_KEY", "")
    api_key_input = st.text_input(
        "Enter your Google Gemini API Key:",
        value=env_key,
        type="password",
        help="Get your free key from https://aistudio.google.com/"
    )

    demo_mode = st.checkbox(
        "🚀 Offline Demo Mode",
        value=False if api_key_input else True,
        help="Check this to test the app and take screenshots immediately without needing an active API key."
    )

    st.markdown("---")
    st.markdown("### ⚙️ Model Selection")
    selected_model = st.selectbox(
        "Choose Gemini Model:",
        ["gemini-2.5-flash", "gemini-1.5-flash", "gemini-2.0-flash"],
        index=0
    )

    st.markdown("---")
    st.markdown("### 📌 About This Prototype")
    st.caption(
        "**Problem Statement 1:** AI Resume Analyzer & ATS Score Checker\n\n"
        "**Workflow:** Resume (PDF/Text) + Job Description ➡️ Gemini AI ➡️ ATS Score, Skill Gap Analysis & 5 Actionable Tips."
    )

# ==========================================
# MAIN APPLICATION INTERFACE
# ==========================================
st.markdown('<div class="main-header">📄 AI Resume Analyzer & ATS Score Checker</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Check your resume against any job description, get an instant ATS match score, identify missing keywords, and receive tailored tips to get shortlisted.</div>',
    unsafe_allow_html=True
)

# Preset sample data for quick testing
SAMPLE_RESUME = """JOHN DOE
Email: john.doe@example.com | Phone: +1-555-0199 | Location: New York, NY
LinkedIn: linkedin.com/in/johndoe | GitHub: github.com/johndoe

EDUCATION
Bachelor of Science in Computer Science | XYZ University (2020 - 2024) - CGPA: 8.6/10

TECHNICAL SKILLS
- Programming Languages: Python, JavaScript, C++, SQL
- Frameworks & Libraries: Streamlit, Flask, Pandas, NumPy, Scikit-Learn
- Databases: PostgreSQL, SQLite
- Developer Tools: Git, GitHub, VS Code, Postman, Docker (Basics)

PROJECTS
1. Smart Expense Tracker (Python, Flask, SQLite)
   - Built a web application allowing users to track daily income and expenditure with categorization.
   - Designed interactive dashboards with chart visualizations using Chart.js.
   - Implemented secure user authentication with password hashing and session tokens.

2. Customer Sentiment Analyzer (Python, NLTK, Scikit-Learn)
   - Developed a machine learning pipeline to classify 10,000+ customer reviews into positive/negative sentiments.
   - Extracted features using TF-IDF and trained a Logistic Regression classifier achieving 88% accuracy.
   - Deployed the prediction interface as an interactive Streamlit app.

EXPERIENCE & INTERNSHIPS
Software Engineering Intern | TechCorp Solutions (Jan 2024 - Jun 2024)
- Assisted in developing RESTful API endpoints using Python and Flask for internal analytics.
- Automated weekly data reporting scripts using Pandas, reducing reporting turnaround by 35%.
- Collaborated with senior engineers in Agile sprints and code reviews via GitHub."""

SAMPLE_JD = """Position: Junior Python / AI Developer
Company: NextGen Innovators
Location: Remote / Hybrid

About the Role:
We are looking for an ambitious Junior Python / AI Developer to join our engineering team. You will be building AI-powered web applications, REST APIs, and data workflows that serve thousands of users daily.

Key Responsibilities:
- Build, test, and maintain web services using Python, FastAPI or Flask.
- Integrate modern LLMs (Gemini, OpenAI) and machine learning models into user-facing web interfaces.
- Work with relational and NoSQL databases (PostgreSQL, MongoDB) to store and query application data.
- Participate in CI/CD pipeline deployments using Docker and GitHub Actions.
- Optimize application latency, API responsiveness, and search performance.

Required Qualifications & Skills:
- Bachelor's degree in Computer Science, Information Technology, or related field.
- Strong proficiency in Python and familiarity with data manipulation (Pandas, NumPy).
- Hands-on experience developing web applications (Streamlit, FastAPI, or Flask).
- Familiarity with version control (Git, GitHub) and REST API principles.
- Basic understanding of cloud platforms (AWS/GCP) and containerization with Docker.

Nice to Have:
- Experience with GenAI / LLM APIs (Gemini, LangChain).
- Understanding of Unit Testing (pytest) and Agile development methodology.
- Good communication skills and eagerness to learn."""

# Two column input layout
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Candidate Resume")
    resume_file = st.file_uploader("Upload Resume (PDF format)", type=["pdf"], help="Upload your resume in PDF format.")

    # Button to load sample resume
    if st.button("📋 Load Sample Resume Text", key="btn_sample_resume"):
        st.session_state["resume_input_text"] = SAMPLE_RESUME

    resume_text_area = st.text_area(
        "Or paste resume text directly:",
        value=st.session_state.get("resume_input_text", ""),
        height=260,
        placeholder="Paste resume text here if you do not have a PDF handy..."
    )

with col2:
    st.subheader("2. Target Job Description")
    if st.button("📋 Load Sample Job Description", key="btn_sample_jd"):
        st.session_state["jd_input_text"] = SAMPLE_JD

    jd_text_area = st.text_area(
        "Paste the Job Description (JD):",
        value=st.session_state.get("jd_input_text", ""),
        height=325,
        placeholder="Paste full job description including requirements, qualifications, and responsibilities..."
    )

st.markdown("---")

# Determine final resume text
final_resume_text = ""
if resume_file is not None:
    extracted = extract_text_from_pdf(resume_file)
    if extracted:
        final_resume_text = extracted
        st.success(f"✅ Successfully extracted {len(final_resume_text.split())} words from '{resume_file.name}'")
elif resume_text_area.strip():
    final_resume_text = resume_text_area.strip()

final_jd_text = jd_text_area.strip()

# Analyze Button
analyze_clicked = st.button("🚀 Analyze Resume & Calculate ATS Score", type="primary", use_container_width=True)

if analyze_clicked:
    if not final_resume_text:
        st.warning("⚠️ Please upload a PDF resume or paste resume text before analyzing.")
    elif not final_jd_text:
        st.warning("⚠️ Please provide a job description to compare against.")
    else:
        with st.spinner("🤖 Gemini AI is evaluating ATS keywords, skills match, and resume formatting..."):
            result_data = None
            if demo_mode or not api_key_input:
                if not api_key_input and not demo_mode:
                    st.info("ℹ️ No API key detected. Running in Demo Mode with instant realistic sample results.")
                result_data = get_demo_analysis()
            else:
                try:
                    result_data = call_gemini_api(
                        api_key=api_key_input,
                        resume_text=final_resume_text,
                        job_description=final_jd_text,
                        model_name=selected_model
                    )
                except Exception as ex:
                    st.error(f"❌ Error during AI analysis: {ex}")
                    st.info("💡 You can switch on 'Offline Demo Mode' in the sidebar to test without an API key.")

            if result_data:
                st.session_state["analysis_result"] = result_data

# ==========================================
# DISPLAY ANALYSIS RESULTS
# ==========================================
if "analysis_result" in st.session_state:
    data = st.session_state["analysis_result"]
    st.markdown("## 📊 ATS Analysis & Match Report")

    # Score Overview Cards
    score = data.get("match_score", 0)
    level = data.get("match_level", "Evaluated")
    summary = data.get("summary", "")
    matched = data.get("matched_skills", [])
    missing = data.get("missing_skills", [])
    suggestions = data.get("improvement_suggestions", [])
    rewrite = data.get("sample_bullet_rewrite", {})

    mcol1, mcol2, mcol3, mcol4 = st.columns(4)
    with mcol1:
        st.metric(label="🎯 ATS Match Score", value=f"{score} / 100")
        st.progress(score / 100)
    with mcol2:
        st.metric(label="📈 Match Status", value=level.split()[0] if level else "Good")
        st.caption(level)
    with mcol3:
        st.metric(label="✅ Matched Skills", value=len(matched))
        st.caption("Skills found in resume & JD")
    with mcol4:
        st.metric(label="⚠️ Missing Skills", value=len(missing))
        st.caption("Important keywords missing")

    # Executive Summary
    st.info(f"**AI Assessment:** {summary}")

    # Skills Breakdown in 2 Columns
    scol1, scol2 = st.columns(2)
    with scol1:
        st.markdown("### ✅ Skills Found Matching the Job")
        if matched:
            badges_html = "".join([f'<span class="skill-badge-green">✓ {skill}</span>' for skill in matched])
            st.markdown(badges_html, unsafe_allow_html=True)
        else:
            st.write("No direct skills match detected.")

    with scol2:
        st.markdown("### ⚠️ Missing Skills & Critical Keywords")
        if missing:
            badges_html = "".join([f'<span class="skill-badge-red">+ {skill}</span>' for skill in missing])
            st.markdown(badges_html, unsafe_allow_html=True)
        else:
            st.write("Great job! No major keyword gaps identified.")

    st.markdown("---")

    # 5 Suggestions for Improvement
    st.markdown("### 💡 5 Actionable Suggestions to Improve Your Resume")
    for idx, suggestion in enumerate(suggestions[:5], start=1):
        st.markdown(f"""
        <div class="suggestion-box">
            <b>{idx}.</b> {suggestion}
        </div>
        """, unsafe_allow_html=True)

    # Bullet Point Rewrite Example
    if rewrite and "ats_optimized_bullet" in rewrite:
        st.markdown("---")
        st.markdown("### ✍️ Sample Resume Bullet Point Transformation")
        bcol1, bcol2 = st.columns(2)
        with bcol1:
            st.caption("🔴 Before (Passive / Generic):")
            st.error(rewrite.get("original_weak_bullet", "Worked on a web application."))
        with bcol2:
            st.caption("🟢 After (Quantified & ATS-Optimized):")
            st.success(rewrite.get("ats_optimized_bullet", "Architected web service using Python, boosting performance by 30%."))

    # Downloadable Report
    st.markdown("---")
    report_text = f"""==================================================
AI RESUME ANALYZER & ATS SCORE REPORT
==================================================
ATS Match Score: {score} / 100
Match Level: {level}

EXECUTIVE SUMMARY:
{summary}

MATCHED SKILLS:
{', '.join(matched)}

MISSING SKILLS & KEYWORDS:
{', '.join(missing)}

5 ACTIONABLE SUGGESTIONS TO IMPROVE:
""" + "\n".join([f"{i+1}. {s}" for i, s in enumerate(suggestions)]) + f"""

SAMPLE BULLET REWRITE:
- Before: {rewrite.get('original_weak_bullet', 'N/A')}
- After:  {rewrite.get('ats_optimized_bullet', 'N/A')}
==================================================
Generated with AI Resume Analyzer (Streamlit + Google Gemini)
"""

    st.session_state["generated_report_text"] = report_text

    col_dl1, col_dl2 = st.columns([3, 1])
    with col_dl1:
        st.download_button(
            label="📥 Download Full ATS Report as .TXT",
            data=st.session_state["generated_report_text"],
            file_name="ATS_Resume_Analysis_Report.txt",
            mime="text/plain",
            use_container_width=True,
            key="download_full_ats_report_key"
        )
    with col_dl2:
        if st.button("📋 View Raw Report", key="view_raw_report_key", use_container_width=True):
            st.session_state["show_raw_report"] = not st.session_state.get("show_raw_report", False)

    if st.session_state.get("show_raw_report", False):
        st.code(st.session_state["generated_report_text"], language="text")

# ==========================================
# VIVA & EXPLANATION GUIDE (FOR SUBMISSION)
# ==========================================
with st.expander("📚 Student Guide: How to Explain this Project in Viva / Submission"):
    st.markdown("""
    ### Key Concepts to Explain:
    1. **Architecture & Pipeline:**
       - **Input:** User uploads a resume (PDF parsed via `pypdf` into clean text) and enters a Job Description.
       - **AI Model:** Google Gemini (`gemini-2.5-flash`) processes both texts using a structured prompt with few-shot constraints.
       - **Output:** The model outputs structured JSON parsed into an ATS score, keyword tags (matched vs missing), and 5 targeted recommendations.
    2. **Why Applicant Tracking Systems (ATS) matter:**
       - Companies use ATS scanners to parse keywords, job titles, and hard skills before a human recruiter ever sees the resume.
       - Missing keywords (e.g., Docker, FastAPI, CI/CD) cause qualified applicants to be filtered out automatically.
    3. **Safe API Key Management:**
       - The API key is securely loaded via `python-dotenv` from a `.env` file or Streamlit sidebar, and is excluded from source code and GitHub commits via `.gitignore`.
    """)
