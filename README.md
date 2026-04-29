# Resume Ranker & Filtering System

An intelligent, automated resume screening and ranking system built with Flask. This application helps recruiters and hiring managers streamline their hiring process by comparing applicant resumes against a job description, scoring them based on skills, experience, and keywords, and providing an easy-to-use filtering dashboard.

## Features

- **Automated Resume Parsing:** Extracts key information from resumes (PDFs), including the candidate's name, email, phone number, and years of experience.
- **Smart Scoring System:** Calculates a match percentage based on:
  - **Skills Match (60%):** Matches skills found in the job description (using a dynamic `skills.json` bank) with the skills present in the resume.
  - **Experience Match (30%):** Compares the candidate's total years of experience against the required experience extracted from the job description.
  - **Keyword Relevance (10%):** Uses TF-IDF and Cosine Similarity to measure semantic similarity between the resume text and the job description.
- **AI-Powered Explanations:** Provides quick insights into why a candidate is a good fit, highlighting strong skill matches, missing skills, and experience gaps.
- **Advanced Filtering:** Filter the generated candidate list by:
  - Minimum Experience (Years)
  - Minimum Match Percentage
  - Must-Have Skills (Comma-separated)
- **Status Categorization:** Automatically categories candidates into `SELECTED` (≥ 60%), `CONSIDER` (40% - 59%), and `REJECTED` (< 40%).
- **Interactive UI:** A modern and dynamic web interface to upload documents and view the ranked results.

## Technology Stack

- **Backend:** Python, Flask, Werkzeug
- **NLP & Machine Learning:** scikit-learn (TF-IDF, Cosine Similarity)
- **PDF Extraction:** `pdfplumber`, `PyPDF2`
- **Frontend:** HTML, CSS (Vanilla), JavaScript

## Installation & Setup

1. **Clone the repository or navigate to the project directory:**
   ```bash
   cd resume_ranker
   ```

2. **Create a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install dependencies:**
   Ensure you have the required Python packages installed:
   ```bash
   pip install Flask Werkzeug PyPDF2 pdfplumber scikit-learn
   ```

4. **Run the Application:**
   ```bash
   python app.py
   ```

5. **Access the Web App:**
   Open your browser and navigate to `http://127.0.0.1:5000`

## Project Structure

- `app.py`: Main Flask application handling routes, file uploads, and core logic.
- `utils.py`: Utility functions for text cleaning, data extraction (emails, phones, experience), PDF processing, and similarity scoring.
- `skills.json`: A configurable JSON file containing a wide range of skills categorized by domain. The system uses this to extract relevant skills from the job description.
- `templates/index.html`: The frontend UI dashboard for uploading documents and displaying ranked candidates.
- `test.py`: Testing script for debugging extraction and scoring logic.
- `resumes/`: Temporary storage directory where uploaded resumes are saved and processed.

## How to Use

1. Enter the Job Description text OR upload a Job Description PDF.
2. Upload multiple candidate Resumes (in PDF format).
3. Click **Analyze & Rank**.
4. Review the generated list of candidates sorted by their match percentage.
5. Use the **Filters** section to narrow down candidates by minimum experience, required score, or specific "must-have" skills.

## Contributing

Feel free to fork the project and submit pull requests. To add new skills to the tracking algorithm, simply update the `skills.json` file.
