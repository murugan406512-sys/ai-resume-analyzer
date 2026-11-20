# 📄 AI Resume Analyzer & ATS Score Checker

> **Task 2: Prototype or Model Creation using AI**  
> **Chosen Problem Statement:** Problem 1 — AI Resume Analyzer & ATS Score Checker  
> **Tech Stack:** Python 3, Streamlit, Google Gemini API (`google-genai`), PyPDF

---

## 🌟 Overview & Problem Solved
Many companies use **Applicant Tracking System (ATS)** software to screen hundreds of resumes before a human recruiter ever sees them. Students and job seekers often get filtered out simply because their resumes lack specific keywords, tools, or formatting expected by the job description.

This application acts as an intelligent ATS scanner:
1. **Reads Resume:** Extracts text from an uploaded PDF or pasted text.
2. **Evaluates Match with AI:** Sends the resume and target job description to Google's Gemini model.
3. **Displays Results:**
   - **ATS Match Score** (out of 100) and match category badge.
   - **Matched Skills** (found in both resume and JD).
   - **Missing Skills / Keywords** (critical gaps to fix).
   - **5 Actionable Suggestions** to improve the resume.
   - **Quantified Bullet Point Rewrite** example.
   - **Downloadable ATS Report (.txt)**.

---

## 🚀 Quick Setup & Execution

### 1. Prerequisites
- Python 3.9+ installed
- A free Google Gemini API key from [Google AI Studio](https://aistudio.google.com/)

### 2. Install Dependencies
Open your terminal / command prompt in this folder and run:
```bash
pip install streamlit google-genai pypdf python-dotenv
```
*(Or use `pip install -r requirements.txt`)*

### 3. Set Your API Key (Optional)
You can set your API key in any of these three ways:
1. **Via UI Sidebar:** Enter your key directly into the sidebar text field when the app is running.
2. **Via `.env` file:** Copy `.env.example` to `.env` and paste your key:
   ```env
   GEMINI_API_KEY=your_actual_api_key_here
   ```
3. **Offline Demo Mode:** If you don't have an API key yet, check the **"Offline Demo Mode"** box in the sidebar to test all UI features and generate sample outputs instantly for screenshots!

### 4. Run the Streamlit Application
```bash
streamlit run app.py
```
The app will open automatically in your browser at `http://localhost:8501`.

---

## 📸 How to Complete Your Submission

### Step 1: Take the Output Screenshot
1. Launch the app and load either your resume or click **"Load Sample Resume"** and **"Load Sample Job Description"**.
2. Click **"🚀 Analyze Resume & Calculate ATS Score"**.
3. Once the score and skills breakdown are displayed, capture a full-window screenshot.
4. Save the image as:
   ```
   RollNo_Name_Output.jpg   (or .png)
   ```
   *(e.g., `21CS042_RahulSharma_Output.png`)*

### Step 2: Create the Code ZIP File
Make sure your actual `.env` file is NOT included in the submission.
You can run our automated script:
```bash
python generate_zip.py <YourRollNumber> <YourName>
```
Example:
```bash
python generate_zip.py 21CS042 RahulSharma
```
This automatically produces `21CS042_RahulSharma_Code.zip` containing all source code and assets, while safely excluding `.env` and temporary files!

### Step 3 (Bonus): Free Hosting on Streamlit Cloud
1. Push this project folder to your GitHub repository.
2. Go to [share.streamlit.io](https://share.streamlit.io/) and log in with GitHub.
3. Click **"New app"**, select your repository, branch (`main`), and set the main file path to `app.py`.
4. In Advanced Settings, add your `GEMINI_API_KEY` under Secrets.
5. Click **"Deploy"** to get a public live URL!

---

## 💡 Viva / Project Explanation Cheat Sheet

If your professor or evaluator asks you to explain the code and design:

| Question | Clear Answer |
| :--- | :--- |
| **What is the core architecture?** | It follows an **Input ➡️ AI Model ➡️ Structured Output** pipeline. The frontend is built with Streamlit, PDF parsing uses `pypdf`, and the reasoning is performed by Google Gemini (`gemini-2.5-flash`). |
| **How does the PDF extraction work?** | `pypdf.PdfReader` iterates through each page of the uploaded PDF stream in memory, extracts raw text strings, and concatenates them without needing to save temporary files to disk. |
| **How do you ensure the AI returns clean, parseable output?** | We instruct Gemini to return strictly valid JSON with predefined keys (`match_score`, `matched_skills`, `missing_skills`, etc.), and handle markdown fence stripping before running `json.loads()`. |
| **Why is the API key not in the code?** | Best security practices require keeping secrets out of version control. The key is managed via environment variables (`.env`), `.gitignore`, or Streamlit Secrets. |
| **What is the practical value of ATS scoring?** | Over 75% of resumes are screened out before reaching recruiters. By comparing job keywords with resume text, job seekers can tailor their applications to pass algorithmic filters. |

---

## 📁 File Structure
```
ai-resume-analyzer/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── generate_zip.py             # Submission packaging script
├── .env.example                # Template for Gemini API key
├── .gitignore                  # Prevents committing secrets & caches
├── README.md                   # Project documentation & viva guide
└── sample_data/
    ├── sample_resume.txt       # Example candidate resume
    └── sample_job_description.txt # Example target job description
```
