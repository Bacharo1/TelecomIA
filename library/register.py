from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from config import engine, pwd_context

router = APIRouter()

class RegisterRequest(BaseModel):
    username: str
    password: str
    equipe_id: str = None

@router.post("/register")
async def register(request: RegisterRequest):
    try:
        # On hache le mot de passe reçu en clair avant de toucher à la BDD
        hashed_password = pwd_context.hash(request.password)

        with engine.connect() as connection:
            # Sécurité : On vérifie si le username est déjà pris
            check_query = text("SELECT username FROM users WHERE username = :user")
            if connection.execute(check_query, {"user": request.username}).fetchone():
                raise HTTPException(status_code=400, detail="Ce nom d'utilisateur existe déjà.")

            # On insère le nouvel utilisateur avec son mot de passe HACHÉ
            insert_query = text("""
                INSERT INTO users (username, motpasse, equipe_id, is_active) 
                VALUES (:user, :pass, :equipe, TRUE)
            """)
            connection.execute(insert_query, {
                "user": request.username,
                "pass": hashed_password,
                "equipe": request.equipe_id
            })
            
            # Ne pas oublier de valider la transaction pour sauvegarder dans MySQL
            connection.commit() 

        return {"success": True, "message": "Utilisateur créé avec succès"}

    except HTTPException as http_ext:
        raise http_ext
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur serveur : {str(e)}")

