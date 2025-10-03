import os
import json
import zipfile
import smtplib
import django
from datetime import datetime
from django.core.mail import EmailMessage
from django.apps import apps
from django.conf import settings
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "liliumpharm.settings")
django.setup()
print(settings.LOGGING_CONFIG)
# Dossier où stocker les backups
BACKUP_DIR = "backups"
if not os.path.exists(BACKUP_DIR):
    os.makedirs(BACKUP_DIR)

# Générer un nom d'archive
backup_filename = f"backup_models_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.zip"
backup_path = os.path.join(BACKUP_DIR, backup_filename)

# Sauvegarder chaque modèle en JSON
json_files = []
for model in apps.get_models():
    model_name = model._meta.label  # Nom complet de l'app et du modèle
    data = list(model.objects.values())  # Convertir en dictionnaire

    if data:  # Ne pas sauvegarder si le modèle est vide
        json_file = os.path.join(BACKUP_DIR, f"{model_name}.json")
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        json_files.append(json_file)

# Compresser en ZIP
with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for json_file in json_files:
        zipf.write(json_file, os.path.basename(json_file))
        os.remove(json_file)  # Supprimer le JSON après l'ajout au ZIP

print(f"✅ Backup compressé : {backup_path}")

# 🔹 Fonction d'envoi par email
def send_email(zip_path):
    EMAIL_TO = "contact@liliumpharma.com"
    EMAIL_FROM = settings.EMAIL_HOST_USER  # Récupéré depuis settings.py

    msg = MIMEMultipart()
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO
    msg["Subject"] = "Backup Django Models"

    with open(zip_path, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(zip_path)}")
        msg.attach(part)

    try:
        server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_FROM, settings.EMAIL_HOST_PASSWORD)
        server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
        server.quit()
        print(f"✅ Email envoyé à {EMAIL_TO}")
    except Exception as e:
        print(f"❌ Erreur envoi email : {e}")

# Envoyer le backup par email
send_email(backup_path)
