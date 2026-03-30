from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()

# LangChain - imports modernes (v1.x LCEL)
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

app = FastAPI()

# 🔹 Fichiers statiques (Images, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")

# 🔹 Charger PDF
def load_docs():
    docs = []
    for file in os.listdir("doc"):
        if file.endswith(".pdf"):
            loader = PyPDFLoader(f"doc/{file}")
            docs.extend(loader.load())
    return docs

# 🔹 Split
def split_docs(docs):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100
    )
    return splitter.split_documents(docs)

# 🔹 Embeddings et base vectorielle (avec persistance optimisée)
embeddings = OllamaEmbeddings(model="nomic-embed-text")

# Dossier pour la base de données
db_path = "./db"

if os.path.exists(db_path) and os.listdir(db_path):
    print("📂 UTILISATION DE LA BASE VECTORIELLE EXISTANTE")
    db = Chroma(persist_directory=db_path, embedding_function=embeddings)
else:
    print("⏳ CRÉATION DE LA BASE VECTORIELLE (Première fois)...")
    docs = load_docs()
    chunks = split_docs(docs)
    db = Chroma.from_documents(chunks, embeddings, persist_directory=db_path)

retriever = db.as_retriever(search_kwargs={"k": 5})

# 🔹 Fonction utilitaire pour le contexte
def format_docs(docs):
    if not docs:
        return "[INFO] Aucun document pertinent trouvé dans la base de l'Institut Molière."
    return "\n\n".join(doc.page_content for doc in docs)

# 🔹 LLM Ultra Rapide (Groq) ou Local
from langchain_groq import ChatGroq

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if GROQ_API_KEY:
    print("🚀 GROQ API DÉTECTÉE : Utilisation du modèle Llama 3.3 (70B) Ultra Rapide")
    llm = ChatGroq(model_name="llama-3.3-70b-versatile", groq_api_key=GROQ_API_KEY)
else:
    print("⚠️ GROQ API NON DÉTECTÉE : Utilisation du CPU local Llama 3.2 (Lent)")
    llm = ChatOllama(model="llama3.2:1b")

# 🔹 Prompt SUPER STRICT
prompt = ChatPromptTemplate.from_template("""
Tu es l'assistant officiel de l'Institut Molière. Ton rôle est d'aider les utilisateurs UNIQUEMENT sur des sujets liés à l'institut (formations, tarifs, calendrier, inscriptions, localisation à Tunis, etc.).

### RÈGLE D'OR (LIMITE DE RÉPONSE) :
Si la question de l'utilisateur porte sur un sujet général, historique, politique (comme l'identité d'un président), sportif ou tout autre sujet NON mentionné dans l'institut Molière ou dans le contexte ci-dessous :
-> RÉPONDS POLIMENT que tu es uniquement un assistant dédié à l'Institut Molière et que tu ne peux pas répondre à cette question. Suggestion : "Je suis désolé, je suis programmé pour répondre uniquement aux questions concernant l'Institut Molière. Puis-je vous aider sur nos formations ou services ?"

### DIRECTIVES :
- Règle ABSOLUE : Pas de phrases du type "D'après les documents", "Selon le contexte" ou "Les informations fournies".
- Sois direct, naturel et concis.
- Réponds toujours dans la même langue que la question (Français ou Anglais).

### CONTEXTE DE L'INSTITUT :
{context}

### QUESTION DE L'UTILISATEUR :
{question}

Réponse :
""")

# 🔹 Chaîne LCEL moderne
chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# 🔹 API
class Question(BaseModel):
    question: str

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def get_home(request: Request):
    suggestions_list = [
        "Quel est le numéro de téléphone ?",
        "Où se trouve l'Institut Molière ?" ,
        "Comment s’inscrire à une activité ?" ,
        "Quels sont les horaires d'ouverture ?"
    ]
    return templates.TemplateResponse("index.html", {"request": request, "suggestions": suggestions_list})

@app.post("/ask")
def chat(q: Question):
    answer = chain.invoke(q.question)
    return {"response": answer, "type": "RAG"}