from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import os, json, shutil, io
from groq import Groq
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from gtts import gTTS
import uvicorn

# Load shared environment variables (GROQ_API_KEY)
load_dotenv()

app = FastAPI(title="Robot Conversationnel Molière")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

if GROQ_API_KEY:
    print("🤖 Robot Mode: GROQ API DÉTECTÉE")
    llm = ChatGroq(model_name="llama-3.3-70b-versatile", groq_api_key=GROQ_API_KEY)
else:
    print("🤖 Robot Mode: Utilisation locale (Whisper nécessitera Groq cependant)")
    from langchain_ollama import ChatOllama
    llm = ChatOllama(model="llama3.2:1b")

# Prompt for the Conversational Robot Evaluation
robot_prompt = ChatPromptTemplate.from_template("""
Tu es un professeur de français très patient. Voici ce que l'étudiant a lu au microphone (transcription) :

"{transcription}"

Tâche :
1. Analyse cette phrase. Corrige les éventuelles fautes de grammaire, de conjugaison ou d'orthographe (ou si un mot semble mal prononcé d'après la transcription STT).
2. Donne un feedback court, bienveillant et utile en français.
3. Traduis la phrase correcte en anglais et en arabe pour l'aider à comprendre.
4. Prépare une phrase que le robot va utiliser pour son discours audio. Si l'étudiant a fait une erreur, dis : "Vous avez dit : [erreur]. La correction est : [phrase corrigée]". Si pas d'erreur, dis "Parfait ! Très bonne prononciation."

Renvoie UNIQUEMENT un objet JSON valide avec EXACTEMENT ces clés (sans Markdown ni texte autour, pure JSON) :
- "correction_fr": la phrase corrigée en français
- "feedback": ton conseil pédagogique
- "traduction_en": traduction anglaise de la phrase corrigée
- "traduction_ar": traduction arabe de la phrase corrigée
- "phrase_audio": la phrase textuelle destinée au Text-to-Speech
""")

robot_chain = robot_prompt | llm | StrOutputParser()

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("robot.html", {"request": request})

@app.post("/api/analyze")
async def analyze_speech(audio: UploadFile = File(...)):
    if not groq_client:
        return JSONResponse(status_code=500, content={"error": "Clé API Groq manquante pour Whisper."})
    
    temp_file = f"tmp_{audio.filename}"
    try:
        # Save uploaded audio to a temporary file
        with open(temp_file, "wb") as f:
            shutil.copyfileobj(audio.file, f)
        
        # Send audio to Groq Whisper for STT
        with open(temp_file, "rb") as f:
            transcription = groq_client.audio.transcriptions.create(
                file=(audio.filename, f.read()),
                model="whisper-large-v3",
                language="fr"
            )
        text = transcription.text
    except Exception as e:
        if os.path.exists(temp_file): os.remove(temp_file)
        return JSONResponse(status_code=500, content={"error": f"Erreur STT Whisper: {str(e)}"})
        
    if os.path.exists(temp_file): os.remove(temp_file)

    # Send transcribed text to LLM for Grammar & Translation
    try:
        result = robot_chain.invoke({"transcription": text})
        clean_json = result.replace("```json", "").replace("```", "").strip()
        analysis = json.loads(clean_json)
    except Exception as e:
        analysis = {
            "correction_fr": text,
            "feedback": f"Erreur du LLM: {str(e)}. (Raw: {result})",
            "traduction_en": "",
            "traduction_ar": "",
            "phrase_audio": text
        }
        
    return {
        "transcription_originale": text,
        "analyse": analysis
    }

@app.get("/api/tts")
async def get_tts(text: str, lang: str = 'fr'):
    """
    Takes text and language, generates audio via gTTS, and streams it back.
    """
    try:
        tts = gTTS(text=text, lang=lang)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return StreamingResponse(fp, media_type="audio/mpeg")
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

if __name__ == "__main__":
    # Runs the robot component on a completely separate port (8001)
    uvicorn.run("robot_main:app", host="127.0.0.1", port=8001, reload=True)
