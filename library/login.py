from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from config import engine, pwd_context

router = APIRouter()

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
                SELECT username, motpasse, equipe_id
                FROM users 
                WHERE username = :user AND is_active = TRUE
            """)
            resultat = connection.execute(query, {
                "user": request.username
            }).fetchone()

            # Si on trouve une ligne, la connexion est réussie
            if resultat:
                # Vérifier le mot de passe
                if pwd_context.verify(request.password, resultat.motpasse):
                    return {
                        "success": True, 
                        "message": "Connexion réussie", 
                        "username": resultat.username,
                        "equipe_id": resultat.equipe_id
                    }
                else:
                    # Sinon, mauvais identifiants ou compte inactif
                    raise HTTPException(status_code=401, detail="Identifiants ou mot de passe incorrects")
            else:
                # Sinon, mauvais identifiants ou compte inactif
                raise HTTPException(status_code=401, detail="Identifiants ou mot de passe incorrects")
            
                
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Erreur serveur : {str(e)}")



