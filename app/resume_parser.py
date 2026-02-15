import os
from pdfminer.high_level import extract_text
from io import BytesIO
from dotenv import load_dotenv
import json
import time

# Import openai at the top level to make it available throughout the module
try:
    import openai
except ImportError:
    print("Failed to import openai module")

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
api_key = os.getenv('OPENAI_API_KEY')
print(f"Loaded API key: {api_key[:10]}...")  # Print first 10 chars for debugging

# Set the API key for the openai module if it was imported
if 'openai' in globals():
    openai.api_key = api_key
    print("Set API key for old OpenAI API")

# Check OpenAI version to use correct client
is_new_version = False
try:
    # Try to import pkg_resources (part of setuptools)
    import pkg_resources
    openai_version = pkg_resources.get_distribution("openai").version
    print(f"OpenAI version: {openai_version}")
    is_new_version = int(openai_version.split('.')[0]) >= 1
except ImportError:
    print("pkg_resources not available, defaulting to old OpenAI API")
    # Default to old API if can't detect version
    is_new_version = False
except Exception as e:
    print(f"Error detecting OpenAI version: {e}, defaulting to old OpenAI API")
    is_new_version = False

# Initialize client variable in the global scope
client = None

try:
    if is_new_version:
        # New OpenAI client (v1.0.0+)
        try:
            from openai import OpenAI
            # Initialize with only the api_key parameter to avoid compatibility issues
            client = OpenAI(api_key=api_key)
            print("Successfully initialized OpenAI client with new API")
        except (TypeError, ImportError) as e:
            print(f"Error initializing OpenAI client: {e}")
            # Fall back to the old client if there's a problem with initialization
            is_new_version = False
            print("Falling back to old OpenAI API")
    else:
        # Old OpenAI client (v0.28 or earlier)
        print("Using old OpenAI API")
except Exception as e:
    print(f"Error setting up OpenAI: {e}")
    # Default to old version as fallback
    is_new_version = False
    print("Defaulting to old OpenAI API due to error")

def parse_resume(file):
    # Read the file content into a BytesIO object
    file_content = file.read()
    pdf_file = BytesIO(file_content)
    text = extract_text(pdf_file)
    return text

def fallback_resume_analysis():
    """Fallback response when OpenAI quota is exceeded"""
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
        "note": "AI fallback response used due to API quota limits"
    }


def analyze_resume(resume_text):
    """Analyze the resume using OpenAI's API"""
    # Reference the global variables
    global is_new_version, client, openai
    
    # Set up retry parameters
    max_retries = 3
    retry_delay = 2  # seconds
    
    try:
        # Create the prompt for the analysis
        prompt = f"""Analyze this resume and provide detailed feedback in JSON format with the following structure:
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
                "improvements": [
                    "Specific suggestions to improve ATS score"
                ]
            }},
            "feedback": {{
                "overallAssessment": {{
                    "strengths": ["list of key strengths"],
                    "areasForImprovement": ["list of areas to improve"]
                }},
                "educationSection": {{
                    "strengths": ["list of strengths"],
                    "areasForImprovement": ["list of improvements"]
                }},
                "extraCurricularActivities": {{
                    "strengths": ["list of strengths"],
                    "areasForImprovement": ["list of improvements"]
                }},
                "awardsAndAchievements": {{
                    "strengths": ["list of strengths"],
                    "areasForImprovement": ["list of improvements"]
                }},
                "professionalExperience": {{
                    "strengths": ["list of strengths"],
                    "areasForImprovement": ["list of improvements"]
                }},
                "aboutMeSection": {{
                    "strengths": ["list of strengths"],
                    "areasForImprovement": ["list of improvements"]
                }},
                "skillsSection": {{
                    "strengths": ["list of strengths"],
                    "areasForImprovement": ["list of improvements"]
                }}
            }}
        }}

        Resume text:
        {resume_text}

        Provide an ATS (Applicant Tracking System) score out of 100 based on:
        1. Keywords relevance (0-25 points): How well the resume uses industry-specific keywords
        2. Formatting (0-20 points): Simple, clean formatting that ATS can parse
        3. Experience section (0-25 points): Clear job titles, companies, dates, and achievements
        4. Skills section (0-20 points): Relevant technical and soft skills
        5. Education (0-10 points): Clear education details

        Also provide specific, actionable feedback for each section. Focus on strengths and areas for improvement.
        Keep the response concise but detailed. Ensure the JSON is properly formatted and complete."""

        messages = [
            {"role": "system", "content": "You are a professional resume reviewer. Provide detailed, constructive feedback in JSON format."},
            {"role": "user", "content": prompt}
        ]

        content = None
        last_error = None
        
        for attempt in range(max_retries):
            try:
                use_old_api = False
                
                # Attempt to use new API if available
                if is_new_version and client is not None:
                    try:
                        print(f"Attempt {attempt+1}/{max_retries}: Using new OpenAI API...")
                        response = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=messages,
                            temperature=0.7,
                            max_tokens=2000
                        )
                        content = response.choices[0].message.content.strip()
                        print("Successfully used new OpenAI API")
                        break  # Exit the retry loop if successful
                    except Exception as new_api_error:
                        error_message = str(new_api_error)
                        print(f"Error with new OpenAI API: {error_message}")
                        
                        # If it's a rate limit or quota error, immediately try the old API
                        if "Rate limit" in error_message or "quota" in error_message.lower():
                            print("Quota limit detected, trying old API as fallback...")
                            use_old_api = True
                        # If it's a Bad Gateway, we'll retry after delay
                        elif "502" in error_message or "Bad Gateway" in error_message:
                            last_error = new_api_error
                            print(f"Server error (502), retrying in {retry_delay} seconds...")
                            time.sleep(retry_delay)
                            continue
                        else:
                            use_old_api = True
                else:
                    use_old_api = True
                
                # Try the old API if needed
                if use_old_api:
                    try:
                        print(f"Attempt {attempt+1}/{max_retries}: Using old OpenAI API...")
                        # Ensure openai is available
                        if 'openai' not in globals() or openai is None:
                            import openai
                            openai.api_key = api_key
                        
                        # Call the old API
                        response = openai.ChatCompletion.create(
                            model="gpt-4o-mini",
                            messages=messages,
                            temperature=0.7,
                            max_tokens=2000
                        )
                        content = response['choices'][0]['message']['content'].strip()
                        print("Successfully used old OpenAI API")
                        break  # Exit the retry loop if successful
                    except Exception as old_api_error:
                        error_message = str(old_api_error)
                        print(f"Error with old OpenAI API: {error_message}")
                        
                        # Store the error for potential use if all retries fail
                        last_error = old_api_error
                        
                        # If it's a rate limit or quota error, no point in retrying
                        if "rate limit" in error_message.lower() or "quota" in error_message.lower():
                            print("⚠️ API quota exceeded — using fallback response")
                            return fallback_resume_analysis()
                        # If it's a Bad Gateway, we'll retry after delay
                        elif "502" in error_message or "Bad Gateway" in error_message:
                            print(f"Server error (502), retrying in {retry_delay} seconds...")
                            time.sleep(retry_delay)
                            continue
                        # For other errors, wait and retry
                        else:
                            if attempt < max_retries - 1:  # If not the last attempt
                                print(f"Retrying in {retry_delay} seconds...")
                                time.sleep(retry_delay)
                            else:
                                return {"error": f"OpenAI API error: {error_message}"}
            
            except Exception as loop_error:
                print(f"Unexpected error in retry loop: {loop_error}")
                last_error = loop_error
                if attempt < max_retries - 1:  # If not the last attempt
                    print(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
        
        # If we've exhausted all retries and still have no content
        if content is None:
            print("⚠️ No AI response received — using fallback")
            return fallback_resume_analysis()
        
        # Try to parse the content as JSON to validate it
        try:
            feedback = json.loads(content)
            return feedback
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Raw content: {content}")
            # If JSON parsing fails, try to extract the JSON part from the content
            try:
                # Find the first { and last } to extract the JSON
                start = content.find('{')
                end = content.rfind('}') + 1
                if start >= 0 and end > start:
                    json_str = content[start:end]
                    feedback = json.loads(json_str)
                    return feedback
            except Exception as e:
                print(f"Failed to extract JSON: {e}")
                return {"error": "Failed to parse resume analysis", "raw_content": content}

    except Exception as e:
        print(f"Error in analyze_resume: {e}")
        return {"error": str(e)}
