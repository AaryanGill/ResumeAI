import os
from pdfminer.high_level import extract_text
from io import BytesIO
from dotenv import load_dotenv
import json
import time
from groq import Groq

# Load environment variables
load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

# Create Groq client
if api_key:
    print(f"Loaded Groq API key: {api_key[:10]}...")
    client = Groq(api_key=api_key)
else:
    print("No Groq API key found, using fallback mode.")
    client = None


def parse_resume(file):
    file_content = file.read()
    pdf_file = BytesIO(file_content)
    text = extract_text(pdf_file)
    return text


def fallback_resume_analysis():
    return {
        "atsScore": {
            "score": 72,
            "scoreBreakdown": {
                "keywords": 16,
                "formatting": 14,
                "experience": 18,
                "skills": 14,
                "education": 10
            },
            "improvements": [
                "Add more role-specific keywords",
                "Use bullet points with quantified results",
                "Keep formatting simple for ATS systems"
            ]
        },
        "feedback": {
            "overallAssessment": {
                "strengths": [
                    "Relevant technical projects",
                    "Clear education section",
                    "Consistent formatting"
                ],
                "areasForImprovement": [
                    "Lack of quantified achievements",
                    "Missing industry keywords"
                ]
            },
            "educationSection": {
                "strengths": ["Degree clearly mentioned"],
                "areasForImprovement": ["Add GPA or academic highlights"]
            },
            "extraCurricularActivities": {
                "strengths": ["Shows initiative"],
                "areasForImprovement": ["Link activities to skills"]
            },
            "awardsAndAchievements": {
                "strengths": [],
                "areasForImprovement": ["Add certifications or hackathons"]
            },
            "professionalExperience": {
                "strengths": ["Internship experience listed"],
                "areasForImprovement": ["Add impact-based bullet points"]
            },
            "aboutMeSection": {
                "strengths": ["Clear career objective"],
                "areasForImprovement": ["Make it more concise"]
            },
            "skillsSection": {
                "strengths": ["Good technical base"],
                "areasForImprovement": ["Add tools like Docker, Git"]
            }
        },
        "note": "AI fallback response used due to API limits"
    }


def analyze_resume(resume_text):

    global client

    if client is None:
        print("⚠️ No API key detected. Using fallback.")
        return fallback_resume_analysis()

    max_retries = 3
    retry_delay = 2

    prompt = f"""
Analyze this resume and return response ONLY in JSON format.

JSON structure:

{{
"atsScore": {{
"score": 85,
"scoreBreakdown": {{
"keywords": 20,
"formatting": 15,
"experience": 25,
"skills": 15,
"education": 10
}},
"improvements": ["suggestions"]
}},
"feedback": {{
"overallAssessment": {{
"strengths": [],
"areasForImprovement": []
}},
"educationSection": {{
"strengths": [],
"areasForImprovement": []
}},
"extraCurricularActivities": {{
"strengths": [],
"areasForImprovement": []
}},
"awardsAndAchievements": {{
"strengths": [],
"areasForImprovement": []
}},
"professionalExperience": {{
"strengths": [],
"areasForImprovement": []
}},
"aboutMeSection": {{
"strengths": [],
"areasForImprovement": []
}},
"skillsSection": {{
"strengths": [],
"areasForImprovement": []
}}
}}
}}

Resume Text:
{resume_text[:3000]}
"""

    for attempt in range(max_retries):
        try:

            print(f"Attempt {attempt+1}/{max_retries}: Using Groq API...")

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            content = response.choices[0].message.content.strip()

            try:
                return json.loads(content)
            except:
                start = content.find("{")
                end = content.rfind("}") + 1
                json_str = content[start:end]
                return json.loads(json_str)

        except Exception as e:

            print(f"Error with Groq API: {e}")

            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                print("⚠️ Groq failed — using fallback")
                return fallback_resume_analysis()