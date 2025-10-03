import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

print(os.environ.get("DB_USER"))
print(os.environ.get("DB_HOST"))
print(os.environ.get("DB_PASS"))
print(os.environ.get("DB_NAME"))