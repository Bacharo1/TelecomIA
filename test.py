from sqlalchemy import text
from config import engine, pwd_context # On récupère la config partagée !

print("Démarrage de la mise à jour des mots de passe...")

# engine.begin() permet de sauvegarder (commit) automatiquement à la fin
with engine.begin() as connection:
    # 1. On lit tous les utilisateurs actuels
    utilisateurs = connection.execute(text("SELECT username, motpasse FROM users")).fetchall()
    
    compteur = 0
    for user in utilisateurs:
        ancien_mdp = user.motpasse
        
        # 2. On vérifie que le mot de passe n'est pas déjà haché
        if not ancien_mdp.startswith("$2b$"):
            # On génère la version chiffrée
            nouveau_mdp_hache = pwd_context.hash(ancien_mdp)
            
            # 3. On remplace l'ancien mot de passe par le nouveau
            connection.execute(
                text("UPDATE users SET motpasse = :nouveau WHERE username = :user"),
                {"nouveau": nouveau_mdp_hache, "user": user.username}
            )
            print(f" Mot de passe mis à jour et sécurisé pour l'utilisateur : {user.username}")
            compteur += 1

print(f"\nTerminé ! {compteur} mots de passe ont été convertis avec succès.")