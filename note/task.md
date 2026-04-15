# Task List
- [x] Fix RAG Extraction accuracy
- [x] Integrate Groq API for fast RAG Generation
- [x] Add dynamic FAQ suggestions to UI
- [x] Polish CSS and Avatar
- [x] Add logo watermark to chat background
- [x] Apply `#0d1d41` branding color
- [x] Make background blurry (Glassmorphism & Background blur)
- [x] Remove 'RAG' tag from responses
- [x] Add `user.png` avatar
- [x] Implement Mobile Responsive Design
 --------------------------------
                         Utilisateur pose une question
                                    ↓
                        [Query Expansion via LLM]
                   Reformule la question en mots-clés clairs
                                    ↓
                      [Retriever MMR — base Chroma]
                    Cherche les 6 meilleurs extraits
                   parmi tous vos documents (doc/)
                                    ↓
                        [LLM (Groq / Llama 3.3)]
                  Reçoit les extraits + la question
                   et génère une réponse naturelle
                                    ↓
                         Réponse à l'utilisateur
