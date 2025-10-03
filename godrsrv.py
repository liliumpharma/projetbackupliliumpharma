import os
import zipfile
import datetime
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

# Répertoires
MEDIA_DIR = "/var/www/server/media"
BACKUP_NAME = f"backup_media_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
BACKUP_PATH = os.path.join("/var/www/server", BACKUP_NAME)

print("Compression du dossier media...")

# Création de l’archive ZIP
with zipfile.ZipFile(BACKUP_PATH, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(MEDIA_DIR):
        for file in files:
            print(file)
            filepath = os.path.join(root, file)
            arcname = os.path.relpath(filepath, MEDIA_DIR)
            zipf.write(filepath, arcname)

print(f"Fichier compressé -> {BACKUP_PATH} ({os.path.getsize(BACKUP_PATH) / (1024*1024):.2f} Mo)")

# Authentification Google Drive
#gauth = GoogleAuth()
#gauth.LoadCredentialsFile("credentials.json")


# Fichier settings.yaml dans le même dossier
gauth = GoogleAuth(settings_file="settings.yaml")
# Authentification
# Pour un serveur SSH sans navigateur graphique, utilise plutôt :
gauth.LoadClientConfigFile("/var/www/server/client_secrets.json")
#gauth.CommandLineAuth()# ouvrira un navigateur la première fois
gauth.LoadCredentialsFile("/var/www/server/credentials.json")
# Au lieu de "client_secrets.json"

if not gauth.credentials:
    gauth.LocalWebserverAuth()
elif gauth.access_token_expired:
    gauth.Refresh()
else:
    gauth.Authorize()

gauth.SaveCredentialsFile("credentials.json")

drive = GoogleDrive(gauth)

# Upload sur Google Drive
print("Upload vers Google Drive...")
file_drive = drive.CreateFile({'title': BACKUP_NAME})
file_drive.SetContentFile(BACKUP_PATH)
file_drive.Upload()

print(f"✔ Upload terminé : {BACKUP_NAME}")
