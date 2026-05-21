from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

router = APIRouter()

# --- Configuration de la Base de Données ---
load_dotenv()

# 2. On récupère les variables d'environnement nécessaires
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")  
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")

# 3. On assemble l'URL de connexion au format attendu par SQLAlchemy 
# Format : mysql+pymysql://utilisateur:motdepasse@serveur:port/basededonnees
database_url = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

# 4. On crée le "moteur" et on teste la connexion
engine = create_engine(database_url)

class LoginRequest(BaseModel):
    username: str
    password: str


# --- L'Endpoint de Connexion ---
@router.post("/login")
async def login(request: LoginRequest):
    try:
        with engine.connect() as connection:
            # On cherche l'utilisateur dans la base MySQL
            # On vérifie qu'il existe, que le mot de passe correspond, et qu'il est actif
            query = text("""
                SELECT username, equipe_id 
                FROM users 
                WHERE username = :user AND motpasse = :pass AND is_active = TRUE""")
            
            resultat = connection.execute(query, {
                "user": request.username, 
                "pass": request.password
            }).fetchone()

            # Si on trouve une ligne, la connexion est réussie
            if resultat:
                return {
                    "success": True, 
                    "message": "Connexion réussie", 
                    "username": resultat.username,
                    "equipe_id": resultat.equipe_id
                }
            else:
                # Sinon, mauvais identifiants ou compte inactif
                raise HTTPException(status_code=401, detail="Identifiants incorrects")
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur serveur : {str(e)}")



