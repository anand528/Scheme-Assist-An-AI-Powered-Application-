import os
from dotenv import load_dotenv
import google.generativeai as genai

# ---------------------------
# 1. Setup
# ---------------------------

load_dotenv()  # loads GEMINI_API_KEY from .env

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found. Please set it in your .env file.")

# Create Gemini client (NEW SDK)
genai.configure(api_key=API_KEY)

MODEL_NAME = "gemini-2.5-flash"

model = genai.GenerativeModel(MODEL_NAME)
# ---------------------------
# 2. Prompt template
# ---------------------------

PROMPT_TEMPLATE = """
You are an assistant that explains Indian government schemes in very simple and clear language.

I will give you the NAME of a government scheme.
You must respond ONLY in valid Markdown, using the exact headings and structure below.

Important instructions:
- If you are not sure about any detail, write "Not clearly available" or "Varies by state / source".
- Use simple, student-friendly language.
- Keep points concise and in bullet lists where appropriate.
- Mention if any information may change over time.
- If the scheme name is ambiguous, pick the most well-known Indian government scheme with that name and clearly mention your assumption.
- personalise the content to user details if available (e.g., age, location, occupation) and mention that you are personalising the content.
Required OUTPUT FORMAT (Markdown):

# Scheme-{Scheme_Name}

## Description
(simple sentences explaining what this scheme is and why it exists.)

## Benefits
- Bullet points of main benefits
- Mention monetary support, services, concessions, etc.

## Eligibility
- Who can apply
- Important conditions

## Exclusions
- Who CANNOT apply
- Common reasons for rejection

## Application Process

### Online Process
- Step 1: ...
- Step 2: ...
- Step 3: ...

### Offline Process
- Step 1: ...
- Step 2: ...
- Step 3: ...

## Documents Required
- List common documents
- Mention if documents vary by state

## Sources and References
- Official website if known
- Otherwise mention official government portals

Now generate details for this scheme:

Scheme Name: "{SCHEME_NAME}"
"""


def build_prompt(scheme_name: str) -> str:
    return PROMPT_TEMPLATE.replace(
        "{SCHEME_NAME}", scheme_name
    ).replace(
        "{Scheme_Name}", scheme_name
    )

# ---------------------------
# 3. Gemini call function (UPDATED)
# ---------------------------

def explain_scheme_markdown(scheme_name: str) -> str:
    """
    Queries Gemini and returns Markdown output
    """
    prompt = build_prompt(scheme_name)
    response = model.generate_content(
        prompt,
        generation_config=genai.GenerationConfig(
            temperature=0.4,
            top_p=0.9,
            top_k=40,
            max_output_tokens=2048,
        )
    )

    return response.text


# ---------------------------
# 4. Wrapper class (unchanged API)
# ---------------------------

class Gemini:
    def generate(self, scheme_name: str ) -> str:
        try:
            markdown_output = explain_scheme_markdown(scheme_name)
            return markdown_output
        except Exception as e:
            return "Error while calling Gemini API:"+str(e) 
            
