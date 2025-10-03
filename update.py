import redis
import json

# Connexion à Redis
r = redis.Redis(host='localhost', port=6379, db=0)

mot_cle = "yahiaoui"

# Accéder à la clé spécifique
data_bytes = r.get("bouchachiadz_medecins")

if data_bytes:
    try:
        data = json.loads(data_bytes)
        
        # Si c'est une liste d'objets JSON
        for item in data:
            if any(mot_cle.lower() in str(v).lower() for v in item.values()):
                print(f"✔️ Trouvé : {item}")
    except json.JSONDecodeError:
        print("❌ Erreur : la valeur n'est pas un JSON valide.")
else:
    print("❌ Clé 'bouchachiadz_medecins' introuvable ou vide.")
