
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from jose import jwt, JWTError
from fastapi.responses import StreamingResponse
from sqlalchemy import or_
from backend.database import Base, engine, SessionLocal
from backend.models import User
from backend.schemas import SignupSchema, LoginSchema 
from backend.auth import create_user, verify_password
from fastapi.middleware.cors import CORSMiddleware
from backend.agent import run_agent
from backend.security import create_access_token,SECRET_KEY, ALGORITHM
from langdetect import detect
import whisper
import tempfile
import edge_tts

import os

from fastapi.responses import FileResponse
import uuid

from googletrans import Translator

whisper_model = whisper.load_model("base")  # base = fast + accurate


# ------------------ CONFIG ------------------


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# ------------------ APP INIT ------------------
Base.metadata.create_all(bind=engine)
app = FastAPI(title="SchemeAssist Auth API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # allow all origins (OK for development)
    allow_credentials=True,
    allow_methods=["*"],   # allow POST, GET, OPTIONS, etc.
    allow_headers=["*"],
)

# ------------------ DB DEP ------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()





def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user

# ------------------ ROUTES ------------------

@app.post("/signup")
def signup(data: SignupSchema, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(
        (User.username == data.username) | (User.email == data.email)
    ).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    create_user(db, data)
    return {"message": "Account created successfully"}


@app.post("/login")
def login(data: LoginSchema, db: Session = Depends(get_db)):
    user = db.query(User).filter(
    or_(
        User.username == data.username,
        User.email == data.username
    )
).first()

    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=60)
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.username
    }


from typing import Optional

@app.post("/chat")
async def chat(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user),
    audio: UploadFile = File(None)
):
    try:
        # 🎤 AUDIO INPUT
        if audio:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
                tmp.write(await audio.read())
                audio_path = tmp.name

            result = whisper_model.transcribe(audio_path)
            query = result.get("text", "").strip()
            os.remove(audio_path)

            if not query:
                raise HTTPException(status_code=400, detail="Audio transcription failed")

        # 💬 TEXT INPUT
        else:
            body = await request.json()
            query = body.get("message", "").strip()

            if not query:
                raise HTTPException(status_code=400, detail="Empty message")

        # 🌐 LANGUAGE DETECTION
        try:
            language = detect(query)
            if len(query.split()) < 3:
                language = "en"
        except:
            language = "en"

        print(f"Detected language: {language} | Query: {query}")

        # 🤖 AGENT CALL (FIXED)
        agent_response = await run_agent(
            user_input=f"""
User Query:
{query}

""",
            user=current_user,
            language=language
        )

        print("Raw agent response:", agent_response)

        # ✅ CLEAN RESPONSE
        clean_text = str(agent_response)[10::]  # Remove "AgentResult:" prefix if present
        return {"agent_result": clean_text}

    except HTTPException as e:
        raise e

    except Exception as e:
        print("🔥 ERROR:", str(e))   # VERY IMPORTANT
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat-guest")
async def chatguest(
    request: Request,
    audio: UploadFile = File(None)
):
    try:
        # AUDIO
        if audio:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
                tmp.write(await audio.read())
                audio_path = tmp.name

            result = whisper_model.transcribe(audio_path)
            query = result.get("text", "").strip()
            language = result.get("language", "en") 
            os.remove(audio_path)

            if not query:
                raise HTTPException(status_code=400, detail="Audio transcription failed")

        # TEXT
        else:
            body = await request.json()
            query = body.get("message", "").strip()
            language = body.get("language", "en")
            if not query:
                raise HTTPException(status_code=400, detail="Empty message")

    

        
        print(f"Detected language: {language} | Query: {query}")    
        try:
             # 🔥 FIXED CALL
            agent_response =await run_agent(
                user_input=f"""
            User query: {query}

            """,
            user=None,  # No user context for guests
        language=language

    )
        except Exception as e:
            print("Agent error:", str(e))
             
        clean_text = str(agent_response)[10::]

        

        return {
            "agent_result": clean_text,
            
        }
    

    except HTTPException as e:
        raise e

    except Exception as e:
        
        raise HTTPException(status_code=500, detail="Chat processing failed")



@app.get("/user")
def read_profile(user: User = Depends(get_current_user)):
    return {
        "username": user.username,
        "email": user.email,
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
def get_voice(lang):
    if lang == "hi":
        return "hi-IN-MadhurNeural"
    elif lang == "te":
        return "te-IN-ShrutiNeural"
    return "en-IN-PrabhatNeural"


@app.post("/tts")
async def tts(data: dict):
    text = data.get("text")
    lang = data.get("lang", "en")

    voice = get_voice(lang)

    async def audio_stream():
        communicate = edge_tts.Communicate(text, voice)
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                yield chunk["data"]

    return StreamingResponse(audio_stream(), media_type="audio/mpeg")

@app.get("/ping")
def ping():
    return {"status": "alive"}
