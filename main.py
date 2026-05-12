import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from config import UPLOAD_DIR

# On importe les routers 
from library import session, upload, liste_documents, chat

app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.mount("/documents", StaticFiles(directory=str(UPLOAD_DIR)), name="documents")

# ON BRANCHE TOUT ICI
app.include_router(session.router)
app.include_router(upload.router)
app.include_router(liste_documents.router)
app.include_router(chat.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)

