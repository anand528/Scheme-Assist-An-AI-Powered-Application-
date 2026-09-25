# ============================================================
# SchemeAssist – FINAL AGENTIC AI (Stable Core)
# ============================================================
from googletrans import Translator
import os
import re
import json
from typing import Dict
from dotenv import load_dotenv



# ---------------- LANGCHAIN ----------------
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# ---------------- YOUR TOOLS ----------------
from backend.models import User
from backend.tools.search_for_schemes import list_scheme
from backend.tools.generate_scheme_info import generate


# ============================================================
# ENV
# ============================================================

load_dotenv()


# ============================================================
# VOICE (SAFE)
# ============================================================




# ============================================================
# SAFE JSON EXTRACTION
# ============================================================

def extract_json(text: str) -> Dict:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("No JSON found in LLM output")
    return json.loads(match.group())


# ============================================================
# MARKDOWN FORMAT
# ============================================================

def dict_to_markdown(data: Dict) -> str:
    md = []
    for key, value in data.items():
        md.append(f"## {key.replace('_',' ').title()}")
        if isinstance(value, list):
            md.extend([f"- {v}" for v in value])
        elif isinstance(value, dict):
            md.extend([f"- **{k}**: {v}" for k, v in value.items()])
        else:
            md.append(str(value))
        md.append("")
    return "\n".join(md)


# ============================================================
# GEMINI LLM (CORRECT MODEL)
# ============================================================

llm = ChatGoogleGenerativeAI(
    model="models/gemini-3-flash-preview",
    temperature=0.2,
    google_api_key=os.getenv("GEMINI_API_KEY"),
    max_retries=2
)

memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)


# ============================================================
# GENERAL CHAT
# ============================================================

def general_chat_llm(question: str) -> str:
    response = llm.invoke(
        f"Explain clearly in simple English about Indian government schemes:\n{question}"
    )
    return response.content


# ============================================================
# ROUTER PROMPT (FIXED)
# ============================================================

router_prompt = PromptTemplate(
    input_variables=["input"],
    template="""
You are an AI router for an Indian Government Scheme Assistant.

You have THREE tools:

1. list_scheme → when user mensioned eligiblle or eligliblity in his query
2. generate → when user asks about a specific scheme
3. general_chat → for general scheme discussion and also select this when data is insufficient for other tools
orwhen we are not using the other two tools.

Respond ONLY in valid JSON.

FORMAT:
{{
  "tool": "<list_scheme | generate | general_chat>",
  "arguments": {{ ... }}
}}

User message:
{input}
"""
)

router_chain = LLMChain(
    llm=llm,
    prompt=router_prompt,
    memory=memory
)


# ============================================================
# CORE AGENT FUNCTION (REUSABLE)
# ============================================================

async def run_agent(user_input: str, user: User ,language: str="en") -> str:
    print(f"Running agent with input: {user_input} and language: {language}")
    if not user_input.strip():
        return "No input provided."

    try:
        decision = router_chain.invoke({"input": user_input})
        decision_json = extract_json(decision["text"])
    except Exception as e:
        return f"Routing failed: {e}"
    print(f"Router decision: {decision_json}")
    tool = decision_json.get("tool")
    args = decision_json.get("arguments", {})
    if user:
        info= {
                "gender": user.gender,
                "age": user.age, 
                "residence": user.residence,
                "caste": user.caste,
                "percentage": user.percentage,
                "minority": user.minority,
                "is_student":user.is_student,
                "employment": user.employment,
                "is_gov_employee": user.is_gov_employee,
                "state": user.state,
                "is_bpl": user.is_bpl,
                "disability":user.disability,
                "occupation": user.occupation,
                "annual_income": user.annual_income,
                "family_income": user.family_income,
                "economic_distress":user.economic_distress
            }
        
    if user:
            args.update(info)
            
    if tool == "list_scheme":
        print(f"Calling list_scheme with args: {args}") 
        args.pop("query") if "query" in args else None
        result = list_scheme(**args)
        
    elif tool == "generate":
        result = generate(**args)
    elif tool == "general_chat":
        result = {"Answer": general_chat_llm(user_input)}
    else:
        result = {"Message": "Unable to understand request."}
    
    translator = Translator()

    translated_obj = await translator.translate(str(result), dest=language)
    translated = translated_obj.text       

    if isinstance(result, dict):
        markdown = dict_to_markdown(result)
        
        translated_obj = await translator.translate(markdown, dest=language)
        return translated_obj.text

    elif isinstance(result, list):
        text = "## Eligible Schemes\n" + "\n".join(f"- {s}: {r}" for s, r in result)
        
        translated_obj = await translator.translate(text, dest=language)
        return translated_obj.text

    else:
        translated_obj = await translator.translate(str(result), dest=language)
        return translated_obj.text
