import os
import django
import datetime
import subprocess
import gzip
import shutil
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

# ---------------- CONFIGURATION ----------------
POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "openpgpwd"  # mot de passe PostgreSQL
POSTGRES_DB   = "lilliumpharma"
POSTGRES_HOST = "127.0.0.1"
POSTGRES_PORT = 5432

DRIVE_FOLDER_ID = "1r6ty9NdcYH6zJB-yn0qeOe57ixvLwkoB"       # ID du dossier Google Drive
SETTINGS_FILE   = "/var/www/server/settings.yaml"           # chemin vers settings.yaml

# Initialiser Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'liliumpharm.settings')
django.setup()

# ---------------- 1. Dump PostgreSQL ----------------
backup_file = f"/var/www/server/backup_lilliumpharma_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"

os.environ["PGPASSWORD"] = POSTGRES_PASSWORD

command = [
    "pg_dump",
    "-U", POSTGRES_USER,
    "-h", POSTGRES_HOST,
    "-p", str(POSTGRES_PORT),
    "-d", POSTGRES_DB,
    "-F", "p",
    "-f", backup_file
]

subprocess.run(command, check=True)
print(f"Sauvegarde créée -> {backup_file}")

# ---------------- 2. Compression ----------------
compressed_file = backup_file + ".gz"
with open(backup_file, "rb") as f_in:
    with gzip.open(compressed_file, "wb") as f_out:
        shutil.copyfileobj(f_in, f_out)

print(f"Fichier compressé -> {compressed_file}")

# ---------------- 3. Authentification OAuth ----------------
# Fichier settings.yaml dans le même dossier
gauth = GoogleAuth(settings_file="settings.yaml")
# Authentification
# Pour un serveur SSH sans navigateur graphique, utilise plutôt :
gauth.LoadClientConfigFile("/var/www/server/client_secrets.json")
#gauth.CommandLineAuth()# ouvrira un navigateur la première fois
gauth.LoadCredentialsFile("/var/www/server/credentials.json")
# Au lieu de "client_secrets.json"


drive = GoogleDrive(gauth)

# ---------------- 4. Upload vers Google Drive ----------------
gfile = drive.CreateFile({
    "title": os.path.basename(compressed_file),
    "parents": [{"id": DRIVE_FOLDER_ID}]
})
gfile.SetContentFile(compressed_file)
gfile.Upload()

print("✅ Backup envoyé sur Google Drive avec succès !")
