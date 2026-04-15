from fastapi import FastAPI, Request # pour creation serveur web , requete 
from fastapi.staticfiles import StaticFiles # fichiers statiques
from fastapi.templating import Jinja2Templates # template web
from fastapi.responses import HTMLResponse, StreamingResponse # reponse html et streaming
from pydantic import BaseModel # validation des données 
import os # gestioon des fichiers
from dotenv import load_dotenv #varienble env

load_dotenv()

# LangChain - imports modernes (v1.x LCEL)
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma #base vectorielle
from langchain_ollama import OllamaEmbeddings, ChatOllama # embedding et llm
from langchain_experimental.text_splitter import SemanticChunker # chunking
from langchain_core.prompts import ChatPromptTemplate # prompt
from langchain_core.runnables import RunnablePassthrough # pour l'execution du chain
from langchain_core.output_parsers import StrOutputParser # parser de sortie
from langchain_core.documents import Document

# Reranker imports
from langchain_classic.retrievers.document_compressors import CrossEncoderReranker
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from langchain_classic.retrievers import ContextualCompressionRetriever

# Hybride BM25
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers.ensemble import EnsembleRetriever

app = FastAPI()

#  Fichiers statiques (Images, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")

#  Charger PDF et Textes
from langchain_community.document_loaders import TextLoader

def load_docs():
    docs = []
    for file in os.listdir("doc"):
        filepath = os.path.join("doc", file)
        if file.endswith(".pdf"):
            loader = PyPDFLoader(filepath)
            docs.extend(loader.load())
        elif file.endswith(".txt"):
            loader = TextLoader(filepath, encoding="utf-8")
            docs.extend(loader.load())
    return docs

#  Split (chunks plus petits pour plus de précision sémantique)
def split_docs(docs, embeddings):
    splitter = SemanticChunker(embeddings)
    return splitter.split_documents(docs)

#  Embeddings et base vectorielle (avec persistance optimisée)
embeddings = OllamaEmbeddings(model="nomic-embed-text")

# Dossier pour la base de données
db_path = "./db"

if os.path.exists(db_path) and os.listdir(db_path):
    print("  UTILISATION DE LA BASE VECTORIELLE EXISTANTE")
    db = Chroma(persist_directory=db_path, embedding_function=embeddings)
    # Récupérer les chunks pour BM25 sans recalculer le SemanticChunker
    print("  RÉCUPÉRATION DES CHUNKS POUR BM25...")
    data = db.get()
    chunks = [Document(page_content=text, metadata=meta) for text, meta in zip(data['documents'], data['metadatas'])]
else:
    print(" CRÉATION DE LA BASE VECTORIELLE (Première fois)...")
    docs = load_docs()
    chunks = split_docs(docs, embeddings)
    db = Chroma.from_documents(chunks, embeddings, persist_directory=db_path)

#  1. Retriever Sémantique (ChromaDB avec Similarity - Plus rapide que MMR)
chroma_retriever = db.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 10}
)

#  2. Retriever Statistique (BM25)
print("  INITIALISATION DU BM25...")
bm25_retriever = BM25Retriever.from_documents(chunks)
bm25_retriever.k = 10

#  3. Retriever Hybride (Ensemble)
ensemble_retriever = EnsembleRetriever(
    retrievers=[chroma_retriever, bm25_retriever], 
    weights=[0.5, 0.5]
)

#  4. Reranking (Cross-Encoder pour affiner)
model = HuggingFaceCrossEncoder(model_name="cross-encoder/ms-marco-MiniLM-L-6-v2")
compressor = CrossEncoderReranker(model=model, top_n=3)
retriever = ContextualCompressionRetriever(
    base_compressor=compressor,
    base_retriever=ensemble_retriever
)

#  Fonction utilitaire pour le contexte
def format_docs(docs):
    if not docs:
        return "[INFO] Aucun document pertinent trouvé dans la base de l'Institut Molière."
    return "\n\n".join(doc.page_content for doc in docs)

#  LLM Ultra Rapide (Groq) ou Local
from langchain_groq import ChatGroq

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if GROQ_API_KEY:
    print(" GROQ API DÉTECTÉE : Utilisation du modèle Llama 3.3 (70B) Ultra Rapide")
    llm = ChatGroq(model_name="llama-3.3-70b-versatile", groq_api_key=GROQ_API_KEY)
else:
    print(" GROQ API NON DÉTECTÉE : Utilisation du CPU local Llama 3.2 (Lent)")
    llm = ChatOllama(model="llama3.2:1b")

#  Prompt Affiné
prompt = ChatPromptTemplate.from_template("""
Tu es l'assistant officiel de l'Institut Molière. Ton rôle est de renseigner les utilisateurs sur l'Institut et d'aider les parents à accompagner l'apprentissage du français de leurs enfants.

### MISSIONS PRINCIPALES :
1. **Infos Institut** : Répondre aux questions sur les programmes, tarifs, calendriers et services de l'Institut Molière.
2. **Maîtrise du Français** : Expliquer les niveaux CECRL (A1, A1.1, A2) et donner des conseils pédagogiques aux parents.
3. **Ressources & Activités** : Orienter vers des sites, dessins animés, livres, jeux et applications pour apprendre le français à la maison.

### INFORMATIONS DE CONTACT :
- Téléphone : 53.86.53.80
- Localisation : Tunis (Place Pasteur et Menzah 7)
- Horaires : Lundi-Vendredi (8h00 - 17h00). Samedi matin sur rendez-vous.

### RÈGLES DE COMPORTEMENT :
1. **Priorité au Contexte** : Utilise TOUJOURS le CONTEXTE ci-dessous pour répondre précisément.
2. **Sujet élargi permis** : Les questions sur des films, livres, jeux, chansons ou activités POUR ENFANTS sont permises si elles servent à apprendre le français.
3. **Hors-sujet Total (Interdit)** : Si la question n'a RIEN à voir avec l'Institut Molière ou l'apprentissage du français (ex: politique, météo, sport...), réponds :
"Je suis l'assistant dédié à l'Institut Molière et à l'accompagnement en français. Je ne peux répondre qu'aux questions concernant nos services ou l'apprentissage de la langue. Puis-je vous aider sur ces sujets ?"

### RÈGLES DE STYLE :
- Pas de "D'après les documents" ou "Selon le contexte".
- Langue : Réponds toujours dans la langue de la question.
- Très concis.

### CONTEXTE :
{context}

### QUESTION :
{question}

Réponse :
""")

#  Expansion de question (Query Expansion)
query_expansion_prompt = ChatPromptTemplate.from_template("""
Ton rôle est d'extraire les mots-clés essentiels d'une question pour une recherche documentaire.
Reformule la question suivante en une suite de mots-clés ou une phrase très simple et directe en français.
Exemple: "Quels sont les horaires d'ouverture ?" -> "horaires ouverture institut"

Question originale : {question}

Mots-clés / Reformulation :
""")

expansion_chain = query_expansion_prompt | llm | StrOutputParser()

def expand_and_retrieve(question: str) -> str:
    """Reformule la question puis récupère le contexte pertinent."""
    # Si la question est très courte, on évite l'expansion pour gagner du temps
    if len(question.split()) <= 3:
        expanded = question
    else:
        try:
            expanded = expansion_chain.invoke({"question": question})
        except:
            expanded = question
        
    docs = retriever.invoke(expanded)
    return format_docs(docs)

#  Chaîne LCEL avec Query Expansion
chain = (
    {"context": lambda x: expand_and_retrieve(x), "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

#  API
class Question(BaseModel):
    question: str

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def get_home(request: Request):
    suggestions_list = [
        "Quel est le numéro de téléphone ?" ,
        "Quels sont les horaires ?" ,
        "Quels sont les niveaux de français pour les enfants ?",
        "Comment aider mon enfant à s'améliorer à la maison ?"
    ]
    return templates.TemplateResponse("index.html", {"request": request, "suggestions": suggestions_list})

@app.post("/ask")
async def chat(q: Question):
    async def generate_response():
        # Utilisation de astream pour fluidifier l'affichage (streaming)
        async for chunk in chain.astream(q.question):
            yield chunk

    return StreamingResponse(generate_response(), media_type="text/plain")